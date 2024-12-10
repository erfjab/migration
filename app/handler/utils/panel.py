import httpx
import json
from functools import lru_cache
from ..utils.log import logger
from ..models import UserResponse
from ..db import TokenManager
from ..utils.config import MARZNESHIN_ADDRESS, MARZNESHIN_USERNAME, MARZNESHIN_PASSWORD


async def get_token() -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MARZNESHIN_ADDRESS}/api/admins/token",
                data={"username": MARZNESHIN_USERNAME, "password": MARZNESHIN_PASSWORD},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            data = response.json()
            return data["access_token"]

    except Exception as e:
        logger.error(f"Error get token {str(e)}")
        return None


async def get_user(username: str) -> UserResponse:
    try:
        token = await TokenManager.get()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MARZNESHIN_ADDRESS}/api/users/{username}",
                headers={"Authorization": f"Bearer {token.token}"},
            )
            response.raise_for_status()
            data = response.json()
            return UserResponse(**data)

    except Exception as e:
        logger.error(f"Error get user {str(e)}")
        return None


@lru_cache(maxsize=1)
def get_exceptions_list():
    with open("exceptions.json", "r") as file:
        usernames = json.load(file)
    return usernames
