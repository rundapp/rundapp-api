import base64
import json

import aiohttp
from fastapi import Depends

from app.dependencies import get_client_session
from app.infrastructure.clients.ethereum import EthereumClient
from app.infrastructure.clients.strava import StravaClient
from app.settings import settings
from app.usecases.interfaces.clients.ethereum import IEthereumClient
from app.usecases.interfaces.clients.strava import IStravaClient


async def get_strava_client(
    client_session: aiohttp.client.ClientSession = Depends(get_client_session),
) -> IStravaClient:
    """Instantiate and return Strava client."""

    return StravaClient(
        client_session=client_session, base_url=settings.strava_base_url
    )


async def get_ethereum_client() -> IEthereumClient:
    """Instantiate and return Ethereum client."""

    return EthereumClient(
        abi=json.loads(base64.b64decode(settings.abi)), rpc_url=settings.rpc_url
    )
