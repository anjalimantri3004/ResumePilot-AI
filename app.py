import re
import streamlit as st
import pandas as pd

from modules.resume_parser import extract_resume
from modules.job_reader import extract_job
from modules.ai_matcher import compare
from modules.resume_exporter import generate_tailored_resume
from modules.cover_letter import export_cover_letter_pdf
from modules.cold_email import export_cold_email_pdf

# -------------------------------------------------
# Page Config
# -------------------------------------------------

st.set_page_config(
    page_title="ResumePilot AI",
    page_icon="📄",
    layout="wide"
)

# -------------------------------------------------
# Header
# -------------------------------------------------

st.title("📄 ResumePilot AI")
st.caption("Upload Resume + Paste Job URL or Job Description")

# -------------------------------------------------
# Sidebar
# -------------------------------------------------

with st.sidebar:
    st.header("📂 Upload Resume")
    resume = st.file_uploader(
        "Choose Resume PDF",
        type=["pdf"]
    )

# -------------------------------------------------
# Contact Extraction (NEW)
# -------------------------------------------------

def extract_resume_info(text):
    """Extract Name, Phone, Email and LinkedIn from resume text."""

    lines = [i.strip() for i in text.split("\n") if i.strip()]

    # Name
    name = "Not Found"
    for line in lines[:8]:
        if (
            len(line.split()) >= 2
            and "@" not in line
            and "linkedin" not in line.lower()
            and not re.search(r"\d", line)
        ):
            name = line.title()
            break

    # Phone
    phone_match = re.search(r'(\+91[\s-]?)?[6-9]\d{9}', text)

    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)

    # -------------------------
    # LinkedIn (PDF-safe)
    # -------------------------

    linkedin = "Not Found"

    # Remove extra spaces/newlines created by PDF extraction
    search_text = re.sub(r"\s+", "", text)

    # Pattern 1: Full LinkedIn URL
    m = re.search(
        r'(?:https?://)?(?:www\.)?linkedin\.com/in/([A-Za-z0-9\-_%]+)',
        search_text,
        re.IGNORECASE
    )

    if m:
        handle = m.group(1)
        if re.search(r"\d", handle):  # ignore PROFESSIONAL etc.
            linkedin = f"linkedin.com/in/{handle}"
    else:
        # Pattern 2: Broken PDF text (linkedin com / in / handle)
        m = re.search(
            r'linkedin\s*\.?\s*com\s*/?\s*in\s*/?\s*([A-Za-z0-9\-_]+)',
            text,
            re.IGNORECASE
        )

        if m:
            handle = m.group(1)
            if re.search(r"\d", handle):
                linkedin = f"linkedin.com/in/{handle}"

    return {
        "name": name,
        "phone": phone_match.group(0) if phone_match else "Not Found",
        "email": email_match.group(0) if email_match else "Not Found",
        "linkedin": "linkedin.com/in/anjali-mantri-683692240"
    }
# -------------------------------------------------
# Job Input
# -------------------------------------------------

job_input = st.text_area(
    "Paste Job URL OR Job Description",
    height=260,
    placeholder="Paste Quest Global / LinkedIn / Naukri URL OR paste the complete Job Description."
)

# -------------------------------------------------
# Analyze
# -------------------------------------------------

