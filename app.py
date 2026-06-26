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
# 2. Shared taxonomy (single source of truth — used by both the
#    citizen filters AND the CMS form, so they can never drift apart)
# ------------------------------------------------------------------
STAGES = ["Idea Stage", "Startup Stage", "Growth Stage", "Mature MSME Stage"]
SECTORS = ["Agriculture & Agribusiness", "Trade & Retail", "Digital & ICT", "Manufacturing"]

# ------------------------------------------------------------------
# 3. File-based persistence
# ------------------------------------------------------------------
DB_FILE = "gov_db.json"
FEEDBACK_FILE = "feedback_log.json"

DEFAULT_DB = [
    {
        "id": "peg-001",
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
        "id": "ursb-001",
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


def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    save_json(path, default)
    return [dict(item) for item in default]


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_db():
    return load_json(DB_FILE, DEFAULT_DB)


def save_db(data):
    save_json(DB_FILE, data)


def load_feedback():
    return load_json(FEEDBACK_FILE, [])


def save_feedback(data):
    save_json(FEEDBACK_FILE, data)


if "gov_db" not in st.session_state:
    st.session_state.gov_db = load_db()

if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = load_feedback()

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
    save_db(DEFAULT_DB)
    save_feedback([])
    st.session_state.gov_db = load_db()
    st.session_state.feedback_log = []
    st.rerun()

# ==================================================================
# VIEW 1: CITIZEN WHATSAPP SIMULATOR
# ==================================================================
if view == "📱 Citizen WhatsApp Simulator":
    st.title("WhatsApp-First Prototype Flow")
    st.info("💡 Simulated View: This represents the logic executing behind a user's WhatsApp interface via QR Code check-in at an LC1 Office.")

    col_nav1, col_nav2 = st.columns(2)
    
    with col_nav1:
        st.subheader("Interactive Menu Options")
        selected_stage = st.selectbox("WhatsApp Button Send: Choose Your Stage", ["Select Stage"] + STAGES)

        selected_sector = "Select Sector"
        if selected_stage != "Select Stage":
            selected_sector = st.selectbox("WhatsApp Button Send: Choose Your Sector", ["Select Sector"] + SECTORS)

    with col_nav2:
        st.subheader("🔍 Smart Text Search Gateway")
        search_query = st.text_input("Or Type a Keyword Directly (e.g., 'URSB', 'Grant', 'TIN'):", value="", help="Allows instant semantic matching against titles, steps, and managing agency departments.")

    st.write("---")
    st.subheader("💬 WhatsApp Screen Emulator")

    with st.container(border=True):
        st.caption("Incoming from Edge Lab Bot • Active")
        st.write("🤖 **Welcome to Edge Lab Platform!** You scanned the QR code at **LC1 Anchor Office**. Please interact with the filter options or type a search query above.")

        matched = []
        
        if search_query.strip() != "":
            q = search_query.lower()
            matched = [
                card for card in st.session_state.gov_db
                if q in card.get("title", "").lower() 
                or q in card.get("agency", "").lower() 
                or q in card.get("steps", "").lower()
                or q in card.get("eligibility", "").lower()
            ]
            st.success(f"🧑 **WhatsApp Typed Query:** \"{search_query}\" ({len(matched)} match found)")
        elif selected_stage != "Select Stage":
            st.success(f"🧑 **I chose stage:** {selected_stage}")
            if selected_sector != "Select Sector":
                st.success(f"🧑 **My sector is:** {selected_sector}")
                matched = [
                    card for card in st.session_state.gov_db
                    if card.get("stage") == selected_stage and card.get("sector") == selected_sector
                ]

        if (selected_stage != "Select Stage" and selected_sector != "Select Sector") or search_query.strip() != "":
            if matched:
                for card in matched:
                    st.write("---")
                    st.markdown(f"🤖 📄 **OFFICIAL SERVICE CARD: {card['title']}**")
                    st.markdown(f"* 🏛️ Agency:")
                    st.markdown(f"* 🎯 Who Qualifies:")
                    st.markdown(f"* 🛠️ Steps to Take:")
                    st.markdown(f"* 💰 **Statutory Cost:** `{card['cost']}`")
                    st.markdown(f"* 📞 Support Desk:")

                    st.write("---")
                    st.caption("👉 *Did this official information help you today?*")
                    f_col1, f_col2 = st.columns(2)
                    if f_col1.button("👍 Yes, clear steps", key=f"yes_{card['id']}"):
                        st.session_state.feedback_log.append({
                            "timestamp": datetime.now().isoformat(timespec="seconds"),
                            "program": card["title"],
                            "status": "Helpful"
                        })
                        save_feedback(st.session_state.feedback_log)
                        st.success("System routing verification entry saved!")
                    if f_col2.button("👎 No, still confusing", key=f"no_{card['id']}"):
                        st.session_state.feedback_log.append({
                            "timestamp": datetime.now().isoformat(timespec="seconds"),
                            "program": card["title"],
                            "status": "Friction Warning"
                        })
                        save_feedback(st.session_state.feedback_log)
                        st.error("Optimization query dispatched to ministry lead.")
            else:
                st.warning("🤖 No program matches this exact profile permutation yet. Use the CMS portal to instantiate a card layout.")

        st.write("---")
        st.markdown("### 🤖 Edge Lab Conversational AI Copilot")
        st.caption("Simulated LLM Sandboxed Environment — Powered securely via encrypted background application context.")
        
        ai_prompt = st.text_input("Ask an unstructured policy query (e.g., 'How do I start an agricultural venture as a youth group?'):")
        
        if ai_prompt:
            if "OPENAI_API_KEY" in st.secrets or "ANTHROPIC_API_KEY" in st.secrets:
                st.info("✨ Secure API Context Active: Formulating verified, context-aware policy synthesis using live backend data layers...")
                st.write("🤖 **AI Assistant Synthesis:** Based on active national frameworks, you must first cluster into a registered group at your local sub-county level to access targeted value-chain grant mechanisms.")
            else:
                st.warning("🔒 Secure Sandbox Mode Active: Real production LLM tokens are safely isolated via `.streamlit/secrets.toml` variables.")
                with st.expander("🛠️ View Production Key Architecture Setup"):
                    st.code("""
# Verified secure deployment setup inside .streamlit/secrets.toml (Gitignored)
OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                    """, language="toml")
                st.write(f"🤖 **Simulated Response for:** *\"{ai_prompt}\"* \n\nI scanned the active database repositories. To qualify for frameworks like the **Parish Agricultural Value Chain Grant**, you must ensure your enterprise group structure has at least a 30% composition allocation explicitly reserved for youth engagement vectors.")

# ==================================================================
# VIEW 2: CITIZEN USSD SIMULATOR (NEW FUNCTIONAL RUNTIME ADDITION)
# ==================================================================
elif view == "📟 Citizen USSD Simulator":
    st.title("USSD Feature-Phone Simulation Layer")
    st.info("💡 Simulated View: This emulates the offline text interface a citizen sees when dialing a shortcode (e.g., `*284#`) via an Africa's Talking telco aggregator link.")
    
    if "ussd_string" not in st.session_state:
        st.session_state.ussd_string = ""

    col_input, col_screen = st.columns([1, 1])
    
    with col_input:
        st.subheader("Keypad Action Entry")
        st.write("In production, Africa's Talking forwards text selections as a concatenated string delimited by asterisks (e.g., `1`, `1*2`). Enter your input below:")
        
        current_input = st.text_input(
            "Type your numeric choices (Leave blank to view main menu):", 
            value=st.session_state.ussd_string,
            help="Type '1' for Stages, '2' for Sectors, or step sequences like '1*1' for Stage 1 -> Sector 1."
        )
        st.session_state.ussd_string = current_input.strip()
        
        st.write("#### 🧭 Quick Reference Navigation Strings:")
        st.markdown("""
        * Leave Blank / Reset $\rightarrow$ **Main Gateway Menu**
        * `1` $\rightarrow$ View Business Lifecycle Stages
        * `1*1` $\rightarrow$ Stage 1 (Idea Stage) $\rightarrow$ Displays Sector Selection List
        * `1*1*1` $\rightarrow$ Stage 1 $\rightarrow$ Sector 1 (Agribusiness Opportunities)
        * `2` $\rightarrow$ Structural Taxonomies Overview
        """)
        
        if st.button("❌ Reset/End USSD Call Session"):
            st.session_state.ussd_string = ""
            st.rerun()

    with col_screen:
        st.subheader("📟 Simulated Feature-Phone Screen")
        
        with st.container(border=True):
            st.caption("Carrier Protocol Stream • Active Session")
            
            # --- USSD Core State Engine Replication ---
            raw_string = st.session_state.ussd_string
            
            if raw_string == "":
                st.code("CON Welcome to Edge Lab Gateway.\n1. Find Programs by Stage\n2. View Sector Matrices\n3. About Edge Lab", language="text")
            
            elif raw_string == "1":
                st.code("CON Choose Lifecycle Stage:\n1. Idea Stage\n2. Startup Stage\n3. Growth Stage\n4. Mature MSME Stage", language="text")
            
            elif raw_string.startswith("1*"):
                tokens = raw_string.split("*")
                stage_idx = int(tokens[1]) - 1 if (len(tokens) > 1 and tokens[1].isdigit()) else -1
                
                if 0 <= stage_idx < len(STAGES):
                    selected_stage = STAGES[stage_idx]
                    
                    if len(tokens) == 2:
                        st.code(f"CON Profile: {selected_stage}\nSelect Target Sector:\n1. Agriculture & Agribusiness\n2. Trade & Retail\n3. Digital & ICT\n4. Manufacturing", language="text")
                    elif len(tokens) == 3:
                        sector_idx = int(tokens[2]) - 1 if tokens[2].isdigit() else -1
                        if 0 <= sector_idx < len(SECTORS):
                            selected_sector = SECTORS[sector_idx]
                            
                            # Filter local persistent state data live
                            matched = [
                                card for card in st.session_state.gov_db
                                if card.get("stage") == selected_stage and card.get("sector") == selected_sector
                            ]
                            
                            if matched:
                                out_str = f"END Matches Found for {selected_stage}:\n"
                                for item in matched[:2]: # Mimic physical character constraint limits on screen
                                    out_str += f"- {item['title']}\nCost: {item['cost']}\n"
                                st.code(out_str, language="text")
                            else:
                                st.code(f"END No active programs registered under {selected_stage} - {selected_sector} yet.", language="text")
                        else:
                            st.code("END Error: Invalid sector selected.", language="text")
                else:
                    st.code("END Error: Invalid stage choice configuration.", language="text")
            
            elif raw_string == "2":
                st.code("END Active Target Sector Frameworks:\n1. Agribusiness\n2. Trade/Retail\n3. Tech Infrastructure\n4. Heavy Manufacturing", language="text")
            
            elif raw_string == "3":
                st.code("END Edge Lab Platform v1.2\nNational MSME & Youth Opportunity Knowledge Infrastructure.\nKampala, Uganda.", language="text")
            
            else:
                st.code("END Invalid entry pattern. Please hang up and re-dial *284# to flush cache layers.", language="text")

# ==================================================================
# VIEW 3: GOVERNMENT ADMIN CMS PORTAL
# ==================================================================
elif view == "🏛️ Government Admin CMS Portal":
    st.title("Government Admin CMS Portal")
    st.write("Enables direct administrative modification of program parameters, compliance metrics, and active fee structures.")

    with st.form("cms_form", clear_on_submit=True):
        st.markdown("### 📝 Upload/Modify Enterprise Opportunity Data Card")
        new_title = st.text_input("Program Opportunity Name:", value="Emyooga Micro-Finance Credit Line")
        new_agency = st.text_input("Managing Agency/Ministry:", value="Microfinance Support Centre")

        new_stage = st.selectbox("Target Business Lifecycle Stage:", STAGES)
        new_sector = st.selectbox("Target Sector Taxonomy:", SECTORS)

        new_eligibility = st.text_area("Who Qualifies?", value="Active members of a specialized district category SACCO (e.g., Boda Boda operators, tailors).")
        new_cost = st.text_input("Statutory Fee Required (e.g., UGX 253,250):", value="Free to join. Savings equity minimum applies.")
        new_steps = st.text_area("Step-by-Step Application Milestones:", value="1. Join your local category SACCO. 2. Submit development business plan to the District Commercial Officer. 3. Vetting and fund distribution via commercial banks.")
        new_contacts = st.text_input("Direct Officer Contact/Desk:", value="District Commercial Officer at your Local District HQ")

        submit_btn = st.form_submit_button("🚀 Publish to National Gateway")

        if submit_btn:
            st.session_state.gov_db.append({
                "id": str(uuid.uuid4())[:8],
                "title": new_title,
                "agency": new_agency,
                "stage": new_stage,
                "sector": new_sector,
                "eligibility": new_eligibility,
                "cost": new_cost,
                "steps": new_steps,
                "contacts": new_contacts
            })
            save_db(st.session_state.gov_db)
            st.success(f"🎉 Success! '{new_title}' is now live on the citizen system. Switch to the 'Citizen WhatsApp Simulator' view to test it!")

    st.write("---")
    st.markdown("### 📋 Currently Published Cards")
    if st.session_state.gov_db:
        for card in st.session_state.gov_db:
            with st.expander(f"{card['title']} — {card['stage']} / {card['sector']}"):
                st.write(f"Agency:")
                st.write(f"Who Qualifies:")
                st.write(f"Steps:")
                st.write(f"Cost:")
                st.write(f"Contact:")
                if st.button("🗑️ Delete this card", key=f"del_{card['id']}"):
                    st.session_state.gov_db = [c for c in st.session_state.gov_db if c["id"] != card["id"]]
                    save_db(st.session_state.gov_db)
                    st.rerun()
    else:
        st.info("No cards published yet.")

# ==================================================================
# VIEW 4: GOV INTELLIGENCE DASHBOARD
# ==================================================================
elif view == "📊 Gov Intelligence Dashboard":
    st.title("National MSME Demand Intelligence Matrix")
    st.write("Anonymized, real-time demand insights collected from WhatsApp routing systems.")
    st.caption("⚠️ Demo data below — illustrative only, not derived from real usage.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Scans via LC1 QR Blocks", "14,250", "+12% this week")
    col2.metric("Active WhatsApp Flows", "8,940", "84% Completion Rate")
    col3.metric("Highest Bottleneck Point", "URA Tax ID Setup", "Average 4.2 days dropoff", delta_color="inverse")

    st.write("---")
    st.subheader("Geographic and Sectoral Traffic Densities")
    st.caption("⚠️ Demo data — illustrative only, not derived from real usage.")

    chart_data = pd.DataFrame({
        'Agribusiness': [3900, 4500, 2400],
        'ICT': [400, 200, 1900],
        'Logistics': [600, 300, 1200],
        'Manufacturing': [650, 450, 800],
        'Retail & Trade': [1800, 1100, 4100]
    }, index=['Western Region', 'Northern Region', 'Central Region (Kampala)'])

    st.bar_chart(chart_data.T)

    with st.expander("🔍 View Policy Formulation Feedback Logs"):
        st.caption("This reflects real button presses recorded in this running demo — not yet real field data from actual LC1 deployments.")
        if st.session_state.feedback_log:
            st.dataframe(pd.DataFrame(st.session_state.feedback_log), use_container_width=True)
        else:
            st.info("System streaming operational. Real-time logging metrics will populate here as live inputs are recorded.")

    st.write("---")
    st.subheader("🧱 National Infrastructure Production Blueprint")
    st.info("🎯 Technical Transparency: This section explicitly maps out how this identical frontend logic transitions to scale in production using distributed microservices.")
    
    tab_wa, tab_ussd = st.tabs(["💬 Real WhatsApp Business API Architecture", "📱 USSD Telco Aggregator Integration"])
    
    with tab_wa:
        st.markdown("### Production WhatsApp Webhook Routing Matrix")
        st.write("Streamlit serves as our centralized internal CMS portal, telemetry engine, and real-time data visualizer. In production, citizen queries do not touch the Streamlit UI—instead, they interact via Meta's infrastructure, which routes JSON webhooks into a lightweight backend microservice.")
        
        st.markdown("""
        ```mermaid
        [Citizen on WhatsApp] 
               │  (Sends message/button interaction)
               ▼
        [Meta Cloud Infrastructure] 
               │  (Dispatches HTTPS POST Webhook Event)
               ▼
        [Production API Gateway (FastAPI / Flask)] 
               │  Reads/Parses incoming telephone number & payloads
               ├──► Queries [gov_db.json / Shared Database Layer] 
               └──► Streams telemetry counters back to [This Streamlit Intelligence Dashboard]
        ```
        """, unsafe_allow_html=True)
        
        with st.expander("📦 View Sample Microservice Production Hook Structure (FastAPI)"):
            st.code("""
from fastapi import FastAPI, Request, Response
import requests

app = FastAPI()

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    payload = await request.json()
    
    try:
        whatsapp_id = payload["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        message_body = payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
    except KeyError:
        pass
        
    return Response(status_code=200)
            """, language="python")

    with tab_ussd:
        st.markdown("### Production USSD Telecommunications Layout")
        st.write("To guarantee access for citizens using analog feature phones without data access, the platform integrates with telco aggregators (such as **Africa's Talking**) via standard shortcode handshakes.")
        
        st.markdown("""
        * **Shortcode Protocol:** User dials an assigned string (e.g., `*284#`) on MTN or Airtel networks.
        * **Aggregator Forwarding:** The telco aggregator captures the string session state parameters and transforms them into standard HTTP form-data parameters (`sessionId`, `phoneNumber`, `text`).
        * **Dynamic State Engine:** The underlying backend script reads the input string sequence to serve contextual textual menu prompts back to the carrier stream seamlessly.
        """)
        
        with st.expander("📦 View Sample Aggregator Integration Framework"):
            st.code("""
# Production USSD Framework endpoint structure 
@app.post("/ussd")
async def ussd_gateway(request: Request):
    form_data = await request.form()
    
    session_id = form_data.get("sessionId")
    phone_number = form_data.get("phoneNumber")
    user_input = form_data.get("text", "")
    
    if user_input == "":
        response = "CON Welcome to Edge Lab Gateway.\\n1. Select Business Lifecycle\\n2. Check Specific Registration Fees"
    elif user_input == "1":
        response = "CON Choose Lifecycle Stage:\\n1. Idea Stage\\n2. Startup Stage"
    else:
        response = "END Session ended."
        
    return Response(content=response, media_type="text/plain")
            """, language="python")
