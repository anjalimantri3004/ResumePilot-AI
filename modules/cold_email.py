import re
from datetime import datetime
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# ---------------------------------------------------------
# Candidate Information
# ---------------------------------------------------------

NAME = "Anjali Mantri"
PHONE = "6375727784"
EMAIL = "anjalimantrii30@gmail.com"
LINKEDIN = "linkedin.com/in/anjali-mantri-683692240"

styles = getSampleStyleSheet()

TITLE = ParagraphStyle(
    "Title",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=20,
    leading=24,
)

BODY = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=11,
    leading=17,
    alignment=TA_LEFT,
)

# ---------------------------------------------------------
# Company Detection
# ---------------------------------------------------------

COMPANIES = [
    "Quest Global",
    "Amazon Web Services",
    "AWS",
    "Deloitte",
    "Accenture",
    "Capgemini",
    "Microsoft",
    "Google",
    "Infosys",
    "TCS",
]

def detect_company(jd_text):
    lower = jd_text.lower()
    for company in COMPANIES:
        if company.lower() in lower:
            return company
    return "your organization"

# ---------------------------------------------------------
# Role Detection
# ---------------------------------------------------------

ROLE_PATTERNS = [
    r"Business Data Analyst",
    r"Data Analyst",
    r"BI Analyst",
    r"Business Intelligence Analyst",
]

def detect_role(jd_text):
    for pattern in ROLE_PATTERNS:
        m = re.search(pattern, jd_text, re.IGNORECASE)
        if m:
            return m.group(0)
    return "Business Data Analyst"

# ---------------------------------------------------------
# Skill Extraction
# ---------------------------------------------------------

def detect_skills(jd_text):

    skills = []

    candidates = [
        "SQL",
        "Python",
        "Power BI",
        "Snowflake",
        "ETL",
        "DBT",
        "Excel",
        "Power Automate",
        "Data Modeling",
    ]

    lower = jd_text.lower()

    for skill in candidates:
        if skill.lower() in lower:
            skills.append(skill)

    if not skills:
        skills = ["SQL", "Power BI", "Snowflake"]

    return skills[:5]

# ---------------------------------------------------------
# Subject
# ---------------------------------------------------------

def generate_subject(jd_text):

    company = detect_company(jd_text)
    role = detect_role(jd_text)

    return f"Application for {role} – {company}"

# ---------------------------------------------------------
# HR Email
# ---------------------------------------------------------

def generate_hr_email(resume_text, jd_text):

    company = detect_company(jd_text)
    role = detect_role(jd_text)

    return f"""Hi,

I came across the {role} opening at {company} and found that my experience aligns well with the role.

At Thomson Reuters, I've worked on SQL, Power BI, Snowflake and ETL workflows, including building 240+ dashboards and improving reporting efficiency through automation.

I've attached my resume and would appreciate the opportunity to discuss how I can contribute to your team.

Regards,
{NAME}
{PHONE}
"""

# ---------------------------------------------------------
# Hiring Manager Email
# ---------------------------------------------------------

def generate_manager_email(resume_text, jd_text):

    company = detect_company(jd_text)
    role = detect_role(jd_text)

    skills = ", ".join(detect_skills(jd_text))

    return f"""Dear Hiring Manager,

I hope you're doing well.

I recently came across the {role} opportunity at {company} and wanted to express my interest.

My experience at Thomson Reuters includes SQL, Power BI, Snowflake, ETL automation and stakeholder-focused reporting. I've contributed to building 240+ dashboards, improving reporting efficiency and delivering automation-driven business solutions.

The role's emphasis on {skills} strongly aligns with my background.

I'd appreciate the opportunity to connect and discuss how I can contribute to your team.

Best regards,
{NAME}
"""

# ---------------------------------------------------------
# LinkedIn DM
# ---------------------------------------------------------

def generate_linkedin_dm(resume_text, jd_text):

    company = detect_company(jd_text)
    role = detect_role(jd_text)

    return (
        f"Hi! I came across the {role} opening at {company}. "
        f"I'm currently a Business Data Analyst at Thomson Reuters with experience "
        f"in SQL, Power BI and Snowflake. I'd love to connect and learn more about the opportunity."
    )

# ---------------------------------------------------------
# PDF Export
# ---------------------------------------------------------

def export_cold_email_pdf(
    resume_text,
    jd_text,
    output_path="Cold_Email_Kit.pdf"
):

    doc = SimpleDocTemplate(
        output_path,
        pagesize=(8.27*inch,11.69*inch),
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=0.7*inch,
        bottomMargin=0.7*inch,
    )

    story = []

    story.append(Paragraph(NAME, TITLE))
    story.append(Paragraph(PHONE, BODY))
    story.append(Paragraph(EMAIL, BODY))
    story.append(Paragraph(LINKEDIN, BODY))
    story.append(Spacer(1,18))

    story.append(Paragraph("<b>Subject</b>", BODY))
    story.append(Paragraph(generate_subject(jd_text), BODY))
    story.append(Spacer(1,12))

    story.append(Paragraph("<b>HR Email</b>", BODY))
    story.append(Paragraph(generate_hr_email(resume_text, jd_text).replace("\n","<br/>"), BODY))
    story.append(Spacer(1,12))

    story.append(Paragraph("<b>Hiring Manager Email</b>", BODY))
    story.append(Paragraph(generate_manager_email(resume_text, jd_text).replace("\n","<br/>"), BODY))
    story.append(Spacer(1,12))

    story.append(Paragraph("<b>LinkedIn Message</b>", BODY))
    story.append(Paragraph(generate_linkedin_dm(resume_text, jd_text), BODY))

    doc.build(story)

    return output_path