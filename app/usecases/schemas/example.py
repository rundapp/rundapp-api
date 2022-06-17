from datetime import date, datetime
from enum import Enum

from typing import List, Optional, Any, Mapping

from pydantic import BaseModel, Field, constr


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    UNDISCLOSED = "UNDISCLOSED"


class WebhookEvent(BaseModel):
    object_type: str
    object_id: int
    aspect_type: str
    updates: Mapping[str, Any]
    owner_id: int
    subscription_id: int
    event_time: int


class UserBase(BaseModel):
    email: constr(max_length=100) = Field(
        ..., description="The user's email.", example="johndoe@example.com"
    )
    username: constr(max_length=15) = Field(
        ..., description="The user's Pelleum username.", example="johndoe"
    )
    gender: Gender = Field(...,
                           description="The user's gender.", example="FEMALE")
    birthdate: datetime = Field(
        ..., description="The user's birthdate.", example="2002-11-27T06:00:00.000Z"
    )


class UserCreate(UserBase):
    password: constr(max_length=100) = Field(
        ...,
        description="The user's Pelleum account password.",
        example="Examplepas$word",
    )


class UserUpdate(BaseModel):
    email: Optional[constr(max_length=100)] = Field(
        None, description="The user's email.", example="johndoe@example.com"
    )
    username: Optional[constr(max_length=15)] = Field(
        None, description="The user's Pelleum username.", example="johndoe"
    )
    password: Optional[constr(max_length=100)] = Field(
        None,
        description="The user's Pelleum account password.",
        example="Examplepas$word",
    )
    gender: Optional[Gender] = Field(
        None, description="The user's gender.", example="FEMALE"
    )
    birthdate: Optional[datetime] = Field(
        None, description="The user's birthdate.", example="2002-11-27T06:00:00.000Z"
    )


class UserResponse(UserBase):
    user_id: int
    is_active: bool
    is_verified: bool
    gender: Gender
    birthdate: date
    created_at: datetime
    updated_at: datetime


class UserByIdResponse(BaseModel):
    username: str
    user_id: int


class UserWithAuthTokenResponse(UserResponse):
    access_token: str
    token_type: str


class UserInDB(UserBase):
    """Database Model"""

    user_id: int
    hashed_password: str
    is_active: bool
    gender: Gender
    birthdate: date
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class BlockInDb(BaseModel):
    """Database Model"""

    user_id: int
    blocked_user_id: int
    created_at: datetime


class BlockData(BaseModel):
    user_blocks: Optional[List[int]]
    user_blocked_by: Optional[List[int]]
