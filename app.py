import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Uganda Business Opportunity Gateway",
    page_icon="🇺🇬",
    layout="wide"
)

# 2. Initialize the Dynamic Database in Memory (Simulating an external DB)
if "gov_db" not in st.session_state:
    st.session_state.gov_db = [
        {
            "title": "Parish Agricultural Value Chain Grant Support",
            "agency": "Ministry of Local Government / PDM Secretariat",
            "stage": "Idea Stage",
            "sector": "Agriculture & Agribusiness",
            "eligibility": "Subsistence households organized in a registered Parish Enterprise Group (PEG). 30% reserved for Youth.",
            "cost": "Free (Zero statutory charges)",
            "steps": "1. Verify household status with LC1 Chair.\n2. Join a Parish Enterprise Group.\n3. Submit profile to the Parish Development Committee.",
            "contacts": "PDM Desk Officer at Sub-County level"
        },
        {
            "title": "URSB Online Business Name Registration",
            "agency": "Uganda Registration Services Bureau",
            "stage": "Startup Stage",
            "sector": "Trade & Retail",
            "eligibility": "Any Ugandan citizen aged 18+ with a valid National ID (NIN).",
            "cost": "UGX 80,000 Total",
            "steps": "1. Log into URSB OBRS portal.\n2. Run a name availability search.\n3. Complete digitized Form 3 and pay via Mobile Money.",
            "contacts": "URSB Help Desk: 0800 100 006"
        }
    ]

# Initialize Feedback Log
if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

# 3. App Header & Trust Banner
st.title("🇺🇬 Uganda Business Opportunity Gateway")
st.caption("National MSME Knowledge Infrastructure Layer • Partnered with URSB, URA, and PDM")
st.write("---")

# 4. Main Navigation Layers
app_layer = st.sidebar.radio(
    "Choose Platform Layer:",
    ["📱 Citizen Access Portal", "🏛️ Government Admin CMS Portal", "📊 Policy Analytics Hub"]
)

# ==========================================
# LAYER 1: CITIZEN ACCESS PORTAL
# ==========================================
if app_layer == "📱 Citizen Access Portal":
    st.subheader("Layer 1: Multi-Channel Delivery Engine")
    
    channel = st.radio("Select Last-Mile Interface Channel:", ["WhatsApp Simulator", "USSD Engine (*284*45#)"], horizontal=True)
    
    if channel == "WhatsApp Simulator":
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("**Step-by-Step Flow Filters**")
            selected_stage = st.selectbox("Your Business Stage:", ["Idea Stage", "Startup Stage", "Growth Stage"])
            selected_sector = st.selectbox("Your Economic Sector:", ["Agriculture & Agribusiness", "Trade & Retail", "Digital & ICT"])
            
        with col2:
            st.write("💬 **WhatsApp Active Session Screen**")
            with st.container(border=True):
                st.caption("Edge Lab Gateway • Verified Account")
                st.write(f"Hello! You are browsing in English. Let's find opportunities for your profile.")
                
                # Filter our database dynamically based on selection
                matched_cards = [card for card in st.session_state.gov_db if card["stage"] == selected_stage and card["sector"] == selected_sector]
                
                if matched_cards:
                    for card in matched_cards:
                        st.markdown(f"""
                        ---
                        📄 **OFFICIAL SERVICE CARD: {card['title']}**
                        * 🏛️ Agency:
                        * 🎯 Who Qualifies:
                        * 🛠️ Steps to Take:
                        * 💰 **Statutory Cost:** `{card['cost']}`
                        * 📞 Support Desk:
                        """)
                        
                        # --- MENTOR'S FEEDBACK LOOP ENGINE ---
                        st.write("---")
                        st.caption("👉 **Did this official information help you today?**")
                        f_col1, f_col2 = st.columns(2)
                        if f_col1.button("👍 Yes, clear steps"):
                            st.session_state.feedback_log.append({"Program": card['title'], "Status": "Helpful"})
                            st.success("Thank you for your feedback! Data sent to Ministry planners.")
                        if f_col2.button("👎 No, still confusing"):
                            st.session_state.feedback_log.append({"Program": card['title'], "Status": "Confusing/Stuck"})
                            st.error("Feedback logged. Content optimization queue updated.")
                else:
                    st.warning("🤖 No active program matches this selection yet. Try choosing 'Idea Stage' + 'Agriculture' or 'Startup Stage' + 'Trade'.")

    elif channel == "USSD Engine (*284*45#)":
        st.info("📟 Simulating a low-data feature phone network connection:")
        st.code("""
        Gateway Main Menu:
        1. Find Programs by Stage
        2. Help Hotline Details
        
        Reply: 1
        
        Select Stage:
        1. Idea Stage
        2. Startup Stage
        
        Reply: 2
        
        URSB Business Card:
        Cost: UGX 80,000. Text '1' to receive step-by-step SMS guide.
        """, language="text")

