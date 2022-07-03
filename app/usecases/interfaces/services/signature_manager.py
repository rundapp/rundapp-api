from abc import ABC, abstractmethod

from app.usecases.schemas.ethereum import SignedMessage


class ISignatureManager(ABC):
    @abstractmethod
    async def sign(self, challenge_id: str) -> SignedMessage:
        """Signs a message."""
