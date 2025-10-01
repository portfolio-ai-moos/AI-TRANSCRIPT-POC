"""
Data Ingestion Script voor AI Transcript Analyzer
Embedt transcripten en uploadt naar Supabase vector database

Usage:
    1. Zorg dat .env bestand bestaat met credentials
    2. Plaats .txt bestanden in transcripts/ directory
    3. Run: python ingest_data.py
"""

import os
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client, Client
import time

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

TRANSCRIPTS_DIR = Path("transcripts")
CHUNK_SIZE = 500  # Characters per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks
BATCH_SIZE = 10  # Number of documents to process at once

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_clients():
    """Initialize Supabase and Gemini clients"""
    
    # Validate environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "GOOGLE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(
            f"Missing environment variables: {', '.join(missing_vars)}\n"
            f"Please create a .env file with these variables."
        )
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    supabase_client: Client = create_client(supabase_url, supabase_key)
    
    # Initialize Gemini embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # Initialize vector store
    vectorstore = SupabaseVectorStore(
        client=supabase_client,
        embedding=embeddings,
        table_name="transcript_vectors",
        query_name="match_documents"
    )
    
    print("✅ Clients geïnitialiseerd")
    return vectorstore, embeddings


# ============================================================================
# DATA PROCESSING
# ============================================================================

def load_transcripts(directory: Path) -> List[Dict[str, str]]:
    """Load all .txt files from transcripts directory"""
    
    if not directory.exists():
        raise FileNotFoundError(
            f"Directory '{directory}' niet gevonden.\n"
            f"Maak de directory aan en plaats .txt bestanden erin."
        )
    
    transcripts = []
    txt_files = list(directory.glob("*.txt"))
    
    if not txt_files:
        raise FileNotFoundError(
            f"Geen .txt bestanden gevonden in '{directory}'.\n"
            f"Plaats minstens één transcript bestand in deze directory."
        )
    
    print(f"\n📂 {len(txt_files)} transcript(en) gevonden")
    
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                if content:
                    transcripts.append({
                        "content": content,
                        "filename": file_path.name,
                        "source": str(file_path)
                    })
                    print(f"  ✓ {file_path.name} ({len(content)} chars)")
                else:
                    print(f"  ⚠️  {file_path.name} is leeg, overgeslagen")
                    
        except Exception as e:
            print(f"  ❌ Fout bij lezen {file_path.name}: {e}")
    
    return transcripts


def chunk_transcripts(transcripts: List[Dict[str, str]]) -> List[Dict[str, any]]:
    """Split transcripts into smaller chunks for better RAG performance"""
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    all_chunks = []
    
    print(f"\n✂️  Splitting transcripts (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    
    for transcript in transcripts:
        chunks = text_splitter.split_text(transcript["content"])
        
        for i, chunk_text in enumerate(chunks):
            all_chunks.append({
                "content": chunk_text,
                "metadata": {
                    "filename": transcript["filename"],
                    "source": transcript["source"],
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            })
        
        print(f"  ✓ {transcript['filename']}: {len(chunks)} chunks")
    
    return all_chunks


def upload_to_supabase(vectorstore: SupabaseVectorStore, chunks: List[Dict[str, any]]):
    """Upload chunks with embeddings to Supabase"""
    
    print(f"\n🚀 Uploading {len(chunks)} chunks naar Supabase...")
    print(f"   (Batch size: {BATCH_SIZE})")
    
    # Process in batches to avoid rate limits
    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for batch_idx in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[batch_idx:batch_idx + BATCH_SIZE]
        batch_num = (batch_idx // BATCH_SIZE) + 1
        
        try:
            # Extract texts and metadatas
            texts = [chunk["content"] for chunk in batch]
            metadatas = [chunk["metadata"] for chunk in batch]
            
            # Upload batch
            vectorstore.add_texts(texts=texts, metadatas=metadatas)
            
            print(f"  ✓ Batch {batch_num}/{total_batches} uploaded ({len(batch)} chunks)")
            
            # Rate limiting - be nice to Gemini API
            if batch_idx + BATCH_SIZE < len(chunks):
                time.sleep(1)
                
        except Exception as e:
            print(f"  ❌ Fout bij batch {batch_num}: {e}")
            raise
    
    print(f"\n✅ Alle {len(chunks)} chunks succesvol geüpload!")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main ingestion pipeline"""
    
    print("=" * 70)
    print("🧠 AI Transcript Analyzer - Data Ingestion Script")
    print("=" * 70)
    
    try:
        # Step 1: Initialize clients
        print("\n[1/4] Initializing clients...")
        vectorstore, embeddings = initialize_clients()
        
        # Step 2: Load transcripts
        print("\n[2/4] Loading transcripts...")
        transcripts = load_transcripts(TRANSCRIPTS_DIR)
        
        if not transcripts:
            print("\n❌ Geen transcripten gevonden. Voeg .txt bestanden toe aan transcripts/")
            return
        
        # Step 3: Chunk transcripts
        print("\n[3/4] Chunking transcripts...")
        chunks = chunk_transcripts(transcripts)
        
        # Step 4: Upload to Supabase
        print("\n[4/4] Uploading to Supabase...")
        upload_to_supabase(vectorstore, chunks)
        
        # Summary
        print("\n" + "=" * 70)
        print("🎉 DATA INGESTION VOLTOOID!")
        print("=" * 70)
        print(f"📊 Statistieken:")
        print(f"   • Transcripten verwerkt: {len(transcripts)}")
        print(f"   • Chunks aangemaakt: {len(chunks)}")
        print(f"   • Embeddings gegenereerd: {len(chunks)}")
        print(f"   • Database: Supabase (transcript_vectors)")
        print("\n✅ Je app is nu klaar om te testen!")
        print("   Run: streamlit run app.py")
        print("=" * 70)
        
    except FileNotFoundError as e:
        print(f"\n❌ Bestand/Directory fout: {e}")
        print("\n💡 Oplossing:")
        print("   1. Maak de directory 'transcripts' aan")
        print("   2. Plaats .txt bestanden met transcripten erin")
        print("   3. Run het script opnieuw")
        
    except ValueError as e:
        print(f"\n❌ Configuratie fout: {e}")
        print("\n💡 Oplossing:")
        print("   1. Maak een .env bestand aan in de project root")
        print("   2. Voeg de volgende variabelen toe:")
        print("      GOOGLE_API_KEY=your_google_api_key")
        print("      SUPABASE_URL=https://your-project.supabase.co")
        print("      SUPABASE_KEY=your_supabase_key")
        
    except Exception as e:
        print(f"\n❌ Onverwachte fout: {e}")
        print("\n💡 Check de error message hierboven voor details")
        raise


if __name__ == "__main__":
    main()
