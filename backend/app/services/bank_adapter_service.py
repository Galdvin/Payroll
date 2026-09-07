import hashlib
import io
import csv
from typing import Tuple
from sqlalchemy.orm import Session
from app.models.payroll_run import PayrollRun, PayrollEmployee
from app.models.bank_payment import BankPaymentBatch
from app.core.exceptions import PayrollException


class BankAdapterService:

    @staticmethod
    def generate_bank_payment_file(db: Session, payroll_run_id: int, bank_format: str) -> Tuple[bytes, BankPaymentBatch, str]:
        """Generates bank disbursement payload for HDFC, ICICI, SBI, or ISO20022 formats."""
        run = db.query(PayrollRun).filter(PayrollRun.id == payroll_run_id).first()
        if not run:
            raise PayrollException("RUN_NOT_FOUND", f"Payroll run {payroll_run_id} not found")

        employees = run.employee_results
        if not employees:
            raise PayrollException("NO_EMPLOYEE_RESULTS", "Payroll run has no employee calculation results")

        fmt = bank_format.upper()
        content_bytes = b""
        filename = f"Salaries_{fmt}_{run.payroll_period.year_month}.txt"

        if fmt == "HDFC_CMS":
            content_bytes = BankAdapterService._build_hdfc_cms(employees)
            filename = f"HDFC_CMS_{run.payroll_period.year_month}.txt"
        elif fmt == "ICICI_CIB":
            content_bytes = BankAdapterService._build_icici_cib(employees)
            filename = f"ICICI_CIB_{run.payroll_period.year_month}.csv"
        elif fmt == "SBI_CMP":
            content_bytes = BankAdapterService._build_sbi_cmp(employees)
            filename = f"SBI_CMP_{run.payroll_period.year_month}.txt"
        elif fmt == "ISO20022":
            content_bytes = BankAdapterService._build_iso20022(employees)
            filename = f"ISO20022_{run.payroll_period.year_month}.xml"
        else:
            raise PayrollException("UNSUPPORTED_BANK_FORMAT", f"Bank format '{bank_format}' is not supported")

        checksum = hashlib.sha256(content_bytes).hexdigest()

        # Save batch record
        batch = BankPaymentBatch(
            payroll_run_id=payroll_run_id,
            bank_format=fmt,
            total_records=len(employees),
            total_amount=run.total_net,
            checksum_hash=checksum,
            status="GENERATED",
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)

        return content_bytes, batch, filename

    @staticmethod
    def _build_hdfc_cms(employees) -> bytes:
        lines = ["HDFC_CMS_HEADER|SALARY_DISBURSEMENT|VER_2.0"]
        for emp in employees:
            acc = getattr(emp.employee, 'bank_account_number', 'HDFC987654321')
            ifsc = getattr(emp.employee, 'bank_ifsc', 'HDFC0001234')
            name = f"{emp.employee.first_name} {emp.employee.last_name}" if emp.employee else "Staff"
            line = f"FT|{acc}|{emp.net_salary:.2f}|{name}|{ifsc}|SALARY_{emp.payroll_run_id}"
            lines.append(line)
        return "\n".join(lines).encode('utf-8')

    @staticmethod
    def _build_icici_cib(employees) -> bytes:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["TransactionRef", "BeneficiaryAccount", "Amount", "Currency", "BeneficiaryName", "IFSC", "PaymentMode"])
        for emp in employees:
            acc = getattr(emp.employee, 'bank_account_number', 'ICIC987654321')
            ifsc = getattr(emp.employee, 'bank_ifsc', 'ICIC0001234')
            name = f"{emp.employee.first_name} {emp.employee.last_name}" if emp.employee else "Staff"
            writer.writerow([f"TXN-{emp.id}", acc, f"{emp.net_salary:.2f}", "INR", name, ifsc, "NEFT"])
        return output.getvalue().encode('utf-8')

    @staticmethod
    def _build_sbi_cmp(employees) -> bytes:
        lines = ["CMP_SBI_BATCH_HEADER"]
        for emp in employees:
            acc = getattr(emp.employee, 'bank_account_number', 'SBIN987654321')
            ifsc = getattr(emp.employee, 'bank_ifsc', 'SBIN0001234')
            name = f"{emp.employee.first_name} {emp.employee.last_name}" if emp.employee else "Staff"
            lines.append(f"CMP|{acc}|{emp.net_salary:.2f}|INR|{name}|{ifsc}|N")
        return "\n".join(lines).encode('utf-8')

    @staticmethod
    def _build_iso20022(employees) -> bytes:
        xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">', '<CstmrCdtTrfInitn>']
        for emp in employees:
            acc = getattr(emp.employee, 'bank_account_number', 'ISO987654321')
            name = f"{emp.employee.first_name} {emp.employee.last_name}" if emp.employee else "Staff"
            xml.append('  <PmtInf>')
            xml.append(f'    <Cdtr>{name}</Cdtr>')
            xml.append(f'    <Amt Ccy="INR">{emp.net_salary:.2f}</Amt>')
            xml.append(f'    <CdtrAcct><Id><Othr><Id>{acc}</Id></Othr></Id></CdtrAcct>')
            xml.append('  </PmtInf>')
        xml.append('</CstmrCdtTrfInitn>')
        xml.append('</Document>')
        return "\n".join(xml).encode('utf-8')
