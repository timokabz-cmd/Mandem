import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Edge Lab Platform",
    page_icon="🇺🇬",
    layout="wide"
)

# 2. Master Database Initialization
if "gov_db" not in st.session_state:
    st.session_state.gov_db = [
        {
            "title": "Parish Agricultural Value Chain Grant Support",
            "agency": "Ministry of Local Government / PDM Secretariat",
            "stage": "Idea Stage",
            "sector": "Agriculture & Agribusiness",
            "eligibility": "Subsistence households organized in a registered Parish Enterprise Group (PEG). 30% reserved for Youth.",
            "cost": "Free (Zero statutory charges)",
            "steps": "1. Register with your local LC1 Chair. 2. Join a verified Parish Enterprise Group. 3. Apply via the Parish Development Management Information System (PBMIS).",
            "contacts": "PDM Desk Officer at Sub-County level"
        },
        {
            "title": "URSB Online Business Name Registration",
            "agency": "Uganda Registration Services Bureau",
            "stage": "Startup Stage",
            "sector": "Trade & Retail",
            "eligibility": "Any Ugandan citizen aged 18+ with a valid National ID (NIN).",
            "cost": "UGX 80,000 Total",
            "steps": "1. Log into URSB OBRS portal. 2. Run a name availability search. 3. Complete digitized Form 3 and pay via Mobile Money.",
            "contacts": "URSB Help Desk: 0800 100 006"
        }
    ]

if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

# 3. Sidebar Infrastructure Navigation (Matches App Layout Images)
st.sidebar.markdown("## 🇺🇬 EDGE LAB PLATFORM")
st.sidebar.caption("National MSME & Youth Opportunity Knowledge Infrastructure")
st.sidebar.write("---")

view = st.sidebar.radio(
    "Select Interface View:",
    ["📱 Citizen WhatsApp Simulator", "🏛️ Government Admin CMS Portal", "📊 Gov Intelligence Dashboard"]
)

# ==========================================
# VIEW 1: CITIZEN WHATSAPP SIMULATOR
# ==========================================
if view == "📱 Citizen WhatsApp Simulator":
    st.title("WhatsApp-First Prototype Flow")
    st.info("💡 Simulated View: This represents the logic executing behind a user's WhatsApp interface via QR Code check-in at an LC1 Office.")
    
    st.subheader("Interactive Menu Options")
    
    # Conditional Filter Dropdowns
    stage_options = ["Select Stage", "Idea Stage", "Startup Stage", "Growth Stage", "Mature MSME Stage"]
    selected_stage = st.selectbox("WhatsApp Button Send: Choose Your Stage", stage_options)
    
    selected_sector = "Select Sector"
    if selected_stage != "Select Stage":
        sector_options = ["Select Sector", "Agriculture & Agribusiness", "Trade & Retail", "Digital & ICT", "Manufacturing"]
        selected_sector = st.selectbox("WhatsApp Button Send: Choose Your Sector", sector_options)
        
    st.write("---")
    st.subheader("💬 WhatsApp Screen Emulator")
    
    # Message Simulation Feed
    with st.container(border=True):
        st.caption("Incoming from Edge Lab Bot • Active")
        st.write("🤖 **Welcome to Edge Lab Platform!** You scanned the QR code at **LC1 Anchor Office**. Please interact with the options on the left.")
        
        if selected_stage != "Select Stage":
            st.success(f"🧑 **I chose:** {selected_stage}")
            
        if selected_sector != "Select Sector":
            st.success(f"🧑 **My sector is:** {selected_sector}")
            
            # Dynamic DB Query Engine
            matched = [card for card in st.session_state.gov_db if card["stage"] == selected_stage and card["sector"] == selected_sector]
            
            if matched:
                for idx, card in enumerate(matched):
                    st.write("---")
                    st.markdown(f"🤖 📄 **OFFICIAL SERVICE CARD: {card['title']}**")
                    st.markdown(f"* 🏛️ Agency:")
                    st.markdown(f"* 🎯 Who Qualifies:")
                    st.markdown(f"* 🛠️ Steps to Take:")
                    st.markdown(f"* 💰 **Statutory Cost:** `{card['cost']}`")
                    st.markdown(f"* 📞 Support Desk:")
                    
                    # Macro Feedback Metric Connection
                    st.write("---")
                    st.caption("👉 *Did this official information help you today?*")
                    f_col1, f_col2 = st.columns(2)
                    if f_col1.button("👍 Yes, clear steps", key=f"yes_{idx}"):
                        st.session_state.feedback_log.append({"Program": card['title'], "Status": "Helpful Framework"})
                        st.success("System routing verification entry saved!")
                    if f_col2.button("👎 No, still confusing", key=f"no_{idx}"):
                        st.session_state.feedback_log.append({"Program": card['title'], "Status": "Friction Warning"})
                        st.error("Optimization query dispatched to ministry lead.")
            else:
                st.warning("🤖 No program matches this exact profile permutation yet. Use the CMS portal to instantiate a card layout.")

