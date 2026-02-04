import openai
from fpdf import FPDF
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Set default values for company and position
company = "Celestica Inc"
position = "Data Analytics Intern"

today = datetime.now()

# Format the date without leading zeros for the day
day = today.day
month_year = today.strftime("%B %Y")

# Determine the correct suffix
if 4 <= day <= 20 or 24 <= day <= 30:
    suffix = "th"
else:
    suffix = ["st", "nd", "rd"][day % 10 - 1]

formatted_date = f"{month_year.split()[0]} {day}{suffix}, {month_year.split()[1]}"

# Configure OpenAI API key (Ensure it's set in your environment variables or replace here)
openai.api_key = "YOUR_API_KEY_HERE"

# Function to read text files
def read_file(file_name):
    with open(file_name, 'r') as file:
        return file.read()

# Function to call OpenAI and generate cover letter body
def generate_cover_letter_body(company, position, position_requirements, company_facts, resume, cover_letter_example):
    prompt = f"""
    Write the main body of a personalized cover letter for a candidate applying to {company} for the {position} position. 
    The candidate has the following qualifications:
    {resume}
    The job requirements are:
    {position_requirements}
    The company values and facts are:
    {company_facts}
    
    The candidate's goal is to convey enthusiasm, professionalism, and demonstrate a strong alignment between their skills and the company's needs, focusing only on the body of the letter. Do not include placeholders or any other fill-in-the-blank sections, only generate the content directly relevant to the cover letter body.
    
    Use this cover letter example as a structure for reference (but do not repeat it exactly):
    {cover_letter_example}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.7
    )
    
    return response['choices'][0]['message']['content'].strip()

class PDFGenerator(FPDF):
    def header(self):
        # Center the header image and adjust its width
        try:
            self.image('header.png', x=16, y=20, w=160)
            self.ln(20)
        except FileNotFoundError:
            messagebox.showwarning("File Not Found", "Header image not found!")

def create_cover_letter(company, position, position_requirements, company_facts, resume, cover_letter_example, edited_body):
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
    pdf.cell(0, line_height, company, ln=True)
    pdf.cell(0, line_height, position, ln=True)
    pdf.ln(line_height)

    for paragraph in edited_body.split("\n\n"):
        pdf.multi_cell(0, line_height, paragraph, align="L")
        pdf.ln(line_height / 2)

    pdf.output(f"Cover_letter_{company}.pdf")
    messagebox.showinfo("Success", "PDF generated successfully!")

def on_generate_pdf_button_click():
    edited_body = text_area.get("1.0", tk.END).strip()
    if not edited_body:
        messagebox.showwarning("Input Error", "Please edit or enter content before generating the PDF.")
        return

    position_requirements = read_file("position.txt")
    company_facts = read_file("facts.txt")
    resume = read_file("resume.txt")
    cover_letter_example = read_file("cover_letter_example.txt")

    create_cover_letter(company, position, position_requirements, company_facts, resume, cover_letter_example, edited_body)

def on_generate_button_click():
    position_requirements = read_file("position.txt")
    company_facts = read_file("facts.txt")
    resume = read_file("resume.txt")
    cover_letter_example = read_file("cover_letter_example.txt")

    letter_body = generate_cover_letter_body(company, position, position_requirements, company_facts, resume, cover_letter_example)

    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, letter_body)

root = tk.Tk()
root.title("Cover Letter Editor")
root.geometry("600x600")

generate_button = tk.Button(root, text="Generate Cover Letter", command=on_generate_button_click)
generate_button.pack(pady=10)

text_area = tk.Text(root, wrap=tk.WORD, height=20, width=70)
text_area.pack(pady=10)

generate_pdf_button = tk.Button(root, text="Generate PDF", command=on_generate_pdf_button_click)
generate_pdf_button.pack(pady=10)

root.mainloop()
