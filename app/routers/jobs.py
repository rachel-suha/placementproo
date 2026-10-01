from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from ..deps import DB, get_current_user, require_roles
from ..models import Job, StudentProfile, User
from ..schemas import JobIn, JobOut
from ..services import check_eligibility

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("", response_model=JobOut, status_code=201)
def create_job(data: JobIn, db: DB, user: User = Depends(require_roles("recruiter"))):
    job = Job(**data.model_dump(), recruiter_id=user.id)
    db.add(job); db.commit(); db.refresh(job)
    return job

@router.get("", response_model=list[JobOut])
def list_jobs(db: DB, user: User = Depends(get_current_user),
              q: str | None = None, job_type: str | None = None,
              location: str | None = None, company: str | None = None,
              min_package: float | None = None,
              skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    query = db.query(Job)
    if user.role == "student":
        query = query.filter(Job.is_approved == True, Job.is_active == True,
                             Job.deadline >= date.today())
    elif user.role == "recruiter":
        query = query.filter(Job.recruiter_id == user.id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Job.title.ilike(like), Job.company.ilike(like),
                                 Job.description.ilike(like)))
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    if min_package is not None:
        query = query.filter(Job.package_lpa >= min_package)
    return query.order_by(Job.id.desc()).offset(skip).limit(limit).all()

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: DB, user: User = Depends(get_current_user)):
    job = db.get(Job, job_id)
    if not job or (user.role == "student" and not job.is_approved):
        raise HTTPException(404, "Job not found")
    return job

@router.put("/{job_id}", response_model=JobOut)
def update_job(job_id: int, data: JobIn, db: DB, user: User = Depends(require_roles("recruiter"))):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job.recruiter_id != user.id:
        raise HTTPException(403, "You can only edit your own jobs")
    for k, v in data.model_dump().items():
        setattr(job, k, v)
    db.commit(); db.refresh(job)
    return job

@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: DB, user: User = Depends(require_roles("recruiter", "admin"))):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if user.role == "recruiter" and job.recruiter_id != user.id:
        raise HTTPException(403, "You can only delete your own jobs")
    db.delete(job); db.commit()

@router.patch("/{job_id}/approve", response_model=JobOut)
def approve_job(job_id: int, db: DB, _: User = Depends(require_roles("admin"))):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    job.is_approved = True
    db.commit(); db.refresh(job)
    return job

@router.get("/{job_id}/eligibility")
def check_my_eligibility(job_id: int, db: DB, user: User = Depends(require_roles("student"))):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    profile = db.query(StudentProfile).filter_by(user_id=user.id).first()
    if not profile:
        raise HTTPException(400, "Create your profile first")
    reasons = check_eligibility(profile, job)
    return {"eligible": not reasons, "reasons": reasons}
