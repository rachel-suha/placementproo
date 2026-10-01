from fastapi import APIRouter, Depends, HTTPException, Query
from ..deps import DB, require_roles
from ..models import StudentProfile, User
from ..schemas import ProfileIn, ProfileOut

router = APIRouter(prefix="/students", tags=["Students"])

@router.put("/me/profile", response_model=ProfileOut)
def upsert_profile(data: ProfileIn, db: DB, user: User = Depends(require_roles("student"))):
    profile = db.query(StudentProfile).filter_by(user_id=user.id).first()
    if profile:
        for k, v in data.model_dump().items():
            setattr(profile, k, v)
    else:
        profile = StudentProfile(user_id=user.id, **data.model_dump())
        db.add(profile)
    db.commit(); db.refresh(profile)
    return profile

@router.get("/me/profile", response_model=ProfileOut)
def get_my_profile(db: DB, user: User = Depends(require_roles("student"))):
    profile = db.query(StudentProfile).filter_by(user_id=user.id).first()
    if not profile:
        raise HTTPException(404, "Profile not created yet")
    return profile

@router.get("", response_model=list[ProfileOut])
def list_students(db: DB, _: User = Depends(require_roles("admin")),
                  branch: str | None = None, min_cgpa: float | None = None,
                  skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
    q = db.query(StudentProfile)
    if branch:
        q = q.filter(StudentProfile.branch.ilike(branch))
    if min_cgpa is not None:
        q = q.filter(StudentProfile.cgpa >= min_cgpa)
    return q.offset(skip).limit(limit).all()
