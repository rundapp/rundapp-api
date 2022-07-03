from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


##### Entities #####
class UserBase(BaseModel):
    """User base object."""

    email: str = Field(
        ..., description="A user's email address.", example="user@example.com"
    )
    address: Optional[str] = Field(
        None,
        description="A user's ethereum address.",
        example="0xb794f5ea0ba39494ce839613fffba74279579268",
    )
    name: Optional[str] = Field(
        None,
        description="A user's name.",
        example="Bob",
    )


class UserInDb(UserBase):
    """Database Model."""

    id: int = Field(
        ...,
        description="This application's unique identifier for a user.",
        example=23456,
    )
    create_at: datetime = Field(
        ...,
        description="The time that a user object was created.",
        example="2022-06-17 17:47:44.190912",
    )
    updated_at: datetime = Field(
        ...,
        description="The time that a user object was last updated.",
        example="2022-06-17 17:47:44.190912",
    )


class Participants(BaseModel):
    """The challenger and challengee for a given challenge."""

    challenger: UserInDb
    challengee: UserInDb
