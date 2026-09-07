# API Specifications & OpenAPI Integration

## Core Endpoints (Phase 1)

### Authentication
- `POST /api/v1/auth/login`: Authenticate email/password, return access_token & refresh_token.
- `POST /api/v1/auth/refresh`: Issue new access token using refresh_token cookie/body.
- `GET /api/v1/auth/me`: Get current authenticated user profile and assigned permissions.
- `POST /api/v1/auth/seed-admin`: Bootstrap initial superadmin user and system permissions.

### User Management
- `GET /api/v1/users`: List users with pagination and search (`employee.view` permission required).
- `POST /api/v1/users`: Create user account (`employee.create` permission required).
- `GET /api/v1/users/{id}`: Retrieve single user detail.
- `PUT /api/v1/users/{id}`: Update user metadata/roles.

### Role & Permission Management
- `GET /api/v1/roles`: List all system roles.
- `POST /api/v1/roles`: Create custom role.
- `GET /api/v1/roles/permissions`: List all defined granular permissions.
- `POST /api/v1/users/{id}/roles`: Assign roles to user.
