from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=6)
    role: Literal["student", "recruiter"]

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProfileIn(BaseModel):
    branch: str
    cgpa: float = Field(ge=0, le=10)
    graduation_year: int = Field(ge=2000, le=2100)
    backlogs: int = Field(default=0, ge=0)
    skills: str = ""
    resume_url: str | None = None

class ProfileOut(ProfileIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int

class JobBase(BaseModel):
    title: str = Field(min_length=3)
    company: str
    description: str
    job_type: Literal["job", "internship"]
    location: str
    package_lpa: float = Field(ge=0)
    min_cgpa: float = Field(default=0, ge=0, le=10)
    allowed_branches: str = "ALL"
    max_backlogs: int = Field(default=0, ge=0)
    deadline: date

class JobIn(JobBase):
    @field_validator("deadline")
    @classmethod
    def deadline_in_future(cls, v):
        if v < date.today():
            raise ValueError("Deadline cannot be in the past")
        return v

class JobOut(JobBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    recruiter_id: int
    is_active: bool
    is_approved: bool

class ApplyIn(BaseModel):
    job_id: int

StatusType = Literal["applied", "shortlisted", "interview_scheduled", "selected", "rejected"]

class StatusUpdate(BaseModel):
    status: StatusType

class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    job_id: int
    student_id: int
    status: str
    created_at: datetime
