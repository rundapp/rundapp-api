from typing import Optional

from databases import Database
from sqlalchemy import and_

from app.infrastructure.db.models.strava import STRAVA_ACCESS
from app.usecases.interfaces.repos.strava import IStravaRepo
from app.usecases.schemas.strava import (
    CreateStravaAccessAdapter,
    StravaAccessInDb,
    StravaAccessUpdateAdapter,
)


class StravaRepo(IStravaRepo):
    def __init__(self, db: Database):
        self.db = db

    async def upsert(self, new_access: CreateStravaAccessAdapter) -> StravaAccessInDb:
        """Inserts or updates a Strava access object."""

        insert_statment = STRAVA_ACCESS.insert().values(
            athlete_id=new_access.athlete_id,
            user_id=new_access.user_id,
            access_token=new_access.access_token,
            refresh_token=new_access.refresh_token,
            scope=new_access.scope,
            expires_at=new_access.expires_at,
        )

        upsert_statment = insert_statment.on_conflict_do_update(
            index_elements=[
                STRAVA_ACCESS.c.athlete_id,
            ],
            set_=dict(
                access_token=new_access.access_token,
                refresh_token=new_access.refresh_token,
                scope=new_access.scope,
                expires_at=new_access.expires_at,
            ),
        )

        athlete_id = await self.db.execute(upsert_statment)

        return await self.retrieve(athlete_id == athlete_id)

    async def retrieve(
        self, athlete_id: Optional[int] = None, user_id: Optional[int] = None
    ) -> Optional[StravaAccessInDb]:
        """Retreives and returns an access object by id."""

        query_conditions = []

        if athlete_id:
            query_conditions.append(STRAVA_ACCESS.c.athlete_id == athlete_id)

        if user_id:
            query_conditions.append(STRAVA_ACCESS.c.user_id == user_id)

        if len(query_conditions) == 0:
            raise Exception(
                "Please pass a condition parameter to query by to the function, retrieve()"
            )

        query = STRAVA_ACCESS.select().where(and_(*query_conditions))

        result = await self.db.fetch_one(query)
        return StravaAccessInDb(**result) if result else None

    async def update(
        self, athlete_id: int, updated_access: StravaAccessUpdateAdapter
    ) -> StravaAccessInDb:
        """Updates an access object."""

        query_prefix = STRAVA_ACCESS.update()

        updated_access_dict = {}
        updated_subscription_raw = updated_access.dict()
        for key, value in updated_subscription_raw.items():
            if value is not None:
                updated_access_dict[key] = value

        update_statement = query_prefix.values(updated_access_dict).where(
            STRAVA_ACCESS.c.athlete_id == athlete_id
        )

        await self.db.execute(update_statement)

        return await self.retrieve(athlete_id=athlete_id)
