from pydantic import BaseModel
from typing import List, Union, Optional


class ServiceData(BaseModel):
    id: int
    name: str
    inbound_ids: List[int]
    user_ids: List[int]


class ServiceCreate(BaseModel):
    name: str
    inbound_ids: List[int]


class Node(BaseModel):
    id: int
    name: str
    address: str
    port: int
    connection_backend: str
    usage_coefficient: float


class InboundConfig(BaseModel):
    tag: str
    protocol: str
    port: int
    network: str
    tls: str
    sni: List[str]
    host: List[str]
    path: Optional[str]
    header_type: str
    flow: Optional[str]
    is_fallback: bool


class Inbound(BaseModel):
    id: int
    tag: str
    protocol: str
    config: Union[str, InboundConfig]
    node: Node
    service_ids: List[Optional[int]]


class Inbounds(BaseModel):
    items: list[Inbound]
    total: int
    page: int
    size: int
    links: dict