import streamlit as st
import pandas as pd
import json
import os
import uuid
import base64
from datetime import datetime

try:
    from google import genai as google_genai
    from google.genai import types as genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import qrcode
    from io import BytesIO as QRBytesIO
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# ------------------------------------------------------------------
# 1. Page Configuration
# ------------------------------------------------------------------
st.set_page_config(page_title="Edge Lab Platform", page_icon="🇺🇬", layout="wide")

import html as _H

def _e(t):
    return _H.escape(str(t or ""))

def inject_css():
    st.markdown("""
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");
html,body,[class*="css"]{font-family:"Inter",sans-serif;}
.main .block-container{padding-top:1.5rem;padding-bottom:2rem;max-width:1280px;}
footer{visibility:hidden;}
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#152840 0%,#1F3A5F 60%,#1A3254 100%);
  border-right:3px solid #B68D40;}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] .stCaption{color:#CBD5E0 !important;}
[data-testid="stSidebar"] .stRadio label span{color:#E2E8F0 !important;}
[data-testid="stSidebar"] hr{border-color:rgba(182,141,64,0.4) !important;margin:0.8rem 0 !important;}
[data-testid="stSidebar"] .stButton>button{
  background:rgba(182,141,64,0.15) !important;color:#B68D40 !important;
  border:1px solid rgba(182,141,64,0.5) !important;border-radius:8px !important;
  width:100% !important;font-size:0.82rem !important;font-weight:600 !important;}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(182,141,64,0.3) !important;}
.stButton>button{
  background:linear-gradient(135deg,#1F3A5F 0%,#2C5282 100%) !important;
  color:white !important;border:none !important;border-radius:8px !important;
  padding:0.45rem 1.2rem !important;font-weight:600 !important;font-size:0.88rem !important;
  transition:all 0.2s ease !important;box-shadow:0 2px 6px rgba(31,58,95,0.25) !important;}
.stButton>button:hover{
  background:linear-gradient(135deg,#B68D40 0%,#9A7535 100%) !important;
  box-shadow:0 4px 14px rgba(182,141,64,0.35) !important;transform:translateY(-1px) !important;}
.stDownloadButton>button{
  background:linear-gradient(135deg,#B68D40 0%,#9A7535 100%) !important;
  color:white !important;border:none !important;border-radius:8px !important;
  font-weight:600 !important;font-size:0.85rem !important;
  box-shadow:0 2px 6px rgba(182,141,64,0.3) !important;transition:all 0.2s ease !important;}
.stDownloadButton>button:hover{
  background:linear-gradient(135deg,#1F3A5F 0%,#2C5282 100%) !important;
  transform:translateY(-1px) !important;}
[data-testid="metric-container"]{
  background:white !important;border:1px solid #E2E8F0 !important;
  border-radius:12px !important;padding:1rem !important;
  box-shadow:0 2px 8px rgba(0,0,0,0.05) !important;border-top:3px solid #1F3A5F !important;}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p{
  font-size:0.72rem !important;font-weight:700 !important;color:#6C757D !important;
  text-transform:uppercase !important;letter-spacing:0.06em !important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{
  font-size:1.5rem !important;font-weight:700 !important;color:#1F3A5F !important;}
.stTabs [data-baseweb="tab-list"]{
  background-color:#EEF2F7;border-radius:10px;padding:4px;gap:3px;}
.stTabs [data-baseweb="tab"]{
  border-radius:8px;color:#4A5568;font-weight:500;font-size:0.87rem;padding:0.4rem 1rem;}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg,#1F3A5F 0%,#2C5282 100%) !important;
  color:white !important;font-weight:600 !important;}
[data-testid="stVerticalBlockBorderWrapper"]{
  border:1px solid #E2E8F0 !important;border-radius:12px !important;
  box-shadow:0 2px 8px rgba(0,0,0,0.04) !important;background:white !important;}
details summary{
  background-color:#F7FAFC !important;border-radius:8px !important;
  color:#1F3A5F !important;font-weight:600 !important;padding:0.6rem 0.8rem !important;}
details summary:hover{background-color:#EDF2F7 !important;}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{
  border-radius:8px !important;border-color:#CBD5E0 !important;font-size:0.9rem !important;}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{
  border-color:#1F3A5F !important;box-shadow:0 0 0 3px rgba(31,58,95,0.12) !important;}
[data-baseweb="select"]{border-radius:8px !important;}
.stProgress>div>div>div{background:linear-gradient(90deg,#1F3A5F,#B68D40) !important;}
[data-testid="stAlert"]{border-radius:10px !important;border-left-width:4px !important;}
[data-testid="stDataFrame"]{border-radius:10px !important;overflow:hidden !important;}
hr{border-color:#E2E8F0 !important;margin:1.2rem 0 !important;}
</style>""", unsafe_allow_html=True)

def branded_header(title, subtitle="", right_label=""):
    r = (f'<span style="background:rgba(182,141,64,0.25);color:#F6D860;'
         f'padding:0.25rem 0.9rem;border-radius:20px;font-size:0.78rem;'
         f'font-weight:700;">{_e(right_label)}</span>' if right_label else "")
    sub = (f'<div style="color:#B68D40;font-size:0.9rem;margin-top:0.2rem;">'
           f'{_e(subtitle)}</div>' if subtitle else "")
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#152840 0%,#1F3A5F 60%,#2C5282 100%);padding:1.2rem 1.6rem;'
        f'border-radius:14px;margin-bottom:1.5rem;border-left:5px solid #B68D40;'
        f'box-shadow:0 4px 16px rgba(31,58,95,0.22);">"'
        f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">'
        f'<div style="display:flex;align-items:center;gap:0.9rem;">'
        f'<span style="font-size:2rem;">🇺🇬</span>'
        f'<div><div style="color:rgba(255,255,255,0.65);font-size:0.7rem;font-weight:700;'
        f'letter-spacing:0.12em;text-transform:uppercase;">Edge Lab Platform</div>'
        f'<div style="color:white;font-size:1.25rem;font-weight:700;">{_e(title)}</div>{sub}</div></div>{r}</div></div>',
        unsafe_allow_html=True)

def gov_card_html(card):
    is_ngo = card.get("id","").startswith("ngo")
    border = "#2D8653" if is_ngo else "#1F3A5F"
    b_bg   = "#E8F8F5" if is_ngo else "#EBF5FB"
    b_fg   = "#2D8653" if is_ngo else "#1F3A5F"
    badge  = "🌍 UN/NGO Partner" if is_ngo else "🏛️ Government"
    steps  = _e(card.get("steps",""))
    for i in range(1,8): steps = steps.replace(f"{i}. ",f"<br><b>{i}.</b> ")
    steps  = steps.lstrip("<br>")
    return (
        f'<div style="background:white;border-left:5px solid {border};border-radius:12px;'
        f'padding:1.4rem;margin-bottom:0.6rem;box-shadow:0 3px 12px rgba(0,0,0,0.07);">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;'
        f'margin-bottom:0.9rem;gap:0.8rem;">'
        f'<div style="color:#1F3A5F;font-size:1rem;font-weight:700;flex:1;">{_e(card.get("title",""))}</div>'
        f'<span style="background:{b_bg};color:{b_fg};padding:0.22rem 0.65rem;'
        f'border-radius:14px;font-size:0.7rem;font-weight:700;white-space:nowrap;">{badge}</span></div>'
        f'<div style="color:#6C757D;font-size:0.8rem;margin-bottom:0.9rem;">🏛️ <strong>{_e(card.get("agency",""))}</strong></div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.7rem;margin-bottom:0.9rem;">'
        f'<div style="background:#F0F6FF;border-radius:8px;padding:0.7rem;">'
        f'<div style="font-size:0.68rem;color:#1F3A5F;font-weight:800;text-transform:uppercase;'
        f'margin-bottom:0.3rem;">✅ Who Qualifies</div>'
        f'<div style="font-size:0.82rem;color:#2D3748;line-height:1.5;">{_e(card.get("eligibility",""))}</div></div>'
        f'<div style="background:#FFFBF0;border-radius:8px;padding:0.7rem;border-left:3px solid #B68D40;">'
        f'<div style="font-size:0.68rem;color:#B68D40;font-weight:800;text-transform:uppercase;'
        f'margin-bottom:0.3rem;">💰 Cost</div>'
        f'<div style="font-size:0.82rem;color:#2D3748;line-height:1.5;">{_e(card.get("cost",""))}</div></div></div>'
        f'<div style="background:#F8FAFC;border-radius:8px;padding:0.8rem;margin-bottom:0.8rem;">'
        f'<div style="font-size:0.68rem;color:#1F3A5F;font-weight:800;text-transform:uppercase;'
        f'margin-bottom:0.4rem;">🛠️ Steps to Take</div>'
        f'<div style="font-size:0.82rem;color:#2D3748;line-height:1.7;">{steps}</div></div>'
        f'<div style="background:#F0FFF4;border-radius:8px;padding:0.6rem 0.8rem;">'
        f'<span style="font-size:0.8rem;color:#2D8653;font-weight:600;">📞 {_e(card.get("contacts",""))}</span></div></div>'
    )

def blueprint_card_html(bp):
    tm = {"Micro (Under UGX 5M)":("#E8F8F5","#2D8653"),
          "Small (UGX 5M - 20M)":("#EBF5FB","#1F3A5F"),
          "Medium/Commercial (UGX 20M+)":("#FFFBF0","#B68D40")}
    bg,fg = tm.get(bp.get("tier",""),("#F8FAFC","#6C757D"))
    cap = _e(bp.get("capital_required",""))[:80]
    return (
        f'<div style="background:white;border-radius:12px;padding:1.4rem;'
        f'margin-bottom:0.6rem;box-shadow:0 3px 12px rgba(0,0,0,0.07);border-top:4px solid {fg};">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;'
        f'margin-bottom:0.8rem;gap:0.8rem;">'
        f'<div style="color:#1F3A5F;font-size:1rem;font-weight:700;flex:1;">💡 {_e(bp.get("title",""))}</div>'
        f'<span style="background:{bg};color:{fg};padding:0.22rem 0.65rem;'
        f'border-radius:14px;font-size:0.7rem;font-weight:700;">{_e(bp.get("tier",""))}</span></div>'
        f'<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.8rem;">'
        f'<span style="background:#EEF2F7;color:#1F3A5F;padding:0.2rem 0.55rem;'
        f'border-radius:6px;font-size:0.72rem;font-weight:600;">📂 {_e(bp.get("sector",""))}</span>'
        f'<span style="background:#FFFBF0;color:#B68D40;padding:0.2rem 0.55rem;'
        f'border-radius:6px;font-size:0.72rem;font-weight:600;">💰 {cap}</span></div>'
        f'<p style="font-size:0.85rem;color:#374151;line-height:1.65;margin-bottom:0.8rem;">{_e(bp.get("summary",""))}</p>'
        f'<div style="background:#FFFBF0;border-radius:8px;padding:0.75rem;'
        f'margin-bottom:0.7rem;border-left:3px solid #B68D40;">'
        f'<div style="font-size:0.68rem;color:#B68D40;font-weight:800;text-transform:uppercase;'
        f'margin-bottom:0.3rem;">💡 Financial Literacy Tip</div>'
        f'<div style="font-size:0.83rem;color:#374151;line-height:1.55;">{_e(bp.get("fin_lit_tip",""))}</div></div>'
        f'<div style="background:#F0FFF4;border-radius:8px;padding:0.75rem;border-left:3px solid #2D8653;">'
        f'<div style="font-size:0.68rem;color:#2D8653;font-weight:800;text-transform:uppercase;'
        f'margin-bottom:0.3rem;">🏆 Proof It Works</div>'
        f'<div style="font-size:0.83rem;color:#374151;line-height:1.55;">{_e(bp.get("success_case",""))}</div></div></div>'
    )

def lesson_card_html(m, local_ctx=""):
    sc = {"Idea Stage":("# EBF5FB","#1F3A5F","💡"),
          "Startup Stage":("#FFFBF0","#B68D40","🚀"),
          "Growth Stage":("#F0FFF4","#2D8653","📈"),
          "Mature MSME Stage":("#F5F0FF","#6B4FBB","🏢")}
    bg,fg,icon = sc.get(m.get("stage",""),("#F8FAFC","#374151","📌"))
    ug = (f'<div style="background:#EBF5FB;border-radius:8px;padding:0.75rem;margin-bottom:0.7rem;">'
          f'<div style="font-size:0.68rem;color:#1F3A5F;font-weight:800;text-transform:uppercase;'
          f'margin-bottom:0.3rem;">🇺🇬 In Uganda</div>'
          f'<div style="font-size:0.83rem;color:#374151;line-height:1.55;">{_e(m.get("uganda_example",""))}</div></div>'
          if m.get("uganda_example") else "")
    ctx = (f'<div style="background:#E8F0FE;border-radius:8px;padding:0.6rem 0.8rem;margin-bottom:0.7rem;">'
           f'<span style="font-size:0.8rem;color:#1F3A5F;font-weight:600;">📍 In your area: {_e(local_ctx)}</span></div>'
           if local_ctx else "")
    mis = (f'<div style="background:#FFFBF0;border-radius:8px;padding:0.75rem;margin-bottom:0.7rem;'
           f'border-left:3px solid #E07B39;">'
           f'<div style="font-size:0.68rem;color:#E07B39;font-weight:800;text-transform:uppercase;'
           f'margin-bottom:0.3rem;">⚠️ Common Mistake</div>'
           f'<div style="font-size:0.83rem;color:#374151;line-height:1.55;">{_e(m.get("common_mistake",""))}</div></div>'
           if m.get("common_mistake") else "")
    return (
        f'<div style="background:white;border-radius:12px;padding:1.4rem;'
        f'margin-bottom:0.6rem;box-shadow:0 3px 12px rgba(0,0,0,0.07);border-top:4px solid {fg};">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'margin-bottom:0.9rem;gap:0.8rem;">'
        f'<div style="color:#1F3A5F;font-size:1rem;font-weight:700;">{icon} {_e(m.get("topic",""))}</div>'
        f'<span style="background:{bg};color:{fg};padding:0.22rem 0.65rem;'
        f'border-radius:14px;font-size:0.7rem;font-weight:700;">{_e(m.get("stage",""))}</span></div>'
        f'<p style="font-size:0.87rem;color:#374151;line-height:1.65;margin-bottom:0.9rem;">{_e(m.get("summary",""))}</p>'
        f'{ug}{ctx}{mis}'
        f'<div style="background:#F0FFF4;border-radius:8px;padding:0.75rem;border-left:3px solid #2D8653;">'
        f'<div style="font-size:0.68rem;color:#2D8653;font-weight:800;text-transform:uppercase;'
        f'margin-bottom:0.3rem;">✅ Do This Now</div>'
        f'<div style="font-size:0.85rem;color:#2D3748;font-weight:600;line-height:1.55;">{_e(m.get("action_tip",""))}</div></div></div>'
    )



# ------------------------------------------------------------------
# 2. Shared Taxonomies
# ------------------------------------------------------------------
STAGES = ["Idea Stage", "Startup Stage", "Growth Stage", "Mature MSME Stage"]
SECTORS = ["Agriculture & Agribusiness", "Trade & Retail", "Digital & ICT",
           "Manufacturing", "Logistics & Transport"]
CAPITAL_TIERS = ["Micro (Under UGX 5M)", "Small (UGX 5M - 20M)", "Medium/Commercial (UGX 20M+)"]

DISTRICTS_BY_REGION = {
    "Central": sorted([
        "Buikwe", "Bukomansimbi", "Butambala", "Buvuma", "Gomba", "Kalangala",
        "Kalungu", "Kampala", "Kassanda", "Kayunga", "Kiboga", "Kyankwanzi",
        "Kyotera", "Luweero", "Lwengo", "Lyantonde", "Masaka", "Mityana",
        "Mpigi", "Mubende", "Mukono", "Nakaseke", "Nakasongola", "Rakai",
        "Sembabule", "Wakiso"
    ]),
    "Eastern": sorted([
        "Amuria", "Budaka", "Bududa", "Bugiri", "Bugweri", "Bukedea", "Bukwo",
        "Bulambuli", "Busia", "Butaleja", "Butebo", "Buyende", "Iganga",
        "Jinja", "Jinja City", "Kaberamaido", "Kalaki", "Kaliro", "Kamuli",
        "Kapelebyong", "Kapchorwa", "Katakwi", "Kibuku", "Kumi", "Kween",
        "Luuka", "Manafwa", "Mayuge", "Mbale", "Mbale City", "Namayingo",
        "Namisindwa", "Namutumba", "Ngora", "Pallisa", "Serere", "Sironko",
        "Soroti", "Soroti City", "Tororo"
    ]),
    "Northern": sorted([
        "Abim", "Adjumani", "Agago", "Alebtong", "Amolatar", "Amudat", "Amuru",
        "Apac", "Arua", "Arua City", "Dokolo", "Gulu", "Gulu City", "Kaabong",
        "Karenga", "Kitgum", "Koboko", "Kole", "Kotido", "Kwania", "Lamwo",
        "Lira", "Lira City", "Madi-Okollo", "Maracha", "Moroto", "Moyo",
        "Nabilatuk", "Nakapiripirit", "Napak", "Nebbi", "Nwoya", "Obongi",
        "Omoro", "Otuke", "Oyam", "Pader", "Pakwach", "Terego", "Yumbe", "Zombo"
    ]),
    "Western": sorted([
        "Buhweju", "Buliisa", "Bundibugyo", "Bunyangabu", "Bushenyi",
        "Fort Portal City", "Hoima", "Hoima City", "Ibanda", "Isingiro",
        "Kabale", "Kabarole", "Kagadi", "Kakumiro", "Kamwenge", "Kanungu",
        "Kasese", "Kazo", "Kibaale", "Kikuube", "Kiruhura", "Kiryandongo",
        "Kisoro", "Kitagwenda", "Kyegegwa", "Kyenjojo", "Masindi", "Mbarara",
        "Mbarara City", "Mitooma", "Ntoroko", "Ntungamo", "Rubanda", "Rubirizi",
        "Rukiga", "Rukungiri", "Rwampara", "Sheema"
    ])
}

