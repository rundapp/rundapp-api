from abc import ABC, abstractmethod
from typing import Optional

from app.usecases.schemas.strava import (
    CreateStravaAccessAdapter,
    StravaAccessInDb,
    StravaAccessUpdateAdapter,
)


class IStravaRepo(ABC):
    @abstractmethod
    async def upsert(self, new_access: CreateStravaAccessAdapter) -> StravaAccessInDb:
        """Inserts or updates a Strava access object."""

    @abstractmethod
    async def retrieve(
        self, athlete_id: int, user_id: int
    ) -> Optional[StravaAccessInDb]:
        """Retreives and returns an access object by id."""

    @abstractmethod
    async def update(
        self, updated_access: StravaAccessUpdateAdapter
    ) -> StravaAccessInDb:
        """Updates an access object."""
