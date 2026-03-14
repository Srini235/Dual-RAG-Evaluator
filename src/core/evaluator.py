"""
Evaluator Module - Compare baseline vs. ResonanceDB retrieval
"""

from typing import List, Dict, Optional
import numpy as np
from .doc_processor import DocumentProcessor
from .baseline_retriever import BaselineRetriever
from .resonance_client import ResonanceDBClient
from .wave_mapper import query_to_wave


class DualRAGEvaluator:
    """
    Dual RAG comparison system.
    
    Orchestrates both baseline (ChromaDB) and wave-based (ResonanceDB)
    retrieval for side-by-side comparison and evaluation.
    """
    
    def __init__(
        self,
        baseline_retriever: BaselineRetriever,
        resonance_client: ResonanceDBClient,
        embedder: DocumentProcessor
    ):
        """
        Initialize the evaluator with both retrievers.
        
        Args:
            baseline_retriever: ChromaDB-based retriever
            resonance_client: ResonanceDB HTTP client
            embedder: Document processor for embedding queries
            
        Example:
            >>> evaluator = DualRAGEvaluator(baseline, resonance, embedder)
            >>> results = evaluator.compare_retrievers("query text")
        """
        self.baseline = baseline_retriever
        self.resonance = resonance_client
        self.embedder = embedder
    
    def compare_retrievers(
        self,
        query: str,
        top_k: int = 3,
        query_text: str = None,
        print_results: bool = True
    ) -> Dict[str, List[Dict]]:
        """
        Run dual retrieval and compare results.
        
        Args:
            query: Query text to embed and search
            top_k: Number of results per retriever (default: 3)
            query_text: Optional secondary text for negation heuristic
            print_results: If True, print formatted comparison table
        
        Returns:
            Dict with keys:
            - baseline: List of results from ChromaDB
            - resonance: List of results from ResonanceDB
            - overlap: List of chunk IDs present in both top-k
            - overlap_count: Number of overlapping results
            
        Example:
            >>> result = evaluator.compare_retrievers("chronic kidney disease")
            >>> print(f"Overlap: {result['overlap_count']}/{top_k}")
        """
        # Use query for both embedding and negation heuristic if not provided
        query_text = query_text or query
        
        try:
            # Embed query
            print(f"\n[Query] Embedding: '{query}'")
            query_embedding = self.embedder.embed_chunks([query])[0]
            
            # Baseline retrieval
            print("[Retrieval] Baseline (ChromaDB)...")
            baseline_results = self.baseline.retrieve(query_embedding, top_k=top_k)
            
            # Wave-based retrieval
            print("[Retrieval] ResonanceDB (Wave-based)...")
            amplitude, phase = query_to_wave(query_embedding, query_text)
            resonance_results = self.resonance.search_wave(
                amplitude=amplitude,
                phase=phase,
                top_k=top_k
            )
            
            # Calculate overlap
            baseline_ids = {r.get("chunk_id") for r in baseline_results}
            resonance_ids = {r.get("id") for r in resonance_results}
            overlap = baseline_ids & resonance_ids
            
            # Print comparison if requested
            if print_results:
                self._print_comparison(query, baseline_results, resonance_results, overlap)
            
            return {
                "baseline": baseline_results,
                "resonance": [
                    {
                        "chunk_id": r.get("id"),
                        "text": r.get("text"),
                        "score": r.get("score")
                    }
                    for r in resonance_results
                ],
                "overlap": list(overlap),
                "overlap_count": len(overlap)
            }
        
        except Exception as e:
            print(f"ERROR: Comparison failed: {e}")
            return {
                "baseline": [],
                "resonance": [],
                "overlap": [],
                "overlap_count": 0,
                "error": str(e)
            }
    
    def batch_compare(
        self,
        queries: List[str],
        top_k: int = 3
    ) -> List[Dict]:
        """
        Run multiple queries and collect comparison results.
        
        Args:
            queries: List of query strings
            top_k: Number of results per query (default: 3)
        
        Returns:
            List of comparison result dicts
            
        Example:
            >>> queries = ["query1", "query2", "query3"]
            >>> results = evaluator.batch_compare(queries, top_k=3)
            >>> for r in results:
            ...     print(f"Query: {r['query']}, Overlap: {r['overlap_count']}")
        """
        batch_results = []
        
        for i, query in enumerate(queries, 1):
            print(f"\n{'='*80}")
            print(f"Query {i}/{len(queries)}")
            print(f"{'='*80}")
            
            result = self.compare_retrievers(query, top_k=top_k, print_results=True)
            result["query"] = query
            batch_results.append(result)
        
        return batch_results
    
    def _print_comparison(
        self,
        query: str,
        baseline_results: List[Dict],
        resonance_results: List[Dict],
        overlap: set
    ) -> None:
        """
        Pretty-print side-by-side comparison table.
        
        Args:
            query: Original query text
            baseline_results: ChromaDB results
            resonance_results: ResonanceDB results
            overlap: Set of overlapping chunk IDs
        """
        print("\n" + "=" * 120)
        print(f"QUERY: {query}")
        print("=" * 120)
        
        # Print baseline results
        print("\n[BASELINE - ChromaDB (Cosine Similarity)]")
        print("-" * 120)
        print(f"{'Rank':<6} {'Score':<8} {'Text Preview (70 chars)':<100}")
        print("-" * 120)
        
        for rank, result in enumerate(baseline_results, 1):
            text = result.get("text", "N/A")
            text_preview = text[:67] + "..." if len(text) > 70 else text
            score = result.get("score", 0)
            print(f"{rank:<6} {score:<8.4f} {text_preview:<100}")
        
        # Print ResonanceDB results
        print("\n[RESONANCEDB - Wave-Based Retrieval]")
        print("-" * 120)
        print(f"{'Rank':<6} {'Score':<8} {'Text Preview (70 chars)':<100}")
        print("-" * 120)
        
        for rank, result in enumerate(resonance_results, 1):
            text = result.get("text", "N/A")
            text_preview = text[:67] + "..." if len(text) > 70 else text
            score = result.get("score", 0)
            print(f"{rank:<6} {score:<8.4f} {text_preview:<100}")
        
        # Print overlap analysis
        print("\n" + "-" * 120)
        overlap_pct = (len(overlap) / len(baseline_results) * 100) if baseline_results else 0
        print(f"OVERLAP: {len(overlap)}/{len(baseline_results)} results ({overlap_pct:.1f}%)")
        print("=" * 120 + "\n")
    
    def compute_metrics(
        self,
        comparison_results: List[Dict]
    ) -> Dict[str, float]:
        """
        Compute aggregate metrics from multiple comparisons.
        
        Args:
            comparison_results: List of comparison result dicts
        
        Returns:
            Dict with metrics:
            - avg_overlap: Average overlap percentage
            - min_overlap: Minimum overlap percentage
            - max_overlap: Maximum overlap percentage
            - avg_baseline_score: Average baseline score
            - avg_resonance_score: Average ResonanceDB score
            
        Example:
            >>> results = evaluator.batch_compare(queries)
            >>> metrics = evaluator.compute_metrics(results)
            >>> print(f"Avg overlap: {metrics['avg_overlap']:.2%}")
        """
        if not comparison_results:
            return {
                "avg_overlap": 0.0,
                "min_overlap": 0.0,
                "max_overlap": 0.0,
                "avg_baseline_score": 0.0,
                "avg_resonance_score": 0.0
            }
        
        overlaps = []
        baseline_scores = []
        resonance_scores = []
        
        for result in comparison_results:
            if "overlap_count" in result:
                total = len(result.get("baseline", []))
                if total > 0:
                    overlap_ratio = result["overlap_count"] / total
                    overlaps.append(overlap_ratio)
            
            for r in result.get("baseline", []):
                baseline_scores.append(r.get("score", 0))
            
            for r in result.get("resonance", []):
                resonance_scores.append(r.get("score", 0))
        
        return {
            "avg_overlap": np.mean(overlaps) if overlaps else 0.0,
            "min_overlap": np.min(overlaps) if overlaps else 0.0,
            "max_overlap": np.max(overlaps) if overlaps else 0.0,
            "avg_baseline_score": np.mean(baseline_scores) if baseline_scores else 0.0,
            "avg_resonance_score": np.mean(resonance_scores) if resonance_scores else 0.0
        }
