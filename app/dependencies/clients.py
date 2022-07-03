import aiohttp
from fastapi import Depends

from app.dependencies import get_client_session
from app.infrastructure.clients.strava import StravaClient
from app.settings import settings
from app.usecases.interfaces.clients.strava import IStravaClient


async def get_strava_client(
    client_session: aiohttp.client.ClientSession = Depends(get_client_session),
) -> IStravaClient:
    """Instantiate and return Strava client."""

    return StravaClient(
        client_session=client_session, base_url=settings.strava_base_url
    )
