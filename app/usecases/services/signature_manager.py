from eth_account.messages import encode_defunct
from web3.auto import w3 as web3

from app.settings import settings
from app.usecases.interfaces.services.signature_manager import ISignatureManager
from app.usecases.schemas.ethereum import SignedMessage


class SignatureManager(ISignatureManager):
    def __init__(self):
        pass

    async def sign(self, challenge_id: str) -> SignedMessage:
        """Signs a message."""

        message = encode_defunct(text=challenge_id)
        signed_message = web3.eth.account.sign_message(
            message, private_key=settings.private_key
        )

        return SignedMessage(
            message_hash=signed_message.messageHash.hex(),
            signature=signed_message.signature.hex(),
        )
