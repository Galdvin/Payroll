from datetime import date
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from app.core.exceptions import PayrollException, ResourceNotFoundException
from app.models.statutory import StatutoryRule, TaxRule, TaxSlab
from app.schemas.tax_statutory import StatutoryRuleCreate, TaxRuleCreate

DEFAULT_STATUTORY_RULES = [
    ("India", "IN_PF", "Employee Provident Fund (PF)", 0.1200, 0.1200, 15000.0, 1800.0, None, "v2024.1"),
    ("India", "IN_ESI", "Employee State Insurance (ESI)", 0.0075, 0.0325, None, None, 21000.0, "v2024.1"),
    ("India", "IN_PT", "Professional Tax (PT)", 0.0000, 0.0000, None, 200.0, 15000.0, "v2024.1"),
    ("UAE", "UAE_PENSION", "UAE National Pension (GCC Ready)", 0.0500, 0.1250, None, None, None, "v2024.1"),
]


class StatutoryEngineService:

    @staticmethod
    def seed_defaults(db: Session):
        # 1. Seed Statutory Rules
        for country, code, name, ee_rate, er_rate, ceiling, cap, thresh, ver in DEFAULT_STATUTORY_RULES:
            existing = db.query(StatutoryRule).filter(StatutoryRule.rule_code == code).first()
            if not existing:
                rule = StatutoryRule(
                    country=country,
                    rule_code=code,
                    name=name,
                    employee_rate=ee_rate,
                    employer_rate=er_rate,
                    wage_ceiling=ceiling,
                    monthly_cap=cap,
                    eligibility_threshold=thresh,
                    rule_version=ver,
                    effective_date=date(2024, 4, 1),
                    is_active=True,
                )
                db.add(rule)

        # 2. Seed FY 2024-2025 New Tax Regime
        existing_tax = db.query(TaxRule).filter(TaxRule.financial_year == "2024-2025", TaxRule.regime_name == "New Regime").first()
        if not existing_tax:
            t_rule = TaxRule(
                country="India",
                financial_year="2024-2025",
                regime_name="New Regime",
                standard_deduction=75000.0,
                cess_rate=0.0400,
                rule_version="v2024.1",
                effective_date=date(2024, 4, 1),
                is_active=True,
            )
            db.add(t_rule)
            db.flush()

            # FY 24-25 New Regime Slabs:
            # 0 - 3,00,000: 0%
            # 3,00,001 - 7,00,000: 5%
            # 7,00,001 - 10,00,000: 10%
            # 10,00,001 - 12,00,000: 15%
            # 12,00,001 - 15,00,000: 20%
            # Above 15,00,000: 30%
            slabs_data = [
                (0.0, 300000.0, 0.00),
                (300000.0, 700000.0, 0.05),
                (700000.0, 1000000.0, 0.10),
                (1000000.0, 1200000.0, 0.15),
                (1200000.0, 1500000.0, 0.20),
                (1500000.0, None, 0.30),
            ]
            for f_inc, t_inc, rate in slabs_data:
                db.add(TaxSlab(tax_rule_id=t_rule.id, from_income=f_inc, to_income=t_inc, tax_rate=rate))

        db.commit()

    @staticmethod
    def get_statutory_rules(db: Session, country: str = "India") -> List[StatutoryRule]:
        StatutoryEngineService.seed_defaults(db)
        return db.query(StatutoryRule).filter(StatutoryRule.country == country, StatutoryRule.is_active == True).all()

    @staticmethod
    def get_tax_rules(db: Session, country: str = "India") -> List[TaxRule]:
        StatutoryEngineService.seed_defaults(db)
        return db.query(TaxRule).filter(TaxRule.country == country, TaxRule.is_active == True).all()

    # --- Evaluator Functions ---
    @staticmethod
    def calculate_employee_pf(db: Session, prorated_basic: float) -> Tuple[float, float, str]:
        rule = db.query(StatutoryRule).filter(StatutoryRule.rule_code == "IN_PF").first()
        ee_rate = float(rule.employee_rate) if rule else 0.12
        cap = float(rule.monthly_cap) if (rule and rule.monthly_cap) else 1800.0
        version = rule.rule_version if rule else "v2024.1"

        calculated_pf = round(prorated_basic * ee_rate, 2)
        capped_pf = min(cap, calculated_pf)
        return capped_pf, capped_pf, version

    @staticmethod
    def calculate_employee_esi(db: Session, gross_salary: float) -> Tuple[float, float, str]:
        rule = db.query(StatutoryRule).filter(StatutoryRule.rule_code == "IN_ESI").first()
        thresh = float(rule.eligibility_threshold) if (rule and rule.eligibility_threshold) else 21000.0
        ee_rate = float(rule.employee_rate) if rule else 0.0075
        er_rate = float(rule.employer_rate) if rule else 0.0325
        version = rule.rule_version if rule else "v2024.1"

        if gross_salary <= thresh:
            ee_esi = round(gross_salary * ee_rate, 2)
            er_esi = round(gross_salary * er_rate, 2)
            return ee_esi, er_esi, version
        return 0.0, 0.0, version

    @staticmethod
    def calculate_professional_tax(db: Session, gross_salary: float) -> float:
        if gross_salary > 15000.0:
            return 200.0
        return 0.0

    @staticmethod
    def calculate_tds_tax(db: Session, gross_monthly: float, regime_name: str = "New Regime") -> Dict[str, Any]:
        StatutoryEngineService.seed_defaults(db)
        tax_rule = db.query(TaxRule).filter(TaxRule.regime_name == regime_name, TaxRule.is_active == True).first()
        
        annual_gross = gross_monthly * 12.0
        std_ded = float(tax_rule.standard_deduction) if tax_rule else 75000.0
        taxable_annual = max(0.0, annual_gross - std_ded)

        # Evaluate Slabs
        tax_before_cess = 0.0
        if tax_rule and tax_rule.tax_slabs:
            for slab in tax_rule.tax_slabs:
                f_inc = float(slab.from_income)
                t_inc = float(slab.to_income) if slab.to_income else 999999999.0
                rate = float(slab.tax_rate)

                if taxable_annual > f_inc:
                    taxable_amount_in_slab = min(taxable_annual, t_inc) - f_inc
                    tax_before_cess += round(taxable_amount_in_slab * rate, 2)

        cess_rate = float(tax_rule.cess_rate) if tax_rule else 0.04
        cess_amount = round(tax_before_cess * cess_rate, 2)
        total_annual_tax = round(tax_before_cess + cess_amount, 2)
        monthly_tds = round(total_annual_tax / 12.0, 2)

        return {
            "annual_gross": annual_gross,
            "standard_deduction": std_ded,
            "taxable_annual": taxable_annual,
            "tax_before_cess": tax_before_cess,
            "cess_amount": cess_amount,
            "total_annual_tax": total_annual_tax,
            "monthly_tds": monthly_tds,
            "regime_name": regime_name,
            "rule_version": tax_rule.rule_version if tax_rule else "v2024.1",
        }
