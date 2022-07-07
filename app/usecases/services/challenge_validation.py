import time
from dateutil import parser

from app.usecases.interfaces.clients.strava import IStravaClient
from app.usecases.interfaces.repos.challenges import IChallengesRepo
from app.usecases.interfaces.repos.strava import IStravaRepo
from app.usecases.interfaces.services.challange_validation import IChallengeValidation
from app.usecases.interfaces.services.email_manager import IEmailManager
from app.usecases.schemas.challenges import RetrieveChallengesAdapter
from app.usecases.schemas.strava import (
    StravaAccessInDb,
    StravaAccessUpdateAdapter,
    WebhookEvent,
)


class ChallengeValidation(IChallengeValidation):
    def __init__(
        self,
        strava_client: IStravaClient,
        strava_repo: IStravaRepo,
        challenges_repo: IChallengesRepo,
        email_manager: IEmailManager
        # Add ILogger here!
    ):
        self.strava_client = strava_client
        self.strava_repo = strava_repo
        self.challenges_repo = challenges_repo
        self.email_manager = email_manager

    async def validate(self, event: WebhookEvent) -> None:
        """Validates challenge."""

        # 1. Get athelete's access object
        athlete_access = await self.__obtain_access_object(athlete_id=event.owner_id)

        # 2. Get activity from Strava
        activity = await self.strava_client.get_activity(
            access_token=athlete_access.access_token, activity_id=event.object_id
        )

        # 3. Retrieve open challenges
        open_challenges = await self.challenges_repo.retrieve_many(
            query_params=RetrieveChallengesAdapter(
                challengee_user_id=athlete_access.user_id, challenge_complete=False
            )
        )

        # 4. Check for completeness. If complete, mark challenge as complete in database.
        for challenge in open_challenges:
            challenge_requirements = (
                activity.get("map").get("polyline"),
                activity.get("manual") == False,
                activity.get("distance") >= challenge.distance,
                activity.get("average_speed") >= challenge.pace,
                activity.get("type") == "Run",
                parser.parse(activity.get("start_date")).timestamp() > challenge.created_at.timestamp(),
            )
            
            if all(challenge_requirements):
                await self.challenges_repo.update_challenge(id=challenge.id)

            # 5. TODO: Send Challenge Complete Notification Email

    async def __obtain_access_object(self, athlete_id: int) -> StravaAccessInDb:
        """Returns athlete's access object. Access if refreshed if
        currently stored access object is stale."""

        current_access = await self.strava_repo.retrieve(athlete_id=athlete_id)

        if current_access.expires_at < time.time():
            new_access = await self.strava_client.refresh_token(
                refresh_token=current_access.refresh_token
            )

            return await self.strava_repo.update(
                athlete_id=athlete_id,
                updated_access=StravaAccessUpdateAdapter(
                    access_token=new_access.access_token,
                    refresh_token=new_access.refresh_token,
                    expires_at=new_access.expires_at,
                ),
            )

        return current_access
