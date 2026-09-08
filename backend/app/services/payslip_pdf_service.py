import io
import zipfile
from typing import List
from sqlalchemy.orm import Session
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

from app.models.payroll_run import PayrollEmployee, PayrollRun, PayrollPeriod
from app.models.employee import Employee
from app.models.organization import Company
from app.core.exceptions import PayrollException



def number_to_words(amount: float) -> str:
    """Helper converter for INR currency format into words."""
    try:
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

        amt_int = int(amount)
        if amt_int == 0:
            return "Zero Rupees Only"

        def convert_less_than_thousand(n):
            out = ""
            if n >= 100:
                out += units[n // 100] + " Hundred "
                n %= 100
            if n >= 10 and n <= 19:
                out += teens[n - 10] + " "
            elif n >= 20:
                out += tens[n // 10] + " " + units[n % 10] + " "
            elif n > 0:
                out += units[n] + " "
            return out.strip()

        # Indian Numbering System: Crore (10^7), Lakh (10^5), Thousand (10^3)
        crore = amt_int // 10000000
        amt_int %= 10000000
        lakh = amt_int // 100000
        amt_int %= 100000
        thousand = amt_int // 1000
        amt_int %= 1000
        remainder = amt_int

        parts = []
        if crore > 0:
            parts.append(f"{convert_less_than_thousand(crore)} Crore")
        if lakh > 0:
            parts.append(f"{convert_less_than_thousand(lakh)} Lakh")
        if thousand > 0:
            parts.append(f"{convert_less_than_thousand(thousand)} Thousand")
        if remainder > 0:
            parts.append(convert_less_than_thousand(remainder))

        return "Rupees " + " ".join(parts).strip() + " Only"
    except Exception:
        return f"Rupees {amount:,.2f} Only"


class PayslipPDFService:

    @staticmethod
    def generate_payslip_pdf(db: Session, payroll_employee: PayrollEmployee) -> bytes:
        """Generates a professional ReportLab PDF for a single employee's monthly payslip."""
        if not HAS_REPORTLAB:
            raise PayrollException("ReportLab package is required for PDF generation. Please run 'pip install reportlab'.", error_code="REPORTLAB_MISSING")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(

            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle(
            'CompanyTitle',
            parent=styles['Heading1'],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor('#1E293B'),
            fontName='Helvetica-Bold'
        )
        subtitle_style = ParagraphStyle(
            'PayslipSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#0F766E'),
            fontName='Helvetica-Bold'
        )
        body_style = ParagraphStyle(
            'NormalBody',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#334155')
        )
        header_table_style = ParagraphStyle(
            'HeaderTable',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#475569'),
            fontName='Helvetica-Bold'
        )

        elements = []

        # 1. Company Header
        employee: Employee = payroll_employee.employee
        payroll_run: PayrollRun = payroll_employee.payroll_run
        payroll_period: PayrollPeriod = payroll_run.payroll_period

        company_name = "ENTERPRISE PAYROLL SYSTEMS PVT LTD"
        if employee and employee.company:
            company_name = employee.company.name.upper()

        elements.append(Paragraph(company_name, title_style))
        elements.append(Paragraph(f"PAYSLIP FOR THE MONTH OF {payroll_period.name.upper()} ({payroll_period.year_month})", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F766E'), spaceAfter=12))

        # 2. Employee Metadata Grid
        emp_code = f"EMP-{employee.id:04d}" if employee else "EMP-0000"
        emp_name = f"{employee.first_name} {employee.last_name}" if employee else "N/A"
        dept_name = employee.department.name if (employee and employee.department) else "General"
        desig_name = employee.designation.title if (employee and employee.designation) else "Staff"

        meta_data = [
            [
                Paragraph("<b>Employee ID:</b>", header_table_style), Paragraph(emp_code, body_style),
                Paragraph("<b>Bank A/C:</b>", header_table_style), Paragraph(getattr(employee, 'bank_account_number', 'HDFC****9812'), body_style)
            ],
            [
                Paragraph("<b>Employee Name:</b>", header_table_style), Paragraph(emp_name, body_style),
                Paragraph("<b>PAN Number:</b>", header_table_style), Paragraph(getattr(employee, 'pan_number', 'ABCDE1234F'), body_style)
            ],
            [
                Paragraph("<b>Department:</b>", header_table_style), Paragraph(dept_name, body_style),
                Paragraph("<b>PF UAN:</b>", header_table_style), Paragraph(getattr(employee, 'pf_uan', '100918273645'), body_style)
            ],
            [
                Paragraph("<b>Designation:</b>", header_table_style), Paragraph(desig_name, body_style),
                Paragraph("<b>ESI Number:</b>", header_table_style), Paragraph(getattr(employee, 'esi_number', '3100123456'), body_style)
            ],
            [
                Paragraph("<b>Days in Month:</b>", header_table_style), Paragraph(str(payroll_employee.total_days), body_style),
                Paragraph("<b>Payable Days:</b>", header_table_style), Paragraph(str(payroll_employee.payable_days), body_style)
            ],
        ]

        meta_table = Table(meta_data, colWidths=[90, 170, 90, 170])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 14))

        # 3. Itemized Earnings & Deductions Breakdown
        earnings_rows = []
        for e in payroll_employee.earnings:
            earnings_rows.append((e.name, f"₹{e.prorated_amount:,.2f}"))
        
        deductions_rows = []
        for d in payroll_employee.deductions:
            deductions_rows.append((d.name, f"₹{d.amount:,.2f}"))

        max_rows = max(len(earnings_rows), len(deductions_rows))
        
        table_body = [
            [
                Paragraph("<b>EARNINGS</b>", header_table_style),
                Paragraph("<b>AMOUNT</b>", header_table_style),
                Paragraph("<b>DEDUCTIONS</b>", header_table_style),
                Paragraph("<b>AMOUNT</b>", header_table_style)
            ]
        ]

        for idx in range(max_rows):
            earn_title, earn_val = earnings_rows[idx] if idx < len(earnings_rows) else ("", "")
            ded_title, ded_val = deductions_rows[idx] if idx < len(deductions_rows) else ("", "")
            table_body.append([
                Paragraph(earn_title, body_style),
                Paragraph(earn_val, body_style),
                Paragraph(ded_title, body_style),
                Paragraph(ded_val, body_style)
            ])

        # Totals Row
        table_body.append([
            Paragraph("<b>TOTAL GROSS EARNINGS</b>", header_table_style),
            Paragraph(f"<b>₹{payroll_employee.gross_salary:,.2f}</b>", header_table_style),
            Paragraph("<b>TOTAL DEDUCTIONS</b>", header_table_style),
            Paragraph(f"<b>₹{payroll_employee.total_deductions:,.2f}</b>", header_table_style)
        ])

        fin_table = Table(table_body, colWidths=[170, 90, 170, 90])
        fin_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#ECFDF5')),
            ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#FEF2F2')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F1F5F9')),
        ]))
        elements.append(fin_table)
        elements.append(Spacer(1, 14))

        # 4. Net Salary Summary
        net_words = number_to_words(payroll_employee.net_salary)
        net_data = [
            [
                Paragraph("<b>NET TAKE-HOME SALARY:</b>", ParagraphStyle('NetLbl', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#065F46'))),
                Paragraph(f"<b>₹{payroll_employee.net_salary:,.2f}</b>", ParagraphStyle('NetAmt', parent=styles['Normal'], fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#047857')))
            ],
            [
                Paragraph(f"<b>Amount in Words:</b> {net_words}", ParagraphStyle('NetWords', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Oblique', textColor=colors.HexColor('#1E293B'))),
                ""
            ]
        ]

        net_table = Table(net_data, colWidths=[380, 140])
        net_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#D1FAE5')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#059669')),
            ('SPAN', (0, 1), (1, 1)),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(net_table)
        elements.append(Spacer(1, 24))

        # 5. Footer & Seal Placeholder
        footer_data = [
            [
                Paragraph("<i>This is a computer-generated document and does not require a physical signature.</i>", body_style),
                Paragraph("<b>Authorized Signatory</b><br/><br/>[System Verified]", ParagraphStyle('Sig', parent=styles['Normal'], fontSize=9, alignment=1))
            ]
        ]
        footer_table = Table(footer_data, colWidths=[340, 180])
        elements.append(footer_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def generate_bulk_payslips_zip(db: Session, payroll_run_id: int) -> bytes:
        """Generates a ZIP archive containing PDF payslips for all employees in a payroll run."""
        payroll_run = db.query(PayrollRun).filter(PayrollRun.id == payroll_run_id).first()
        if not payroll_run:
            raise PayrollException("PAYROLL_RUN_NOT_FOUND", f"Payroll run {payroll_run_id} not found")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for emp_res in payroll_run.employee_results:
                pdf_bytes = PayslipPDFService.generate_payslip_pdf(db, emp_res)
                emp_name = f"Emp_{emp_res.employee_id}_{emp_res.employee.first_name if emp_res.employee else 'Staff'}"
                file_name = f"Payslip_{payroll_run.payroll_period.year_month}_{emp_name}.pdf"
                zip_file.writestr(file_name, pdf_bytes)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()
