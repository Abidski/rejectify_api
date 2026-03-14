from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
)

router = APIRouter()


@router.get("", response_model=list[ApplicationResponse])
async def get_applications(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Applications).options(selectinload(models.Applications.company))
    )

    applications = result.scalars().all()
    return applications


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application_individual(
    application_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.Applications)
        .options(selectinload(models.Applications.company))
        .where(models.Applications.id == application_id)
    )

    application = result.scalars().first()

    if application:
        return application

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
    )


@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application_partial(
    application_id: int,
    application_data: ApplicationUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Applications).where(models.Applications.id == application_id)
    )

    application = result.scalars().first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    data = application_data.model_dump(exclude_none=True)

    for field, value in data:
        setattr(application, field, value)

    await db.commit()
    await db.refresh(application, attribute_names=["company"])
    return application


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application_full(
    application_id: int,
    application_data: ApplicationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Applications).where(models.Applications.id == application_id)
    )

    application = result.scalars().first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    application.position_title = application_data.position_title
    application.application_status = application_data.application_status

    await db.commit()
    await db.refresh(application, attribute_names=["company"])
    return application


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    application: ApplicationCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    query = await db.execute(
        select(models.Company).where(models.Company.name == application.company)
    )
    company = query.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )
    company_id = company.id

    result = await db.execute(
        select(models.Applications)
        .options(selectinload(models.Applications.company))
        .where(
            and_(
                models.Applications.position_title == application.position_title,
                models.Applications.company_id == company_id,
            )
        )
    )

    exist = result.scalars().first()

    if exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application already exists",
        )

    new_application = models.Applications(
        company_id=company_id,
        position_title=application.position_title,
        application_status=application.application_status,
        application_date=application.application_date,
    )

    db.add(new_application)
    await db.commit()
    await db.refresh(new_application, attribute_names=["company"])

    return new_application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Applications).where(models.Applications.id == application_id)
    )

    application = result.scalars().first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    await db.delete(application)
    await db.commit()