ALL_DISTRICTS = ["Select District"] + [d for region in DISTRICTS_BY_REGION.values() for d in region]

REGION_SAVINGS_CONTEXT = {
    "Central": "In Central Uganda, savings options include MTN MoMo Save, Centenary Bank (strong across Kampala and Wakiso), PostBank Uganda, and dozens of active market-association SACCOs in Nakasero, Owino (St. Balikuddembe), Kikuubo, and Wandegeya. FINCA Uganda and Pride Microfinance also have their strongest branch networks in this region. The Emyooga SACCO for your trade category is organized at constituency level — your LC1 chairperson can connect you to the right one.",
    "Eastern": "In Eastern Uganda, PostBank Uganda branches in Jinja, Mbale, and Soroti are strong savings options alongside MTN MoMo Save. BRAC Uganda has significant microfinance presence across Iganga, Tororo, and Mbale. The Busoga sub-region has an active SACCO culture through market and traders' associations in Jinja and Kamuli. PDM Parish SACCOs are being actively rolled out across all sub-counties — your Sub-County Commercial Officer can identify the nearest active one.",
    "Northern": "In Northern Uganda, PostBank Uganda and Centenary Bank both operate in Gulu, Lira, and Arua. FINCA Uganda and Pride Microfinance cover Gulu and Lira specifically. The PDM Parish SACCO rollout is active across all sub-counties. BRAC Uganda also operates in several Northern districts. For Emyooga SACCOs by trade category, your District Commercial Officer in Gulu, Lira, or Arua can direct you to the relevant constituency-level SACCO.",
    "Western": "Western Uganda has one of the strongest SACCO cultures in the country. Centenary Bank has strong rural reach in Mbarara, Kabale, and Ntungamo. Finance Trust Bank and Pride Microfinance cover most district towns. Agricultural SACCOs in Kiruhura, Isingiro, and Ntungamo have long track records serving dairy and cattle farmers. MTN MoMo Save and PostBank Uganda are widely available across the region. Your Emyooga trade-category SACCO is accessible through the constituency office."
}


def get_user_region(district):
    for region, districts in DISTRICTS_BY_REGION.items():
        if district in districts:
            return region
    return None


# ------------------------------------------------------------------
# 3. Database File Constants
# ------------------------------------------------------------------
GOV_DB_FILE = "gov_db.json"
BLUEPRINT_DB_FILE = "blueprint_db.json"
MASTERCLASS_DB_FILE = "masterclass_db.json"
FEEDBACK_FILE = "feedback_log.json"

# ------------------------------------------------------------------
# FEATURE 1 & 2: Helper Functions  (powered by Google Gemini — free)
# Uses the new google-genai SDK (replaces deprecated google-generativeai)
# ------------------------------------------------------------------

def _gemini_client():
    """Returns a configured Gemini client, or None if key is missing."""
    if not GEMINI_AVAILABLE:
        return None
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    return google_genai.Client(api_key=api_key)


def scan_national_id_with_gemini(image_file):
    """
    Sends ID image to Gemini Vision (free tier) using new google-genai SDK.
    Returns dict with {given_names, sex, district} only.
    NIN is intentionally NOT extracted — preserving the app's privacy policy.
    """
    client = _gemini_client()
    if client is None:
        if not GEMINI_AVAILABLE:
            return {"error": "google-genai not installed — add it to requirements.txt"}
        return {"error": "GEMINI_API_KEY not set in Streamlit secrets"}
    try:
        img_bytes  = image_file.getvalue()
        file_name  = getattr(image_file, "name", "") or ""
        mime_type  = "image/png" if file_name.lower().endswith(".png") else "image/jpeg"
        image_part = genai_types.Part.from_bytes(data=img_bytes, mime_type=mime_type)
        resp = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[
                image_part,
                (
                    "This is a Uganda National ID card.\n"
                    "Return ONLY a JSON object — no markdown, no explanation:\n"
                    '{"given_names": "all given/first names as printed on the card", '
                    '"sex": "Male or Female", '
                    '"district": "district of birth as printed on the card"}\n'
                    "Use null for any field that is not clearly readable."
                )
            ]
        )
        raw = resp.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e)}


def transcribe_audio_gemini(audio_bytes, language_hint="English"):
    """
    Transcribes audio using Gemini multimodal (free tier, new google-genai SDK).
    Uploads audio via Files API then asks Gemini to transcribe it.
    language_hint: 'English', 'Swahili', or 'Arabic'
    """
    client = _gemini_client()
    if client is None:
        return None
    try:
        audio_io      = io.BytesIO(audio_bytes)
        audio_io.name = "recording.webm"
        # Upload via Files API (more reliable than inline for audio)
        uploaded = client.files.upload(
            file=audio_io,
            config=genai_types.UploadFileConfig(mime_type="audio/webm")
        )
        resp = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[
                uploaded,
                f"This audio is spoken in {language_hint}. "
                f"Transcribe exactly what is said, word for word. "
                f"Return only the transcription text, nothing else."
            ]
        )
        # Clean up uploaded file to stay within free tier storage limits
        try:
            client.files.delete(name=uploaded.name)
        except Exception:
            pass
        return resp.text.strip()
    except Exception as e:
        return None


def process_voice_command_with_gemini(user_query, user_profile, gov_db, blueprint_db, masterclass_db):
    """
    Cross-references the user's query against all three databases
    and returns a personalised response via Gemini (free tier, new SDK).
    Automatically responds in Swahili or Arabic if query is in that language.
    """
    client = _gemini_client()
    if client is None:
        if not GEMINI_AVAILABLE:
            return "google-genai is not installed. Add it to requirements.txt."
        return "GEMINI_API_KEY is not set in Streamlit secrets. Add it to complete setup."
    try:
        # Compact summaries to keep tokens efficient
        gov_summary = [
            {"title": c["title"], "stage": c.get("stage"), "sector": c.get("sector"),
             "eligibility": (c.get("eligibility") or "")[:150], "cost": c.get("cost", "")}
            for c in gov_db[:15]
        ]
        bp_summary = [
            {"title": b["title"], "sector": b.get("sector"), "tier": b.get("tier"),
             "summary": (b.get("summary") or "")[:120]}
            for b in blueprint_db[:6]
        ]
        fl_summary = [
            {"topic": m["topic"], "stage": m.get("stage"),
             "action_tip": (m.get("action_tip") or "")[:100]}
            for m in masterclass_db[:12]
        ]

        prompt = f"""You are the Edge Lab Platform assistant — an intelligent advisor for Uganda's MSME and youth community.
Help this citizen find the most relevant grants, business blueprints, and financial advice based on their profile and question.

USER PROFILE:
{json.dumps(user_profile, ensure_ascii=False, indent=1)}

AVAILABLE GOVERNMENT SERVICES & GRANTS ({len(gov_db)} programs):
{json.dumps(gov_summary, ensure_ascii=False, indent=1)}

BUSINESS BLUEPRINTS ({len(blueprint_db)} models):
{json.dumps(bp_summary, ensure_ascii=False, indent=1)}

FINANCIAL LITERACY TOPICS ({len(masterclass_db)} lessons):
{json.dumps(fl_summary, ensure_ascii=False, indent=1)}

USER'S QUESTION: "{user_query}"

RULES:
- Name specific programs, amounts, and eligibility from the data above
- If the question is in Swahili → respond fully in Swahili
- If the question is in Arabic → respond fully in Arabic
- Keep it mobile-friendly: short paragraphs, clear headings
- End with exactly one next step the user can take today"""

        resp = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )
        return resp.text
    except Exception as e:
        return f"Error processing your question: {e}"




# ------------------------------------------------------------------
# 4. Default Government Services Database
# ------------------------------------------------------------------
DEFAULT_GOV_DB = [
    {
        "id": "gov-pdm-001",
        "title": "Parish Agricultural Value Chain Grant Support",
        "agency": "Ministry of Local Government / PDM Secretariat",
        "stage": "Idea Stage", "sector": "Agriculture & Agribusiness",
        "eligibility": "Subsistence households organized inside a registered Parish Enterprise Group (PEG), supported through a SACCO in every parish nationwide.",
        "cost": "Free (Zero statutory application charges across all sub-counties).",
        "steps": "1. Approach local LC1 Chairperson to verify household status. 2. Join or register a verified Parish Enterprise Group matching specific commodity value chains. 3. File data into the Parish Development Management Information System (PBMIS) portal via the Parish Chief. 4. Wait for vetting and subsequent disbursement from the Parish Revolving Fund.",
        "contacts": "Parish Chief / Sub-County PDM Desk Officer."
    },
    {
        "id": "gov-ylp-007",
        "title": "Youth Livelihood Programme (YLP) Revolving Fund",
        "agency": "Ministry of Gender, Labour and Social Development (MGLSD)",
        "stage": "Idea Stage", "sector": "Trade & Retail",
        "eligibility": "Ugandans aged 18-30, organized into a Youth Interest Group (YIG) of 10-15 members, proposing an income-generating project.",
        "cost": "Free; revolving fund of UGX 1,000,000 - 25,000,000 per group, interest-free for the first 12 months.",
        "steps": "1. Form or join a Youth Interest Group (YIG) of 10-15 members. 2. Develop a simple income-generating project proposal as a group. 3. Submit the proposal through your Sub-County/Division Community Development Officer. 4. Await vetting by the District YLP Committee before disbursement.",
        "contacts": "Sub-County or Division Community Development Officer."
    },
    {
        "id": "gov-ursb-002",
        "title": "URSB OBRS Limited Liability Company Incorporation",
        "agency": "Uganda Registration Services Bureau (URSB)",
        "stage": "Startup Stage", "sector": "Manufacturing",
        "eligibility": "Enterprises with a minimum of two directors holding valid Ugandan National Identification Cards with scannable National Identification Numbers (NINs).",
        "cost": "UGX 140,000 standard baseline statutory fees plus registration stamp duty. (Verify current figure on obrs.ursb.go.ug before publishing.)",
        "steps": "1. Access the Online Business Registration System (OBRS) at obrs.ursb.go.ug. 2. Run a corporate name availability search and reserve your unique name. 3. Input profiles for directors, corporate secretaries, and shareholding. 4. Complete Form 18 (Application for Registration) and Form 20 (Notice of Appointment of Directors). 5. Upload digitized Memorandum and Articles of Association. 6. Generate an e-payment PRN and pay via mobile money or bank.",
        "contacts": "URSB Head Office, Uganda Business Facilitation Centre, Plot 1 Baskerville Avenue, Kololo. Toll-free: 0800 100 006 / obrs.ursb.go.ug"
    },
    {
        "id": "gov-ura-003",
        "title": "URA Tax Identification Number (TIN) & Income Tax Compliance",
        "agency": "Uganda Revenue Authority (URA)",
        "stage": "Startup Stage", "sector": "Trade & Retail",
        "eligibility": "Any individual Ugandan business owner (Sole Proprietor) with a valid National ID, or any registered corporate legal entity with a URSB registration number.",
        "cost": "Free (Zero application fees).",
        "steps": "1. Navigate to ura.go.ug and select TIN Registration under e-services. 2. Select business structure type (Individual vs. Non-Individual). 3. Populate personal details matching NIRA records. 4. Map operating address and business activity category codes. 5. Submit to generate an instant acknowledgement receipt. 6. Download your digital TIN certificate via email upon verification.",
        "contacts": "URA Toll-Free: 0800117000 / services@ura.go.ug / URA Headquarters, Plot M193/194, Nakawa Industrial Area, Kampala."
    },
    {
        "id": "gov-kcca-004",
        "title": "KCCA Municipal Trading License Acquisition",
        "agency": "Kampala Capital City Authority / Local Government Municipalities",
        "stage": "Startup Stage", "sector": "Trade & Retail",
        "eligibility": "Operating fixed or mobile physical commercial business premises within Kampala or corresponding municipal zones.",
        "cost": "Variable by business type, sector code, and premises size. (Verify current fee schedule directly with KCCA before publishing.)",
        "steps": "1. Present certified copies of incorporation/business name documents alongside your active URA TIN certificate. 2. Complete the KCCA trading license application (physical or online). 3. A municipal officer inspects premises to verify operations and assign a Grade category. 4. An assessment note generates a Payment Registration Number (PRN). 5. Complete payment. 6. Collect your official trading license sticker.",
        "contacts": "KCCA Citizen Service Centers at City Hall or Division Offices (Central, Nakawa, Makindye, Rubaga, Kawempe)."
    },
    {
        "id": "gov-emyooga-006",
        "title": "Emyooga Specialized SACCO Grant Scheme",
        "agency": "Microfinance Support Centre (MSC) / Ministry of Finance",
        "stage": "Growth Stage", "sector": "Trade & Retail",
        "eligibility": "Ugandans already practicing a specific informal trade (market vending, boda riding, hairdressing, tailoring, etc.). Identification happens at village level with LC1 support, then organized into one of 18 category-specific SACCOs.",
        "cost": "Free to join; standard SACCO savings/share contribution applies per category bylaws.",
        "steps": "1. Identify your trade category and approach your LC1 chairperson, who coordinates village-level identification. 2. Join or form the parish-level association for your category. 3. Register a constituency-level SACCO bringing together parish associations. 4. Apply for SACCO capitalization support disbursed through the Microfinance Support Centre.",
        "contacts": "Microfinance Support Centre (MSC) / Sub-County Commercial Officer."
    },
    {
        "id": "gov-grow-005",
        "title": "PSFU GROW Project Women Enterprise Loan & Grant Scheme",
        "agency": "Private Sector Foundation Uganda (PSFU) / Ministry of Gender, Labour and Social Development, with World Bank funding",
        "stage": "Growth Stage", "sector": "Manufacturing",
        "eligibility": "Enterprises owned or majority-controlled by women (minimum 51% equity shareholding). Open to MSMEs transitioning to the next scale, including women in refugee-hosting districts.",
        "cost": "Zero evaluation fees. Loans from UGX 4,000,000 to UGX 200,000,000 across three tiers at roughly 10% per annum. On-time repayment earns a bonus grant of up to 5% of the loan principal.",
        "steps": "1. Approach any of the six partner banks: Centenary Bank, DFCU, Equity Bank, Finance Trust Bank, Post Bank, or Stanbic Bank. 2. Present documentation proving majority female ownership. 3. Demonstrate existing financial operations via sales books or digital ledgers. 4. Complete the bank's loan application for your eligible tier (4-20M, 20-40M, or 40-200M).",
        "contacts": "Any GROW partner bank branch / PSFU Head Office, Nakasero, Kampala / grow.go.ug"
    },
    {
        "id": "gov-uwep-008",
        "title": "Uganda Women Entrepreneurship Programme (UWEP)",
        "agency": "Ministry of Gender, Labour and Social Development (MGLSD)",
        "stage": "Growth Stage", "sector": "Trade & Retail",
        "eligibility": "Women entrepreneurs aged 18+ organized in groups of 5-30 members undertaking income-generating activities. Priority given to rural and peri-urban women.",
        "cost": "Free; revolving fund grant disbursed to qualifying women enterprise groups through registered SACCO accounts.",
        "steps": "1. Form or join a women enterprise group of 5-30 members with a shared business activity. 2. Register the group at your Sub-County/Division. 3. Open a group SACCO account. 4. Submit project proposal through your District Community Development Officer. 5. Await vetting by the District UWEP Committee.",
        "contacts": "District Community Development Officer / MGLSD Head Office, Simbamanyo House, George Street, Kampala."
    },
    {
        "id": "gov-maaif-009",
        "title": "MAAIF Agricultural Input Support & Extension Services",
        "agency": "Ministry of Agriculture, Animal Industry and Fisheries (MAAIF)",
        "stage": "Startup Stage", "sector": "Agriculture & Agribusiness",
        "eligibility": "Ugandan farmers and farmer groups engaged in food crop, cash crop, livestock, or fisheries production.",
        "cost": "Subsidized inputs (seeds, fertilizers, tools) at reduced cost. Extension services are free.",
        "steps": "1. Register with your Sub-County Agricultural Officer (SACO). 2. Join or form a farmer group recognized at sub-county level. 3. Receive free extension visits, demo farm access, and seasonal input packages. 4. Apply for the Agriculture Credit Facility (ACF) through a participating bank if larger financing is needed.",
        "contacts": "Sub-County Agricultural Officer (SACO) / MAAIF Headquarters, Entebbe Road, Entebbe / maaif.go.ug"
    },
    {
        "id": "gov-udb-010",
        "title": "Uganda Development Bank (UDB) MSME Loan Facility",
        "agency": "Uganda Development Bank (UDB)",
        "stage": "Growth Stage", "sector": "Manufacturing",
        "eligibility": "MSMEs in productive sectors including agriculture, manufacturing, agro-processing, tourism, and services. Must be registered with at least 2 years of operation and basic financial records.",
        "cost": "Concessionary interest rates from 12% to 15% per annum, significantly below commercial bank rates of 20-25%. Loan terms up to 10 years for capital investment.",
        "steps": "1. Prepare a business plan with financial projections. 2. Gather 2 years of financial records. 3. Contact UDB directly or through a participating financial institution. 4. Submit application for review by UDB credit team. 5. Collateral assessment and disbursement upon approval.",
        "contacts": "UDB Head Office, Crested Towers, Hannington Road, Kampala. Tel: +256 417 712 100 / udb.go.ug"
    },
    {
        "id": "gov-nitau-011",
        "title": "NITA-U Digital Innovation Hub Incubation & Grants",
        "agency": "National Information Technology Authority Uganda (NITA-U) / Ministry of ICT and National Guidance",
        "stage": "Startup Stage", "sector": "Digital & ICT",
        "eligibility": "Ugandan youth and entrepreneurs building digital or technology solutions for Ugandan market needs. Startups and SMEs developing innovative ICT products or services.",
        "cost": "Free incubation, co-working space, mentorship, and connectivity. Grant funding available for shortlisted innovations.",
        "steps": "1. Apply to the NITA-U Innovation Hub programme at nita.go.ug. 2. Submit your innovation concept describing the problem, solution, and target users. 3. Shortlisted applicants pitch to a panel of judges. 4. Winners receive grant funding plus a structured incubation programme and linkage to government procurement opportunities.",
        "contacts": "NITA-U, Palm Courts, Plot 7A Rotary Avenue, Kampala / nita.go.ug / +256 417 801 038"
    },
    {
        "id": "gov-uepb-012",
        "title": "UEPB Export Development & International Market Linkage",
        "agency": "Uganda Export Promotion Board (UEPB)",
        "stage": "Mature MSME Stage", "sector": "Agriculture & Agribusiness",
        "eligibility": "Ugandan businesses with export-ready products in agriculture, manufacturing, and services. Priority sectors include coffee, tea, horticulture, fish, and handicrafts.",
        "cost": "Free technical assistance and market information. Subsidized participation in international trade fairs.",
        "steps": "1. Register with UEPB as an exporter at uepb.go.ug. 2. Request an export readiness assessment. 3. Access UEPB buyer-linkage database for international markets. 4. Apply for subsidized trade fair participation (Europe, Middle East, East Africa annually). 5. Obtain guidance on certificate of origin and export documentation.",
        "contacts": "UEPB, Farmers House, Plot 2A Pilkington Road, Kampala / uepb.go.ug / +256 414 259 779"
    },
    {
        "id": "ngo-undp-013",
        "title": "UNDP Youth4Innovation Challenge Fund",
        "agency": "United Nations Development Programme (UNDP) Uganda / YouthConnekt Uganda",
        "stage": "Idea Stage", "sector": "Digital & ICT",
        "eligibility": "Ugandan youth aged 18-30 with innovative business ideas, particularly in digital, green economy, and creative sectors. Early-stage ventures also eligible.",
        "cost": "Free to apply. Successful applicants receive grant funding, mentorship, co-working access, and investor linkage at no cost.",
        "steps": "1. Monitor undp.org/uganda for the annual Youth4Innovation Challenge call for applications. 2. Submit a brief innovation concept (problem, solution, target users, sustainability). 3. Shortlisted applicants pitch to a panel of judges. 4. Winners receive grant funding plus a structured six-month incubation programme.",
        "contacts": "UNDP Uganda Office, Plot 617/618 Ntinda, Kampala / undp.org/uganda"
    },
    {
        "id": "ngo-spotlight-014",
        "title": "EU-UN Spotlight Initiative Vocational Skilling & Start-up Kits",
        "agency": "UNDP Uganda / European Union / Directorate of Industrial Training (DIT)",
        "stage": "Startup Stage", "sector": "Manufacturing",
        "eligibility": "Youth who have completed or are enrolled in vocational training in trades including plumbing, electrical installation, solar installation, fashion and design, baking, carpentry, and motor vehicle mechanics.",
        "cost": "Free -- training certification through DIT/UBTEB plus free start-up tool kits for qualifying graduates.",
        "steps": "1. Enrol in an accredited TVET institution in a qualifying trade. 2. Complete the course and sit for DIT or UBTEB certification. 3. Apply for start-up kit allocation through the programme district coordinator. 4. Formalize your youth enterprise group and get linked to PDM, UYLEP, and UWEP government funding.",
        "contacts": "Directorate of Industrial Training (DIT), Ministry of Education and Sports / dit.go.ug"
    },
    {
        "id": "ngo-fao-015",
        "title": "FAO Uganda Agri-Enterprise & Value Chain Development",
        "agency": "Food and Agriculture Organization of the United Nations (FAO) Uganda",
        "stage": "Growth Stage", "sector": "Agriculture & Agribusiness",
        "eligibility": "Smallholder farmers, farmer cooperatives, and agri-enterprises in priority value chains including coffee, maize, beans, rice, fish, and livestock.",
        "cost": "Free -- FAO provides technical assistance, market linkages, and input support through government and NGO partners at no direct cost to beneficiaries.",
        "steps": "1. Join a recognized farmer cooperative or producer organization in your value chain. 2. Register with your Sub-County Agricultural Officer to be linked to FAO-supported programmes. 3. Access climate-smart agriculture training, post-harvest handling support, and market linkage facilitation. 4. Apply for specific value chain grants through FAO national partner organizations.",
        "contacts": "FAO Uganda Country Office, Plot 88 Buganda Road, Kampala / fao.org/uganda / +256 414 339 680"
    }
]

