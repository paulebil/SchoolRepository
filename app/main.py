from fastapi import FastAPI
from app.database.database import init_db
from contextlib import asynccontextmanager

from app.models.user import User
from app.models.token import Token
from app.models.school import School
from app.models.department import Department

@asynccontextmanager
async def lifespan(app_:FastAPI):
    # startup
    await init_db()
    yield
    # shutdown

def create_application():
    application = FastAPI(lifespan=lifespan)
    return application


app = create_application()

@app.get("/")
async def index():
    return {"message": "School Paper Repository is up and Running. Server Healthy!"}