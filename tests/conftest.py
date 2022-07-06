import os
from typing import List

import pytest_asyncio
import respx
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient

from app.infrastructure.web.setup import setup_app

from tests.mocks.mock_strava_client import MockStravaClient
# Interfaces
from app.usecases.interfaces.repos.users import IUsersRepo
from app.usecases.interfaces.clients.strava import IStravaClient
from app.usecases.interfaces.repos.strava import IStravaRepo
from app.usecases.interfaces.repos.challenges import IChallengesRepo
from app.usecases.interfaces.services.challange_manager import IChallengeManager
from app.usecases.interfaces.services.signature_manager import ISignatureManager
from app.usecases.interfaces.services.email_manager import IEmailManager
from app.usecases.interfaces.services.challange_validation import IChallengeValidation

# Implementations
from app.infrastructure.db.repos.users import UsersRepo
from app.infrastructure.db.repos.strava import StravaRepo
from app.infrastructure.db.repos.challenges import ChallengesRepo
from app.usecases.services.challenge_manager import ChallengeManager
from app.usecases.services.signature_manager import SignatureManager
from app.usecases.services.email_manager import EmailManager
from app.usecases.services.challenge_validation import ChallengeValidation

# Schemas
from app.usecases.schemas.users import UserInDb, UserBase
from app.usecases.schemas.strava import CreateStravaAccessAdapter, StravaAccessInDb
from app.usecases.schemas.challenges import CreateChallengeRepoAdapter, ChallengeJoinPaymentAndUsers


from app.dependencies import (
    get_users_repo,
    get_strava_repo,
    get_strava_client,
    get_challenges_repo,
    get_challenge_manager_service,
    get_challenge_validation_service
)

# Testing Constants
CHALLENGE_PASSING_ACTIVITY_ID = 1
CHALLENGE_PASSING_DISTANCE = 10000.0
CHALLENGE_FAILING_ACTIVITY_ID = 2
CHALLENGE_FAILING_DISTANCE = 5000.0
CHALLENGER_ADDRESS = "0xb794f5ea0ba39494ce839613fffba74279579268"
CHALLENGEE_ADDRESS = "0x9E81eC9222C4F5F4B5f5C442033C94111C281657"
DEFAULT_NUMBER_OF_INSERTED_OBJECTS = 3

# Database Connection
@pytest_asyncio.fixture
async def test_db_url():
    return "postgres://{username}:{password}@{host}:{port}/{database_name}".format(
        username=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5444"),
        database_name=os.getenv("POSTGRES_DB", "rundapp-dev-test"),
    )


@pytest_asyncio.fixture
async def test_db(test_db_url) -> Database:
    test_db = Database(url=test_db_url, min_size=5)

    await test_db.connect()
    yield test_db
    await test_db.execute("TRUNCATE challenges CASCADE")
    await test_db.execute("TRUNCATE payments CASCADE")
    await test_db.execute("TRUNCATE users CASCADE")
    await test_db.execute("TRUNCATE strava_access CASCADE")
    await test_db.disconnect()


# Repos (Database Gateways)
@pytest_asyncio.fixture
async def user_repo(test_db: Database) -> IUsersRepo:
    return UsersRepo(db=test_db)

@pytest_asyncio.fixture
async def strava_repo(test_db: Database) -> IStravaRepo:
    return StravaRepo(db=test_db)

@pytest_asyncio.fixture
async def challenges_repo(test_db: Database) -> IChallengesRepo:
    return ChallengesRepo(db=test_db)


# Clients
@pytest_asyncio.fixture
async def strava_client() -> IStravaClient:
    return MockStravaClient()

# Services
@pytest_asyncio.fixture
async def signature_manager_service() -> ISignatureManager:
    return SignatureManager()

@pytest_asyncio.fixture
async def email_manager_service(strava_repo: IStravaRepo) -> IEmailManager:
    return EmailManager(strava_repo=strava_repo)


@pytest_asyncio.fixture
async def challenge_validation_service(
    strava_client: IStravaClient,
    strava_repo: IStravaRepo,
    challenges_repo: IChallengesRepo,
    email_manager_service: IEmailManager
) -> IChallengeValidation:
    
    return ChallengeValidation(
        strava_client=strava_client,
        strava_repo=strava_repo,
        challenges_repo=challenges_repo,
        email_manager=email_manager_service,
    )


