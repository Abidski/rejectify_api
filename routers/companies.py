from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from schemas import (
    CompanyCreate,
    CompanyResponse,
)

router = APIRouter()


@router.get("", response_model=list[CompanyResponse])
async def get_companies(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Company))

    companies = result.scalars().all()

    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Company).where(models.Company.id == company_id)
    )

    company = result.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    return company


@router.post("", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Company).where(models.Company.name == company_data.name),
    )
    existing_company = result.scalars().first()
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    new_company = models.Company(name=company_data.name)
    db.add(new_company)
    await db.commit()
    await db.refresh(new_company)
    return new_company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Company).where(models.Company.id == company_id)
    )

    company = result.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    company.name = company_data.name

    await db.commit()
    await db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Company).where(models.Company.id == company_id)
    )

    company = result.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    await db.delete(company)
    await db.commit()