# ------------------------------------------------------------------
# 5. Default Blueprint Database
# ------------------------------------------------------------------
DEFAULT_BLUEPRINT_DB = [
    {
        "id": "bp-retail-001",
        "title": "Urban General Merchandise Kiosk & Fast-Moving Retail Shop",
        "sector": "Trade & Retail", "tier": "Micro (Under UGX 5M)",
        "capital_required": "UGX 1,500,000 - UGX 3,500,000 (fast-moving stock, rent deposit, security grill, counter shelving)",
        "summary": "An operations blueprint for launching a high-turnover retail kiosk in dense urban neighborhoods, built around fast-moving stock (sugar, soap, cooking oil, rice) to maximize cash velocity.",
        "fin_lit_tip": "THE INVENTORY LEAK RAPID FIX: Never consume shop inventory for personal use without recording it as a cash purchase in your ledger. Micro-retail shops fail primarily because owners blend personal daily costs directly with store working capital float.",
        "success_case": "Generic composite blueprint modeled on common patterns across Kampala-area neighborhood retail startups — not tied to one named business.",
        "media_anchor": "No specific video anchor — this is a composite, not a single named case."
    },
    {
        "id": "bp-ict-002",
        "title": "Informal Marketplace Digital Transformation Strategy",
        "sector": "Digital & ICT", "tier": "Micro (Under UGX 5M)",
        "capital_required": "UGX 800,000 - UGX 2,000,000 (smartphone, data bundles, and onboarding to an e-commerce platform)",
        "summary": "Roadmap for how informal market vendors digitalize their inventories and fulfill orders through localized courier pipelines, modeled on a real documented programme.",
        "fin_lit_tip": "VIRTUAL OVERHEAD RESTRICTION: Do not rent a premium physical storefront while testing a new product line. Use pick-up points and direct-to-consumer social sales to preserve early working capital.",
        "success_case": "Verified: The UNDP Uganda & Jumia e-commerce partnership, launched May 2020, onboarded over 3,000 vendors across seven Kampala markets (Nakasero, Nakawa, Wandegeya, Bugolobi, Kalerwe, and others), with vendors reporting roughly doubled daily sales after joining.",
        "media_anchor": "Source: undp.org/uganda blog series on the UNDP-Jumia partnership — link the official UNDP article."
    },
    {
        "id": "bp-rabbit-003",
        "title": "Commercial Rabbit Breeding & Meat Processing",
        "sector": "Agriculture & Agribusiness", "tier": "Small (UGX 5M - 20M)",
        "capital_required": "UGX 7,000,000 - 8,000,000 initial investment (breeder stock, cages, startup feed), scalable via government-backed agribusiness credit",
        "summary": "A commercial rabbit breeding and processing model, incubated at the Uganda Industrial Research Institute (UIRI), using every part of the animal — meat, urine-based insecticide, and manure-based fertilizer.",
        "fin_lit_tip": "ASSET RE-INVESTMENT METRIC: Rabbits breed quickly, so early revenue can be reinvested fast. Building separate weaning cages for litters, rather than spending early profits personally, is what let this model scale past 1,000 rabbits.",
        "success_case": "Verified: Bendito Farm (Jeremy Musinguzi and Jessica Nabaasa), Luweero District. Started in 2016 with about UGX 7.5 million and 10 rabbits; received UGX 300 million in MSC support in 2017; reported a net profit of UGX 138 million by September 2018.",
        "media_anchor": "No independently verified video link found — recommend as a first candidate for EdgeLab's own interview engine."
    },
    {
        "id": "bp-log-004",
        "title": "Digital Bus-Ticketing Platform",
        "sector": "Logistics & Transport", "tier": "Small (UGX 5M - 20M)",
        "capital_required": "Primarily a technology and partnerships investment — platform development, mobile money integration, and on-the-ground agent presence at bus parks.",
        "summary": "A digital bus-ticket booking platform connecting travelers to existing bus operators across East Africa, removing the need to queue or risk counterfeit tickets, with a parallel B2B tool for bus owners.",
        "fin_lit_tip": "TRUST-BUILDING OVER PURE TECH: Early growth came from agents physically present at bus parks explaining the platform, not from advertising alone. For trust-sensitive transactions, a human presence at the point of friction matters more than the app itself.",
        "success_case": "Verified: Ronald Hakiza founded Ugabus in 2015-2016 after a personal bus-ticket scam, building it into Uganda's first digital bus-ticketing platform before its acquisition by Treepz. Hakiza has since founded a new venture, Vestafi. (Earlier drafts incorrectly described Ugabus as a motorcycle dispatch business — corrected here.)",
        "media_anchor": "Referenced in 'The Ugandan Podcast' episode on Uganda's innovation ecosystem (Dec 2025) — confirm and link the specific episode."
    },
    {
        "id": "bp-poultry-005",
        "title": "Commercial Layers Poultry Farming",
        "sector": "Agriculture & Agribusiness", "tier": "Medium/Commercial (UGX 20M+)",
        "capital_required": "Commercial-scale poultry housing, layer stock, and feed systems. (Specific capital figures not independently confirmed for this case — verify directly before publishing.)",
        "summary": "A commercial layers poultry operation used by its owner to demonstrate productive fund use by hosting Parish Development Model (PDM) beneficiaries for hands-on training, combining personal enterprise with community impact.",
        "fin_lit_tip": "DEMONSTRATION VALUE: A visible, working enterprise lets you train others by example. When PDM or Emyooga beneficiaries see a real operating model up close, proper fund use improves more than from instructions alone.",
        "success_case": "Verified: Hon. Esther Mbayo, Luuka District Woman MP, runs a poultry farm in the district and has hosted PDM fund beneficiaries there for training (NTV Uganda coverage, July 2023). (Earlier drafts added an unverified avocado component — removed here.)",
        "media_anchor": "Referenced in NTV Uganda coverage of PDM beneficiary training in Luuka (July 2023) — confirm and link the specific segment."
    },
    {
        "id": "bp-bakery-006",
        "title": "Commercial Cake Factory & Bakery Scaling",
        "sector": "Manufacturing", "tier": "Medium/Commercial (UGX 20M+)",
        "capital_required": "UGX 20,000,000+ (industrial ovens, mixers, workspace buildout, retail distribution points)",
        "summary": "Scaling roadmap transforming a domestic kitchen side-hustle into a multi-outlet national brand, focused on product consistency, institutional market linkages, and training culinary staff.",
        "fin_lit_tip": "CAPITAL STACKING & GRANTS: When operating a formal production unit, register your payroll and keep strict financial books — clean records are exactly what unlocks concessionary capital streams like the GROW project loans.",
        "success_case": "Verified: Brenda Sekabembe Mulema, Founder & CEO of Bake 4 Me Ltd, started in 2004 with about UGX 25,000 baking a single cake for a colleague. Bake 4 Me now operates multiple outlets and produced a wedding cake for the Kyabazinga of Busoga.",
        "media_anchor": "Verified: https://www.youtube.com/watch?v=e0mqTJNQxUc — 'How She Built Bake 4 Me Into a Multi-Million Cake Business in Uganda'"
    }
]