@pytest_asyncio.fixture
async def challenge_manager_service(
    users_repo: IUsersRepo,
    challenges_repo: IChallengesRepo,
    signature_manager_service:  ISignatureManager, 
    email_manager_service: IEmailManager
) -> IChallengeManager:
    """ChallangerManager with test services and test repos."""
    return ChallengeManager(
        users_repo=users_repo,
        challenges_repo=challenges_repo,
        signature_manager=signature_manager_service,
        email_manager=email_manager_service,
    )


# Database-inserted Objects
@pytest_asyncio.fixture
async def inserted_user_object(
    user_repo: IUsersRepo,
) -> UserInDb:
    """Inserts a user object into the database for other tests."""
    return await user_repo.create(
        new_user=UserBase(
            email="test@example.com",
            address="0xb794f5ea0ba39494ce839613fffba74279579268",
            name="Bob"
        )
    )

@pytest_asyncio.fixture
async def two_inserted_user_objects(
    user_repo: IUsersRepo,
) -> List[UserInDb]:
    """Inserts a user object into the database for other tests."""

    addresses = (CHALLENGER_ADDRESS, CHALLENGEE_ADDRESS)

    two_users = []
    for count, address in enumerate(addresses):
        two_users.append(await user_repo.create(
            new_user=UserBase(
                email=f"test{count}@example.com",
                address=address,
                name=f"Bob{count}"
            )
        ))

    return two_users


@pytest_asyncio.fixture
async def create_strava_access_adapter(
    inserted_user_object: UserInDb,
) -> CreateStravaAccessAdapter:
    return CreateStravaAccessAdapter(
        athlete_id=12345,
        user_id=inserted_user_object.id,
        access_token="d9d14255fa18a289610f34c33a703ec77a0ffd26",
        refresh_token="a9d14265fa18a289610f34c33a703ec77a0fgd29",
        expires_at=1655511405,
        scope=["activity:read_all", "read_all"]
    )

@pytest_asyncio.fixture
async def inserted_strava_access_object(
    strava_repo: IStravaRepo,
    create_strava_access_adapter: CreateStravaAccessAdapter
) -> StravaAccessInDb:
    """Inserts a user object into the database for other tests."""
    return await strava_repo.upsert(
        new_access=create_strava_access_adapter
    )

@pytest_asyncio.fixture
async def create_challenge_repo_adapter(
    two_inserted_user_objects: List[UserInDb],
) -> CreateChallengeRepoAdapter:
    return CreateChallengeRepoAdapter(
        challenger=two_inserted_user_objects[0],
        challengee=two_inserted_user_objects[1],
        bounty=1000,
        distance=8000.0, # 8 kilometers
        pace=400        # seconds / kilometer
    )

@pytest_asyncio.fixture
async def inserted_challenge_object(
    create_challenge_repo_adapter: CreateChallengeRepoAdapter,
    challenges_repo: IChallengesRepo
) -> ChallengeJoinPaymentAndUsers:
    """Inserts a user object into the database for other tests."""
    
    return await challenges_repo.create(new_challenge=create_challenge_repo_adapter)


@pytest_asyncio.fixture
async def many_inserted_challenge_objects(
    create_challenge_repo_adapter: CreateChallengeRepoAdapter,
    challenges_repo: IChallengesRepo
) -> List[ChallengeJoinPaymentAndUsers]:
    """Inserts a user object into the database for other tests."""
    
    created_challenges = []
    for i, _ in enumerate(range(DEFAULT_NUMBER_OF_INSERTED_OBJECTS)):
        created_challenges.append(await challenges_repo.create(new_challenge=create_challenge_repo_adapter))

    return created_challenges


@pytest_asyncio.fixture
def test_app(
    strava_repo: IStravaRepo,
    strava_client: IStravaClient,
    get_challenges_repo: IChallengesRepo,
    challenge_manager_service: IChallengeManager,
    challenge_validation_service: IChallengeValidation,
    user_repo: IUsersRepo,
) -> FastAPI:
    app = setup_app()
    app.dependency_overrides[get_users_repo] = lambda: user_repo
    app.dependency_overrides[get_strava_repo] = lambda: strava_repo
    app.dependency_overrides[get_strava_client] = lambda: strava_client
    app.dependency_overrides[get_challenges_repo] = lambda: get_challenges_repo
    app.dependency_overrides[get_challenge_manager_service] = lambda: challenge_manager_service
    app.dependency_overrides[get_challenge_validation_service] = lambda: challenge_validation_service
    return app


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")