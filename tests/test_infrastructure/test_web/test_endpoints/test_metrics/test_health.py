import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(test_client: AsyncClient) -> None:

    endpoint = "/metrics/health"

    response = await test_client.get(endpoint)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert response_data["status"] == "healthy"
    assert response_data["datetime"]
