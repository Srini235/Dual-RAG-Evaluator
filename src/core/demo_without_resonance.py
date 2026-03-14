"""
Demo Script - Dual RAG Comparison with Mocked ResonanceDB

This demonstrates the full end-to-end system without needing the actual
ResonanceDB Docker container running.

Run with:
    python demo_without_resonance.py
"""

import sys
import numpy as np
from unittest.mock import Mock
from doc_processor import DocumentProcessor
from baseline_retriever import BaselineRetriever
from resonance_client import ResonanceDBClient
from evaluator import DualRAGEvaluator


def create_mock_resonance_client():
    """Create a mock ResonanceDB client with realistic responses."""
    mock_client = Mock(spec=ResonanceDBClient)
    mock_client.health_check = Mock(return_value=True)
    
    # Mock search results - return relevant medical text
    mock_results = [
        {
            "id": "chunk_0000",
            "text": "Chronic Kidney Disease (CKD) is a condition characterized by gradual loss of kidney function.",
            "score": 0.94
        },
        {
            "id": "chunk_0004",
            "text": "CKD is classified into five stages based on estimated glomerular filtration rate (eGFR).",
            "score": 0.87
        },
        {
            "id": "chunk_0002",
            "text": "Proteinuria or albuminuria is a key marker of kidney damage.",
            "score": 0.73
        }
    ]
    
    mock_client.search_wave = Mock(return_value=mock_results)
    mock_client.insert_record = Mock(return_value=True)
    mock_client.clear_store = Mock(return_value=True)
    mock_client.close = Mock()
    
    return mock_client


def main():
    """Run demo with all components including mocked ResonanceDB."""
    
    print("\n" + "="*90)
    print("DEMO: Dual RAG Comparison (ChromaDB vs. Mocked ResonanceDB)")
    print("="*90)
    
    # ================================================================
    # Step 1: Initialize Components
    # ================================================================
    print("\n[PHASE 1] Initializing Components")
    print("-" * 90)
    
    try:
        embedder = DocumentProcessor()
    except Exception as e:
        print(f"FATAL: Failed to load embedding model: {e}")
        return 1
    
    # ================================================================
    # Step 2: Load Sample Data
    # ================================================================
    print("\n[PHASE 2] Loading Sample Data")
    print("-" * 90)
    
    chunks = embedder.get_sample_chunks()
    print(f"[OK] Loaded {len(chunks)} sample chunks")
    
    print("\nSample Chunks:")
    for i, chunk in enumerate(chunks, 1):
        preview = chunk[:70] + "..." if len(chunk) > 70 else chunk
        print(f"  {i}. {preview}")
    
    # ================================================================
    # Step 3: Generate Embeddings
    # ================================================================
    print("\n[PHASE 3] Generating Embeddings")
    print("-" * 90)
    
    embeddings = embedder.embed_chunks(chunks)
    print(f"[OK] Generated embeddings for {len(chunks)} chunks")
    print(f"  Shape: {embeddings.shape}")
    print(f"  Dtype: {embeddings.dtype}")
    
    # ================================================================
    # Step 4: Initialize Retrievers
    # ================================================================
    print("\n[PHASE 4] Initializing Retrievers")
    print("-" * 90)
    
    # Baseline (ChromaDB)
    baseline = BaselineRetriever(embeddings=embeddings, texts=chunks)
    print(f"[OK] ChromaDB initialized with {baseline.get_collection_count()} chunks")
    
    # Mock ResonanceDB
    resonance = create_mock_resonance_client()
    print("[OK] ResonanceDB client initialized (MOCKED)")
    
    # ================================================================
    # Step 5: Initialize Evaluator
    # ================================================================
    print("\n[PHASE 5] Initializing Evaluator")
    print("-" * 90)
    
    evaluator = DualRAGEvaluator(baseline, resonance, embedder)
    print("[OK] Evaluator ready")
    
    # ================================================================
    # Step 6: Run Comparisons
    # ================================================================
    print("\n[PHASE 6] Running Retrieval Comparisons")
    print("="*90)
    
    test_queries = [
        "What is chronic kidney disease?",
        "How does hypertension affect kidneys?",
        "What is proteinuria?",
    ]
    
    all_results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*90}")
        print(f"QUERY {i}/3: {query}")
        print(f"{'='*90}")
        
        result = evaluator.compare_retrievers(query, top_k=3, print_results=True)
        result["query"] = query
        all_results.append(result)
    
    # ================================================================
    # Step 7: Compute Metrics
    # ================================================================
    print("\n" + "="*90)
    print("AGGREGATE METRICS (All 3 Queries)")
    print("="*90)
    
    metrics = evaluator.compute_metrics(all_results)
    
    print(f"\nOverlap Analysis:")
    print(f"  Average overlap:  {metrics['avg_overlap']:.1%}")
    print(f"  Min overlap:      {metrics['min_overlap']:.1%}")
    print(f"  Max overlap:      {metrics['max_overlap']:.1%}")
    
    print(f"\nScore Analysis:")
    print(f"  Avg baseline score:    {metrics['avg_baseline_score']:.4f}")
    print(f"  Avg resonance score:   {metrics['avg_resonance_score']:.4f}")
    
    # ================================================================
    # Step 8: Individual Query Analysis
    # ================================================================
    print("\n" + "="*90)
    print("DETAILED RESULTS BY QUERY")
    print("="*90)
    
    for i, result in enumerate(all_results, 1):
        query = result["query"]
        overlap = result["overlap_count"]
        print(f"\nQuery {i}: {query}")
        print(f"  Overlap: {overlap}/3 results ({overlap/3*100:.0f}%)")
        print(f"  Baseline top score: {result['baseline'][0]['score']:.4f}")
        print(f"  ResonanceDB top score: {result['resonance'][0]['score']:.4f}")
    
    # ================================================================
    # Summary
    # ================================================================
    print("\n" + "="*90)
    print("SUMMARY")
    print("="*90)
    
    print(f"""
[OK] System Components:
  - Document Processor: WORKING (384-dim embeddings)
  - ChromaDB Baseline: WORKING (cosine similarity)
  - ResonanceDB Client: READY (mocked for this demo)
  - Evaluator: WORKING (dual comparison)

[OK] Test Results:
  - Total queries: {len(test_queries)}
  - Average overlap: {metrics['avg_overlap']:.1%}
  - Baseline avg score: {metrics['avg_baseline_score']:.4f}
  - ResonanceDB avg score: {metrics['avg_resonance_score']:.4f}

Next Steps:"
  1. Start ResonanceDB Docker container:
     cd ..\ResonanceDB && docker build -t resonance-db . && docker run -p 8080:8080 resonance-db
  
  2. Run the full system:
     python main.py --use-samples
  
  3. Run actual tests:
     python -m pytest test_dual_rag.py -v

Documentation Files:
  - IMPLEMENTATION_PLAN.md: Architecture and module breakdown
  - API_REFERENCE.md: ResonanceDB REST API specification
  - CODE_PATTERNS.md: Reusable code patterns for Copilot
  - API_INTEGRATION_DEBUG.md: Debugging and troubleshooting guide
  - .copilot-instructions.md: VS Code Copilot configuration
""")
    
    print("="*90 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
