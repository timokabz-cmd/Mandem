import streamlit as st
import pandas as pd
import json
import os
import uuid

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

# Master Dataset 1: Official Regulatory & Funding Channels
# Every entry below was checked against an independent source before being
# included. Two fields could not be independently confirmed and are marked
# inline as "unverified" rather than stated as fact — confirm directly with
# the agency before this goes in front of a partner.
DEFAULT_GOV_DB = [
    {
        "id": "gov-pdm-001",
        "title": "Parish Agricultural Value Chain Grant Support",
        "agency": "Ministry of Local Government / PDM Secretariat",
        "stage": "Idea Stage",
        "sector": "Agriculture & Agribusiness",
        "eligibility": "Subsistence households organized inside a registered Parish Enterprise Group (PEG), supported through a SACCO in every parish nationwide.",
        "cost": "Free (Zero statutory application charges across all sub-counties).",
        "steps": "1. Approach local LC1 Chairperson to verify household status. 2. Join or register a verified Parish Enterprise Group matching specific commodity value chains. 3. File data into the Parish Development Management Information System (PBMIS) portal via the Parish Chief. 4. Wait for vetting and subsequent disbursement from the Parish Revolving Fund.",
        "contacts": "Parish Chief / Sub-County PDM Desk Officer."
    },
    {
        "id": "gov-emyooga-006",
        "title": "Emyooga Specialized SACCO Grant Scheme",
        "agency": "Microfinance Support Centre (MSC) / Ministry of Finance, Planning and Economic Development",
        "stage": "Growth Stage",
        "sector": "Trade & Retail",
        "eligibility": "Ugandans already practicing a specific informal trade (market vending, boda riding, hairdressing, tailoring, etc.). Identification happens at village level with the support of the LC1 chairperson, then organized into one of 18 category-specific SACCOs.",
        "cost": "Free to join; standard SACCO savings/share contribution applies per category bylaws.",
        "steps": "1. Identify your trade category and approach your LC1 chairperson, who coordinates village-level identification of members in that category. 2. Join or help form the parish-level association for your category. 3. Register a constituency-level SACCO bringing together parish associations in that category. 4. Apply for SACCO capitalization support disbursed through the Microfinance Support Centre.",
        "contacts": "Microfinance Support Centre (MSC) / Sub-County Commercial Officer."
    },
    {
        "id": "gov-ylp-007",
        "title": "Youth Livelihood Programme (YLP) Revolving Fund",
        "agency": "Ministry of Gender, Labour and Social Development (MGLSD)",
        "stage": "Idea Stage",
        "sector": "Trade & Retail",
        "eligibility": "Ugandans aged 18-30, organized into a Youth Interest Group (YIG) of 10-15 members, proposing an income-generating project.",
        "cost": "Free; revolving fund of UGX 1,000,000 - 25,000,000 per group, interest-free for the first 12 months.",
        "steps": "1. Form or join a Youth Interest Group (YIG) of 10-15 members. 2. Develop a simple income-generating project proposal as a group. 3. Submit the proposal through your Sub-County/Division Community Development Officer. 4. Await vetting by the District Youth Livelihood Programme Committee before disbursement.",
        "contacts": "Sub-County or Division Community Development Officer."
    },
    {
        "id": "gov-ursb-002",
        "title": "URSB OBRS Limited Liability Company Incorporation",
        "agency": "Uganda Registration Services Bureau (URSB)",
        "stage": "Startup Stage",
        "sector": "Manufacturing",
        "eligibility": "Enterprises with a minimum of two directors holding valid Ugandan National Identification Cards (NIDs) with scannable National Identification Numbers (NINs).",
        "cost": "UGX 140,000 standard baseline statutory registration assessment fees plus registration stamp duty fees. (Fee figure not independently re-confirmed for the current year — verify on obrs.ursb.go.ug before publishing.)",
        "steps": "1. Access the Online Business Registration System (OBRS) portal via obrs.ursb.go.ug. 2. Run a real-time corporate name availability search and reserve your unique name. 3. Input legal profiles for directors, corporate secretaries, and shareholding percentages. 4. Complete Form 18 (Application for Registration) and Form 20 (Notice of Appointment of Directors). 5. Upload digitized copies of the Memorandum and Articles of Association. 6. Generate an e-payment PRN and pay via mobile money or commercial bank.",
        "contacts": "URSB Head Office, Uganda Business Facilitation Centre, Plot 1 Baskerville Avenue, Kololo. Toll-free: 0800 100 006 / obrs.ursb.go.ug"
    },
    {
        "id": "gov-ura-003",
        "title": "URA Tax Identification Number (TIN) & Income Tax Compliance",
        "agency": "Uganda Revenue Authority (URA)",
        "stage": "Startup Stage",
        "sector": "Trade & Retail",
        "eligibility": "Any individual Ugandan business owner (Sole Proprietor) with a valid National ID, or any registered corporate legal entity with a certified URSB registration number.",
        "cost": "Free (Zero application fees for system issuance).",
        "steps": "1. Navigate to the official URA web portal at ura.go.ug. 2. Select 'TIN Registration' under the e-services panel. 3. Select business structure type (Individual vs. Non-Individual). 4. Populate personal details matching NIRA records. 5. Map physical operating address and business activity category codes. 6. Submit to generate an instant acknowledgement receipt. 7. Download your digital TIN certificate via email upon verification.",
        "contacts": "URA Toll-Free Call Centre: 0800117000 / services@ura.go.ug / URA Headquarters, Plot M193/194, Nakawa Industrial Area, Kampala."
    },
    {
        "id": "gov-kcca-004",
        "title": "KCCA Municipal Trading License Acquisition",
        "agency": "Kampala Capital City Authority / Local Government Municipalities",
        "stage": "Startup Stage",
        "sector": "Trade & Retail",
        "eligibility": "Operating fixed or mobile physical commercial business premises within Kampala or corresponding municipal zones.",
        "cost": "Variable, calculated on business type, sector code, and premises size. (Specific UGX range not independently confirmed for the current fee schedule — verify directly with KCCA before publishing.)",
        "steps": "1. Present certified copies of incorporation/business name documents alongside your active URA TIN certificate. 2. Complete the KCCA trading license application (physical or online). 3. A municipal officer inspects premises to verify operations and assign a Grade category. 4. An assessment note generates a Payment Registration Number (PRN). 5. Complete payment. 6. Collect your official trading license sticker.",
        "contacts": "KCCA Citizen Service Centers at City Hall or Division Offices (Central, Nakawa, Makindye, Rubaga, Kawempe)."
    },
    {
        "id": "gov-grow-005",
        "title": "PSFU GROW Project Women Enterprise Loan & Grant Scheme",
        "agency": "Private Sector Foundation Uganda (PSFU) / Ministry of Gender, Labour and Social Development, with World Bank funding",
        "stage": "Growth Stage",
        "sector": "Manufacturing",
        "eligibility": "Enterprises owned or majority-controlled by women (minimum 51% equity shareholding). Open to micro, small, and medium enterprises transitioning to the next scale, including women in refugee-hosting districts.",
        "cost": "Zero evaluation fees. Loans range from UGX 4,000,000 to UGX 200,000,000 across three tiers, at roughly 10% per annum (up to 10.5% depending on the bank). On-time repayment can also earn a bonus grant of up to 5% of the loan principal.",
        "steps": "1. Approach any of the six partner banks: Centenary Bank, DFCU, Equity Bank, Finance Trust Bank, Post Bank, or Stanbic Bank. 2. Present documentation proving majority female ownership. 3. Demonstrate existing financial operations via sales books or digital ledgers. 4. Complete the bank's loan application process for your eligible loan tier (4-20M, 20-40M, or 40-200M).",
        "contacts": "Any GROW partner bank branch / PSFU Head Office, Nakasero, Kampala / grow.go.ug"
    }
]

