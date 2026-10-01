from fastapi import APIRouter, Depends, HTTPException
from ..deps import DB, require_roles
from ..models import Application, Job, StudentProfile, User
from ..schemas import ApplicationOut, ApplyIn, StatusUpdate
from ..services import ALLOWED_TRANSITIONS, check_eligibility

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("", response_model=ApplicationOut, status_code=201)
def apply(data: ApplyIn, db: DB, user: User = Depends(require_roles("student"))):
    job = db.get(Job, data.job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    profile = db.query(StudentProfile).filter_by(user_id=user.id).first()
    if not profile:
        raise HTTPException(400, "Complete your profile before applying")
    reasons = check_eligibility(profile, job)
    if reasons:
        raise HTTPException(422, detail={"message": "Not eligible", "reasons": reasons})
    if db.query(Application).filter_by(job_id=job.id, student_id=user.id).first():
        raise HTTPException(409, "You have already applied to this job")
    app = Application(job_id=job.id, student_id=user.id)
    db.add(app); db.commit(); db.refresh(app)
    return app

@router.get("/me", response_model=list[ApplicationOut])
def my_applications(db: DB, user: User = Depends(require_roles("student"))):
    return db.query(Application).filter_by(student_id=user.id).all()

@router.get("/job/{job_id}", response_model=list[ApplicationOut])
def job_applications(job_id: int, db: DB, user: User = Depends(require_roles("recruiter", "admin"))):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if user.role == "recruiter" and job.recruiter_id != user.id:
        raise HTTPException(403, "Not your job posting")
    return db.query(Application).filter_by(job_id=job_id).all()

@router.patch("/{app_id}/status", response_model=ApplicationOut)
def update_status(app_id: int, data: StatusUpdate, db: DB,
                  user: User = Depends(require_roles("recruiter", "admin"))):
    app = db.get(Application, app_id)
    if not app:
        raise HTTPException(404, "Application not found")
    job = db.get(Job, app.job_id)
    if user.role == "recruiter" and job.recruiter_id != user.id:
        raise HTTPException(403, "Not your job posting")
    if data.status not in ALLOWED_TRANSITIONS[app.status]:
        raise HTTPException(400, f"Cannot move from '{app.status}' to '{data.status}'")
    app.status = data.status
    db.commit(); db.refresh(app)
    return app

@router.delete("/{app_id}", status_code=204)
def withdraw(app_id: int, db: DB, user: User = Depends(require_roles("student"))):
    app = db.get(Application, app_id)
    if not app or app.student_id != user.id:
        raise HTTPException(404, "Application not found")
    if app.status != "applied":
        raise HTTPException(400, "Cannot withdraw after the application is processed")
    db.delete(app); db.commit()
