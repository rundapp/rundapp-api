from fastapi import APIRouter, Body, Depends, Query

from app.dependencies import (
    get_challenge_validation_service,
    get_strava_client,
    get_strava_repo,
)
from app.libraries.errors import ApplicationErrors
from app.settings import settings
from app.usecases.interfaces.clients.strava import IStravaClient
from app.usecases.interfaces.repos.strava import IStravaRepo
from app.usecases.interfaces.services.challange_validation import IChallengeValidation
from app.usecases.schemas.strava import (
    CreateStravaAccessAdapter,
    StravaAccessUpdateAdapter,
    WebhookEvent,
    WebhookVerificationResponse,
)

strava_router = APIRouter(tags=["Strava"])


@strava_router.post(
    "/webhook",
    status_code=200,
    response_model=None,
)
async def receive_webhook(
    body: WebhookEvent = Body(...),
    challenge_validation_service: IChallengeValidation = Depends(
        get_challenge_validation_service
    ),
    strava_repo: IStravaRepo = Depends(get_strava_repo),
) -> None:
    """Receives Strava webhook event."""

    if body.aspect_type == "create" and body.object_type == "activity":
        # The event is a newly submitted activity, so validate it against a challenge
        await challenge_validation_service.validate(event=body)

    elif body.aspect_type == "update" and body.updates.get("authorized") == False:
        # The user revoked access to this application
        await strava_repo.update(updated_access=StravaAccessUpdateAdapter(scope=[]))


@strava_router.get(
    "/webhook",
    status_code=200,
    response_model=WebhookVerificationResponse,
)
async def validate_webhook_subscription(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge"),
) -> WebhookVerificationResponse:
    """Echoes Strava challenge to validate webhook subscription."""

    if mode == "subscribe" and token == settings.verify_token:
        return WebhookVerificationResponse(challenge=challenge)

    raise await ApplicationErrors().unauthorized_access()


@strava_router.get(
    "/authorize",
    status_code=200,
    response_model=None,
)
async def receive_authorization_code(
    user_id: str = Query(...),
    code: str = Query(...),
    scope: str = Query(...),
    strava_repo: IStravaRepo = Depends(get_strava_repo),
    strava_client: IStravaClient = Depends(get_strava_client),
) -> None:
    """Endpoint that users are redirected to upon authorizing this app."""

    access_response = await strava_client.exhange_code_for_token(code=code)

    await strava_repo.upsert(
        new_access=CreateStravaAccessAdapter(
            athlete_id=access_response.athlete.id,
            user_id=user_id,
            access_token=access_response.access_token,
            refresh_token=access_response.refresh_token,
            expires_at=access_response.expires_at,
            scope=scope.split(","),
        )
    )
