import os
from typing import List

import pytest_asyncio
import respx
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient

from app.dependencies import (
    get_users_repo,
)


DEFAULT_NUMBER_OF_INSERTED_OBJECTS = 3
NON_HASHED_USER_PASSWORD = "AFGADaHAF$HADFHA1R"
TEST_USERNAME = "inserted_name"

# Database Connection
@pytest_asyncio.fixture
async def test_db_url():
    return "postgres://{username}:{password}@{host}:{port}/{database_name}".format(
        username=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5444"),
        database_name=os.getenv("POSTGRES_DB", "blockrunner-dev-test"),
    )


@pytest_asyncio.fixture
async def test_db(test_db_url) -> Database:
    test_db = Database(url=test_db_url, min_size=5)

    await test_db.connect()
    yield test_db
    await test_db.execute("TRUNCATE assets CASCADE")
    await test_db.execute("TRUNCATE post_reactions CASCADE")
    await test_db.execute("TRUNCATE posts CASCADE")
    await test_db.disconnect()


# Repos (Database Gateways)
@pytest_asyncio.fixture
async def user_repo(test_db: Database) -> IUsersRepo:
    return UsersRepo(db=test_db)


@pytest_asyncio.fixture
async def stripe_client() -> IStripeClient:
    return MockStripeClient()


# Database-inserted Objects
@pytest_asyncio.fixture
async def inserted_user_object(
    user_repo: IUsersRepo,
) -> users.UserInDB:
    """Inserts a user object into the database for other tests."""
    return await user_repo.create(
        new_user=users.UserCreate(
            email="inserted@test.com",
            username="inserted_name",
            password=NON_HASHED_USER_PASSWORD,
            gender="FEMALE",
            birthdate="2002-11-27T06:00:00.000Z",
        ),
        password_context=CryptContext(schemes=["bcrypt"], deprecated="auto"),
    )


@pytest_asyncio.fixture
async def inserted_post_object(
    inserted_user_object: users.UserInDB,
    posts_repo: IPostsRepo,
) -> posts.PostInDB:
    """Inserts a post object into the database for other tests."""

    return await posts_repo.create(
        new_post=posts.CreatePostRepoAdapter(
            content="This is an inserted test post!",
            asset_symbol="TSLA",
            sentiment=posts.Sentiment.BULL,
            user_id=inserted_user_object.user_id,
            username=inserted_user_object.username,
        )
    )


thesis_title = "Test Thesis Title"


@pytest_asyncio.fixture
async def inserted_thesis_object(
    inserted_user_object: users.UserInDB,
    theses_repo: IThesesRepo,
) -> theses.ThesisInDB:
    """Inserts a thesis object into the database for other tests."""
    global thesis_title

    thesis_title += "1"

    return await theses_repo.create(
        thesis=theses.CreateThesisRepoAdapter(
            title=thesis_title,
            content="This is a test thesis on a test asset.",
            asset_symbol="BTC",
            sentiment=theses.Sentiment.BULL,
            sources=["https://www.pelleum.com", "https://www.youtube.com"],
            user_id=inserted_user_object.user_id,
            username=inserted_user_object.username,
        )
    )


@pytest_asyncio.fixture
async def create_thesis_object(
    inserted_user_object: users.UserInDB,
) -> theses.CreateThesisRepoAdapter:
    return theses.CreateThesisRepoAdapter(
        title="Test Thesis Title",
        content="This is a test thesis on a test asset.",
        asset_symbol="BTC",
        sentiment=theses.Sentiment.BULL,
        sources=["https://www.pelleum.com", "https://www.youtube.com"],
        user_id=inserted_user_object.user_id,
        username=inserted_user_object.username,
    )


@pytest_asyncio.fixture
async def many_inserted_theses(
    theses_repo: IThesesRepo, create_thesis_object: theses.CreateThesisRepoAdapter
) -> List[theses.ThesisInDB]:

    created_theses = []
    for i, _ in enumerate(range(DEFAULT_NUMBER_OF_INSERTED_OBJECTS)):
        create_thesis_object.title += str(i)
        created_theses.append(await theses_repo.create(thesis=create_thesis_object))

    return created_theses


@pytest_asyncio.fixture
async def create_post_object(
    inserted_user_object: users.UserInDB,
) -> posts.CreatePostRepoAdapter:
    return posts.CreatePostRepoAdapter(
        content="This is a test post!",
        asset_symbol="TSLA",
        sentiment=posts.Sentiment.BULL,
        user_id=inserted_user_object.user_id,
        username=inserted_user_object.username,
    )


@pytest_asyncio.fixture
async def many_inserted_posts(
    posts_repo: IPostsRepo,
    create_post_object: posts.CreatePostRepoAdapter,
) -> List[posts.PostInDB]:
    """Create many posts, so many post reactions can be created"""

    return [
        await posts_repo.create(new_post=create_post_object)
        for _ in range(DEFAULT_NUMBER_OF_INSERTED_OBJECTS)
    ]


@pytest_asyncio.fixture
async def inserted_subscription_object(
    subscriptions_repo: ISubscriptionsRepo, inserted_user_object: users.UserInDB
) -> subscriptions.SubscriptionInDB:
    new_record = subscriptions.SubscriptionRepoCreate(
        user_id=inserted_user_object.user_id,
        subscription_tier="PRO",
        stripe_customer_id="cus_123test",
        stripe_subscription_id="sub_123test",
        is_active=False,
    )
    return await subscriptions_repo.create(new_subscription=new_record)


@pytest_asyncio.fixture
def test_app(
    inserted_user_object: users.UserInDB,
    user_repo: IUsersRepo,

) -> FastAPI:
    app = setup_app()
    app.dependency_overrides[get_current_active_user] = lambda: inserted_user_object
    app.dependency_overrides[get_users_repo] = lambda: user_repo

    return app


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncClient:
    respx.route(host="test").pass_through()
    return AsyncClient(app=test_app, base_url="http://test")