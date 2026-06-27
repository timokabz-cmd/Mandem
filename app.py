import streamlit as st
import uuid

# ==================================
# 1. PAGE SETUP
# ==================================
st.set_page_config(
    page_title="Mandem",
    page_icon="🇺🇬",
    layout="wide"
)

# ==================================
# 2. 🔒 SECURITY LOCK GATE
# ==================================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔒 Locked")
    st.write("Under maintenance.")
    
    with st.form("gate"):
        pin = st.text_input(
            "PIN:", 
            type="password"
        )
        if st.form_submit_button("Go"):
            if pin == "2567":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Denied")
    st.stop()

# ==================================
# 3. CORE TAXONOMIES
# ==================================
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

# Ultra-short line safe data stack
if "cards" not in st.session_state:
    st.session_state.cards = [
        {
            "id": str(uuid.uuid4()),
            "title": "Emyooga Seed Capital",
            "stage": "Idea Stage",
            "sector": "Manufacturing",
            "agency": "MSC Support Centre",
            "steps": "Register via Parish",
            "cost": "Free",
            "contact": "info@msc.co.ug"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "URSB Name Reg",
            "stage": "Startup Stage",
            "sector": "Trade & Retail",
            "agency": "URSB Uganda",
            "steps": "Submit Form 3 OBRS",
            "cost": "24,000 UGX",
            "contact": "ursb@ursb.go.ug"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "URSB Incorporation",
            "stage": "Startup Stage",
            "sector": "Manufacturing",
            "agency": "URSB Uganda",
            "steps": "Upload MemArts",
            "cost": "180,000 UGX",
            "contact": "ursb@ursb.go.ug"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "URA Tax TIN",
            "stage": "Startup Stage",
            "sector": "Trade & Retail",
            "agency": "URA Uganda",
            "steps": "Apply via portal",
            "cost": "Free",
            "contact": "services@ura.go.ug"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "MAAIF Irrigation",
            "stage": "Growth Stage",
            "sector": "Agriculture & Agribusiness",
            "agency": "Min of Agri",
            "steps": "Apply to District",
            "cost": "Co-funding split",
            "contact": "maaif@maaif.go.ug"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "PSFU GROW Project",
            "stage": "Growth Stage",
            "sector": "Trade & Retail",
            "agency": "PSFU / World Bank",
            "steps": "Apply via banks",
            "cost": "Concessionary",
            "contact": "grow@psfu.org.ug"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "NSSF Hi-Innovator",
            "stage": "Growth Stage",
            "sector": "Digital & ICT",
            "agency": "NSSF & Outbox",
            "steps": "Online modules",
            "cost": "Equity-free",
            "contact": "hi-innovator@nssfug.org"
        }
    ]

# ==================================
# 4. SIDEBAR NAVIGATION
# ==================================
st.sidebar.title("Menu")
view = st.sidebar.radio(
    "Navigate:",
    ["🏛️ Matrix", "📟 USSD", "⚙️ Admin"]
)

# ==================================
# VIEW 1: MATRIX
# ==================================
if view == "🏛️ Matrix":
    st.title("🏛️ Matrix")
    
    stg = st.selectbox(
        "Maturity:", 
        ["All"] + STAGES
    )
    sec = st.selectbox(
        "Sector:", 
        ["All"] + SECTORS
    )
    
    filtered = st.session_state.cards
    if stg != "All":
        filtered = [
            c for c in filtered 
            if c["stage"] == stg
        ]
    if sec != "All":
        filtered = [
            c for c in filtered 
            if c["sector"] == sec
        ]
        
    st.markdown("---")
    
    for c in filtered:
        lbl = f"{c['title']}"
        with st.expander(lbl):
            st.write(f"**Agency:** {c['agency']}")
            st.write(f"**Steps:** {c['steps']}")
            st.write(f"**Fees:** `{c['cost']}`")
            st.write(f"**Contact:** `{c['contact']}`")
            
            with st.form(f"del_{c['id']}"):
                if st.form_submit_button("🗑️ Delete"):
                    st.session_state.cards = [
                        x for x in st.session_state.cards 
                        if x["id"] != c["id"]
                    ]
                    st.success("Removed.")
                    st.rerun()

# ==================================
# VIEW 2: USSD SIMULATOR
# ==================================
elif view == "📟 USSD":
    st.title("📟 USSD Engine")
    
    curr = st.text_input("Code:")
    if st.button("Transmit String"):
        st.session_state.u_str = curr
        st.rerun()
        
    val = st.session_state.get(
        "u_str", "None"
    )
    st.markdown(
        f"""
        <div style="background-color:#1e1e1e; 
        padding:15px; border-radius:8px; 
        color:#00ff00; font-family:monospace;">
            <strong>[SESSION LIVE]</strong><br>
            Code: {val}<br><br>
            1. Frameworks Matrix<br>
            2. Capital Seed Programs<br>
        </div>
        """, 
        unsafe_html=True
    )

# ==================================
# VIEW 3: ADMIN CONTROL
# ==================================
elif view == "⚙️ Admin":
    st.title("⚙️ Operations Panel")
    
    with st.form("add"):
        t = st.text_input("Title:")
        stg = st.selectbox("Stage:", STAGES)
        sec = st.selectbox("Sector:", SECTORS)
        ag = st.text_input("Agency:")
        step = st.text_area("Steps:")
        cst = st.text_input("Cost:")
        cnt = st.text_input("Contact:")
        
        if st.form_submit_button("⚡ Save"):
            if t and ag:
                st.session_state.cards.append({
                    "id": str(uuid.uuid4()),
                    "title": t,
                    "stage": stg,
                    "sector": sec,
                    "agency": ag,
                    "steps": step,
                    "cost": cst,
                    "contact": cnt
                })
                st.success("Saved.")
                st.rerun()
