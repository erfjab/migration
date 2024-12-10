from typing import Optional, TypeVar, Type

import httpx
from pydantic import BaseModel

from . import logger, config
from ..models import (
    AdminCreate,
    AdminData,
    AdminToken,
    ServiceCreate,
    ServiceData,
    UserCreate,
    UserData,
    Inbounds,
    AdminUpdate,
)

T = TypeVar("T", bound=BaseModel)


class MarzneshinClient:
    def __init__(self, base_url: str = config.MARZNESHIN_ADDRESS):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[AdminToken] = None
        self._client = httpx.AsyncClient()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        response_model: Type[T],
        data: dict = None,
        params: dict = None,
        headers: dict = None,
        auth_required: bool = True,
    ) -> Optional[T]:
        """Generic method to make HTTP requests"""
        try:
            url = f"{self.base_url}{endpoint}"

            request_headers = {"Content-Type": "application/json"}
            if auth_required and self.token:
                request_headers["Authorization"] = f"Bearer {self.token.access_token}"
            if headers:
                request_headers.update(headers)

            response = await self._client.request(
                method=method,
                url=url,
                json=data if method not in ["GET"] else None,
                params=params if method in ["GET"] else None,
                headers=request_headers,
            )
            response.raise_for_status()

            return response_model(**response.json())

        except httpx.HTTPError:
            logger.error(
                f"HTTP error during {method} {endpoint}: {response.status_code if response else 'pass'}"
            )
            return None
        except Exception:
            logger.error(
                f"Unexpected error during {method} {endpoint}: {response.status_code if response else 'pass'}"
            )
            return None

    async def login(self, username: str, password: str) -> Optional[AdminData]:
        """Login and get access token"""
        try:
            response = await self._client.post(
                f"{self.base_url}/api/admins/token",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            self.token = AdminToken(**response.json())
            return self.token
        except Exception:
            return False

    async def create_admin(self, admin: AdminCreate) -> Optional[AdminData]:
        return await self._make_request(
            method="POST",
            endpoint="/api/admins",
            data=admin.dict(),
            response_model=AdminData,
        )

    async def get_admin(self, username: str) -> Optional[AdminData]:
        return await self._make_request(
            method="GET", endpoint=f"/api/admins/{username}", response_model=AdminData
        )

    async def update_admin(self, admin: AdminUpdate) -> Optional[AdminData]:
        return await self._make_request(
            method="PUT",
            endpoint=f"/api/admins/{admin.username}",
            data=admin.dict(),
            response_model=AdminData,
        )

    async def create_service(self, service: ServiceCreate) -> Optional[ServiceData]:
        return await self._make_request(
            method="POST",
            endpoint="/api/services",
            data=service.dict(),
            response_model=ServiceData,
        )

    async def get_service(self, service_id: int) -> Optional[ServiceData]:
        return await self._make_request(
            method="GET",
            endpoint=f"/api/services/{service_id}",
            response_model=ServiceData,
        )

    async def create_user(self, user: UserCreate) -> Optional[UserData]:
        return await self._make_request(
            method="POST",
            endpoint="/api/users",
            data=user.dict(),
            response_model=UserData,
        )

    async def get_user(self, username: str) -> Optional[UserData]:
        return await self._make_request(
            method="GET", endpoint=f"/api/users/{username}", response_model=UserData
        )

    async def get_inbounds(self) -> Optional[Inbounds]:
        return await self._make_request(
            method="GET", endpoint="/api/inbounds", response_model=Inbounds
        )