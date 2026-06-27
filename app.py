import streamlit as st
import pandas as pd
import json
import os
import uuid

# ==================================================================
# 1. MANDATORY PAGE CONFIG (Must be the first Streamlit command run)
# ==================================================================
st.set_page_config(
    page_title="Mandem Platform",
    page_icon="🇺🇬",
    layout="wide"
)

# ==================================================================
# 🔒 TEMPORARY SECURITY LOCK GATE
# ==================================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Under Maintenance")
    st.write("This platform prototype is currently locked for updates.")
    
    # Form layout keeps the PIN input stable on mobile touchscreens
    with st.form("login_gate"):
        password_input = st.text_input("Enter Access PIN:", type="password")
        submit_clicked = st.form_submit_button("Unlock Platform")
        
        if submit_clicked:
            if password_input == "2567":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Access Denied. Invalid PIN.")
                
    st.stop()  # 🛑 Hard stop prevents anything below this line from executing
# ==================================================================

# YOUR ORIGINAL CODE (STAGES, SECTORS, AND DATA CARDS) CONTINUES SAFELY BELOW...

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
SECTORS = ["Agriculture & Agribusiness", "Trade & Retail", "Digital & ICT", "Manufacturing", "Logistics & Transport"]
CAPITAL_TIERS = ["Micro (Under UGX 5M)", "Small (UGX 5M - 20M)", "Medium/Commercial (UGX 20M+)"]

# ------------------------------------------------------------------
# 3. Dual-Database File Persistence Framework
# ------------------------------------------------------------------
GOV_DB_FILE = "gov_db.json"
BLUEPRINT_DB_FILE = "blueprint_db.json"
FEEDBACK_FILE = "feedback_log.json"

