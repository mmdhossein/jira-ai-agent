# backend/app/services/pdf_generator.py
from weasyprint import HTML
from typing import List
from app.models.report import Report
from app.models.image import Image
import base64


class PDFGenerator:
    """Service for generating PDF reports."""
    
    async def generate_report_pdf(self, report: Report, images: List[Image]) -> bytes:
        """
        Generate PDF from report and associated images.
        
        Args:
            report: Report model instance
            images: List of Image model instances
            
        Returns:
            PDF file as bytes
        """
        # Build images HTML
        images_html = ""
        
        for img in images:
            # Encode image data to base64
            encoded = base64.b64encode(img.image_data).decode("utf-8")
            images_html += f"""
                <div class="chart">
                    <img src="data:image/{img.image_type};base64,{encoded}" alt="Chart" />
                </div>
            """
        
        # Build structured data HTML if available
        structured_data_html = ""
        if report.structured_data:
            structured_data_html = "<h2>Detailed Data</h2><div class='data'>"
            
            # Handle different data structures
            if isinstance(report.structured_data, dict):
                for key, value in report.structured_data.items():
                    structured_data_html += f"<h3>{key.replace('_', ' ').title()}</h3>"
                    
                    if isinstance(value, list):
                        structured_data_html += "<ul>"
                        for item in value:
                            if isinstance(item, dict):
                                structured_data_html += "<li>"
                                for k, v in item.items():
                                    structured_data_html += f"<strong>{k}:</strong> {v} &nbsp;&nbsp;"
                                structured_data_html += "</li>"
                            else:
                                structured_data_html += f"<li>{item}</li>"
                        structured_data_html += "</ul>"
                    else:
                        structured_data_html += f"<p>{value}</p>"
            
            structured_data_html += "</div>"
        
        # Build complete HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    color: #333;
                    line-height: 1.6;
                }}
                
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                    margin-bottom: 30px;
                }}
                
                h2 {{
                    color: #34495e;
                    margin-top: 30px;
                    margin-bottom: 15px;
                }}
                
                h3 {{
                    color: #7f8c8d;
                    margin-top: 20px;
                    margin-bottom: 10px;
                }}
                
                .metadata {{
                    background-color: #ecf0f1;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 30px;
                }}
                
                .metadata p {{
                    margin: 5px 0;
                    font-size: 14px;
                }}
                
                .summary {{
                    background-color: #fff;
                    padding: 20px;
                    border-left: 4px solid #3498db;
                    margin-bottom: 30px;
                    white-space: pre-line;
                }}
                
                .chart {{
                    margin: 30px 0;
                    text-align: center;
                    page-break-inside: avoid;
                }}
                
                .chart img {{
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                    background-color: white;
                }}
                
                .data {{
                    margin-top: 20px;
                }}
                
                .data ul {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                
                .data li {{
                    background-color: #f8f9fa;
                    padding: 10px;
                    margin-bottom: 5px;
                    border-radius: 3px;
                }}
                
                .data strong {{
                    color: #2c3e50;
                }}
                
                .footer {{
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    text-align: center;
                    font-size: 12px;
                    color: #7f8c8d;
                }}
                
                .page-break {{
                    page-break-after: always;
                }}
            </style>
        </head>
        <body>
            <h1>AI Project Management Report</h1>
            
            <div class="metadata">
                <p><strong>Report Type:</strong> {report.report_type.replace('_', ' ').title()}</p>
                <p><strong>Generated:</strong> {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Report ID:</strong> {report.id}</p>
            </div>
            
            <h2>Summary</h2>
            <div class="summary">
                {report.summary or "No summary available."}
            </div>
            
            {images_html}
            
            {structured_data_html}
            
            <div class="footer">
                <p>Generated by AI Project Management Agent</p>
                <p>This report contains confidential information</p>
            </div>
        </body>
        </html>
        """
        
        # Generate PDF from HTML
        try:
            pdf = HTML(string=html_content).write_pdf()
            return pdf
        except Exception as e:
            # Fallback to simple PDF if WeasyPrint fails
            print("Exception in generating PDF, falling back to simple")
            return self._generate_simple_pdf(report, images)
    
    def _generate_simple_pdf(self, report: Report, images: List[Image]) -> bytes:
        """
        Fallback method to generate a simple PDF without complex styling.
        
        Args:
            report: Report model instance
            images: List of Image model instances
            
        Returns:
            PDF file as bytes
        """
        images_html = ""
        for img in images:
            encoded = base64.b64encode(img.image_data).decode("utf-8")
            images_html += f'<img src="data:image/{img.image_type};base64,{encoded}" style="max-width:100%;"/><br/>'
        
        simple_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                h1 {{ color: #333; }}
                pre {{ white-space: pre-wrap; }}
            </style>
        </head>
        <body>
            <h1>Report #{report.id}</h1>
            <p><strong>Type:</strong> {report.report_type}</p>
            <p><strong>Date:</strong> {report.created_at}</p>
            <hr/>
            <h2>Summary</h2>
            <pre>{report.summary or "No summary"}</pre>
            <hr/>
            <h2>Charts</h2>
            {images_html}
        </body>
        </html>
        """
        
        pdf = HTML(string=simple_html).write_pdf()
        return pdf
    
    async def generate_custom_pdf(self, title: str, content: str, images_data: List[bytes] = None) -> bytes:
        """
        Generate a custom PDF with provided content.
        
        Args:
            title: PDF title
            content: Main content (HTML or plain text)
            images_data: Optional list of image bytes
            
        Returns:
            PDF file as bytes
        """
        images_html = ""
        if images_data:
            for img_bytes in images_data:
                encoded = base64.b64encode(img_bytes).decode("utf-8")
                images_html += f'<div style="text-align:center;margin:20px 0;"><img src="data:image/png;base64,{encoded}" style="max-width:100%;"/></div>'
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; padding: 30px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .content {{ margin: 20px 0; white-space: pre-line; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div class="content">{content}</div>
            {images_html}
        </body>
        </html>
        """
        
        pdf = HTML(string=html_content).write_pdf()
        return pdf
