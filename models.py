from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from schemas import Status


class Base(DeclarativeBase):
    pass


class Company(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    applications: Mapped[List["Applications"]] = relationship(back_populates="company")


class Applications(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"), index=True)
    postions_title: Mapped[str] = mapped_column(String(255))
    application_status: Mapped[Status] = mapped_column(index=True)
    application_date: Mapped[datetime] = mapped_column()
    update_date: Mapped[datetime] = mapped_column()

    company: Mapped["Company"] = relationship(back_populates="applications")
