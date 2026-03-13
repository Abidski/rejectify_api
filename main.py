from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import Base, engine, get_db
from schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    CompanyCreate,
    CompanyResponse,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/api/applications", response_model=list[ApplicationResponse])
async def get_applications(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Applications).options(selectinload(models.Applications.company))
    )

    applications = result.scalars().all()
    return applications


@app.get("/api/applications/{application_id}", response_model=ApplicationResponse)
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


@app.patch("/api/applications/{application_id}", response_model=ApplicationResponse)
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


@app.put("/api/applications/{application_id}", response_model=ApplicationResponse)
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


@app.post(
    "/api/applications",
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


@app.delete(
    "/api/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT
)
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


@app.get("/api/companies", response_model=list[CompanyResponse])
async def get_companies(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Company))

    companies = result.scalars().all()

    return companies


@app.get("/api/companies/{company_id}", response_model=CompanyResponse)
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


@app.post("/api/companies", response_model=CompanyResponse)
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


@app.put("/api/companies/{company_id}", response_model=CompanyResponse)
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


@app.delete("/api/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
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
