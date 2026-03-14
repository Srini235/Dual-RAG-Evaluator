# Code Patterns & Examples for Copilot

This document provides concrete code patterns and examples that Copilot can reference when generating code.

---

## Pattern 1: ResonanceDB Client Basic Usage

### ✅ DO: Simple, typed, error-aware

```python
from resonance_client import ResonanceDBClient
import numpy as np

# Initialize client
client = ResonanceDBClient(base_url="http://localhost:8080")

# Check if server is running
try:
    if not client.health_check():
        print("ResonanceDB server is not available")
        exit(1)
except ConnectionError as e:
    print(f"Failed to connect: {e}")
    exit(1)

# Insert a record
amplitude = np.array([0.1, 0.45, 0.67, ...]).tolist()  # Convert to list
phase = np.array([-3.14, 1.57, 0.5, ...]).tolist()

success = client.insert_record(
    chunk_id="chunk_001",
    text="Sample medical text",
    amplitude=amplitude,
    phase=phase
)

if success:
    print("Record inserted successfully")
else:
    print("Failed to insert record")

# Search the database
query_amplitude = np.array([0.12, 0.48, ...]).tolist()
query_phase = np.array([-3.0, 1.2, ...]).tolist()

results = client.search_wave(
    amplitude=query_amplitude,
    phase=query_phase,
    top_k=3
)

for rank, result in enumerate(results, 1):
    print(f"{rank}. {result['text'][:50]}... (score: {result['score']:.3f})")
```

---

## Pattern 2: Vector-to-Wave Conversion

### ✅ DO: Vectorized numpy, handle negations

```python
import numpy as np
import math

NEGATION_WORDS = {"not", "never", "unless", "contraindicated", "no", "none", "without"}

def vector_to_wave(vector: np.ndarray, text: str) -> tuple[list[float], list[float]]:
    """
    Convert a base embedding vector to amplitude and phase.
    
    Args:
        vector: 1D numpy array of floats (e.g., shape (384,))
        text: Associated text (used for negation heuristic)
    
    Returns:
        (amplitude_list, phase_list) both as lists of floats
    """
    # Amplitude: normalized absolute values
    amplitude = np.abs(vector)
    amplitude = amplitude / (np.max(amplitude) + 1e-8)  # Normalize to [0, 1]
    
    # Phase: random in [-π, π]
    phase = np.random.uniform(-math.pi, math.pi, size=vector.shape[0])
    
    # Heuristic: detect negation in text
    text_lower = text.lower()
    if any(word in text_lower for word in NEGATION_WORDS):
        # Shift phase by π (destructive interference)
        phase = (phase + math.pi) % (2 * math.pi)
        # Map back to [-π, π]
        phase = np.where(phase > math.pi, phase - 2 * math.pi, phase)
    
    return amplitude.tolist(), phase.tolist()


def query_to_wave(embedding: np.ndarray, query_text: str) -> tuple[list[float], list[float]]:
    """Same logic as vector_to_wave for query embeddings."""
    return vector_to_wave(embedding, query_text)
```

---

## Pattern 3: ChromaDB Baseline Retriever

### ✅ DO: Clean class-based design

```python
from typing import List, Dict
import chromadb
import numpy as np

class BaselineRetriever:
    """In-memory ChromaDB store with cosine similarity."""
    
    def __init__(self, embeddings: np.ndarray = None, texts: List[str] = None):
        """
        Initialize ChromaDB client.
        
        Args:
            embeddings: Optional (N, embedding_dim) array
            texts: Optional list of N text chunks
        """
        self.client = chromadb.EphemeralClient()
        self.collection = self.client.create_collection(
            name="baseline_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        
        if embeddings is not None and texts is not None:
            self.insert(embeddings, texts)
    
    def insert(self, embeddings: np.ndarray, texts: List[str]) -> None:
        """
        Store embeddings and text chunks.
        
        Args:
            embeddings: (N, embedding_dim) array of float32
            texts: List of N strings
        """
        ids = [f"chunk_{i:04d}" for i in range(len(texts))]
        
        # ChromaDB expects embeddings as nested lists
        embedding_lists = embeddings.tolist()
        
        self.collection.add(
            ids=ids,
            embeddings=embedding_lists,
            metadatas=[{"text": text} for text in texts],
            documents=texts  # Store full text for retrieval
        )
        print(f"Inserted {len(texts)} chunks into ChromaDB")
    
    def retrieve(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top_k similar chunks using cosine similarity.
        
        Args:
            query_embedding: 1D array (embedding_dim,)
            top_k: Number of results
        
        Returns:
            List of dicts: [{"chunk_id": str, "text": str, "score": float}, ...]
        """
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        # Flatten results (ChromaDB returns nested lists)
        output = []
        for idx, (chunk_id, distance, metadata) in enumerate(zip(
            results["ids"][0],
            results["distances"][0],
            results["metadatas"][0]
        )):
            # ChromaDB's cosine returns distances, which are 1 - similarity
            # For compatibility, we convert to similarity score [0, 1]
            score = 1.0 - distance
            output.append({
                "chunk_id": chunk_id,
                "text": results["documents"][0][idx],
                "score": float(score)
            })
        
        return output
```

