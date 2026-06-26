import streamlit as st
import pandas as pd
import json
import os
import uuid
from datetime import datetime

# ------------------------------------------------------------------
# 1. Page Configuration
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Edge Lab Platform",
    page_icon="🇺🇬",
    layout="wide"
)

# ------------------------------------------------------------------
# 2. Shared Taxonomies & Single Sources of Truth
# ------------------------------------------------------------------
STAGES = ["Idea Stage", "Startup Stage", "Growth Stage", "Mature MSME Stage"]
SECTORS = ["Agriculture & Agribusiness", "Trade & Retail", "Digital & ICT", "Manufacturing"]
CAPITAL_TIERS = ["Micro (Under UGX 5M)", "Small (UGX 5M - 20M)", "Medium/Commercial (UGX 20M+)"]

# ------------------------------------------------------------------
# 3. Dual-Database File Persistence Framework
# ------------------------------------------------------------------
GOV_DB_FILE = "gov_db.json"
BLUEPRINT_DB_FILE = "blueprint_db.json"
FEEDBACK_FILE = "feedback_log.json"

# Master Dataset 1: Official Regulatory & Funding Channels
DEFAULT_GOV_DB = [
    {
        "id": "peg-001",
        "title": "Parish Agricultural Value Chain Grant Support",
        "agency": "Ministry of Local Government / PDM Secretariat",
        "stage": "Idea Stage",
        "sector": "Agriculture & Agribusiness",
        "eligibility": "Subsistence households organized in a registered Parish Enterprise Group (PEG). 30% reserved for Youth.",
        "cost": "Free (Zero statutory charges)",
        "steps": "1. Register with your local LC1 Chair. 2. Join a verified Parish Enterprise Group. 3. Apply via the PBMIS portal.",
        "contacts": "PDM Desk Officer at Sub-County level"
    },
    {
        "id": "ursb-002",
        "title": "URSB Limited Liability Company Incorporation",
        "agency": "Uganda Registration Services Bureau",
        "stage": "Startup Stage",
        "sector": "Manufacturing",
        "eligibility": "Enterprises with a minimum of two directors holding valid Ugandan National IDs (NIN).",
        "cost": "UGX 140,000 baseline registration assessment fees.",
        "steps": "1. Reserve company name online via OBRS portal. 2. Upload digitized Memorandum and Articles of Association. 3. Complete Form 18 and Form 20 parameters.",
        "contacts": "URSB Bureau Head Office, Kampala / obrs.ursb.go.ug"
    },
    {
        "id": "grow-001",
        "title": "PSFU GROW Project Women Enterprise Loan Scheme",
        "agency": "Private Sector Foundation Uganda / MoGLSD",
        "stage": "Growth Stage",
        "sector": "Trade & Retail",
        "eligibility": "Micro or small enterprises owned by women (minimum 51% shareholding) with a valid trading license.",
        "cost": "Zero application fees. Concessionary borrowing rates fixed at 10%-12% per annum.",
        "steps": "1. Confirm business functions match social safeguard baselines. 2. Present flexible security options to a participating commercial bank partner.",
        "contacts": "GROW Project Secretariat Hub at PSFU / grow@psfu.org.ug"
    }
]

