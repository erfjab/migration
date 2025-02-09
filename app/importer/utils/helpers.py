import json
import pytz
import re
import hashlib

from functools import lru_cache
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, List

from . import config, logger
from ..models import MarzAdminData, MarzUserData, UserCreate, UserExpireStrategy

USERNAME_REGEXP = r"^\w{3,32}$"


@lru_cache(maxsize=1)
def get_exceptions_list():
    with open("exceptions.json", "r") as file:
        usernames = json.load(file)
    return usernames


def find_duplicates(username: str):
    lowercase_usernames = list(map(str.lower, username))
    duplicates = [
        item for item in lowercase_usernames if lowercase_usernames.count(item) > 1
    ]
    return list(set(duplicates))


def make_exceptions_list(json_file: str | Path = config.MARZBAN_USERS_DATA):
    try:
        file_path = Path(json_file)

        if not file_path.exists():
            logger.error(f"Marzban data file not found at: {file_path}")
            return None

        with file_path.open(encoding="utf-8") as file:
            data: Dict[str, List[dict]] = json.load(file)

        usernames = [user.get("username") for user in data["users"]]
        dup = find_duplicates(usernames)
        exceptions = []

        for username in usernames:
            # Replace '-' with '_' and check the regex pattern
            modified_u = username.replace("-", "_")
            is_valid_format = re.fullmatch(USERNAME_REGEXP, modified_u)
            is_not_duplicate = username.lower() not in dup
            is_unique_or_same = (
                modified_u not in usernames if modified_u != username else True
            )
            if not (is_valid_format and is_not_duplicate and is_unique_or_same):
                exceptions.append(username)

        with open("exceptions.json", "w") as file:
            json.dump(exceptions, file)
        return True
    except Exception as e:
        logger.error(e)
    return False


def gen_key(uuid: str) -> str:
    stripped = uuid.strip('"')
    return stripped.replace("-", "")

def MarzeUSERDATA_parse_args(users):
    output = []
    for user in users:
        _user = MarzUserData(id=user.get('id',None),
                             username=user.get('username',None),
                             status=user.get('status',None),
                             used_traffic=user.get('used_traffic',None),
                             data_limit=user.get('data_limit',None),
                             expire=user.get('expire',None),
                             created_at=user.get('created_at',None),
                             admin_id=user.get('admin_id',None),
                             data_limit_reset_strategy=user.get('data_limit_reset_strategy',None),
                             sub_revoked_at=user.get('sub_revoked_at',None),
                             note=user.get('note',None),
                             sub_updated_at=user.get('sub_updated_at',None),
                             sub_last_user_agent=user.get('sub_last_user_agent',None),
                             online_at=user.get('online_at',None),
                             edit_at=user.get('edit_at',None),
                             on_hold_timeout=user.get('on_hold_timeout',None),
                             on_hold_expire_duration=user.get('on_hold_expire_duration',None),
                             auto_delete_in_days=user.get('auto_delete_in_days',None),
                             last_status_change=user.get('last_status_change',None),
                             uuid=user.get('uuid',None),
                             proxy_type=user.get('proxy_type',None))
        output.append(_user)
    return output

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
        for user in MarzeUSERDATA_parse_args(data["users"]):
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
    if username in get_exceptions_list():
        clean = re.sub(r"[^\w]", "", username.lower())
        hash_str = str(
            int(hashlib.md5(username.encode()).hexdigest(), 16) % 10000
        ).zfill(4)
        username = f"{clean}_{hash_str}"[:32]
    else:
        username = (username.lower()).replace("-", "_")

    key = gen_key(old.uuid) if old.uuid is not None else None

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
        key=key,
    )
