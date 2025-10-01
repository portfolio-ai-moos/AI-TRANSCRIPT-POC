# 🧠 AI Transcript Analyzer

**Portfolio Project**: Production-ready RAG (Retrieval-Augmented Generation) system voor transcript analyse

[![Tech Stack](https://img.shields.io/badge/Gemini-AI-blue)](https://ai.google.dev/)
[![LangChain](https://img.shields.io/badge/LangChain-LCEL-green)](https://langchain.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Vector_DB-orange)](https://supabase.com/)
[![Vercel](https://img.shields.io/badge/Vercel-Serverless-black)](https://vercel.com/)

---

## 📋 Project Overzicht

Dit project demonstreert een **end-to-end AI-systeem** dat:
- 🔍 **Vector similarity search** uitvoert op transcript data
- 🤖 **Gemini AI** gebruikt voor embeddings en analyse
- 📊 **Gestructureerde output** genereert via Pydantic schemas
- 🌐 **Serverless deployment** op Vercel met stabiliteitsfixes
- 💾 **Supabase + pgvector** voor schaalbare vector storage

---

## 🏗️ Architectuur

```
┌─────────────────┐
│  Streamlit UI   │  ← Portfolio-grade frontend
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vercel API     │  ← Serverless Python function
│  /api/analyze   │     (Lazy initialization fix)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│ Gemini │ │   Supabase   │
│   AI   │ │  + pgvector  │
└────────┘ └──────────────┘
```

### Tech Stack Details

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Gemini 1.5 Flash | Klachten analyse & structured output |
| **Embeddings** | Gemini embedding-001 | Vector representations (1536 dim) |
| **Vector DB** | Supabase + pgvector | Similarity search met IVFFlat index |
| **Framework** | LangChain LCEL | RAG pipeline orchestration |
| **Backend** | Vercel Serverless | Python 3.9 HTTP handler |
| **Frontend** | Streamlit | Interactive dashboard |
| **Validation** | Pydantic 2.6 | Schema-validated JSON output |

---

## 🚀 Deployment Instructies

### 1️⃣ Vercel Backend Deployment

#### A. Push naar GitHub
```bash
git add .
git commit -m "Complete AI Transcript Analyzer"
git push origin main
```

#### B. Vercel Project Setup
1. Ga naar [vercel.com](https://vercel.com) en importeer je repository
2. Vercel detecteert automatisch de `vercel.json` configuratie

#### C. Environment Variables Instellen
In Vercel Dashboard → Settings → Environment Variables:

```bash
GOOGLE_API_KEY=your_google_ai_studio_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_key
```

**Waar vind je deze keys?**
- **GOOGLE_API_KEY**: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **SUPABASE_URL & KEY**: Supabase Dashboard → Project Settings → API

#### D. Deploy & Test
```bash
# Vercel deployment URL (voorbeeld)
https://your-project.vercel.app/api/analyze
```

Test de API:
```bash
curl -X POST https://your-project.vercel.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"question": "Wat zijn de meest voorkomende klachten?"}'
```

---

### 2️⃣ Streamlit Frontend Deployment

#### Optie A: Streamlit Cloud (Aanbevolen voor Portfolio)

1. **Push naar GitHub** (als nog niet gedaan)
2. Ga naar [share.streamlit.io](https://share.streamlit.io)
3. Klik "New app" en selecteer je repository
4. **Main file path**: `app.py`
5. **Advanced settings** → Secrets:

```toml
API_ENDPOINT = "https://your-project.vercel.app/api/analyze"
```

6. Deploy! 🚀

#### Optie B: Lokaal Testen

```bash
# Installeer dependencies
pip install -r requirements.txt

# Maak .streamlit/secrets.toml
mkdir -p .streamlit
echo 'API_ENDPOINT = "https://your-project.vercel.app/api/analyze"' > .streamlit/secrets.toml

# Run Streamlit
streamlit run app.py
```

---

## 📊 Data Seeding (Optioneel)

Om de app te testen met echte data, voeg transcript vectors toe aan Supabase:

```python
# seed_data.py (voorbeeld)
from supabase import create_client
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Voorbeeld transcript
transcript = "Klant belt over late levering. Product kwam 3 dagen te laat aan."
embedding = embeddings.embed_query(transcript)

supabase.table("transcript_vectors").insert({
    "content": transcript,
    "embedding": embedding,
    "metadata": {"datum": "2025-10-01", "type": "klacht"}
}).execute()
```

---

## 🎯 Portfolio Highlights

### Wat maakt dit project indrukwekkend?

✅ **Production-Ready Architecture**
- Lazy initialization pattern voor Vercel cold starts
- Proper error handling met typed exceptions
- CORS configuratie voor cross-origin requests

✅ **Modern AI Stack**
- LangChain LCEL (Expression Language) voor composable chains
- Pydantic voor runtime type validation
- Structured output via PydanticOutputParser

✅ **Schaalbare Database**
- pgvector extension voor vector similarity
- IVFFlat index voor performance
- JSONB metadata filtering

✅ **Professional Frontend**
- Custom CSS styling met gradient themes
- Plotly interactive visualizations
- RAG transparency met source snippets

✅ **DevOps Best Practices**
- Version-pinned dependencies
- Environment variable management
- Serverless deployment met auto-scaling

---

## 🐛 Troubleshooting

### "DESCRIPTOR fout" op Vercel
✅ **Opgelost** via lazy initialization pattern in `api/analyze.py`

### API timeout errors
- Check Supabase project status (moet ACTIVE_HEALTHY zijn)
- Verifieer GOOGLE_API_KEY quota limits
- Verhoog timeout in `app.py` (huidige: 30s)

### Geen resultaten in frontend
- Controleer of `transcript_vectors` tabel data bevat
- Test API endpoint direct met curl
- Check browser console voor CORS errors

---

## 📝 Licentie & Contact

**Project Type**: Portfolio / Proof of Concept  
**Author**: [Jouw Naam]  
**LinkedIn**: [Jouw LinkedIn]  
**GitHub**: [Jouw GitHub]

---

## 🙏 Acknowledgments

- **Gemini AI** voor state-of-the-art embeddings en chat
- **LangChain** voor de RAG framework
- **Supabase** voor managed Postgres + pgvector
- **Vercel** voor serverless deployment platform

---

**⭐ Als dit project je helpt, geef het een ster op GitHub!**
