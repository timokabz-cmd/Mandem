import streamlit as st
import pandas as pd
import json
import os
import uuid

# ==================================================================
# 1. MANDATORY PAGE CONFIGURATION (Must be the absolute first command)
# ==================================================================
st.set_page_config(
    page_title="Mandem Platform Engine",
    page_icon="🇺🇬",
    layout="wide"
)

# ==================================================================
# 2. 🔒 TEMPORARY SECURITY LOCK GATE
# ==================================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Under Maintenance")
    st.write("This platform prototype is currently locked for internal updates.")
    
    # Form structure stabilizes input memory on mobile touchscreens
    with st.form("login_gate"):
        password_input = st.text_input("Enter Access PIN:", type="password")
        submit_clicked = st.form_submit_button("Unlock Platform")
        
        if submit_clicked:
            if password_input == "2567":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Access Denied. Invalid PIN.")
                
    st.stop()  # 🛑 Hard stop prevents any code below from running for unverified users

# ==================================================================
# 3. SINGLE SOURCES OF TRUTH & SHARED TAXONOMIES
# ==================================================================
STAGES = ["Idea Stage", "Startup Stage", "Growth Stage", "Mature MSME Stage"]
SECTORS = ["Agriculture & Agribusiness", "Trade & Retail", "Digital & ICT", "Manufacturing", "Logistics & Transport"]

# Initialize persistent memory for framework data cards
if "frameworks" not in st.session_state:
    st.session_state.frameworks = [
        {
            "id": str(uuid.uuid4()),
            "title": "Emyooga Specialized Category Seed Capital Access",
            "stage": "Idea Stage",
            "sector": "Manufacturing",
            "agency": "Microfinance Support Centre (MSC)",
            "qualifies": "Valid youth/entrepreneur category SACCOs formed at parish levels.",
            "steps": "Form a specialized category SACCO, register with the District Commercial Officer, and apply for seed allocation.",
            "cost": "Free initialization",
            "contact": "info@msc.co.ug"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "
