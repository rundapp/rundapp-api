from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas.challenges import (
    ChallengeJoinPayment,
    ChallengeJoinPaymentAndUsers,
    CreateChallengeRepoAdapter,
    RetrieveChallengesAdapter,
)


class IChallengesRepo(ABC):
    @abstractmethod
    async def create(
        self, new_challenge: CreateChallengeRepoAdapter
    ) -> ChallengeJoinPaymentAndUsers:
        """Inserts and returns new challenge (and payment) object."""

    @abstractmethod
    async def retrieve(
        self,
        id: int,
    ) -> Optional[ChallengeJoinPaymentAndUsers]:
        """Retreives a challenge with payment information."""

    @abstractmethod
    async def retrieve_many(
        self,
        query_params: RetrieveChallengesAdapter,
    ) -> List[ChallengeJoinPaymentAndUsers]:
        """Retreives challenge objects by specified query parameters."""

    @abstractmethod
    async def update_challenge(self, id: int) -> ChallengeJoinPaymentAndUsers:
        """Updates a challenge."""

    @abstractmethod
    async def update_payment(self, id: int) -> None:
        """Marks a payment as complete."""
