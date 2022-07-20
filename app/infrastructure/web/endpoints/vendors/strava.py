from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import HTMLResponse
from pydantic import conint, constr

from app.dependencies import (
    get_challenge_validation_service,
    get_strava_client,
    get_strava_repo,
    get_users_repo,
)
from app.libraries.errors import ApplicationErrors
from app.settings import settings
from app.usecases.interfaces.clients.strava import IStravaClient
from app.usecases.interfaces.repos.strava import IStravaRepo
from app.usecases.interfaces.repos.users import IUsersRepo
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

    elif body.aspect_type == "update" and body.updates.get("authorized") == "false":
        # The user revoked access to this application
        await strava_repo.update(
            athlete_id=body.owner_id, updated_access=StravaAccessUpdateAdapter(scope=[])
        )


@strava_router.get(
    "/webhook",
    status_code=200,
    response_model=WebhookVerificationResponse,
)
async def validate_webhook_subscription(
    mode: constr(max_length=256) = Query(..., alias="hub.mode"),
    token: constr(max_length=256) = Query(..., alias="hub.verify_token"),
    challenge: constr(max_length=256) = Query(..., alias="hub.challenge"),
) -> WebhookVerificationResponse:
    """Echoes Strava challenge to validate webhook subscription."""

    if mode == "subscribe" and token == settings.verify_token:
        return WebhookVerificationResponse(challenge=challenge)

    raise await ApplicationErrors().unauthorized_access()


@strava_router.get(
    "/authorize",
    response_class=HTMLResponse,
)
async def receive_authorization_code(
    user_id: conint(lt=1000000000000) = Query(...),
    code: constr(max_length=256) = Query(...),
    scope: constr(max_length=256) = Query(...),
    strava_repo: IStravaRepo = Depends(get_strava_repo),
    users_repo: IUsersRepo = Depends(get_users_repo),
    strava_client: IStravaClient = Depends(get_strava_client),
) -> HTMLResponse:
    """Endpoint that users are redirected to upon authorizing this app."""

    user = await users_repo.retrieve(id=user_id)

    if not user:
        raise await ApplicationErrors().invalid_resource_id()

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

    html_content = """
        <html>
            <head>
                <title>It worked</title>
            </head>
            <body>
                <h1 style="text-align:center;font-family:'Avenir'">Strava integration was successful! You can now close this window.</h1>
            </body>
        </html>
    """

    return HTMLResponse(content=html_content, status_code=200)
