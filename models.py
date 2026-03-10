from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from schemas import Status


class Company(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    applications: Mapped[list[Applications]] = relationship(back_populates="company")


class Applications(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("company.id"), index=True, nullable=False
    )
    position_title: Mapped[str] = mapped_column()
    application_status: Mapped[Status] = mapped_column(index=True)
    application_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    update_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("America/New_York")),
    )

    company: Mapped[Company] = relationship(back_populates="applications")
