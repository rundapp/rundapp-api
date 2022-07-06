import pytest

from app.usecases.interfaces.repos.strava import IStravaRepo
from app.usecases.schemas.strava import CreateStravaAccessAdapter, StravaAccessInDb


@pytest.mark.asyncio
async def test_upsert(
    strava_repo: IStravaRepo, create_strava_access_adapter: CreateStravaAccessAdapter
) -> None:

    # Test Create
    test_strava_access_object = await strava_repo.upsert(
        new_access=create_strava_access_adapter
    )

    assert isinstance(test_strava_access_object, StravaAccessInDb)
    for key, value in test_strava_access_object.dict().items():
        if key not in ("created_at", "updated_at"):
            assert value == create_strava_access_adapter[key]

    # Test Update
    updated_create_strava_access_adapter = create_strava_access_adapter.copy()
    updated_create_strava_access_adapter.access_token = "new-token"
    updated_create_strava_access_adapter.refresh_token = "new-refresh-token"
    updated_create_strava_access_adapter.expires_at = 1656872859

    udpated_test_strava_access_object = await strava_repo.upsert(
        new_access=updated_create_strava_access_adapter
    )

    assert isinstance(udpated_test_strava_access_object, StravaAccessInDb)
    assert (
        test_strava_access_object.athlete_id
        == udpated_test_strava_access_object.athlete_id
    )
    for key, value in udpated_test_strava_access_object.dict().items():
        if key not in ("created_at", "updated_at"):
            assert value == updated_create_strava_access_adapter[key]


@pytest.mark.asyncio
async def test_retrieve(
    strava_repo: IStravaRepo, inserted_strava_access_object: StravaAccessInDb
) -> None:

    test_strava_access_object = await strava_repo.retrieve(
        athlete_id=inserted_strava_access_object
    )

    assert isinstance(test_strava_access_object, StravaAccessInDb)
    for key, value in test_strava_access_object.dict().items():
        assert value == inserted_strava_access_object[key]


@pytest.mark.asyncio
async def test_update(
    strava_repo: IStravaRepo, inserted_strava_access_object: StravaAccessInDb
) -> None:

    updated_test_strava_access_object = await strava_repo.update(
        athlete_id=inserted_strava_access_object.athlete_id,
        updated_access=StravaAccessUpdateAdapter(scope=[]),
    )

    assert isinstance(updated_test_strava_access_object, StravaAccessInDb)
    assert updated_test_strava_access_object.scope == []
