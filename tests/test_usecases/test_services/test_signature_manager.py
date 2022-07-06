import os

from web3.auto import w3
import pytest

from app.usecases.interfaces.services.signature_manager import ISignatureManager
from app.usecases.schemas.challenges import ChallengeJoinPaymentAndUsers
from app.usecases.schemas.ethereum import SignedMessage



@pytest.mark.asyncio
async def test_sign(
    inserted_challenge_object: ChallengeJoinPaymentAndUsers,
    signature_manager_service: ISignatureManager,
) -> None:

    # 1. Call function
    signed_message = await signature_manager_service.sign(challenge_id=inserted_challenge_object.id)
    signer_address = w3.eth.account.recoverHash(signed_message.message_hash, signature=signed_message.signature)
    confirmed_signer_address=os.getenv("SIGNER_ADDRESS")

    # Assertions
    assert isinstance(signed_message, SignedMessage)
    assert signer_address == confirmed_signer_address