import json
import re
from pathlib import Path

# -------------------------------------------------
# Load Skills Dictionary
# -------------------------------------------------

skills_path = Path(__file__).parent / "skills.json"

with open(skills_path, "r", encoding="utf-8") as f:
    SKILLS = json.load(f)

# Critical skills get higher priority in sorting
CRITICAL = {
    "sql",
    "etl",
    "tableau",
    "data modeling",
    "dashboard development"
}


# -------------------------------------------------
# Text Normalization
# -------------------------------------------------

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def count_alias(text, alias):
    alias = normalize(alias)
    pattern = r"\b" + re.escape(alias) + r"\b"
    return len(re.findall(pattern, text))


# -------------------------------------------------
# Resume Evidence Mapping
# -------------------------------------------------

def evidence(skill, resume):

    score = 0

    # SQL
    if skill == "sql":
        for k in [
            "joins",
            "join",
            "cte",
            "window function",
            "window functions",
            "group by",
            "order by",
            "stored procedure"
        ]:
            if k in resume:
                score += 1

    # ETL
    elif skill == "etl":
        for k in [
            "etl workflow",
            "pipeline automation",
            "data transformation",
            "workflow",
            "pipeline"
        ]:
            if k in resume:
                score += 1

    # Dashboard Development
    elif skill == "dashboard development":
        if "power bi" in resume:
            score += 2
        if "dashboard" in resume:
            score += 1

    # Data Warehousing
    elif skill == "data warehousing":
        if "snowflake" in resume:
            score += 2

    # Data Validation
    elif skill == "data validation":
        if "qa sample" in resume:
            score += 2
        elif "qa" in resume:
            score += 1
        elif "validation" in resume:
            score += 1

    # Large Datasets
    elif skill == "large datasets":
        if "240 dashboards" in resume:
            score += 2
        if "large dataset" in resume:
            score += 1

    # Performance Optimization
    elif skill == "performance optimization":
        if "automation" in resume:
            score += 1
        if "execution time" in resume:
            score += 1
        if "maintenance overhead" in resume:
            score += 1

    # Stakeholder Collaboration
    elif skill == "stakeholder collaboration":
        if "stakeholder" in resume:
            score += 1
        if "requirement gathering" in resume:
            score += 2

    # Power BI
    elif skill == "power bi":
        if "dax" in resume:
            score += 1
        if "power query" in resume:
            score += 1

    # DBT
    elif skill == "dbt":
        if "dbt cloud" in resume:
            score += 1

    return score


# -------------------------------------------------
# Compare Resume vs JD
# -------------------------------------------------

def compare(resume_text, jd_text):

    resume = normalize(resume_text)
    jd = normalize(jd_text)

    rows = []

    for skill, aliases in SKILLS.items():

        jd_hits = 0
        resume_hits = 0

        for alias in aliases:
            jd_hits += count_alias(jd, alias)
            resume_hits += count_alias(resume, alias)

        if jd_hits == 0:
            continue

        # Resume evidence bonus
        resume_hits += evidence(skill, resume)

        ratio = resume_hits / max(jd_hits, 1)

        if resume_hits == 0:
            status = "❌ Missing"

        elif ratio >= 0.60:
            status = "✅ Strong"

        elif ratio >= 0.25:
            status = "⚠️ Weak"

        else:
            status = "❌ Missing"

        rows.append((
            skill,
            jd_hits,
            resume_hits,
            status
        ))

    rows.sort(
        key=lambda x: (
            x[0] in CRITICAL,
            x[1],
            x[2]
        ),
        reverse=True
    )

    return rows