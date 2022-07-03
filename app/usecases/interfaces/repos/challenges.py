from abc import ABC, abstractmethod
from typing import Optional, List
from app.usecases.schemas.challenges import (
    ChallengeBase,
    ChallengeJoinPaymentAndUsers,
    ChallengeJoinPayment,
    RetrieveChallengesAdapter
)


class IChallengesRepo(ABC):
    @abstractmethod
    async def create(self, new_challenge: ChallengeBase) -> ChallengeJoinPayment:
        """Inserts and returns new challenge (and payment) object."""

    @abstractmethod
    async def retrieve(
        self,
        id: int,
    ) -> Optional[ChallengeJoinPayment]:
        """Retreives a challenge with payment information."""

    @abstractmethod
    async def retrieve_many(
        self,
        query_params: RetrieveChallengesAdapter,
    ) -> List[ChallengeJoinPaymentAndUsers]:
        """Retreives challenge objects by specified query parameters."""

    @abstractmethod
    async def update_challenge(self, id: int) -> ChallengeJoinPayment:
        """Updates a challenge."""

    @abstractmethod
    async def update_payment(self, id: int) -> None:
        """Marks a payment as complete."""
