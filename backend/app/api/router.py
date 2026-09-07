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