---

## Pattern 4: Document Processing (Simple Version)

### ✅ DO: Start with hardcoded chunks, then scale to PDF

```python
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

class DocumentProcessor:
    """Load, chunk, and embed documents."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize embedding model."""
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 500, 
        overlap: int = 50
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Full document text
            chunk_size: Target chunk size in chars
            overlap: Overlap between chunks in chars
        
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - overlap
            
            # Avoid infinite loop on very small text
            if end == len(text):
                break
        
        return chunks
    
    def embed_chunks(self, chunks: List[str]) -> np.ndarray:
        """
        Generate embeddings for text chunks.
        
        Args:
            chunks: List of text strings
        
        Returns:
            (N, embedding_dim) numpy array of float32
        """
        embeddings = self.model.encode(chunks, convert_to_numpy=True)
        return embeddings.astype(np.float32)
    
    @staticmethod
    def load_sample_chunks() -> List[str]:
        """Return hardcoded sample chunks for quick testing."""
        return [
            "Chronic Kidney Disease (CKD) is a condition characterized by gradual loss of kidney function. The kidneys filter waste and excess water from the blood to form urine.",
            "CKD is classified into five stages based on estimated glomerular filtration rate (eGFR). Stage 1: eGFR ≥ 90 mL/min/1.73m². Stage 2: eGFR 60-89 mL/min/1.73m².",
            "Hypertension is the most common cause of CKD and accounts for about 30% of cases. Blood pressure control is essential in slowing the progression of kidney disease.",
            "Proteinuria or albuminuria is the presence of protein in the urine and is a key marker of kidney damage. It indicates glomerular injury and is associated with faster CKD progression.",
            "Diabetes is the leading cause of kidney disease, accounting for approximately 35-40% of CKD cases. Diabetic nephropathy develops in about 20-40% of patients with diabetes.",
            "ACE inhibitors and ARBs are first-line medications for CKD patients, especially those with hypertension or diabetes, as they provide renal protection beyond blood pressure reduction.",
        ]
```

---

## Pattern 5: Dual RAG Evaluator

### ✅ DO: Side-by-side comparison with clear output

