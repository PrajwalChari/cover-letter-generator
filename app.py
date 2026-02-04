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
    .version-header {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .version-header-default {
        background-color: #f0f2f6;
        color: #333;
    }
    .version-header-selected {
        background-color: #1e88e5;
        color: white;
    }
    .selected-container {
        border: 3px solid #1e88e5;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #e3f2fd;
    }
    .default-container {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #fafafa;
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

# Initialize session state for multiple versions
if 'cover_letters' not in st.session_state:
    st.session_state.cover_letters = []  # List of dicts: {id, content, timestamp}
if 'next_id' not in st.session_state:
    st.session_state.next_id = 1
if 'selected_letter_id' not in st.session_state:
    st.session_state.selected_letter_id = None

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
                
                new_letter = response.choices[0].message.content.strip()
                
                # Add new version to the beginning of the list
                new_version = {
                    'id': st.session_state.next_id,
                    'content': new_letter,
                    'timestamp': datetime.now().strftime("%I:%M %p")
                }
                st.session_state.cover_letters.insert(0, new_version)
                st.session_state.selected_letter_id = new_version['id']
                st.session_state.next_id += 1
                
                st.success("Cover letter generated! New version added at the top.")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating cover letter: {str(e)}")
    
    # Display all versions with editable text areas
    if st.session_state.cover_letters:
        st.divider()
        st.subheader("Generated Cover Letters")
        st.caption("Newest versions appear at the top. All versions are editable.")
        
        for i, letter in enumerate(st.session_state.cover_letters):
            # Check if this version is selected
            is_selected = st.session_state.selected_letter_id == letter['id']
            
            # Container styling based on selection
            container_class = "selected-container" if is_selected else "default-container"
            header_class = "version-header version-header-selected" if is_selected else "version-header version-header-default"
            
            st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([6, 1])
            with col1:
                status_text = " - SELECTED" if is_selected else ""
                st.markdown(f'<div class="{header_class}">Version {letter["id"]} - {letter["timestamp"]}{status_text}</div>', unsafe_allow_html=True)
            with col2:
                button_label = "Selected" if is_selected else "Select"
                if st.button(button_label, key=f"select_{letter['id']}", use_container_width=True, disabled=is_selected):
                    st.session_state.selected_letter_id = letter['id']
                    st.rerun()
            
            edited_content = st.text_area(
                f"Edit Version {letter['id']}" + (" (Selected for Download)" if is_selected else ""),
                value=letter['content'],
                height=300,
                key=f"letter_{letter['id']}"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Update the stored content if edited
            st.session_state.cover_letters[i]['content'] = edited_content
            
            if i < len(st.session_state.cover_letters) - 1:
                st.divider()

with tab3:
    st.subheader("Preview & Download")
    
    # Get the selected letter
    selected_letter = None
    if st.session_state.selected_letter_id and st.session_state.cover_letters:
        for letter in st.session_state.cover_letters:
            if letter['id'] == st.session_state.selected_letter_id:
                selected_letter = letter
                break
    
    # If no selection but letters exist, use the first one
    if not selected_letter and st.session_state.cover_letters:
        selected_letter = st.session_state.cover_letters[0]
        st.session_state.selected_letter_id = selected_letter['id']
    
    if selected_letter:
        # Show current selection prominently
        st.success(f"Currently viewing: Version {selected_letter['id']} (Generated at {selected_letter['timestamp']})")
        
        # Version selector
        if len(st.session_state.cover_letters) > 1:
            version_options = [f"Version {l['id']} ({l['timestamp']})" for l in st.session_state.cover_letters]
            selected_idx = next((i for i, l in enumerate(st.session_state.cover_letters) if l['id'] == st.session_state.selected_letter_id), 0)
            
            selected_version = st.selectbox(
                "Select version to preview/download:",
                options=version_options,
                index=selected_idx
            )
            
            # Update selected letter based on dropdown
            new_idx = version_options.index(selected_version)
            selected_letter = st.session_state.cover_letters[new_idx]
            st.session_state.selected_letter_id = selected_letter['id']
        
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
            st.markdown(selected_letter['content'])
        
        st.divider()
        
        # PDF Generation
        st.markdown("### Download Options")
        
        # Filename format selector
        filename_format = st.radio(
            "Filename format:",
            options=["Company Name", "Position Name", "Both (Company_Position)"],
            horizontal=True
        )
        
        # Generate filename based on selection
        def get_filename(extension):
            company_clean = company.replace(' ', '_') if company else 'Company'
            position_clean = position.replace(' ', '_') if position else 'Position'
            
            if filename_format == "Company Name":
                base = f"Cover_Letter_{company_clean}"
            elif filename_format == "Position Name":
                base = f"Cover_Letter_{position_clean}"
            else:  # Both
                base = f"Cover_Letter_{company_clean}_{position_clean}"
            
            return f"{base}_v{selected_letter['id']}.{extension}"
        
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
                    
                    for paragraph in selected_letter['content'].split("\n\n"):
                        pdf.multi_cell(0, line_height, paragraph, align="L")
                        pdf.ln(line_height / 2)
                    
                    # Save to bytes
                    pdf_output = pdf.output(dest='S').encode('latin-1')
                    
                    # Create download button
                    st.download_button(
                        label="Download PDF",
                        data=pdf_output,
                        file_name=get_filename("pdf"),
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
                data=f"{formatted_date}\n\nHiring Manager\n{company}\n{position}\n\n{selected_letter['content']}",
                file_name=get_filename("txt"),
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