# ------------------------------------------------------------------
# 6. Default Financial Literacy Masterclass — Expanded & Uganda-Specific
# ------------------------------------------------------------------
DEFAULT_MASTERCLASS_DB = [
    # ---- IDEA STAGE ----
    {
        "id": "fl-001", "stage": "Idea Stage", "topic": "Saving & Emergency Funds",
        "summary": "Building personal savings before launching a business is your financial protection during the months when your new idea generates less income than expected — which is almost always true at first. Without a personal emergency buffer separate from your startup capital, the first unexpected expense forces you to pull money from the business or take on emergency debt at high cost. Even saving a small, consistent weekly amount over several months builds meaningful capital, and the habit matters as much as the amount. A good starting target is savings that could cover three to six months of your personal living expenses before you commit fully to the business.",
        "uganda_example": "MTN MoMo Save and Airtel Money savings wallets are accessible on any basic mobile phone in Uganda and earn interest on balances held — you do not need a bank account to start. Village Savings and Loan Associations (VSLAs) operate across most Ugandan communities, running three-month saving cycles where members contribute weekly from as little as UGX 2,000, leaving each cycle with a meaningful lump sum available for investment or emergencies.",
        "common_mistake": "Treating startup capital and personal emergency savings as the same fund. They serve two different purposes and one emergency will drain both if they are not kept separately from the start.",
        "action_tip": "Open a separate MTN MoMo Save or Airtel Money savings wallet today, set a fixed weekly contribution (even UGX 5,000), and treat it as locked for three months minimum."
    },
    {
        "id": "fl-002", "stage": "Idea Stage", "topic": "Credit, Loans & Borrowing",
        "summary": "Borrowing money to fund an idea that has not yet been tested with real paying customers is one of the most common ways early entrepreneurs in Uganda create serious financial problems. The issue is not borrowing itself — it is the timing. Debt has a fixed repayment schedule that does not adjust to your business performance, which means if the idea takes longer than expected, you are still obligated to repay regardless of how the business is doing. Find a way to prove that people will actually pay for what you are offering before you borrow a single shilling.",
        "uganda_example": "Informal lenders in Uganda — sometimes called Shylocks or ka-loan operators — charge between 20% and 50% interest per month. Even regulated Tier 4 microfinance institutions charge 2-5% per month. Taking any of these to fund an untested idea means your first revenue will go entirely to debt service rather than building the business. The Uganda Microfinance Regulatory Authority (UMRA) regulates Tier 4 lenders — always verify a lender's registration before borrowing.",
        "common_mistake": "Borrowing from an informal lender because the bank process feels too slow, then discovering the interest rate erases every shilling of early profit.",
        "action_tip": "Before approaching any lender, identify three ways to test whether people will actually pay for your idea for under UGX 100,000 total — if you cannot, the idea is not yet ready for debt."
    },
    {
        "id": "fl-003", "stage": "Idea Stage", "topic": "Budgeting & Cash Flow Management",
        "summary": "Budgeting before a business exists might feel unnecessary, but the financial habits you form now carry directly into how you manage money once the business is running and things get busier and more complex. A simple personal budget — tracking how much comes in and how much goes out each week — trains you to spot gaps early and make deliberate spending decisions rather than reactive ones. Most business budgets are just more detailed versions of this same skill. Starting now gives you months of practice before real business money is involved.",
        "uganda_example": "A simple weekly budget written in a notebook or tracked on a free phone app like Money Manager (available on Android in Uganda) takes about ten minutes and immediately shows where money is disappearing. Many entrepreneurs in Uganda are surprised to discover that small daily purchases — boda rides, airtime, small meals — account for 30-40% of their weekly spending once they actually write it down for the first time.",
        "common_mistake": "Waiting until the business starts to begin tracking money, then discovering the discipline is not there when it is needed most.",
        "action_tip": "Write down every shilling you spend this week — every single transaction, no matter how small — and review the full list on Sunday before the next week begins."
    },
    {
        "id": "fl-004", "stage": "Idea Stage", "topic": "Separating Personal and Business Money",
        "summary": "One of the most damaging habits among small business owners in Uganda is running personal and business money through the same mobile wallet or envelope. When this happens, it becomes structurally impossible to tell whether the business is actually profitable, because personal spending is silently eating into the margin. The habit of separation needs to start before the business launches — even if only a small amount of startup capital is involved — because introducing it later once real money is flowing is much harder to discipline. Two wallets, two records, from the first day.",
        "uganda_example": "Using a dedicated mobile money line for business — even a second SIM on the same phone — is a practical, low-cost way to enforce this separation in Uganda without needing a bank account. When all business receipts go into one number and all personal spending comes from another, your business performance becomes visible immediately without any accounting software. A second MTN or Airtel SIM can be registered at any authorized agent for free.",
        "common_mistake": "Using the same MTN MoMo wallet for airtime top-ups, household groceries, school fees, and business stock — making it impossible to ever know the true business profit or loss.",
        "action_tip": "Register a second MTN or Airtel SIM today and designate it exclusively for business money — commit that you will never use it for personal purchases, starting immediately."
    },
    {
        "id": "fl-005", "stage": "Idea Stage", "topic": "Investing & Growing Your Capital",
        "summary": "At the idea stage, your most valuable investment is not financial — it is the time you spend confirming whether your idea actually solves a real problem that people will pay to have solved. Spending money on a product, signage, or equipment before confirming this is one of the most common ways early capital disappears in Uganda. The cheapest test is almost always a conversation: talk to ten potential customers, try to collect even a small advance payment, and learn from both what they say and what they choose not to pay for.",
        "uganda_example": "Market vendors in Uganda regularly test a new product by placing it alongside their existing stock for one or two weeks before committing to a larger order — this is validation thinking in practice, even without knowing the term. A tailoring startup can take three small paid orders before buying a sewing machine. A food vendor can cook once for a market-day test before renting a stall full-time. The pattern is consistent among the most successful traders: confirm the market before committing the capital.",
        "common_mistake": "Spending the majority of startup capital on equipment, branding, or a shop space before a single customer has confirmed they will pay for the product.",
        "action_tip": "Identify the single cheapest version of your idea you could put in front of a real potential customer this week — and try to collect even a small payment from them before investing further."
    },
    {
        "id": "fl-new01", "stage": "Idea Stage", "topic": "Understanding SACCOs vs Banks",
        "summary": "Savings and Credit Cooperative Organizations (SACCOs) are not a poorer substitute for a bank — they are a different kind of financial institution that often suits the needs of early-stage entrepreneurs and informal traders better than commercial banks do. SACCOs pool member savings and lend back to members at relatively low interest rates, without requiring the collateral a bank demands. The key insight is that your borrowing capacity at a SACCO grows automatically as your savings history with them grows, which is why joining early and saving consistently matters more than most people realize.",
        "uganda_example": "Uganda has hundreds of registered SACCOs operating nationally, many of them sector-specific through the Emyooga programme — there is a SACCO category for market vendors, boda riders, tailors, salon operators, carpenters, fishermen, and more, organized at constituency level. PostBank Uganda also offers a SACCO-linkage product that allows SACCOs to manage their accounts formally. Your LC1 chairperson and District Commercial Officer can identify the active SACCO in your specific trade category and constituency.",
        "common_mistake": "Waiting until you urgently need a loan before joining a SACCO — by that point, you have no savings history with them and will not qualify for the loan size you actually need.",
        "action_tip": "Identify the Emyooga SACCO that matches your intended business category in your constituency and make your first savings contribution this month — the earlier your savings record starts, the earlier your borrowing eligibility builds."
    },
    {
        "id": "fl-new02", "stage": "Idea Stage", "topic": "Mobile Money & Digital Finance",
        "summary": "Mobile money is not just a payment tool — used deliberately, it is a basic financial system that is accessible to almost every Ugandan with a phone. MTN MoMo and Airtel Money together cover most of the country, and their savings wallets, merchant accounts, and payment tools offer genuine functionality for small businesses far beyond just sending and receiving cash. Understanding all of what mobile money can do for your business — beyond the basic transactions — is a practical financial skill that costs nothing to learn and can replace several expensive formal banking services at this early stage.",
        "uganda_example": "MTN MoMo Pay (formerly MoMo Merchant) allows you to receive payments directly from customers who scan a code, eliminating cash handling and automatically generating a digital transaction record. Airtel Money Business similarly lets you manage collections and supplier payments with a transaction history that is increasingly accepted by Ugandan banks as evidence of business revenue when you apply for a loan later. Building this record now costs nothing and creates future value.",
        "common_mistake": "Using mobile money only to receive and immediately withdraw cash, losing both the savings function and the transaction history that would have built your financial track record for free.",
        "action_tip": "Register for MTN MoMo Pay or Airtel Money Business and make it your default way of receiving even small payments — the transaction history you build now is a financial record you will need when applying for credit in twelve to eighteen months."
    },
    {
        "id": "fl-new03", "stage": "Idea Stage", "topic": "Insurance & Risk Protection",
        "summary": "Most early entrepreneurs do not think about insurance until after they have experienced a loss — a fire, theft, medical emergency — and discovered the cost of recovery is enough to permanently end the business they were just starting. Building even a basic personal risk buffer from the beginning is what separates entrepreneurs who survive one bad month from those who do not. At the idea stage, formal insurance may not be necessary, but a small locked emergency fund that is never touched except for genuine crises serves a similar purpose at near-zero cost.",
        "uganda_example": "NSSF voluntary membership is open to self-employed Ugandans outside formal employment, with a minimum monthly contribution of UGX 5,000 and no maximum. Starting now builds a long-term financial safety net using the government's tax-advantaged scheme. UAP Old Mutual Uganda, Jubilee Insurance, and APA Insurance also offer micro-health and micro-business policies at premiums as low as UGX 10,000 per month for basic coverage — a small but meaningful protection even at the idea stage.",
        "common_mistake": "Assuming that because the business idea is still small, nothing serious can go wrong — then discovering that one medical emergency or stolen test-batch inventory can eliminate months of accumulated savings.",
        "action_tip": "Set aside a fixed non-negotiable 'risk fund' each week — separate from your startup savings — and investigate NSSF voluntary membership online at nssf.or.ug as a starting point for longer-term protection."
    },

    # ---- STARTUP STAGE ----
    {
        "id": "fl-006", "stage": "Startup Stage", "topic": "Budgeting & Cash Flow Management",
        "summary": "A business can show strong sales numbers and still fail within months because of poor cash flow management — this is not theoretical, it is the most common operational cause of small business closure in Uganda. Cash flow means the timing of when money actually enters and leaves the business, not just the totals at the end of the month. If customers owe you money for thirty days but your suppliers want payment in seven days, you can be profitable on paper and still run out of operating cash. Tracking cash weekly — not just monthly — is what makes this problem visible before it becomes a crisis.",
        "uganda_example": "Many Kampala traders experience severe cash-flow pressure in January and after major school-fee payment periods, even when their annual revenue is healthy, because customers reduce spending while suppliers still expect payment on schedule. Traders who track their daily and weekly cash position can anticipate these gaps two to three weeks in advance and arrange a short-term facility from their Emyooga SACCO or Centenary Bank branch before they hit zero, rather than scrambling when it is already too late.",
        "common_mistake": "Tracking profit (revenue minus costs) but not cash flow (actual money in the account right now) — a business can be 'profitable' in total while the owner still needs to borrow daily to pay rent.",
        "action_tip": "Pick one fixed day each week to count actual cash on hand and compare it to what you expected — any gap needs to be understood and explained before the next week begins."
    },
    {
        "id": "fl-007", "stage": "Startup Stage", "topic": "Separating Personal and Business Money",
        "summary": "At the startup stage, separating personal and business money is no longer just a good habit — it is essential for knowing whether the business is actually viable. Mixing the two makes it structurally impossible to calculate profit, because personal withdrawals look identical to business expenses in the records. Many Ugandan entrepreneurs at this stage discover, once they properly separate accounts, that the business is making far less than they thought — or, sometimes, that it is making more, but they have been spending it before it could compound. Either way, the truth is more useful than comfortable confusion.",
        "uganda_example": "A practical working structure for a small business in Uganda: one mobile money line for all customer payments, one for supplier payments, and personal withdrawals taken as a fixed 'salary' on the same day each week or fortnight. This structure generates a meaningful profit-and-loss picture without any accounting software and without a bank account. Many successful Kampala traders operate this way from their first year of business.",
        "common_mistake": "Taking money from the business whenever it is needed personally without recording it — which eventually makes the business appear to be spending more than it earns, even when customers are paying regularly.",
        "action_tip": "Set a fixed weekly 'salary' you will pay yourself from the business, transfer it to your personal wallet on the same day every week, and treat everything left behind as belonging to the business — not to you."
    },
    {
        "id": "fl-008", "stage": "Startup Stage", "topic": "Credit, Loans & Borrowing",
        "summary": "At the startup stage, borrowing becomes more realistic and sometimes genuinely appropriate — but the discipline is to borrow only against something already proven to generate enough cash flow to repay the loan. The test is simple: could this month's revenue, at its current level without the loan, cover the repayments? If yes, borrowing to accelerate makes sense. If no, the borrowing is adding risk to a foundation that has not yet been proven, and one slow month could result in default. Start with the smallest possible loan size and prove you can manage repayment before scaling up the amount.",
        "uganda_example": "Centenary Bank's group lending products and FINCA Uganda's individual loans both operate across Uganda with repayment terms of three to twelve months. A UGX 500,000 loan at 3% per month for six months costs approximately UGX 90,000 in interest — meaning your business needs to generate at least UGX 90,000 in additional profit from the borrowed capital to break even on the borrowing decision. If it cannot, the loan makes you poorer, not richer.",
        "common_mistake": "Using a business loan to cover personal expenses or smooth a cash-flow gap rather than to purchase a specific asset or fund a specific revenue-generating activity — then finding there is nothing to show for the debt.",
        "action_tip": "Before signing for any loan, write down exactly what you will buy with it, how much additional revenue that purchase will generate per month, and confirm the revenue number is larger than the monthly repayment before you proceed."
    },
    {
        "id": "fl-009", "stage": "Startup Stage", "topic": "Record-Keeping & Bookkeeping",
        "summary": "Basic record-keeping at the startup stage is not primarily about tax compliance — it is about understanding your own business well enough to survive. Without records, you cannot tell whether your prices are set correctly, which products are actually profitable, whether a particular customer is worth the credit risk you are extending, or whether the business is genuinely growing. A simple cashbook — one column for money in, one for money out, reviewed every week — provides more business intelligence than most startup owners realize until they actually try it for one month.",
        "uganda_example": "Free mobile apps like Wave Accounting (available on Android in Uganda with basic bookkeeping features) or a shared Excel sheet can replace a physical cashbook for traders who move frequently. URA's Electronic Fiscal Receipting and Invoicing Solution (EFRIS) — required for VAT-registered businesses but useful as a habit earlier — also creates a digital transaction record automatically, which doubles as a basic bookkeeping system that is already formatted for tax compliance.",
        "common_mistake": "Keeping 'records' in memory or in unorganized mobile money transaction history rather than a structured format — making it impossible to answer basic business questions like 'what did I spend on stock this month?' without hours of searching.",
        "action_tip": "Start a simple cashbook today — a physical notebook divided into 'In' and 'Out' columns is enough — and enter every transaction on the same day it happens, not from memory at the end of the week."
    },
    {
        "id": "fl-010", "stage": "Startup Stage", "topic": "Investing & Growing Your Capital",
        "summary": "The most important investment decision for a startup business is how much of early profit to reinvest versus how much to withdraw for personal use. Withdrawing everything because the business 'just made money this week' is the most common way entrepreneurs in Uganda find themselves at exactly the same point six months later with no growth to show for the revenue. A useful starting structure is to reinvest at least half of early profit back into more stock, better equipment, or targeted marketing, and pay yourself a fixed modest salary regardless of weekly performance. Growth requires capital left inside the business long enough to compound.",
        "uganda_example": "A typical Kampala market vendor who makes UGX 300,000 profit in a good week and withdraws it all will still be running the same single stall three years later. A vendor who withdraws UGX 150,000 and reinvests UGX 150,000 into additional stock or a second product line will typically double their stall's revenue within twelve months — this pattern is visible among the most successful traders in Nakasero, Owino, and Kikuubo markets.",
        "common_mistake": "Treating all profit as personal income immediately, then needing to take a loan to restock or handle a slow period — effectively paying interest to replace capital that was already there and did not need to leave.",
        "action_tip": "Decide today what percentage of profit you will reinvest (at least 50% is recommended at startup stage) and treat that amount as belonging to the business, not to you, for the next six months."
    },
    {
        "id": "fl-new04", "stage": "Startup Stage", "topic": "Pricing Your Products/Services",
        "summary": "Getting pricing wrong at the startup stage is one of the most common silent killers of otherwise promising businesses in Uganda. Many entrepreneurs price to win customers by being cheaper, without calculating whether that price actually covers all costs and leaves a real margin — then work hard for months and discover they have been losing money on every sale. The correct starting point for any price is total cost plus a target margin, not 'what the competitor charges minus a little.' Underpricing is not a competitive strategy; it is a slow collapse disguised as busyness.",
        "uganda_example": "A biscuit maker in Uganda pricing at UGX 500 per pack to match a competitor might not have accounted for packaging, transport to market, production time, and waste. Once all these are included, the real cost might be UGX 450 — leaving only UGX 50 margin per pack, which cannot cover a slow week or any ingredient price increase. Knowing your true cost per unit before setting a price is not optional; it is the most basic financial discipline a business owner needs.",
        "common_mistake": "Setting prices based on what a competitor charges without knowing whether your own cost structure allows you to match them profitably — a competitor may have lower costs, different suppliers, or higher volume that justifies a price you cannot afford to match.",
        "action_tip": "List every single cost involved in producing or delivering one unit of your product or service, add them up, then add 30% minimum for your margin — that is your floor price, and you should charge more wherever the market will support it."
    },
    {
        "id": "fl-new05", "stage": "Startup Stage", "topic": "Understanding SACCOs vs Banks",
        "summary": "At the startup stage, a SACCO is often a better first financial partner than a commercial bank for one practical reason: SACCOs lend based on your savings history with them, while banks primarily lend based on collateral you may not yet have. If you joined a SACCO at the idea stage and have been saving consistently, your borrowing capacity has been building automatically without you needing land or property as security. The interest rates at well-managed SACCOs are also typically lower than microfinance institutions, though the loan amounts are limited by member savings levels.",
        "uganda_example": "Emyooga SACCOs in Uganda are organized by specific trade category — market vendors, boda riders, salon operators, tailors, carpenters, and more — meaning the other members understand your business because they are in the same trade. This peer knowledge also provides informal business advice and buyer referrals that a bank cannot offer. The Microfinance Support Centre oversees capitalization of these SACCOs and your District Commercial Officer can provide guidance on joining the right one.",
        "common_mistake": "Joining a SACCO only when you urgently need to borrow, with no prior savings history — then being disappointed that the available loan amount is too small to be useful for your current need.",
        "action_tip": "Confirm your savings balance with your SACCO this week and ask the manager what loan amount you currently qualify for based on your savings record — use that number to plan your next investment decision."
    },

    # ---- GROWTH STAGE ----
    {
        "id": "fl-011", "stage": "Growth Stage", "topic": "Investing & Growing Your Capital",
        "summary": "At the growth stage, the investment question is no longer whether to reinvest but what to invest in and in what sequence. The most common growth investment error in Uganda is expanding the operation — more stock, more staff, more locations — before the unit economics (profit per sale) of the current operation are fully understood and optimized. A business making thin margins on high volume at one location will make thin margins at two. Fix the margin first, then expand the volume — not the other way around.",
        "uganda_example": "A Kampala-based trader who adds a second market stall before understanding which product lines in the first stall drive the most profit frequently discovers the second stall performs worse, not better, because the same operational weaknesses replicate at scale. The traders who expand successfully in Nakasero and Owino markets are typically those who can clearly name their top three margin products and their minimum profitable order quantities before signing a second lease.",
        "common_mistake": "Treating revenue growth as business success without checking whether profit margin has grown proportionally — revenue can double while profit margin halves if cost control is not actively maintained during expansion.",
        "action_tip": "Calculate your gross profit margin (revenue minus direct cost of goods, divided by revenue) for this month before deciding on any expansion investment — if it is below 30%, fix that number first before adding more locations or stock."
    },
    {
        "id": "fl-012", "stage": "Growth Stage", "topic": "Saving & Emergency Funds",
        "summary": "At the growth stage, the emergency fund requirement changes in character — it is no longer just a personal survival buffer but a genuine business reserve covering operational costs during a disruption. A fire, a stock theft, a key supplier failing, or a sudden market contraction can all create a gap of several months where the business cannot generate normal revenue. A reserve covering three to four months of operating costs — rent, staff wages, and basic stock — is what separates businesses that survive serious shocks from those that do not.",
        "uganda_example": "The COVID-19 lockdown period in Uganda demonstrated clearly which businesses had reserves and which did not. Traders and entrepreneurs who had accumulated savings equivalent to two to three months of expenses were able to reduce operations while keeping their premises and core supplier relationships intact. Those with no reserves were often forced to terminate leases, dismiss staff, and restart from scratch when restrictions lifted — setting them back by years of accumulated progress.",
        "common_mistake": "Treating accumulated profit as a signal to immediately expand rather than first building a three-month operating reserve — then having no cushion when the first serious disruption hits.",
        "action_tip": "Calculate your average monthly operating costs (rent, wages, stock, utilities) and set a target to keep that amount multiplied by three in a reserve account that is never used for operations or personal withdrawal."
    },
    {
        "id": "fl-013", "stage": "Growth Stage", "topic": "Credit, Loans & Borrowing",
        "summary": "At the growth stage, formal borrowing from banks and larger microfinance institutions becomes not just possible but often strategically important for expansion capital that SACCO limits cannot provide. The critical discipline is comparing the true cost of borrowing — interest rate plus all fees plus the opportunity cost of any collateral tied up — against the realistic additional profit the expansion will actually generate. A loan at 25% annual interest that funds an expansion generating 40% additional profit is a sound decision; the same loan funding an expansion generating 15% additional profit is a trap.",
        "uganda_example": "Uganda Development Bank (UDB) offers credit facilities to MSMEs in agriculture, manufacturing, and services at interest rates significantly below commercial bank rates, with terms of up to ten years for capital investment. PSFU's GROW project targets women-led businesses with loan tiers from UGX 4 million to 200 million at approximately 10% annually — both are meaningfully cheaper than the 20-25% standard commercial bank rate for most SME borrowers in Uganda.",
        "common_mistake": "Borrowing from a commercial bank at 24% annual interest when a government-backed facility at 10-12% is available and accessible — often because the entrepreneur did not know the cheaper option existed or assumed they would not qualify.",
        "action_tip": "Before accepting any business loan offer, check whether you qualify for UDB facilities or the PSFU GROW project (for women-led businesses) — the interest rate difference over a three-year loan term can amount to millions of shillings."
    },
    {
        "id": "fl-014", "stage": "Growth Stage", "topic": "Record-Keeping & Bookkeeping",
        "summary": "Transitioning from a notebook cashbook to formal accounting records at the growth stage is not primarily about tax compliance — it changes the quality of decisions you are able to make about the business. Formal records reveal which product lines, customers, or locations are actually profitable and which are consuming resources without returning enough to justify the investment. They also make you bankable: banks, formal investors, and institutional buyers (supermarkets, hotels, government procurement) all require at least two years of clean financial records before engaging seriously, and those records cannot be produced retroactively.",
        "uganda_example": "QuickBooks and Wave Accounting (free for basic use) both have Uganda-specific tax settings and are widely used by growing Kampala-based SMEs. A part-time bookkeeper in Kampala typically costs UGX 200,000 to 400,000 per month — less than many business owners spend on airtime. Centenary Bank and DFCU both cite clean, consistent financial records as the most frequently missing document in loan applications from otherwise viable Ugandan businesses.",
        "common_mistake": "Continuing to manage accounts in a notebook because it has 'always worked,' then being unable to produce two-year financial statements when a major buyer, investor, or bank asks for them as a standard requirement.",
        "action_tip": "Move to a digital accounting tool this month — Wave Accounting is free for basic use and works on a phone — and enter at least the last three months of transactions to build a starting financial position."
    },
    {
        "id": "fl-015", "stage": "Growth Stage", "topic": "Risk, Diversification & Succession",
        "summary": "At the growth stage, most businesses are still heavily dependent on the founder's personal relationships, daily presence, and specific knowledge — which means the business and the person are effectively the same risk. If the founder falls ill, travels, or is unavailable for a month, revenue often drops to near zero. Beginning to build documented systems, train staff to make decisions independently, and develop at least one revenue stream that does not require the founder's personal involvement are the three most important risk-reduction moves at this stage.",
        "uganda_example": "Several established Ugandan businesses in retail and agriculture have moved toward a trusted second-in-command model — either a family member or a trained employee with authority to manage daily operations — specifically after experiencing a health crisis or family emergency that threatened the business. This transition often starts with one small step: giving a trusted staff member authority to make purchases up to a defined amount without the owner's prior approval.",
        "common_mistake": "Believing the business is stable because revenue is consistent, while all of that revenue depends on the owner personally showing up every day — this is not stability, it is a demanding job with extra administrative steps.",
        "action_tip": "Identify one decision you make daily that you could teach someone else to make, document the criteria for that decision in writing, and let that person make it for two weeks with you only reviewing afterward — not intervening."
    },
    {
        "id": "fl-new06", "stage": "Growth Stage", "topic": "Pricing Your Products/Services",
        "summary": "At the growth stage, pricing strategy becomes more sophisticated than at startup — you now have enough sales history to know which customers are most profitable, which product margins cover your fixed costs most efficiently, and where competitors are positioning their prices. This data should actively inform your prices rather than being set once and never revisited. Inflation, supplier cost increases, and growing operational costs all erode margins silently unless prices are reviewed on a deliberate schedule — typically every three to six months for Ugandan businesses where costs shift with fuel prices and exchange rate movements.",
        "uganda_example": "The depreciation of the Uganda shilling against the US dollar periodically increases the cost of imported goods — electronics, some food ingredients, packaging materials — in ways that are not immediately visible if price reviews are infrequent. Traders who anchor prices to a mental cost figure from twelve months ago while their actual purchase cost has risen 15-20% are effectively offering a discount they can no longer afford, even though it appears on the surface that nothing has changed.",
        "common_mistake": "Setting prices once during the startup phase and never formally reviewing them, then wondering why margins are shrinking despite revenue holding steady — the costs have been creeping up while the prices stayed fixed.",
        "action_tip": "Schedule a formal price review for the first week of every quarter, recalculate your cost per unit using current supplier prices, and adjust your prices before the margin erosion compounds further."
    },
    {
        "id": "fl-new07", "stage": "Growth Stage", "topic": "Insurance & Risk Protection",
        "summary": "At the growth stage, the range of risks that can seriously damage the business expands alongside the business itself — larger stock means higher fire and theft exposure, more staff creates payroll obligations during revenue gaps, and physical premises create liability. Formal insurance at this scale is not just prudent risk management — it is increasingly expected by institutional buyers, banks, and partnership agreements. A business fire or major stock theft event that would have been survivable at startup can be terminal at the growth stage if there is no insurance in place.",
        "uganda_example": "UAP Old Mutual Uganda, Jubilee Insurance, and APA Insurance all offer SME-specific insurance products covering stock, equipment, fire, and theft. For a business with UGX 20 million in stock, a basic stock insurance policy might cost UGX 300,000 to 500,000 annually — a fraction of the replacement cost of a single theft or fire incident. Workers Compensation Insurance is also legally required under Uganda's Workers Compensation Act for any business with employees, with fines for non-compliance.",
        "common_mistake": "Carrying no formal insurance past the startup stage, when the potential loss per incident has grown to a size that no personal reserve could realistically absorb in one event.",
        "action_tip": "Request a quote from at least two Uganda-registered insurers for your main business risks — stock, equipment, and fire — this month, and factor the annual premium into your operating budget as a fixed cost."
    },

    # ---- MATURE MSME STAGE ----
    {
        "id": "fl-016", "stage": "Mature MSME Stage", "topic": "Risk, Diversification & Succession",
        "summary": "A mature business that remains entirely dependent on one product, one market, or one key individual is more fragile than it appears from the outside. True business maturity means the enterprise can survive the loss of its biggest customer, the illness of its founder, or a disruption in its primary supply chain without entering a crisis. Achieving this requires deliberate diversification — a second product line, a second customer segment, a second key supplier — and documented succession arrangements that go beyond informal understanding between family members.",
        "uganda_example": "Several established Ugandan family businesses have navigated founder succession with varying degrees of success. Those that prepared governance structures — boards, documented management procedures, professionally managed finance functions — before the transition were significantly more likely to remain profitable through it. The pattern is visible across manufacturing businesses in Jinja and Kampala where second-generation management has succeeded or struggled based on how much was formalized before the handover.",
        "common_mistake": "Assuming that because the business 'runs itself now,' succession is not urgent — then discovering that most of what makes it run is the founder's personal relationships and institutional memory that was never written down.",
        "action_tip": "List the three things that would stop working immediately if you were unavailable for six months — those are your three highest-priority succession risks, and each one needs a named person and a documented process assigned to it."
    },
    {
        "id": "fl-017", "stage": "Mature MSME Stage", "topic": "Investing & Growing Your Capital",
        "summary": "At the mature stage, the investment question shifts from 'how do I grow the business' to 'how do I ensure what the business has built translates into lasting personal and family wealth.' A business that has generated strong returns for ten years but holds all of that value inside one company, one sector, or one building is not diversified wealth — it is a concentrated bet that looks successful until something goes wrong with that one asset. Moving a portion of accumulated business capital into different asset classes is not abandoning the business; it is protecting what the business built.",
        "uganda_example": "The Uganda Securities Exchange (USE) offers access to listed equities including Stanbic Bank Uganda, MTN Uganda, Uganda Clays, and others representing different economic sectors. Unit Trusts operated by UAP Old Mutual Uganda and ICEA Lion Asset Management provide professionally managed investment exposure without requiring direct stock-market knowledge. Real estate in growing secondary towns — Mbarara, Gulu, Mbale, Fort Portal — has also historically generated strong capital appreciation for Ugandan investors who entered early and held through the development cycle.",
        "common_mistake": "Reinvesting 100% of mature business profits back into the same business indefinitely, concentrating all personal wealth in one asset and one sector, then having no buffer when that sector faces a structural disruption.",
        "action_tip": "Identify one asset class outside your current business — listed equities via a stockbroker, a unit trust, or property — and invest a fixed percentage of this quarter's profit into it as a non-negotiable standing transfer, not a decision made month by month."
    },
    {
        "id": "fl-018", "stage": "Mature MSME Stage", "topic": "Tax & Compliance Awareness",
        "summary": "At the mature stage, tax compliance is not just a legal obligation — it is a strategic asset with real commercial value. A clean, audited tax compliance record is one of the strongest signals a business can send to a bank, formal investor, or institutional buyer, and in Uganda it directly affects access to government procurement (which requires a valid Tax Clearance Certificate from URA), preferential bank lending rates, and the ability to participate in formal supply chains that require documented financial accountability. Legal tax planning — understanding allowable deductions, capital allowances, and available exemptions — can meaningfully reduce your effective tax rate without any risk of non-compliance.",
        "uganda_example": "URA's domestic tax division offers a taxpayer advisory service, and several professional tax consulting firms in Kampala provide reviews for SMEs that regularly identify unused deductions or incorrectly classified expenses. The three-year income tax holiday available to qualifying new businesses under the Income Tax Act is a commonly overlooked benefit. Clean compliance records also directly unlock URA's Authorised Economic Operator status for export-oriented businesses, which provides expedited customs processing.",
        "common_mistake": "Treating tax compliance as purely a cost to minimize rather than as a business tool — then missing procurement opportunities because there is no current Tax Clearance Certificate, or paying higher loan interest because the compliance record could not be independently verified.",
        "action_tip": "Schedule a one-hour session with a qualified Ugandan tax professional this quarter — not to file returns, but specifically to identify any legal deductions, exemptions, or structural options you are currently not using."
    },
    {
        "id": "fl-019", "stage": "Mature MSME Stage", "topic": "Saving & Emergency Funds",
        "summary": "The owner-withdrawal question at the mature stage is one of the most important financial management decisions a Ugandan entrepreneur faces, and it is almost never explicitly planned. Many mature business owners find themselves generating real profit but with little personal financial security outside the business, because profit was always either reinvested or spent personally before it could accumulate. A deliberate, consistent policy — specifying what percentage of profit goes to personal savings, what percentage goes to business reserves, and what percentage goes to reinvestment — is what makes a business owner genuinely wealthy rather than just business-rich.",
        "uganda_example": "NSSF Uganda is open to self-employed Ugandans through voluntary contribution, with a minimum monthly contribution of UGX 5,000 and no maximum — for a mature business owner who has never been formally employed, starting voluntary NSSF contributions now builds long-term retirement security using the government's tax-advantaged scheme. PostBank Uganda's fixed deposit accounts and unit trust products offered through UAP Old Mutual and ICEA Lion also provide structured personal wealth accumulation vehicles that are entirely separate from the business.",
        "common_mistake": "Conflating 'the business is doing well' with 'I am financially secure' — the business is an asset, not a bank account, and its value can change faster than a savings balance in the wrong economic conditions.",
        "action_tip": "Decide this month your three-way profit split — specific percentages to: personal savings and wealth, business operating reserve, and reinvestment — and treat it as a standing policy applied every quarter, not a decision made case by case."
    },
    {
        "id": "fl-020", "stage": "Mature MSME Stage", "topic": "Record-Keeping & Bookkeeping",
        "summary": "At the mature stage, the transition from bookkeeping to governance-level financial management means the owner is no longer the person doing the accounts — but should absolutely be the person regularly reading and interrogating them. The risk at this stage is delegation without oversight: handing the finance function to a staff member or external accountant and only looking at the numbers when something has already gone wrong. Governance-level financial review means reading management accounts monthly, understanding the key ratios, and asking specific questions rather than accepting summary reassurances.",
        "uganda_example": "Several documented fraud cases in Ugandan small businesses — including payroll fraud, stock theft, and supplier collusion — have occurred specifically at the mature stage when the founder stopped personally reviewing financial records. A monthly management accounts review combined with occasional surprise stock counts is a basic internal control that businesses of this scale should have formalized. The Institute of Certified Public Accountants of Uganda (ICPAU) can provide referrals to qualified professionals for independent review.",
        "common_mistake": "Delegating the finance function entirely and only reviewing figures quarterly or annually — by which time any fraud, error, or margin deterioration has had months to compound into a much larger problem.",
        "action_tip": "Block time in your calendar on the same day each month to sit with your accountant and review a one-page management accounts summary — revenue, gross profit, cash balance, debtors, creditors — and ask at least three specific questions each time."
    },
    {
        "id": "fl-new08", "stage": "Mature MSME Stage", "topic": "Insurance & Risk Protection",
        "summary": "At the mature stage, insurance needs extend well beyond protecting physical assets — business interruption insurance, key-man insurance (covering the business against the financial impact of losing a critical person), directors and officers liability, and professional indemnity are all relevant at this scale. The cost of comprehensive cover as a percentage of business value is typically small, while an uninsured major incident can eliminate a decade of accumulated value in a single event. A formal annual insurance review should be a standing governance item at this stage.",
        "uganda_example": "UAP Old Mutual Uganda and Jubilee Insurance both offer business interruption policies that cover lost revenue during periods when the business cannot operate due to fire, flood, or other covered events — allowing staff salaries and fixed costs to continue being paid while the physical business rebuilds. Key-man insurance specifically covers the financial impact if the founder or a critical staff member becomes unable to work, which is one of the most overlooked risks in Ugandan family businesses that have grown dependent on specific individuals.",
        "common_mistake": "Insuring the physical assets — stock, equipment, building — but not the revenue stream that those assets generate, then discovering after a covered fire that the policy covers replacement cost of goods but not the six months of lost sales while the business rebuilds and restores customer confidence.",
        "action_tip": "Ask your current insurer specifically about business interruption coverage and key-man insurance at your next renewal — if they do not offer these products at your scale, request comparative quotes from UAP Old Mutual Uganda and Jubilee Insurance before renewing."
    },
]

