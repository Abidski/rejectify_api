from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Status(str, Enum):
    pending = "pending"
    rejected = "rejected"
    offered = "offered"
    applied = "applied"
    interview = "interview"


class Application(BaseModel):
    position_title: str = Field(min_length=3)
    application_status: Status


class Company(BaseModel):
    name: str


class CompanyResponse(Company):
    pass


class CompanyCreate(Company):
    pass


class ApplicationResponse(Application):
    id: int
    application_status: Status
    update_date: datetime
    company: str
    model_config = ConfigDict(from_attributes=True)

    @field_validator("company", mode="before")
    @classmethod
    def get_company_name(cls, v, info):
        # This handles the 'Input should be a valid string' error
        # by pulling the 'name' from the Company object
        if hasattr(v, "name"):
            return v.name
        return v


class ApplicationCreate(Application):
    position: str
    status: Status
    application_date: datetime
    company: str
