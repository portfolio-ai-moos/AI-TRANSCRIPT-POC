"""
RAG API Serverless Function voor AI Transcript Analyzer
Gebruikt Gemini voor embeddings en chat, Supabase voor vector search
"""

import os
import json
from typing import List, Optional
from http.server import BaseHTTPRequestHandler

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
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
# LAZY INITIALIZATION - Cruciale fix voor Vercel DESCRIPTOR fout
# ============================================================================

_embeddings = None
_vectorstore = None
_llm = None
_rag_chain = None


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Lazy initialisatie van Gemini embeddings"""
    global _embeddings
    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.environ.get("GOOGLE_API_KEY")
        )
    return _embeddings


def get_vectorstore() -> SupabaseVectorStore:
    """Lazy initialisatie van Supabase vector store"""
    global _vectorstore
    if _vectorstore is None:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL en SUPABASE_KEY moeten ingesteld zijn")
        
        supabase_client: Client = create_client(supabase_url, supabase_key)
        
        _vectorstore = SupabaseVectorStore(
            client=supabase_client,
            embedding=get_embeddings(),
            table_name="transcript_vectors",
            query_name="match_documents"
        )
    return _vectorstore


def get_llm() -> ChatGoogleGenerativeAI:
    """Lazy initialisatie van Gemini chat model"""
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.environ.get("GOOGLE_API_KEY"),
            temperature=0.3
        )
    return _llm


def get_rag_chain():
    """Lazy initialisatie van de complete RAG chain"""
    global _rag_chain
    if _rag_chain is None:
        # Pydantic parser voor gestructureerde output
        parser = PydanticOutputParser(pydantic_object=AnalyseResultaat)
        
        # RAG Prompt Template
        template = """Je bent een AI-assistent die transcripten van klantenservice gesprekken analyseert.

Gebruik de volgende context om de vraag te beantwoorden:

CONTEXT:
{context}

VRAAG:
{question}

INSTRUCTIES:
1. Identificeer alle klachten in de context
2. Tel hoe vaak elke klacht voorkomt
3. Geef een beknopte samenvatting per klacht
4. Retourneer het resultaat in het gevraagde JSON formaat

{format_instructions}

ANTWOORD:"""

        prompt = ChatPromptTemplate.from_template(template)
        
        # Retriever voor vector search
        retriever = get_vectorstore().as_retriever(
            search_kwargs={"k": 5}
        )
        
        # LCEL Chain: Retrieval -> Prompt -> LLM -> Parser
        _rag_chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough(),
                "format_instructions": lambda _: parser.get_format_instructions()
            }
            | prompt
            | get_llm()
            | parser
        )
    
    return _rag_chain


def format_docs(docs) -> str:
    """Formatteer retrieved documents naar string"""
    return "\n\n".join([doc.page_content for doc in docs])


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
            
            # Voer RAG chain uit
            rag_chain = get_rag_chain()
            result: AnalyseResultaat = rag_chain.invoke(question)
            
            # Haal ook de gebruikte bronnen op voor transparantie
            retriever = get_vectorstore().as_retriever(search_kwargs={"k": 5})
            source_docs = retriever.invoke(question)
            used_sources = [doc.page_content[:200] + "..." for doc in source_docs]
            
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
