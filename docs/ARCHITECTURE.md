# System Architecture - Enterprise Payroll Management System

## Overview
The Enterprise Payroll Management System is a multi-tenant, high-performance payroll calculation engine, compliance automation platform, and financial self-service suite.

---

## Architectural Principles
1. **Multi-Tenant Isolation**: Complete logical data isolation across companies and organizations.
2. **Deterministic Calculation Engine**: Stateless, reproducible salary calculations with step-by-step mathematical trace trees.
3. **Decoupled Statutory Rules**: Versioned tax slabs and statutory rules (India PF/ESI/PT/TDS & UAE Pension) stored in DB rules tables rather than hardcoded logic.
4. **Cryptographic Integrity**: SHA-256 hash chaining (\(Hash_n = SHA256(Hash_{n-1} + Payload)\)) ensuring tamper-evident audit logs.
5. **Double-Entry General Ledger Accounting**: Automatic generation of balanced debit and credit entries (\(\sum Debit = \sum Credit\)) mapping to ERP systems (SAP, Tally, QuickBooks).

---

## High-Level Architecture Diagram
```
                     +---------------------------------------+
                     |           React SPA Frontend          |
                     |  TypeScript + Vite + Glassmorphic UI  |
                     +-------------------+-------------------+
                                         |
                                  REST API (JSON)
                                         |
                     +-------------------v-------------------+
                     |            FastAPI Backend            |
                     |    OAuth2 JWT + RBAC Security Guard   |
                     +-------------------+-------------------+
                                         |
         +-------------------------------+-------------------------------+
         |                               |                               |
+--------v-------+               +-------v--------+              +-------v--------+
| Payroll Engine |               | Tax/Statutory  |              | ReportLab PDF  |
| Calculation    |               | Rules Catalog  |              | Generator      |
+--------+-------+               +-------+--------+              +-------+--------+
         |                               |                               |
         +-------------------------------+-------------------------------+
                                         |
                                 SQLAlchemy 2.0 ORM
                                         |
                     +-------------------v-------------------+
                     |         PostgreSQL 16 Database        |
                     +---------------------------------------+
```

---

## Role-Based Access Control (RBAC) Matrix

| Role | Permissions | Scope |
| :--- | :--- | :--- |
| **Super Admin** | `*` (Full System Access) | Cross-Tenant / Organization |
| **Payroll Manager** | `payroll.*`, `salary.*`, `reports.*`, `payments.*` | Company Level |
| **Finance Manager** | `payroll.approve`, `payments.*`, `reports.view` | Finance Review |
| **Employee** | `ess.view`, `payslip.download`, `leave.apply` | Self Service Only |
