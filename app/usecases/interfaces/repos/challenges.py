from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas.challenges import (
    ChallengeBase,
    ChallengeJoinPayment,
    ChallengeJoinPaymentAndUsers,
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
        challengee_user_id: Optional[int] = None,
        challenger_user_id: Optional[int] = None,
        challengee_address: Optional[int] = None,
        challenger_address: Optional[int] = None,
        complete_value: Optional[bool] = None,
    ) -> List[ChallengeJoinPaymentAndUsers]:
        """Retreives challenge objects by specified query parameters."""

    @abstractmethod
    async def update_challenge(self, id: int) -> ChallengeJoinPayment:
        """Updates a challenge."""

    @abstractmethod
    async def update_payment(self, id: int) -> None:
        """Marks a payment as complete."""
