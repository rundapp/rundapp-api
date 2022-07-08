from abc import ABC, abstractmethod

from app.usecases.schemas.challenges import ChallengeOnChain


class IEthereumClient(ABC):
    @abstractmethod
    def get_challenge(self, challenge_id: str) -> ChallengeOnChain:
        """Retrieves on-chain challenge by challenge_id."""