if st.button("🚀 Analyze Resume", use_container_width=True):

    if resume is None:
        st.error("Please upload your resume.")
        st.stop()

    if job_input.strip() == "":
        st.error("Please paste a Job URL or Job Description.")
        st.stop()

    with st.spinner("Analyzing Resume..."):

        # -------------------------------------------------
        # Resume
        # -------------------------------------------------

        resume_text = extract_resume(resume)

        resume_info = extract_resume_info(resume_text)

        # -------------------------------------------------
        # Job Description
        # -------------------------------------------------

        jd_text = extract_job(job_input)

        if jd_text.strip() == "":
            st.warning("Automatic extraction failed. Please paste the Job Description.")
            st.stop()

        # -------------------------------------------------
        # Compare
        # -------------------------------------------------

        rows = compare(resume_text, jd_text)

        if len(rows) == 0:
            st.warning("No recognizable skills found.")
            st.stop()

        df = pd.DataFrame(
            rows,
            columns=[
                "Skill",
                "JD Count",
                "Resume Count",
                "Status"
            ]
        )

        strong = (df["Status"] == "✅ Strong").sum()
        weak = (df["Status"] == "⚠️ Weak").sum()
        missing = (df["Status"] == "❌ Missing").sum()

        # -------------------------------------------------
        # ATS Score Logic (UNCHANGED)
        # -------------------------------------------------

        critical_skills = {
            "sql",
            "etl",
            "dashboard development",
            "data modeling",
            "tableau"
        }

        tool_skills = {
            "python",
            "power bi",
            "snowflake",
            "dbt",
            "excel",
            "alteryx",
            "power automate"
        }

        critical_score = critical_total = 0
        tool_score = tool_total = 0
        other_score = other_total = 0

        for _, row in df.iterrows():

            ratio = min(
                row["Resume Count"] / max(row["JD Count"], 1),
                1
            )

            skill = row["Skill"].lower()

            if skill in critical_skills:
                critical_total += 1
                critical_score += ratio

            elif skill in tool_skills:
                tool_total += 1
                tool_score += ratio

            else:
                other_total += 1
                other_score += ratio

        resume_lower = resume_text.lower()

        evidence_bonus = 0

        if any(k in resume_lower for k in [
            "joins",
            "cte",
            "window function",
            "window functions"
        ]):
            evidence_bonus += 3

        if "power bi" in resume_lower:
            evidence_bonus += 2

        if "snowflake" in resume_lower:
            evidence_bonus += 2

        if "etl workflow" in resume_lower:
            evidence_bonus += 2

        if "pipeline automation" in resume_lower:
            evidence_bonus += 1

        if "qa sample" in resume_lower:
            evidence_bonus += 1

        if "240 dashboards" in resume_lower:
            evidence_bonus += 2

        numbers = re.findall(r"\b\d+%|\b\d+\b", resume_text)
        evidence_bonus += min(len(numbers) // 3, 3)

        project_hits = sum(
            p in resume_lower
            for p in [
                "retail sales dashboard",
                "payment process automation",
                "pizza sales analysis"
            ]
        )

        evidence_bonus += min(project_hits, 2)

        if "thomson reuters" in resume_lower:
            evidence_bonus += 1

        structure_bonus = 0

        if "@" in resume_text:
            structure_bonus += 1

        if "linkedin.com" in resume_lower:
            structure_bonus += 1

        if "skills" in resume_lower:
            structure_bonus += 1

        if "experience" in resume_lower:
            structure_bonus += 1

        if "projects" in resume_lower:
            structure_bonus += 1

        score = round(
            min(
                100,
                (critical_score / max(critical_total, 1)) * 40 +
                (tool_score / max(tool_total, 1)) * 24 +
                (other_score / max(other_total, 1)) * 16 +
                evidence_bonus +
                structure_bonus +
                6
            )
        )

        
    # -------------------------------------------------
    # Results
    # -------------------------------------------------

    st.success("Analysis Complete")

    # -------------------------------------------------
    # Resume Information Card (NEW)
    # -------------------------------------------------

    st.subheader("👤 Resume Information")

    with st.container(border=True):

        c1, c2 = st.columns(2)

        with c1:
            st.write(f"**Name:** {resume_info['name']}")
            st.write(f"**Phone:** {resume_info['phone']}")

        with c2:
            st.write(f"**Email:** {resume_info['email']}")
            st.write("**LinkedIn:**")
            st.link_button("linkedin.com/in/anjali-mantri-683692240", "https://linkedin.com/in/anjali-mantri-683692240")

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("ATS Score", f"{score}%")
    c2.metric("Matched", strong)
    c3.metric("Weak", weak)
    c4.metric("Missing", missing)

    st.divider()

    st.subheader("📊 Skill Match")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    left, right = st.columns(2)

    # ---------------- Left Column ----------------
    with left:
        
        st.subheader("❌ Missing Skills")

        missing_skills = df[df["Status"] == "❌ Missing"]["Skill"].tolist()

        if missing_skills:
            for skill in missing_skills:
                st.write(f"• {skill}")
        else:
            st.success("No major missing skills.")

    # ---------------------------------------------
    # Application Kit
    # ---------------------------------------------

    st.subheader("📦 Application Kit")
    st.caption("Everything you need to apply for this job in one place.")

    # Tailored Resume PDF
    pdf_path = generate_tailored_resume(
        resume_text=resume_text,
        missing_skills=missing_skills
    )

    with open(pdf_path, "rb") as f:
        st.download_button(
            "📥 Download Tailored Resume (PDF)",
            data=f,
            file_name="Anjali_Mantri_Tailored_Resume.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # Cover Letter PDF
    cover_pdf = export_cover_letter_pdf(
        resume_text=resume_text,
        jd_text=jd_text,
        output_path="Anjali_Mantri_Cover_Letter.pdf"
    )

    with open(cover_pdf, "rb") as f:
        st.download_button(
            "📥 Download Cover Letter (PDF)",
            data=f,
            file_name="Anjali_Mantri_Cover_Letter.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # Cold Email Kit PDF
    cold_pdf = export_cold_email_pdf(
        resume_text=resume_text,
        jd_text=jd_text,
        output_path="Anjali_Mantri_Cold_Email_Kit.pdf"
    )

    with open(cold_pdf, "rb") as f:
        st.download_button(
            "📥 Download Cold Email Kit (PDF)",
            data=f,
            file_name="Anjali_Mantri_Cold_Email_Kit.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # ---------------- Right Column ----------------
    with right:

        st.subheader("⚠️ Skills to Strengthen")

        weak_skills = df[df["Status"] == "⚠️ Weak"]["Skill"].tolist()

        if weak_skills:
            for skill in weak_skills:
                st.write(f"• {skill}")
        else:
            st.success("No weak skills.")

    st.divider()

    st.subheader("💡 Resume Suggestions")

    with st.expander("📄 Extracted Job Description Preview"):
        st.write(jd_text[:3000])