# Master Dataset 2: "It Works. Try It." Business Histories & Content Blueprints
DEFAULT_BLUEPRINT_DB = [
    {
        "id": "bp-poultry-001",
        "title": "High-Yield Commercial Poultry Blueprint (5,000 Birds)",
        "sector": "Agriculture & Agribusiness",
        "tier": "Medium/Commercial (UGX 20M+)",
        "capital_required": "UGX 35,000,000 - UGX 45,000,000 (Chicks, feed cycle, and structures)",
        "summary": "Detailed implementation operational guide for scaling a commercial layer poultry unit. Focuses on biosecurity controls, deep-litter housing layout vectors, and high-tier nutritional sourcing metrics.",
        "fin_lit_tip": "CRITICAL CASHFLOW METRIC: Point-of-lay birds require intensive feed inputs for the first 18-20 weeks before generating single-egg revenues. Maintain a minimum working capital reserve equal to 45% of infrastructure cost exclusively for feed layers.",
        "success_case": "Case Study: Ronald K. from Wakiso District successfully expanded from 200 birds to 5,500 birds using localized feed formulation techniques.",
        "media_anchor": "📺 Video Link: 'It Works. Try It.' — Episode 12: Structuring Poultry Run-Rates"
    },
    {
        "id": "bp-coffee-001",
        "title": "Smallholder Arabica/Robusta Coffee Cultivation Roadmap",
        "sector": "Agriculture & Agribusiness",
        "tier": "Small (UGX 5M - 20M)",
        "capital_required": "UGX 6,500,000 (Per acre including land prep, high-yield plantlets, and fertilizer lines)",
        "summary": "Step-by-step land spacing mapping (3m x 3m for Robusta) optimizing yield metrics per acre. Features integrated intercropping systems with seasonal cash crops to provide immediate short-term farm liquidity.",
        "fin_lit_tip": "HARVEST CYCLING: Coffee is a long-term economic anchor requiring 2-3 years to mature. Intercrop with beans or matooke during seasons 1 and 2 to absorb maintenance cash-burn until your primary harvest windows open.",
        "success_case": "Case Study: Nabakooza Mary in Masaka managed to self-fund her processing huller equipment using high-density organic intercropping returns.",
        "media_anchor": "📺 Video Link: 'It Works. Try It.' — Episode 08: Intercropping Cash Extraction Strategies"
    },
    {
        "id": "bp-bakery-001",
        "title": "Urban Specialized Bakery & Pastry Setup",
        "sector": "Manufacturing",
        "tier": "Small (UGX 5M - 20M)",
        "capital_required": "UGX 12,000,000 (Commercial deck oven, high-capacity mixer, and premises retrofitting)",
        "summary": "A startup production template detailing daily raw material handling, local government health certification guidelines, and decentralized distributions targeting corner retail stores.",
        "fin_lit_tip": "ASSET DEPRECIATION CONTROL: Prioritize high-quality locally fabricated stainless steel tables but invest heavily in a standard imported deck oven with predictable heat regulation parameters to eliminate batch spoilage.",
        "success_case": "Case Study: Edge Bakery Project started with a single domestic home oven in Kamwokya and now supplies 14 retail shops across Kampala central.",
        "media_anchor": "📺 Video Link: 'It Works. Try It.' — Episode 19: Bakery Unit Economics Demystified"
    }
]


def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    save_json(path, default)
    return [dict(item) for item in default]


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# Initializing memory caches
if "gov_db" not in st.session_state:
    st.session_state.gov_db = load_json(GOV_DB_FILE, DEFAULT_GOV_DB)

if "blueprint_db" not in st.session_state:
    st.session_state.blueprint_db = load_json(BLUEPRINT_DB_FILE, DEFAULT_BLUEPRINT_DB)

if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = load_json(FEEDBACK_FILE, [])

# ------------------------------------------------------------------
# 4. Sidebar Navigation & Developer Controls
# ------------------------------------------------------------------
st.sidebar.markdown("## 🇺🇬 EDGE LAB PLATFORM")
st.sidebar.caption("National MSME & Youth Opportunity Knowledge Infrastructure")
st.sidebar.write("---")

view = st.sidebar.radio(
    "Select Interface View:",
    [
        "📱 Citizen WhatsApp Simulator", 
        "📟 Citizen USSD Simulator", 
        "🏛️ Government Admin CMS Portal", 
        "📊 Gov Intelligence Dashboard"
    ]
)

