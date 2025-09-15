import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Final Delivery Check Sheet",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .section-header {
        font-size: 20px;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 25px;
        margin-bottom: 15px;
        border-bottom: 2px solid #3498db;
        padding-bottom: 5px;
    }
    .signature-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-top: 30px;
    }
    .acceptance-text {
        font-style: italic;
        color: #555;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Title
    st.markdown('<h1 class="main-header">Final Delivery Check Sheet</h1>', unsafe_allow_html=True)
    
    # Sidebar for actions
    with st.sidebar:
        st.header("Actions")
        
        # Load pre-filled data
        if st.button("Load Sample Data"):
            load_sample_data()
            st.rerun()
        
        # Save current data
        if st.button("Save as JSON"):
            save_data()
        
        # Load data from JSON
        uploaded_file = st.file_uploader("Load Saved Data", type=['json'])
        if uploaded_file is not None:
            load_data(uploaded_file)
            st.rerun()
        
        st.markdown("---")
        st.info("💡 Use the sidebar to save/load form data")
    
    # Initialize session state
    initialize_session_state()
    
    # Header Information Section
    st.markdown('<div class="section-header">Vehicle & Customer Information</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.customer_name = st.text_input(
            "Customer Name:", 
            value=st.session_state.get('customer_name', '')
        )
        st.session_state.odometer_reading = st.text_input(
            "Odometer Reading:", 
            value=st.session_state.get('odometer_reading', '')
        )
    
    with col2:
        st.session_state.registration = st.text_input(
            "Registration:", 
            value=st.session_state.get('registration', '')
        )
        st.session_state.sale_id = st.text_input(
            "Sale ID:", 
            value=st.session_state.get('sale_id', '')
        )
    
    # Important Checks Section
    st.markdown('<div class="section-header">Important Checks</div>', unsafe_allow_html=True)
    
    important_checks = [
        "Customer Requests Completed",
        "Quality Control Check Passed", 
        "Service Completed (if applicable)",
        "Roadworthy Check Completed"
    ]
    
    for check in important_checks:
        create_check_item(check, "important")
    
    # Documentation Section
    st.markdown('<div class="section-header">Documentation</div>', unsafe_allow_html=True)
    
    documentation_items = [
        "Registration Papers",
        "Roadworthy Certificate",
        "Contract Signed / Invoice Received",
        "User Manual (if applicable)",
        "Service History (if available)",
        "Diagnostic Report (if applicable)",
        "Battery Test Report"
    ]
    
    for doc in documentation_items:
        create_check_item(doc, "documentation")
    
    # Final Inspection Section
    st.markdown('<div class="section-header">Final Inspection</div>', unsafe_allow_html=True)
    
    inspection_items = [
        "Paintwork & Panels",
        "Windscreen & Windows",
        "Tyres & Wheels",
        "Lights & Indicators",
        "Interior Trim",
        "Boot area",
        "Infotainment/Dashboard Warning Lights",
        "Keys (Count & Battery Status)",
        "Seat/Boot Mats (if applicable)"
    ]
    
    for item in inspection_items:
        create_check_item(item, "inspection")
    
    # Signature Section
    st.markdown('<div class="section-header">Customer Acceptance</div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="signature-section">
        <div class="acceptance-text">
            <strong>I have reviewed this document and accept the vehicle in its described condition. 
            I also understand that should the vehicle be returned, it must be returned in the same 
            condition it was accepted in.</strong>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.time_date = st.text_input(
            "Time & Date:", 
            value=st.session_state.get('time_date', datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        st.session_state.customer_signature = st.text_input(
            "Customer Signature:", 
            value=st.session_state.get('customer_signature', '')
        )
    
    with col2:
        st.session_state.specialist_signature = st.text_input(
            "Cars24 Specialist Signature:", 
            value=st.session_state.get('specialist_signature', '')
        )
    
    # Summary Section
    if st.button("Generate Summary Report", type="primary"):
        generate_summary()

def create_check_item(item_name, category):
    """Create a checkbox item with comments field"""
    col1, col2 = st.columns([1, 2])
    
    # Clean item name for session state key
    key_name = f"{category}_{item_name.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').lower()}"
    
    with col1:
        checked = st.checkbox(
            f"✓ {item_name}", 
            key=f"check_{key_name}",
            value=st.session_state.get(f"check_{key_name}", False)
        )
    
    with col2:
        comment = st.text_area(
            "Comments:", 
            key=f"comment_{key_name}",
            value=st.session_state.get(f"comment_{key_name}", ''),
            height=60,
            label_visibility="collapsed",
            placeholder="Add comments here..."
        )

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'customer_name': '',
        'registration': '',
        'odometer_reading': '',
        'sale_id': '',
        'time_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'customer_signature': '',
        'specialist_signature': ''
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def load_sample_data():
    """Load sample data for demonstration"""
    st.session_state.customer_name = "John Smith"
    st.session_state.registration = "ABC123"
    st.session_state.odometer_reading = "45,000 km"
    st.session_state.sale_id = "CARS24-2024-001"
    st.session_state.customer_signature = "J. Smith"
    st.session_state.specialist_signature = "M. Johnson"
    
    # Sample some checks
    st.session_state.check_important_customer_requests_completed = True
    st.session_state.check_important_quality_control_check_passed = True
    st.session_state.check_documentation_registration_papers = True
    st.session_state.check_inspection_paintwork__panels = True
    
    st.success("Sample data loaded!")

def save_data():
    """Save current form data as JSON"""
    data = {}
    for key, value in st.session_state.items():
        if isinstance(value, (str, int, float, bool)):
            data[key] = value
    
    json_string = json.dumps(data, indent=2)
    st.download_button(
        label="Download Data",
        data=json_string,
        file_name=f"delivery_check_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json"
    )

def load_data(uploaded_file):
    """Load data from uploaded JSON file"""
    try:
        data = json.load(uploaded_file)
        for key, value in data.items():
            st.session_state[key] = value
        st.success("Data loaded successfully!")
    except Exception as e:
        st.error(f"Error loading data: {e}")

def generate_summary():
    """Generate a summary report"""
    st.markdown("---")
    st.markdown("## 📋 Summary Report")
    
    # Vehicle info summary
    st.markdown("### Vehicle Information")
    st.write(f"**Customer:** {st.session_state.get('customer_name', 'N/A')}")
    st.write(f"**Registration:** {st.session_state.get('registration', 'N/A')}")
    st.write(f"**Odometer:** {st.session_state.get('odometer_reading', 'N/A')}")
    st.write(f"**Sale ID:** {st.session_state.get('sale_id', 'N/A')}")
    
    # Count completed items
    all_checks = [key for key in st.session_state.keys() if key.startswith('check_')]
    completed_checks = [key for key in all_checks if st.session_state.get(key, False)]
    
    st.markdown("### Completion Status")
    st.write(f"**Items Checked:** {len(completed_checks)}/{len(all_checks)}")
    st.progress(len(completed_checks) / len(all_checks) if all_checks else 0)
    
    # Show any comments
    comments = {key: value for key, value in st.session_state.items() 
               if key.startswith('comment_') and value.strip()}
    
    if comments:
        st.markdown("### Comments Summary")
        for key, comment in comments.items():
            item_name = key.replace('comment_', '').replace('_', ' ').title()
            st.write(f"**{item_name}:** {comment}")
    
    # PDF Download Button
    st.markdown("### 📄 Download PDF Report")
    if st.button("Generate & Download PDF", type="primary"):
        pdf_buffer = create_pdf_report()
        
        current_time = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"delivery_check_report_{current_time}.pdf"
        
        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name=filename,
            mime="application/pdf",
            type="primary"
        )

def create_pdf_report():
    """Create a comprehensive PDF report of the delivery check"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], 
                                    fontSize=18, spaceAfter=30, alignment=1, textColor=colors.darkblue)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], 
                                     fontSize=14, spaceAfter=12, textColor=colors.darkblue)
        normal_style = styles['Normal']
        
        # Title
        title = Paragraph("FINAL DELIVERY CHECK SHEET", title_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Vehicle Information Section
        vehicle_info_data = [
            ['Customer Name:', st.session_state.get('customer_name', 'N/A'), 
             'Registration:', st.session_state.get('registration', 'N/A')],
            ['Odometer Reading:', st.session_state.get('odometer_reading', 'N/A'), 
             'Sale ID:', st.session_state.get('sale_id', 'N/A')]
        ]
        
        vehicle_table = Table(vehicle_info_data, colWidths=[2*inch, 2*inch, 1.5*inch, 1.5*inch])
        vehicle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(vehicle_table)
        elements.append(Spacer(1, 20))
        
        # Helper function to create check sections
        def create_check_section(section_name, items, category_prefix):
            elements.append(Paragraph(section_name, heading_style))
            
            section_data = [['Item', 'Status', 'Comments']]
            
            for item in items:
                # Clean the item name for the key
                clean_item = item.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '').replace('-', '_').lower()
                key_name = f"{category_prefix}_{clean_item}"
                check_key = f"check_{key_name}"
                comment_key = f"comment_{key_name}"
                
                status = "✓ COMPLETED" if st.session_state.get(check_key, False) else "○ PENDING"
                comment = st.session_state.get(comment_key, '') or '-'
                
                # Truncate long comments for PDF
                if len(comment) > 50:
                    comment = comment[:47] + "..."
                
                section_data.append([item, status, comment])
            
            section_table = Table(section_data, colWidths=[3*inch, 1.5*inch, 2.5*inch])
            section_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            elements.append(section_table)
            elements.append(Spacer(1, 15))
        
        # Important Checks
        important_checks = [
            "Customer Requests Completed",
            "Quality Control Check Passed", 
            "Service Completed (if applicable)",
            "Roadworthy Check Completed"
        ]
        create_check_section("IMPORTANT CHECKS", important_checks, "important")
        
        # Documentation
        documentation_items = [
            "Registration Papers",
            "Roadworthy Certificate",
            "Contract Signed / Invoice Received",
            "User Manual (if applicable)",
            "Service History (if available)",
            "Diagnostic Report (if applicable)",
            "Battery Test Report"
        ]
        create_check_section("DOCUMENTATION", documentation_items, "documentation")
        
        # Final Inspection
        inspection_items = [
            "Paintwork & Panels",
            "Windscreen & Windows",
            "Tyres & Wheels",
            "Lights & Indicators",
            "Interior Trim",
            "Boot area",
            "Infotainment/Dashboard Warning Lights",
            "Keys (Count & Battery Status)",
            "Seat/Boot Mats (if applicable)"
        ]
        create_check_section("FINAL INSPECTION", inspection_items, "inspection")
        
        # Customer Acceptance
        elements.append(Paragraph("CUSTOMER ACCEPTANCE", heading_style))
        
        acceptance_text = """I have reviewed this document and accept the vehicle in its described condition. 
        I also understand that should the vehicle be returned, it must be returned in the same condition it was accepted in."""
        
        elements.append(Paragraph(acceptance_text, normal_style))
        elements.append(Spacer(1, 15))
        
        # Signatures
        signature_data = [
            ['Time & Date:', st.session_state.get('time_date', 'N/A')],
            ['Customer Signature:', st.session_state.get('customer_signature', 'N/A')],
            ['Cars24 Specialist Signature:', st.session_state.get('specialist_signature', 'N/A')]
        ]
        
        signature_table = Table(signature_data, colWidths=[2.5*inch, 4*inch])
        signature_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(signature_table)
        elements.append(Spacer(1, 20))
        
        # Summary Statistics
        all_checks = [key for key in st.session_state.keys() if key.startswith('check_')]
        completed_checks = [key for key in all_checks if st.session_state.get(key, False)]
        completion_rate = (len(completed_checks) / len(all_checks) * 100) if all_checks else 0
        
        summary_text = f"""
        <b>COMPLETION SUMMARY:</b><br/>
        Total Items: {len(all_checks)}<br/>
        Completed Items: {len(completed_checks)}<br/>
        Completion Rate: {completion_rate:.1f}%<br/>
        Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        
        elements.append(Paragraph(summary_text, normal_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and return it
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
        
    except Exception as e:
        # If PDF generation fails, create a simple error PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        error_content = [
            Paragraph("PDF Generation Error", styles['Title']),
            Spacer(1, 20),
            Paragraph(f"Error: {str(e)}", styles['Normal']),
            Spacer(1, 20),
            Paragraph("Please try again or contact support.", styles['Normal'])
        ]
        
        doc.build(error_content)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data

if __name__ == "__main__":
    main()