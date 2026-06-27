import streamlit as st
import pandas as pd
import json
import os
import uuid

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Mandem Platform",
    page_icon="🇺🇬",
    layout="wide"
)

# ==========================================
# 2. 🔒 SECURITY LOCK GATE
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Under Maintenance")
    st.write("Locked for internal updates.")
    
    with st.form("login_gate"):
        pwd = st.text_input(
            "Enter Access PIN:", 
            type="password"
        )
        submit = st.form_submit_button(
            "Unlock Platform"
        )
        
        if submit:
            if pwd == "2567":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid PIN.")
                
    st.stop()

# ==========================================
# 3. TAXONOMIES & DATA CORES
# ==========================================
STAGES = [
    "Idea Stage", 
    "Startup Stage", 
    "Growth Stage", 
    "Mature MSME Stage"
]
SECTORS = [
    "Agriculture & Agribusiness", 
    "Trade & Retail", 
    "Digital & ICT", 
    "Manufacturing", 
    "Logistics & Transport"
]

if "frameworks" not in st.session_state:
    st.session_state.frameworks = [
        {
            "id": str(uuid.uuid4()),
            "title": (
                "Emyooga Specialized Category "
                "Seed Capital Access"
            ),
            "stage": "Idea Stage",
            "sector": "Manufacturing",
            "agency": "MSC Support Centre",
            "qualifies": "Valid youth parish SACCOs.",
            "steps": "Register via District Officer.",
            "cost": "Free initialization",
            "contact": "info@msc.co.ug"
        },
        {
            "id": str(uuid.uuid4()),
            "title": (
                "URSB Online Business "
                "Name Registration"
            ),
            "stage": "Startup Stage",
            "sector": "Trade & Retail",
            "agency": "URSB Uganda",
            "qualifies": "Sole proprietors.",
            "steps": "Submit Form 3 on OBRS gateway.",
            "cost": "24,000 UGX",
            "contact": "ursb@ursb.go.ug"
        },
        {
            "id": str(uuid.uuid4()),
            "title": (
                "URSB Limited Liability "
                "Company Incorporation"
            ),
            "stage": "Startup Stage",
            "sector": "Manufacturing",
            "agency": "URSB Uganda",
            "qualifies": "Founders seeking corporate body.",
            "steps": "Upload MemArts documents to OBRS.",
            "cost": "180,000 UGX approx",
            "contact": "ursb@ursb.go.ug"
        },
        {
            "id": str(uuid.uuid4()),
            "title": (
                "URA Corporate Tax "
                "Identification Number"
            ),
            "stage": "Startup Stage",
            "sector": "Trade & Retail",
            "agency": "Uganda Revenue Authority",
            "qualifies": "Any registered business entity.",
            "steps": "Complete online TIN request form.",
            "cost": "Free allocation",
            "contact": "services@ura.go.ug"
        },
        {
            "id": str(uuid.uuid4()),
            "title": (
                "MAAIF Micro-Scale "
                "Irrigation Matching Grant"
            ),
            "stage": "Growth Stage",
            "sector": "Agriculture & Agribusiness",
            "agency": "Ministry of Agriculture",
            "qualifies": "Smallholder farmers with water.",
            "steps": "Apply via District Production Officer.",
            "cost": "Co-funding split metrics",
            "contact": "maaif@maaif.go.ug"
        },
        {
            "id": str(uuid.uuid4()),
            "title": (
                "PSFU GROW Project "
                "Women Enterprise Scheme"
            ),
            "stage": "Growth Stage",
            "sector": "Trade & Retail",
            "agency": "PSFU / World Bank",
            "qualifies": "Female-led or female-owned MSMEs.",
            "steps": "Apply via tier bank intermediaries.",
            "cost": "Concessionary rates apply",
            "contact": "grow@psfu.org.ug"
        },
        {
            "id": str(uuid.uuid4()),
            "title": (
                "NSSF Hi-Innovator "
                "Seed Funding Accelerator"
            ),
            "stage": "Growth Stage",
            "sector": "Digital & ICT",
            "agency": "NSSF & Outbox Hub",
            "qualifies": "Post-revenue local tech startups.",
            "steps": "Complete online learning modules