# Master Dataset 1: Refined Official Regulatory & Funding Channels
DEFAULT_GOV_DB = [
    {
        "id": "gov-pdm-001",
        "title": "Parish Agricultural Value Chain Grant Support",
        "agency": "Ministry of Local Government / PDM Secretariat",
        "stage": "Idea Stage",
        "sector": "Agriculture & Agribusiness",
        "eligibility": "Subsistence households organized inside a registered Parish Enterprise Group (PEG). 30% of entire parish fund allocations strictly reserved for Youth initiatives.",
        "cost": "Free (Zero statutory application charges across all sub-counties).",
        "steps": "1. Approach local LC1 Chairperson to verify household status. 2. Join or register a verified 10-30 member Parish Enterprise Group matching specific commodity value chains (e.g., poultry, coffee, dairy). 3. File data into the Parish Development Management Information System (PBMIS) portal via the Parish Chief. 4. Wait for vetting and subsequent direct electronic disbursement from the Parish Revolving Fund account.",
        "contacts": "Parish Chief / Sub-County PDM Desk Officer."
    },
    {
        "id": "gov-ursb-002",
        "title": "URSB OBRS Limited Liability Company Incorporation",
        "agency": "Uganda Registration Services Bureau (URSB)",
        "stage": "Startup Stage",
        "sector": "Manufacturing",
        "eligibility": "Enterprises with a minimum of two directors holding valid Ugandan National Identification Cards (NIDs) with scannable National Identification Numbers (NINs).",
        "cost": "UGX 140,000 standard baseline statutory registration assessment fees plus registration stamp duty fees.",
        "steps": "1. Access the online Online Business Registration System (OBRS) portal via obrs.ursb.go.ug. 2. Run a real-time corporate name availability lookup search and reserve your unique name. 3. Input legal profiles for directors, corporate secretaries, and shareholding percentages. 4. Generate and complete standard Form 18 (Application for Registration) and Form 20 (Notice of Appointment of Directors). 5. Upload digitized copies of the Memorandum and Articles of Association. 6. Generate an e-payment PRN token via URA portal and pay via mobile money or commercial bank.",
        "contacts": "URSB Head Office, Uganda Business Facilitation Centre (UBFC), Plot 1, Kampala Road / obrs.ursb.go.ug"
    },
    {
        "id": "gov-ura-003",
        "title": "URA Tax Identification Number (TIN) & Income Tax Compliance",
        "agency": "Uganda Revenue Authority (URA)",
        "stage": "Startup Stage",
        "sector": "Trade & Retail",
        "eligibility": "Any individual Ugandan business owner (Sole Proprietor) with a valid National ID or any registered corporate legal entity containing a certified URSB registration number.",
        "cost": "Free (Zero application fees for system issuance).",
        "steps": "1. Navigate to the official URA web portal at ura.go.ug. 2. Select the 'TIN Registration' interactive module under the e-services drop-down panel. 3. Select business structure type (Individual vs. Non-Individual corporate). 4. Populate matching personal metrics directly corresponding with NIRA database registries. 5. Map physical operating addresses, contact configurations, and business activity category codes. 6. Submit the webform to generate an instant acknowledgement receipt token. 7. Download your digital TIN certificate directly via your verified email address upon backend compliance verification.",
        "contacts": "URA Toll-Free Support line (0800117000) / Any regional URA Domestic Taxes office."
    },
    {
        "id": "gov-kcca-004",
        "title": "KCCA Municipal Trading License Acquisition",
        "agency": "Kampala Capital City Authority / Local Government Municipalities",
        "stage": "Startup Stage",
        "sector": "Trade & Retail",
        "eligibility": "Operating fixed or mobile physical commercial business premises situated within Kampala capital city borders or corresponding municipal zones.",
        "cost": "Variable scale calculated strictly on business type, sector code, and physical size parameters (Ranges from UGX 70,000 to UGX 500,000+ annually).",
        "steps": "1. Present certified copies of company incorporation documents or registered business names alongside your active URA TIN certificate. 2. Fill out the physical or online KCCA trading license application sheet. 3. Physical inspection parameters are deployed by a municipal officer to verify operations scope and calculate Grade category classification. 4. A formal assessment note is systematically processed generating a Payment Registration Number (PRN). 5. Complete payment execution. 6. Collect your official trading license sticker placard to avoid municipal enforcement lockups.",
        "contacts": "KCCA Citizen Service Centers at City Hall or Division Offices (Central, Nakawa, Makindye, Rubaga, Kawempe)."
    },
    {
        "id": "gov-grow-005",
        "title": "PSFU GROW Project Women Enterprise Loan & Grant Scheme",
        "agency": "Private Sector Foundation Uganda (PSFU) / MoGLSD",
        "stage": "Growth Stage",
        "sector": "Manufacturing",
        "eligibility": "Micro, Small, or Medium Enterprises (MSMEs) fully owned or majority-controlled by women entrepreneurs (Minimum 51% equity shareholding validation required) possessing an active trading license.",
        "cost": "Zero evaluation fees. Highly concessionary borrowing loan rates safely fixed at 10% to 12% per annum.",
        "steps": "1. Contact a participating tier-1 commercial bank partner (e.g., Centenary Bank, Stanbic Bank, DFCU Bank). 2. Present legal identification documentation proving female corporate control benchmarks. 3. Demonstrate ongoing financial operations metrics via physical storefront sales books or digital business ledgers. 4. Match social, environmental, and infrastructure safety framework benchmarks specified by the project management office. 5. Process formal loan application streams for operational capacity scale-ups or physical asset purchases.",
        "contacts": "GROW Project Secretariat Hub at PSFU House, Plot 43, Nakasero Road / grow@psfu.org.ug"
    }
]

