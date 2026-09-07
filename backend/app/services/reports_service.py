import io
import csv
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.payroll_run import PayrollRun, PayrollEmployee, PayrollPeriod
from app.models.employee import Employee
from app.models.organization import Department
from app.core.exceptions import PayrollException


class ReportsService:

    @staticmethod
    def generate_master_payroll_register(db: Session, period_id: int) -> Dict[str, Any]:
        """Generates itemized master payroll register for a pay period."""
        run = db.query(PayrollRun).filter(PayrollRun.payroll_period_id == period_id).first()
        if not run:
            raise PayrollException("RUN_NOT_FOUND", f"No calculated payroll run found for period {period_id}")

        register_rows = []
        for emp in run.employee_results:
            employee: Employee = emp.employee
            emp_name = f"{employee.first_name} {employee.last_name}" if employee else "Staff"
            dept_name = employee.department.name if (employee and employee.department) else "General"
            
            # Map earnings
            earnings_map = {e.component_code: e.prorated_amount for e in emp.earnings}
            deductions_map = {d.component_code: d.amount for d in emp.deductions}

            register_rows.append({
                "payroll_employee_id": emp.id,
                "employee_id": emp.employee_id,
                "employee_code": f"EMP-{emp.employee_id:04d}",
                "employee_name": emp_name,
                "department": dept_name,
                "total_days": emp.total_days,
                "payable_days": emp.payable_days,
                "basic": earnings_map.get("BASIC", 0.0),
                "hra": earnings_map.get("HRA", 0.0),
                "transport": earnings_map.get("TRANSPORT", 0.0),
                "special_allowance": earnings_map.get("SPECIAL_ALLOWANCE", 0.0),
                "bonus": earnings_map.get("BONUS", 0.0),
                "gross_salary": emp.gross_salary,
                "pf_deduction": deductions_map.get("IN_PF", 0.0),
                "esi_deduction": deductions_map.get("IN_ESI", 0.0),
                "tds_deduction": deductions_map.get("IN_TDS", 0.0),
                "pt_deduction": deductions_map.get("IN_PT", 0.0),
                "total_deductions": emp.total_deductions,
                "net_salary": emp.net_salary,
            })

        return {
            "period_id": period_id,
            "payroll_run_id": run.id,
            "period_name": run.payroll_period.name if run.payroll_period else "",
            "total_employees": len(register_rows),
            "total_gross": run.total_gross,
            "total_deductions": run.total_deductions,
            "total_net": run.total_net,
            "records": register_rows,
        }

    @staticmethod
    def generate_pf_ecr_file(db: Session, period_id: int) -> bytes:
        """Generates India PF Electronic Challan cum Return (ECR) text file with `#~#` delimiters."""
        run = db.query(PayrollRun).filter(PayrollRun.payroll_period_id == period_id).first()
        if not run:
            raise PayrollException("RUN_NOT_FOUND", f"No payroll run found for period {period_id}")

        lines = []
        for emp in run.employee_results:
            employee = emp.employee
            uan = getattr(employee, 'pf_uan', '100918273645')
            name = f"{employee.first_name} {employee.last_name}" if employee else "Staff"
            
            gross = emp.gross_salary
            epf_wages = min(gross, 15000.0) # PF statutory cap ₹15,000
            eps_wages = epf_wages
            edli_wages = epf_wages
            
            epf_contrib = round(epf_wages * 0.12, 0)
            eps_contrib = round(epf_wages * 0.0833, 0)
            diff = round(epf_contrib - eps_contrib, 0)

            # ECR text format: UAN#~#MemberName#~#GrossWages#~#EPFWages#~#EPSWages#~#EDLIWages#~#EPFContrib#~#EPSContrib#~#Diff
            line = f"{uan}#~#{name}#~#{int(gross)}#~#{int(epf_wages)}#~#{int(eps_wages)}#~#{int(edli_wages)}#~#{int(epf_contrib)}#~#{int(eps_contrib)}#~#{int(diff)}"
            lines.append(line)

        return "\n".join(lines).encode('utf-8')

    @staticmethod
    def generate_cost_center_breakdown(db: Session, period_id: int) -> List[Dict[str, Any]]:
        """Generates department & cost center payroll allocation summary."""
        run = db.query(PayrollRun).filter(PayrollRun.payroll_period_id == period_id).first()
        if not run:
            return []

        dept_summary: Dict[str, Dict[str, Any]] = {}
        for emp in run.employee_results:
            dept_name = emp.employee.department.name if (emp.employee and emp.employee.department) else "General"
            if dept_name not in dept_summary:
                dept_summary[dept_name] = {
                    "department": dept_name,
                    "employee_count": 0,
                    "gross_salary": 0.0,
                    "total_deductions": 0.0,
                    "net_salary": 0.0,
                    "employer_cost": 0.0,
                }
            
            dept_summary[dept_name]["employee_count"] += 1
            dept_summary[dept_name]["gross_salary"] += emp.gross_salary
            dept_summary[dept_name]["total_deductions"] += emp.total_deductions
            dept_summary[dept_name]["net_salary"] += emp.net_salary
            dept_summary[dept_name]["employer_cost"] += emp.employer_cost

        return list(dept_summary.values())

    @staticmethod
    def get_executive_analytics(db: Session) -> Dict[str, Any]:
        """Returns executive level metrics: YTD gross, total runs executed, department allocation ratios."""
        runs = db.query(PayrollRun).all()
        periods = db.query(PayrollPeriod).all()

        total_runs = len(runs)
        total_ytd_gross = sum(r.total_gross for r in runs)
        total_ytd_net = sum(r.total_net for r in runs)
        total_ytd_deductions = sum(r.total_deductions for r in runs)

        # Period trends
        trends = []
        for r in runs:
            trends.append({
                "period_id": r.payroll_period_id,
                "period_name": r.payroll_period.name if r.payroll_period else f"Run #{r.id}",
                "year_month": r.payroll_period.year_month if r.payroll_period else "",
                "total_gross": r.total_gross,
                "total_net": r.total_net,
                "total_employees": r.total_employees,
            })

        return {
            "total_runs_executed": total_runs,
            "total_active_periods": len(periods),
            "total_ytd_gross": total_ytd_gross,
            "total_ytd_net": total_ytd_net,
            "total_ytd_deductions": total_ytd_deductions,
            "payroll_trends": trends,
        }
