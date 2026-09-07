# Automated Testing Strategy

## Test Suite Architecture

```
tests/
├── conftest.py            # Global fixtures (SQLite in-memory session, TestClient, Admin/Employee seeds)
├── unit/
│   └── test_security.py   # Password hashing, JWT encoding/decoding, expiry rules
└── api/
    ├── test_auth.py       # Login, token refresh, invalid credentials, seed endpoints
    └── test_rbac.py       # Role assignment, granular permission requirement enforcement
```

## Running Tests
- **Backend Pytest**: `pytest tests/ -v --cov=app`
- **Frontend Vitest**: `npm test`
