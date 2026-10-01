from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .database import Base, SessionLocal, engine
from .deps import DB, require_roles
from .models import Application, Job, User
from .routers import applications, auth, jobs, students
from .security import hash_password

STATIC = Path(__file__).resolve().parent.parent / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter_by(role="admin").first():
            db.add(User(name="Placement Officer", email="admin@placementpro.com",
                        hashed_password=hash_password("Admin@123"), role="admin"))
            db.commit()
    finally:
        db.close()
    yield

app = FastAPI(title="PlacementPro", version="1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(jobs.router)
app.include_router(applications.router)

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC / "index.html")

@app.get("/admin/stats", tags=["Admin"])
def stats(db: DB, _: User = Depends(require_roles("admin"))):
    return {
        "students": db.query(User).filter_by(role="student").count(),
        "recruiters": db.query(User).filter_by(role="recruiter").count(),
        "jobs": db.query(Job).count(),
        "applications": db.query(Application).count(),
        "selected": db.query(Application).filter_by(status="selected").count(),
    }
