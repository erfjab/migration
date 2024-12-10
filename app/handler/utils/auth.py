from base64 import b64decode, b64encode
from datetime import datetime
from hashlib import sha256
from typing import Union
from ..utils.config import MARZBAN_JWT_TOKEN
from jose import JWTError, jwt
from ..models import MarzbanToken


def get_subscription_payload(
    token: str,
) -> Union[MarzbanToken, None]:
    try:
        if len(token) < 15:
            return None

        if token.startswith("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."):
            payload = jwt.decode(token, MARZBAN_JWT_TOKEN, algorithms=["HS256"])
            if payload.get("access") == "subscription":
                return MarzbanToken(
                    username=payload["sub"],
                    created_at=datetime.utcfromtimestamp(payload["iat"]),
                )
            else:
                return None
        else:
            u_token, u_signature = token[:-10], token[-10:]
            try:
                u_token_dec = b64decode(
                    u_token.encode("utf-8")
                    + b"=" * (-len(u_token.encode("utf-8")) % 4),
                    altchars=b"-_",
                    validate=True,
                ).decode("utf-8")
            except:  # noqa: E722
                return None

            u_token_resign = b64encode(
                sha256((u_token + MARZBAN_JWT_TOKEN).encode("utf-8")).digest(),
                altchars=b"-_",
            ).decode("utf-8")[:10]

            if u_signature == u_token_resign:
                u_username, u_created_at = u_token_dec.split(",")
                return MarzbanToken(
                    username=u_username,
                    created_at=datetime.utcfromtimestamp(int(u_created_at)),
                )
            else:
                return None
    except JWTError:
        return None
