import streamlit as st
import google.generativeai as genai
import pypdf
import os

# Set browser tab title and layout
st.set_page_config(page_title="AI Resume & ATS Matcher", page_icon="📄", layout="wide")

st.title("📄 AI Resume & ATS Job Matcher")
st.write("Upload your resume and paste a job description to get instant ATS match analysis!")

# Fetch API key securely from Streamlit secrets
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ API Key missing! Please set GEMINI_API_KEY in Streamlit Cloud Secrets.")
    st.stop()

genai.configure(api_key=api_key)


# Function to extract text from uploaded PDF
def extract_pdf_text(uploaded_file):
    reader = pypdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    return text


# Layout UI into two columns
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Your Resume (PDF format)", type=["pdf"])

with col2:
    job_description = st.text_area("Paste the Job Description", height=200)

# Trigger Analysis
if st.button("🚀 Analyze ATS Match", type="primary"):
    if not uploaded_file:
        st.warning("Please upload a PDF resume first!")
    elif not job_description.strip():
        st.warning("Please paste a job description!")
    else:
        with st.spinner("Analyzing resume against job requirements..."):
            try:
                resume_text = extract_pdf_text(uploaded_file)

                prompt = f"""
                You are an expert Applicant Tracking System (ATS) recruiter.

                Evaluate the following Resume against the provided Job Description.

                Resume:
                {resume_text}

                Job Description:
                {job_description}

                Provide a structured report using clear Markdown:
                1. **Overall Match Percentage**: (Give an estimated score out of 100%)
                2. **Matching Key Skills**: (List matching technical and soft skills)
                3. **Missing Critical Keywords**: (List important skills required by the job but missing in the resume)
                4. **Actionable Suggestions**: (Provide 3 specific bullet points to tailor the resume)
                """

                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)

                st.success("Analysis Complete!")
                st.markdown("---")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")