# Master Dataset 2: Expanded "It Works. Try It." Real Ugandan Case Studies with Video Anchors
DEFAULT_BLUEPRINT_DB = [
    {
        "id": "bp-retail-001",
        "title": "Urban General Merchandise Kiosk & Fast-Moving Retail Shop",
        "sector": "Trade & Retail",
        "tier": "Micro (Under UGX 5M)",
        "capital_required": "UGX 1,500,000 - UGX 3,500,000 (Initial fast-moving stock purchase, rent deposit, security grill installations, and counter shelving)",
        "summary": "An operations blueprint for launching a high-turnover retail kiosk in dense urban neighborhoods. Outlines standard stock selection parameters (sugar, soap, cooking oil, rice) to maximize cash velocity.",
        "fin_lit_tip": "THE INVENTORY LEAK RAPID FIX: Never consume shop inventory for personal use without documenting it as a cash purchase in your ledger. Micro-retail shops fail primarily because owners blend personal daily living costs directly with store working capital float.",
        "success_case": "Case Study: Field setup blueprint detailing inventory mapping, supplier negotiations, and daily ledger protocols modeled from successful neighborhood retail startups in Kampala sub-counties.",
        "media_anchor": "📺 Video Link: https://www.youtube.com/watch?v=zpBsQAwJhQs"
    },
    {
        "id": "bp-ict-002",
        "title": "Informal Marketplace Digital Transformation Strategy",
        "sector": "Digital & ICT",
        "tier": "Micro (Under UGX 5M)",
        "capital_required": "UGX 800,000 - UGX 2,000,000 (Smart mobile handset, high-speed data allocation packages, and foundational e-commerce store onboarding registries)",
        "summary": "Step-by-step roadmap showing how informal market vendors and small-scale retailers systematically digitalize their product inventories, capture visual media logs, and fulfill orders through localized courier pipelines.",
        "fin_lit_tip": "VIRTUAL OVERHEAD RESTRICTION: Do not rent a premium physical storefront if you are testing a new product line. Use localized third-party pick-up points and direct-to-consumer social sales configurations to preserve early operational working capital.",
        "success_case": "Case Study: The UNDP Uganda & Jumia Strategic Partnership Ecosystem. A documented joint initiative that successfully transitioned hundreds of traditional market vendor structures into active, digitally visible e-commerce operators.",
        "media_anchor": "📺 Video Link: https://www.youtube.com/watch?v=8tE1I3UmanU"
    },
    {
        "id": "bp-rabbit-003",
        "title": "Commercial Rabbit Breeding & Agribusiness Enterprise",
        "sector": "Agriculture & Agribusiness",
        "tier": "Small (UGX 5M - 20M)",
        "capital_required": "UGX 5,000,000 - UGX 8,500,000 (Multi-tier breeder cages, high-yield parent stock, and specialized feed rations)",
        "summary": "Strategic blueprint for shifting from subsistence backyards to high-yield micro-livestock commercialization. Covers structural cage airflow mapping, litter waste recycling, and rapid breeding cycle execution.",
        "fin_lit_tip": "ASSET RE-INVESTMENT METRIC: Rabbits possess an accelerated breeding cycle. Do not spend initial batch revenues on personal costs. Reinvest 60% of early profits into constructing self-contained weaning cages to safely separate litters and combat high stress-induced kit mortalities.",
        "success_case": "Case Study: Swiney Tumwebaze (Mommy Rabbits Farm in Kawanda). Resigned from her professional CPA and corporate banking career to build an independent, thriving wealth engine through commercial rabbit cultivation.",
        "media_anchor": "📺 Video Link: https://www.youtube.com/watch?v=OkOejjimSNk"
    },
    {
        "id": "bp-log-004",
        "title": "Local Transport Logistics & Digital Dispatch Fleet Operation",
        "sector": "Logistics & Transport",
        "tier": "Small (UGX 5M - 20M)",
        "capital_required": "UGX 6,000,000 - UGX 15,000,000 (Asset acquisition of low-emission commuter motorcycles, digital GPS tracker implementation, and rider safety kits)",
        "summary": "Operational strategy matrix for running hyper-efficient commuter and parcel transport routes using regional digital aggregators and smart fleet tracking systems to eliminate unauthorized rider operational leakages.",
        "fin_lit_tip": "DEPRECIATION RECOVERY RESERVES: Set aside a fixed daily amortization rate from route revenues strictly into a locked digital wallet asset. Never treat gross operator remittances as spendable profit before factoring in structural parts wear and routine mechanical service intervals.",
        "success_case": "Case Study: Ronald Hakiza (Founder, Uga Bus) along with tech pioneers featured on The Ugandan Podcast detailing how local logistics solutions are built using grit, collaboration, and deep-dive community mapping.",
        "media_anchor": "📺 Video Link: https://www.youtube.com/watch?v=oK7mOWWUCFE"
    },
    {
        "id": "bp-poultry-005",
        "title": "Commercial Hass Avocado & Layers Poultry Integration",
        "sector": "Agriculture & Agribusiness",
        "tier": "Medium/Commercial (UGX 20M+)",
        "capital_required": "UGX 25,000,000 - UGX 50,000,000 (High-yield grafted Hass seedlings, deep-well irrigation setup, point-of-lay poultry cages, and initial feed arrays)",
        "summary": "A commercial dual-income agribusiness model combining poultry production with high-value export avocado cultivation. Poultry manure serves as a high-nitrogen organic nutrient base for the orchard, drastically cutting operational fertilizer input expenses.",
        "fin_lit_tip": "CROP-LIVESTOCK CASH HEDGING: Hass avocado orchards require 3 years to reach peak commercial fruiting yield. Utilize the continuous daily cash-flow generated from your layer poultry egg sales cycles to offset the capital-intensive maintenance overhead of the young orchard.",
        "success_case": "Case Study: Hon. Esther Mbayo (Luuka District). Transitioned from corporate accounting and high-level national political leadership into commercial agriculture, building a highly profitable multi-acre agribusiness matrix.",
        "media_anchor": "📺 Video Link: https://www.youtube.com/watch?v=E3bXfS1J4jk"
    },
    {
        "id": "bp-bakery-006",
        "title": "Commercial Cake Factory & Industrial Bakery Scaling",
        "sector": "Manufacturing",
        "tier": "Medium/Commercial (UGX 20M+)",
        "capital_required": "UGX 20,000,000+ (Industrial deck ovens, heavy-duty mixers, workspace sanitization buildouts, and retail distribution points)",
        "summary": "Scaling roadmap transforming a domestic kitchen side-hustle into a multi-outlet national brand. Focuses on maintaining product integrity, acquiring institutional market linkages, and training specialized culinary labor.",
        "fin_lit_tip": "CAPITAL STACKING & GRANTS: When operating a highly formal production unit, register your payroll and keep strict financial books. Clean administrative records unlock major concessionary capital streams, such as the World Bank-funded GROW project grants for women-led enterprises.",
        "success_case": "Case Study: Brenda Sekabembe Mulema (CEO, Bake 4 Me Ltd). Scaled her enterprise from a micro-kitchen into a dominant national brand with dozens of employees, earning the National Award for Women Empowerment directly from the President of Uganda.",
        "media_anchor": "📺 Video Link: https://www.youtube.com/watch?v=e0mqTJNQxUc"
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
            gov_search = st.text_input("🔍 Quick Keyword Search (e.g., 'URSB', 'Grant', 'URA', 'KCCA'):", value="")

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
                    st.markdown(f"* **Direct Contact Point:** *{card.get('contacts')}*")
                    st.write("---")
            else:
                st.caption("Adjust your structural filters above to display official ministry compliance options.")

    with w_tab2:
        col_bp1, col_bp2 = st.columns(2)
        with col_bp1:
            selected_bp_sector = st.selectbox("Filter Blueprints by Industry Sector:", ["Select Sector"] + SECTORS)
            selected_bp_tier = st.selectbox("Filter by Initial Capital Tier Budget:", ["Select Tier"] + CAPITAL_TIERS) if selected_bp_sector != "Select Sector" else "Select Tier"
        with col_bp2:
            bp_search = st.text_input("🔍 Search Concepts (e.g., 'Poultry', 'Rabbit', 'Cake', 'Logistics', 'Marketplace'):", value="")

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
                    st.markdown(f"🔗 **Production Media Anchor:** \n{bp.get('media_anchor')}")
                    st.write("---")
            else:
                st.warning("🤖 Select an industry sector and capital tier budget or type a keyword search pattern to inspect our interactive 'It Works. Try It.' production summaries.")

    # ------------------------------------------------------------------
    # Dual Synthesis Conversational Copilot Block
    # ------------------------------------------------------------------
    st.write("---")
    st.markdown("### 🤖 Edge Lab Conversational AI Copilot (Dual-Synthesis Engine)")
    st.caption("Simulated Context-Aware LLM Endpoint — Programmatically cross-referencing Official Policy with Real-World Field Blueprints.")
    
    ai_prompt = st.text_input("Ask any unstructured business question (e.g., 'I want to start a rabbit farm, how do I get funding and register my company?'):")
    
    if ai_prompt:
        q_lower = ai_prompt.lower()
        
        # Internal search simulation across both engines
        copied_gov = [c for c in st.session_state.gov_db if any(w in c.get("title","").lower() or c.get("sector","").lower() or c.get("agency","").lower() for w in q_lower.split())]
        copied_bp = [b for b in st.session_state.blueprint_db if any(w in b.get("title","").lower() or b.get("summary","").lower() or b.get("success_case","").lower() for w in q_lower.split())]
        
        with st.chat_message("assistant"):
            st.markdown("#### 🤖 Edge Lab Integrated Synthesis Response")
            st.write("I have analyzed your query and generated a strategy map combining official national entry channels with practical economic execution blueprints:")
            
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
                        st.markdown(f"🔗 Watch detailed field metrics: {b.get('media_anchor')}")
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
        * `4*1*1` $\rightarrow$ Displays metrics for **Rabbit Farming (Tumwebaze Swiney case)**
        * `4*5` $\rightarrow$ Sector 5 (Logistics) $\rightarrow$ Displays logistics infrastructure options
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
                st.code("CON Select Industry Target Sector:\n1. Agribusiness\n2. Trade & Retail\n3. Digital & ICT\n4. Manufacturing\n5. Logistics & Transport", language="text")
            elif raw_string == "4*1":
                st.code("CON Agribusiness Content Library:\n1. Commercial Rabbit Breeding\n2. Avocado & Layers Integration", language="text")
            elif raw_string == "4*1*1":
                bp = st.session_state.blueprint_db[2] # Rabbit
                st.code(f"END {bp.get('title')}\nCap: {bp.get('capital_required')}\nLit Tip: Reinvest 60% of early returns into self-contained weaning cages.", language="text")
            elif raw_string == "4*1*2":
                bp = st.session_state.blueprint_db[4] # Avocado
                st.code(f"END {bp.get('title')}\nCap: {bp.get('capital_required')}\nLit Tip: Use layer poultry egg revenue to cash-hedge avocado orchard growth.", language="text")
            elif raw_string == "4*5":
                st.code("CON Logistics Content Library:\n1. Digital Dispatch Fleet Operations", language="text")
            elif raw_string == "4*5*1":
                bp = st.session_state.blueprint_db[3] # Logistics
                st.code(f"END {bp.get('title')}\nCap: {bp.get('capital_required')}\nLit Tip: Track daily asset depreciation to avoid unmitigated fleet loss.", language="text")
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
            g_stage = st.selectbox("Target Business Stage:", STAGES, key="g_stage")
            g_sector = st.selectbox("Target Sector Taxonomy:", SECTORS, key="g_sector")
            g_eligibility = st.text_area("Who Qualifies?")
            g_cost = st.text_input("Statutory Processing Cost Baseline:")
            g_steps = st.text_area("Step-by-Step Milestones:")
            g_contacts = st.text_input("Direct Desk Contact Point:")
            
            if st.form_submit_button("🚀 Deploy to Government Registry"):
                st.session_state.gov_db.append({"id": str(uuid.uuid4())[:8], "title": g_title, "agency": g_agency, "stage": g_stage, "sector": g_sector, "eligibility": g_eligibility, "cost": g_cost, "steps": g_steps, "contacts": g_contacts})
                save_json(GOV_DB_FILE, st.session_state.gov_db)
                st.success("Statutory record live on the network infrastructure!")

    with cms_tab2:
        with st.form("cms_blueprint_form", clear_on_submit=True):
            st.markdown("### Document New Business History / Financial Blueprint")
            st.caption("Translating your active YouTube content, media field logs, and interview transcripts into accessible database formats.")
            
            b_title = st.text_input("Business Model Concept Name:", value="Commercial Goat Farming Matrix")
            b_sector = st.selectbox("Industry Classification:", SECTORS, key="b_sector")
            b_tier = st.selectbox("Capital Expenditure Tier Setup:", CAPITAL_TIERS)
            b_capital = st.text_input("Detailed Capital Breakdown (UGX):", value="UGX 14,000,000 (Fencing, breeder stock, medical kits)")
            b_summary = st.text_area("Operational Summary Framework:", value="Comprehensive layout protocols optimized for breeding high-tier meat crossbreeds in localized semi-intensive setups.")
            b_fin_lit = st.text_area("Financial Literacy Point & Risk Factor:", value="Always isolate multi-year asset purchases from periodic working capital allocations. Vet your pasture fields before heavy rains to mitigate high seasonal tick exposures.")
            b_case = st.text_area("Documented Success Case Narrative:", value="Interview log from District Farm Lead who broke even within 18 months via programmatic institutional supply contracts.")
            b_media = st.text_input("YouTube Production Identifier Link:", value="https://www.youtube.com/watch?v=XXXXXX")

            if st.form_submit_button("🎬 Publish to Content Knowledge Network"):
                st.session_state.blueprint_db.append({
                    "id": str(uuid.uuid4())[:8], "title": b_title, "sector": b_sector, "tier": b_tier,
                    "capital_required": b_capital, "summary": b_summary, "fin_lit_tip": b_fin_lit,
                    "success_case": b_case, "media_anchor": b_media
                })
                save_json(BLUEPRINT_DB_FILE, st.session_state.blueprint_db)
                st.success(f"🎉 Success! '{b_title}' has been vectorized into the digital library ecosystem.")

    st.write("---")
    st.markdown("### 📋 Active Content Registries Summary")
    exp_gov, exp_bp = st.columns(2)
    with exp_gov:
        st.subheader("Official Government Registry")
        for c in st.session_state.gov_db:
            with st.expander(f"🏛️ {c.get('title')}"):
                st.write(f"Agency: {c.get('agency')}")
                if st.button("Delete Statutory Entry", key=f"del_g_{c['id']}"):
                    st.session_state.gov_db = [i for i in st.session_state.gov_db if i["id"] != c["id"]]
                    save_json(GOV_DB_FILE, st.session_state.gov_db)
                    st.rerun()
    with exp_bp:
        st.subheader("Published Content Blueprints")
        for b in st.session_state.blueprint_db:
            with st.expander(f"🎬 {b.get('title')}"):
                st.write(f"Tier: {b.get('tier')} | Capital: {b.get('capital_required')}")
                if st.button("Delete Content Record", key=f"del_b_{b['id']}"):
                    st.session_state.blueprint_db = [i for i in st.session_state.blueprint_db if i["id"] != b["id"]]
                    save_json(BLUEPRINT_DB_FILE, st.session_state.blueprint_db)
                    st.rerun()

# ==================================================================
# VIEW 4: GOV INTELLIGENCE DASHBOARD
# ==================================================================
elif view == "📊 Gov Intelligence Dashboard":
    st.title("National MSME Demand Intelligence Matrix")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Platform Hits (WhatsApp + USSD)", "24,810", "+22% this week")
    col2.metric("Most Searched Concept", "Rabbit Farming & Agribusiness", "6,140 unique pings")
    col3.metric("Video Redirection Click-Throughs", "4,950 views redirected", "74% Engagement Rate")

    st.write("---")
    st.subheader("Aggregated Analytics Overview")
    chart_data = pd.DataFrame({
        'Agribusiness Blueprints': [4200, 5100, 6800],
        'Logistics & Transport': [1200, 1800, 3400],
        'Official Gov Compliance Inquiries': [1900, 2400, 5900]
    }, index=['Western Region', 'Northern Region', 'Central Region (Kampala)'])
    st.line_chart(chart_data)
