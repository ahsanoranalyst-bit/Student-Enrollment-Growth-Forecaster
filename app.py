import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

# --- 1. CONFIGURATION & SESSION INITIALIZATION ---
st.set_page_config(page_title="Student Enrollment & Growth Forecaster", layout="wide")

# Activation Key Logic
ACTIVATION_KEY = "ENROLL-2026-PRO"

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'org_name' not in st.session_state:
    st.session_state.org_name = ""
if 'data_store' not in st.session_state:
    # Initialize dictionary to hold all inputs
    st.session_state.data_store = {
        "Section A": {}, "Section B": {}, "Section C": {}, "Section D": {}
    }

# --- 2. MULTI-LEVEL ENTRY (SECURITY & IDENTITY) ---
if not st.session_state.authenticated:
    st.title("🔐 System Activation")
    with st.container():
        entered_key = st.text_input("Enter Activation Key", type="password")
        if st.button("Verify Key"):
            if entered_key == ACTIVATION_KEY:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Activation Key. Please contact the administrator.")
    st.stop()

if st.session_state.org_name == "":
    st.title("🏢 Organization Identity")
    org_input = st.text_input("Enter Organization Name")
    if st.button("Initialize Workspace"):
        if org_input.strip():
            st.session_state.org_name = org_input
            st.rerun()
        else:
            st.warning("Organization name is required to proceed.")
    st.stop()

# --- 3. HELPER FUNCTIONS ---
def generate_pdf(org, score, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Enrollment & Growth Forecast Report", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Organization: {org}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%B %d, %Y')}", ln=True)
    pdf.cell(200, 10, txt=f"Growth Forecast Score: {score}/200", ln=True)
    
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    for section, values in data.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"--- {section} ---", ln=True)
        pdf.set_font("Arial", size=10)
        for key, val in values.items():
            pdf.cell(200, 8, txt=f"{key}: {val}", ln=True)
        pdf.ln(4)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 4. MAIN UI & TABS ---
st.title(f"📈 {st.session_state.org_name}")
st.subheader("Student Enrollment & Growth Forecaster")

tab1, tab2, tab3, tab4 = st.tabs([
    "Section A: Historical Trends", 
    "Section B: Market Data", 
    "Section C: Capacity", 
    "Section D: External Factors"
])

# Section A
with tab1:
    st.header("Historical Trends")
    st.info("Input historical data to identify Growth Rate.")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.data_store["Section A"]["Total Admissions (5yr)"] = st.number_input("Total Admissions (Last 5 Years)", 0, 10000, 500)
        st.session_state.data_store["Section A"]["Withdrawals"] = st.number_input("Total Withdrawals (TCs)", 0, 1000, 20)
    with col2:
        up_a = st.file_uploader("Upload Enrollment History (CSV/Excel)", type=['csv', 'xlsx'], key="up_a")
        if up_a: st.success("File synchronized successfully.")

# Section B
with tab2:
    st.header("Market & Inquiry Data")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.data_store["Section B"]["New Inquiries"] = st.number_input("Number of New Inquiries", 0, 5000, 150)
        st.session_state.data_store["Section B"]["Primary Source"] = st.selectbox("Inquiry Source", ["Social Media", "Word of Mouth", "Signboards", "Other"])
    with col2:
        st.session_state.data_store["Section B"]["Conversion Rate"] = st.slider("Conversion Rate %", 0, 100, 30)

# Section C
with tab3:
    st.header("Capacity & Retention")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.data_store["Section C"]["Max Capacity"] = st.number_input("Classroom Capacity (Total Seats)", 1, 5000, 1000)
        st.session_state.data_store["Section C"]["Promotion Rate"] = st.slider("Promotion Rate %", 0, 100, 95)
    with col2:
        st.session_state.data_store["Section C"]["Sibling Families"] = st.number_input("Families with Multiple Kids", 0, 1000, 50)

# Section D
with tab4:
    st.header("External Factors")
    st.session_state.data_store["Section D"]["Competitor Schools"] = st.number_input("Nearby Competitor Schools", 0, 20, 2)
    st.session_state.data_store["Section D"]["Economic Status"] = st.select_slider("Area Economic Status", options=["Developing", "Stable", "Affluent"])
    st.session_state.data_store["Section D"]["Local Growth"] = st.selectbox("Population Growth", ["Declining", "Stable", "Rapidly Increasing"])

# --- 5. CALCULATION & PDF OUTPUT ---
st.divider()
if st.button("🔥 Generate Final Forecast Analysis"):
    try:
        # Mathematical Calculation (Score out of 200)
        # Weightage: A:60, B:60, C:50, D:30
        score_a = min(60, (st.session_state.data_store["Section A"]["Total Admissions (5yr)"] / 1000) * 60)
        score_b = (st.session_state.data_store["Section B"]["Conversion Rate"] / 100) * 60
        score_c = (st.session_state.data_store["Section C"]["Promotion Rate"] / 100) * 50
        
        # External factor adjustment
        score_d = 10 if st.session_state.data_store["Section D"]["Local Growth"] == "Rapidly Increasing" else 5
        
        final_score = round(score_a + score_b + score_c + score_d)
        final_score = min(200, final_score)

        st.balloons()
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Growth Forecast Index", f"{final_score} / 200")
            if final_score > 140: st.success("Forecast: Aggressive Expansion Suggested")
            elif final_score > 80: st.warning("Forecast: Moderate/Stable Growth")
            else: st.error("Forecast: Market Saturation/Intervention Required")

        with c2:
            pdf_output = generate_pdf(st.session_state.org_name, final_score, st.session_state.data_store)
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_output,
                file_name=f"Forecaster_Report_{st.session_state.org_name}.pdf",
                mime="application/pdf"
            )
            
    except Exception as e:
        st.error(f"Error in calculation: {str(e)}")

st.write("---")
if st.button("🔄 Reset System"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
