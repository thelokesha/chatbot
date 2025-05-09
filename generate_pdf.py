import os
from weasyprint import HTML
from datetime import datetime

def generate_deployment_pdf():
    """Generate a PDF from the deployment_guide.html file"""
    print("Generating deployment PDF...")
    
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Paths for HTML source and PDF output
    html_path = os.path.join(current_dir, 'deployment_guide.html')
    pdf_path = os.path.join(current_dir, 'MindfulAI_Deployment_Guide.pdf')
    
    # Generate the PDF
    HTML(html_path).write_pdf(pdf_path)
    
    print(f"PDF generated successfully at: {pdf_path}")
    
if __name__ == "__main__":
    generate_deployment_pdf()