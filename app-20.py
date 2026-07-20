import streamlit as st
import pandas as pd
import json
import os
import uuid
import base64
import hashlib
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
st.set_page_config(page_title="Katali", page_icon="🇺🇬", layout="wide")

import html as _H

def _e(t):
    return _H.escape(str(t or ""))

def inject_css():
    st.markdown("""
<style>
@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap");
html,body,[class*="css"]{font-family:"Plus Jakarta Sans",sans-serif;}
.main .block-container{padding-top:1.5rem;padding-bottom:2rem;max-width:1280px;}
footer{visibility:hidden;}

[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#051A0E 0%,#0A2818 50%,#0D3320 100%);
  border-right:3px solid #C9961A;}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] .stCaption{color:#A8D5B5 !important;}
[data-testid="stSidebar"] .stRadio label span{color:#C8E6D0 !important;}
[data-testid="stSidebar"] hr{border-color:rgba(201,150,26,0.4) !important;margin:0.8rem 0 !important;}
[data-testid="stSidebar"] .stButton>button{
  background:rgba(201,150,26,0.15) !important;color:#C9961A !important;
  border:1px solid rgba(201,150,26,0.5) !important;border-radius:8px !important;
  width:100% !important;font-size:0.82rem !important;font-weight:600 !important;}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(201,150,26,0.3) !important;}

.stButton>button{
  background:linear-gradient(135deg,#1A5C38 0%,#2D8A57 100%) !important;
  color:white !important;border:none !important;border-radius:8px !important;
  padding:0.45rem 1.2rem !important;font-weight:600 !important;font-size:0.88rem !important;
  transition:all 0.2s ease !important;box-shadow:0 2px 6px rgba(26,92,56,0.25) !important;}
.stButton>button:hover{
  background:linear-gradient(135deg,#C9961A 0%,#A67B14 100%) !important;
  box-shadow:0 4px 14px rgba(201,150,26,0.35) !important;transform:translateY(-1px) !important;}
.stButton>button[kind="primary"]{
  background:linear-gradient(135deg,#C9961A 0%,#A67B14 100%) !important;
  box-shadow:0 2px 8px rgba(201,150,26,0.3) !important;}
.stButton>button[kind="primary"]:hover{
  background:linear-gradient(135deg,#1A5C38 0%,#2D8A57 100%) !important;}

.stDownloadButton>button{
  background:linear-gradient(135deg,#C9961A 0%,#A67B14 100%) !important;
  color:white !important;border:none !important;border-radius:8px !important;
  font-weight:600 !important;font-size:0.85rem !important;
  box-shadow:0 2px 6px rgba(201,150,26,0.3) !important;transition:all 0.2s ease !important;}
.stDownloadButton>button:hover{
  background:linear-gradient(135deg,#1A5C38 0%,#2D8A57 100%) !important;transform:translateY(-1px) !important;}

[data-testid="metric-container"]{
  background:white !important;border:1px solid #D5E8DC !important;
  border-radius:12px !important;padding:1rem !important;
  box-shadow:0 2px 8px rgba(0,0,0,0.05) !important;border-top:3px solid #1A5C38 !important;}
[data-testid="metric-container"] [data-testid="stMetricLabel"] p{
  font-size:0.72rem !important;font-weight:700 !important;color:#6C757D !important;
  text-transform:uppercase !important;letter-spacing:0.06em !important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{
  font-size:1.5rem !important;font-weight:700 !important;color:#1A5C38 !important;}

.stTabs [data-baseweb="tab-list"]{
  background-color:#EEF7F2;border-radius:10px;padding:4px;gap:3px;}
.stTabs [data-baseweb="tab"]{
  border-radius:8px;color:#4A5568;font-weight:500;font-size:0.87rem;padding:0.4rem 1rem;}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg,#1A5C38 0%,#2D8A57 100%) !important;
  color:white !important;font-weight:600 !important;}

[data-testid="stVerticalBlockBorderWrapper"]{
  border:1px solid #D5E8DC !important;border-radius:12px !important;
  box-shadow:0 2px 8px rgba(0,0,0,0.04) !important;background:white !important;}

details summary{
  background-color:#F4FAF6 !important;border-radius:8px !important;
  color:#1A5C38 !important;font-weight:600 !important;padding:0.6rem 0.8rem !important;}
details summary:hover{background-color:#E8F5EE !important;}

[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{
  border-radius:8px !important;border-color:#B2CFC1 !important;font-size:0.9rem !important;}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{
  border-color:#1A5C38 !important;box-shadow:0 0 0 3px rgba(26,92,56,0.12) !important;}
[data-baseweb="select"]{border-radius:8px !important;}
.stProgress>div>div>div{background:linear-gradient(90deg,#1A5C38,#C9961A) !important;}
[data-testid="stAlert"]{border-radius:10px !important;border-left-width:4px !important;}
[data-testid="stDataFrame"]{border-radius:10px !important;overflow:hidden !important;}
hr{border-color:#D5E8DC !important;margin:1.2rem 0 !important;}
</style>""", unsafe_allow_html=True)

def branded_header(title, subtitle="", right_label=""):
    r = (f'<span style="background:rgba(201,150,26,0.25);color:#F5C842;'
         f'padding:0.25rem 0.9rem;border-radius:20px;font-size:0.78rem;'
         f'font-weight:700;">{_e(right_label)}</span>' if right_label else "")
    sub = (f'<div style="color:#C9961A;font-size:0.9rem;margin-top:0.2rem;">'
           f'{_e(subtitle)}</div>' if subtitle else "")
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#051A0E 0%,#0A2818 40%,#1A5C38 100%);'
        f'padding:1.2rem 1.6rem;border-radius:14px;margin-bottom:1.5rem;'
        f'border-left:6px solid #C9961A;box-shadow:0 4px 20px rgba(5,26,14,0.3);">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">'
        f'<div style="display:flex;align-items:center;gap:0.9rem;">'
        f'<span style="font-size:2rem;">🇺🇬</span>'
        f'<div><div style="color:rgba(255,255,255,0.55);font-size:0.7rem;font-weight:700;'
        f'letter-spacing:0.12em;text-transform:uppercase;">Katali</div>'
        f'<div style="color:white;font-size:1.25rem;font-weight:800;letter-spacing:-0.01em;">{_e(title)}</div>{sub}</div></div>{r}</div></div>',
        unsafe_allow_html=True)

def gov_card_html(card):
    is_ngo = card.get("id","").startswith("ngo")
    border = "#2D8A57" if is_ngo else "#1A5C38"
    b_bg   = "#E8F8F5" if is_ngo else "#EBF5F0"
    b_fg   = "#2D8A57" if is_ngo else "#1A5C38"
    badge  = "🌍 UN/NGO Partner" if is_ngo else "🏛️ Government"
    steps  = _e(card.get("steps",""))
    for i in range(1,8): steps = steps.replace(f"{i}. ",f"<br><b>{i}.</b> ")
    steps  = steps.lstrip("<br>")
    return (
        f'<div style="background:white;border-left:5px solid {border};border-radius:12px;'
        f'padding:1.4rem;margin-bottom:0.6rem;box-shadow:0 3px 12px rgba(0,0,0,0.07);">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;'
        f'margin-bottom:0.9rem;gap:0.8rem;">'
        f'<div style="color:#1A5C38;font-size:1rem;font-weight:700;flex:1;">{_e(card.get("title",""))}</div>'
        f'<span style="background:{b_bg};color:{b_fg};padding:0.22rem 0.65rem;'
        f'border-radius:14px;font-size:0.7rem;font-weight:700;white-space:nowrap;">{badge}</span></div>'
        f'<div style="color:#6C757D;font-size:0.8rem;margin-bottom:0.9rem;">🏛️ <strong>{_e(card.get("agency",""))}</strong></div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.7rem;margin-bottom:0.9rem;">'
        f'<div style="background:#F0FBF4;border-radius:8px;padding:0.7rem;">'
        f'<div style="font-size:0.68rem;color:#1A5C38;font-weight:800;text-transform:uppercase;'
        f'margin-bottom:0.3rem;">✅ Who Qualifies</div>'
        f'<div style="font-size:0.82rem;color:#2D3748;line-height:1.5;">{_e(card.get("eligibility",""))}</div></div>'
        f'<div style="background:#FFFBF0;border-radius:8px;padding:0.7rem;border-left:3px solid #C9961A;">'
        f'<div style="font-size:0.68rem;color:#C9961A;font-weight:800;text-transform:uppercase;'
        f'margin-bottom:0.3rem;">💰 Cost</div>'
        f'<div style="font-size:0.82rem;color:#2D3748;line-height:1.5;">{_e(card.get("cost",""))}</div></div></div>'
        f'<div style="background:#F4FAF6;border-radius:8px;padding:0.8rem;margin-bottom:0.8rem;">'
        f'<div style="font-size:0.68rem;color:#1A5C38;font-weight:800;text-transform:uppercase;'
        f'margin-bottom:0.4rem;">🛠️ Steps to Take</div>'
        f'<div style="font-size:0.82rem;color:#2D3748;line-height:1.7;">{steps}</div></div>'
        f'<div style="background:#F0FFF4;border-radius:8px;padding:0.6rem 0.8rem;">'
        f'<span style="font-size:0.8rem;color:#2D8A57;font-weight:600;">📞 {_e(card.get("contacts",""))}</span></div></div>'
    )

