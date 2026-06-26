import streamlit as st
import pandas as pd
import random

# App Config
st.set_page_config(page_title="Edge Lab Platform", page_icon="🇺🇬", layout="wide")

# Mock Database for Uganda Knowledge Layer
KNOWLEDGE_BASE = {
    "Idea Stage": {
        "Agriculture & Agribusiness": {
            "title": "PDM Agriculture Value Chain Support",
            "eligibility": "Subsistence households, women (30%), youth (30%) organized in Parish SACCOs.",
            "steps": "1. Register with your local LC1 Chair.\n2. Join a verified Parish Enterprise Group.\n3. Apply via the Parish Development Management Information System (PBMIS).",
            "cost": "Free",
            "agency": "Ministry of Local Government / PDM Secretariat"
        },
        "Trade & Retail": {
            "title": "Micro-Retail Registration Pathways",
            "eligibility": "Sole proprietors, local informal kiosk owners.",
            "steps": "1. Choose 3 unique business names.\n2. Submit name reservation on the URSB OBRS portal.",
            "cost": "UGX 25,000 for name reservation",
            "agency": "URSB"
        }
    },
    "Startup Stage": {
        "Agriculture & Agribusiness": {
            "title": "URSB Business Name Registration",
            "eligibility": "Any Ugandan citizen aged 18+ with a valid National ID.",
            "steps": "1. Access the URSB Online Business Registration System (OBRS).\n2. Upload National ID.\n3. Pay statutory fees via Mobile Money.",
            "cost": "UGX 80,000+",
            "agency": "URSB"
        },
        "Trade & Retail": {
            "title": "URA TIN Acquisition",
            "eligibility": "Registered business name or company owners.",
            "steps": "1. Log into URA web portal.\n2. Submit URSB registration number.\n3. Complete self-assessment for presumptive tax thresholds.",
            "cost": "Free",
            "agency": "Uganda Revenue Authority"
        }
    }
}

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🇺🇬 EDGE LAB PLATFORM")
st.sidebar.markdown("*National MSME & Youth Opportunity Knowledge Infrastructure*")
st.sidebar.write("---")
view_mode = st.sidebar.radio("Select Interface View:", ["📱 Citizen WhatsApp Simulator", "📊 Gov Intelligence Dashboard"])

# --- VIEW 1: CITIZEN WHATSAPP SIMULATOR ---
if view_mode == "📱 Citizen WhatsApp Simulator":
    st.title("WhatsApp-First Prototype Flow")
    st.info("💡 Simulated View: This represents the logic executing behind a user's WhatsApp interface via QR Code check-in at an LC1 Office.")
    
    # Simulating session state variables for chat history
    if "stage" not in st.session_state:
        st.session_state.stage = "Select Stage"
    if "sector" not in st.session_state:
        st.session_state.sector = None

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Interactive Menu Options")
        
        # Step 1: Select Lifecycle Stage
        stages = ["Select Stage", "Idea Stage", "Startup Stage", "Growth Stage", "Mature MSME Stage"]
        selected_stage = st.selectbox("WhatsApp Button Send: Choose Your Stage", stages, index=stages.index(st.session_state.stage))
        
        if selected_stage != st.session_state.stage:
            st.session_state.stage = selected_stage
            st.session_state.sector = None
            st.rerun()

        # Step 2: Select Sector Taxonomy
        if st.session_state.stage != "Select Stage":
            sectors = ["Select Sector", "Agriculture & Agribusiness", "Trade & Retail", "Digital & ICT", "Manufacturing"]
            selected_sector = st.selectbox("WhatsApp Button Send: Choose Your Sector", sectors)
            if selected_sector != "Select Sector":
                st.session_state.sector = selected_sector

    with col2:
        st.subheader("💬 WhatsApp Screen Emulator")
        
        # Base UI block representing phone window
        with st.container(border=True):
            st.caption("Incoming from Edge Lab Bot • Active")
            st.chat_message("assistant").write(f"Welcome to Edge Lab Platform! You scanned the QR code at **LC1 Anchor Office**. Please interact with the options on the left.")
            
            if st.session_state.stage != "Select Stage":
                st.chat_message("user").write(f"I chose: *{st.session_state.stage}*")
                
                if st.session_state.sector:
                    st.chat_message("user").write(f"My sector is: *{st.session_state.sector}*")
                    
                    # Fetch card data
                    card = KNOWLEDGE_BASE.get(st.session_state.stage, {}).get(st.session_state.sector, None)
                    
                    if card:
                        st.chat_message("assistant").markdown(f"""
                        **📄 SERVICE CARD: {card['title']}**
                        
                        *🏛️ Managing Agency:* {card['agency']}
                        
                        *🎯 Who Qualifies:* {card['eligibility']}
                        
                        *🛠️ Step-by-Step Process:*
                        {card['steps']}
                        
                        *💰 Total Estimated Cost:* `{card['cost']}`
                        
                        ---
                        *Reply 'HELP' to speak with an assistant or '0' to return to Main Menu.*
                        """)
                    else:
                        st.chat_message("assistant").write("⚠️ No localized service card is available for this combination yet. Content pipeline active.")

# --- VIEW 2: GOVERNMENT INTELLIGENCE LAYER ---
elif view_mode == "📊 Gov Intelligence Dashboard":
    st.title("National MSME Demand Intelligence Matrix")
    st.markdown("Anonymized, real-time demand insights collected from WhatsApp routing systems.")
    
    # Mock Data Matrix
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    metrics_col1.metric("Total Scans via LC1 QR Blocks", "14,250", "+12% this week")
    metrics_col2.metric("Active WhatsApp Flows", "8,940", "84% Completion Rate")
    metrics_col3.metric("Highest Bottleneck Point", "URA Tax ID Setup", "Average 4.2 days dropoff")
    
    st.write("---")
    st.subheader("Geographic and Sectoral Traffic Densities")
    
    # Simulating data insights for policy feedback
    chart_data = pd.DataFrame({
        'Sector': ['Agribusiness', 'Retail & Trade', 'Logistics', 'ICT', 'Manufacturing'],
        'Central Region (Kampala/Wakiso)': [2300, 4100, 1200, 1900, 800],
        'Northern Region (Gulu/Lira)': [4500, 1100, 300, 200, 400],
        'Western Region (Mbarara/Hoima)': [3900, 1800, 600, 400, 700]
    })
    
    st.bar_chart(chart_data.set_index('Sector'))
    
    with st.expander("🔍 View Policy Formulation Feedback Logs"):
        st.dataframe(pd.DataFrame([
            {"Timestamp": "2026-06-25", "District": "Gulu", "Insight": "High baseline dropout rates noted when users encounter the phrase 'URSB OBRS Portal'. Suggesting localized radio show explainer content for URSB registration steps."},
            {"Timestamp": "2026-06-26", "District": "Mbarara", "Insight": "Agribusiness applications for PDM funding spiking. Ensure regional desks validate physical group setups via LC2 chairs immediately."}
        ]))
