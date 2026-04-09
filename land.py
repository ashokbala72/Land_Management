import streamlit as st
import os
import requests
import yfinance as yf
from dotenv import load_dotenv
from openai import AzureOpenAI

# =========================
# LOAD ENV
# =========================
load_dotenv()

AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MAPS_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-12-01-preview",
    azure_endpoint=AZURE_ENDPOINT
)

st.set_page_config(layout="wide")

# =========================
# CSS
# =========================
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f172a, #1e293b); }
h1 { color: white !important; }
label, .stMarkdown, .stText { color: white; }

.section-header {
    background-color: white;
    color: black;
    font-weight: 700;
    padding: 6px 10px;
    border-radius: 6px;
    margin-bottom: 10px;
}

.card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 15px;
}

input, button {
    color: black !important;
    background: white !important;
}
</style>
""", unsafe_allow_html=True)

def section_header(text):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)

# =========================
# COMPANY MAPPING
# =========================
TICKER_MAP = {
    "ExxonMobil": "XOM",
    "Chevron": "CVX",
    "NextEra Energy": "NEE"
}

DOMAIN_MAP = {
    "ExxonMobil": "exxonmobil.com",
    "Chevron": "chevron.com",
    "NextEra Energy": "nexteraenergy.com"
}

LOCATION_MAP = {
    "ExxonMobil": {"lat": 31.9686, "lon": -99.9018},
    "Chevron": {"lat": 37.7749, "lon": -122.4194},
    "NextEra Energy": {"lat": 27.6648, "lon": -81.5158}
}

# =========================
# FUNCTIONS
# =========================
def get_financials(company):
    ticker = yf.Ticker(TICKER_MAP[company])
    
    try:
        info = ticker.info
        revenue = info.get("totalRevenue", None)
        price = info.get("currentPrice", None)
    except:
        revenue, price = None, None

    if revenue:
        revenue = f"${revenue/1e9:.1f}B"
    else:
        revenue = "Not available"

    if not price:
        price = "N/A"

    return revenue, price


def fetch_news(company):
    url = f"https://newsapi.org/v2/everything?q={company}&apiKey={NEWS_API_KEY}"
    res = requests.get(url).json()
    return [a["title"] for a in res.get("articles", [])[:5]]


def ai_summary(text):
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an ESG and risk analyst."},
                {"role": "user", "content": f"""
Provide:
1. Sentiment score (0-100)
2. 2-line summary
3. Key risks (bullet points)

{text}
"""}
            ]
        )
        return response.choices[0].message.content
    except:
        return "AI analysis unavailable"


def get_map(company):
    loc = LOCATION_MAP[company]
    return f"""
    https://maps.googleapis.com/maps/api/staticmap?
    center={loc['lat']},{loc['lon']}
    &zoom=5
    &size=800x400
    &markers=color:red%7C{loc['lat']},{loc['lon']}
    &key={MAPS_KEY}
    """

# =========================
# UI
# =========================
st.title("📊 Company Intelligence Dashboard")

company = st.selectbox("Select Company", list(TICKER_MAP.keys()))

with st.spinner("Fetching live company data..."):
    revenue, price = get_financials(company)
    news = fetch_news(company)
    ai_insight = ai_summary(" ".join(news))

col1, col2, col3 = st.columns([1.2, 2, 1.2])

# =========================
# LEFT PANEL
# =========================
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    section_header("Revenue (B)")

    st.image(f"https://logo.clearbit.com/{DOMAIN_MAP[company]}")
    st.markdown(f"### {company}")

    st.markdown("**Revenue**")
    st.markdown(f"### {revenue}")

    st.markdown("**Stock Price**")
    st.markdown(f"### ${price}")

    # 🔥 USE CASE 3
    st.markdown("---")
    st.markdown("#### Compensation Estimation")

    # 🔥 SECTION HEADER
    st.markdown("#### Compensation Inputs - Land Size (acres) & Rate ($ per acre)")

# Inputs
    land_size = st.number_input("Land Size (acres)", value=100)
    rate = st.number_input("Rate ($/acre)", value=5000)
    st.markdown(f"""
<div style="
    background-color:#111827;
    padding:12px;
    border-radius:10px;
    margin-top:10px;
">
    <div style="font-size:12px; color:#9ca3af;">
        Estimated Compensation
    </div>
    <div style="font-size:28px; font-weight:700; color:#22c55e;">
        ${land_size * rate:,.0f}
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # SENTIMENT
    st.markdown('<div class="card">', unsafe_allow_html=True)
    section_header("Stakeholder Sentiment")
    st.progress(70)
    st.write(ai_insight[:200] + "...")
    with st.expander("View Detailed Analysis"):
        st.write(ai_insight)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# CENTER PANEL
# =========================
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    section_header("Company Map & Assets")

    st.image(get_map(company))

    asset_info = ai_summary(f"Describe key assets of {company}")
    st.write(asset_info)

    # 🔥 USE CASE 4
    st.markdown("---")
    st.markdown("#### Geospatial + Document Analysis")

    uploaded_file = st.file_uploader("Upload Land Document")

    if uploaded_file:
        text = uploaded_file.read().decode("utf-8", errors="ignore")
        with st.spinner("Analyzing document..."):
            st.write(ai_summary(f"Extract risks:\n{text}"))

    st.markdown('</div>', unsafe_allow_html=True)

    # STOCK
    st.markdown('<div class="card">', unsafe_allow_html=True)
    section_header("Stock Trend")
    hist = yf.Ticker(TICKER_MAP[company]).history(period="6mo")
    st.line_chart(hist["Close"])
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# RIGHT PANEL
# =========================
with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    section_header("AI Insights")

    st.write(ai_insight)

    # 🔥 USE CASE 5
    st.markdown("---")
    st.markdown("#### Document Intelligence")

    files = st.file_uploader("Upload Documents", accept_multiple_files=True)

    if files:
        for file in files:
            text = file.read().decode("utf-8", errors="ignore")
            with st.spinner(f"Processing {file.name}..."):
                result = ai_summary(f"Extract obligations:\n{text}")
            st.write(f"📄 {file.name}")
            st.write(result)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    section_header("Latest News")

    for n in news:
        st.write(f"- {n}")

    st.markdown('</div>', unsafe_allow_html=True)