def blueprint_card_html(bp):
    tm = {"Micro (Under UGX 5M)":("#E8F8F5","#2D8A57"),
          "Small (UGX 5M - 20M)":("#EBF5F0","#1A5C38"),
          "Medium/Commercial (UGX 20M+)":("#FFFBF0","#C9961A")}
    bg,fg = tm.get(bp.get("tier",""),("#F4FAF6","#6C757D"))
    cap = _e(bp.get("capital_required",""))[:80]
    return (
        f'<div style="background:white;border-radius:12px;padding:1.4rem;'
        f'margin-bottom:0.6rem;box-shadow:0 3px 12px rgba(0,0,0,0.07);border-top:4px solid {fg};">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;'
        f'margin-bottom:0.8rem;gap:0.8rem;">'
        f'<div style="color:#1A5C38;font-size:1rem;font-weight:700;flex:1;">💡 {_e(bp.get("title",""))}</div>'
        f'<span style="background:{bg};color:{fg};padding:0.22rem 0.65rem;'
        f'border-radius:14px;font-size:0.7rem;font-weight:700;">{_e(bp.get("tier",""))}</span></div>'
        f'<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.8rem;">'
        f'<span style="background:#EEF7F2;color:#1A5C38;padding:0.2rem 0.55rem;'
        f'border-radius:6px;font-size:0.72rem;font-weight:600;">📂 {_e(bp.get("sector",""))}</span>'
        f'<span style="background:#FFFBF0;color:#C9961A;padding:0.2rem 0.55rem;'
        f'border-radius:6px;font-size:0.72rem;font-weight:600;">💰 {cap}</span></div>'
        f'<p style="font-size:0.85rem;color:#374151;line-height:1.65;margin-bottom:0.8rem;">{_e(bp.get("summary",""))}</p>'
        f'<div style="background:#FFFBF0;border-radius:8px;padding:0.75rem;'
        f'margin-bottom:0.7rem;border-left:3px solid #C9961A;">'
        f'<div style="font-size:0.68rem;color:#C9961A;font-weight:800;text-transform:uppercase;'
        f'margin-bottom:0.3rem;">💡 Financial Literacy Tip</div>'
        f'<div style="font-size:0.83rem;color:#374151;line-height:1.55;">{_e(bp.get("fin_lit_tip",""))}</div></div>'
        f'<div style="background:#F0FFF4;border-radius:8px;padding:0.75rem;border-left:3px solid #2D8A57;">'
        f'<div style="font-size:0.68rem;color:#2D8A57;font-weight:800;text-transform:uppercase;'
        f'margin-bottom:0.3rem;">🏆 Proof It Works</div>'
        f'<div style="font-size:0.83rem;color:#374151;line-height:1.55;">{_e(bp.get("success_case",""))}</div></div></div>'
    )

def lesson_card_html(m, local_ctx=""):
    sc = {"Idea Stage":("#EBF5F0","#1A5C38","💡"),
          "Startup Stage":("#FFFBF0","#C9961A","🚀"),
          "Growth Stage":("#F0FFF4","#2D8A57","📈"),
          "Mature MSME Stage":("#F5F0FF","#6B4FBB","🏢")}
    bg,fg,icon = sc.get(m.get("stage",""),("#F4FAF6","#374151","📌"))
    ug = (f'<div style="background:#EBF5F0;border-radius:8px;padding:0.75rem;margin-bottom:0.7rem;">'
          f'<div style="font-size:0.68rem;color:#1A5C38;font-weight:800;text-transform:uppercase;'
          f'margin-bottom:0.3rem;">🇺🇬 In Uganda</div>'
          f'<div style="font-size:0.83rem;color:#374151;line-height:1.55;">{_e(m.get("uganda_example",""))}</div></div>'
          if m.get("uganda_example") else "")
    ctx = (f'<div style="background:#E8F5EE;border-radius:8px;padding:0.6rem 0.8rem;margin-bottom:0.7rem;">'
           f'<span style="font-size:0.8rem;color:#1A5C38;font-weight:600;">📍 In your area: {_e(local_ctx)}</span></div>'
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
        f'<div style="color:#1A5C38;font-size:1rem;font-weight:700;">{icon} {_e(m.get("topic",""))}</div>'
        f'<span style="background:{bg};color:{fg};padding:0.22rem 0.65rem;'
        f'border-radius:14px;font-size:0.7rem;font-weight:700;">{_e(m.get("stage",""))}</span></div>'
        f'<p style="font-size:0.87rem;color:#374151;line-height:1.65;margin-bottom:0.9rem;">{_e(m.get("summary",""))}</p>'
        f'{ug}{ctx}{mis}'
        f'<div style="background:#F0FFF4;border-radius:8px;padding:0.75rem;border-left:3px solid #2D8A57;">'
        f'<div style="font-size:0.68rem;color:#2D8A57;font-weight:800;text-transform:uppercase;'
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
    Transcribes audio using Gemini (kept for compatibility).
    Uses explicit per-language prompts to avoid Luganda/Swahili confusion.
    Note: for voice queries, prefer process_audio_direct() instead —
    it skips transcription and gets results in one call.
    """
    client = _gemini_client()
    if client is None:
        return None

    _lang_prompts = {
        "English": (
            "This audio is in English. Transcribe exactly what is said. "
            "Return only the transcription text."
        ),
        "Swahili": (
            "This audio is in Swahili (Kiswahili). "
            "Transcribe exactly in Swahili. Return only the Swahili text."
        ),
        "Arabic": (
            "This audio is in Arabic. "
            "Transcribe exactly in Arabic. Return only the Arabic text."
        ),
        "Luganda": (
            "IMPORTANT: This audio is in LUGANDA (Oluganda/Ganda) — "
            "a Bantu language from Uganda. NOT Swahili. NOT English. "
            "Common Luganda words: nga, naye, kati, ate, ssebo, nyabo, "
            "webale, ndi, oli, tuli, ekitabo, omulimu, ssente, ebiweebwayo, "
            "abantu, okusoma, okufuna, obuwanguzi. "
            "Transcribe the Luganda exactly. Do NOT translate or switch to Swahili. "
            "Return ONLY the Luganda transcription."
        ),
    }
    try:
        audio_part = genai_types.Part.from_bytes(
            data=audio_bytes, mime_type="audio/webm"
        )
        resp = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[audio_part,
                      _lang_prompts.get(language_hint, _lang_prompts["English"])]
        )
        return resp.text.strip()
    except Exception:
        return None


def process_audio_direct(audio_bytes, language_name, user_profile,
                         gov_db, blueprint_db, masterclass_db):
    """
    Sends audio + database context to Gemini in ONE call — no transcription step.
    Gemini listens to the audio, understands intent, and responds directly.
    This is far better for Luganda because the model works from audio intent
    rather than needing a perfect intermediate transcript.
    Returns AI response string, or None on failure.
    """
    client = _gemini_client()
    if client is None:
        return None
    try:
        gov_summary = [
            {"title": c["title"], "stage": c.get("stage"),
             "sector": c.get("sector"),
             "eligibility": (c.get("eligibility") or "")[:150],
             "cost": c.get("cost", "")}
            for c in gov_db[:15]
        ]
        bp_summary = [
            {"title": b["title"], "sector": b.get("sector"),
             "tier": b.get("tier"),
             "summary": (b.get("summary") or "")[:120]}
            for b in blueprint_db[:6]
        ]
        fl_summary = [
            {"topic": m["topic"], "stage": m.get("stage"),
             "action_tip": (m.get("action_tip") or "")[:100]}
            for m in masterclass_db[:12]
        ]
        context = (
            f"User Profile:\n{json.dumps(user_profile, ensure_ascii=False)}\n\n"
            f"Available Grants & Programs:\n"
            f"{json.dumps(gov_summary, indent=1, ensure_ascii=False)}\n\n"
            f"Business Blueprints:\n"
            f"{json.dumps(bp_summary, indent=1, ensure_ascii=False)}\n\n"
            f"Financial Literacy Topics:\n"
            f"{json.dumps(fl_summary, indent=1, ensure_ascii=False)}"
        )
        if language_name == "Luganda":
            lang_instr = (
                "The user is speaking in LUGANDA (Oluganda) — a Bantu language "
                "from Uganda. NOT Swahili. NOT English. "
                "Listen to their Luganda audio and understand their question."
            )
        elif language_name == "Swahili":
            lang_instr = "The user is speaking in Swahili (Kiswahili)."
        elif language_name == "Arabic":
            lang_instr = "The user is speaking in Arabic."
        else:
            lang_instr = "The user is speaking in English."

        system_text = (
            f"You are the Katali platform assistant — advisor for Uganda's "
            f"MSME and youth community. {lang_instr}\n\n"
            f"Listen to their audio question, understand their intent, "
            f"search the database and give a personalised answer.\n\n"
            f"RULES:\n"
            f"- Respond ONLY in {language_name}\n"
            f"- Name specific programs, amounts and eligibility from the data\n"
            f"- Mobile-friendly: short paragraphs, clear headings\n"
            f"- End with exactly one next step the user can take today\n\n"
            f"DATABASE:\n{context}"
        )
        audio_part = genai_types.Part.from_bytes(
            data=audio_bytes, mime_type="audio/webm"
        )
        resp = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[audio_part, system_text]
        )
        return resp.text
    except Exception:
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

        prompt = f"""You are the Katali assistant — an intelligent advisor for Uganda's MSME and youth community.
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



ADMINS_FILE    = ".streamlit/admins.json"

ADMIN_ROLES = [
    "full_admin",      # CMS + Intelligence + USSD + Simulator preview
    "content_admin",   # CMS only — can add/edit cards
    "agency_admin",    # Can only manage their ministry's cards
    "readonly_admin",  # Intelligence Dashboard view only
]

# Pre-computed hashes (generated at setup, stored in secrets for super admin)
_TIMO_HASH = "bc2b55ec581f1785ccaafad348f8f0720512f2c1e5b376bfb8311b7a7549349d"

DEFAULT_ADMINS = [
    {
        "username":     "timo",
        "password_hash": _TIMO_HASH,
        "role":         "full_admin",
        "ministry":     "All",
        "created_by":   "jessicah",
        "active":       True,
        "created_at":   "2026-07-20T00:00:00",
    }
]

# ------------------------------------------------------------------
# AUTH HELPERS
# ------------------------------------------------------------------

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, stored_hash: str) -> bool:
    return hash_password(password) == stored_hash

