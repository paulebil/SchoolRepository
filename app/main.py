from fastapi import FastAPI
from app.database.database import init_db
from contextlib import asynccontextmanager

from app.models.user import User, UserToken, PasswordResetToken
from app.models.signup_token import SignupToken
from app.models.school import School
from app.models.department import Department
from app.models.supervisor_comment import SupervisorComment
from app.models.past_paper import PastPaper
from app.models.research_paper import ResearchPaper
from app.models.research_paper_author import ResearchPaperAuthor
from app.models.reading_material import ReadingMaterial

from app.routers.user import user_router, auth_router
from app.routers.school import sch_router
from app.routers.department import dept_router
from app.routers.lecturer import lect_router

@asynccontextmanager
async def lifespan(app_:FastAPI):
    # startup
    await init_db()
    yield
    # shutdown

def create_application():
    application = FastAPI(lifespan=lifespan)
    application.include_router(user_router)
    application.include_router(auth_router)
    application.include_router(sch_router)
    application.include_router(dept_router)
    application.include_router(lect_router)
    return application


app = create_application()

@app.get("/")
async def index():
    return {"message": "School Paper Repository is up and Running. Server Healthy!"}