# app.py
# Run with: streamlit run app.py

import streamlit as st
from utils import (
    extract_pdf_text,
    extract_docx_text,
    extract_excel_text,
    assess_risk,
)

st.set_page_config(page_title="AI Vendor Risk Assessment", layout="wide")

st.title("AI Vendor Risk Assessment Assistant")
st.write(
    "Upload a vendor document (PDF, Word, Excel, or TXT) to receive a "
    "keyword-based risk assessment with AI-powered analysis aligned to "
    "industry standards."
)

# --- File Upload ---
uploaded_file = st.file_uploader(
    "Upload Vendor Document",
    type=["pdf", "docx", "txt", "xlsx"]
)

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("Analyze Vendor Risk"):

        # --- Text Extraction ---
        if uploaded_file.name.endswith(".pdf"):
            vendor_text = extract_pdf_text(uploaded_file)

        elif uploaded_file.name.endswith(".docx"):
            vendor_text = extract_docx_text(uploaded_file)

        elif uploaded_file.name.endswith(".xlsx"):
            vendor_text = extract_excel_text(uploaded_file)

        else:  # .txt
            vendor_text = uploaded_file.read().decode("utf-8")

        if not vendor_text.strip():
            st.error("No readable text found in the document.")
        else:
            # --- Risk Assessment (KEYWORDS + AI) ---
            (
                risk_score,
                risk_level,
                issues,
                ai_explanation
            ) = assess_risk(vendor_text)

            # --- Keyword-Based Results ---
            st.subheader("🔍 Keyword-Based Risk Assessment")
            st.write(f"**Risk Score:** {risk_score}")
            st.write(f"**Risk Level:** {risk_level}")

            if issues:
                st.write("**Detected Issues:**")
                for issue in issues:
                    st.write(f"- {issue}")
            else:
                st.write("No keyword-based issues detected.")

            # --- AI Explanation ---
            st.subheader("🧠 AI Risk Analysis & Standards-Based Assessment")
            st.write(ai_explanation)
