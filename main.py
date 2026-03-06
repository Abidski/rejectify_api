from fastapi import FastAPI, status

from schemas import ApplicationResponse

app = FastAPI()


@app.get("/api/applications", response_model=ApplicationResponse)
def get_applications():
    return {"Hello": "World"}


@app.get("/api/applications/{application_id}", response_model=ApplicationResponse)
def get_application():
    return {"Hello": "World"}


@app.post(
    "/api/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application():
    return {"Hello": "World"}


@app.put("/api/applications/{application_id}", response_model=ApplicationResponse)
def update_application():
    return {"Hello": "World"}


@app.get("/api/companies", response_model=ApplicationResponse)
def get_compnaies():
    return {"Hello": "World"}
