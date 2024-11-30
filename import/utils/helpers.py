import json
import pytz
import re
import hashlib

from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, List

from utils import config, logger
from models import MarzAdminData, MarzUserData, UserCreate, UserExpireStrategy


def parse_marzban_data(
    json_file: str | Path = config.MARZBAN_USERS_DATA,
) -> Optional[Tuple[List[MarzAdminData], Dict[str, List[MarzUserData]]]]:
    try:
        file_path = Path(json_file)

        if not file_path.exists():
            logger.error(f"Marzban data file not found at: {file_path}")
            return None

        with file_path.open(encoding="utf-8") as file:
            data: Dict[str, List[dict]] = json.load(file)

        if not all(key in data for key in ("users", "admins", "jwt")):
            logger.error(
                "Missing required keys 'users' or 'admins' or 'jwt' in JSON data"
            )
            return None

        admins = [MarzAdminData(**admin) for admin in data["admins"]]
        admins.append(
            MarzAdminData(
                id=99999999,
                username="bear",
                hashed_password="bear",
                created_at=datetime.now(),
                is_sudo=0,
            )
        )
        admin_map = {admin.id: admin.username for admin in admins}

        users_by_admin = defaultdict(list)
        for user in [MarzUserData(**user) for user in data["users"]]:
            users_by_admin[admin_map.get(user.admin_id, "bear")].append(user)

        users_by_admin = dict(users_by_admin)

        logger.info(
            f"Parsed {len(data['users'])} users across {len(users_by_admin)} admin groups"
        )
        return admins, dict(users_by_admin)

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {str(e)}")
        return None

    except KeyError as e:
        logger.error(f"Missing required key in data structure: {str(e)}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error parsing Marzban data: {str(e)}")
        logger.exception(e)
        return None


def parse_marz_user(old: MarzUserData, service: int) -> UserCreate:
    if old.data_limit:
        remaining_data = old.data_limit - old.used_traffic
        data_limit = 1024 * 1024 if remaining_data <= 0 else remaining_data
    else:
        data_limit = 0

    tehran_tz = pytz.timezone("Asia/Tehran")
    expire_date = (
        datetime.fromtimestamp(old.expire, tz=timezone.utc)
        .astimezone(tehran_tz)
        .isoformat()
        if old.expire
        else None
    )

    username = old.username
    clean = re.sub(r"[^\w]", "", username.lower())
    hash_str = str(int(hashlib.md5(username.encode()).hexdigest(), 16) % (10 ** config.USERNAME_SUFFIX)).zfill(config.USERNAME_SUFFIX)
    username = f"{clean}_{hash_str}"[:32]

    return UserCreate(
        username=username,
        data_limit=data_limit,
        data_limit_reset_strategy=old.data_limit_reset_strategy,
        expire_strategy=(
            UserExpireStrategy.START_ON_FIRST_USE
            if old.status == "on_hold"
            else (
                UserExpireStrategy.FIXED_DATE
                if old.expire
                else UserExpireStrategy.NEVER
            )
        ),
        note=old.note or "",
        usage_duration=old.on_hold_expire_duration if old.status == "on_hold" else None,
        activation_deadline=(
            old.on_hold_timeout.isoformat()
            if old.status == "on_hold" and old.on_hold_timeout
            else None
        ),
        service_ids=[service],
        expire_date=expire_date,
        created_at=old.created_at.isoformat() if old.created_at else None,
        sub_revoked_at=old.sub_revoked_at.isoformat() if old.sub_revoked_at else None,
    )
