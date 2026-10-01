from datetime import date, datetime
from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    hashed_password: Mapped[str]
    role: Mapped[str] = mapped_column(String(20))  # student | recruiter | admin

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    branch: Mapped[str] = mapped_column(String(50))
    cgpa: Mapped[float]
    graduation_year: Mapped[int]
    backlogs: Mapped[int] = mapped_column(default=0)
    skills: Mapped[str] = mapped_column(Text, default="")
    resume_url: Mapped[str | None] = mapped_column(nullable=True)

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    recruiter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(150), index=True)
    company: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str] = mapped_column(Text)
    job_type: Mapped[str] = mapped_column(String(20))
    location: Mapped[str] = mapped_column(String(100))
    package_lpa: Mapped[float]
    min_cgpa: Mapped[float] = mapped_column(default=0)
    allowed_branches: Mapped[str] = mapped_column(String(200), default="ALL")
    max_backlogs: Mapped[int] = mapped_column(default=0)
    deadline: Mapped[date]
    is_active: Mapped[bool] = mapped_column(default=True)
    is_approved: Mapped[bool] = mapped_column(default=False)

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("job_id", "student_id", name="uq_job_student"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(30), default="applied")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
