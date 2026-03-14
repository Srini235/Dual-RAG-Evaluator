"""
Main Entry Point - Dual RAG Comparison: ChromaDB vs. ResonanceDB

Run with:
    python main.py [--pdf path/to/file.pdf] [--use-samples]

Examples:
    python main.py --use-samples
        Use hardcoded sample chunks (no file I/O)
    
    python main.py --pdf sample_documents.txt
        Load text from file and process
"""

import sys
import argparse
from pathlib import Path

from doc_processor import DocumentProcessor
from baseline_retriever import BaselineRetriever
from resonance_client import ResonanceDBClient, MockResonanceDBClient
from evaluator import DualRAGEvaluator
from wave_mapper import vector_to_wave


def setup_logger():
    """Configure basic logging."""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main():
    """End-to-end Dual RAG comparison."""
    
    print("""
========================================================================
           Dual RAG Comparison: Vector DB vs. ResonanceDB
                                                                   
  Comparing:                                                                  
  - BASELINE: ChromaDB with cosine similarity (vector search)
  - RESONANCEDB: Wave-based semantic retrieval (phase-coherent matching)
========================================================================
    """)
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Dual RAG Comparison",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--pdf",
        type=str,
        default=None,
        help="Path to PDF or text file to load (default: use sample chunks)"
    )
    parser.add_argument(
        "--use-samples",
        action="store_true",
        help="Use hardcoded sample chunks (ignores --pdf)"
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Single query to run (skips interactive mode)"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of results per retriever (default: 3)"
    )
    
    args = parser.parse_args()
    
    # ================================================================
    # PHASE 1: Initialize Components
    # ================================================================
    print("\n[PHASE 1] Initializing Components")
    print("-" * 80)
    
    try:
        embedder = DocumentProcessor()
    except Exception as e:
        print(f"FATAL: Failed to load embedding model: {e}")
        return 1
    
    # ================================================================
    # PHASE 2: Load Documents
    # ================================================================
    print("\n[PHASE 2] Loading Documents")
    print("-" * 80)
    
    if args.use_samples:
        print("Using hardcoded sample chunks...")
        chunks = embedder.get_sample_chunks()
        print(f"[OK] Loaded {len(chunks)} sample chunks")
    
    elif args.pdf:
        print(f"Loading from: {args.pdf}")
        try:
            if args.pdf.endswith('.pdf'):
                text = embedder.load_from_pdf(args.pdf)
            else:
                text = embedder.load_from_text_file(args.pdf)
            
            chunks, embeddings = embedder.process_text(text)
        except FileNotFoundError:
            print(f"ERROR: File not found: {args.pdf}")
            return 1
        except Exception as e:
            print(f"ERROR: Failed to load document: {e}")
            return 1
    
    else:
        # Try to load sample_documents.txt if it exists
        if Path("sample_documents.txt").exists():
            print("Loading from sample_documents.txt...")
            try:
                text = embedder.load_from_text_file("sample_documents.txt")
                chunks, embeddings = embedder.process_text(text)
            except Exception as e:
                print(f"WARNING: Failed to load sample_documents.txt: {e}")
                print("Falling back to hardcoded samples...")
                chunks = embedder.get_sample_chunks()
        else:
            print("Using hardcoded sample chunks (sample_documents.txt not found)...")
            chunks = embedder.get_sample_chunks()
    
    # If we only have chunks (sample mode), generate embeddings
    if 'embeddings' not in locals():
        print("\n[PHASE 2b] Generating Embeddings")
        print("-" * 80)
        embeddings = embedder.embed_chunks(chunks)
    
    print(f"\n[OK] Total chunks: {len(chunks)}")
    print(f"[OK] Embedding shape: {embeddings.shape}")
    
    # ================================================================
    # PHASE 3: Initialize Retrievers
    # ================================================================
    print("\n[PHASE 3] Initializing Retrievers")
    print("-" * 80)
    
    # Initialize baseline (ChromaDB)
    try:
        baseline = BaselineRetriever(embeddings=embeddings, texts=chunks)
    except Exception as e:
        print(f"ERROR: Failed to initialize ChromaDB: {e}")
        return 1
    
    # Initialize ResonanceDB client
    try:
        resonance = ResonanceDBClient()
        if not resonance.health_check():
            print("\nWARNING: ResonanceDB server not responding.")
            print("Using mock client for demonstration...")
            resonance = MockResonanceDBClient()
    except Exception as e:
        print(f"\nWARNING: Cannot connect to ResonanceDB: {e}")
        print("Using mock client for demonstration...")
        resonance = MockResonanceDBClient()
    
    # ================================================================
    # PHASE 4: Pre-populate ResonanceDB
    # ================================================================
    print("\n[PHASE 4] Pre-populating ResonanceDB")
    print("-" * 80)
    
    try:
        # Clear previous data if any
        resonance.clear_store()
        
        # Insert chunks into ResonanceDB
        inserted = 0
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            amplitude, phase = vector_to_wave(embedding, chunk)
            success = resonance.insert_record(
                chunk_id=f"chunk_{i:04d}",
                text=chunk,
                amplitude=amplitude,
                phase=phase
            )
            if success:
                inserted += 1
        
        print(f"[OK] Inserted {inserted}/{len(chunks)} records into ResonanceDB")
    except Exception as e:
        print(f"ERROR: Failed to populate ResonanceDB: {e}")
        return 1
    
    # ================================================================
    # PHASE 5: Initialize Evaluator
    # ================================================================
    print("\n[PHASE 5] Initializing Evaluator")
    print("-" * 80)
    
    try:
        evaluator = DualRAGEvaluator(baseline, resonance, embedder)
        print("[OK] Evaluator ready")
    except Exception as e:
        print(f"ERROR: Failed to initialize evaluator: {e}")
        return 1
    
    # ================================================================
    # PHASE 6: Run Retrieval Comparison
    # ================================================================
    print("\n[PHASE 6] Running Retrieval Comparison")
    print("-" * 80)
    
    if args.query:
        # Single query mode
        print(f"\nRunning single query: '{args.query}'")
        evaluator.compare_retrievers(args.query, top_k=args.top_k)
    
    else:
        # Interactive/batch mode
        sample_queries = [
            "What is chronic kidney disease?",
            "How does hypertension affect the kidneys?",
            "What is diabetic nephropathy?",
            "Tell me about proteinuria",
            "What are the stages of CKD?",
        ]
        
        print("\n" + "=" * 80)
        print("SAMPLE QUERIES")
        print("=" * 80)
        
        results = evaluator.batch_compare(sample_queries, top_k=args.top_k)
        
        # Print aggregate metrics
        print("\n" + "=" * 80)
        print("AGGREGATE METRICS")
        print("=" * 80)
        
        metrics = evaluator.compute_metrics(results)
        
        print(f"\nOverlap Analysis:")
        print(f"  Average overlap:  {metrics['avg_overlap']:.1%}")
        print(f"  Min overlap:      {metrics['min_overlap']:.1%}")
        print(f"  Max overlap:      {metrics['max_overlap']:.1%}")
        
        print(f"\nScore Analysis:")
        print(f"  Avg baseline score:    {metrics['avg_baseline_score']:.4f}")
        print(f"  Avg resoance score:    {metrics['avg_resonance_score']:.4f}")
        
        # Interactive query loop
        print("\n" + "=" * 80)
        print("INTERACTIVE MODE")
        print("=" * 80)
        print("\nEnter custom queries (or 'quit' to exit):")
        
        while True:
            try:
                query = input("\nQuery> ").strip()
                if not query or query.lower() == 'quit':
                    break
                
                evaluator.compare_retrievers(query, top_k=args.top_k)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    # ================================================================
    # Cleanup
    # ================================================================
    print("\n[Cleanup] Closing connections...")
    resonance.close()
    print("[OK] Done")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
