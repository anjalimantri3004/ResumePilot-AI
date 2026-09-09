import re
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)

# ---------------------------------------------------------
# Fixed Candidate Information
# ---------------------------------------------------------

NAME = "Anjali Mantri"
PHONE = "6375727784"
EMAIL = "anjalimantrii30@gmail.com"
LINKEDIN = "linkedin.com/in/anjali-mantri-683692240"

# ---------------------------------------------------------
# Styles
# ---------------------------------------------------------

styles = getSampleStyleSheet()

BODY = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=11,
    leading=18,
    alignment=TA_LEFT,
)

NAME_STYLE = ParagraphStyle(
    "Name",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=24,
    alignment=TA_LEFT,
)

# ---------------------------------------------------------
# Company Detection
# ---------------------------------------------------------

KNOWN_COMPANIES = [
    "Amazon Web Services",
    "AWS",
    "Thomson Reuters",
    "Quest Global",
    "Deloitte",
    "Accenture",
    "Capgemini",
    "Infosys",
    "TCS",
    "Wipro",
    "Cognizant",
    "Microsoft",
    "Google",
]


def detect_company(jd_text):

    lower = jd_text.lower()

    for company in KNOWN_COMPANIES:

        if company.lower() in lower:
            return company

    return "your organization"


# ---------------------------------------------------------
# Role Detection
# ---------------------------------------------------------

ROLE_PATTERNS = [
    r'Business Data Analyst',
    r'Data Analyst',
    r'Business Intelligence Analyst',
    r'BI Analyst',
    r'Data Engineer',
    r'Analytics Engineer',
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

def extract_highlight_skills(jd_text):

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
        "Data Warehousing",
        "Dashboard Development",
        "Stakeholder Management",
    ]

    found = []

    lower = jd_text.lower()

    for skill in candidates:

        if skill.lower() in lower:
            found.append(skill)

    if not found:
        found = [
            "SQL",
            "Power BI",
            "Snowflake",
        ]

    return found[:5]


# ---------------------------------------------------------
# Cover Letter Generator
# ---------------------------------------------------------

def generate_cover_letter_text(resume_text, jd_text):

    company = detect_company(jd_text)
    role = detect_role(jd_text)
    skills = extract_highlight_skills(jd_text)

    skill_text = ", ".join(skills)

    today = datetime.today().strftime("%d %B %Y")

    letter = f"""
{today}

Dear Hiring Manager,

I am excited to apply for the {role} position at {company}. With hands-on experience at Thomson Reuters in Business Intelligence, reporting automation, SQL, Power BI, Snowflake and ETL workflows, I believe my background aligns well with the requirements outlined in your job description.

In my current role at Thomson Reuters, I have built and optimized more than 240 Power BI dashboards, improved reporting efficiency through automation, and contributed to digital inventory reporting initiatives. I have worked extensively with SQL, Snowflake, Alteryx, DBT and Power Automate to streamline business processes, reduce manual effort and deliver accurate reporting solutions for stakeholders.

The opportunity at {company} particularly interests me because it emphasizes {skill_text}. My experience collaborating with cross-functional teams, solving business problems through data analysis and delivering measurable process improvements would allow me to contribute effectively from day one.

I appreciate your time and consideration. I would welcome the opportunity to discuss how my technical skills, analytical mindset and business intelligence experience can contribute to your team's success.

Sincerely,

{NAME}
"""

    return letter.strip()


# ---------------------------------------------------------
# PDF Export
# ---------------------------------------------------------

def export_cover_letter_pdf(
    resume_text,
    jd_text,
    output_path="Cover_Letter.pdf"
):

    company = detect_company(jd_text)
    role = detect_role(jd_text)

    body_text = generate_cover_letter_text(
        resume_text,
        jd_text,
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=(8.27 * inch, 11.69 * inch),
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )

    story = []

    story.append(Paragraph(NAME, NAME_STYLE))
    story.append(Paragraph(PHONE, BODY))
    story.append(Paragraph(EMAIL, BODY))
    story.append(
        Paragraph(
            f'<link href="https://{LINKEDIN}">{LINKEDIN}</link>',
            BODY,
        )
    )

    story.append(Spacer(1, 18))

    for para in body_text.split("\n\n"):

        story.append(Paragraph(para.strip(), BODY))
        story.append(Spacer(1, 10))

    doc.build(story)

    return output_path