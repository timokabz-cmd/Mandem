import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_set_page_config if hasattr(st, "set_set_page_config") else st.set_page_config(
    page_title="Uganda Business Opportunity Gateway",
    page_icon="🇺🇬",
    layout="wide"
)

# 2. Initialize the Master Database in Memory (Simulating Decoupled Data Layer)
if "gov_db" not in st.session_state:
    st.session_state.gov_db = [
        {
            "title": "Parish Agricultural Value Chain Grant Support",
            "agency": "Ministry of Local Government / PDM Secretariat",
            "stage": "Idea Stage",
            "sector": "Agriculture & Agribusiness",
            "eligibility": "Subsistence households organized in a registered Parish Enterprise Group (PEG). 30% reserved for Youth.",
            "cost": "Free (Zero statutory charges)",
            "steps": "1. Verify household status with LC1 Chair. 2. Join a Parish Enterprise Group. 3. Submit profile to the Parish Development Committee.",
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
        },
        {
            "title": "UiT Digital Skilling & ICT Innovation Grant",
            "agency": "Ministry of ICT and National Guidance",
            "stage": "Growth Stage",
            "sector": "Digital & ICT",
            "eligibility": "Young Ugandan tech innovators with an active working prototype or MVP.",
            "cost": "Free to apply",
            "steps": "1. Submit technical architecture documentation online. 2. Present proof of concept to innovation hub assessment team.",
            "contacts": "National ICT Innovation Hub, Nakawa"
        }
    ]

# Initialize Dynamic Feedback Log for the Telemetry Engine
if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

# 3. Main Infrastructure Title Banner
st.title("🇺🇬 Uganda Business Opportunity Gateway")
st.caption("National MSME Knowledge Infrastructure Layer • Powered by Edge Lab Analytics")
st.write("---")

# MOBILE FIX 1: Navigation via Main Tabs instead of Sidebar to prevent browser connection drops
tab_citizen, tab_cms, tab_analytics = st.tabs([
    "📱 Citizen Access Portal", 
    "🏛️ Government Admin CMS Portal", 
    "📊 Policy Analytics Hub"
])

# ==========================================
# TAB 1: CITIZEN ACCESS PORTAL
# ==========================================
with tab_citizen:
    st.subheader("Layer 1: Multi-Channel Delivery Infrastructure")
    
    # Last-Mile Delivery Channel Toggle
    channel = st.radio("Choose Last-Mile Access Channel Interface:", ["WhatsApp Core Simulator", "USSD Engine (*284*45#)", "Conversational AI Assistant Layer"], horizontal=True)
    st.write("---")
    
    if channel == "WhatsApp Core Simulator":
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 👤 User Profile & Localization")
            # Localization & Profile variables retained from previous builds
            selected_lang = st.selectbox("Interface Language / Localization:", ["English", "Luganda", "Runyankole", "Ateso", "Acholi", "Lusoga"])
            selected_profile = st.selectbox("Target Demographics Profile:", ["General Public", "Youth-Led Enterprise", "Women in Business", "Refugee Entrepreneurs"])
            
            st.markdown("### 🔍 Taxonomy Navigation Filters")
            selected_stage = st.selectbox("Your Business Lifecycle Stage:", ["Idea Stage", "Startup Stage", "Growth Stage"])
            selected_sector = st.selectbox("Your Economic Sector:", ["Agriculture & Agribusiness", "Trade & Retail", "Digital & ICT"])
            
        with col2:
            st.write(f"💬 **Active WhatsApp Session ({selected_lang})**")
            with st.container(border=True):
                st.caption("🔒 Verified Government Information Gateway")
                st.write(f"Hello! Your profile is configured as **{selected_profile}**. Showing verified operational steps matching your criteria below:")
                
                # Query the in-memory database array dynamically
                matched_cards = [card for card in st.session_state.gov_db if card["stage"] == selected_stage and card["sector"] == selected_sector]
                
                if matched_cards:
                    for idx, card in enumerate(matched_cards):
                        st.write("---")
                        # MOBILE FIX 2: Individual line rendering explicitly avoids markdown interpretation bugs
                        st.markdown(f"### 📄 OFFICIAL SERVICE CARD: {card['title']}")
                        st.markdown(f"🏛️ Managing Agency:")
                        st.markdown(f"🎯 Direct Eligibility Requirements:")
                        st.markdown(f"🛠️ Step-by-Step Milestones:")
                        st.markdown(f"**💰 Statutory Costs & Fees:** `{card['cost']}`")
                        st.markdown(f"📞 Direct Help Desk Contacts:")
                        
                        # --- THE CRITICAL FEEDBACK LOOP ENGINE ---
                        st.write("---")
                        st.caption("👉 **Did this official information help you navigate the process?**")
                        f_col1, f_col2 = st.columns(2)
                        if f_col1.button("👍 Yes, steps are clear", key=f"yes_{idx}_{card['title']}"):
                            st.session_state.feedback_log.append({"Program": card['title'], "Status": "Helpful", "Language": selected_lang})
                            st.success("Feedback submitted to macro policy planning dashboard!")
                        if f_col2.button("👎 No, I am still stuck", key=f"no_{idx}_{card['title']}"):
                            st.session_state.feedback_log.append({"Program": card['title'], "Status": "Confusing/Stuck", "Language": selected_lang})
                            st.error("Bottleneck report logged. Redirecting to optimization queue.")
                else:
                    st.warning("🤖 No active program matches this exact stage and sector filter combination yet. Use the CMS tab to publish one instantly.")

    elif channel == "USSD Engine (*284*45#)":
        st.info("📟 Simulating Real-Time USSD String Broadcast over Telecommunications Network:")
        st.code("""
        Gateway Main Menu:
        1. Find Programs by Stage
        2. Language Selection (English/Luganda)
        3. Help Desk Lines
        
        [Reply 1]
        
        Select Lifecycle Stage:
        1. Idea Stage
        2. Startup Stage
        3. Growth Stage
