from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AdminCreate(BaseModel):
    username: str
    password: str
    enabled: bool = True
    is_sudo: bool = False
    service_ids: List[Optional[int]]
    all_services_access: bool = False
    modify_users_access: bool = False
    subscription_url_prefix: Optional[str] = ""


class AdminUpdate(BaseModel):
    username: str
    password: str
    enabled: Optional[bool] = None
    is_sudo: Optional[bool] = None
    service_ids: Optional[List[Optional[int]]] = None
    all_services_access: Optional[bool] = None
    modify_users_access: Optional[bool] = None
    subscription_url_prefix: Optional[str] = None


class AdminData(BaseModel):
    id: int
    username: str
    enabled: bool
    is_sudo: bool
    service_ids: List[Optional[int]]
    all_services_access: bool
    modify_users_access: bool
    subscription_url_prefix: Optional[str] = ""


class AdminToken(BaseModel):
    access_token: str
    is_sudo: bool
    token_type: str


class MarzAdminData(BaseModel):
    id: int
    username: str
    hashed_password: str
    created_at: datetime
    is_sudo: int
    password_reset_at: Optional[datetime] = None
    telegram_id: Optional[datetime] = None
    discord_webhook: Optional[str] = None