```python
from typing import Dict, List
from document_processor import DocumentProcessor
from baseline_retriever import BaselineRetriever
from resonance_client import ResonanceDBClient
from wave_mapper import vector_to_wave, query_to_wave
import numpy as np

class DualRAGEvaluator:
    """Compare baseline vector DB vs. ResonanceDB retrieval."""
    
    def __init__(
        self,
        baseline_retriever: BaselineRetriever,
        resonance_client: ResonanceDBClient,
        embedder: DocumentProcessor
    ):
        self.baseline = baseline_retriever
        self.resonance = resonance_client
        self.embedder = embedder
    
    def compare_retrievers(
        self,
        query: str,
        top_k: int = 3,
        query_text: str = None
    ) -> Dict[str, List[Dict]]:
        """
        Run dual retrieval and return side-by-side results.
        
        Args:
            query: Query text
            top_k: Number of results per retriever
            query_text: Optional secondary text for negation heuristic
        
        Returns:
            Dict with "baseline" and "resonance" result lists
        """
        query_text = query_text or query
        
        # Embed query
        query_embedding = self.embedder.embed_chunks([query])[0]
        
        # Baseline retrieval
        baseline_results = self.baseline.retrieve(query_embedding, top_k=top_k)
        
        # Wave-based retrieval
        amplitude, phase = query_to_wave(query_embedding, query_text)
        resonance_results = self.resonance.search_wave(
            amplitude=amplitude,
            phase=phase,
            top_k=top_k
        )
        
        # Print comparison
        self._print_comparison(query, baseline_results, resonance_results)
        
        return {
            "baseline": baseline_results,
            "resonance": resonance_results
        }
    
    def _print_comparison(
        self,
        query: str,
        baseline_results: List[Dict],
        resonance_results: List[Dict]
    ) -> None:
        """Pretty-print side-by-side results."""
        print("\n" + "=" * 100)
        print(f"Query: {query}")
        print("=" * 100)
        
        # Baseline results
        print("\n[BASELINE - Cosine Similarity]")
        print("-" * 100)
        for rank, result in enumerate(baseline_results, 1):
            text_preview = result["text"][:70] + "..." if len(result["text"]) > 70 else result["text"]
            print(f"{rank}. Score: {result['score']:.4f} | {text_preview}")
        
        # ResonanceDB results
        print("\n[RESONANCEDB - Wave-Based]")
        print("-" * 100)
        for rank, result in enumerate(resonance_results, 1):
            text_preview = result["text"][:70] + "..." if len(result["text"]) > 70 else result["text"]
            print(f"{rank}. Score: {result['score']:.4f} | {text_preview}")
        
        # Overlap analysis
        baseline_ids = {r["chunk_id"] for r in baseline_results}
        resonance_ids = {r["chunk_id"] for r in resonance_results}
        overlap = baseline_ids & resonance_ids
        print(f"\nOverlap in Top-{len(baseline_results)}: {len(overlap)}/{len(baseline_results)}")
        print("=" * 100 + "\n")
```

---

## Pattern 6: Main Entry Point (Integration)

### ✅ DO: Clear orchestration of all components

```python
from document_processor import DocumentProcessor
from baseline_retriever import BaselineRetriever
from resonance_client import ResonanceDBClient
from evaluator import DualRAGEvaluator
import sys

def main():
    """End-to-end dual RAG comparison."""
    
    print("=== Dual RAG Comparison: ChromaDB vs. ResonanceDB ===\n")
    
    # 1. Initialize components
    print("[1/5] Initializing embedding model...")
    embedder = DocumentProcessor(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print(f"     Embedding dimension: {embedder.embedding_dim}")
    
    # 2. Load sample documents
    print("\n[2/5] Loading sample documents...")
    chunks = embedder.load_sample_chunks()
    print(f"     Loaded {len(chunks)} chunks")
    
    # 3. Generate embeddings
    print("\n[3/5] Generating embeddings...")
    embeddings = embedder.embed_chunks(chunks)
    print(f"     Shape: {embeddings.shape}")
    
    # 4. Initialize baseline (ChromaDB)
    print("\n[4/5] Initializing baseline retriever (ChromaDB)...")
    baseline = BaselineRetriever(embeddings=embeddings, texts=chunks)
    
    # 5. Initialize ResonanceDB client
    print("\n[5/5] Initializing ResonanceDB client...")
    resonance = ResonanceDBClient(base_url="http://localhost:8080")
    
    try:
        if not resonance.health_check():
            print("ERROR: ResonanceDB server not responding!")
            print("Make sure: docker-compose up -d in ResonanceDB folder")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not connect to ResonanceDB: {e}")
        sys.exit(1)
    
    print("     Connected to ResonanceDB")
    
    # 6. Pre-populate ResonanceDB
    print("\n[6/6] Pre-populating ResonanceDB...")
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        amplitude, phase = vector_to_wave(embedding, chunk)
        resonance.insert_record(
            chunk_id=f"chunk_{i:04d}",
            text=chunk,
            amplitude=amplitude,
            phase=phase
        )
    print(f"     Inserted {len(chunks)} records")
    
    # 7. Run evaluation
    print("\n" + "=" * 100)
    print("RUNNING DUAL RETRIEVAL COMPARISON")
    print("=" * 100)
    
    evaluator = DualRAGEvaluator(baseline, resonance, embedder)
    
    test_queries = [
        "What is chronic kidney disease?",
        "How does hypertension relate to kidney disease?",
        "Tell me about diabetic nephropathy",
    ]
    
    for query in test_queries:
        evaluator.compare_retrievers(query, top_k=3)

if __name__ == "__main__":
    main()
```