CHECKIN_RULES = {
    "cash_flow_negative": ["Budgeting & Cash Flow Management", "Saving & Emergency Funds"],
    "no_separation": ["Separating Personal and Business Money", "Record-Keeping & Bookkeeping"],
    "no_savings": ["Saving & Emergency Funds", "Mobile Money & Digital Finance"],
    "considering_loan": ["Credit, Loans & Borrowing", "Understanding SACCOs vs Banks"],
}

# ------------------------------------------------------------------
# 7. PDF Generation Functions
# ------------------------------------------------------------------
def _sanitize_for_pdf(text):
    """Convert characters outside Latin-1 range to ASCII equivalents.
    fpdf2 with built-in Helvetica font only supports Latin-1.  All
    em-dashes, curly quotes etc. in the masterclass content need to be
    replaced before writing to the PDF — the Streamlit display is
    unaffected and keeps the original characters."""
    if not text:
        return ""
    return (str(text)
            .replace("\u2014", "--")   # em dash
            .replace("\u2013", "-")    # en dash
            .replace("\u2018", "'")    # left single quote
            .replace("\u2019", "'")    # right single quote
            .replace("\u201c", '"')    # left double quote
            .replace("\u201d", '"')    # right double quote
            .replace("\u2026", "...")  # horizontal ellipsis
            .encode("latin-1", errors="replace")
            .decode("latin-1"))


def _pdf_header(pdf, line1, line2=""):
    pdf.set_fill_color(31, 58, 95)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, line1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
    if line2:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, line2, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_text_color(0, 0, 0)


def _pdf_section(pdf, title, content, title_color=(31, 58, 95)):
    if not content:
        return
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*title_color)
    pdf.multi_cell(0, 6, _sanitize_for_pdf(title) + ":", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 5, _sanitize_for_pdf(content), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def _pdf_footer(pdf):
    pdf.set_y(-18)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 4, f"Edge Lab Platform | @edgelabanalytics | {datetime.now().strftime('%d %B %Y')}",
             align="C", new_x="LMARGIN", new_y="NEXT")


