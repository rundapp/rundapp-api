from typing import Optional

from fastapi import APIRouter, Body, Query, Response

from app.dependencies import (
    get_example_repo
)

from app.usecases.interfaces.example import IExampleRepo
from app.usecases.schemas import example


strava_router = APIRouter(tags=["Strava"])


# POST request to webhook
@strava_router.post(
    "/webhook",
    status_code=200,
    response_model=None,
)
async def event_received(
    body: example.WebhookEvent = Body(...),
) -> None:
    """Receives Strava webhook event"""
    print("EVENT_RECEIVED\n", body, "\n")


# GET request to webhook
@strava_router.get(
    "/webhook",
    status_code=200,
    response_model=dict,
)
async def validate_subscription(
    response: Response,
    mode: Optional[str] = Query(None, alias="hub.mode"),
    token: Optional[str] = Query(None, alias="hub.verify_token"),
    challenge: Optional[str] = Query(None, alias="hub.challenge")
) -> dict:
    """Echoes Strava challenge to validate webhook subscription"""

    # String chosen by the application owner when creating a subscription, which helps for client security.
    # An identical string will be included in the validation request made by Strava's subscription service.
    VERIFY_TOKEN = "STRAVA"

    if mode and token:
        # Verify that the mode and token sent are valid
        if mode == "subscribe" and token == VERIFY_TOKEN:
            # Respond with the challenge token from the request
            print("WEBHOOK_VERIFIED\n")
            return {"hub.challenge": challenge}
        else:
            response.status_code = 403


# GET request to root for user authentication
@strava_router.get(
    "/",
    status_code=200,
    response_model=None,
)
async def authenticate_user(
) -> None:
    """Allows users to authorize our app to access their data"""
    print("\nThank you.\n")
