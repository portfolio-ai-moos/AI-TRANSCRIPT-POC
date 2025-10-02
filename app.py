"""
AI Transcript Analyzer V2 - Streamlit Frontend
Portfolio project showcasing RAG architecture with Gemini & Supabase
Professional SaaS-grade dashboard
"""

import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from typing import Dict, List
import time

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Transcript Analyzer | Enterprise RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional high-tech styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container styling */
    .main {
        background: #0f172a;
        color: #e2e8f0;
    }
    
    /* Portfolio Banner */
    .portfolio-banner {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        padding: 0.75rem 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
    }
    
    .portfolio-banner h4 {
        color: white;
        margin: 0;
        font-size: 1.1rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .portfolio-banner p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
    }
    
    /* Header styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(120deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
        letter-spacing: -2px;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 2rem;
        text-align: center;
        font-weight: 400;
    }
    
    /* Info cards */
    .stAlert {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
    }
    
    /* Tech badge styling */
    .tech-badge {
        display: inline-block;
        padding: 0.5rem 1.2rem;
        margin: 0.4rem;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* Complaint card styling */
    .complaint-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2rem;
        border-radius: 16px;
        border-left: 4px solid #3b82f6;
        margin: 1.5rem 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        transition: all 0.3s;
        color: #e2e8f0;
    }
    
    .complaint-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(59, 130, 246, 0.3);
        border-left-color: #8b5cf6;
    }
    
    .complaint-card h4 {
        color: #3b82f6;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .complaint-card p {
        color: #cbd5e1;
        font-size: 1rem;
        line-height: 1.6;
        margin: 0.5rem 0;
    }
    
    .complaint-card strong {
        color: #3b82f6;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 0 8px 16px rgba(59, 130, 246, 0.4);
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        box-shadow: 0 12px 24px rgba(59, 130, 246, 0.6);
        transform: translateY(-2px);
    }
    
    /* Input styling */
    .stTextArea textarea {
        background: #1e293b;
        border-radius: 12px;
        border: 2px solid #334155;
        padding: 1rem;
        font-size: 1rem;
        color: #e2e8f0;
    }
    
    .stTextArea textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #3b82f6;
    }
    
    /* Code block styling */
    .stCodeBlock {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    
    code {
        color: #3b82f6 !important;
        background: #1e293b !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
    }
    
    /* Divider */
    hr {
        border-color: #334155 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #1e293b;
        border-radius: 8px;
        color: #e2e8f0 !important;
    }
    
    /* Source snippet card */
    .source-snippet {
        background: #1e293b;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 3px solid #8b5cf6;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .source-snippet pre {
        color: #cbd5e1;
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 0;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

# API Endpoint - Update this after Vercel deployment
DEFAULT_API_ENDPOINT = "https://your-project.vercel.app/api/analyze"
API_ENDPOINT = st.secrets.get("API_ENDPOINT", DEFAULT_API_ENDPOINT)

# ============================================================================
# SIDEBAR - PORTFOLIO INFO
# ============================================================================

with st.sidebar:
    st.markdown("### 👨‍💻 Portfolio Showcase")
    st.markdown("Deze applicatie demonstreert **full-stack AI engineering** vaardigheden")
    
    st.divider()
    
    st.markdown("### 🛠️ Tech Stack")
    st.markdown("""
    <div>
        <span class="tech-badge">Gemini 2.5</span>
        <span class="tech-badge">Supabase</span>
        <span class="tech-badge">pgvector</span>
        <span class="tech-badge">Vercel</span>
        <span class="tech-badge">Streamlit</span>
        <span class="tech-badge">Pydantic</span>
        <span class="tech-badge">Python</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 🏗️ Architecture")
    st.markdown("""
    - **Vector DB**: Supabase + pgvector (768-dim)
    - **Embeddings**: Gemini embedding-001
    - **LLM**: Gemini 2.5 Flash
    - **Backend**: Vercel Serverless Python
    - **RAG Pattern**: Direct API integration
    """)
    
    st.divider()
    
    st.markdown("### ⚙️ Production Status")
    if API_ENDPOINT != DEFAULT_API_ENDPOINT:
        st.success("✅ Live Production API")
        st.caption("🌐 Deployed on Vercel")
    else:
        st.warning("⚠️ Demo endpoint")
        st.caption("Configure production URL")

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Portfolio Banner
st.markdown("""
<div class="portfolio-banner">
    <h4>🎓 Portfolio Project | AI Engineering Showcase</h4>
    <p>Deze applicatie toont mijn vaardigheden in moderne AI architectuur, RAG-systemen, en production-ready deployments</p>
</div>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🧠 AI Transcript Analyzer</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Enterprise RAG System | Gemini 2.5 Flash + Supabase Vector Search</p>',
    unsafe_allow_html=True
)

# Info cards
col1, col2, col3 = st.columns(3)
with col1:
    st.info("📊 **Structured Output**\nPydantic-validated JSON responses")
with col2:
    st.info("🔍 **Vector Search**\nCosine similarity with pgvector")
with col3:
    st.info("🎯 **Production-Ready**\nLazy initialization for Vercel")

st.divider()

# ============================================================================
# ANALYSIS INTERFACE
# ============================================================================

st.markdown("### 💬 Stel een vraag aan de transcript database")
st.caption("🔍 De AI doorzoekt duizenden transcripten met vector similarity search")

# Input row with better UX
col_input, col_button = st.columns([5, 1])

with col_input:
    question = st.text_area(
        "Jouw vraag:",
        placeholder="Bijvoorbeeld: Wat zijn de meest voorkomende klachten over de levertijd?",
        height=120,
        help="De AI zal de transcript database doorzoeken en een gestructureerde analyse geven",
        label_visibility="collapsed"
    )

with col_button:
    st.write("")  # Spacing
    st.write("")  # Spacing
    submitted = st.button("🚀 Analyseer", use_container_width=True, type="primary")
    clear_btn = st.button("🗑️ Clear", use_container_width=True)

# ============================================================================
# API CALL & RESULTS
# ============================================================================

def analyze_question(question: str) -> Dict:
    """Call the RAG API and return structured results"""
    payload = {"question": question}
    response = requests.post(API_ENDPOINT, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


if submitted and question.strip():
    # Professional status tracking
    with st.status("🔄 RAG Pipeline wordt uitgevoerd...", expanded=True) as status:
        try:
            # Step 1: Vector Search
            st.write("🔍 **Stap 1/3:** Vector similarity search in Supabase...")
            time.sleep(0.5)  # Visual feedback
            
            # Step 2: API Call
            st.write("🤖 **Stap 2/3:** Gemini AI analyse wordt gegenereerd...")
            result = analyze_question(question.strip())
            
            # Step 3: Complete
            st.write("✅ **Stap 3/3:** Gestructureerde output ontvangen!")
            time.sleep(0.3)
            
            status.update(label="✅ Analyse voltooid!", state="complete", expanded=False)
            
            # Success banner
            st.success("🎉 **Analyse succesvol!** De AI heeft je vraag verwerkt met RAG.")
            
            # Display question
            st.markdown(f"**📝 Vraag:** {result.get('question', question)}")
            
            st.divider()
            
            # ================================================================
            # KLACHTEN VISUALISATIE
            # ================================================================
            
            analysis = result.get("analysis", {})
            klachten = analysis.get("klachten", [])
            
            if klachten:
                st.markdown("### 📊 Geïdentificeerde Klachten")
                
                # Sort by frequency
                sorted_klachten = sorted(
                    klachten,
                    key=lambda x: x.get("frequentie", 0),
                    reverse=True
                )
                
                # Metrics row
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Totaal Klachten",
                        len(sorted_klachten),
                        delta=None,
                        help="Aantal unieke klachten geïdentificeerd"
                    )
                with col2:
                    total_freq = sum(k.get("frequentie", 0) for k in sorted_klachten)
                    st.metric(
                        "Totale Frequentie",
                        total_freq,
                        delta=None,
                        help="Totaal aantal keer genoemd"
                    )
                with col3:
                    if sorted_klachten:
                        top_klacht = sorted_klachten[0].get("naam", "N/A")
                        st.metric(
                            "Top Klacht",
                            top_klacht[:20] + "..." if len(top_klacht) > 20 else top_klacht,
                            delta=None,
                            help="Meest voorkomende klacht"
                        )
                
                st.write("")  # Spacing
                
                # Create DataFrame for visualization
                df = pd.DataFrame([
                    {
                        "Klacht": k.get("naam", "Onbekend"),
                        "Frequentie": k.get("frequentie", 0),
                        "Samenvatting": k.get("samenvatting", "")
                    }
                    for k in sorted_klachten
                ])
                
                # Interactive bar chart with Plotly
                fig = px.bar(
                    df,
                    x="Klacht",
                    y="Frequentie",
                    title="📈 Klachten Frequentie Analyse",
                    color="Frequentie",
                    color_continuous_scale="Purples",
                    text="Frequentie",
                    hover_data=["Samenvatting"]
                )
                fig.update_layout(
                    showlegend=False,
                    height=450,
                    xaxis_title="",
                    yaxis_title="Aantal keer genoemd",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(size=12)
                )
                fig.update_traces(textposition='outside', marker_line_width=0)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed complaint cards
                st.markdown("### 📋 Gedetailleerde Analyse")
                
                for idx, klacht in enumerate(sorted_klachten, 1):
                    with st.container():
                        st.markdown(f"""
                        <div class="complaint-card">
                            <h4>#{idx} {klacht.get('naam', 'Onbekend')}</h4>
                            <p><strong>Frequentie:</strong> {klacht.get('frequentie', 0)}x genoemd</p>
                            <p>{klacht.get('samenvatting', 'Geen samenvatting beschikbaar')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
            else:
                st.info("ℹ️ Geen specifieke klachten geïdentificeerd in de analyse.")
            
            st.divider()
            
            # ================================================================
            # RAG TRANSPARENCY - SOURCE SNIPPETS
            # ================================================================
            
            st.markdown("### 🔍 RAG Grondigheid: Gebruikte Bronnen")
            st.caption(
                "Deze fragmenten tonen de daadwerkelijke transcript-stukken die de AI "
                "heeft gebruikt voor de analyse. Dit bewijst dat de output 'grounded' is."
            )
            
            used_sources = result.get("used_sources_snippets", [])
            
            if used_sources:
                with st.expander(f"📚 Bekijk {len(used_sources)} bronfragmenten", expanded=False):
                    for idx, snippet in enumerate(used_sources, 1):
                        st.markdown(f"**📄 Bron {idx}**")
                        st.markdown(f"""
                        <div class="source-snippet">
                            <pre>{snippet}</pre>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Geen bronfragmenten beschikbaar")
            
        except requests.exceptions.ConnectionError:
            status.update(label="❌ Verbindingsfout", state="error", expanded=False)
            st.error("❌ **Verbindingsfout**: Kan de API niet bereiken")
            st.info("💡 **Oplossing**: Controleer of de API_ENDPOINT correct is ingesteld en de backend draait")
            with st.expander("🔧 Technische details"):
                st.code(f"API Endpoint: {API_ENDPOINT}")
            
        except requests.exceptions.Timeout:
            status.update(label="⏱️ Timeout", state="error", expanded=False)
            st.error("⏱️ **Timeout**: De API reageert niet binnen 30 seconden")
            st.info("💡 **Oplossing**: De backend kan overbelast zijn of de vraag is te complex. Probeer een kortere vraag.")
            
        except requests.exceptions.HTTPError as e:
            status.update(label=f"❌ HTTP Error {e.response.status_code}", state="error", expanded=False)
            st.error(f"❌ **HTTP Error {e.response.status_code}**")
            try:
                error_detail = e.response.json()
                with st.expander("🔧 API Response Details"):
                    st.json(error_detail)
            except:
                with st.expander("🔧 Raw Response"):
                    st.code(e.response.text)
                
        except ValueError as e:
            status.update(label="❌ Parse Error", state="error", expanded=False)
            st.error("❌ **JSON Parse Error**: Onverwacht antwoordformaat")
            st.info(f"💡 **Technisch detail**: {str(e)}")
            
        except Exception as e:
            status.update(label="❌ Onverwachte fout", state="error", expanded=False)
            st.error("❌ **Onverwachte fout**")
            with st.expander("🔧 Stack Trace"):
                st.exception(e)

elif submitted:
    st.warning("⚠️ Vul eerst een vraag in om de analyse te starten")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

st.markdown("""
<div style="text-align: center; padding: 3rem 0;">
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                padding: 2rem; 
                border-radius: 16px; 
                border: 1px solid #334155;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
        <h3 style="color: #3b82f6; margin-bottom: 1rem; font-size: 1.8rem; font-weight: 700;">
            🧠 AI Transcript Analyzer
        </h3>
        <p style="font-size: 1.2rem; margin-bottom: 1rem; color: #e2e8f0;">
            <strong style="color: #8b5cf6;">Portfolio Project</strong> | Enterprise RAG System
        </p>
        <p style="font-size: 1rem; color: #94a3b8; margin-bottom: 1.5rem; line-height: 1.6;">
            Deze applicatie demonstreert geavanceerde AI engineering skills:<br/>
            <strong style="color: #3b82f6;">Gemini 2.5 Flash</strong> | 
            <strong style="color: #3b82f6;">Vector Search</strong> | 
            <strong style="color: #3b82f6;">Serverless Deployment</strong> | 
            <strong style="color: #3b82f6;">Production-Ready Code</strong>
        </p>
        <p style="font-size: 0.9rem; color: #64748b; margin-top: 1.5rem; font-style: italic;">
            Gebouwd om mijn vaardigheden te tonen in full-stack AI development,<br/>
            van database design tot frontend UX
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
