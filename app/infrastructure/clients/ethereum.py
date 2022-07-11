from web3 import Web3

from app.settings import settings
from app.usecases.interfaces.clients.ethereum import IEthereumClient
from app.usecases.schemas.challenges import ChallengeOnChain


class EthereumClient(IEthereumClient):
    """Faciliates communication with deployed smart contract."""

    def __init__(self, abi: list, rpc_url: str):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract = self.web3.eth.contract(
            address=settings.contract_address, abi=abi
        )

    def get_challenge(self, challenge_id: str) -> ChallengeOnChain:
        """Retrieves on-chain challenge by challenge_id."""

        response = self.contract.functions.challengeLookup(challenge_id).call()

        return ChallengeOnChain(
            challengeId=response[0],
            challenger=response[1],
            challengee=response[2],
            bounty=response[3],
            distance=response[4],
            speed=response[5],
            issuedAt=response[6],
            complete=response[7],
        )
