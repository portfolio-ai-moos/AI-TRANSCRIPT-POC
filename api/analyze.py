"""
RAG API Serverless Function voor AI Transcript Analyzer
Gebruikt Gemini voor embeddings en chat, Supabase voor vector search
Lightweight version zonder langchain voor Vercel size limits
"""

import os
import json
from typing import List, Optional, Dict, Any
from http.server import BaseHTTPRequestHandler

from pydantic import BaseModel, Field
import google.generativeai as genai
from supabase import create_client, Client


# ============================================================================
# PYDANTIC SCHEMAS - Gestructureerde JSON Output
# ============================================================================

class Klacht(BaseModel):
    """Een individuele klacht uit het transcript"""
    naam: str = Field(description="Korte naam van de klacht")
    frequentie: int = Field(description="Hoe vaak deze klacht voorkomt")
    samenvatting: str = Field(description="Beknopte uitleg van de klacht")


class AnalyseResultaat(BaseModel):
    """Het complete analyse resultaat"""
    klachten: List[Klacht] = Field(description="Lijst van geïdentificeerde klachten")


# ============================================================================
# LAZY INITIALIZATION - Lightweight without langchain
# ============================================================================

_supabase_client = None
_genai_configured = False


def get_supabase_client() -> Client:
    """Lazy initialisatie van Supabase client"""
    global _supabase_client
    if _supabase_client is None:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL en SUPABASE_KEY moeten ingesteld zijn")
        
        _supabase_client = create_client(supabase_url, supabase_key)
    return _supabase_client


def configure_genai():
    """Configure Google AI"""
    global _genai_configured
    if not _genai_configured:
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY moet ingesteld zijn")
        genai.configure(api_key=google_api_key)
        _genai_configured = True


def get_embedding(text: str) -> List[float]:
    """Generate embedding for text using Gemini"""
    configure_genai()
    result = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_query"
    )
    return result['embedding']


def vector_search(question: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Perform vector similarity search in Supabase"""
    client = get_supabase_client()
    
    # Generate embedding for question
    query_embedding = get_embedding(question)
    
    # Call Supabase RPC function for vector search
    response = client.rpc(
        'match_documents',
        {
            'query_embedding': query_embedding,
            'match_count': top_k
        }
    ).execute()
    
    return response.data if response.data else []


def generate_analysis(question: str, context_docs: List[Dict[str, Any]]) -> AnalyseResultaat:
    """Generate structured analysis using Gemini"""
    configure_genai()
    
    # Format context
    context = "\n\n".join([doc.get('content', '') for doc in context_docs])
    
    # Build prompt
    prompt = f"""Je bent een AI-assistent die transcripten van klantenservice gesprekken analyseert.

Gebruik de volgende context om de vraag te beantwoorden:

CONTEXT:
{context}

VRAAG:
{question}

INSTRUCTIES:
1. Identificeer alle klachten in de context
2. Tel hoe vaak elke klacht voorkomt
3. Geef een beknopte samenvatting per klacht
4. Retourneer het resultaat als JSON object met deze structuur:
{{
  "klachten": [
    {{
      "naam": "Naam van klacht",
      "frequentie": aantal_keer_voorkomend,
      "samenvatting": "Korte uitleg"
    }}
  ]
}}

ANTWOORD (alleen JSON, geen extra tekst):"""
    
    # Generate response with Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    # Parse JSON from response
    response_text = response.text.strip()
    
    # Remove markdown code blocks if present
    if response_text.startswith('```'):
        response_text = response_text.split('```')[1]
        if response_text.startswith('json'):
            response_text = response_text[4:]
        response_text = response_text.strip()
    
    # Parse to Pydantic model
    result_dict = json.loads(response_text)
    return AnalyseResultaat(**result_dict)


# ============================================================================
# VERCEL SERVERLESS HANDLER
# ============================================================================

class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Function Handler"""
    
    def do_POST(self):
        """Handle POST requests naar /api/analyze"""
        try:
            # Parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            question = data.get("question", "")
            
            if not question:
                self.send_error(400, "Vraag is verplicht")
                return
            
            # Perform vector search
            source_docs = vector_search(question, top_k=5)
            
            # Generate analysis with Gemini
            result: AnalyseResultaat = generate_analysis(question, source_docs)
            
            # Extract snippets for transparency
            used_sources = [doc.get('content', '')[:200] + "..." for doc in source_docs]
            
            # Bouw response
            response_data = {
                "question": question,
                "analysis": result.dict(),
                "used_sources_snippets": used_sources
            }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                "error": str(e),
                "type": type(e).__name__
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
