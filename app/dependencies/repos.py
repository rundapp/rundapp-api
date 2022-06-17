from app.infrastructure.db.core import get_or_create_database
from app.infrastructure.db.repos.example import ExampleRepo
from app.usecases.interfaces.example import IExampleRepo


async def get_example_repo() -> IExampleRepo:
    return ExampleRepo(db=await get_or_create_database())
