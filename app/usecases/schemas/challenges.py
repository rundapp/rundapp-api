from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, constr


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

    id: str = Field(..., description="The challenge ID in database.", example=12345)
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

    address: Optional[str] = Field(
        None,
        description="A user's ethereum address.",
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


class BountyVerification(BaseModel):
    """Bounty verification model for rightly claimed bounties."""

    challenge_id: str = Field(
        ...,
        description="The unique identifier of the challege associated with the bounty.",
        example="9ffb6aa3-d776-4ee6-9423-3013a8e5168f",
    )
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


##### Request Models #####
class IssueChallengeBody(ChallengeBase):
    """JSON body sent when a challenge is issued."""

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
    challengee_address: Optional[constr(min_length=42, max_length=42)] = Field(
        None,
        description="The Ethereum addresss of the challengee.",
        example="0xcF107AdC80c7F7b5eE430B52744F96e2D76681a2",
    )
    challenger_address: constr(min_length=42, max_length=42) = Field(
        ...,
        description="The Ethereum addresss of the challenger.",
        example="0x63958fDFA9DAF21bb9bE4312c3f53cb080DA80D8",
    )


##### Response Models #####
class ClaimBountyResponse(BaseModel):
    """Response model for rightly claiming bounties."""

    verified_bounties: List[BountyVerification]
