# Database Architecture & Schema

## 1. Schema Overview

The database is built on PostgreSQL 16 utilizing normalized schemas with strict foreign keys, indexes, and audit timestamps (`created_at`, `updated_at`).

## 2. Core Tables (Phase 1: Foundation & RBAC)

### `users`
- `id` (UUID / Integer Primary Key)
- `email` (VARCHAR 255, Unique, Indexed)
- `hashed_password` (VARCHAR 255)
- `full_name` (VARCHAR 255)
- `is_active` (BOOLEAN, Default True)
- `is_superuser` (BOOLEAN, Default False)
- `organization_id` (UUID / Integer, Nullable for SuperAdmin)
- `company_id` (UUID / Integer, Nullable)
- `created_at` (TIMESTAMP WITH TIMEZONE)
- `updated_at` (TIMESTAMP WITH TIMEZONE)

### `roles`
- `id` (Integer Primary Key)
- `name` (VARCHAR 100, Unique) — e.g. "Super Admin", "HR Manager", "Payroll Manager", "Employee"
- `description` (TEXT)
- `is_system_role` (BOOLEAN, Default False)

### `permissions`
- `id` (Integer Primary Key)
- `code` (VARCHAR 100, Unique) — e.g. `employee.view`, `payroll.calculate`, `salary.view`
- `module` (VARCHAR 50) — e.g. `employee`, `payroll`, `reports`
- `description` (TEXT)

### `user_roles`
- `user_id` (FK -> users.id)
- `role_id` (FK -> roles.id)

### `role_permissions`
- `role_id` (FK -> roles.id)
- `permission_id` (FK -> permissions.id)

### `refresh_tokens`
- `id` (UUID Primary Key)
- `user_id` (FK -> users.id)
- `token_hash` (VARCHAR 255, Indexed)
- `expires_at` (TIMESTAMP WITH TIMEZONE)
- `is_revoked` (BOOLEAN, Default False)
- `device_info` (VARCHAR 255)

### `audit_logs`
- `id` (BigInteger Primary Key)
- `user_id` (FK -> users.id, Nullable)
- `action` (VARCHAR 100) — e.g. "USER_LOGIN", "PAYROLL_CALCULATED"
- `module` (VARCHAR 50)
- `record_id` (VARCHAR 100)
- `old_values` (JSONB)
- `new_values` (JSONB)
- `ip_address` (VARCHAR 45)
- `user_agent` (TEXT)
- `timestamp` (TIMESTAMP WITH TIMEZONE)
