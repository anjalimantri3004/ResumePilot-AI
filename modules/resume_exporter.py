import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
    HRFlowable,
    KeepTogether,
)

# =========================================================
# ResumePilot AI - Production Resume Exporter
# ATS Safe + Recruiter Friendly
# =========================================================

LINKEDIN_URL = "https://linkedin.com/in/anjali-mantri-683692240"
LINKEDIN_TEXT = "linkedin.com/in/anjali-mantri-683692240"

BLOCKED_SKILLS = {"tableau"}

# ---------------------------------------------------------
# Styles
# ---------------------------------------------------------

styles = getSampleStyleSheet()

NAME_STYLE = ParagraphStyle(
    "NameStyle",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=24,
    leading=28,
    alignment=TA_CENTER,
    textColor=colors.black,
    spaceAfter=6,
)

CONTACT_STYLE = ParagraphStyle(
    "ContactStyle",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10,
    leading=14,
    alignment=TA_CENTER,
    textColor=colors.black,
)

SECTION_STYLE = ParagraphStyle(
    "SectionStyle",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=15,
    textColor=colors.black,
    spaceBefore=12,
    spaceAfter=3,
)

ROLE_STYLE = ParagraphStyle(
    "RoleStyle",
    parent=styles["BodyText"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=14,
)

DATE_STYLE = ParagraphStyle(
    "DateStyle",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9,
    leading=11,
    alignment=TA_RIGHT,
)

BODY_STYLE = ParagraphStyle(
    "BodyStyle",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10,
    leading=15,
)

PROJECT_TITLE = ParagraphStyle(
    "ProjectTitle",
    parent=styles["BodyText"],
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=13,
)

# ---------------------------------------------------------
# Utilities
# ---------------------------------------------------------

def clean(text):

    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()

# ---------------------------------------------------------
# Contact Extraction
# ---------------------------------------------------------

def extract_contact(text):

    phone = re.search(
        r"(\+91[\s-]?)?[6-9]\d{9}",
        text,
    )

    email = re.search(
        r"[\w\.-]+@[\w\.-]+\.\w+",
        text,
    )

    return {
        "name": "Anjali Mantri",
        "phone": phone.group(0) if phone else "6375727784",
        "email": email.group(0) if email else "anjalimantrii30@gmail.com",
    }

# ---------------------------------------------------------
# JD Skill Prioritization
# ---------------------------------------------------------

DEFAULT_SKILLS = [
    "SQL",
    "Python",
    "Power BI",
    "Snowflake",
    "ETL",
    "Alteryx",
    "Excel",
    "DBT",
    "Power Automate",
]

def prioritize_skills(missing_skills=None):

    if missing_skills is None:
        missing_skills = []

    skills = DEFAULT_SKILLS.copy()

    for skill in missing_skills:

        if skill.lower() in BLOCKED_SKILLS:
            continue

        if skill not in skills:
            skills.append(skill)

    return skills

# ---------------------------------------------------------
# AI Tailored Summary
# ---------------------------------------------------------

def build_summary(missing_skills=None):

    if missing_skills is None:
        missing_skills = []

    summary = (
        "Business Data Analyst with hands-on experience at Thomson Reuters "
        "delivering SQL, Power BI, Snowflake, ETL and automation solutions. "
        "Experienced in dashboard development, reporting optimization, "
        "stakeholder collaboration and data transformation."
    )

    extra = []

    for skill in missing_skills:

        s = skill.lower()

        if s in BLOCKED_SKILLS:
            continue

        if s in {
            "data modeling",
            "data warehousing",
            "data validation",
            "performance optimization",
            "generative ai",
            "troubleshooting",
        }:
            extra.append(skill)

    if extra:

        summary += (
            " Familiar with concepts including "
            + ", ".join(extra)
            + "."
        )

    return summary

# ---------------------------------------------------------
# Experience Builder
# ---------------------------------------------------------

def experience_block():

    bullets = [
        "Built and optimized 240+ Power BI dashboards supporting business reporting.",
        "Achieved approximately 87% automation in digital inventory reporting workflows.",
        "Reduced reporting time from 45 minutes to 10 minutes through SQL, Snowflake and Alteryx automation.",
        "Reduced manual effort by approximately 80% through workflow automation.",
        "Collaborated with stakeholders to deliver business intelligence solutions."
    ]

    flow = [
        Paragraph(
            "Business Data Analyst",
            ROLE_STYLE,
        ),
        Paragraph(
            "<b>Thomson Reuters</b> | Bangalore | July 2025 – Present",
            BODY_STYLE,
        ),
        Spacer(1, 4),
        ListFlowable(
            [
                ListItem(
                    Paragraph(i, BODY_STYLE)
                )
                for i in bullets
            ],
            bulletType="bullet",
            leftIndent=15,
        ),
    ]

    return KeepTogether(flow)

# ---------------------------------------------------------
# Project Builder
# ---------------------------------------------------------

def projects_block():

    projects = [

        (
            "Retail Sales Dashboard | Power BI, Snowflake",
            [
                "Built KPI dashboards using Snowflake and Power BI with drill-through reporting.",
                "Delivered actionable business insights through interactive visualizations.",
            ],
        ),

        (
            "Payment Process Automation | Alteryx, Power Automate",
            [
                "Automated TAT reporting workflows using integrated data sources.",
                "Reduced manual effort by approximately 80% through end-to-end automation.",
            ],
        ),

        (
            "Pizza Sales Analysis | SQL",
            [
                "Developed SQL queries using JOINs, CTEs and Window Functions.",
                "Analyzed transactional sales data to identify business insights.",
            ],
        ),
    ]

    flow = []

    for title, bullets in projects:

        flow.append(Paragraph(title, PROJECT_TITLE))

        flow.append(
            ListFlowable(
                [
                    ListItem(Paragraph(b, BODY_STYLE))
                    for b in bullets
                ],
                bulletType="bullet",
                leftIndent=15,
            )
        )

        flow.append(Spacer(1, 6))

    return flow
# ---------------------------------------------------------
# Education Block
# ---------------------------------------------------------

def education_block():

    return Paragraph(
        "Bachelor of Engineering – Electronics & Computer Engineering | MBM University | Graduated May 2025 | CGPA: 7.0",
        BODY_STYLE,
    )

# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------

def section(title):

    return [
        Paragraph(title, SECTION_STYLE),
        HRFlowable(
            width="100%",
            thickness=0.8,
            color=colors.black,
        ),
        Spacer(1, 4),
    ]
# ---------------------------------------------------------
# Header Builder
# ---------------------------------------------------------

def build_header(contact):

    story = []

    story.append(
        Paragraph(
            contact["name"],
            NAME_STYLE
        )
    )

    contact_html = (
        f'{contact["phone"]} | '
        f'{contact["email"]} | '
        f'<link href="{LINKEDIN_URL}">{LINKEDIN_TEXT}</link>'
    )

    story.append(
        Paragraph(
            contact_html,
            CONTACT_STYLE
        )
    )

    story.append(Spacer(1, 12))

    return story


# ---------------------------------------------------------
# Skills Builder
# ---------------------------------------------------------

def skills_block(missing_skills):

    skills = prioritize_skills(missing_skills)

    return Paragraph(
        ", ".join(skills),
        BODY_STYLE
    )


# ---------------------------------------------------------
# Page Builder
# ---------------------------------------------------------

def build_story(resume_text, missing_skills):

    contact = extract_contact(resume_text)

    story = []

    # Header
    story.extend(build_header(contact))

    # Summary
    story.extend(section("PROFESSIONAL SUMMARY"))

    story.append(
        Paragraph(
            build_summary(missing_skills),
            BODY_STYLE
        )
    )

    story.append(Spacer(1, 10))

    # Skills
    story.extend(section("TECHNICAL SKILLS"))

    story.append(
        skills_block(missing_skills)
    )

    story.append(Spacer(1, 10))

    # Experience
    story.extend(section("PROFESSIONAL EXPERIENCE"))

    story.append(
        experience_block()
    )

    story.append(Spacer(1, 10))

    # Projects
    story.extend(section("PROJECTS"))

    story.extend(
        projects_block()
    )

    story.append(Spacer(1, 6))

    # Education
    story.extend(section("EDUCATION"))

    story.append(
        education_block()
    )

    story.append(Spacer(1, 6))

    return story


# ---------------------------------------------------------
# Main Export Function
# ---------------------------------------------------------

def generate_tailored_resume(
    resume_text,
    missing_skills=None,
    output_path="Tailored_Resume.pdf",
):

    """
    Generate ATS-safe recruiter-friendly resume PDF.

    Args:
        resume_text (str): Parsed resume text.
        missing_skills (list): Skills missing from ATS analysis.
        output_path (str): Output PDF path.

    Returns:
        str: Generated PDF path.
    """

    if missing_skills is None:
        missing_skills = []

    doc = SimpleDocTemplate(
        output_path,
        pagesize=(8.27 * inch, 11.69 * inch),   # A4
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )

    story = build_story(
        resume_text,
        missing_skills,
    )

    doc.build(story)

    return output_path


# ---------------------------------------------------------
# Local Test (Optional)
# ---------------------------------------------------------

if __name__ == "__main__":

    sample = """
    Anjali Mantri

    6375727784
    anjalimantrii30@gmail.com

    Business & Data Analyst at Thomson Reuters.
    """

    generate_tailored_resume(
        sample,
        missing_skills=["Data Modeling"],
        output_path="Sample_Tailored_Resume.pdf",
    )

    print("Resume generated successfully.")