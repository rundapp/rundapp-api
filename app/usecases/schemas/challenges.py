from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, constr

##### Exceptions #####


class ChallengeException(Exception):
    """General Challenge Exception."""


class ChallengeBase(BaseModel):
    """A base challenge object."""

    bounty: int = Field(
        ...,
        description="The amount in WEI the challengee receives upon challenge completion.",
        example=1000000000000,
    )
    distance: float = Field(
        ...,
        description="The distance in miles the challengee must run to complete the challenge.",
        example=10000.00,
    )
    pace: Optional[float] = Field(
        None,
        description="The average time (seconds) per mile of the specified distance the challenge must acheive during the run.",
        example=500,
    )


class CreateChallengeRepoAdapter(ChallengeBase):
    """Model used to save new challenge in database."""

    id: str = Field(
        ...,
        description="The unique identifier of the challege associated with the bounty.",
        example="9ffb6aa3-d776-4ee6-9423-3013a8e5168f",
    )
    challenger: int = Field(
        ...,
        description="A foreign key user ID that represents the person that issued the challenge.",
        example=23456,
    )
    challengee: int = Field(
        ...,
        description="A foreign key user ID that represents the person that was challenged.",
        example=34567,
    )


class ChallengeInDb(CreateChallengeRepoAdapter):
    """Database Model."""

    complete: bool = Field(
        ...,
        description="Whether of not the challenge has been completed.",
        example=True,
    )
    created_at: datetime = Field(
        ...,
        description="The time that the challenge was issued.",
        example="2022-06-17 17:47:44.190912",
    )
    updated_at: datetime = Field(
        ...,
        description="The time that the challenge was completed.",
        example="2022-06-18 17:47:44.190912",
    )


class ChallengeJoinPayment(ChallengeInDb):
    """Challenge and payment table objects joined."""

    payment_complete: bool = Field(
        ..., description="Whether or not a payment has completed.", example=True
    )
    payment_id: int = Field(
        ..., description="The unique identifier for a payment object.", example=True
    )


class ChallengeJoinPaymentAndUsers(ChallengeJoinPayment):
    """Challenge, users, and payment table objects joined."""

    challengee_address: Optional[str] = Field(
        None,
        description="Challengee's ethereum address.",
        example="0xb794f5ea0ba39494ce839613fffba74279579268",
    )
    challenger_address: Optional[str] = Field(
        None,
        description="Challenger's ethereum address.",
        example="0xb794f5ea0ba39494ce839613fffba74279579268",
    )


class RetrieveChallengesAdapter(BaseModel):
    """Parameters to query challenges by."""

    challengee_user_id: Optional[int]
    challenger_user_id: Optional[int]
    challengee_address: Optional[str]
    challenger_address: Optional[str]
    challenge_complete: Optional[bool]
    payment_complete: Optional[bool]


##### On-chain Response #####
class ChallengeOnChain(BaseModel):
    challenger: str
    challengee: str
    bounty: int
    distance: int
    speed: int
    issuedAt: int
    complete: bool


##### Request Models #####
class IssueChallengeBody(BaseModel):
    """JSON body sent when a challenge is issued."""

    challenger_name: Optional[constr(max_length=100)] = Field(
        None,
        description="The name of the challenger.",
        example="Bob",
    )
    challengee_name: Optional[constr(max_length=100)] = Field(
        None,
        description="The name of the challengee.",
        example="Alice",
    )
    challenger_email: constr(max_length=100) = Field(
        ...,
        description="The email addresss of the challenger.",
        example="challenger@example.com",
    )
    challengee_email: constr(max_length=100) = Field(
        ...,
        description="The email addresss of the challengee.",
        example="challengee@example.com",
    )
    challenge_id: str = Field(
        ...,
        description="The unique identifier of the challege associated with the bounty.",
        example="9ffb6aa3-d776-4ee6-9423-3013a8e5168f",
    )


class BountyVerification(BaseModel):
    """Bounty verification model for rightly claimed bounties."""

    challenge: ChallengeJoinPaymentAndUsers
    hashed_message: str = Field(
        ...,
        description="A hashed message (hexademical string) for contract signature verification.",
        example="0x43bdcd52f31fc1ff9e00b231d89f8e6692d1124c622afac4e5e48df72c86b119",
    )
    signature: str = Field(
        ...,
        description="A 'signed' hashed message for contract signature verification.",
        example="0x3b99982e7faf1bc4a328ce993c15af402b9179a18eea2738e87b26936f5c5b4f66488db49d255a57c84a0a72",
    )


##### Response Models #####
class ClaimBountyResponse(BaseModel):
    """Response model for rightly claiming bounties."""

    verified_bounties: List[BountyVerification]
