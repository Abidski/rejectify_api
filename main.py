from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db
from schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    CompanyCreate,
    CompanyResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/api/applications", response_model=list[ApplicationResponse])
def get_applications(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Applications))

    applications = result.scalars().all()
    return applications


@app.get("/api/applications/{application_id}", response_model=ApplicationResponse)
def get_application_individual(
    application_id: int, db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(
        select(models.Applications).where(models.Applications.id == application_id)
    )

    application = result.scalars().first()

    if application:
        return application

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
    )


@app.patch("/api/applications/{application_id}", response_model=ApplicationResponse)
def update_application_partial(
    application_id: int,
    application_data: ApplicationUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(
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

    db.commit()
    db.refresh(application)
    return application


@app.put("/api/applications/{application_id}", response_model=ApplicationResponse)
def update_application_full(
    application_id: int,
    application_data: ApplicationCreate,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(
        select(models.Applications).where(models.Applications.id == application_id)
    )

    application = result.scalars().first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    application.position_title = application_data.position_title
    application.application_status = application_data.application_status

    db.commit()
    db.refresh(application)
    return application


@app.post(
    "/api/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    application: ApplicationCreate, db: Annotated[Session, Depends(get_db)]
):
    query = db.execute(
        select(models.Company).where(models.Company.name == application.company)
    )
    company = query.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )
    company_id = company.id

    result = db.execute(
        select(models.Applications).where(
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
    db.commit()
    db.refresh(new_application)

    return new_application


@app.delete("/api/applications/{application_id}", response_model=ApplicationResponse)
def delete_application(
    application_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(
        select(models.Applications).where(models.Applications.id == application_id)
    )

    application = result.scalars().first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    db.delete(application)
    db.commit()


@app.get("/api/companies", response_model=list[CompanyResponse])
def get_companies(application_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Company))

    companies = result.scalars().all()

    return companies


@app.get("/api/companies/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Company).where(models.Company.id == company_id))

    company = result.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    return company


@app.post("/api/companies", response_model=CompanyResponse)
def create_company(
    company_data: CompanyCreate,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(
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
    db.commit()
    db.refresh(new_company)
    return new_company


@app.put("/api/company/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_data: CompanyCreate,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(select(models.Company).where(models.Company.id == company_id))

    company = result.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    company.name = company_data.name

    db.commit()
    db.refresh(company)
    return company


@app.delete("/api/company/{company_id}", response_model=CompanyResponse)
def delete_company(
    company_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(select(models.Company).where(models.Company.id == company_id))

    company = result.scalars().first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    db.delete(company)
    db.commit()
