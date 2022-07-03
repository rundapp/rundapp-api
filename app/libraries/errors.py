from fastapi import HTTPException, status


class ApplicationErrors:
    def __init__(self, detail: str = None):
        self.detail = detail

    async def unauthorized_access(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=self.detail if self.detail else "Unauthorized access.",
        )

    async def forbidden_access(self):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=self.detail if self.detail else "Forbidden resources.",
        )

    async def invalid_resource_id(self):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=self.detail
            if self.detail
            else "The supplied resource ID is invalid.",
        )
