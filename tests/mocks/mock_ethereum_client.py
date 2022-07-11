from app.usecases.schemas.challenges import ChallengeOnChain
from app.usecases.interfaces.clients.ethereum import IEthereumClient

from tests.constants import TEST_CHALLENGE_ID, TEST_CHALLENGE_ID_NOT_FOUND



class MockEthereumClient(IEthereumClient):

    def get_challenge(self, challenge_id: str) -> ChallengeOnChain:
        """Retrieves on-chain challenge by challenge_id."""

        onchain_challenge = ChallengeOnChain(
            challengeId="4fbf9ee4-5aba-4b79-a62c-7f5ec1a4ecd1",
            challenger="0x3f9E4A6120aB7868485602241AbE9D85d6F9E382",
            challengee="0xDe076D651613C7bde3260B8B69C860D67Bc16f49",
            bounty=14400000000000000,
            distance=10,
            speed=3,
            issuedAt=1657304490,
            complete=False,
        )

        if challenge_id == TEST_CHALLENGE_ID:
            onchain_challenge.complete = True
        elif challenge_id == TEST_CHALLENGE_ID_NOT_FOUND:
            onchain_challenge.challengee = "0x0000000000000000000000000000000000000000"
            onchain_challenge.challenger = "0x0000000000000000000000000000000000000000"

        return onchain_challenge