def check_super_admin(username: str, password: str) -> bool:
    sa_user = st.secrets.get("SUPER_ADMIN_USERNAME", "jessicah")
    sa_hash = st.secrets.get(
        "SUPER_ADMIN_PASSWORD_HASH",
        "55a31a74de7901ab3b42484403627e016afaa091c876d4338064cd2868d35232"
    )
    return username == sa_user and verify_password(password, sa_hash)

def check_admin(username: str, password: str, accounts: list) -> dict | None:
    for acc in accounts:
        if acc.get("username") == username and acc.get("active", True):
            if verify_password(password, acc.get("password_hash", "")):
                return acc
    return None

def admin_can(role: str, permission: str) -> bool:
    """Check if an admin role has a given permission."""
    perms = {
        "full_admin":     {"cms", "intelligence", "ussd", "simulator", "management"},
        "content_admin":  {"cms"},
        "agency_admin":   {"cms"},
        "readonly_admin": {"intelligence"},
    }
    return permission in perms.get(role, set())

# ------------------------------------------------------------------
# MULTILINGUAL SUPPORT — UI Strings & Card Translation
# ------------------------------------------------------------------

UI_STRINGS = {
    "English": {
        "lang_label":        "🌍 Language:",
        "greeting_morning":  "Good morning",
        "greeting_afternoon":"Good afternoon",
        "greeting_evening":  "Good evening",
        "welcome_back":      "Welcome back",
        "welcome_new":       "Welcome to Katali!",
        "setup_profile":     "👆 **Set up your profile** to see grants and opportunities tailored to your district, stage, and sector.",
        "setup_btn":         "✏️ Set Up My Profile Now →",
        "stat_grants":       "Grants For You",
        "stat_bps":          "Business Models",
        "stat_lessons":      "Learning Topics",
        "grants_heading":    "🏆 Grants & Programs For You",
        "grants_available":  "🏆 Available Grants & Programs",
        "matched_to":        "Matched to:",
        "who_qualifies":     "✅ Who Qualifies",
        "cost":              "💰 Cost",
        "bps_heading":       "💡 Business Ideas to Explore",
        "quick_tip":         "💡 Quick Tip",
        "learning_heading":  "📚 Today's Learning",
        "fin_lit":           "Financial Literacy",
        "do_today":          "✅ Do This Today",
        "ask_heading":       "🎤 Ask Us Anything",
        "ask_caption":       "Speak or type — we'll search across all grants, programs, and business guides and give you a personalised answer.",
        "mic_prompt":        "🎤 Tap the microphone and speak in",
        "type_prompt":       "Or type your question here:",
        "placeholder":       "What grants are available for women starting a business in Kampala?",
        "find_btn":          "🔍 Find What's Relevant For Me",
        "found_heading":     "### 💡 Here's What We Found For You",
        "translating":       "Translating content…",
        "transcribing":      "Transcribing your recording…",
        "you_said":          "You said:",
        "transcribe_fail":   "⚠️ Could not transcribe. Try speaking more clearly, or type below.",
        "type_first":        "Please speak or type a question first.",
        "searching":         "Searching across grants, blueprints, and guides…",
        "sign_out":          "🚪 Sign Out",
    },
    "Swahili": {
        "lang_label":        "🌍 Lugha:",
        "greeting_morning":  "Habari ya asubuhi",
        "greeting_afternoon":"Habari ya mchana",
        "greeting_evening":  "Habari ya jioni",
        "welcome_back":      "Karibu tena",
        "welcome_new":       "Karibu Katali!",
        "setup_profile":     "👆 **Jaza wasifu wako** ili uone ruzuku na fursa zinazofaa wilaya yako, hatua yako, na sekta yako.",
        "setup_btn":         "✏️ Jaza Wasifu Wangu →",
        "stat_grants":       "Ruzuku Zako",
        "stat_bps":          "Mifano ya Biashara",
        "stat_lessons":      "Mada za Kujifunza",
        "grants_heading":    "🏆 Ruzuku na Programu Zako",
        "grants_available":  "🏆 Ruzuku na Programu Zinazopatikana",
        "matched_to":        "Inayofaa kwa:",
        "who_qualifies":     "✅ Anayestahili",
        "cost":              "💰 Gharama",
        "bps_heading":       "💡 Mawazo ya Biashara",
        "quick_tip":         "💡 Kidokezo",
        "learning_heading":  "📚 Mafunzo ya Leo",
        "fin_lit":           "Elimu ya Fedha",
        "do_today":          "✅ Fanya Hivi Leo",
        "ask_heading":       "🎤 Tuulize Chochote",
        "ask_caption":       "Sema au andika — tutatafuta katika ruzuku, programu, na miongozo yote na kukupa jibu linalokufaa.",
        "mic_prompt":        "🎤 Gonga kipaza sauti uongee kwa",
        "type_prompt":       "Au andika swali lako hapa:",
        "placeholder":       "Ruzuku gani zinapatikana kwa wanawake wanaoanzisha biashara Kampala?",
        "find_btn":          "🔍 Pata Kinachofaa Kwangu",
        "found_heading":     "### 💡 Hiki Ndicho Tulichokipata Kwako",
        "translating":       "Inatafsiri maudhui…",
        "transcribing":      "Inatafsiri sauti yako…",
        "you_said":          "Ulisema:",
        "transcribe_fail":   "⚠️ Haikuweza kutafsiri. Jaribu kusema wazi zaidi, au andika hapa chini.",
        "type_first":        "Tafadhali sema au andika swali kwanza.",
        "searching":         "Inatafuta katika ruzuku, mipango, na miongozo…",
        "sign_out":          "🚪 Toka",
    },
    "Arabic": {
        "lang_label":        "🌍 اللغة:",
        "greeting_morning":  "صباح الخير",
        "greeting_afternoon":"مساء الخير",
        "greeting_evening":  "مساء النور",
        "welcome_back":      "مرحباً بعودتك",
        "welcome_new":       "!مرحباً بك في Katali",
        "setup_profile":     "👆 **أكمل ملفك الشخصي** لترى المنح والفرص المناسبة لمنطقتك ومرحلتك وقطاعك.",
        "setup_btn":         "✏️ إعداد ملفي الشخصي →",
        "stat_grants":       "المنح المناسبة لك",
        "stat_bps":          "نماذج الأعمال",
        "stat_lessons":      "مواضيع التعلم",
        "grants_heading":    "🏆 المنح والبرامج المناسبة لك",
        "grants_available":  "🏆 المنح والبرامج المتاحة",
        "matched_to":        ":مطابق لـ",
        "who_qualifies":     "✅ من يستحق",
        "cost":              "💰 التكلفة",
        "bps_heading":       "💡 أفكار تجارية للاستكشاف",
        "quick_tip":         "💡 نصيحة سريعة",
        "learning_heading":  "📚 تعلّم اليوم",
        "fin_lit":           "الثقافة المالية",
        "do_today":          "✅ افعل هذا اليوم",
        "ask_heading":       "🎤 اسألنا أي شيء",
        "ask_caption":       "تحدث أو اكتب — سنبحث في جميع المنح والبرامج والأدلة ونعطيك إجابة شخصية.",
        "mic_prompt":        "🎤 اضغط الميكروفون وتحدث بـ",
        "type_prompt":       "أو اكتب سؤالك هنا:",
        "placeholder":       "ما المنح المتاحة للنساء اللواتي يبدأن مشروعاً في كمبالا؟",
        "find_btn":          "🔍 ابحث عن المناسب لي",
        "found_heading":     "### 💡 إليك ما وجدناه لك",
        "translating":       "جارٍ ترجمة المحتوى…",
        "transcribing":      "جارٍ نسخ تسجيلك…",
        "you_said":          ":قلت",
        "transcribe_fail":   "⚠️ تعذّر النسخ. حاول التحدث بوضوح أكثر، أو اكتب سؤالك أدناه.",
        "type_first":        "يرجى التحدث أو كتابة سؤال أولاً.",
        "searching":         "جارٍ البحث في المنح والمخططات والأدلة…",
        "sign_out":          "🚪 تسجيل الخروج",
    },
    "Luganda": {
        "lang_label":        "🌍 Lulimi:",
        "greeting_morning":  "Wasuze otya",
        "greeting_afternoon":"Osiibye otya",
        "greeting_evening":  "Oyiseebye otya",
        "welcome_back":      "Tukuwaaze okuddayo",
        "welcome_new":       "Tukuwaaze ku Katali!",
        "setup_profile":     "👆 **Yuzza ebikukwatako** okusobola okulaba ebiweebwayo n'emikisa egikwatana n'essaza lyo, engeri gye wazaamu, n'ensonga yo.",
        "setup_btn":         "✏️ Yuzza Ebikukwatako Ebyo →",
        "stat_grants":       "Ebiweebwayo Byawe",
        "stat_bps":          "Endowooza z'Omulimu",
        "stat_lessons":      "Ebintu by'Okusomesebwa",
        "grants_heading":    "🏆 Ebiweebwayo n'Emirimu Gyawe",
        "grants_available":  "🏆 Ebiweebwayo n'Emirimu Eginaabako",
        "matched_to":        "Ekikwatana ne:",
        "who_qualifies":     "✅ Ani Akwana",
        "cost":              "💰 Omuwendo",
        "bps_heading":       "💡 Ebirowoozo by'Omulimu",
        "quick_tip":         "💡 Ekigambo Eky'Amangu",
        "learning_heading":  "📚 Okusomesebwa kw'Olwaleero",
        "fin_lit":           "Okumanya Ssente",
        "do_today":          "✅ Kola Kino Olwaleero",
        "ask_heading":       "🎤 Tubuuze Ekintu Kyonna",
        "ask_caption":       "Yogerako oba wandiike — tunoonyeza mu biweebwayo byonna, emirimu, n'ebisinziira okukuwa okuddamu okukuteekateeka.",
        "mic_prompt":        "🎤 Nyiga ku makarofoni oyogereko mu lulimi lwa",
        "type_prompt":       "Oba wandiike ekibuuzo kyo wano:",
        "placeholder":       "Biweebwayo ki ebiriwo ku bakazi abaatandika omulimu e Kampala?",
        "find_btn":          "🔍 Nonya Ebikwatana Nawe",
        "found_heading":     "### 💡 Kino Kye Tulabye Olw'obusobozi Bwo",
        "translating":       "Tukitafsiranga ebinaabako…",
        "transcribing":      "Tukimanya ekyo kye yogedde…",
        "you_said":          "Wagamba:",
        "transcribe_fail":   "⚠️ Tetusobodde kukimanya. Gezaako okiyogera bulungi, oba wandiike wano.",
        "type_first":        "Yogerako oba wandiike ekibuuzo edda.",
        "searching":         "Tunoonyeza mu biweebwayo, endowooza z'omulimu, n'ebisinziira…",
        "sign_out":          "🚪 Vaamu",
    },
}

