# utils.py
# Helper functions for text extraction and AI-assisted vendor risk assessment (AI-only)

import pdfplumber
from docx import Document
import pandas as pd
from openai import OpenAI

# Initialize OpenAI client (expects OPENAI_API_KEY env var to be set)
client = OpenAI()

# --------------------------------------------------
# MAIN RISK ASSESSMENT FUNCTION (AI-ONLY)
# --------------------------------------------------

def assess_risk(text):
    """
    Performs vendor risk assessment using AI-driven qualitative explanation aligned to standards.
    Returns:
    - ai_explanation (str)
    """

    ai_prompt = f"""
You are a cybersecurity risk assessor specializing in third-party vendor reviews.

The following text is from a vendor questionnaire or policy document:

{text}

Your task:
1. Identify security or compliance control gaps or weaknesses.
2. Map each finding to common industry frameworks where applicable:
   - NIST SP 800-53 / 800-92
   - ISO/IEC 27001
   - SOC 2 Trust Services Criteria
3. Evaluate whether described practices meet industry norms.
   - If timelines, frequencies, or controls are weak or vague, explain why.
4. Assign a risk rating (Low / Medium / High).
5. Provide **clear, actionable remediation recommendations** appropriate for a third-party vendor.

IMPORTANT:
- Be practical and realistic (do not assume unlimited resources).
- Avoid generic advice like “improve security.”
- If no significant risk is identified, clearly state that.

Respond using this exact structure for EACH finding:

Control Area:
<name>

Framework Mapping:
- NIST: <control IDs if applicable>
- ISO/IEC 27001: <control IDs if applicable>
- SOC 2: <criteria if applicable>

Finding:
<what is missing or weak>

Risk Explanation:
<why this matters and potential impact>

Risk Rating:
Low / Medium / High

Recommended Remediation:
<specific actions the vendor should take>

If multiple findings exist, separate them clearly.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": ai_prompt}],
        temperature=0.2,
    )

    ai_explanation = response.choices[0].message.content
    return ai_explanation


# --------------------------------------------------
# TEXT EXTRACTION FUNCTIONS
# --------------------------------------------------

def extract_pdf_text(file):
    """Extracts text from PDF files"""
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_docx_text(file):
    """Extracts text from Word (.docx) files"""
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_excel_text(file):
    """
    Extracts text from all sheets in an Excel file
    Returns a single concatenated string
    """
    xls = pd.ExcelFile(file)
    all_text = ""
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name)
        all_text += (
            df.fillna("").astype(str).agg(" ".join, axis=1).str.cat(sep="\n")
        )
        all_text += "\n"
    return all_text