def generate_qr_png(url):
    """Generate a QR code PNG for a given URL. Returns PNG bytes or None."""
    if not QR_AVAILABLE:
        return None
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1F3A5F", back_color="white")
    buf = QRBytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_gov_card_pdf(card, profile=None):
    if not PDF_AVAILABLE:
        return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=20)
    _pdf_header(pdf, "EDGE LAB PLATFORM | Uganda MSME Gateway", "Official Government Service Card")
    pdf.set_font("Helvetica", "B", 13)
    pdf.multi_cell(0, 7, _sanitize_for_pdf(card.get("title", "")), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(90, 90, 90)
    pdf.multi_cell(0, 5, _sanitize_for_pdf(f"Managing Agency: {card.get('agency', '')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_draw_color(180, 144, 64)
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    _pdf_section(pdf, "Who Qualifies", card.get("eligibility", ""))
    _pdf_section(pdf, "Steps to Take", card.get("steps", ""))
    _pdf_section(pdf, "Cost", card.get("cost", ""))
    _pdf_section(pdf, "Contact", card.get("contacts", ""))
    if profile and profile.get("district"):
        pdf.ln(2)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Printed for: {profile.get('name', 'Citizen')} | District: {profile['district']}",
                 new_x="LMARGIN", new_y="NEXT")
    _pdf_footer(pdf)
    return bytes(pdf.output())


def generate_masterclass_pdf(lesson, profile=None, local_context=""):
    if not PDF_AVAILABLE:
        return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=20)
    _pdf_header(pdf, "EDGE LAB | Financial Literacy Masterclass",
                f"Stage: {lesson.get('stage', '')} | Topic: {lesson.get('topic', '')}")
    pdf.set_font("Helvetica", "B", 13)
    pdf.multi_cell(0, 7, lesson.get("topic", ""), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_draw_color(180, 144, 64)
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    _pdf_section(pdf, "What You Need to Know", lesson.get("summary", ""))
    _pdf_section(pdf, "In Uganda", lesson.get("uganda_example", ""))
    if local_context:
        _pdf_section(pdf, "In Your Area", local_context)
    _pdf_section(pdf, "Common Mistake to Avoid", lesson.get("common_mistake", ""), title_color=(180, 0, 0))
    _pdf_section(pdf, "Do This Now", lesson.get("action_tip", ""), title_color=(0, 120, 0))
    _pdf_footer(pdf)
    return bytes(pdf.output())


def generate_blueprint_pdf(bp, profile=None):
    if not PDF_AVAILABLE:
        return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=20)
    _pdf_header(pdf, "EDGE LAB | 'It Works. Try It.' Business Blueprint",
                f"Sector: {bp.get('sector', '')} | {bp.get('tier', '')}")
    pdf.set_font("Helvetica", "B", 13)
    pdf.multi_cell(0, 7, bp.get("title", ""), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_draw_color(180, 144, 64)
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    _pdf_section(pdf, "Estimated Capital Required", bp.get("capital_required", ""))
    _pdf_section(pdf, "Business Model Summary", bp.get("summary", ""))
    _pdf_section(pdf, "Financial Literacy Tip", bp.get("fin_lit_tip", ""))
    _pdf_section(pdf, "Proof It Works", bp.get("success_case", ""), title_color=(0, 120, 0))
    if bp.get("media_anchor"):
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 4, _sanitize_for_pdf(f"Video Resource: {bp.get('media_anchor', '')}"), new_x="LMARGIN", new_y="NEXT")
    _pdf_footer(pdf)
    return bytes(pdf.output())


def generate_digest_pdf(gov_cards, blueprint_cards, masterclass_cards, district=""):
    if not PDF_AVAILABLE:
        return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.set_fill_color(31, 58, 95)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "EDGE LAB PLATFORM", fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    label = f"Weekly Knowledge Digest | {district} | {datetime.now().strftime('%B %Y')}" if district else f"Weekly Knowledge Digest | {datetime.now().strftime('%B %Y')}"
    pdf.cell(0, 7, label, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4,
                   "Available at your LC1 office. Scan the Edge Lab QR code for the full interactive version with PDF downloads for every card.",
                   align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    def section_bar(label, r, g, b):
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, label, fill=True, align="L", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

    section_bar("GOVERNMENT SERVICES & OPPORTUNITIES", 31, 58, 95)
    for card in gov_cards[:3]:
        pdf.set_font("Helvetica", "B", 10)
        pdf.multi_cell(0, 5, f"* {card.get('title', '')}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8)
        pdf.multi_cell(0, 4,
                       f"  Agency: {card.get('agency', '')} | Cost: {card.get('cost', '')} | Contact: {card.get('contacts', '')}",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    pdf.ln(3)

    section_bar("'IT WORKS. TRY IT.' BUSINESS BLUEPRINTS", 180, 144, 64)
    for bp in blueprint_cards[:2]:
        pdf.set_font("Helvetica", "B", 10)
        pdf.multi_cell(0, 5, f"* {bp.get('title', '')} ({bp.get('tier', '')})", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8)
        pdf.multi_cell(0, 4, _sanitize_for_pdf(f"  Capital: {bp.get('capital_required', '')[:90]}"), new_x="LMARGIN", new_y="NEXT")
        case = _sanitize_for_pdf(bp.get('success_case', '')[:130])
        pdf.multi_cell(0, 4, f"  {case}...", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    pdf.ln(3)

    section_bar("FINANCIAL LITERACY MASTERCLASS", 0, 100, 60)
    for lesson in masterclass_cards[:3]:
        pdf.set_font("Helvetica", "B", 10)
        pdf.multi_cell(0, 5, f"* {lesson.get('topic', '')} ({lesson.get('stage', '')})",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8)
        summary = _sanitize_for_pdf(lesson.get('summary', '')[:160])
        pdf.multi_cell(0, 4, f"  {summary}...", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "B", 8)
        pdf.multi_cell(0, 4, _sanitize_for_pdf(f"  Do This: {lesson.get('action_tip', '')}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    pdf.ln(3)

    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, "HOW TO ACCESS FULL INFORMATION:", fill=True, align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(0, 4,
                   "1. Scan the Edge Lab QR code at this LC1 office.  2. Select your business stage and sector.  3. Browse government services, business blueprints, and financial literacy lessons.  4. Download any individual card as a printable PDF to keep.",
                   new_x="LMARGIN", new_y="NEXT")

    _pdf_footer(pdf)
    return bytes(pdf.output())


# ------------------------------------------------------------------
# 8. JSON Persistence Utilities
# ------------------------------------------------------------------
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    save_json(path, default)
    return [dict(item) for item in default]


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ------------------------------------------------------------------
# 9. Session State Initialization
#    User profile is session-state ONLY (not persisted to file) so
#    each browser session/device gets its own independent profile —
#    correct for a shared-URL multi-citizen access pattern.
# ------------------------------------------------------------------
if "gov_db" not in st.session_state:
    st.session_state.gov_db = load_json(GOV_DB_FILE, DEFAULT_GOV_DB)
if "blueprint_db" not in st.session_state:
    st.session_state.blueprint_db = load_json(BLUEPRINT_DB_FILE, DEFAULT_BLUEPRINT_DB)
if "masterclass_db" not in st.session_state:
    st.session_state.masterclass_db = load_json(MASTERCLASS_DB_FILE, DEFAULT_MASTERCLASS_DB)
if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = load_json(FEEDBACK_FILE, [])
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}

# Prefill state (Feature 1 — ID Scanner)
for _k, _v in [("prefill_name", ""), ("prefill_district", ""),
                ("prefill_region", ""), ("prefill_gender", ""),
                ("id_scanned", False), ("last_voice_query", "")]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ------------------------------------------------------------------
# 10. Sidebar
# ------------------------------------------------------------------
st.sidebar.markdown("## 🇺🇬 EDGE LAB PLATFORM")
st.sidebar.caption("National MSME & Youth Opportunity Knowledge Infrastructure")

profile = st.session_state.user_profile
if profile.get("name"):
    st.sidebar.write("---")
    st.sidebar.markdown(f"**👋 Hello, {profile['name']}**")
    if profile.get("district"):
        st.sidebar.caption(f"📍 {profile['district']}")
    if profile.get("stage"):
        st.sidebar.caption(f"🏢 {profile['stage']}")
st.sidebar.write("---")

view = st.sidebar.radio(
    "Select View:",
    [
        "👤 My Profile / Register",
        "📱 Citizen WhatsApp Simulator",
        "📟 Citizen USSD Simulator",
        "🏛️ Government Admin CMS Portal",
        "📊 Gov Intelligence Dashboard"
    ]
)

st.sidebar.write("---")
st.sidebar.markdown("### 🛠️ Developer Controls")
if st.sidebar.button("🔄 Reset Content Databases"):
    save_json(GOV_DB_FILE, DEFAULT_GOV_DB)
    save_json(BLUEPRINT_DB_FILE, DEFAULT_BLUEPRINT_DB)
    save_json(MASTERCLASS_DB_FILE, DEFAULT_MASTERCLASS_DB)
    save_json(FEEDBACK_FILE, [])
    st.session_state.gov_db = load_json(GOV_DB_FILE, DEFAULT_GOV_DB)
    st.session_state.blueprint_db = load_json(BLUEPRINT_DB_FILE, DEFAULT_BLUEPRINT_DB)
    st.session_state.masterclass_db = load_json(MASTERCLASS_DB_FILE, DEFAULT_MASTERCLASS_DB)
    st.session_state.feedback_log = []
    st.rerun()

# ------------------------------------------------------------------
# 11. Helpers
# ------------------------------------------------------------------
def get_local_context(district):
    region = get_user_region(district)
    return REGION_SAVINGS_CONTEXT.get(region, "") if region else ""


# ==================================================================
# VIEW 0: PROFILE / REGISTRATION
# ==================================================================
if view == "👤 My Profile / Register":
    inject_css()
    branded_header('My Profile', 'Personalise your experience')
    st.title("👤 Your Profile")
    st.caption("Personalise your experience. Telling us your district and business stage means every tab shows content most relevant to you. This information stays only in your current browser session — nothing is stored on a server or shared with anyone.")

    if not profile.get("name"):
        st.info("You have not set up a profile yet. Fill in the form below — it takes 30 seconds and you can change anything at any time.")

    # ──────────────────────────────────────────────────────────────
    # FEATURE 1: NATIONAL ID SCANNER
    # ──────────────────────────────────────────────────────────────
    with st.expander(
        "🪪 **Quick Fill — Scan Your National ID** *(fastest way to fill the form below)*",
        expanded=not st.session_state["id_scanned"]
    ):
        st.caption("Point your camera at the front of your ID or upload a photo. Your ID is used only to fill this form — no NIN is collected or stored anywhere.")
        st.info("✅ Only your **Name, District and Gender** are read from the ID. Everything else stays with you.")

        scan_tab, upload_tab = st.tabs(["📸 Use Camera", "📁 Upload Photo"])

        with scan_tab:
            st.caption("Hold your ID flat in good lighting. Capture the front side first.")
            col_f, col_b = st.columns(2)
            with col_f:
                front_cam = st.camera_input("Front of ID", key="cam_front")
            with col_b:
                st.camera_input("Back of ID (optional)", key="cam_back")

            if front_cam and not st.session_state["id_scanned"]:
                with st.spinner("🔍 Reading your ID..."):
                    result = scan_national_id_with_gemini(front_cam)
                if result and "error" not in result:
                    st.session_state["prefill_name"]     = result.get("given_names") or ""
                    st.session_state["prefill_district"] = result.get("district") or ""
                    _r = get_user_region(result.get("district") or "")
                    st.session_state["prefill_region"]   = _r or ""
                    _s = (result.get("sex") or "").strip()
                    st.session_state["prefill_gender"]   = _s if _s in ["Male", "Female"] else "Prefer not to say"
                    st.session_state["id_scanned"]       = True
                    st.success("✅ ID read! Scroll down — the form has been filled. Edit anything before saving.")
                    st.rerun()
                else:
                    st.warning(f"⚠️ Could not read ID clearly. Try better lighting or use the upload tab. ({result.get('error','')})")

        with upload_tab:
            st.caption("Upload a clear photo of your National ID (JPG or PNG).")
            col1u, col2u = st.columns(2)
            with col1u:
                front_up = st.file_uploader("Front of ID", type=["jpg", "jpeg", "png"], key="up_front")
            with col2u:
                st.file_uploader("Back of ID (optional)", type=["jpg", "jpeg", "png"], key="up_back")

            if front_up and not st.session_state["id_scanned"]:
                with st.spinner("🔍 Reading your ID..."):
                    result = scan_national_id_with_gemini(front_up)
                if result and "error" not in result:
                    st.session_state["prefill_name"]     = result.get("given_names") or ""
                    st.session_state["prefill_district"] = result.get("district") or ""
                    _r = get_user_region(result.get("district") or "")
                    st.session_state["prefill_region"]   = _r or ""
                    _s = (result.get("sex") or "").strip()
                    st.session_state["prefill_gender"]   = _s if _s in ["Male", "Female"] else "Prefer not to say"
                    st.session_state["id_scanned"]       = True
                    st.success("✅ ID read! Scroll down — the form has been filled. Edit anything before saving.")
                    st.rerun()
                else:
                    st.warning(f"⚠️ Could not read ID clearly. Try a clearer photo. ({result.get('error','')})")

        if st.session_state["id_scanned"]:
            col_msg, col_btn = st.columns([3, 1])
            with col_msg:
                st.success("✅ Form auto-filled from your ID. Check below and edit anything before saving.")
            with col_btn:
                if st.button("🔄 Rescan"):
                    for _k in ["prefill_name", "prefill_district", "prefill_region", "prefill_gender"]:
                        st.session_state[_k] = ""
                    st.session_state["id_scanned"] = False
                    st.rerun()

    st.write("---")
    if st.session_state["id_scanned"]:
        st.markdown("### ✏️ Your Profile *(auto-filled from ID — edit anything, then save)*")
    else:
        st.markdown("### ✏️ Tell us about yourself")

    # ──────────────────────────────────────────────────────────────
    # PROFILE FORM — with ID-prefill support
    # ──────────────────────────────────────────────────────────────
    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            # NAME — pre-filled from ID scan if available
            _default_name = profile.get("name") or st.session_state["prefill_name"]
            f_name = st.text_input("First name:", value=_default_name, placeholder="e.g. Sarah")

            # REGION — pre-filled from district lookup
            _region_opts   = ["Select Region"] + list(DISTRICTS_BY_REGION.keys())
            _saved_region  = profile.get("region", "")
            _pre_region    = st.session_state["prefill_region"]
            _region_val    = _saved_region if _saved_region in _region_opts else _pre_region
            _region_idx    = _region_opts.index(_region_val) if _region_val in _region_opts else 0
            f_region = st.selectbox("Your region:", _region_opts, index=_region_idx)

            # DISTRICT — pre-filled from ID, filtered by selected region
            districts_for_region = DISTRICTS_BY_REGION.get(f_region, []) if f_region != "Select Region" else []
            district_opts        = ["Select District"] + districts_for_region
            _saved_district      = profile.get("district", "")
            _pre_district        = st.session_state["prefill_district"]
            _district_val        = _saved_district if _saved_district in district_opts else _pre_district
            _district_idx        = district_opts.index(_district_val) if _district_val in district_opts else 0
            f_district = st.selectbox("Your district:", district_opts, index=_district_idx)

            f_stage = st.selectbox(
                "Your current business stage:",
                ["Select Stage"] + STAGES,
                index=(STAGES.index(profile["stage"]) + 1) if profile.get("stage") in STAGES else 0
            )

        with col2:
            f_sector = st.selectbox(
                "Your main sector of interest (optional):",
                ["Not sure yet"] + SECTORS,
                index=(SECTORS.index(profile["sector"]) + 1) if profile.get("sector") in SECTORS else 0
            )

            # GENDER — pre-filled from ID scan if available
            _gender_opts  = ["Prefer not to say", "Female", "Male"]
            _saved_gender = profile.get("gender", "Prefer not to say")
            _pre_gender   = st.session_state["prefill_gender"]
            _gender_val   = _saved_gender if _saved_gender in _gender_opts else _pre_gender
            _gender_idx   = _gender_opts.index(_gender_val) if _gender_val in _gender_opts else 0
            f_gender = st.selectbox(
                "Gender (optional — helps us flag relevant grants like GROW/UWEP):",
                _gender_opts, index=_gender_idx
            )

            f_phone = st.text_input(
                "Phone number (optional — for future WhatsApp reminder opt-in):",
                value=profile.get("phone", ""),
                placeholder="e.g. 0772 000 000"
            )

        st.caption("No NIN or national ID is collected here. This profile is stored only in your current browser session.")

        if st.form_submit_button("💾 Save My Profile"):
            if not f_name.strip():
                st.warning("Please enter your first name.")
            elif f_district == "Select District" or f_region == "Select Region":
                st.warning("Please select your region and district.")
            elif f_stage == "Select Stage":
                st.warning("Please select your current business stage.")
            else:
                st.session_state.user_profile = {
                    "name": f_name.strip(),
                    "region": f_region,
                    "district": f_district,
                    "stage": f_stage,
                    "sector": f_sector if f_sector != "Not sure yet" else "",
                    "gender": f_gender,
                    "phone": f_phone.strip(),
                    "registered_at": datetime.now().isoformat(timespec="seconds")
                }
                # Clear prefill state after saving
                for _k in ["prefill_name", "prefill_district", "prefill_region", "prefill_gender"]:
                    st.session_state[_k] = ""
                st.session_state["id_scanned"] = False
                st.success(f"✅ Profile saved! Welcome, {f_name.strip()}. Switch to the Citizen WhatsApp Simulator to see your personalised content.")
                st.rerun()

    if profile.get("name"):
        st.write("---")
        st.markdown("#### Your current profile")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {profile.get('name', '—')}")
            st.write(f"**District:** {profile.get('district', '—')}")
            st.write(f"**Stage:** {profile.get('stage', '—')}")
        with col2:
            st.write(f"**Sector:** {profile.get('sector', 'Not set') or 'Not set'}")
            st.write(f"**Gender:** {profile.get('gender', 'Not set')}")
            if profile.get("phone"):
                st.write(f"**Phone:** {profile.get('phone')}")
        if st.button("🗑️ Clear Profile (start over)"):
            st.session_state.user_profile = {}
            st.rerun()

    # ──────────────────────────────────────────────────────────────
    # FEATURE 2: VOICE / TEXT SMART ASSISTANT
    # ──────────────────────────────────────────────────────────────
    st.write("---")
    st.markdown("## 🎤 Ask Us Anything")
    st.caption(
        "Speak or type a question in **English, Swahili, or Arabic** — "
        "we'll cross-reference our full database of grants, programs, and business guides "
        "and give you a personalised answer based on your profile."
    )

    # Language selector
    v_lang = st.radio(
        "Choose your language / Chagua lugha yako / اختر لغتك:",
        ["🇬🇧 English", "🇰🇪 Swahili", "🇸🇦 Arabic"],
        horizontal=True,
        key="voice_lang_select"
    )
    _lang_code_map = {"🇬🇧 English": "en-UG", "🇰🇪 Swahili": "sw-KE", "🇸🇦 Arabic": "ar-SA"}
    _active_code   = _lang_code_map[v_lang]
    _lang_label    = v_lang.split(" ", 1)[1]

    # Voice input (requires Streamlit ≥ 1.38 and google-cloud-speech in requirements.txt)
    try:
        audio_val = st.audio_input(
            f"🎤 Tap the microphone and speak in {_lang_label}",
            key="voice_audio_input"
        )
        if audio_val:
            _audio_bytes = audio_val.read()
            if GEMINI_AVAILABLE and st.secrets.get("GEMINI_API_KEY"):
                with st.spinner(f"Transcribing your {_lang_label} recording..."):
                    _transcript = transcribe_audio_gemini(_audio_bytes, _lang_label) or ""
                if _transcript:
                    st.session_state["last_voice_query"] = _transcript
                    st.success(f"**You said:** {_transcript}")
                else:
                    st.warning("⚠️ Could not transcribe the recording. Try speaking more clearly, or type your question below.")
            else:
                st.info("🔧 Add your GEMINI_API_KEY to Streamlit secrets to enable voice transcription. Type your question below for now.")
    except AttributeError:
        # st.audio_input was added in Streamlit 1.38 — show instructions if not available
        st.info(
            "🎙️ **To enable voice recording:** add `streamlit>=1.38.0` to your requirements.txt and redeploy. "
            "Until then, type your question in the box below."
        )

    # Text input — works as both voice fallback and manual entry
    text_q = st.text_area(
        "Or type your question here:",
        value=st.session_state.get("last_voice_query", ""),
        placeholder=(
            "Examples:\n"
            "• What grants are available for women starting a business in Kampala?\n"
            "• Ni msaada gani kwa vijana wanaoanza biashara ya kilimo?\n"
            "• ما هي البرامج المتاحة للشباب في قطاع التكنولوجيا؟"
        ),
        height=110,
        key="voice_text_input"
    )

    if st.button("🔍 Find What's Relevant For Me", type="primary", use_container_width=True):
        _final_query = text_q.strip() or st.session_state.get("last_voice_query", "").strip()
        if not _final_query:
            st.warning("Please speak or type a question first.")
        else:
            _current_profile = st.session_state.user_profile or {
                "name": "", "region": "", "district": "",
                "stage": "", "sector": "", "gender": ""
            }
            with st.spinner("Searching across grants, blueprints, and financial guides for you..."):
                _ai_response = process_voice_command_with_gemini(
                    _final_query,
                    _current_profile,
                    st.session_state.gov_db,
                    st.session_state.blueprint_db,
                    st.session_state.masterclass_db
                )
            st.markdown("---")
            st.markdown("### 💡 Here's What We Found For You")
            st.markdown(_ai_response)
            st.caption(f"*Query: {_final_query}*")
            # Log for analytics (recorded in the Intelligence Dashboard)
            st.session_state.feedback_log.append({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "program": "Voice/Text Query",
                "status": "Voice Query",
                "district": st.session_state.user_profile.get("district", "unknown"),
                "query": _final_query[:200]
            })
            try:
                save_json(FEEDBACK_FILE, st.session_state.feedback_log)
            except Exception:
                pass

# ==================================================================
# VIEW 1: CITIZEN WHATSAPP SIMULATOR
# ==================================================================
elif view == "📱 Citizen WhatsApp Simulator":
    inject_css()
    branded_header('Citizen Gateway', 'Business guidance · Government services · Financial literacy')
    if profile.get("name"):
        st.markdown(f"### 👋 Welcome back, {profile['name']} — showing content for **{profile.get('district', 'your district')}**")
    else:
        st.info("💡 **Tip:** Set up your profile (👤 tab in the sidebar) to see content tailored to your district and business stage.")

    st.title("WhatsApp-First Interactive Prototype Flow")

    local_ctx = get_local_context(profile.get("district", ""))

    # Pre-fill stage from profile if available
    default_stage_idx = (STAGES.index(profile["stage"]) + 1) if profile.get("stage") in STAGES else 0
    default_sector_idx = (SECTORS.index(profile["sector"]) + 1) if profile.get("sector") in SECTORS else 0

    w_tab1, w_tab2, w_tab3 = st.tabs(["🏛️ Official Government Services",
                                        "📺 'It Works. Try It.' Business Blueprints",
                                        "💰 Financial Literacy Masterclass"])

    # ── Tab 1: Government Services ──────────────────────────────────
    with w_tab1:
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            selected_stage = st.selectbox("Choose Your Current Lifecycle Stage:", ["Select Stage"] + STAGES,
                                          index=default_stage_idx)
            selected_sector = st.selectbox("Choose Your Target Sector:", ["Select Sector"] + SECTORS,
                                           index=default_sector_idx) if selected_stage != "Select Stage" else "Select Sector"
        with col_nav2:
            gov_search = st.text_input("🔍 Keyword Search (e.g., 'URSB', 'Grant', 'Emyooga'):", value="")

        with st.container(border=True):
            st.caption("Incoming from Edge Lab Bot • Regulatory Portal")
            matched_gov = []
            if gov_search.strip():
                q = gov_search.lower()
                matched_gov = [c for c in st.session_state.gov_db
                               if q in c.get("title", "").lower() or q in c.get("agency", "").lower()]
            elif selected_stage != "Select Stage" and selected_sector != "Select Sector":
                matched_gov = [c for c in st.session_state.gov_db
                               if c.get("stage") == selected_stage and c.get("sector") == selected_sector]

            if matched_gov:
                for card in matched_gov:
                    st.markdown(gov_card_html(card), unsafe_allow_html=True)
                    if local_ctx:
                        st.info(f"📍 In your area ({profile.get('district','your district')}): {local_ctx}")
                    col_fb1, col_fb2, col_dl = st.columns([1, 1, 1])
                    with col_fb1:
                        if st.button("👍 Helpful", key=f"yes_g_{card['id']}"):
                            st.session_state.feedback_log.append({
                                "timestamp": datetime.now().isoformat(timespec="seconds"),
                                "program": card["title"], "status": "Helpful",
                                "district": profile.get("district", "unknown")
                            })
                            save_json(FEEDBACK_FILE, st.session_state.feedback_log)
                            st.success("Feedback recorded!")
                    with col_fb2:
                        if st.button("👎 Still confusing", key=f"no_g_{card['id']}"):
                            st.session_state.feedback_log.append({
                                "timestamp": datetime.now().isoformat(timespec="seconds"),
                                "program": card["title"], "status": "Friction Warning",
                                "district": profile.get("district", "unknown")
                            })
                            save_json(FEEDBACK_FILE, st.session_state.feedback_log)
                            st.error("Feedback sent to optimization queue.")
                    with col_dl:
                        if PDF_AVAILABLE:
                            pdf_bytes = generate_gov_card_pdf(card, profile)
                            if pdf_bytes:
                                st.download_button("📄 Download PDF", data=pdf_bytes,
                                                   file_name=f"{card['id']}.pdf",
                                                   mime="application/pdf",
                                                   key=f"dl_g_{card['id']}")
                    st.write("---")
            else:
                st.caption("Adjust the filters above to display official ministry compliance options.")

    # ── Tab 2: Business Blueprints ──────────────────────────────────
    with w_tab2:
        col_bp1, col_bp2 = st.columns(2)
        with col_bp1:
            selected_bp_sector = st.selectbox("Filter Blueprints by Sector:", ["Select Sector"] + SECTORS,
                                              index=default_sector_idx)
            selected_bp_tier = (st.selectbox("Filter by Capital Tier:", ["Select Tier"] + CAPITAL_TIERS)
                                if selected_bp_sector != "Select Sector" else "Select Tier")
        with col_bp2:
            bp_search = st.text_input("🔍 Search (e.g., 'Rabbit', 'Cake', 'Logistics'):", value="")

        with st.container(border=True):
            st.caption("Incoming from Edge Lab Bot • 'It Works. Try It.' Knowledge Stream")
            matched_bp = []
            if bp_search.strip():
                q = bp_search.lower()
                matched_bp = [b for b in st.session_state.blueprint_db
                              if q in b.get("title", "").lower() or q in b.get("summary", "").lower()
                              or q in b.get("success_case", "").lower()]
            elif selected_bp_sector != "Select Sector" and selected_bp_tier != "Select Tier":
                matched_bp = [b for b in st.session_state.blueprint_db
                              if b.get("sector") == selected_bp_sector and b.get("tier") == selected_bp_tier]

            if matched_bp:
                for bp in matched_bp:
                    st.markdown(blueprint_card_html(bp), unsafe_allow_html=True)
                    if bp.get("media_anchor"):
                        st.caption(f"Video: {bp.get('media_anchor')}")
                    if local_ctx:
                        st.info(f"📍 In your area: {local_ctx}")
                    if PDF_AVAILABLE:
                        pdf_bytes = generate_blueprint_pdf(bp, profile)
                        if pdf_bytes:
                            st.download_button("📄 Download Blueprint PDF", data=pdf_bytes,
                                               file_name=f"{bp['id']}.pdf", mime="application/pdf",
                                               key=f"dl_bp_{bp['id']}")
                    st.write("")
            else:
                st.warning("Select a sector and capital tier or search a keyword to browse blueprints.")

    # ── Tab 3: Financial Literacy Masterclass ──────────────────────
    with w_tab3:
        st.markdown("#### ⚡ Quick Check-In")
        st.caption("Answer 4 quick questions and get your most relevant lessons immediately. This is plain rule-based logic — nothing here can invent advice that is not already in the verified library below.")

        qc_stage = st.selectbox("Your current business stage:", ["Select Stage"] + STAGES,
                                 key="qc_stage",
                                 index=default_stage_idx)
        qc_col1, qc_col2 = st.columns(2)
        with qc_col1:
            cash_flow = st.radio("Current cash flow?", ["Positive", "Breaking even", "Negative"],
                                 key="qc_cash", horizontal=True)
            separate_money = st.radio("Business and personal money separated?",
                                      ["Yes", "Sort of", "No"], key="qc_sep", horizontal=True)
        with qc_col2:
            has_savings = st.radio("Do you have business savings set aside?",
                                   ["Yes", "No"], key="qc_save", horizontal=True)
            considering_loan = st.radio("Thinking about taking a loan soon?",
                                        ["No", "Yes"], key="qc_loan", horizontal=True)

        if st.button("✅ Get My Recommendations"):
            if qc_stage == "Select Stage":
                st.warning("Select your business stage above first.")
            else:
                def find_lesson(stage, topic_candidates):
                    for t in topic_candidates:
                        hit = [m for m in st.session_state.masterclass_db
                               if m["stage"] == stage and m["topic"] == t]
                        if hit:
                            return hit[0]
                    return None

                recommended = []
                if cash_flow == "Negative":
                    l = find_lesson(qc_stage, CHECKIN_RULES["cash_flow_negative"])
                    if l:
                        recommended.append(l)
                if separate_money in ("No", "Sort of"):
                    l = find_lesson(qc_stage, CHECKIN_RULES["no_separation"])
                    if l:
                        recommended.append(l)
                if has_savings == "No":
                    l = find_lesson(qc_stage, CHECKIN_RULES["no_savings"])
                    if l:
                        recommended.append(l)
                if considering_loan == "Yes":
                    l = find_lesson(qc_stage, CHECKIN_RULES["considering_loan"])
                    if l:
                        recommended.append(l)

                seen_ids = set()
                recommended = [r for r in recommended if not (r["id"] in seen_ids or seen_ids.add(r["id"]))]

                if not recommended:
                    fallback = find_lesson(qc_stage, ["Investing & Growing Your Capital"])
                    st.success("Your check-in looks healthy! Here is a lesson to keep building on:")
                    if fallback:
                        recommended = [fallback]

                for m in recommended:
                    _lctx = local_ctx if (local_ctx and m.get("topic","") in [
                        "Saving & Emergency Funds","Understanding SACCOs vs Banks",
                        "Credit, Loans & Borrowing","Mobile Money & Digital Finance"]) else ""
                    st.markdown(lesson_card_html(m, _lctx), unsafe_allow_html=True)
                    if PDF_AVAILABLE:
                        pdf_bytes = generate_masterclass_pdf(m, profile, local_ctx if local_ctx else "")
                        if pdf_bytes:
                            st.download_button("📄 Download This Lesson as PDF", data=pdf_bytes,
                                               file_name=f"{m['id']}_lesson.pdf", mime="application/pdf",
                                               key=f"dl_fl_ci_{m['id']}")
                    st.write("")

        st.write("---")
        st.markdown("#### 📚 Browse the Full Library")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            m_browse_stage = st.selectbox("Filter by Stage:", ["Select Stage"] + STAGES,
                                          key="m_browse_stage", index=default_stage_idx)
        with col_m2:
            m_search = st.text_input("🔍 Search Topics (e.g., 'saving', 'credit', 'sacco'):",
                                     key="m_browse_search")

        matched_m = []
        if m_search.strip():
            q = m_search.lower()
            matched_m = [m for m in st.session_state.masterclass_db
                         if q in m.get("topic", "").lower() or q in m.get("summary", "").lower()]
        elif m_browse_stage != "Select Stage":
            matched_m = [m for m in st.session_state.masterclass_db if m.get("stage") == m_browse_stage]

        if matched_m:
            for m in matched_m:
                _bctx = local_ctx if (local_ctx and m.get("topic","") in [
                    "Saving & Emergency Funds","Understanding SACCOs vs Banks",
                    "Credit, Loans & Borrowing","Mobile Money & Digital Finance"]) else ""
                st.markdown(lesson_card_html(m, _bctx), unsafe_allow_html=True)
                if PDF_AVAILABLE:
                    pdf_bytes = generate_masterclass_pdf(m, profile, local_ctx if local_ctx else "")
                    if pdf_bytes:
                        st.download_button("📄 Download This Lesson as PDF", data=pdf_bytes,
                                           file_name=f"{m['id']}_lesson.pdf", mime="application/pdf",
                                           key=f"dl_fl_br_{m['id']}")
                st.write("")
        else:
            st.caption("Select a stage or search a topic above to see lessons.")

    # ── Cross-Database Keyword Search ───────────────────────────────
    st.write("---")
    st.markdown("### 🔎 Cross-Database Keyword Search")
    st.caption("Simple keyword matching across all three databases simultaneously — not an AI model. Searches as you type.")
    ai_prompt = st.text_input("Search all databases at once (e.g., 'rabbit farm funding', 'register URSB'):")
    if ai_prompt:
        q_lower = ai_prompt.lower()
        matched_gov_q = [c for c in st.session_state.gov_db if any(
            w in c.get("title", "").lower() or w in c.get("sector", "").lower() or w in c.get("agency", "").lower()
            for w in q_lower.split())]
        matched_bp_q = [b for b in st.session_state.blueprint_db if any(
            w in b.get("title", "").lower() or w in b.get("summary", "").lower()
            or w in b.get("success_case", "").lower() for w in q_lower.split())]
        matched_fl_q = [m for m in st.session_state.masterclass_db if any(
            w in m.get("topic", "").lower() or w in m.get("summary", "").lower() for w in q_lower.split())]

        with st.chat_message("assistant"):
            st.markdown("#### Keyword Matches Found")
            syn_col1, syn_col2, syn_col3 = st.columns(3)
            with syn_col1:
                st.markdown("📂 **1. Government Services**")
                if matched_gov_q:
                    g = matched_gov_q[0]
                    st.markdown(f"**{g.get('title')}**")
                    st.markdown(f"Agency: {g.get('agency')}")
                    st.markdown(f"Cost: `{g.get('cost')}`")
                else:
                    st.write("No match — try the stage/sector filters in the first tab.")
            with syn_col2:
                st.markdown("📊 **2. Business Blueprints**")
                if matched_bp_q:
                    b = matched_bp_q[0]
                    st.markdown(f"**{b.get('title')}**")
                    st.info(f"💡 {b.get('fin_lit_tip')}")
                else:
                    st.write("No match — try the sector/tier filters in the second tab.")
            with syn_col3:
                st.markdown("💰 **3. Financial Literacy**")
                if matched_fl_q:
                    m = matched_fl_q[0]
                    st.markdown(f"**{m.get('topic')}** ({m.get('stage')})")
                    st.write(m.get("summary", "")[:200] + "...")
                    st.info(f"✅ {m.get('action_tip')}")
                else:
                    st.write("No match — try the stage filter in the third tab.")


# ==================================================================
# VIEW 2: CITIZEN USSD SIMULATOR (dynamic, ID-safe — never positional)
# ==================================================================
elif view == "📟 Citizen USSD Simulator":
    inject_css()
    branded_header('USSD Feature-Phone Simulator', 'Low-tech access for basic mobile phones')
    st.title("USSD Feature-Phone Simulation Layer")
    st.info("💡 Emulating a USSD session over a basic feature-phone connection. Menus generated live from current database.")

    if "ussd_string" not in st.session_state:
        st.session_state.ussd_string = ""

    col_input, col_screen = st.columns([1, 1])

    with col_input:
        st.subheader("Keypad Entry")
        current_input = st.text_input("Type your numeric choices (e.g. 1, then 1*1, then 1*1*1):",
                                      value=st.session_state.ussd_string)
        st.session_state.ussd_string = current_input.strip()
        st.markdown("""
        **Navigation:**
        * Blank → Main menu
        * `1` → Government Services → Stage → Sector → Item
        * `2` → Business Blueprints → Sector → Item
        * `3` → Financial Literacy → Stage → Topic
        * Menus reflect whatever is currently published via the CMS.
        """)
        if st.button("❌ End USSD Session"):
            st.session_state.ussd_string = ""
            st.rerun()

    with col_screen:
        st.subheader("📟 Feature-Phone Screen")
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

            screen = "END Invalid selection. Dial *284# to restart."

            if not parts:
                screen = "CON Welcome to Edge Lab.\n1. Government Services\n2. Business Blueprints ('It Works')\n3. Financial Literacy Masterclass"

            elif parts[0] == "1":
                stages_avail = [s for s in STAGES if any(c["stage"] == s for c in st.session_state.gov_db)]
                if len(parts) == 1:
                    screen = ("CON Choose Lifecycle Stage:\n" + "\n".join(
                        f"{i+1}. {s}" for i, s in enumerate(stages_avail))) if stages_avail else "END No government services published yet."
                else:
                    idx1 = safe_idx(parts, 1)
                    if idx1 and idx1 <= len(stages_avail):
                        stage = stages_avail[idx1 - 1]
                        sectors_avail = sorted({c["sector"] for c in st.session_state.gov_db if c["stage"] == stage})
                        if len(parts) == 2:
                            screen = (f"CON {stage} - Choose Sector:\n" + "\n".join(
                                f"{i+1}. {s}" for i, s in enumerate(sectors_avail))) if sectors_avail else f"END No services yet for {stage}."
                        else:
                            idx2 = safe_idx(parts, 2)
                            if idx2 and idx2 <= len(sectors_avail):
                                sector = sectors_avail[idx2 - 1]
                                matches = [c for c in st.session_state.gov_db
                                           if c["stage"] == stage and c["sector"] == sector]
                                if len(parts) == 3:
                                    if len(matches) == 1:
                                        c = matches[0]
                                        screen = f"END {c['title']}\nAgency: {c['agency']}\nCost: {c['cost']}\nContact: {c['contacts']}"
                                    elif matches:
                                        screen = f"CON {sector} - Select:\n" + "\n".join(
                                            f"{i+1}. {c['title'][:30]}" for i, c in enumerate(matches))
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
                    screen = ("CON Business Blueprints - Choose Sector:\n" + "\n".join(
                        f"{i+1}. {s}" for i, s in enumerate(sectors_avail))) if sectors_avail else "END No blueprints published yet."
                else:
                    idx1 = safe_idx(parts, 1)
                    if idx1 and idx1 <= len(sectors_avail):
                        sector = sectors_avail[idx1 - 1]
                        items = [b for b in st.session_state.blueprint_db if b["sector"] == sector]
                        if len(parts) == 2:
                            screen = (f"CON {sector} Blueprints:\n" + "\n".join(
                                f"{i+1}. {b['title'][:30]}" for i, b in enumerate(items))) if items else "END No blueprints for this sector."
                        else:
                            idx2 = safe_idx(parts, 2)
                            if idx2 and idx2 <= len(items):
                                b = items[idx2 - 1]
                                screen = f"END {b['title']}\nCapital: {b['capital_required'][:80]}\nTip: {b['fin_lit_tip'][:120]}"

            elif parts[0] == "3":
                stages_avail_m = [s for s in STAGES if any(m["stage"] == s for m in st.session_state.masterclass_db)]
                if len(parts) == 1:
                    screen = ("CON Financial Literacy - Choose Stage:\n" + "\n".join(
                        f"{i+1}. {s}" for i, s in enumerate(stages_avail_m))) if stages_avail_m else "END No financial literacy notes published yet."
                else:
                    idx1 = safe_idx(parts, 1)
                    if idx1 and idx1 <= len(stages_avail_m):
                        stage = stages_avail_m[idx1 - 1]
                        topics = [m for m in st.session_state.masterclass_db if m["stage"] == stage]
                        if len(parts) == 2:
                            screen = (f"CON {stage} - Choose Topic:\n" + "\n".join(
                                f"{i+1}. {m['topic'][:30]}" for i, m in enumerate(topics))) if topics else "END No notes for this stage yet."
                        else:
                            idx2 = safe_idx(parts, 2)
                            if idx2 and idx2 <= len(topics):
                                m = topics[idx2 - 1]
                                screen = f"END {m['topic']}\n{m['summary'][:120]}\nDo this: {m['action_tip'][:100]}"

            st.code(screen, language="text")


# ==================================================================
# VIEW 3: GOVERNMENT ADMIN CMS PORTAL
# ==================================================================
elif view == "🏛️ Government Admin CMS Portal":
    inject_css()
    branded_header('Government Admin CMS', 'Publish and manage all platform content')
    st.title("Government Admin CMS & Content Management Portal")

    cms_tab1, cms_tab2, cms_tab3 = st.tabs(["📝 Government Service Cards",
                                              "🎬 'It Works. Try It.' Blueprints",
                                              "💰 Financial Literacy Notes"])

    with cms_tab1:
        with st.form("cms_gov_form", clear_on_submit=True):
            st.markdown("### Publish a Government Service Card")
            g_title = st.text_input("Program / Service Name:")
            g_agency = st.text_input("Managing Agency/Ministry:")
            g_stage = st.selectbox("Target Business Stage:", STAGES, key="g_stage")
            g_sector = st.selectbox("Target Sector:", SECTORS, key="g_sector")
            g_eligibility = st.text_area("Who Qualifies?")
            g_cost = st.text_input("Cost / Fees:")
            g_steps = st.text_area("Step-by-Step Process:")
            g_contacts = st.text_input("Contact Details:")
            if st.form_submit_button("🚀 Publish to Government Registry"):
                st.session_state.gov_db.append({
                    "id": str(uuid.uuid4())[:8], "title": g_title, "agency": g_agency,
                    "stage": g_stage, "sector": g_sector, "eligibility": g_eligibility,
                    "cost": g_cost, "steps": g_steps, "contacts": g_contacts
                })
                save_json(GOV_DB_FILE, st.session_state.gov_db)
                st.success(f"Published '{g_title}' to the government registry.")

    with cms_tab2:
        with st.form("cms_blueprint_form", clear_on_submit=True):
            st.markdown("### Publish a Business Blueprint / Success Case")
            st.caption("If a detail is not yet independently confirmed, say so in the field rather than guessing — see the seed data entries for the pattern.")
            b_title = st.text_input("Business Model Name:", value="Commercial Goat Farming")
            b_sector = st.selectbox("Industry Sector:", SECTORS, key="b_sector")
            b_tier = st.selectbox("Capital Tier:", CAPITAL_TIERS)
            b_capital = st.text_input("Capital Required (UGX):", value="UGX 14,000,000 (fencing, breeder stock, kits)")
            b_summary = st.text_area("Business Model Summary:", value="Semi-intensive goat farming for meat.")
            b_fin_lit = st.text_area("Financial Literacy Tip:", value="Separate breeding stock costs from working capital.")
            b_case = st.text_area("Verified Success Case:", value="Interview with District Farm Lead who broke even at 18 months.")
            b_media = st.text_input("YouTube / Media Link:", value="https://www.youtube.com/watch?v=XXXXXX")
            if st.form_submit_button("🎬 Publish Blueprint"):
                st.session_state.blueprint_db.append({
                    "id": str(uuid.uuid4())[:8], "title": b_title, "sector": b_sector, "tier": b_tier,
                    "capital_required": b_capital, "summary": b_summary, "fin_lit_tip": b_fin_lit,
                    "success_case": b_case, "media_anchor": b_media
                })
                save_json(BLUEPRINT_DB_FILE, st.session_state.blueprint_db)
                st.success(f"Published '{b_title}' to the blueprint library.")

    with cms_tab3:
        with st.form("cms_masterclass_form", clear_on_submit=True):
            st.markdown("### Publish a Financial Literacy Note")
            st.caption("General financial-literacy principles (saving, budgeting, separating money) are safe to write directly as universal practice. Any Uganda-specific rate, institution, or rule still needs independent verification before publishing — same discipline as the other two tabs.")
            existing_topics = sorted({m["topic"] for m in st.session_state.masterclass_db})
            st.caption("Existing topics: " + ", ".join(existing_topics) if existing_topics else "No topics yet.")
            fl_topic = st.text_input("Topic Name (use an existing name to add stage depth, or a new name for a new theme):",
                                     value="Saving & Emergency Funds")
            fl_stage = st.selectbox("Business Stage:", STAGES, key="fl_stage")
            fl_summary = st.text_area("Lesson (3-4 sentences, substantive):",
                                      value="Explain the core point in plain language.")
            fl_uganda = st.text_area("Uganda-Specific Example (2-3 sentences):",
                                     value="Reference a real Ugandan institution, programme, or documented pattern.")
            fl_mistake = st.text_input("Common Mistake to Avoid (1-2 sentences):",
                                       value="What people in Uganda most commonly get wrong on this topic.")
            fl_action = st.text_input("Concrete Action Tip (one doable next step):",
                                      value="One specific action the reader can take this week.")
            if st.form_submit_button("📌 Publish Financial Note"):
                st.session_state.masterclass_db.append({
                    "id": str(uuid.uuid4())[:8], "topic": fl_topic, "stage": fl_stage,
                    "summary": fl_summary, "uganda_example": fl_uganda,
                    "common_mistake": fl_mistake, "action_tip": fl_action
                })
                save_json(MASTERCLASS_DB_FILE, st.session_state.masterclass_db)
                st.success(f"Published '{fl_topic}' for {fl_stage}.")

    st.write("---")
    st.markdown("### 📋 Active Content Registries")
    exp_gov, exp_bp, exp_fl = st.columns(3)
    with exp_gov:
        st.subheader("Government Registry")
        for c in st.session_state.gov_db:
            with st.expander(f"🏛️ {c.get('title')}"):
                st.write(f"Stage: {c.get('stage')} | Sector: {c.get('sector')}")
                st.write(f"Agency: {c.get('agency')}")
                if st.button("🗑️ Delete", key=f"del_g_{c['id']}"):
                    st.session_state.gov_db = [i for i in st.session_state.gov_db if i["id"] != c["id"]]
                    save_json(GOV_DB_FILE, st.session_state.gov_db)
                    st.rerun()
    with exp_bp:
        st.subheader("Blueprint Library")
        for b in st.session_state.blueprint_db:
            with st.expander(f"🎬 {b.get('title')}"):
                st.write(f"Tier: {b.get('tier')} | Sector: {b.get('sector')}")
                if st.button("🗑️ Delete", key=f"del_b_{b['id']}"):
                    st.session_state.blueprint_db = [i for i in st.session_state.blueprint_db if i["id"] != b["id"]]
                    save_json(BLUEPRINT_DB_FILE, st.session_state.blueprint_db)
                    st.rerun()
    with exp_fl:
        st.subheader("Financial Literacy Notes")
        for m in st.session_state.masterclass_db:
            with st.expander(f"💰 {m.get('topic')} ({m.get('stage')})"):
                st.write(m.get("summary", "")[:120] + "...")
                if st.button("🗑️ Delete", key=f"del_fl_{m['id']}"):
                    st.session_state.masterclass_db = [i for i in st.session_state.masterclass_db if i["id"] != m["id"]]
                    save_json(MASTERCLASS_DB_FILE, st.session_state.masterclass_db)
                    st.rerun()


# ==================================================================
# VIEW 4: GOV INTELLIGENCE DASHBOARD
# ==================================================================
elif view == "📊 Gov Intelligence Dashboard":
    inject_css()
    branded_header('Intelligence Dashboard', 'National MSME Knowledge Infrastructure Analytics')
    st.title("📊 National MSME Knowledge Infrastructure -- Intelligence Dashboard")
    st.caption("A decision-support tool for government partners. Real feedback data is highlighted. Illustrative demo metrics are clearly labelled.")

    # Section A: Executive KPIs
    st.markdown("## A. Executive Summary")
    total_gov_cards  = len(st.session_state.gov_db)
    total_blueprints = len(st.session_state.blueprint_db)
    total_fl_lessons = len(st.session_state.masterclass_db)
    total_feedback   = len(st.session_state.feedback_log)
    helpful_count    = sum(1 for f in st.session_state.feedback_log if f.get("status") == "Helpful")
    friction_count   = sum(1 for f in st.session_state.feedback_log if f.get("status") == "Friction Warning")
    satisfaction_pct = round(helpful_count / total_feedback * 100, 1) if total_feedback else 0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Gov Service Cards", total_gov_cards)
    k2.metric("Business Blueprints", total_blueprints)
    k3.metric("Financial Literacy Lessons", total_fl_lessons)
    k4.metric("Citizen Feedback Interactions", total_feedback, "Real data")
    k5.metric("Satisfaction Rate", f"{satisfaction_pct}%", f"{helpful_count} helpful" if helpful_count else "No data yet")
    k6.metric("Friction Warnings", friction_count, "Needs attention" if friction_count > 0 else "All clear", delta_color="inverse" if friction_count > 0 else "off")
    st.caption("Columns 1-3 are computed from live content databases. Columns 4-6 reflect real citizen feedback button presses.")

    st.markdown("---")

    # Section B: Content Coverage Gap Analysis
    st.markdown("## B. Content Coverage Gap Analysis")
    st.caption("Which stage-sector combinations have NO government service card? These are the programme communication gaps.")
    all_combos  = [(s, sec) for s in STAGES for sec in SECTORS]
    covered     = {(c["stage"], c["sector"]) for c in st.session_state.gov_db}
    gaps        = [(s, sec) for s, sec in all_combos if (s, sec) not in covered]
    coverage_pct = round(len(covered) / len(all_combos) * 100)

    gc1, gc2 = st.columns(2)
    with gc1:
        st.markdown(f"**Coverage: {len(covered)}/{len(all_combos)} stage-sector combinations ({coverage_pct}%)**")
        st.progress(coverage_pct / 100)
        if gaps:
            st.markdown("**Gaps (no content yet):**")
            st.dataframe(pd.DataFrame(gaps, columns=["Stage", "Sector"]), use_container_width=True, hide_index=True)
        else:
            st.success("All stage-sector combinations are covered.")
    with gc2:
        stage_counts = pd.DataFrame(
            [(s, sum(1 for c in st.session_state.gov_db if c["stage"] == s)) for s in STAGES],
            columns=["Stage", "Cards"]
        )
        st.markdown("**Cards per stage:**")
        st.bar_chart(stage_counts.set_index("Stage"))

    st.markdown("---")

    # Section C: Real Citizen Feedback
    st.markdown("## C. Citizen Feedback Intelligence (Live Data)")
    if st.session_state.feedback_log:
        df_fb = pd.DataFrame(st.session_state.feedback_log)
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            st.markdown("**Feedback by Programme**")
            if "program" in df_fb.columns:
                st.dataframe(df_fb.groupby(["program", "status"]).size().unstack(fill_value=0), use_container_width=True)
        with fc2:
            st.markdown("**Helpful vs Friction**")
            if "status" in df_fb.columns:
                st.bar_chart(df_fb.groupby("status").size())
        with fc3:
            st.markdown("**Geographic Distribution**")
            if "district" in df_fb.columns and df_fb["district"].notna().any():
                st.bar_chart(df_fb.groupby("district").size().sort_values(ascending=False).head(10))
            else:
                st.info("No district data yet. Activate geographic tracking by having citizens set up profiles.")

        if "status" in df_fb.columns:
            friction_df = df_fb[df_fb["status"] == "Friction Warning"]
            if not friction_df.empty:
                st.markdown("**Friction Warning Log -- Programmes Needing Ministry Attention**")
                st.dataframe(friction_df, use_container_width=True)
                st.warning(f"{len(friction_df)} friction warnings logged. The relevant ministries should review and simplify these programme descriptions.")

        st.markdown("**Full Feedback Log**")
        st.dataframe(df_fb, use_container_width=True)
    else:
        st.info("No citizen feedback recorded yet. Feedback populates here automatically once the platform is deployed at LC1 offices.")

    st.markdown("---")

    # Section D: Illustrative Demand Projections
    st.markdown("## D. Sector Demand Intelligence (Illustrative Projections)")
    st.caption("These figures are illustrative projections based on Uganda MSME population and digital-access estimates. They will be replaced by real traffic data once deployed at LC1 offices.")

    dc1, dc2 = st.columns(2)
    with dc1:
        st.markdown("**Projected Monthly Active Users by Region**")
        proj = pd.DataFrame({
            "Central": [1200, 1800, 2600, 3900, 5200, 7100],
            "Eastern": [400,  700,  1100, 1700, 2400, 3200],
            "Northern": [300, 500,  800,  1300, 1900, 2700],
            "Western": [350,  600,  950,  1500, 2100, 2900],
        }, index=["Month 1","Month 2","Month 3","Month 4","Month 5","Month 6"])
        st.line_chart(proj)
    with dc2:
        st.markdown("**Programme Category Demand Forecast (Month 6)**")
        forecast = pd.DataFrame({
            "Est. Monthly Queries": [7100, 4200, 3800, 3100, 2600, 2300, 1900]
        }, index=["PDM/Agri Grants", "URSB Registration", "YLP Youth Grants",
                  "Emyooga SACCO", "URA/Tax", "NGO Opportunities", "Export/UEPB"])
        st.bar_chart(forecast)

    st.markdown("---")

    # Section E: Policy Recommendations
    st.markdown("## E. Policy Intelligence Recommendations")
    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown("**Automated Content Recommendations**")
        if gaps:
            st.warning(f"{len(gaps)} content gaps identified. Priority gaps: {', '.join([f'{s}/{sec}' for s,sec in gaps[:3]])}")
        if friction_count > 0:
            progs = list(set(f.get("program","") for f in st.session_state.feedback_log if f.get("status") == "Friction Warning"))
            st.error(f"{friction_count} friction warnings on: {', '.join(progs[:3])}. Simplify with the relevant ministry.")
        if total_feedback == 0:
            st.info("No citizen interaction data yet. Deploy QR codes at LC1 offices to begin generating real intelligence.")
        if total_gov_cards < 15:
            st.info(f"Content library has {total_gov_cards} government service cards. Consider adding more entries, particularly for Mature MSME stage.")
    with rc2:
        st.markdown("**Platform Readiness Assessment**")
        checks = [
            ("Government service cards",       total_gov_cards >= 5,    f"{total_gov_cards} published"),
            ("Business blueprints",            total_blueprints >= 3,   f"{total_blueprints} published"),
            ("Financial literacy lessons",     total_fl_lessons >= 10,  f"{total_fl_lessons} published"),
            ("Content coverage",               coverage_pct >= 60,      f"{coverage_pct}% of stage-sector combinations"),
            ("Citizen feedback system",        True,                    "Active"),
            ("PDF downloads",                  PDF_AVAILABLE,           "Available" if PDF_AVAILABLE else "fpdf2 not installed"),
            ("QR code generator",              QR_AVAILABLE,            "Available" if QR_AVAILABLE else "qrcode not installed"),
        ]
        for label, passing, detail in checks:
            st.markdown(f"{'OK' if passing else 'WARN'} **{label}** -- {detail}")

    st.markdown("---")

    # Section F: LC1 Deployment Tools
    st.markdown("## F. LC1 Deployment Tools")
    ftab1, ftab2 = st.tabs(["Generate Weekly Digest PDF", "Generate QR Code for LC1 Office"])

    with ftab1:
        st.caption("A printable one-page summary for posting at an LC1 office alongside the QR code.")
        if PDF_AVAILABLE:
            fc1, fc2 = st.columns(2)
            with fc1:
                digest_district = st.text_input("District for header:", value=profile.get("district",""), placeholder="e.g. Kampala")
                digest_stage = st.selectbox("Focus on stage (or All):", ["All Stages"] + STAGES)
            with fc2:
                n_gov = st.slider("Government service cards:", 1, min(5, len(st.session_state.gov_db)), 3)
                n_bp  = st.slider("Business blueprints:", 1, min(3, len(st.session_state.blueprint_db)), 2)
                n_fl  = st.slider("Financial literacy lessons:", 1, min(5, len(st.session_state.masterclass_db)), 3)
            if st.button("Generate Weekly Digest PDF"):
                gov_s = ([c for c in st.session_state.gov_db if c.get("stage") == digest_stage][:n_gov]
                         if digest_stage != "All Stages" else st.session_state.gov_db[:n_gov])
                bp_s  = st.session_state.blueprint_db[:n_bp]
                fl_s  = ([m for m in st.session_state.masterclass_db if m.get("stage") == digest_stage][:n_fl]
                         if digest_stage != "All Stages" else st.session_state.masterclass_db[:n_fl])
                pdf_b = generate_digest_pdf(gov_s, bp_s, fl_s, digest_district)
                if pdf_b:
                    st.download_button("Download Digest PDF", data=pdf_b,
                                       file_name=f"edgelab_digest_{digest_district or 'all'}.pdf",
                                       mime="application/pdf")
        else:
            st.warning("PDF unavailable -- ensure fpdf2 is in requirements.txt and redeploy.")

    with ftab2:
        st.markdown("Generate a QR code pointing to this platform. Download it, print it at A5 size or larger, laminate it, and post it at any LC1 office, SACCO branch, or market notice board.")
        if QR_AVAILABLE:
            app_url = st.text_input(
                "Enter your Streamlit app URL:",
                value="https://mandem-kaazycrhjo6wlhh7bhqxud.streamlit.app",
                placeholder="https://yourapp.streamlit.app"
            )
            qr_label    = st.text_input("Label (shown below QR code on printout):", value="Scan for Free Business Guidance -- Edge Lab Platform")
            qr_district = st.text_input("LC1 location label:", value=profile.get("district",""), placeholder="e.g. Namuwongo LC1 Office, Kampala")
            if st.button("Generate QR Code"):
                if app_url.strip():
                    qr_bytes = generate_qr_png(app_url.strip())
                    if qr_bytes:
                        st.image(qr_bytes, caption=f"{qr_label} | {qr_district}", width=300)
                        st.download_button(
                            "Download QR Code (PNG -- print at A5 or larger)",
                            data=qr_bytes,
                            file_name=f"edgelab_qr_{qr_district.replace(' ','_') or 'lc1'}.png",
                            mime="image/png"
                        )
                        st.success("QR code generated. Print at A5 size minimum, laminate, and post at the LC1 office alongside the weekly digest PDF.")
                        st.info("What citizens see: scanning this QR opens the Edge Lab Platform directly on their phone -- no app download needed.")
                else:
                    st.warning("Please enter the app URL first.")
        else:
            st.warning("QR code generation unavailable -- add qrcode[pil] and pillow to requirements.txt and redeploy.")