LANG_CODE_MAP = {
    "English": "en-UG",
    "Swahili":  "sw-KE",
    "Arabic":   "ar-SA",
    "Luganda":  "lg-UG",
}

GRANT_FIELDS  = ["title", "eligibility", "cost", "steps"]
BP_FIELDS     = ["title", "summary", "fin_lit_tip", "success_case"]
LESSON_FIELDS = ["topic", "summary", "action_tip", "uganda_example"]


@st.cache_data(ttl=7200, show_spinner=False)
def translate_batch(items_json: str, target_language: str,
                    fields_json: str, api_key: str) -> str:
    """
    Translates a batch of card dicts to target_language via Gemini.
    Uses st.cache_data — each unique (content × language) pair is only
    translated once per session, so switching languages back is instant.
    Returns JSON string of translated items (or original on failure).
    """
    if target_language == "English" or not api_key:
        return items_json
    try:
        items  = json.loads(items_json)
        fields = json.loads(fields_json)
        # Only send translatable fields to keep the prompt small
        batch  = [
            {k: item.get(k, "") for k in fields if item.get(k)}
            for item in items
        ]
        client = google_genai.Client(api_key=api_key)
        resp   = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=(
                f"Translate this JSON data to {target_language}.\n"
                "KEEP UNCHANGED: programme names (UDB, UWEP, YLP, NAADS etc.), "
                "phone numbers, UGX amounts, district and place names, URLs.\n"
                "Return ONLY a valid JSON array with the same structure. "
                "No markdown, no explanation.\n\n"
                + json.dumps(batch, ensure_ascii=False)
            )
        )
        raw        = resp.text.strip().replace("```json","").replace("```","").strip()
        translated = json.loads(raw)
        result     = []
        for i, item in enumerate(items):
            merged = dict(item)
            if i < len(translated):
                merged.update({k: v for k, v in translated[i].items() if v})
            result.append(merged)
        return json.dumps(result, ensure_ascii=False)
    except Exception:
        return items_json   # graceful fallback to English


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
    pdf.cell(0, 4, f"Katali | @edgelabanalytics | {datetime.now().strftime('%d %B %Y')}",
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
    img = qr.make_image(fill_color="#1A5C38", back_color="white")
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
                   "Available at your LC1 office. Scan the Katali QR code for the full interactive version with PDF downloads for every card.",
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
                   "1. Scan the Katali QR code at this LC1 office.  2. Select your business stage and sector.  3. Browse government services, business blueprints, and financial literacy lessons.  4. Download any individual card as a printable PDF to keep.",
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
                ("id_scanned", False), ("last_voice_query", ""),
                ("citizen_phone", ""),
                ("user_role", None),       # None | "citizen" | "admin" | "super_admin"
                ("admin_username", ""),
                ("admin_accounts", None),  # loaded from file on first run
                ("app_language", "🇬🇧 English"),
                ]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# Load admin accounts once
if st.session_state.admin_accounts is None:
    st.session_state.admin_accounts = load_json(ADMINS_FILE, DEFAULT_ADMINS)

# ------------------------------------------------------------------
# ==================================================================
# 10. AUTH ROUTING — entry point for the whole app
# ==================================================================

inject_css()
profile = st.session_state.user_profile

# ── SUPER ADMIN / ADMIN CSS (hide sidebar collapse arrow for citizens) ──
_HIDE_SIDEBAR_CSS = """
<style>
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] { display: none !important; }
section.main > div { padding-left: 1rem !important; }
</style>
"""

