import streamlit as st
from openai import OpenAI
from fpdf import FPDF
from datetime import datetime
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Cover Letter Generator",
    layout="wide"
)

# Custom CSS for modern minimal styling
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 600;
        color: #111;
        margin-bottom: 0.5rem;
    }
    .stTextArea textarea {
        font-size: 14px;
        border-radius: 8px;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">Cover Letter Generator</p>', unsafe_allow_html=True)

# Get formatted date
def get_formatted_date():
    today = datetime.now()
    day = today.day
    month_year = today.strftime("%B %Y")
    
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    
    return f"{month_year.split()[0]} {day}{suffix}, {month_year.split()[1]}"

# Initialize session state
if 'generated_letter' not in st.session_state:
    st.session_state.generated_letter = ""

# Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.divider()
    
    st.header("Job Details")
    company = st.text_input("Company Name", placeholder="e.g., Google Inc.")
    position = st.text_input("Position", placeholder="e.g., Software Engineer")

# Main content area with tabs
tab1, tab2, tab3 = st.tabs(["Input", "Generate", "Preview & Download"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Resume")
        resume = st.text_area(
            "Paste your resume here",
            height=300,
            placeholder="Paste your full resume content here...",
            key="resume_input"
        )
        
        st.subheader("Job Requirements")
        position_requirements = st.text_area(
            "Paste the job requirements/description",
            height=200,
            placeholder="Paste the job posting requirements here...",
            key="requirements_input"
        )
    
    with col2:
        st.subheader("Company Facts")
        company_facts = st.text_area(
            "Facts about the company",
            height=200,
            placeholder="Enter relevant facts about the company (values, mission, recent news, etc.)...",
            key="facts_input"
        )
        
        st.subheader("Example Cover Letter")
        cover_letter_example = st.text_area(
            "Paste an example cover letter for style reference",
            height=300,
            placeholder="Paste an example cover letter that you like the style of...",
            key="example_input"
        )

with tab2:
    st.subheader("Generate Your Cover Letter")
    
    # Validation
    can_generate = all([api_key, company, position, resume, position_requirements])
    
    if not can_generate:
        st.warning("Please fill in all required fields:")
        missing = []
        if not api_key:
            missing.append("- OpenAI API Key (in sidebar)")
        if not company:
            missing.append("- Company Name (in sidebar)")
        if not position:
            missing.append("- Position (in sidebar)")
        if not resume:
            missing.append("- Resume")
        if not position_requirements:
            missing.append("- Job Requirements")
        st.markdown("\n".join(missing))
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button(
            "Generate Cover Letter",
            type="primary",
            use_container_width=True,
            disabled=not can_generate
        )
    
    if generate_button:
        with st.spinner("Generating your personalized cover letter..."):
            try:
                client = OpenAI(api_key=api_key)
                
                prompt = f"""
                Write the main body of a personalized cover letter for a candidate applying to {company} for the {position} position. 
                The candidate has the following qualifications:
                {resume}
                The job requirements are:
                {position_requirements}
                The company values and facts are:
                {company_facts if company_facts else "Not provided"}
                
                The candidate's goal is to convey enthusiasm, professionalism, and demonstrate a strong alignment between their skills and the company's needs, focusing only on the body of the letter. Do not include placeholders or any other fill-in-the-blank sections, only generate the content directly relevant to the cover letter body.
                
                {"Use this cover letter example as a structure for reference (but do not repeat it exactly): " + cover_letter_example if cover_letter_example else ""}
                """
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that writes professional cover letters."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.7
                )
                
                st.session_state.generated_letter = response.choices[0].message.content.strip()
                st.success("Cover letter generated successfully! Go to 'Preview & Download' tab to view and download.")
                
            except Exception as e:
                st.error(f"Error generating cover letter: {str(e)}")
    
    # Editable text area for the generated letter
    if st.session_state.generated_letter:
        st.divider()
        st.subheader("Edit Your Cover Letter")
        edited_letter = st.text_area(
            "Make any edits you need:",
            value=st.session_state.generated_letter,
            height=400,
            key="edited_letter"
        )
        st.session_state.generated_letter = edited_letter

with tab3:
    st.subheader("Preview & Download")
    
    if st.session_state.generated_letter:
        # Preview section
        formatted_date = get_formatted_date()
        
        st.markdown("### Preview")
        preview_container = st.container()
        with preview_container:
            st.markdown(f"**{formatted_date}**")
            st.markdown("")
            st.markdown("**Hiring Manager**")
            st.markdown(f"**{company}**")
            st.markdown(f"**{position}**")
            st.markdown("")
            st.markdown(st.session_state.generated_letter)
        
        st.divider()
        
        # PDF Generation
        st.markdown("### Download Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate PDF", type="primary", use_container_width=True):
                try:
                    # Create PDF
                    class PDFGenerator(FPDF):
                        pass
                    
                    pdf = PDFGenerator()
                    pdf.set_auto_page_break(auto=True, margin=20)
                    pdf.set_left_margin(20)
                    pdf.set_right_margin(20)
                    pdf.set_top_margin(20)
                    pdf.add_page()
                    pdf.set_font("Times", "", 12)
                    
                    line_height = pdf.font_size * 1.5
                    
                    pdf.cell(0, line_height, formatted_date, ln=True)
                    pdf.ln(line_height)
                    pdf.cell(0, line_height, "Hiring Manager", ln=True)
                    pdf.cell(0, line_height, company if company else "", ln=True)
                    pdf.cell(0, line_height, position if position else "", ln=True)
                    pdf.ln(line_height)
                    
                    for paragraph in st.session_state.generated_letter.split("\n\n"):
                        pdf.multi_cell(0, line_height, paragraph, align="L")
                        pdf.ln(line_height / 2)
                    
                    # Save to bytes
                    pdf_output = pdf.output(dest='S').encode('latin-1')
                    
                    # Create download button
                    st.download_button(
                        label="Download PDF",
                        data=pdf_output,
                        file_name=f"Cover_Letter_{company.replace(' ', '_') if company else 'Company'}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("PDF generated! Click the download button above.")
                    
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
        
        with col2:
            # Text download option
            st.download_button(
                label="Download as Text",
                data=f"{formatted_date}\n\nHiring Manager\n{company}\n{position}\n\n{st.session_state.generated_letter}",
                file_name=f"Cover_Letter_{company.replace(' ', '_') if company else 'Company'}.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.info("Generate a cover letter first in the 'Generate' tab to preview and download it here.")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.85rem;">
    <p>Run with <code>streamlit run app.py</code></p>
</div>
""", unsafe_allow_html=True)