st.sidebar.write("---")
st.sidebar.markdown("### 🛠️ Developer Controls")
if st.sidebar.button("🔄 Reset Demo Data (DB + Feedback)"):
    save_json(GOV_DB_FILE, DEFAULT_GOV_DB)
    save_json(BLUEPRINT_DB_FILE, DEFAULT_BLUEPRINT_DB)
    save_json(FEEDBACK_FILE, [])
    st.session_state.gov_db = load_json(GOV_DB_FILE, DEFAULT_GOV_DB)
    st.session_state.blueprint_db = load_json(BLUEPRINT_DB_FILE, DEFAULT_BLUEPRINT_DB)
    st.session_state.feedback_log = []
    st.rerun()

# ==================================================================
# VIEW 1: CITIZEN WHATSAPP SIMULATOR
# ==================================================================
if view == "📱 Citizen WhatsApp Simulator":
    st.title("WhatsApp-First Interactive Prototype Flow")
    st.info("💡 Simulated View: This emulates the logic executed by the automated Edge Lab WhatsApp bot framework.")

    w_tab1, w_tab2 = st.tabs(["🏛️ Official Government Services", "📺 'It Works. Try It.' Business Blueprints"])

    with w_tab1:
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            selected_stage = st.selectbox("Choose Your Current Lifecycle Stage:", ["Select Stage"] + STAGES)
            selected_sector = st.selectbox("Choose Your Target Sector:", ["Select Sector"] + SECTORS) if selected_stage != "Select Stage" else "Select Sector"
        with col_nav2:
            gov_search = st.text_input("🔍 Quick Keyword Search (e.g., 'URSB', 'Grant'):", value="")

        with st.container(border=True):
            st.caption("Incoming from Edge Lab Bot • Regulatory Portal")
            matched_gov = []
            
            if gov_search.strip():
                q = gov_search.lower()
                matched_gov = [c for c in st.session_state.gov_db if q in c.get("title","").lower() or q in c.get("agency","").lower()]
            elif selected_stage != "Select Stage" and selected_sector != "Select Sector":
                matched_gov = [c for c in st.session_state.gov_db if c.get("stage") == selected_stage and c.get("sector") == selected_sector]

            if matched_gov:
                for card in matched_gov:
                    st.markdown(f"🤖 📄 **OFFICIAL REGULATORY SERVICE: {card.get('title')}**")
                    st.markdown(f"* **Ministry/Agency:** {card.get('agency')}")
                    st.markdown(f"* **Qualifications:** {card.get('eligibility')}")
                    st.markdown(f"* **Execution Steps:** {card.get('steps')}")
                    st.markdown(f"* **Statutory Fee:** `{card.get('cost')}`")
                    st.write("---")
            else:
                st.caption("Adjust your structural filters above to display official ministry compliance options.")

    with w_tab2:
        col_bp1, col_bp2 = st.columns(2)
        with col_bp1:
            selected_bp_sector = st.selectbox("Filter Blueprints by Industry Sector:", ["Select Sector"] + SECTORS)
            selected_bp_tier = st.selectbox("Filter by Initial Capital Tier Budget:", ["Select Tier"] + CAPITAL_TIERS) if selected_bp_sector != "Select Sector" else "Select Tier"
        with col_bp2:
            bp_search = st.text_input("🔍 Search Concepts (e.g., 'Poultry', 'Coffee', 'Bakery'):", value="")

        with st.container(border=True):
            st.caption("Incoming from Edge Lab Bot • Knowledge & Financial Literacy Stream")
            matched_bp = []

            if bp_search.strip():
                q = bp_search.lower()
                matched_bp = [b for b in st.session_state.blueprint_db if q in b.get("title","").lower() or q in b.get("summary","").lower() or q in b.get("success_case","").lower()]
            elif selected_bp_sector != "Select Sector" and selected_bp_tier != "Select Tier":
                matched_bp = [b for b in st.session_state.blueprint_db if b.get("sector") == selected_bp_sector and b.get("tier") == selected_bp_tier]

            if matched_bp:
                for bp in matched_bp:
                    st.markdown(f"### 💡 {bp.get('title')}")
                    st.caption(f"📂 Sector: {bp.get('sector')} | Capital Tier Allocation: {bp.get('tier')}")
                    st.markdown(f"💰 **Estimated Startup Capital Requirement:** \n`{bp.get('capital_required')}`")
                    st.markdown("📝 **Core Strategic Summary:**")
                    st.write(bp.get("summary"))
                    st.markdown("📊 **Financial Literacy Masterclass Note:**")
                    st.info(bp.get("fin_lit_tip"))
                    st.markdown("🏆 **Field Proof Verification:**")
                    st.success(bp.get("success_case"))
                    st.markdown(f"🔗 **Production Media Anchor:** \n`{bp.get('media_anchor')}`")
                    st.write("---")
            else:
                st.warning("🤖 Select an industry sector and capital tier budget or type a keyword search pattern to inspect our interactive 'It Works. Try It.' production summaries.")

    # ------------------------------------------------------------------
    # Dual Synthesis Conversational Copilot Block
    # ------------------------------------------------------------------
    st.write("---")
    st.markdown("### 🤖 Edge Lab Conversational AI Copilot (Dual-Synthesis Engine)")
    st.caption("Simulated Context-Aware LLM Endpoint — Programmatically cross-referencing Official Policy with Real-World Field Blueprints.")
    
    ai_prompt = st.text_input("Ask any unstructured business question (e.g., 'I want to start a poultry farm, how do I get funding and survive the first months?'):")
    
    if ai_prompt:
        q_lower = ai_prompt.lower()
        
        # Internal search simulation across both engines
        copied_gov = [c for c in st.session_state.gov_db if any(w in c.get("title","").lower() or c.get("sector","").lower() for w in q_lower.split())]
        copied_bp = [b for b in st.session_state.blueprint_db if any(w in b.get("title","").lower() or b.get("summary","").lower() for w in q_lower.split())]
        
        with st.chat_message("assistant"):
            st.markdown("#### 🤖 Edge Lab Integrated Synthesis Response")
            st.write("I have analyzed your query and generated a strategy map combining official national entry channels with practical economic execution blueprints:")
            
            # Column layout for dual response display
            syn_col1, syn_col2 = st.columns(2)
            
            with syn_col1:
                st.markdown("📂 **1. Official Frameworks & Compliance Paths**")
                if copied_gov:
                    for g in copied_gov[:1]:
                        st.markdown(f"**Recommended Vehicle:** {g.get('title')}")
                        st.markdown(f"* **Managing Body:** {g.get('agency')}")
                        st.markdown(f"* **Actionable Step:** {g.get('steps')}")
                        st.markdown(f"* **Statutory Fees:** `{g.get('cost')}`")
                else:
                    st.write("• Form an enterprise group at your local sub-county to align with upcoming PDM asset support allocations.")
                    st.write("• Register your unique business identity structure online via the URSB OBRS gateway.")
            
            with syn_col2:
                st.markdown("📊 **2. 'It Works. Try It.' Financial Literacy Matrix**")
                if copied_bp:
                    for b in copied_bp[:1]:
                        st.markdown(f"**Operational Target:** {b.get('title')}")
                        st.markdown(f"* **Capital Threshold:** `{b.get('capital_required')}`")
                        st.info(f"💡 **Survival Metric:** {b.get('fin_lit_tip')}")
                        st.success(f"🏆 {b.get('success_case')}")
                        st.markdown(f"🔗 Watch detailed field metrics: `{b.get('media_anchor')}`")
                else:
                    st.write("• Maintain a liquid cash cushion equivalent to 40% of setup parameters to absorb initial cyclical cash-burn variations.")
                    st.write("• Document your unit economics via digital cash-flow logs starting from day one of product cycle testing.")

