from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
from app.api.v1.organization import router as org_router
from app.api.v1.employee import router as employee_router
from app.api.v1.attendance import router as attendance_router
from app.api.v1.leave import router as leave_router
from app.api.v1.salary import router as salary_router
from app.api.v1.payroll import router as payroll_router
from app.api.v1.tax_statutory import router as tax_statutory_router
from app.api.v1.financial_extras import router as financial_extras_router
from app.api.v1.payslip import router as payslip_router
from app.api.v1.bank_payment import router as bank_payment_router
from app.api.v1.reports import router as reports_router
from app.api.v1.self_service import router as self_service_router
from app.api.v1.audit import router as audit_router

from app.api.v1.fnf import router as fnf_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(org_router)
api_router.include_router(employee_router)
api_router.include_router(attendance_router)
api_router.include_router(leave_router)
api_router.include_router(salary_router)
api_router.include_router(payroll_router)
api_router.include_router(tax_statutory_router)
api_router.include_router(financial_extras_router)
api_router.include_router(payslip_router)
api_router.include_router(bank_payment_router)
api_router.include_router(reports_router)
api_router.include_router(self_service_router)
api_router.include_router(audit_router)
api_router.include_router(fnf_router)







