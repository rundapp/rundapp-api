import pytest
import pytest_asyncio

from app.usecases.interfaces.repos.users import IUsersRepo
from app.usecases.schemas.users import UserBase, UserInDb


@pytest_asyncio.fixture
def user_base_object() -> UserBase:
    return UserBase(
        email="test@example.com",
        address="0xb794f5ea0ba39494ce839613fffba74279579268",
        name="Bob",
    )


@pytest.mark.asyncio
async def test_create(users_repo: IUsersRepo, user_base_object: UserBase) -> None:

    test_user = await users_repo.create(new_user=user_base_object)

    assert isinstance(test_user, UserInDb)
    assert test_user.email == user_base_object.email
    assert test_user.address == user_base_object.address
    assert test_user.name == user_base_object.name


@pytest.mark.asyncio
async def test_retrieve(users_repo: IUsersRepo, inserted_user_object: UserInDb) -> None:

    test_user = await users_repo.retrieve(id=inserted_user_object.id)

    assert isinstance(test_user, UserInDb)
    assert test_user.email == inserted_user_object.email
    assert test_user.address == inserted_user_object.address
    assert test_user.name == inserted_user_object.name


@pytest.mark.asyncio
async def test_update(users_repo: IUsersRepo, inserted_user_object: UserInDb) -> None:

    updated_address = "0x9E81eC9222C4F5F4B5f5C442033C94111C281657"

    test_user = await users_repo.update(
        id=inserted_user_object.id, address=updated_address
    )

    assert isinstance(test_user, UserInDb)
    assert test_user.address == updated_address
