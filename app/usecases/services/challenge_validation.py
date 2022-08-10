import time

from dateutil import parser

from app.usecases.interfaces.clients.strava import IStravaClient
from app.usecases.interfaces.repos.challenges import IChallengesRepo
from app.usecases.interfaces.repos.strava import IStravaRepo
from app.usecases.interfaces.repos.users import IUsersRepo
from app.usecases.interfaces.services.challange_validation import IChallengeValidation
from app.usecases.interfaces.services.conversion_manager import IConversionManager
from app.usecases.interfaces.services.email_manager import IEmailManager
from app.usecases.schemas.challenges import (
    ChallengeJoinPaymentAndUsers,
    CompletedChallenge,
    RetrieveChallengesAdapter,
)
from app.usecases.schemas.strava import (
    StravaAccessInDb,
    StravaAccessUpdateAdapter,
    WebhookEvent,
)
from app.usecases.schemas.users import Participants


class ChallengeValidation(IChallengeValidation):
    def __init__(
        self,
        strava_client: IStravaClient,
        strava_repo: IStravaRepo,
        users_repo: IUsersRepo,
        challenges_repo: IChallengesRepo,
        email_manager: IEmailManager,
        conversion_manager: IConversionManager,
    ):
        self.strava_client = strava_client
        self.strava_repo = strava_repo
        self.users_repo = users_repo
        self.challenges_repo = challenges_repo
        self.email_manager = email_manager
        self.conversion_manager = conversion_manager

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
                activity.get("distance") >= (challenge.distance / 100),  # Meters
                activity.get("average_speed")
                >= (challenge.pace / 100),  # Meters/Second
                activity.get("type") == "Run" or activity.get("type") == "Walk",
                parser.parse(activity.get("start_date")).timestamp()
                > challenge.created_at.timestamp(),
            )

            if all(challenge_requirements):
                await self.challenges_repo.update_challenge(id=challenge.id)

                # 5. Stored challenge unit conversion.
                challenge.distance = self.conversion_manager.cm_to_miles(
                    distance=challenge.distance
                )
                challenge.pace = (
                    self.conversion_manager.cm_per_second_to_minutes_per_mile(
                        pace=challenge.pace
                    )
                )

                # 5. Send challenge completion notification
                participants = await self.__retrieve_participants(challenge=challenge)
                await self.email_manager.completed_challenge_notification(
                    participants=participants,
                    challenge=challenge,
                    completed_challenge=CompletedChallenge(
                        distance=self.conversion_manager.cm_to_miles(
                            distance=activity.get("distance") * 100
                        ),
                        pace=self.conversion_manager.cm_per_second_to_minutes_per_mile(
                            pace=activity.get("average_speed") * 100
                        ),
                    ),
                )

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

    async def __retrieve_participants(
        self, challenge: ChallengeJoinPaymentAndUsers
    ) -> Participants:

        return Participants(
            challenger=await self.users_repo.retrieve(id=challenge.challenger),
            challengee=await self.users_repo.retrieve(id=challenge.challengee),
        )
