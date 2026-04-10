import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import time

# -----------------------------
# LOAD ENV
# -----------------------------
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# -----------------------------
# INIT OPENAI
# -----------------------------
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def call_openai(prompt):
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ OpenAI Error: {e}"

# -----------------------------
# CACHE NEWS (FIX FOR 429)
# -----------------------------
@st.cache_data(ttl=300)
def get_news():
    url = f"https://newsapi.org/v2/everything?q=Equinor&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    return response

# -----------------------------
# UI CONFIG
# -----------------------------
st.set_page_config(layout="wide")

st.markdown("""
<h1 style='text-align: center; color: #1f4e79;'>
    Equinor US Land Management Dashboard
</h1>
<h4 style='text-align: center; color: gray; margin-top: -10px;'>
    Powered by TCS Gen AI & Azure OpenAI
</h4>
<hr>
""", unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stSidebar"] > div:first-child {
    padding-top: 120px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SITE SELECTOR
# -----------------------------
site = st.selectbox("Select Site", [
    "Houston", "Austin", "Midland", "North Dakota"
])

# -----------------------------
# SIDEBAR MENU
# -----------------------------
use_case = st.sidebar.radio(
    "Choose Use Case",
    ["Stakeholder Sentiment", "Compliance Risk", "Compensation Forecast", "Land Agreement", "Land Access Planning", "AI Insights"]
)

# =============================
# UC1 - NEWS SENTIMENT (FIXED)
# =============================
if use_case == "Stakeholder Sentiment":
    st.markdown("""
    <div style="background-color:#E3F2FD; padding:12px; border-radius:10px;">
        <b>1️⃣ Stakeholder Sentiment</b>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Fetch News"):

        with st.spinner("Fetching news..."):
            time.sleep(1)  # prevent rapid clicks

            response = get_news()

            # 🚨 HANDLE RATE LIMIT
            if response.status_code == 429:
                st.warning("⚠️ Rate limit reached. Showing sample data instead.")

                articles = [
                    {"title": "Equinor faces environmental concerns in Texas"},
                    {"title": "Oil drilling regulations tightening in US"},
                    {"title": "Energy companies under ESG pressure"}
                ]

            elif response.status_code != 200:
                st.error(f"News API Error: {response.status_code}")
                articles = []

            else:
                data = response.json()
                articles = data.get("articles", [])

            if not articles:
                st.warning("No news found")
            else:
                for article in articles[:5]:
                    title = article.get("title", "")
                    desc = article.get("description", "")

                    st.write(f"📰 {title}")

                    prompt = f"""
                    Analyze sentiment (Positive/Neutral/Negative),
                    risk level (Low/Medium/High),
                    and give 1-line summary:

                    {title} {desc}
                    """

                    result = call_openai(prompt)
                    st.write(result)
                    st.markdown("---")

# =============================
# UC2
# =============================
elif use_case == "Compliance Risk":
    st.markdown("""
    <div style="background-color:#E8F5E9; padding:12px; border-radius:10px;">
        <b>2️⃣ Compliance Risk</b>
    </div>
    """, unsafe_allow_html=True)

    file = st.file_uploader("Upload Compliance File")

    if file:
        text = file.read().decode("utf-8")

        with st.spinner("Analyzing..."):
            prompt = f"""
            Analyze compliance data and return:
            - obligations with risk + status
            - alerts
            - recommendations

            {text}
            """

            result = call_openai(prompt)
            st.write(result)

# =============================
# UC3
# =============================
elif use_case == "Compensation Forecast":
    st.markdown("""
    <div style="background-color:#FFF3E0; padding:12px; border-radius:10px;">
        <b>3️⃣ Compensation</b>
    </div>
    """, unsafe_allow_html=True)

    json_file = st.file_uploader("Upload JSON", type="json")

    if json_file:
        data = json.load(json_file)

        with st.spinner("Processing..."):
            prompt = f"""
            Analyze compensation:
            - totals by site
            - forecast (5% increase)
            - anomalies
            - insights

            DATA:
            {data}
            """

            result = call_openai(prompt)
            st.write(result)

# =============================
# UC4
# =============================
elif use_case == "Land Agreement":
    st.markdown("""
    <div style="background-color:#F3E5F5; padding:12px; border-radius:10px;">
        <b>4️⃣ Land Agreement</b>
    </div>
    """, unsafe_allow_html=True)

    doc = st.file_uploader("Upload Agreement", key="doc")

    if doc:
        text = doc.read().decode("utf-8")

        with st.spinner("Extracting..."):
            prompt = f"""
            Extract:
            - land details
            - stakeholders
            - risks
            - compliance
            - alerts

            {text}
            """

            result = call_openai(prompt)
            st.write(result)

# =============================
# UC5
# =============================
elif use_case == "Land Access Planning":
    st.markdown("""
    <div style="background-color:#E0F7FA; padding:12px; border-radius:10px;">
        <b>5️⃣ Land Access Planning</b>
    </div>
    """, unsafe_allow_html=True)

    geo_doc = st.file_uploader("Upload Geo Doc", key="geo")

    if geo_doc:
        text = geo_doc.read().decode("utf-8")

        with st.spinner("Analyzing land..."):
            prompt = f"""
            Analyze:
            - feasibility
            - constraints
            - risks
            - recommendation
            - drilling decision

            {text}
            """

            result = call_openai(prompt)
            st.write(result)

# =============================
# AI INSIGHTS
# =============================
elif use_case == "AI Insights":
    st.markdown("""
    <div style="background-color:#FBE9E7; padding:12px; border-radius:10px;">
        <b>💡 AI Insights</b>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Generate Insights"):
        with st.spinner("Thinking..."):
            prompt = """
            Provide executive insights based on:
            - sentiment
            - compliance
            - compensation
            - land agreements
            - land access

            Output:
            - key risks
            - recommendations
            - trends
            """

            result = call_openai(prompt)
            st.write(result)