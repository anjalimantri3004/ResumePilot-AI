import html
import json
import re
import requests
from bs4 import BeautifulSoup

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT = True
except Exception:
    PLAYWRIGHT = False


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0 Safari/537.36"
    )
}


# -------------------------------------------------
# Clean extracted text
# -------------------------------------------------

def clean(text):

    if not text:
        return ""

    # Decode HTML entities
    text = html.unescape(text)

    text = text.replace("\xa0", " ")

    # Convert common HTML tags
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p>", "\n", text, flags=re.I)
    text = re.sub(r"<p[^>]*>", "", text, flags=re.I)

    # Remove formatting tags
    text = re.sub(
        r"</?(strong|b|em|i|ul|ol|li|div|span)[^>]*>",
        "",
        text,
        flags=re.I
    )

    # Remove any remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Clean spacing
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


# -------------------------------------------------
# Detect URL
# -------------------------------------------------

def is_url(text):
    return text.lower().startswith(("http://", "https://"))


# -------------------------------------------------
# Extract useful text from JSON
# -------------------------------------------------

def extract_from_json(obj):

    collected = []

    def walk(x):

        if isinstance(x, dict):

            for key, value in x.items():

                if isinstance(value, str):

                    key = key.lower()

                    if any(word in key for word in [
                        "description",
                        "responsibilities",
                        "qualification",
                        "requirements",
                        "jobdescription",
                        "overview",
                        "summary"
                    ]):

                        if len(value) > 30:
                            collected.append(value)

                else:
                    walk(value)

        elif isinstance(x, list):

            for item in x:
                walk(item)

    walk(obj)

    return clean(" ".join(collected))


# -------------------------------------------------
# Requests extraction
# -------------------------------------------------

def requests_extract(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=25
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Next.js JSON
        next_data = soup.find("script", id="__NEXT_DATA__")

        if next_data and next_data.string:

            try:
                text = extract_from_json(json.loads(next_data.string))

                if len(text) > 800:
                    return text

            except:
                pass

        # JSON-LD
        for script in soup.find_all(
            "script",
            type="application/ld+json"
        ):

            try:
                text = extract_from_json(json.loads(script.string))

                if len(text) > 800:
                    return text

            except:
                pass

        # Visible sections
        selectors = [
            "[class*=description]",
            "[class*=job]",
            "[class*=content]",
            "[id*=description]",
            "article",
            "main",
            "section"
        ]

        for selector in selectors:

            block = soup.select_one(selector)

            if block:

                text = clean(
                    block.get_text(" ", strip=True)
                )

                if len(text) > 800:
                    return text

        return clean(soup.get_text(" ", strip=True))

    except:
        return ""


# -------------------------------------------------
# Playwright extraction
# -------------------------------------------------

def playwright_extract(url):

    if not PLAYWRIGHT:
        return ""

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(headless=True)

            page = browser.new_page(
                user_agent=HEADERS["User-Agent"]
            )

            page.goto(
                url,
                wait_until="networkidle",
                timeout=45000
            )

            page.wait_for_timeout(3000)

            # Expand hidden content
            for text in [
                "Show more",
                "See more",
                "Read more",
                "View more"
            ]:

                try:
                    page.get_by_text(text).first.click(timeout=1000)
                except:
                    pass

            # Next.js JSON inside browser
            try:

                json_text = page.locator("#__NEXT_DATA__").inner_text()

                extracted = extract_from_json(json.loads(json_text))

                if len(extracted) > 800:
                    browser.close()
                    return extracted

            except:
                pass

            best = ""

            selectors = [
                "[class*=description]",
                "[class*=job]",
                "article",
                "main",
                "section",
                "body"
            ]

            for selector in selectors:

                try:

                    txt = clean(
                        page.locator(selector).first.inner_text()
                    )

                    if len(txt) > len(best):
                        best = txt

                except:
                    pass

            browser.close()

            return best

    except:
        return ""


# -------------------------------------------------
# Main Function
# -------------------------------------------------

def extract_job(job_input):

    job_input = job_input.strip()

    # User pasted Job Description
    if not is_url(job_input):
        return clean(job_input)

    text = requests_extract(job_input)

    if len(text) < 1200:

        pw = playwright_extract(job_input)

        if len(pw) > len(text):
            text = pw

    return clean(text)