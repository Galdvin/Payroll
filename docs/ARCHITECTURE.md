# Architecture Overview — Enterprise Payroll Management System

## 1. System Overview

The Enterprise Payroll Management System is designed as a modular, extensible, multi-tenant application capable of processing payroll across multiple organizational units, branches, and multi-country tax/statutory rule frameworks.

## 2. Technical Stack

- **Backend**: FastAPI (Python 3.11+), SQLAlchemy 2.0 ORM, Pydantic v2, PostgreSQL 16, Redis 7, Celery.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, React Query, Zustand.
- **Authentication & Security**: OAuth2 JWT + Refresh Tokens, Argon2/BCrypt password hashing, Granular RBAC, Audit Logging.
- **Testing**: Pytest (Backend API & Calculation Engine), Playwright/Vitest (Frontend & E2E).

## 3. Modular Clean Architecture

```
                               ┌─────────────────────────┐
                               │  Vite React Frontend    │
                               └────────────┬────────────┘
                                            │ HTTP / JSON JWT
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                            FastAPI Application Gateway                         │
│  ┌───────────────────────────────┐     ┌────────────────────────────────────┐  │
│  │   CORS / Rate Limit / Auth    │     │   Granular RBAC Permission Layer   │  │
│  └──────────────┬────────────────┘     └─────────────────┬──────────────────┘  │
└─────────────────┼────────────────────────────────────────┼─────────────────────┘
                  │                                        │
                  ▼                                        ▼
┌───────────────────────────────────┐     ┌──────────────────────────────────────┐
│        API Controllers            │ ──► │          Service Domain Layer        │
│  - Auth / Users / Roles           │     │  - AuthService                       │
│  - Employees / Organizations      │     │  - EmployeeService                   │
│  - Attendance / Leave             │     │  - PayrollEngineService              │
│  - Payroll Engine                 │     │  - StatutoryRuleEngine (India / GCC) │
└───────────────────────────────────┘     └──────────────────┬───────────────────┘
                                                             │
                                                             ▼
                                          ┌──────────────────────────────────────┐
                                          │      Data Repository & DB Layer      │
                                          │  - SQLAlchemy 2.0 Models             │
                                          │  - Alembic Database Migrations       │
                                          └──────────────────┬───────────────────┘
                                                             │
                                                             ▼
                                          ┌──────────────────────────────────────┐
                                          │    PostgreSQL Database (Multi-Tenant)│
                                          └──────────────────────────────────────┘
```

## 4. Key Architectural Patterns

1. **Rule Engine Isolation**: Tax and statutory calculations are decoupled into dynamic, versioned rule engines rather than hard-coded into business logic.
2. **Auditability & Traceability**: Every payroll calculation stores detailed calculation traces explaining Gross, Tax, Deductions, and Net Salary steps.
3. **Multi-Tenancy**: All domain tables enforce `organization_id` and `company_id` soft/hard boundaries.
4. **Idempotency & Concurrency Locking**: Finalized payroll runs enter an immutable `LOCKED` status preventing duplicate processing.
