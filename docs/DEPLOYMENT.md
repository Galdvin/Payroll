# Production Deployment Guide - Enterprise Payroll Management System

## Overview
This guide documents the containerized production deployment of the Enterprise Payroll Management System using Docker Compose.

---

## Production Prerequisites
- Docker Engine v24.0+
- Docker Compose v2.20+
- Minimum 4 GB RAM, 2 CPU Cores

---

## Quick Deployment Steps

### 1. Clone Repository & Navigate to Workspace
```bash
git clone https://github.com/enterprise/payroll-system.git
cd payroll-system
```

### 2. Configure Production Environment Variables
Edit `docker-compose.yml` to set secure credentials:
```yaml
POSTGRES_USER: payroll_prod_user
POSTGRES_PASSWORD: YourVerySecurePasswordHere!
POSTGRES_DB: enterprise_payroll_prod
JWT_SECRET: ProductionSecretJWTSignatureKey2026!
```

### 3. Launch Docker Containers
```bash
docker-compose up -d --build
```

### 4. Verify Services
- **Frontend SPA**: `http://localhost` (Nginx port 80)
- **FastAPI Backend Swagger Docs**: `http://localhost:8000/docs`
- **PostgreSQL Database**: `localhost:5432`

---

## Container Architecture

```
+-------------------------------------------------------------+
|                      Host Server                            |
|                                                             |
|   +-------------------+  +-------------------+              |
|   |  frontend:80      |  |  backend:8000     |              |
|   |  Nginx + React    |  |  FastAPI Uvicorn  |              |
|   +---------+---------+  +---------+---------+              |
|             |                      |                        |
|             +----------+-----------+                        |
|                        |                                    |
|              +---------v---------+                          |
|              |  postgres:5432    |                          |
|              |  PostgreSQL 16    |                          |
|              +-------------------+                          |
+-------------------------------------------------------------+
```
