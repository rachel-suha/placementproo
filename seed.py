from datetime import date, timedelta
from app.database import SessionLocal, engine, Base
from app.models import User, StudentProfile, Job, Application
from app.security import hash_password

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Job).first():
            print("Database already contains jobs. Skipping seed.")
            return

        print("Seeding demo data into Supabase PostgreSQL...")

        # 1. Recruiters
        rec1 = User(name="Sundar (Google Campus)", email="recruiter@google.com",
                    hashed_password=hash_password("Recruiter@123"), role="recruiter")
        rec2 = User(name="Satya (Microsoft Hiring)", email="recruiter@microsoft.com",
                    hashed_password=hash_password("Recruiter@123"), role="recruiter")
        db.add_all([rec1, rec2])
        db.commit()
        db.refresh(rec1); db.refresh(rec2)

        # 2. Students
        s1 = User(name="Arun Kumar", email="arun@student.com",
                  hashed_password=hash_password("Student@123"), role="student")
        s2 = User(name="Priya Sharma", email="priya@student.com",
                  hashed_password=hash_password("Student@123"), role="student")
        s3 = User(name="Rahul Verma", email="rahul@student.com",
                  hashed_password=hash_password("Student@123"), role="student")
        db.add_all([s1, s2, s3])
        db.commit()
        db.refresh(s1); db.refresh(s2); db.refresh(s3)

        # 3. Student Profiles
        p1 = StudentProfile(user_id=s1.id, branch="CSE", cgpa=8.9, graduation_year=2026,
                            backlogs=0, skills="Python, FastAPI, React, PostgreSQL",
                            resume_url="https://example.com/resumes/arun.pdf")
        p2 = StudentProfile(user_id=s2.id, branch="ECE", cgpa=7.8, graduation_year=2026,
                            backlogs=0, skills="C++, Embedded Systems, Python",
                            resume_url="https://example.com/resumes/priya.pdf")
        p3 = StudentProfile(user_id=s3.id, branch="MECH", cgpa=6.8, graduation_year=2026,
                            backlogs=1, skills="CAD, Python, Data Analysis",
                            resume_url="https://example.com/resumes/rahul.pdf")
        db.add_all([p1, p2, p3])
        db.commit()

        # 4. Jobs
        today = date.today()
        j1 = Job(recruiter_id=rec1.id, title="Software Development Engineer", company="Google",
                 description="Build scalable distributed systems using modern backend tech.",
                 job_type="job", location="Bangalore", package_lpa=24.0, min_cgpa=8.0,
                 allowed_branches="CSE,IT", max_backlogs=0, deadline=today + timedelta(days=30),
                 is_active=True, is_approved=True)

        j2 = Job(recruiter_id=rec2.id, title="Cloud Solution Architect", company="Microsoft",
                 description="Design enterprise Azure solutions and microservices architectures.",
                 job_type="job", location="Hyderabad", package_lpa=20.0, min_cgpa=7.5,
                 allowed_branches="ALL", max_backlogs=0, deadline=today + timedelta(days=25),
                 is_active=True, is_approved=True)

        j3 = Job(recruiter_id=rec1.id, title="Backend Engineering Intern", company="Google",
                 description="3-month summer internship working with core API infrastructure.",
                 job_type="internship", location="Remote", package_lpa=12.0, min_cgpa=7.0,
                 allowed_branches="CSE,ECE,IT", max_backlogs=1, deadline=today + timedelta(days=15),
                 is_active=True, is_approved=True)

        j4 = Job(recruiter_id=rec2.id, title="DevOps Engineer", company="Microsoft",
                 description="Manage CI/CD pipelines, container orchestration and reliability.",
                 job_type="job", location="Noida", package_lpa=16.5, min_cgpa=7.0,
                 allowed_branches="ALL", max_backlogs=0, deadline=today + timedelta(days=20),
                 is_active=True, is_approved=False) # pending admin approval to demo approval feature

        db.add_all([j1, j2, j3, j4])
        db.commit()
        db.refresh(j1); db.refresh(j2); db.refresh(j3); db.refresh(j4)

        # 5. Applications
        a1 = Application(job_id=j1.id, student_id=s1.id, status="interview_scheduled")
        a2 = Application(job_id=j2.id, student_id=s1.id, status="shortlisted")
        a3 = Application(job_id=j2.id, student_id=s2.id, status="applied")
        a4 = Application(job_id=j3.id, student_id=s2.id, status="selected")
        db.add_all([a1, a2, a3, a4])
        db.commit()

        print("Seeding completed successfully! Demo data is now live.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
