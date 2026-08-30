from pydantic import HttpUrl
from sqlmodel import Field, SQLModel


class LinkBase(SQLModel):
    short_name: str = Field(index=True, min_length=1, max_length=255, unique=True)


class Link(LinkBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_url: str


class LinkPayload(LinkBase):
    original_url: HttpUrl


class LinkCreate(LinkPayload):
    pass


class LinkUpdate(LinkPayload):
    pass


class LinkRead(SQLModel):
    id: int
    original_url: HttpUrl
    short_name: str
    short_url: str
