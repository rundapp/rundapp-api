from datetime import datetime
from typing import Any, List, Mapping, Optional

from pydantic import BaseModel, Field


####### Strava Client Models #######
class StravaException(Exception):
    """Generic exception"""


class RefreshTokenResponse(BaseModel):
    """Refresh token response returned from Strava."""

    token_type: str
    access_token: str
    expires_at: int
    expires_in: int
    refresh_token: str


####### Request Models #######
class WebhookEvent(BaseModel):
    """Event object sent from Strava."""

    object_type: str
    object_id: int
    aspect_type: str
    owner_id: int
    subscription_id: int
    event_time: int
    updates: Mapping[str, Any]


####### Response Models #######
class WebhookVerificationResponse(BaseModel):
    """Response echoed to Strava to verify webhook subscription."""

    challenge: str = Field(
        ...,
        alias="hub.challenge",
        description="Strava's issued challenge, which needs to be echoed back.",
        example="some_challange",
    )

    class Config:
        allow_population_by_field_name = True


class Athlete(BaseModel):
    id: int


class TokenExchangeResponse(BaseModel):
    token_type: str
    expires_at: int
    expires_in: int
    refresh_token: str
    access_token: str
    athlete: Athlete


###### Entities ######
class StravaAccessUpdateAdapter(BaseModel):
    """This model is utilized by the StravaRepo
    to create a new strava access object."""

    access_token: Optional[str] = Field(
        None,
        description="The access token neccessary to act on a Strava user's behalf.",
        example="d9d14255fa18a289610f34c33a703ec77a0ffd26",
    )
    refresh_token: Optional[str] = Field(
        None,
        description="The token used to obtain a new access token.",
        example="a9d14265fa18a289610f34c33a703ec77a0fgd29",
    )
    expires_at: Optional[int] = Field(
        None, description="The time elapsed in seconds since epoch.", example=1655511405
    )
    scope: Optional[List[str]] = Field(
        None,
        description="The permissions this app has, granted by the Strava user.",
        example=["activity:read_all", "read_all"],
    )


class CreateStravaAccessAdapter(BaseModel):
    """This model is utilized by the StravaRepo
    to create a new strava access object."""

    athlete_id: int = Field(
        ...,
        description="The Strava-assigned unique identifier for a Strava user.",
        example=12345,
    )
    user_id: int = Field(
        ...,
        description="This application's unique identifier for a user.",
        example=23456,
    )
    access_token: str = Field(
        ...,
        description="The access token neccessary to act on a Strava user's behalf.",
        example="d9d14255fa18a289610f34c33a703ec77a0ffd26",
    )
    refresh_token: str = Field(
        ...,
        description="The token used to obtain a new access token.",
        example="a9d14265fa18a289610f34c33a703ec77a0fgd29",
    )
    expires_at: int = Field(
        ..., description="The time elapsed in seconds since epoch.", example=1655511405
    )
    scope: List[str] = Field(
        ...,
        description="The permissions this app has, granted by the Strava user.",
        example=["activity:read_all", "read_all"],
    )


class StravaAccessInDb(CreateStravaAccessAdapter):
    """Database Model."""

    created_at: datetime = Field(
        ...,
        description="The time that the Strava access object was created.",
        example="2022-06-17 17:47:44.190912",
    )
    updated_at: datetime = Field(
        ...,
        description="The time that the Strava access object was last updated.",
        example="2022-06-17 17:47:44.190912",
    )