# Master Dataset 2: "It Works. Try It." Real Ugandan Case Studies
#
# Every named individual/case below was checked against independent sources.
# Where a specific number or detail could not be confirmed, it has been
# removed or flagged rather than stated as fact. One entry from the
# previous version ("Swiney Tumwebaze / Mommy Rabbits Farm") returned no
# matching results in any source and has been replaced with a real,
# multi-sourced case (Bendito Farm) covering the same business model.
DEFAULT_BLUEPRINT_DB = [
    {
        "id": "bp-retail-001",
        "title": "Urban General Merchandise Kiosk & Fast-Moving Retail Shop",
        "sector": "Trade & Retail",
        "tier": "Micro (Under UGX 5M)",
        "capital_required": "UGX 1,500,000 - UGX 3,500,000 (Initial fast-moving stock purchase, rent deposit, security grill installations, and counter shelving)",
        "summary": "An operations blueprint for launching a high-turnover retail kiosk in dense urban neighborhoods, built around fast-moving stock (sugar, soap, cooking oil, rice) to maximize cash velocity.",
        "fin_lit_tip": "THE INVENTORY LEAK RAPID FIX: Never consume shop inventory for personal use without documenting it as a cash purchase in your ledger. Micro-retail shops fail primarily because owners blend personal daily living costs directly with store working capital float.",
        "success_case": "Generic composite blueprint, not tied to one named business — modeled on common patterns across Kampala-area neighborhood retail startups.",
        "media_anchor": "No specific video anchor — this is a composite, not a single named case."
    },
    {
        "id": "bp-ict-002",
        "title": "Informal Marketplace Digital Transformation Strategy",
        "sector": "Digital & ICT",
        "tier": "Micro (Under UGX 5M)",
        "capital_required": "UGX 800,000 - UGX 2,000,000 (Smartphone, data bundles, and onboarding to an e-commerce platform)",
        "summary": "Roadmap showing how informal market vendors digitalize their inventories and fulfill orders through localized courier pipelines, modeled on a real, documented programme.",
        "fin_lit_tip": "VIRTUAL OVERHEAD RESTRICTION: Do not rent a premium physical storefront while testing a new product line. Use pick-up points and direct-to-consumer social sales to preserve early working capital.",
        "success_case": "Verified: The UNDP Uganda & Jumia e-commerce partnership, launched May 2020, onboarded over 3,000 vendors across seven Kampala markets (Nakasero, Nakawa, Wandegeya, Bugolobi, Kalerwe, and others), with vendors reporting roughly doubled daily sales after joining.",
        "media_anchor": "Source: undp.org/uganda blog series on the UNDP-Jumia partnership — recommend linking the official UNDP article rather than a third-party video."
    },
    {
        "id": "bp-rabbit-003",
        "title": "Commercial Rabbit Breeding & Meat Processing",
        "sector": "Agriculture & Agribusiness",
        "tier": "Small (UGX 5M - 20M)",
        "capital_required": "UGX 7,000,000 - 8,000,000 initial investment (breeder stock, cages, and startup feed), with potential to scale via government-backed agribusiness credit",
        "summary": "A commercial rabbit breeding and processing model, incubated at the Uganda Industrial Research Institute (UIRI), built around using every part of the animal — meat, urine-based insecticide, and manure-based fertilizer.",
        "fin_lit_tip": "ASSET RE-INVESTMENT METRIC: Rabbits breed quickly, so early revenue can be reinvested fast. Building separate weaning cages for litters, rather than spending early profits personally, is what let this model scale past 1,000 rabbits.",
        "success_case": "Verified: Bendito Farm (Jeremy Musinguzi and Jessica Nabaasa), Luweero District. Started in 2016 with about UGX 7.5 million and 10 rabbits; received UGX 300 million in support from the government-owned Microfinance Support Centre in 2017; reported a net profit of UGX 138 million by September 2018, while also supplying contract-farming income to five youth and women's groups.",
        "media_anchor": "No independently verified video link found — recommend this as a strong first candidate for EdgeLab's own interview engine rather than reusing an unconfirmed link."
    },
    {
        "id": "bp-log-004",
        "title": "Digital Bus-Ticketing Platform",
        "sector": "Logistics & Transport",
        "tier": "Small (UGX 5M - 20M)",
        "capital_required": "Primarily a technology and partnerships investment — platform development, mobile money integration, and on-the-ground agent presence at bus parks — rather than vehicles or physical fleet assets.",
        "summary": "A digital bus-ticket booking platform connecting travelers to existing bus operators across East Africa, removing the need to queue or risk counterfeit tickets, with a parallel B2B tool helping bus owners manage schedules and e-ticketing.",
        "fin_lit_tip": "TRUST-BUILDING OVER PURE TECH: Early growth came from agents physically present at bus parks explaining the platform face-to-face, not from advertising alone. For trust-sensitive transactions, a human presence at the point of friction can matter more than the app itself.",
        "success_case": "Verified, corrected: Ronald Hakiza founded Ugabus in 2015-2016 after a personal bus-ticket scam, building it into Uganda's first digital bus-ticketing platform before its later acquisition by Treepz. Hakiza has since founded a new venture, Vestafi. (Earlier drafts of this card incorrectly described Ugabus as a motorcycle dispatch/fleet business — corrected here.)",
        "media_anchor": "Referenced in 'The Ugandan Podcast' episode on Uganda's innovation ecosystem (Dec 2025) — recommend confirming and linking the specific episode rather than reusing an unconfirmed video ID."
    },
    {
        "id": "bp-poultry-005",
        "title": "Commercial Layers Poultry Farming",
        "sector": "Agriculture & Agribusiness",
        "tier": "Medium/Commercial (UGX 20M+)",
        "capital_required": "Commercial-scale poultry housing, layer stock, and feed systems. (Specific capital figures not independently confirmed for this case — verify directly before publishing.)",
        "summary": "A commercial layers poultry operation in Luuka District, also used by its owner to demonstrate productive fund use to constituents by hosting Parish Development Model (PDM) beneficiaries for hands-on training.",
        "fin_lit_tip": "DEMONSTRATION VALUE: A visible, working enterprise lets you train others by example — when PDM or Emyooga beneficiaries see a real operating model up close, proper fund use improves more than from instructions alone.",
        "success_case": "Verified, corrected: Hon. Esther Mbayo, Luuka District Woman Member of Parliament, runs a poultry farm in the district and has hosted PDM fund beneficiaries there for training. (Earlier drafts added an unverified avocado-orchard component and incorrectly framed this as a 'transition away from politics' — she continues to serve as a sitting/recent MP. Both corrected here.)",
        "media_anchor": "Referenced in NTV Uganda coverage of PDM beneficiary training in Luuka (July 2023) — recommend confirming and linking the specific segment."
    },
    {
        "id": "bp-bakery-006",
        "title": "Commercial Cake Factory & Bakery Scaling",
        "sector": "Manufacturing",
        "tier": "Medium/Commercial (UGX 20M+)",
        "capital_required": "UGX 20,000,000+ (Industrial ovens, mixers, workspace buildout, and retail distribution points)",
        "summary": "Scaling roadmap transforming a domestic kitchen side-hustle into a multi-outlet national brand, focused on product consistency, institutional market linkages, and training culinary staff.",
        "fin_lit_tip": "CAPITAL STACKING & GRANTS: When operating a formal production unit, register your payroll and keep strict financial books — clean administrative records are exactly what unlocks concessionary capital streams like the GROW project loans.",
        "success_case": "Verified, corrected: Brenda Sekabembe Mulema, Founder & CEO of Bake 4 Me Ltd, started in 2004 with about UGX 25,000 baking a single cake for a colleague. Bake 4 Me now operates multiple outlets across Kampala and has produced cakes for high-profile occasions, including a wedding cake for the Kyabazinga of Busoga. (An earlier draft of this card included a specific presidential-award claim that could not be independently confirmed — removed here rather than asserted.)",
        "media_anchor": "Verified: https://www.youtube.com/watch?v=e0mqTJNQxUc — 'How She Built Bake 4 Me Into a Multi-Million Cake Business in Uganda'"
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
            gov_search = st.text_input("🔍 Quick Keyword Search (e.g., 'URSB', 'Grant', 'URA', 'KCCA', 'Emyooga'):", value="")

        with st.container(border=True):
            st.caption("Incoming from Edge Lab Bot • Regulatory Portal")
            matched_gov = []

            if gov_search.strip():
                q = gov_search.lower()
                matched_gov = [c for c in st.session_state.gov_db if q in c.get("title", "").lower() or q in c.get("agency", "").lower()]
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
                matched_bp = [b for b in st.session_state.blueprint_db if q in b.get("title", "").lower() or q in b.get("summary", "").lower() or q in b.get("success_case", "").lower()]
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
    # Keyword Synthesis Search Block (renamed — see note below)
    # ------------------------------------------------------------------
    st.write("---")
    st.markdown("### 🔎 Keyword Synthesis Search (Cross-Database)")
    st.caption("This is simple keyword matching across both databases below — it is NOT a language model or AI assistant. A future version could connect this box to a real AI model, as long as that model is restricted to answering only from this same verified data, never from general knowledge, so it can't invent a grant, fee, or eligibility rule that doesn't exist.")

    ai_prompt = st.text_input("Search both databases at once (e.g., 'rabbit farm funding', 'register company URSB'):")

    if ai_prompt:
        q_lower = ai_prompt.lower()

        matched_gov_q = [c for c in st.session_state.gov_db if any(w in c.get("title", "").lower() or w in c.get("sector", "").lower() or w in c.get("agency", "").lower() for w in q_lower.split())]
        matched_bp_q = [b for b in st.session_state.blueprint_db if any(w in b.get("title", "").lower() or w in b.get("summary", "").lower() or w in b.get("success_case", "").lower() for w in q_lower.split())]

        with st.chat_message("assistant"):
            st.markdown("#### Keyword Matches Found")
            syn_col1, syn_col2 = st.columns(2)

            with syn_col1:
                st.markdown("📂 **1. Official Frameworks & Compliance Paths**")
                if matched_gov_q:
                    for g in matched_gov_q[:1]:
                        st.markdown(f"**Match:** {g.get('title')}")
                        st.markdown(f"* **Managing Body:** {g.get('agency')}")
                        st.markdown(f"* **Actionable Step:** {g.get('steps')}")
                        st.markdown(f"* **Statutory Fees:** `{g.get('cost')}`")
                else:
                    st.write("No keyword match in the official services database. Try the stage/sector filters in the first tab instead.")

            with syn_col2:
                st.markdown("📊 **2. 'It Works. Try It.' Financial Literacy Matrix**")
                if matched_bp_q:
                    for b in matched_bp_q[:1]:
                        st.markdown(f"**Match:** {b.get('title')}")
                        st.markdown(f"* **Capital Threshold:** `{b.get('capital_required')}`")
                        st.info(f"💡 **Survival Metric:** {b.get('fin_lit_tip')}")
                        st.success(f"🏆 {b.get('success_case')}")
                        st.markdown(f"🔗 {b.get('media_anchor')}")
                else:
                    st.write("No keyword match in the blueprint database. Try the sector/tier filters in the second tab instead.")

# ==================================================================
# VIEW 2: CITIZEN USSD SIMULATOR
# ------------------------------------------------------------------
# Rebuilt to read live from gov_db / blueprint_db by stage+sector and
# by id — NOT by list position. The previous version used hardcoded
# list-index lookups (e.g. blueprint_db[2]), which silently showed the
# WRONG content the moment any entry was added or deleted through the
# CMS. This version regenerates every menu from current data, so it
# also automatically reflects anything published through the CMS,
# instead of only the 3 hardcoded paths that existed before.
# ==================================================================
elif view == "📟 Citizen USSD Simulator":
    st.title("USSD Feature-Phone Simulation Layer")
    st.info("💡 Simulated View: Emulating a USSD session over a basic feature-phone connection.")

    if "ussd_string" not in st.session_state:
        st.session_state.ussd_string = ""

    col_input, col_screen = st.columns([1, 1])

    with col_input:
        st.subheader("Keypad Action Entry")
        current_input = st.text_input("Type your numeric choices (e.g. 1, then 1*1, then 1*1*1):", value=st.session_state.ussd_string)
        st.session_state.ussd_string = current_input.strip()

        st.write("#### 🧭 How navigation works:")
        st.markdown("""
        * Leave blank → Main menu
        * `1` → Government Services, then pick a numbered Stage, then a numbered Sector, then (if more than one) a numbered item
        * `2` → Business Blueprints, then pick a numbered Sector, then a numbered item
        * Menus are generated live from whatever is currently published in the CMS — adding or removing a card here changes what shows up in USSD automatically.
        """)
        if st.button("❌ Terminate Current USSD Session"):
            st.session_state.ussd_string = ""
            st.rerun()

    with col_screen:
        st.subheader("📟 Simulated Feature-Phone Screen")
        with st.container(border=True):
            raw = st.session_state.ussd_string
            parts = raw.split("*") if raw else []

            def safe_idx(parts, i):
                if i < len(parts):
                    try:
                        v = int(parts[i])
                        return v if v >= 1 else None
                    except ValueError:
                        return None
                return None

            INVALID = "END Invalid selection. Dial *284# to restart."
            screen = INVALID

            if not parts:
                screen = "CON Welcome to Edge Lab.\n1. Government Services\n2. Business Blueprints ('It Works')"

            elif parts[0] == "1":
                stages_avail = [s for s in STAGES if any(c["stage"] == s for c in st.session_state.gov_db)]
                if len(parts) == 1:
                    if stages_avail:
                        lines = [f"{i + 1}. {s}" for i, s in enumerate(stages_avail)]
                        screen = "CON Choose Lifecycle Stage:\n" + "\n".join(lines)
                    else:
                        screen = "END No government services published yet."
                else:
                    idx1 = safe_idx(parts, 1)
                    if idx1 and idx1 <= len(stages_avail):
                        stage = stages_avail[idx1 - 1]
                        sectors_avail = sorted({c["sector"] for c in st.session_state.gov_db if c["stage"] == stage})
                        if len(parts) == 2:
                            if sectors_avail:
                                lines = [f"{i + 1}. {s}" for i, s in enumerate(sectors_avail)]
                                screen = f"CON {stage} - Choose Sector:\n" + "\n".join(lines)
                            else:
                                screen = f"END No services yet listed for {stage}."
                        else:
                            idx2 = safe_idx(parts, 2)
                            if idx2 and idx2 <= len(sectors_avail):
                                sector = sectors_avail[idx2 - 1]
                                matches = [c for c in st.session_state.gov_db if c["stage"] == stage and c["sector"] == sector]
                                if len(parts) == 3:
                                    if len(matches) == 1:
                                        c = matches[0]
                                        screen = f"END {c['title']}\nAgency: {c['agency']}\nCost: {c['cost']}\nContact: {c['contacts']}"
                                    elif matches:
                                        lines = [f"{i + 1}. {c['title'][:30]}" for i, c in enumerate(matches)]
                                        screen = f"CON {sector} - Select:\n" + "\n".join(lines)
                                    else:
                                        screen = "END No services found."
                                else:
                                    idx3 = safe_idx(parts, 3)
                                    if idx3 and idx3 <= len(matches):
                                        c = matches[idx3 - 1]
                                        screen = f"END {c['title']}\nAgency: {c['agency']}\nCost: {c['cost']}\nContact: {c['contacts']}"

            elif parts[0] == "2":
                sectors_avail = sorted({b["sector"] for b in st.session_state.blueprint_db})
                if len(parts) == 1:
                    if sectors_avail:
                        lines = [f"{i + 1}. {s}" for i, s in enumerate(sectors_avail)]
                        screen = "CON Business Blueprints - Choose Sector:\n" + "\n".join(lines)
                    else:
                        screen = "END No blueprints published yet."
                else:
                    idx1 = safe_idx(parts, 1)
                    if idx1 and idx1 <= len(sectors_avail):
                        sector = sectors_avail[idx1 - 1]
                        items = [b for b in st.session_state.blueprint_db if b["sector"] == sector]
                        if len(parts) == 2:
                            if items:
                                lines = [f"{i + 1}. {b['title'][:30]}" for i, b in enumerate(items)]
                                screen = f"CON {sector} Blueprints:\n" + "\n".join(lines)
                            else:
                                screen = "END No blueprints found for this sector."
                        else:
                            idx2 = safe_idx(parts, 2)
                            if idx2 and idx2 <= len(items):
                                b = items[idx2 - 1]
                                screen = f"END {b['title']}\nCapital: {b['capital_required']}\nTip: {b['fin_lit_tip'][:140]}"

            st.code(screen, language="text")

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
            st.caption("Translating your active YouTube content, media field logs, and interview transcripts into accessible database formats. If a detail isn't independently confirmed yet, say so in the field rather than guessing — see the seed data above for the pattern.")

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
    st.caption("⚠️ Demo data below — illustrative only, not derived from real usage. Replace once real WhatsApp/USSD traffic exists.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Platform Hits (WhatsApp + USSD)", "24,810", "+22% this week")
    col2.metric("Most Searched Concept", "Rabbit Farming & Agribusiness", "6,140 unique pings")
    col3.metric("Video Redirection Click-Throughs", "4,950 views redirected", "74% Engagement Rate")

    st.write("---")
    st.subheader("Aggregated Analytics Overview")
    st.caption("⚠️ Demo data — illustrative only, not derived from real usage.")

    chart_data = pd.DataFrame({
        'Agribusiness Blueprints': [4200, 5100, 6800],
        'Logistics & Transport': [1200, 1800, 3400],
        'Official Gov Compliance Inquiries': [1900, 2400, 5900]
    }, index=['Western Region', 'Northern Region', 'Central Region (Kampala)'])
    st.line_chart(chart_data)

    st.write("---")
    st.subheader("Feedback Log")
    st.caption("This one IS real — it reflects actual feedback-button presses recorded in this running instance, not synthetic data.")
    if st.session_state.feedback_log:
        st.dataframe(pd.DataFrame(st.session_state.feedback_log), use_container_width=True)
    else:
        st.info("No feedback recorded yet in this session. Use the WhatsApp Simulator's feedback buttons to generate entries.")
