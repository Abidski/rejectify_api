from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, engine
from routers import applications, companies


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(
    applications.router, prefix="/api/applications", tags=["applicatoins"]
)
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
