# Deployment & Operational Guide

## Docker Compose Deployment
```bash
docker-compose up -d --build
```

## Production Verification Checklist
- [ ] Database credentials updated in `.env`
- [ ] `SECRET_KEY` changed to a 64+ byte cryptographically strong secret
- [ ] SSL/TLS certificates configured (HTTPS enabled)
- [ ] Database migrations applied via Alembic (`alembic upgrade head`)
- [ ] SuperAdmin user bootstrapped (`POST /api/v1/auth/seed-admin`)