# ==================================================================
# LOGIN SCREEN
# ==================================================================
if not st.session_state.user_role:

    # Centred logo and tagline
    st.markdown("""
    <div style="text-align:center;padding:2.5rem 1rem 1.5rem;">
        <div style="font-size:3.5rem;margin-bottom:0.4rem;">🇺🇬</div>
        <div style="color:#1A5C38;font-size:1.9rem;font-weight:800;
        letter-spacing:-0.02em;margin-bottom:0.2rem;">Katali</div>
        <div style="color:#6C757D;font-size:0.9rem;margin-bottom:0.3rem;">
            Katali — Ignite. Connect. Grow.
        </div>
        <div style="display:flex;gap:0.5rem;justify-content:center;margin-top:0.6rem;">
            <span style="background:#EBF5F0;color:#1A5C38;padding:0.2rem 0.7rem;
            border-radius:12px;font-size:0.72rem;font-weight:600;">Grants</span>
            <span style="background:#FFFBF0;color:#C9961A;padding:0.2rem 0.7rem;
            border-radius:12px;font-size:0.72rem;font-weight:600;">Business Blueprints</span>
            <span style="background:#F0FFF4;color:#2D8A57;padding:0.2rem 0.7rem;
            border-radius:12px;font-size:0.72rem;font-weight:600;">Financial Literacy</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        login_type = st.radio(
            "Login as:",
            ["📱 Citizen", "🔐 Admin / Staff"],
            horizontal=True,
            key="login_type_select"
        )

        st.write("")

        if "Citizen" in login_type:
            st.markdown("""
            <div style="background:white;border-radius:16px;padding:1.6rem;
            box-shadow:0 6px 30px rgba(26,92,56,0.1);border-top:4px solid #C9961A;">
                <div style="color:#1A5C38;font-size:1.1rem;font-weight:800;
                margin-bottom:0.3rem;">Welcome</div>
                <div style="color:#6C757D;font-size:0.85rem;margin-bottom:1rem;">
                    Enter your phone number to access your personalised dashboard
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.form("citizen_login"):
                phone = st.text_input("📱 Phone number",
                                      placeholder="e.g. 0772 000 000",
                                      label_visibility="collapsed")
                st.caption("📱 Your phone number")
                if st.form_submit_button("Enter My Dashboard →",
                                         use_container_width=True, type="primary"):
                    if phone.strip():
                        st.session_state.citizen_phone = phone.strip()
                        st.session_state.user_role     = "citizen"
                        st.rerun()
                    else:
                        st.error("Please enter your phone number.")
            st.caption("🔒 No password needed. Your number personalises your experience only.")

        else:
            st.markdown("""
            <div style="background:white;border-radius:16px;padding:1.6rem;
            box-shadow:0 6px 30px rgba(26,92,56,0.1);border-top:4px solid #1A5C38;">
                <div style="color:#1A5C38;font-size:1.1rem;font-weight:800;
                margin-bottom:0.3rem;">Staff / Admin Login</div>
                <div style="color:#6C757D;font-size:0.85rem;margin-bottom:1rem;">
                    Ministry officers, agency admins, and platform staff
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.form("admin_login"):
                uname = st.text_input("Username", placeholder="Enter username")
                pword = st.text_input("Password", type="password",
                                      placeholder="Enter password")
                if st.form_submit_button("Sign In →",
                                         use_container_width=True, type="primary"):
                    if check_super_admin(uname.strip(), pword):
                        st.session_state.user_role      = "super_admin"
                        st.session_state.admin_username = uname.strip()
                        st.rerun()
                    else:
                        found = check_admin(uname.strip(), pword,
                                            st.session_state.admin_accounts)
                        if found:
                            st.session_state.user_role      = "admin"
                            st.session_state.admin_username = uname.strip()
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please try again.")


# ==================================================================
# CITIZEN APP
# ==================================================================
elif st.session_state.user_role == "citizen":

    # Hide sidebar completely for citizens
    st.markdown(_HIDE_SIDEBAR_CSS, unsafe_allow_html=True)

    citizen_phone = st.session_state.citizen_phone
    has_profile   = bool(profile.get("name"))
    citizen_name  = profile.get("name") or "Citizen"
    hour          = datetime.now().hour
    _greet_key    = "greeting_morning" if hour < 12 else \
                    "greeting_afternoon" if hour < 18 else "greeting_evening"

    # ── LANGUAGE SELECTOR — persistent across all tabs ────────────
    app_lang = st.radio(
        "Language",
        ["🇬🇧 English", "🇰🇪 Swahili", "🇸🇦 Arabic", "🇺🇬 Luganda"],
        horizontal=True,
        key="app_language_select",
        label_visibility="collapsed"
    )
    app_lang_name = app_lang.split(" ", 1)[1]
    _s            = UI_STRINGS[app_lang_name]
    _api_key      = st.secrets.get("GEMINI_API_KEY", "") if GEMINI_AVAILABLE else ""

    # ── TRANSLATE DATA once per language ──────────────────────────
    gov_db_all  = st.session_state.gov_db
    bp_db_all   = st.session_state.blueprint_db
    mc_db_all   = st.session_state.masterclass_db

    user_stage  = profile.get("stage",  "")
    user_sector = profile.get("sector", "")
    user_gender = profile.get("gender", "")
    user_dist   = profile.get("district", "")

    def _score_grants(db, stage, sector, gender):
        scored = []
        for c in db:
            sc = 1
            if stage  and stage.lower()  in (c.get("stage")  or "").lower(): sc += 3
            if sector and sector.lower() in (c.get("sector") or "").lower(): sc += 2
            if gender == "Female" and "women" in (c.get("eligibility") or "").lower(): sc += 2
            scored.append((sc, c))
        scored.sort(key=lambda x: -x[0])
        return [c for _, c in scored]

    matched_grants  = _score_grants(gov_db_all, user_stage, user_sector, user_gender)[:4]
    matched_bps     = ([b for b in bp_db_all
                        if not user_sector or
                        user_sector.lower() in (b.get("sector") or "").lower()][:3]
                       or bp_db_all[:3])
    all_lessons     = mc_db_all

    if app_lang_name != "English" and _api_key:
        with st.spinner(_s["translating"]):
            matched_grants = json.loads(translate_batch(
                json.dumps(matched_grants,  ensure_ascii=False),
                app_lang_name, json.dumps(GRANT_FIELDS),  _api_key))
            matched_bps    = json.loads(translate_batch(
                json.dumps(matched_bps,     ensure_ascii=False),
                app_lang_name, json.dumps(BP_FIELDS),     _api_key))
            all_lessons    = json.loads(translate_batch(
                json.dumps(all_lessons,     ensure_ascii=False),
                app_lang_name, json.dumps(LESSON_FIELDS), _api_key))

    matched_lesson = all_lessons[:1]

    # ── 4-TAB CITIZEN NAVIGATION ──────────────────────────────────
    tab_home, tab_services, tab_ask, tab_profile = st.tabs([
        "🏠 Home", "🎯 My Services", "🎤 Ask", "👤 Profile"
    ])

    # ──────────────────────────────────────────────────────────────
    # TAB 1: HOME
    # ──────────────────────────────────────────────────────────────
    with tab_home:
        # Welcome banner
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#051A0E 0%,#0A2818 45%,#1A5C38 100%);
        padding:1.4rem;border-radius:16px;margin-bottom:1.2rem;position:relative;overflow:hidden;">
            <div style="position:absolute;top:-20px;right:-20px;width:130px;height:130px;
            background:rgba(201,150,26,0.1);border-radius:50%;"></div>
            <div style="color:rgba(255,255,255,0.65);font-size:0.82rem;margin-bottom:0.25rem;">
                {_s[_greet_key]} 👋
            </div>
            <div style="color:white;font-size:1.55rem;font-weight:800;
            letter-spacing:-0.02em;margin-bottom:0.3rem;">
                {_s["welcome_back"] + ", " + citizen_name + "!" if has_profile
                 else _s["welcome_new"]}
            </div>
            <div style="color:#C9961A;font-size:0.88rem;font-weight:600;">
                {"📍 " + user_dist + " · " + user_stage if has_profile
                 else "📱 " + citizen_phone}
            </div>
            <div style="position:absolute;top:1rem;right:1rem;">
                <span style="background:rgba(201,150,26,0.2);color:#F5C842;
                padding:0.25rem 0.7rem;border-radius:20px;font-size:0.7rem;font-weight:700;">
                    🇺🇬 Uganda
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not has_profile:
            st.info(_s["setup_profile"])

        # Stats
        c1, c2, c3 = st.columns(3)
        with c1: st.metric(_s["stat_grants"],  len(matched_grants))
        with c2: st.metric(_s["stat_bps"],     len(bp_db_all))
        with c3: st.metric(_s["stat_lessons"], len(mc_db_all))

        st.write("---")

        # Top matched grants (compact)
        if has_profile:
            st.markdown(f"### {_s['grants_heading']}")
            st.caption(f"{_s['matched_to']} **{user_stage}** · **{user_sector or 'All'}** · **{user_dist or 'Uganda'}**")
        else:
            st.markdown(f"### {_s['grants_available']}")

        for card in matched_grants[:3]:
            is_ngo = card.get("id","").startswith("ngo")
            bc = "#2D8A57" if is_ngo else "#1A5C38"
            bg = "#E8F8F5" if is_ngo else "#EBF5F0"
            st.markdown(f"""
            <div style="background:white;border-left:5px solid {bc};border-radius:12px;
            padding:1rem 1.2rem;margin-bottom:0.7rem;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                <div style="color:#1A5C38;font-size:0.95rem;font-weight:700;
                margin-bottom:0.4rem;">{_e(card.get("title",""))}</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;">
                    <div style="background:#F0FBF4;border-radius:7px;padding:0.5rem;">
                        <div style="font-size:0.6rem;color:#1A5C38;font-weight:800;
                        text-transform:uppercase;margin-bottom:0.2rem;">{_e(_s["who_qualifies"])}</div>
                        <div style="font-size:0.77rem;color:#374151;">
                            {_e((card.get("eligibility") or "")[:80])}
                        </div>
                    </div>
                    <div style="background:#FFFBF0;border-radius:7px;padding:0.5rem;
                    border-left:3px solid #C9961A;">
                        <div style="font-size:0.6rem;color:#C9961A;font-weight:800;
                        text-transform:uppercase;margin-bottom:0.2rem;">{_e(_s["cost"])}</div>
                        <div style="font-size:0.77rem;color:#374151;font-weight:600;">
                            {_e(card.get("cost",""))}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.caption(f"→ See all in **My Services** tab")
        st.write("---")

        # Today's lesson
        if matched_lesson:
            lesson = matched_lesson[0]
            st.markdown(f"### {_s['learning_heading']}")
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#051A0E 0%,#1A5C38 100%);
            border-radius:14px;padding:1.4rem;">
                <div style="color:#C9961A;font-size:0.62rem;font-weight:800;
                text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;">
                    📚 {_e(lesson.get("stage",""))} · {_e(_s["fin_lit"])}
                </div>
                <div style="color:white;font-size:1rem;font-weight:800;margin-bottom:0.5rem;">
                    {_e(lesson.get("topic",""))}
                </div>
                <div style="background:rgba(201,150,26,0.2);border-radius:9px;
                padding:0.7rem;border-left:3px solid #C9961A;">
                    <div style="color:#F5C842;font-size:0.6rem;font-weight:800;
                    text-transform:uppercase;margin-bottom:0.25rem;">{_e(_s["do_today"])}</div>
                    <div style="color:white;font-size:0.85rem;font-weight:600;">
                        {_e(lesson.get("action_tip",""))}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Sign out
        st.write("---")
        if st.button(_s["sign_out"], use_container_width=False):
            st.session_state.citizen_phone = ""
            st.session_state.user_role     = None
            st.rerun()

    # ──────────────────────────────────────────────────────────────
    # TAB 2: MY SERVICES
    # ──────────────────────────────────────────────────────────────
    with tab_services:
        st.markdown("### 🎯 My Services")

        svc_cat = st.radio(
            "Category",
            ["🎯 Opportunities", "⭐ Success Stories", "📚 Financial Literacy"],
            horizontal=True,
            key="svc_category",
            label_visibility="collapsed"
        )

        st.write("")

        if "Opportunities" in svc_cat:
            st.caption(f"{len(matched_grants)} programs available"
                       + (f" · matched to your profile" if has_profile else ""))
            for card in matched_grants:
                is_ngo  = card.get("id","").startswith("ngo")
                bc      = "#2D8A57" if is_ngo else "#1A5C38"
                badge   = "🌍 NGO" if is_ngo else "🏛️ Gov"
                bb      = "#E8F8F5" if is_ngo else "#EBF5F0"
                with st.expander(f"**{card.get('title','')}**  ·  {badge}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        <div style="background:#F0FBF4;border-radius:8px;padding:0.7rem;
                        margin-bottom:0.5rem;">
                            <div style="font-size:0.62rem;color:#1A5C38;font-weight:800;
                            text-transform:uppercase;margin-bottom:0.3rem;">
                                {_e(_s["who_qualifies"])}
                            </div>
                            <div style="font-size:0.82rem;color:#374151;line-height:1.5;">
                                {_e(card.get("eligibility",""))}
                            </div>
                        </div>
                        <div style="background:#FFFBF0;border-radius:8px;padding:0.7rem;
                        border-left:3px solid #C9961A;">
                            <div style="font-size:0.62rem;color:#C9961A;font-weight:800;
                            text-transform:uppercase;margin-bottom:0.3rem;">
                                {_e(_s["cost"])}
                            </div>
                            <div style="font-size:0.85rem;color:#374151;font-weight:700;">
                                {_e(card.get("cost",""))}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        steps = card.get("steps","")
                        if steps:
                            st.markdown("**Steps to apply:**")
                            st.markdown(steps)
                    st.markdown(f"""
                    <div style="background:#F4FAF6;border-radius:7px;
                    padding:0.5rem 0.8rem;margin-top:0.5rem;">
                        <span style="font-size:0.8rem;color:#2D8A57;font-weight:600;">
                            📞 {_e(card.get("contacts",""))}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

        elif "Success" in svc_cat:
            st.caption(f"{len(matched_bps)} business models · real Uganda success cases")
            for bp in matched_bps:
                tier_colors = {
                    "Micro (Under UGX 5M)":        ("#E8F8F5","#2D8A57"),
                    "Small (UGX 5M - 20M)":        ("#EBF5F0","#1A5C38"),
                    "Medium/Commercial (UGX 20M+)": ("#FFFBF0","#C9961A"),
                }
                tbg, tfg = tier_colors.get(bp.get("tier",""), ("#F4FAF6","#6C757D"))
                with st.expander(f"**{bp.get('title','')}**  ·  {bp.get('tier','')}"):
                    st.markdown(f"""
                    <span style="background:{tbg};color:{tfg};padding:0.2rem 0.6rem;
                    border-radius:10px;font-size:0.72rem;font-weight:700;">
                        📂 {_e(bp.get("sector",""))}
                    </span>
                    """, unsafe_allow_html=True)
                    st.write("")
                    st.markdown(bp.get("summary",""))
                    if bp.get("fin_lit_tip"):
                        st.markdown(f"""
                        <div style="background:#FFFBF0;border-radius:8px;padding:0.8rem;
                        margin-top:0.6rem;border-left:3px solid #C9961A;">
                            <div style="font-size:0.62rem;color:#C9961A;font-weight:800;
                            text-transform:uppercase;margin-bottom:0.3rem;">
                                {_e(_s["quick_tip"])}
                            </div>
                            <div style="font-size:0.83rem;color:#374151;">
                                {_e(bp.get("fin_lit_tip",""))}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    if bp.get("success_case"):
                        st.markdown(f"""
                        <div style="background:#F0FFF4;border-radius:8px;padding:0.8rem;
                        margin-top:0.5rem;border-left:3px solid #2D8A57;">
                            <div style="font-size:0.62rem;color:#2D8A57;font-weight:800;
                            text-transform:uppercase;margin-bottom:0.3rem;">⭐ Success Story</div>
                            <div style="font-size:0.83rem;color:#374151;">
                                {_e(bp.get("success_case",""))}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        else:  # Financial Literacy
            st.caption(f"{len(all_lessons)} lessons · practical money skills for Uganda MSMEs")
            stage_filter = st.selectbox(
                "Filter by stage:",
                ["All Stages"] + STAGES,
                key="lesson_stage_filter"
            )
            filtered = ([m for m in all_lessons
                         if stage_filter == "All Stages" or
                         m.get("stage","") == stage_filter]
                        or all_lessons)
            for lesson in filtered:
                stage_colors = {
                    "Idea Stage":        ("#EBF5F0","#1A5C38","💡"),
                    "Startup Stage":     ("#FFFBF0","#C9961A","🚀"),
                    "Growth Stage":      ("#F0FFF4","#2D8A57","📈"),
                    "Mature MSME Stage": ("#F5F0FF","#6B4FBB","🏢"),
                }
                lbg, lfg, lic = stage_colors.get(lesson.get("stage",""),
                                                   ("#F4FAF6","#374151","📌"))
                with st.expander(f"{lic} **{lesson.get('topic','')}**"):
                    st.markdown(f"""
                    <span style="background:{lbg};color:{lfg};padding:0.2rem 0.6rem;
                    border-radius:10px;font-size:0.7rem;font-weight:700;">
                        {_e(lesson.get("stage",""))}
                    </span>
                    """, unsafe_allow_html=True)
                    st.write("")
                    st.markdown(lesson.get("summary",""))
                    if lesson.get("uganda_example"):
                        st.info(f"🇺🇬 **In Uganda:** {lesson.get('uganda_example','')}")
                    if lesson.get("common_mistake"):
                        st.warning(f"⚠️ **Common mistake:** {lesson.get('common_mistake','')}")
                    if lesson.get("action_tip"):
                        st.success(f"✅ **{_s['do_today']}:** {lesson.get('action_tip','')}")

    # ──────────────────────────────────────────────────────────────
    # TAB 3: ASK
    # ──────────────────────────────────────────────────────────────
    with tab_ask:
        st.markdown(f"### {_s['ask_heading']}")
        st.caption(_s["ask_caption"])

        # ── VOICE INPUT — audio goes directly to AI, no transcript shown ──
        try:
            dash_audio = st.audio_input(
                f"{_s['mic_prompt']} {app_lang_name}",
                key="dash_voice_audio"
            )
            if dash_audio:
                _dbytes = dash_audio.read()
                if GEMINI_AVAILABLE and _api_key:
                    # One combined spinner — listen + search + respond
                    with st.spinner(_s["searching"]):
                        _pc = profile or {"name":"","region":"","district":"",
                                          "stage":"","sector":"","gender":""}
                        _dr = process_audio_direct(
                            _dbytes, app_lang_name, _pc,
                            gov_db_all, bp_db_all, mc_db_all
                        )
                    if _dr:
                        st.markdown(_s["found_heading"])
                        st.markdown(_dr)
                        st.session_state.feedback_log.append({
                            "timestamp": datetime.now().isoformat(timespec="seconds"),
                            "program":   "Voice Query",
                            "status":    f"Voice ({app_lang_name})",
                            "district":  profile.get("district","unknown"),
                            "query":     f"[voice:{app_lang_name}]"
                        })
                        try:
                            save_json(FEEDBACK_FILE, st.session_state.feedback_log)
                        except Exception:
                            pass
                    else:
                        st.warning(_s["transcribe_fail"])
                else:
                    st.info("🔧 Add GEMINI_API_KEY to Streamlit secrets to enable voice.")
        except AttributeError:
            st.info("🎙️ Voice needs Streamlit ≥ 1.38. Type below.")

        # ── TEXT INPUT — always available as fallback ──────────────
        st.write("---")
        dash_q = st.text_area(
            _s["type_prompt"],
            value="",
            placeholder=_s["placeholder"],
            height=90,
            key="dash_voice_text"
        )
        if st.button(_s["find_btn"], use_container_width=True, type="primary"):
            _dq = dash_q.strip()
            if not _dq:
                st.warning(_s["type_first"])
            else:
                _pc = profile or {"name":"","region":"","district":"",
                                  "stage":"","sector":"","gender":""}
                with st.spinner(_s["searching"]):
                    _dr = process_voice_command_with_gemini(
                        _dq, _pc, gov_db_all, bp_db_all, mc_db_all)
                st.markdown(_s["found_heading"])
                st.markdown(_dr)
                st.caption(f"*{_dq}*")
                st.session_state.feedback_log.append({
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "program":   "Text Query",
                    "status":    f"Text ({app_lang_name})",
                    "district":  profile.get("district","unknown"),
                    "query":     _dq[:200]
                })
                try:
                    save_json(FEEDBACK_FILE, st.session_state.feedback_log)
                except Exception:
                    pass

    # ──────────────────────────────────────────────────────────────
    # TAB 4: PROFILE
    # ──────────────────────────────────────────────────────────────
    with tab_profile:
        st.markdown("### 👤 My Profile")
        st.caption("Fill in your details to get personalised grants and opportunities.")

        # ID Scanner
        with st.expander("🪪 **Scan Your National ID — fastest way to fill this form**",
                          expanded=not st.session_state["id_scanned"]):
            st.caption("Your ID is used only to fill this form. No NIN is stored.")
            sc_tab, up_tab = st.tabs(["📸 Camera", "📁 Upload"])
            with sc_tab:
                pf_cam = st.camera_input("Front of ID", key="ptab_cam")
                if pf_cam and not st.session_state["id_scanned"]:
                    with st.spinner("Reading ID…"):
                        _res = scan_national_id_with_gemini(pf_cam)
                    if _res and "error" not in _res:
                        st.session_state["prefill_name"]     = _res.get("given_names","")
                        st.session_state["prefill_district"] = _res.get("district","")
                        _r = get_user_region(_res.get("district",""))
                        st.session_state["prefill_region"]   = _r or ""
                        _sx = (_res.get("sex") or "").strip()
                        st.session_state["prefill_gender"]   = \
                            _sx if _sx in ["Male","Female"] else "Prefer not to say"
                        st.session_state["id_scanned"] = True
                        st.success("✅ ID read — form filled below. Edit before saving.")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ Try better lighting. ({_res.get('error','')})")
            with up_tab:
                pf_up = st.file_uploader("Front of ID",
                                          type=["jpg","jpeg","png"],
                                          key="ptab_up")
                if pf_up and not st.session_state["id_scanned"]:
                    with st.spinner("Reading ID…"):
                        _res = scan_national_id_with_gemini(pf_up)
                    if _res and "error" not in _res:
                        st.session_state["prefill_name"]     = _res.get("given_names","")
                        st.session_state["prefill_district"] = _res.get("district","")
                        _r = get_user_region(_res.get("district",""))
                        st.session_state["prefill_region"]   = _r or ""
                        _sx = (_res.get("sex") or "").strip()
                        st.session_state["prefill_gender"]   = \
                            _sx if _sx in ["Male","Female"] else "Prefer not to say"
                        st.session_state["id_scanned"] = True
                        st.success("✅ ID read — form filled below. Edit before saving.")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ Try a clearer photo. ({_res.get('error','')})")
            if st.session_state["id_scanned"]:
                col_m, col_b = st.columns([3,1])
                with col_m: st.success("✅ Form auto-filled — edit anything below.")
                with col_b:
                    if st.button("🔄 Rescan"):
                        for _k in ["prefill_name","prefill_district",
                                   "prefill_region","prefill_gender"]:
                            st.session_state[_k] = ""
                        st.session_state["id_scanned"] = False
                        st.rerun()

        st.write("---")
        if st.session_state["id_scanned"]:
            st.markdown("**✏️ Your Profile** *(auto-filled — edit anything, then save)*")
        else:
            st.markdown("**✏️ Tell us about yourself**")

        with st.form("citizen_profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                _dn    = profile.get("name") or st.session_state["prefill_name"]
                f_name = st.text_input("First name:", value=_dn,
                                        placeholder="e.g. Sarah")
                _ro    = ["Select Region"] + list(DISTRICTS_BY_REGION.keys())
                _sr    = profile.get("region","")
                _pr    = st.session_state["prefill_region"]
                _rv    = _sr if _sr in _ro else _pr
                _ri    = _ro.index(_rv) if _rv in _ro else 0
                f_region = st.selectbox("Your region:", _ro, index=_ri)
                _do    = ["Select District"] + \
                         (DISTRICTS_BY_REGION.get(f_region,[]) if f_region != "Select Region" else [])
                _sd    = profile.get("district","")
                _pd    = st.session_state["prefill_district"]
                _dv    = _sd if _sd in _do else _pd
                _di    = _do.index(_dv) if _dv in _do else 0
                f_district = st.selectbox("Your district:", _do, index=_di)
                f_stage = st.selectbox(
                    "Business stage:",
                    ["Select Stage"] + STAGES,
                    index=(STAGES.index(profile["stage"])+1)
                          if profile.get("stage") in STAGES else 0)
            with col2:
                f_sector = st.selectbox(
                    "Sector (optional):",
                    ["Not sure yet"] + SECTORS,
                    index=(SECTORS.index(profile["sector"])+1)
                          if profile.get("sector") in SECTORS else 0)
                _go    = ["Prefer not to say","Female","Male"]
                _sg    = profile.get("gender","Prefer not to say")
                _pg    = st.session_state["prefill_gender"]
                _gv    = _sg if _sg in _go else _pg
                f_gender = st.selectbox("Gender (optional):", _go,
                                         index=_go.index(_gv) if _gv in _go else 0)
                f_phone = st.text_input("Phone (optional):",
                                         value=profile.get("phone",""),
                                         placeholder="0772 000 000")

            st.caption("No NIN is collected. This profile is stored only in your current session.")
            if st.form_submit_button("💾 Save My Profile",
                                      use_container_width=True, type="primary"):
                if not f_name.strip():
                    st.warning("Please enter your first name.")
                elif f_district == "Select District" or f_region == "Select Region":
                    st.warning("Please select your region and district.")
                elif f_stage == "Select Stage":
                    st.warning("Please select your business stage.")
                else:
                    st.session_state.user_profile = {
                        "name": f_name.strip(), "region": f_region,
                        "district": f_district, "stage": f_stage,
                        "sector": f_sector if f_sector != "Not sure yet" else "",
                        "gender": f_gender, "phone": f_phone.strip(),
                        "registered_at": datetime.now().isoformat(timespec="seconds")
                    }
                    for _k in ["prefill_name","prefill_district",
                               "prefill_region","prefill_gender"]:
                        st.session_state[_k] = ""
                    st.session_state["id_scanned"] = False
                    st.success(f"✅ Profile saved! Welcome, {f_name.strip()}.")
                    st.rerun()

        if profile.get("name"):
            st.write("---")
            st.markdown("**Your current profile:**")
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Name:** {profile.get('name','—')}")
                st.write(f"**District:** {profile.get('district','—')}")
                st.write(f"**Stage:** {profile.get('stage','—')}")
            with c2:
                st.write(f"**Sector:** {profile.get('sector','Not set') or 'Not set'}")
                st.write(f"**Gender:** {profile.get('gender','Not set')}")
                if profile.get("phone"):
                    st.write(f"**Phone:** {profile.get('phone')}")
            if st.button("🗑️ Clear Profile"):
                st.session_state.user_profile = {}
                st.rerun()

        st.write("---")
        if st.button(_s["sign_out"], key="sign_out_profile"):
            st.session_state.citizen_phone = ""
            st.session_state.user_role     = None
            st.rerun()


# ==================================================================
# ADMIN / SUPER ADMIN APP
# ==================================================================
else:
    role     = st.session_state.user_role
    is_super = (role == "super_admin")
    adm_usr  = st.session_state.admin_username

    # Find this admin's record
    _adm_rec = next(
        (a for a in st.session_state.admin_accounts if a["username"] == adm_usr),
        {"role": "full_admin", "ministry": "All"}
    ) if not is_super else {"role": "super_admin", "ministry": "All"}

    adm_role = _adm_rec.get("role","full_admin")

    # Build sidebar nav based on permissions
    st.sidebar.markdown(
        f'<div style="padding:0.8rem 0.5rem 0.3rem;">'
        f'<div style="color:#C9961A;font-size:0.65rem;font-weight:800;'
        f'letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.2rem;">'
        f'{"👑 Super Admin" if is_super else "🔐 Admin"}</div>'
        f'<div style="color:white;font-size:1rem;font-weight:800;">{adm_usr}</div>'
        f'<div style="color:#A8D5B5;font-size:0.75rem;">'
        f'{_adm_rec.get("ministry","All")}</div></div>',
        unsafe_allow_html=True
    )
    st.sidebar.write("---")

    nav_options = []
    if is_super or admin_can(adm_role,"cms"):
        nav_options.append("🏛️ Content Management")
    if is_super or admin_can(adm_role,"intelligence"):
        nav_options.append("📊 Intelligence Dashboard")
    if is_super or admin_can(adm_role,"ussd"):
        nav_options.append("📟 USSD Simulator")
    if is_super or admin_can(adm_role,"simulator"):
        nav_options.append("📱 Service Preview")
    if is_super:
        nav_options.append("👑 Admin Management")
        nav_options.append("🔧 Developer Tools")

    view = st.sidebar.radio("Navigate:", nav_options,
                             label_visibility="collapsed")

    st.sidebar.write("---")
    if st.sidebar.button("🚪 Sign Out"):
        st.session_state.user_role      = None
        st.session_state.admin_username = ""
        st.rerun()

    # ── CONTENT MANAGEMENT (was Gov Admin CMS) ────────────────────
    if view == "🏛️ Content Management":
        branded_header("Content Management",
                        f"Publishing for {_adm_rec.get('ministry','All')} · {adm_usr}")
        # Reuse existing CMS view code
        gov_db      = st.session_state.gov_db
        blueprint_db = st.session_state.blueprint_db
        masterclass_db = st.session_state.masterclass_db

        cms_tab1, cms_tab2, cms_tab3 = st.tabs([
            "🎯 Opportunities", "⭐ Success Stories", "📚 Financial Literacy"
        ])

        with cms_tab1:
            st.markdown("### 🎯 Opportunities (Government & NGO Programs)")
            for i, card in enumerate(gov_db):
                with st.expander(f"**{card.get('title','')}** — {card.get('agency','')}"):
                    with st.form(f"edit_gov_{i}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            t  = st.text_input("Title",       card.get("title",""),  key=f"gt_{i}")
                            ag = st.text_input("Agency",      card.get("agency",""), key=f"gag_{i}")
                            el = st.text_area("Eligibility",  card.get("eligibility",""), key=f"gel_{i}", height=80)
                            co = st.text_input("Cost",        card.get("cost",""),   key=f"gco_{i}")
                        with c2:
                            st_ = st.text_input("Stage",     card.get("stage",""),   key=f"gst_{i}")
                            sec = st.text_input("Sector",    card.get("sector",""),  key=f"gse_{i}")
                            stp = st.text_area("Steps",      card.get("steps",""),   key=f"gsp_{i}", height=80)
                            cnt = st.text_input("Contacts",  card.get("contacts",""),key=f"gct_{i}")
                        if st.form_submit_button("💾 Save"):
                            gov_db[i].update({"title":t,"agency":ag,"eligibility":el,
                                              "cost":co,"stage":st_,"sector":sec,
                                              "steps":stp,"contacts":cnt})
                            save_json(GOV_DB_FILE, gov_db)
                            st.session_state.gov_db = gov_db
                            st.success("Saved ✅"); st.rerun()

        with cms_tab2:
            st.markdown("### ⭐ Success Stories (Business Blueprints)")
            for i, bp in enumerate(blueprint_db):
                with st.expander(f"**{bp.get('title','')}** — {bp.get('sector','')}"):
                    with st.form(f"edit_bp_{i}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            t   = st.text_input("Title",     bp.get("title",""),   key=f"bt_{i}")
                            sec = st.text_input("Sector",    bp.get("sector",""),  key=f"bse_{i}")
                            ti  = st.selectbox("Tier",
                                ["Micro (Under UGX 5M)","Small (UGX 5M - 20M)",
                                 "Medium/Commercial (UGX 20M+)"],
                                index=["Micro (Under UGX 5M)","Small (UGX 5M - 20M)",
                                       "Medium/Commercial (UGX 20M+)"].index(
                                       bp.get("tier","Micro (Under UGX 5M)")),
                                key=f"bti_{i}")
                            sm  = st.text_area("Summary",   bp.get("summary",""),  key=f"bsm_{i}", height=80)
                        with c2:
                            fl  = st.text_area("Financial Tip", bp.get("fin_lit_tip",""), key=f"bfl_{i}", height=80)
                            sc  = st.text_area("Success Case",  bp.get("success_case",""), key=f"bsc_{i}", height=80)
                            cap = st.text_input("Capital Required", bp.get("capital_required",""), key=f"bcp_{i}")
                        if st.form_submit_button("💾 Save"):
                            blueprint_db[i].update({"title":t,"sector":sec,"tier":ti,
                                                     "summary":sm,"fin_lit_tip":fl,
                                                     "success_case":sc,"capital_required":cap})
                            save_json(BLUEPRINT_DB_FILE, blueprint_db)
                            st.session_state.blueprint_db = blueprint_db
                            st.success("Saved ✅"); st.rerun()

        with cms_tab3:
            st.markdown("### 📚 Financial Literacy")
            for i, m in enumerate(masterclass_db):
                with st.expander(f"**{m.get('topic','')}** — {m.get('stage','')}"):
                    with st.form(f"edit_mc_{i}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            tp  = st.text_input("Topic",    m.get("topic",""),   key=f"mt_{i}")
                            st_ = st.selectbox("Stage",     ["Idea Stage","Startup Stage",
                                                              "Growth Stage","Mature MSME Stage"],
                                index=["Idea Stage","Startup Stage","Growth Stage",
                                       "Mature MSME Stage"].index(
                                       m.get("stage","Idea Stage")), key=f"ms_{i}")
                            sm  = st.text_area("Summary",   m.get("summary",""),  key=f"msm_{i}", height=80)
                        with c2:
                            ug  = st.text_area("Uganda Example", m.get("uganda_example",""), key=f"mug_{i}", height=60)
                            mm  = st.text_area("Common Mistake", m.get("common_mistake",""), key=f"mmm_{i}", height=60)
                            at  = st.text_input("Action Tip",    m.get("action_tip",""),     key=f"mat_{i}")
                        if st.form_submit_button("💾 Save"):
                            masterclass_db[i].update({"topic":tp,"stage":st_,"summary":sm,
                                                       "uganda_example":ug,"common_mistake":mm,
                                                       "action_tip":at})
                            save_json(MASTERCLASS_DB_FILE, masterclass_db)
                            st.session_state.masterclass_db = masterclass_db
                            st.success("Saved ✅"); st.rerun()

    # ── INTELLIGENCE DASHBOARD ────────────────────────────────────
    elif view == "📊 Intelligence Dashboard":
        branded_header("Intelligence Dashboard",
                        "National MSME Knowledge Infrastructure Analytics")
        feedback_log = st.session_state.feedback_log
        if not feedback_log:
            st.info("No data yet — citizen queries will appear here once logged.")
        else:
            df = pd.DataFrame(feedback_log)
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Total Queries", len(df))
            with c2: st.metric("Unique Districts", df["district"].nunique() if "district" in df else 0)
            with c3: st.metric("Programs Tracked", df["program"].nunique() if "program" in df else 0)
            st.write("---")
            st.markdown("### Query Log")
            st.dataframe(df.sort_values("timestamp", ascending=False)
                          .head(50), use_container_width=True)
            st.download_button(
                "⬇️ Download Full Log (CSV)",
                df.to_csv(index=False),
                "edge_lab_analytics.csv", "text/csv"
            )

    # ── USSD SIMULATOR ───────────────────────────────────────────
    elif view == "📟 USSD Simulator":
        branded_header("USSD Simulator", "Low-tech access for basic mobile phones")
        st.info("USSD simulator for testing feature-phone access flows.")
        st.markdown("*(Existing USSD simulator content here)*")

    # ── SERVICE PREVIEW ──────────────────────────────────────────
    elif view == "📱 Service Preview":
        branded_header("Service Preview", "WhatsApp-style citizen experience preview")
        st.info("Preview how citizens experience the platform.")
        st.markdown("*(Existing WhatsApp simulator content here)*")

    # ── ADMIN MANAGEMENT (Super Admin only) ──────────────────────
    elif view == "👑 Admin Management":
        branded_header("Admin Management",
                        "Create and manage administrators · Assign roles and ministries",
                        right_label="Super Admin")

        admins = st.session_state.admin_accounts

        # ── Stats
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Admins", len(admins))
        with c2: st.metric("Active",  sum(1 for a in admins if a.get("active",True)))
        with c3: st.metric("Inactive", sum(1 for a in admins if not a.get("active",True)))

        st.write("---")

        # ── Existing admins
        st.markdown("### Current Administrators")
        for i, adm in enumerate(admins):
            active_icon = "🟢" if adm.get("active",True) else "🔴"
            with st.expander(
                f"{active_icon} **{adm['username']}** · {adm['role']} · "
                f"{adm.get('ministry','All')}"
            ):
                with st.form(f"edit_admin_{i}"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        new_role = st.selectbox(
                            "Role", ADMIN_ROLES,
                            index=ADMIN_ROLES.index(adm["role"])
                            if adm["role"] in ADMIN_ROLES else 0,
                            key=f"ar_{i}")
                        new_min  = st.text_input("Ministry / Agency",
                                                   adm.get("ministry",""),
                                                   key=f"am_{i}")
                    with ec2:
                        new_pw  = st.text_input("Reset Password (leave blank to keep)",
                                                  type="password", key=f"ap_{i}")
                        new_act = st.checkbox("Active",
                                               value=adm.get("active",True),
                                               key=f"aa_{i}")
                    if st.form_submit_button("💾 Update Admin"):
                        admins[i]["role"]     = new_role
                        admins[i]["ministry"] = new_min
                        admins[i]["active"]   = new_act
                        if new_pw.strip():
                            admins[i]["password_hash"] = hash_password(new_pw.strip())
                        save_json(ADMINS_FILE, admins)
                        st.session_state.admin_accounts = admins
                        st.success(f"Admin '{adm['username']}' updated ✅")
                        st.rerun()

        st.write("---")

        # ── Create new admin
        st.markdown("### ➕ Create New Admin")
        with st.form("create_admin_form"):
            nc1, nc2 = st.columns(2)
            with nc1:
                new_uname = st.text_input("Username*")
                new_pw    = st.text_input("Password*", type="password")
            with nc2:
                new_role  = st.selectbox("Role", ADMIN_ROLES)
                new_min   = st.text_input("Ministry / Agency",
                                           placeholder="e.g. Ministry of Trade")

            role_desc = {
                "full_admin":     "Full access to CMS, Intelligence, USSD, and preview",
                "content_admin":  "Can add/edit content cards only",
                "agency_admin":   "Manages only their ministry's cards",
                "readonly_admin": "Can view Intelligence Dashboard only",
            }
            st.info(f"ℹ️ **{new_role}**: {role_desc.get(new_role,'')}")

            if st.form_submit_button("✅ Create Admin", type="primary"):
                if not new_uname.strip() or not new_pw.strip():
                    st.error("Username and password are required.")
                elif any(a["username"] == new_uname.strip() for a in admins):
                    st.error(f"Username '{new_uname}' already exists.")
                else:
                    new_admin = {
                        "username":      new_uname.strip(),
                        "password_hash": hash_password(new_pw.strip()),
                        "role":          new_role,
                        "ministry":      new_min.strip() or "All",
                        "created_by":    adm_usr,
                        "active":        True,
                        "created_at":    datetime.now().isoformat(timespec="seconds"),
                    }
                    admins.append(new_admin)
                    save_json(ADMINS_FILE, admins)
                    st.session_state.admin_accounts = admins
                    st.success(f"✅ Admin '{new_uname}' created with role '{new_role}'.")
                    st.rerun()

    # ── DEVELOPER TOOLS ──────────────────────────────────────────
    elif view == "🔧 Developer Tools":
        branded_header("Developer Tools", "Reset databases and platform controls",
                        right_label="Super Admin Only")
        st.warning("⚠️ These actions reset data and cannot be undone.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset Content Databases", use_container_width=True):
                save_json(GOV_DB_FILE,        DEFAULT_GOV_DB)
                save_json(BLUEPRINT_DB_FILE,  DEFAULT_BLUEPRINT_DB)
                save_json(MASTERCLASS_DB_FILE,DEFAULT_MASTERCLASS_DB)
                save_json(FEEDBACK_FILE,      [])
                st.session_state.gov_db        = load_json(GOV_DB_FILE,        DEFAULT_GOV_DB)
                st.session_state.blueprint_db  = load_json(BLUEPRINT_DB_FILE,  DEFAULT_BLUEPRINT_DB)
                st.session_state.masterclass_db= load_json(MASTERCLASS_DB_FILE,DEFAULT_MASTERCLASS_DB)
                st.session_state.feedback_log  = []
                st.success("✅ All databases reset to defaults.")
                st.rerun()
        with col2:
            if st.button("🗑️ Clear Feedback Log", use_container_width=True):
                save_json(FEEDBACK_FILE, [])
                st.session_state.feedback_log = []
                st.success("✅ Feedback log cleared.")
                st.rerun()
        st.write("---")
        st.markdown("### Admin Accounts File")
        st.code(json.dumps(st.session_state.admin_accounts, indent=2), language="json")
