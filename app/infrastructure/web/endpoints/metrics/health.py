from datetime import datetime

from fastapi import APIRouter

health_router = APIRouter(tags=["health"])


@health_router.get("")
async def health_check():

    return {"status": "healthy", "datetime": datetime.now().isoformat()}