# ==================================================================
# VIEW 2: CITIZEN USSD SIMULATOR 
# ==================================================================
elif view == "📟 Citizen USSD Simulator":
    st.title("USSD Feature-Phone Simulation Layer")
    st.info("💡 Simulated View: Emulating cell telco carrier text handshakes over analog frameworks.")
    
    if "ussd_string" not in st.session_state:
        st.session_state.ussd_string = ""

    col_input, col_screen = st.columns([1, 1])
    
    with col_input:
        st.subheader("Keypad Action Entry")
        current_input = st.text_input("Type your numeric choices:", value=st.session_state.ussd_string)
        st.session_state.ussd_string = current_input.strip()
        
        st.write("#### 🧭 Core Command Navigation Matrix:")
        st.markdown("""
        * Leave Blank $\rightarrow$ **Main Welcome Gateway Menu**
        * `1` $\rightarrow$ View Programs by Lifecycle Stage
        * `4` $\rightarrow$ **Launch 'It Works. Try It.' Business Blueprints Engine**
        * `4*1` $\rightarrow$ Sector 1 (Agribusiness) $\rightarrow$ Displays available operational lists
        * `4*1*1` $\rightarrow$ Displays direct cost/financial metrics for **Poultry Farms (5,000 birds)**
        """)
        if st.button("❌ Terminate Current USSD Session"):
            st.session_state.ussd_string = ""
            st.rerun()

    with col_screen:
        st.subheader("📟 Simulated Feature-Phone Screen")
        with st.container(border=True):
            raw_string = st.session_state.ussd_string
            
            if raw_string == "":
                st.code("CON Welcome to Edge Lab.\n1. Find Gov Services\n2. View Taxonomies\n3. About Hub\n4. Business Blueprints ('It Works')", language="text")
            elif raw_string == "1":
                st.code("CON Choose Lifecycle Stage:\n1. Idea Stage\n2. Startup Stage\n3. Growth Stage", language="text")
            elif raw_string == "4":
                st.code("CON Select Industry Target Sector:\n1. Agribusiness\n2. Trade & Retail\n3. Digital & ICT\n4. Manufacturing", language="text")
            elif raw_string == "4*1":
                st.code("CON Agribusiness Content Library:\n1. Poultry Setup (5,000 Birds)\n2. Coffee Cultivation Guide", language="text")
            elif raw_string == "4*1*1":
                bp = st.session_state.blueprint_db[0] # Poultry
                st.code(f"END {bp.get('title')}\nCap: {bp.get('capital_required')}\nLit Tip: Maintain 45% capital reserve backstop for feed layer cycles.", language="text")
            elif raw_string == "4*1*2":
                bp = st.session_state.blueprint_db[1] # Coffee
                st.code(f"END {bp.get('title')}\nCost: {bp.get('capital_required')}\nTip: Intercrop with short-rotation cash crops seasons 1-2.", language="text")
            elif raw_string == "4*4":
                st.code("CON Manufacturing Content Library:\n1. Urban Specialized Bakery Setup", language="text")
            elif raw_string == "4*4*1":
                bp = st.session_state.blueprint_db[2] # Bakery
                st.code(f"END {bp.get('title')}\nCap: {bp.get('capital_required')}\nTip: Use durable local steel tables; source imported deck ovens.", language="text")
            else:
                st.code("END Interface exception. Command combination string not mapped. Dial *284# to refresh parameters.", language="text")

# ==================================================================
# VIEW 3: GOVERNMENT ADMIN CMS PORTAL
# ==================================================================
elif view == "🏛️ Government Admin CMS Portal":
    st.title("Government Admin CMS & Content Management Portal")
    
    cms_tab1, cms_tab2 = st.tabs(["📝 Institutional Government Profiles", "🎬 'It Works. Try It.' Success Case Upload"])

    with cms_tab1:
        with st.form("cms_gov_form", clear_on_submit=True):
            st.markdown("### Publish Statutory Opportunity Profile Card")
            g_title = st.text_input("Program Opportunity Name:")
            g_agency = st.text_input("Managing Agency/Ministry:")
            g_stage = st.selectbox("Target Business Stage:", STAGES,
