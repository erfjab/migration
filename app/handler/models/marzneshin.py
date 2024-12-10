from datetime import datetime

from pydantic import (
    ConfigDict,
    BaseModel,
)


class UserResponse(BaseModel):
    id: int
    activated: bool
    is_active: bool
    expired: bool
    data_limit_reached: bool
    enabled: bool
    used_traffic: int
    lifetime_used_traffic: int
    sub_revoked_at: datetime | None
    created_at: datetime
    service_ids: list[int | None]
    subscription_url: str
    owner_username: str | None
    traffic_reset_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
