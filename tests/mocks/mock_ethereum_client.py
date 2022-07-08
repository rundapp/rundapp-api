from app.usecases.schemas.challenges import ChallengeOnChain
from app.usecases.interfaces.clients.ethereum import IEthereumClient



class MockEthereumClient(IEthereumClient):

    def get_challenge(self, challenge_id: str) -> ChallengeOnChain:
        """Retrieves on-chain challenge by challenge_id."""
        
        return ChallengeOnChain(
            challenger="0x3f9E4A6120aB7868485602241AbE9D85d6F9E382",
            challengee="0xDe076D651613C7bde3260B8B69C860D67Bc16f49",
            bounty=14400000000000000,
            distance=10,
            speed=3,
            issuedAt=1657304490,
            complete=False,
        )