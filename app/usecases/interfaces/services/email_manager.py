from abc import ABC, abstractmethod

from app.usecases.schemas.challenges import ChallengeJoinPaymentAndUsers
from app.usecases.schemas.users import Participants


class IEmailManager(ABC):
    @abstractmethod
    async def send(self, sender: str, recipient: str, subject: str, body: str) -> None:
        """Sends an email."""

    @abstractmethod
    async def challenge_issuance_notification(
        self, participants: Participants, challenge: ChallengeJoinPaymentAndUsers
    ) -> None:
        """Notifies challenge participants."""
