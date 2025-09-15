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

if __name__ == "__main__":
    main()