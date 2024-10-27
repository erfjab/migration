import secrets
from pydantic import BaseModel,Field,field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ProxyType(str, Enum):
    VLESS = 'VLESS'
    VMess = 'VMess'

class UserDataUsageResetStrategy(str, Enum):
    no_reset = "no_reset"
    day = "day"
    week = "week"
    month = "month"
    year = "year"


class UserExpireStrategy(str, Enum):
    NEVER = "never"
    FIXED_DATE = "fixed_date"
    START_ON_FIRST_USE = "start_on_first_use"


class UserCreate(BaseModel):
    activation_deadline: Optional[str]
    data_limit: int
    data_limit_reset_strategy: UserDataUsageResetStrategy
    expire_strategy: UserExpireStrategy
    expire_date: Optional[str]
    note: Optional[str] = ""
    service_ids: List[int]
    usage_duration: Optional[int]
    username: str
    sub_revoked_at: Optional[str]
    created_at: str
    key:str = Field(default_factory=lambda: secrets.token_hex(16))
    
    @field_validator('key', mode='before')
    def set_default_if_none(cls, value):
        return value or secrets.token_hex(16)


class UserData(BaseModel):
    id: int
    username: str
    expire_strategy: UserExpireStrategy
    expire_date: Optional[datetime]
    usage_duration: Optional[int]
    activation_deadline: Optional[datetime]
    key: str
    data_limit: Optional[int]
    data_limit_reset_strategy: UserDataUsageResetStrategy
    note: Optional[str]
    sub_updated_at: Optional[datetime]
    sub_last_user_agent: Optional[str]
    online_at: Optional[datetime]
    activated: bool
    is_active: bool
    expired: bool
    data_limit_reached: bool
    enabled: bool
    used_traffic: int
    lifetime_used_traffic: int
    created_at: datetime
    service_ids: List[int]
    subscription_url: str
    owner_username: Optional[str]
    traffic_reset_at: Optional[datetime]


class MarzUserData(BaseModel):
    id: int
    username: str
    status: str
    used_traffic: int
    data_limit: Optional[int]
    expire: Optional[int]
    created_at: datetime
    admin_id: Optional[int]
    data_limit_reset_strategy: UserDataUsageResetStrategy
    sub_revoked_at: Optional[datetime]
    note: Optional[str]
    sub_updated_at: Optional[datetime]
    sub_last_user_agent: Optional[str]
    online_at: Optional[datetime]
    edit_at: Optional[datetime]
    on_hold_timeout: Optional[datetime]
    on_hold_expire_duration: Optional[int]
    auto_delete_in_days: Optional[int]
    last_status_change: Optional[datetime]
    uuid : str
    proxy_type: ProxyType