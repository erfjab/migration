import httpx
import re
import hashlib

from fastapi import APIRouter, HTTPException, status, Request, Response
from utils.log import logger
from utils import auth, panel
from utils.config import MARZBAN_XRAY_SUBSCRIPTION_PATH, USERNAME_SUFFIX

router = APIRouter(tags=["Subscription"], prefix=f"/{MARZBAN_XRAY_SUBSCRIPTION_PATH}")


@router.get("/{token}/")
@router.get("/{token}", include_in_schema=False)
async def upsert_user(request: Request, token: str):
    sub = auth.get_subscription_payload(token=token)
    if not sub:
        raise HTTPException(status_code=400, detail="Invalid subscription token")

    username = sub.username
    clean = re.sub(r"[^\w]", "", username.lower())
    hash_str = str(int(hashlib.md5(username.encode()).hexdigest(), 16) % (10 ** USERNAME_SUFFIX)).zfill(USERNAME_SUFFIX)
    username = f"{clean}_{hash_str}"[:32]

    dbuser = await panel.get_user(username)
    if not dbuser or dbuser.created_at > sub.created_at:
        raise HTTPException(
            status_code=404, detail="User not found or invalid creation date"
        )

    if dbuser.sub_revoked_at and dbuser.sub_revoked_at > sub.created_at:
        raise HTTPException(status_code=403, detail="Subscription has been revoked")

    try:
        # Check if subscription_url exists
        if not dbuser.subscription_url:
            raise HTTPException(
                status_code=404, detail="Subscription URL not found for user"
            )

        headers = dict(request.headers)
        headers.pop("host", None)
        params = dict(request.query_params)

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                f"{dbuser.subscription_url}",
                headers=headers,
                params=params,
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type", "text/plain"),
            )

    except httpx.RequestError as e:
        logger.error(f"Error forwarding subscription request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error forwarding subscription request",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
