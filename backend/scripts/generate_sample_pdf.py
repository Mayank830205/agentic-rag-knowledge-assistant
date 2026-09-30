"""
Script to generate the fictional company policies PDF document for testing and demo.
Fictional Company: Apex Technologies Inc.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_sample_pdf(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    disclaimer_style = ParagraphStyle(
        'DisclaimerCustom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#C53030'),
        spaceAfter=15
    )

    story = []

    # Page 1: Title, Disclaimer, Leave Policy, Working Hours
    story.append(Paragraph("Apex Technologies Inc. - Employee Handbook & Policies", title_style))
    story.append(Paragraph("Internal Operations Manual & Corporate Guidelines (Version 2026.1)", subtitle_style))
    story.append(Paragraph("NOTICE: THIS IS FICTITIOUS SAMPLE DATA FOR AGENTRAG SYSTEM DEMONSTRATION PURPOSES ONLY.", disclaimer_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E0'), spaceAfter=15))

    story.append(Paragraph("1. Leave Policy", h1_style))
    story.append(Paragraph(
        "Apex Technologies believes in maintaining a healthy work-life balance for all team members. "
        "The following paid time off (PTO) provisions apply to all full-time employees:",
        body_style
    ))
    story.append(Paragraph("• <b>Annual Paid Leave:</b> All full-time employees are entitled to 20 days of paid annual leave per calendar year, accrued monthly at 1.66 days per completed month of service.", bullet_style))
    story.append(Paragraph("• <b>Sick Leave:</b> Employees receive 10 days of paid sick leave annually for medical illness, mental health days, or caring for immediate family members.", bullet_style))
    story.append(Paragraph("• <b>Parental Leave:</b> Primary caregivers receive 16 weeks of 100% paid parental leave, while secondary caregivers receive 8 weeks of paid leave following the birth or adoption of a child.", bullet_style))
    story.append(Paragraph("• <b>Bereavement Leave:</b> Up to 5 consecutive paid business days are granted for the loss of an immediate family member.", bullet_style))
    story.append(Paragraph("• <b>Leave Carryover:</b> Employees may carry over a maximum of 5 unused annual leave days into the subsequent year. All carried over days must be utilized before March 31st or they are forfeited.", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. Working Hours & Attendance Policy", h1_style))
    story.append(Paragraph(
        "Our standard work schedule is designed to promote collaboration across time zones while offering flexibility.",
        body_style
    ))
    story.append(Paragraph("• <b>Standard Work Week:</b> 40 hours per week, Monday through Friday.", bullet_style))
    story.append(Paragraph("• <b>Core Working Hours:</b> All employees are required to be online and available between 10:00 AM and 4:00 PM EST for meetings and cross-team synchronization.", bullet_style))
    story.append(Paragraph("• <b>Flexible Schedule:</b> The remaining 2 hours per day may be scheduled flexibly between 7:00 AM and 7:00 PM EST with manager approval.", bullet_style))
    story.append(Paragraph("• <b>Lunch Break:</b> A mandatory 60-minute unpaid lunch break is required for every shift exceeding 6 consecutive hours.", bullet_style))
    
    # Page Break to Page 2
    story.append(PageBreak())

    # Page 2: Remote Work & Employee Benefits
    story.append(Paragraph("Apex Technologies Inc. - Corporate Policies (Continued)", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E0'), spaceAfter=15))

    story.append(Paragraph("3. Remote & Hybrid Work Policy", h1_style))
    story.append(Paragraph(
        "Apex Technologies operates under a flexible hybrid model supporting both remote and in-office collaboration:",
        body_style
    ))
    story.append(Paragraph("• <b>Hybrid Requirements:</b> Employees residing within a 30-mile radius of a regional hub office are expected to work in-office at least 2 days per week (typically Tuesdays and Thursdays).", bullet_style))
    story.append(Paragraph("• <b>Fully Remote Status:</b> Employees designated as fully remote must maintain a quiet workspace, a dedicated desk, and high-speed broadband connection (minimum 50 Mbps download speed).", bullet_style))
    story.append(Paragraph("• <b>Home Office Equipment Stipend:</b> Newly hired full-time employees receive a one-time reimbursement of up to $500 for ergonomic office furniture and external monitors.", bullet_style))
    story.append(Paragraph("• <b>Internet & Utilities Subsidy:</b> Remote and hybrid employees receive a monthly tax-free reimbursement of $60 to assist with high-speed internet and utility expenses.", bullet_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("4. Employee Benefits & Wellness Program", h1_style))
    story.append(Paragraph(
        "Comprehensive health, retirement, and continuous learning benefits are provided to all permanent staff:",
        body_style
    ))
    story.append(Paragraph("• <b>Health, Dental, & Vision:</b> Company covers 90% of healthcare premiums for employees and 75% for eligible dependents, effective from the first day of employment.", bullet_style))
    story.append(Paragraph("• <b>401(k) Retirement Plan:</b> Apex matches 100% of employee contributions up to 5% of annual base salary with immediate vesting.", bullet_style))
    story.append(Paragraph("• <b>Professional Development Stipend:</b> Each employee has an annual budget of $1,200 for technical certifications, conferences, books, and courses.", bullet_style))
    story.append(Paragraph("• <b>Wellness Allowance:</b> Employees receive a $50 monthly allowance toward gym memberships, yoga classes, or wellness applications.", bullet_style))

    # Page Break to Page 3
    story.append(PageBreak())

    # Page 3: Customer Refund Policy & Confidentiality
    story.append(Paragraph("Apex Technologies Inc. - Customer & Service Policies", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E0'), spaceAfter=15))

    story.append(Paragraph("5. Customer & Subscription Refund Policy", h1_style))
    story.append(Paragraph(
        "This policy governs customer refunds, subscription cancellations, and billing disputes across all software licenses and cloud services offered by Apex Technologies:",
        body_style
    ))
    story.append(Paragraph("• <b>Monthly Software Subscriptions:</b> Customers may cancel their monthly software subscription at any time. A full refund is granted if cancellation occurs within 14 calendar days of the initial subscription start date.", bullet_style))
    story.append(Paragraph("• <b>Annual Enterprise Contracts:</b> Annual enterprise commitments cancelled within 30 days of contract execution are eligible for a prorated refund minus a 10% administrative processing fee. Cancellations requested after 30 days are non-refundable.", bullet_style))
    story.append(Paragraph("• <b>Professional Services & Implementation Fees:</b> Dedicated architectural onboarding and custom software development fees are strictly non-refundable once engineering work has commenced.", bullet_style))
    story.append(Paragraph("• <b>Refund Processing Timeline:</b> Approved refunds will be issued to the original payment method within 5 to 7 business days following formal confirmation by the billing team.", bullet_style))
    story.append(Paragraph("• <b>Billing Dispute Inquiries:</b> To initiate a refund request, customers must email support@apextechnologies-sample.com with their invoice number and reason for cancellation.", bullet_style))
    story.append(Spacer(1, 15))

    story.append(Paragraph("Summary Note", h1_style))
    story.append(Paragraph(
        "This corporate policy document is reviewed annually by the People Operations and Legal departments. "
        "Any questions regarding the interpretation of these guidelines should be directed to hr@apextechnologies-sample.com.",
        body_style
    ))

    doc.build(story)
    print(f"Sample PDF generated successfully at: {output_path}")

if __name__ == "__main__":
    target = os.path.join("data", "documents", "sample_company_policies.pdf")
    create_sample_pdf(target)
