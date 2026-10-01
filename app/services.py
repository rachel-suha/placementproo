from datetime import date
from .models import Job, StudentProfile

def check_eligibility(profile: StudentProfile, job: Job) -> list[str]:
    """Reasons the student is NOT eligible. Empty list = eligible."""
    reasons = []
    if not job.is_approved:
        reasons.append("Job is not approved by the placement office")
    if not job.is_active:
        reasons.append("Job is no longer active")
    if job.deadline < date.today():
        reasons.append("Application deadline has passed")
    if profile.cgpa < job.min_cgpa:
        reasons.append(f"Minimum CGPA required is {job.min_cgpa}, yours is {profile.cgpa}")
    branches = [b.strip().upper() for b in job.allowed_branches.split(",")]
    if "ALL" not in branches and profile.branch.upper() not in branches:
        reasons.append(f"Branch {profile.branch} is not allowed (allowed: {job.allowed_branches})")
    if profile.backlogs > job.max_backlogs:
        reasons.append(f"Maximum backlogs allowed is {job.max_backlogs}, you have {profile.backlogs}")
    return reasons

ALLOWED_TRANSITIONS = {
    "applied": {"shortlisted", "rejected"},
    "shortlisted": {"interview_scheduled", "rejected"},
    "interview_scheduled": {"selected", "rejected"},
    "selected": set(),
    "rejected": set(),
}
