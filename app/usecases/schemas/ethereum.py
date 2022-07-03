from pydantic import BaseModel


class SignedMessage(BaseModel):

    message_hash: str
    signature: str