# ==========================================
# VIEW 2: GOVERNMENT ADMIN CMS PORTAL
# ==========================================
elif view == "🏛️ Government Admin CMS Portal":
    st.title("Government Admin CMS Portal")
    st.write("Enables direct administrative modification of program parameters, compliance metrics, and active fee structures.")
    
    with st.form("cms_form", clear_on_submit=True):
        st.markdown("### 📝 Upload/Modify Enterprise Opportunity Data Card")
        new_title = st.text_input("Program Opportunity Name:", value="Emyooga Micro-Finance Credit Line")
        new_agency = st.text_input("Managing Agency/Ministry:", value="Microfinance Support Centre")
        
        new_stage = st.selectbox("Target Business Lifecycle Stage:", ["Idea Stage", "Startup Stage", "Growth Stage", "Mature MSME Stage"])
        new_sector = st.selectbox("Target Sector Taxonomy:", ["Agriculture & Agribusiness", "Trade & Retail", "Digital & ICT", "Manufacturing"])
        
        new_eligibility = st.text_area("Who Qualifies?", value="Active members of a specialized district category SACCO (e.g., Boda Boda operators, tailors).")
        new_cost = st.text_input("Statutory Fee Required (e.g., UGX 253,250):", value="Free to join. Savings equity minimum applies.")
        new_steps = st.text_area("Step-by-Step Application Milestones:", value="1. Join your local category SACCO. 2. Submit development business plan to the District Commercial Officer. 3. Vetting and fund distribution via commercial banks.")
        new_contacts = st.text_input("Direct Officer Contact/Desk:", value="District Commercial Officer at your Local District HQ")
        
        submit_btn = st.form_submit_button("🚀 Publish to National Gateway")
        
        if submit_btn:
            st.session_state.gov_db.append({
                "title": new_title,
                "agency": new_agency,
                "stage": new_stage,
                "sector": new_sector,
                "eligibility": new_eligibility,
                "cost": new_cost,
                "steps": new_steps,
                "contacts": new_contacts
            })
            st.success(f"🎉 Success! '{new_title}' is now live on the citizen system. Switch to the 'Citizen WhatsApp Simulator' view to test it!")

# ==========================================
# VIEW 3: GOV INTELLIGENCE DASHBOARD
# ==========================================
elif view == "📊 Gov Intelligence Dashboard":
    st.title("National MSME Demand Intelligence Matrix")
    st.write("Anonymized, real-time demand insights collected from WhatsApp routing systems.")
    
    # High-level matrix targets matching Image 9 exactly
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Scans via LC1 QR Blocks", "14,250", "+12% this week")
    col2.metric("Active WhatsApp Flows", "8,940", "84% Completion Rate")
    col3.metric("Highest Bottleneck Point", "URA Tax ID Setup", "Average 4.2 days dropoff", delta_color="inverse")
    
    st.write("---")
    st.subheader("Geographic and Sectoral Traffic Densities")
    
    # Accurate multi-regional analytics layout tracking metrics matching Image 10
    chart_data = pd.DataFrame({
        'Agribusiness': [3900, 4500, 2400],
        'ICT': [400, 200, 1900],
        'Logistics': [600, 300, 1200],
        'Manufacturing': [650, 450, 800],
        'Retail & Trade': [1800, 1100, 4100]
    }, index=['Western Region', 'Northern Region', 'Central Region (Kampala)'])
    
    st.bar_chart(chart_data.T)
    
    # Real-Time Telemetry Log Component
    with st.expander("🔍 View Policy Formulation Feedback Logs"):
        if st.session_state.feedback_log:
            st.dataframe(pd.DataFrame(st.session_state.feedback_log), use_container_width=True)
        else:
            st.info("System streaming operational. Real-time logging metrics will populate here as live inputs are recorded.")
