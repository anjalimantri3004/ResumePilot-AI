import pdfplumber
import re

# ----------------------------------------
# Clean extracted text
# ----------------------------------------

def clean_text(text):
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


# ----------------------------------------
# Extract Resume Text
# ----------------------------------------

def extract_resume(pdf_file):

    pages = []

    with pdfplumber.open(pdf_file) as pdf:

        for page in pdf.pages:

            text = page.extract_text(layout=True)

            # Fallback if extract_text fails
            if not text or len(text.strip()) < 20:
                words = page.extract_words(
                    x_tolerance=2,
                    y_tolerance=2
                )

                text = " ".join(w["text"] for w in words)

            if text:
                pages.append(text)

    return clean_text("\n\n".join(pages))