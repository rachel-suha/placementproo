# PlacementPro — Presentation & Technical Guide

---

## 1. Problem Statement
Traditional campus placement drives rely on fragmented spreadsheets, emails, and manual tracking. This leads to four critical problems:
1. **Screening Overhead**: Recruiters waste hours manually filtering out ineligible students who do not meet strict criteria (CGPA cutoff, allowed branches, active backlogs).
2. **Duplicate & Inconsistent Applications**: Students repeatedly apply to the same openings without centralized validation.
3. **Security & Ownership Risks**: Lack of role isolation allows unauthorized edits to job postings or applicant statuses.
4. **Administrative Blindspots**: Placement officers cannot view real-time hiring ratios, open drives, or student participation analytics.

---

## 2. Solution Overview
**PlacementPro** is a modern RESTful API built with **FastAPI**, **SQLAlchemy 2.0**, and **PostgreSQL (Supabase)**. It provides:
- **Automated Eligibility Engine**: Validates criteria (CGPA, branches, backlogs, deadlines) prior to application submission.
- **Strict Role-Based Access Control (RBAC)**: Distinct permissions for `student`, `recruiter`, and `admin`.
- **Application State Machine**: Enforces structured lifecycle progression (`applied` → `shortlisted` → `interview_scheduled` → `selected` / `rejected`).
- **Production-Ready Configuration**: Decoupled environment settings via `.env` and `pydantic-settings`.

---

## 3. Script-by-Script Technical Breakdown

### Core Architecture

- **`app/config.py`**:
  - Uses `pydantic-settings` to dynamically parse environment variables from `.env`.
  - Normalizes PostgreSQL connection URIs (`postgres://` → `postgresql://`) for cloud providers like Supabase and Neon.

- **`app/database.py`**:
  - Initializes SQLAlchemy 2.0 database engine with connection health checks (`pool_pre_ping=True`).
  - Provides the `get_db()` dependency generator to yield transactional sessions and cleanly close them after request completion.

- **`app/models.py`**:
  - Uses modern SQLAlchemy 2.0 `Mapped` and `mapped_column` typed declarations.
  - Defines core tables: `User`, `StudentProfile`, `Job`, and `Application`.
  - Enforces database-level integrity with foreign keys and a `UniqueConstraint("job_id", "student_id", name="uq_job_student")` to prevent duplicate submissions.

- **`app/schemas.py`**:
  - Pydantic v2 data models for input validation and output serialization.
  - Features `EmailStr`, string length constraints, CGPA range bounds (`0.0` to `10.0`), and custom `@field_validator` ensuring job deadlines cannot be set in the past.

- **`app/security.py`**:
  - Implements password hashing with salted **bcrypt** (`hashpw` / `checkpw`).
  - Generates and decodes HS256 **JWT access tokens** with configurable expiration.

- **`app/deps.py`**:
  - Contains reusable FastAPI dependencies:
    - `DB`: Injects database session.
    - `get_current_user`: Extracts and validates the JWT Bearer token via `OAuth2PasswordBearer`.
    - `require_roles(*roles)`: Role-based guard enforcing 403 Forbidden on unauthorized access.

- **`app/services.py`**:
  - **Eligibility Engine**: `check_eligibility(profile, job)` compares student metrics against job requirements and returns a detailed list of rejection reasons.
  - **State Machine**: `ALLOWED_TRANSITIONS` defines legal progression paths for application statuses, preventing invalid stage jumping.

- **`app/main.py`**:
  - Configures FastAPI app metadata, CORS middleware, and route mounting.
  - Features an asynchronous `lifespan` handler that creates database tables and seeds the default administrator account (`admin@placementpro.com`).
  - Provides the `GET /admin/stats` dashboard analytics endpoint and serves the frontend.

---

### Routers (`app/routers/`)

- **`app/routers/auth.py`**:
  - `POST /auth/register`: Self-registration for students and recruiters with duplicate email protection (409 Conflict).
  - `POST /auth/login`: OAuth2 password flow returning a JWT Bearer access token.
  - `GET /auth/me`: Returns the authenticated user's profile.

- **`app/routers/students.py`**:
  - `PUT /students/me/profile`: Upserts student academic details (CGPA, branch, backlogs, skills, resume).
  - `GET /students/me/profile`: Fetches student profile (404 if not yet created).
  - `GET /students`: Admin-only directory with branch filtering, minimum CGPA filtering, and pagination (`skip`, `limit`).

- **`app/routers/jobs.py`**:
  - `POST /jobs`: Recruiter job creation with eligibility criteria.
  - `GET /jobs`: Filtered job search (`q`, `job_type`, `location`, `company`, `min_package`) with pagination. Students only see approved, active, unexpired jobs.
  - `GET/PUT/DELETE /jobs/{job_id}`: Job lookup, update, and deletion protected by recruiter ownership checks.
  - `PATCH /jobs/{job_id}/approve`: Admin-only endpoint to approve jobs.
  - `GET /jobs/{job_id}/eligibility`: Evaluates whether the calling student is eligible for a specific job.

- **`app/routers/applications.py`**:
  - `POST /applications`: Validates eligibility (422 if unqualified) and duplicate prevention (409 if applied already) before recording the application.
  - `GET /applications/me`: Lists all applications submitted by the logged-in student.
  - `GET /applications/job/{job_id}`: Recruiter views applicants for their specific posting.
  - `PATCH /applications/{app_id}/status`: Recruiter updates applicant status adhering to the state machine (400 if invalid transition).
  - `DELETE /applications/{app_id}`: Allows student to withdraw an unprocessed application.

---

## 4. Speaking Script for Demo

1. **Introduction**:
   > *"Good morning/afternoon. Today I am presenting PlacementPro, an automated Campus Placement Management System built with FastAPI, SQLAlchemy 2.0, and PostgreSQL on Supabase."*

2. **The Problem & Solution**:
   > *"In campus placement drives, recruiters spend excessive time manually checking if students meet CGPA or branch cutoffs. PlacementPro solves this by embedding an automated Eligibility Engine that pre-evaluates applicants before an application can even be submitted."*

3. **Live Demonstration**:
   - **Admin**: Log in as `admin@placementpro.com` / `Admin@123`. Show the **All jobs** approval workflow, the **Students** academic directory, and the **Stats** dashboard.
   - **Recruiter**: Log in as `recruiter@google.com` / `Recruiter@123`. Show job posting with cutoffs and applicant pipeline management.
   - **Student**: Log in as `arun@student.com` / `Student@123`. Show real-time eligibility check on job postings and application tracking.
   - **Swagger UI**: Navigate to `/docs` to showcase the OpenAPI documentation, JWT authentication, and REST HTTP status codes (`200`, `201`, `400`, `401`, `403`, `404`, `409`, `422`).
