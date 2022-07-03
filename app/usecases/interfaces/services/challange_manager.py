from abc import ABC, abstractmethod
from typing import List, Optional

from app.usecases.schemas.challenges import BountyVerification, IssueChallengeBody
from app.usecases.schemas.users import Participants


class IChallengeManager(ABC):
    @abstractmethod
    async def handle_challenge_issuance(self, payload: IssueChallengeBody) -> None:
        """Handles a newly issued challenge."""

    @abstractmethod
    async def handle_users(
        self,
        challenger_email: str,
        challenger_address: str,
        challengee_email: str,
        challengee_address: Optional[str] = None,
    ) -> Participants:
        """Retrieves or creates users."""

    @abstractmethod
    async def claim_bounty(self, address: str) -> List[BountyVerification]:
        """Performs actions necessary for a user to rightly claim a bounty."""
