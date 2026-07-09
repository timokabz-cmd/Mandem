import streamlit as st
import pandas as pd
import json
import os
import uuid
from datetime import datetime

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ------------------------------------------------------------------
# 1. Page Configuration
# ------------------------------------------------------------------
st.set_page_config(page_title="Edge Lab Platform", page_icon="🇺🇬", layout="wide")

# ------------------------------------------------------------------
# 2. Shared Taxonomies
# ------------------------------------------------------------------
STAGES = ["Idea Stage", "Startup Stage", "Growth Stage", "Mature MSME Stage"]
SECTORS = ["Agriculture & Agribusiness", "Trade & Retail", "Digital & ICT",
           "Manufacturing", "Logistics & Transport"]
CAPITAL_TIERS = ["Micro (Under UGX 5M)", "Small (UGX 5M - 20M)", "Medium/Commercial (UGX 20M+)"]

DISTRICTS_BY_REGION = {
    "Central": sorted(["Kampala", "Wakiso", "Mukono", "Buikwe", "Kayunga", "Luweero",
                        "Masaka City", "Mpigi", "Mubende", "Mityana", "Nakasongola",
                        "Kalangala", "Gomba", "Kiboga", "Kyankwanzi", "Lwengo",
                        "Lyantonde", "Rakai", "Sembabule", "Bukomansimbi", "Kalungu"]),
    "Eastern": sorted(["Jinja City", "Mbale City", "Soroti City", "Tororo", "Iganga",
                        "Kamuli", "Pallisa", "Bugiri", "Busia", "Mayuge", "Namutumba",
                        "Luuka", "Buyende", "Kaliro", "Namayingo", "Kibuku", "Kumi",
                        "Ngora", "Serere", "Kaberamaido", "Amuria", "Katakwi",
                        "Bududa", "Manafwa", "Namisindwa", "Sironko", "Bulambuli", "Butaleja"]),
    "Northern": sorted(["Gulu City", "Lira City", "Arua City", "Kitgum", "Pader",
                         "Apac", "Dokolo", "Amolatar", "Oyam", "Kole", "Alebtong",
                         "Otuke", "Agago", "Lamwo", "Nwoya", "Amuru", "Nebbi",
                         "Zombo", "Koboko", "Maracha", "Moyo", "Adjumani", "Yumbe",
                         "Obongi", "Omoro"]),
    "Western": sorted(["Mbarara City", "Kabale", "Fort Portal City", "Kasese", "Bushenyi",
                        "Ntungamo", "Rukungiri", "Kanungu", "Kisoro", "Isingiro",
                        "Kiruhura", "Buhweju", "Mitooma", "Rubirizi", "Sheema",
                        "Ibanda", "Hoima City", "Kibaale", "Masindi", "Buliisa",
                        "Kiryandongo", "Kagadi", "Kakumiro", "Kazo", "Rwampara"])
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
    st.title("👤 Your Profile")
    st.caption("Personalise your experience. Telling us your district and business stage means every tab shows content most relevant to you. This information stays only in your current browser session — nothing is stored on a server or shared with anyone.")

    if not profile.get("name"):
        st.info("You have not set up a profile yet. Fill in the form below — it takes 30 seconds and you can change anything at any time.")

    with st.form("profile_form"):
        st.markdown("### Tell us about yourself")
        col1, col2 = st.columns(2)

        with col1:
            f_name = st.text_input("First name:", value=profile.get("name", ""), placeholder="e.g. Sarah")
            f_region = st.selectbox("Your region:", ["Select Region"] + list(DISTRICTS_BY_REGION.keys()),
                                    index=0)
            districts_for_region = DISTRICTS_BY_REGION.get(f_region, []) if f_region != "Select Region" else []
            current_district = profile.get("district", "")
            district_opts = ["Select District"] + districts_for_region
            default_dist_idx = district_opts.index(current_district) if current_district in district_opts else 0
            f_district = st.selectbox("Your district:", district_opts, index=default_dist_idx)
            f_stage = st.selectbox("Your current business stage:",
                                   ["Select Stage"] + STAGES,
                                   index=(STAGES.index(profile["stage"]) + 1) if profile.get("stage") in STAGES else 0)

        with col2:
            f_sector = st.selectbox("Your main sector of interest (optional):",
                                    ["Not sure yet"] + SECTORS,
                                    index=(SECTORS.index(profile["sector"]) + 1) if profile.get("sector") in SECTORS else 0)
            f_gender = st.selectbox("Gender (optional — helps us flag relevant grants like GROW/UWEP):",
                                    ["Prefer not to say", "Female", "Male"],
                                    index=["Prefer not to say", "Female", "Male"].index(profile.get("gender", "Prefer not to say")))
            f_phone = st.text_input("Phone number (optional — for future WhatsApp reminder opt-in):",
                                    value=profile.get("phone", ""),
                                    placeholder="e.g. 0772 000 000")

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
                st.success(f"✅ Profile saved! Welcome, {f_name.strip()}. Switch to the Citizen WhatsApp Simulator to see your personalized content.")
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

# ==================================================================
# VIEW 1: CITIZEN WHATSAPP SIMULATOR
# ==================================================================
elif view == "📱 Citizen WhatsApp Simulator":
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
                    st.markdown(f"🤖 📄 **OFFICIAL REGULATORY SERVICE: {card.get('title')}**")
                    st.markdown(f"* **Ministry/Agency:** {card.get('agency')}")
                    st.markdown(f"* **Qualifications:** {card.get('eligibility')}")
                    st.markdown(f"* **Execution Steps:** {card.get('steps')}")
                    st.markdown(f"* **Statutory Fee:** `{card.get('cost')}`")
                    st.markdown(f"* **Direct Contact Point:** *{card.get('contacts')}*")
                    if local_ctx:
                        st.info(f"📍 **In your area ({profile.get('district', 'your district')}):** {local_ctx}")
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
                    st.markdown(f"### 💡 {bp.get('title')}")
                    st.caption(f"Sector: {bp.get('sector')} | Capital Tier: {bp.get('tier')}")
                    st.markdown(f"💰 **Estimated Capital:** `{bp.get('capital_required')}`")
                    st.write(bp.get("summary"))
                    st.info(f"💡 **Financial Literacy Tip:** {bp.get('fin_lit_tip')}")
                    st.success(f"🏆 **Proof It Works:** {bp.get('success_case')}")
                    st.markdown(f"🔗 {bp.get('media_anchor')}")
                    if local_ctx:
                        st.info(f"📍 **In your area ({profile.get('district', 'your district')}):** {local_ctx}")
                    if PDF_AVAILABLE:
                        pdf_bytes = generate_blueprint_pdf(bp, profile)
                        if pdf_bytes:
                            st.download_button("📄 Download Blueprint PDF", data=pdf_bytes,
                                               file_name=f"{bp['id']}.pdf", mime="application/pdf",
                                               key=f"dl_bp_{bp['id']}")
                    st.write("---")
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
                    st.markdown(f"##### 📌 {m['topic']} — {m['stage']}")
                    st.write(m["summary"])
                    if m.get("uganda_example"):
                        st.info(f"🇺🇬 **In Uganda:** {m['uganda_example']}")
                    if local_ctx and (m.get("topic", "") in ["Saving & Emergency Funds",
                                                              "Understanding SACCOs vs Banks",
                                                              "Credit, Loans & Borrowing",
                                                              "Mobile Money & Digital Finance"]):
                        st.info(f"📍 **In your area ({profile.get('district', 'your district')}):** {local_ctx}")
                    if m.get("common_mistake"):
                        st.warning(f"⚠️ **Common Mistake:** {m['common_mistake']}")
                    st.info(f"✅ **Do This Now:** {m['action_tip']}")
                    if PDF_AVAILABLE:
                        pdf_bytes = generate_masterclass_pdf(m, profile, local_ctx if local_ctx else "")
                        if pdf_bytes:
                            st.download_button("📄 Download This Lesson as PDF", data=pdf_bytes,
                                               file_name=f"{m['id']}_lesson.pdf", mime="application/pdf",
                                               key=f"dl_fl_ci_{m['id']}")
                    st.write("---")

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
                st.markdown(f"##### 📌 {m['topic']} — {m['stage']}")
                st.write(m["summary"])
                if m.get("uganda_example"):
                