# ==========================================
# LAYER 2: GOVERNMENT ADMIN CMS PORTAL
# ==========================================
elif app_layer == "🏛️ Government Admin CMS Portal":
    st.subheader("Layer 2: Decentralized Content Management System")
    st.write("This allows verified Ministry Officers to update fees or upload new opportunities without touching code.")
    
    with st.form("cms_form", clear_on_submit=True):
        st.markdown("### Create / Update an Official Opportunity Card")
        new_title = st.text_input("Program/Opportunity Name:", value="Emyooga Micro-Finance Credit Line")
        new_agency = st.text_input("Managing Agency/Ministry:", value="Microfinance Support Centre")
        
        c1, c2 = st.columns(2)
        new_stage = c1.selectbox("Target Business Lifecycle Stage:", ["Idea Stage", "Startup Stage", "Growth Stage"])
        new_sector = c2.selectbox("Target Sector Taxonomy:", ["Agriculture & Agribusiness", "Trade & Retail", "Digital & ICT"])
        
        new_eligibility = st.text_area("Who Qualifies?", value="Active members of a specialized district category SACCO (e.g., Boda Boda operators, tailors).")
        new_cost = st.text_input("Statutory Fee Required:", value="Free to join. Savings equity minimum applies.")
        new_steps = st.text_area("Step-by-Step Application Milestones:", value="1. Join your local category SACCO.\n2. Submit development business plan to the District Commercial Officer.\n3. Vetting and fund distribution via commercial banks.")
        new_contacts = st.text_input("Direct Officer Contact/Desk:", value="District Commercial Officer at your Local District HQ")
        
        submit_btn = st.form_submit_button("🚀 Publish to National Gateway")
        
        if submit_btn:
            # Append new record directly to our live in-memory database array
            new_record = {
                "title": new_title,
                "agency": new_agency,
                "stage": new_stage,
                "sector": new_sector,
                "eligibility": new_eligibility,
                "cost": new_cost,
                "steps": new_steps,
                "contacts": new_contacts
            }
            st.session_state.gov_db.append(new_record)
            st.success(f"🎉 Success! '{new_title}' is now live on the citizen system. Switch to the 'Citizen Access Portal' tab to test it!")

# ==========================================
# LAYER 3: POLICY ANALYTICS HUB
# ==========================================
elif app_layer == "📊 Policy Analytics Hub":
    st.subheader("Layer 3: Real-Time Policy Telemetry Engine")
    st.write("Data insights flowing directly from citizen interactions to guide macroeconomic planning updates.")
    
    st.markdown("### 📈 Live User Feedback Stream")
    if st.session_state.feedback_log:
        df = pd.DataFrame(st.session_state.feedback_log)
        st.dataframe(df, use_container_width=True)
        
        # Simple count calculation
        helpful_count = sum(1 for item in st.session_state.feedback_log if item["Status"] == "Helpful")
        st.metric("Total Citizen Success Inputs Received", helpful_count, f"{len(st.session_state.feedback_log) - helpful_count} flagged bottlenecks")
    else:
        st.info("No feedback metrics gathered yet this session. Go to the Citizen Portal, review a card, and click a Thumbs Up/Down button to populate this dashboard.")
