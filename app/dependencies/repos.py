from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.db.repos.challenges import ChallengesRepo
from app.infrastructure.db.repos.strava import StravaRepo
from app.infrastructure.db.repos.users import UsersRepo
from app.usecases.interfaces.repos.challenges import IChallengesRepo
from app.usecases.interfaces.repos.strava import IStravaRepo
from app.usecases.interfaces.repos.users import IUsersRepo


async def get_strava_repo() -> IStravaRepo:
    return StravaRepo(db=await get_or_create_database())


async def get_challenges_repo() -> IChallengesRepo:
    return ChallengesRepo(db=await get_or_create_database())


async def get_users_repo() -> IUsersRepo:
    return UsersRepo(db=await get_or_create_database())