---

## Pattern 7: Error Handling for HTTP Calls

### ✅ DO: Robust, informative error handling

```python
import requests
from typing import Optional, Dict
import json

class RobustHTTPClient:
    """Example of error-aware HTTP communication."""
    
    def post_with_retry(
        self,
        url: str,
        payload: Dict,
        timeout: int = 10,
        max_retries: int = 2
    ) -> Optional[Dict]:
        """
        POST with retry logic and detailed error reporting.
        
        Args:
            url: Full URL endpoint
            payload: JSON-serializable dict
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
        
        Returns:
            Parsed JSON response or None on failure
        """
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=timeout,
                    headers={"Content-Type": "application/json"}
                )
                
                # Check status code
                if response.status_code >= 200 and response.status_code < 300:
                    return response.json()
                elif response.status_code >= 400 and response.status_code < 500:
                    # Client error - don't retry
                    error_msg = response.json().get("error", "Unknown error")
                    print(f"Client Error ({response.status_code}): {error_msg}")
                    return None
                else:
                    # Server error - retry
                    print(f"Server Error ({response.status_code}). Attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        continue
                    return None
            
            except requests.exceptions.ConnectionError as e:
                print(f"Connection failed: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying (attempt {attempt + 2}/{max_retries})...")
                    continue
                return None
            
            except requests.exceptions.Timeout:
                print(f"Request timed out (>{timeout}s). Attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    continue
                return None
            
            except json.JSONDecodeError as e:
                print(f"Invalid JSON in response: {e}")
                print(f"Response body: {response.text[:200]}")
                return None
            
            except Exception as e:
                print(f"Unexpected error: {type(e).__name__}: {e}")
                return None
        
        return None
```

---

## Pattern 8: Type Hints & Validation

### ✅ DO: Proper typing for IDE + Copilot

```python
from typing import List, Tuple, Optional, Dict
import numpy as np

# Good: Clear signatures with proper types
def vector_to_wave(
    vector: np.ndarray, 
    text: str
) -> Tuple[List[float], List[float]]:
    """Convert vector (384,) to amplitude, phase lists."""
    ...

def search_wave(
    amplitude: List[float],
    phase: List[float],
    top_k: int = 3
) -> List[Dict[str, any]]:
    """Query ResonanceDB with wave pattern."""
    ...

def chunk_document(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """Split document into overlapping chunks."""
    ...

# Validation helper
def validate_wave_pattern(
    amplitude: List[float],
    phase: List[float],
    expected_dim: int = 384
) -> bool:
    """Check amplitude/phase have correct dimensions."""
    if len(amplitude) != expected_dim or len(phase) != expected_dim:
        raise ValueError(
            f"Expected dimension {expected_dim}, "
            f"got amplitude={len(amplitude)}, phase={len(phase)}"
        )
    return True
```

---

## Pattern 9: Constants & Configuration

### ✅ DO: Centralize all magic numbers

```python
# config.py - Single source of truth

# Models
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Document processing
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# ResonanceDB
RESONANCE_BASE_URL = "http://localhost:8080"
RESONANCE_TIMEOUT = 10  # seconds
RESONANCE_MAX_RETRIES = 2

# Retrieval
TOP_K = 3
WAVE_SEARCH_TIMEOUT = 30  # for batch operations

# Negation detection
NEGATION_WORDS = {
    "not", "never", "unless", "contraindicated",
    "no", "none", "without", "absence", "lack"
}

# Math constants
import math
PI = math.pi
```

---

## How to Use These Patterns with Copilot

### For Chat Completions:
1. Copy the pattern into your message
2. Tell Copilot what you want to change: *"Modify this pattern to support batch search"*
3. Copilot will extend/adapt the code while maintaining style

### For Inline Completions:
1. Start typing a function signature
2. Copilot will autocomplete following the patterns above
3. Use `↑↓` to suggest alternatives

### Example Prompt:
```
I have this pattern for ResonanceDB insertion (paste code).
Now create a similar pattern for batch insertion that:
- Takes a list of 100+ records
- Splits into batches of 50
- Handles partial failures
- Logs progress
- Returns statistics
```
