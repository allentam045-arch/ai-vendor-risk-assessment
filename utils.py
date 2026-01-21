# utils.py
# Helper functions for text extraction and AI-assisted vendor risk assessment

import pdfplumber
from docx import Document
import pandas as pd
from openai import OpenAI

# Initialize OpenAI client (expects OPENAI_API_KEY env var to be set)
client = OpenAI()

# --------------------------------------------------
# KEYWORD-BASED RISK DOMAINS (DETECTION LAYER)
# --------------------------------------------------

RISK_DOMAINS = {
    "Identity & Access Management": [
        "no mfa",
        "shared account",
        "weak password",
        "no access review"
    ],
    "Logging & Monitoring": [
        "audit logs reviewed every",
        "logs reviewed every",
        "no log review"
    ],
    "Incident Response": [
        "no incident response",
        "no ir plan",
        "no incident plan"
    ],
    "Data Protection": [
        "no encryption",
        "unencrypted data"
    ],
    "Vulnerability Management": [
        "no vulnerability scan",
        "no patching",
        "no patch management"
    ],
    "Governance & Risk": [
        "no security program",
        "no risk assessment",
        "no policies"
    ],
}

# --------------------------------------------------
# MAIN RISK ASSESSMENT FUNCTION (AI + KEYWORDS)
# --------------------------------------------------

def assess_risk(text):
    """
    Performs vendor risk assessment using:
    1) Keyword-based detection
    2) AI-driven qualitative explanation aligned to standards

    Returns:
    - risk_score (int)
    - risk_level (Low / Medium / High)
    - detected_issues (list)
    - ai_explanation (str)
    """

    text_lower = text.lower()
    detected_issues = []

    # --- Step 1: Keyword detection ---
    for category, keywords in RISK_DOMAINS.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected_issues.append(f"{category}: {keyword}")

    risk_score = len(detected_issues)

    if risk_score <= 2:
        risk_level = "Low"
    elif risk_score <= 5:
        risk_level = "Medium"
    else:
        risk_level = "High"

    # --- Step 2: AI qualitative explanation ---
    ai_prompt = f"""
You are a cybersecurity risk assessor specializing in third-party vendor reviews.

The following text is from a vendor questionnaire or policy document:

{text}

Detected issues (from automated review):
{detected_issues if detected_issues else "No explicit keyword-based issues detected."}

Instructions:
1. Identify the relevant security or compliance control areas (e.g., logging, access control).
2. Evaluate whether the described practices align with common industry expectations such as:
   - NIST SP 800-53 / 800-92
   - ISO/IEC 27001
   - SOC 2
3. If timeframes, frequencies, or practices are weak, outdated, or vague, clearly explain WHY.
   Example: Audit log reviews occurring every 5 years are inconsistent with industry norms.
4. Describe the potential risk or impact of the gaps identified.

Respond using the following structure:

Control Area:
<name>

Framework Mapping:
- NIST: <control IDs if applicable>
- ISO/IEC 27001: <control IDs if applicable>
- SOC 2: <control criteria if applicable>

Assessment:
<brief assessment>

Risk Explanation:
<why this is a risk and impact>

Risk Rating:
Low / Medium / High

"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": ai_prompt}],
        temperature=0.2,
    )

    ai_explanation = response.choices[0].message.content

    return risk_score, risk_level, detected_issues, ai_explanation

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
            df.fillna("")
            .astype(str)
            .agg(" ".join, axis=1)
            .str.cat(sep="\n")
        )
        all_text += "\n"

    return all_text
