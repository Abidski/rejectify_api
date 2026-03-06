from enum import Enum

from pydantic import BaseModel, Field


class Status(str, Enum):
    pending = "pending"
    rejected = "rejected"
    offered = "offered"
    applied = "applied"
    interview = "interview"


class Application(BaseModel):
    company: str = Field(min_length=3)
    position: str = Field(min_length=3)


class ApplicationResponse(Application):
    id: int
    status: Status
    update_date: str


class ApplicationCreate(Application):
    pass
