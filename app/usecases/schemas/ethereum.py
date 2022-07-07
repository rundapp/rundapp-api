from pydantic import BaseModel


class SignedMessage(BaseModel):

    hashed_message: str
    signature: str
