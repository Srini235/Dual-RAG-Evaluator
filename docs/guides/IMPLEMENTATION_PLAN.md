# Implementation Plan: Dual RAG Retrieval (ChromaDB vs. ResonanceDB)

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Dual RAG Comparison System                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Document Processing Layer                                  │
│     └─> Load PDF → Chunk → Generate Base Embeddings           │
│                                                                 │
│  2. Baseline Pipeline (Traditional Vector DB)                  │
│     └─> ChromaDB/FAISS In-Memory Store                        │
│     └─> Cosine Similarity Retrieval (top_k)                   │
│                                                                 │
│  3. Wave-Based Pipeline (ResonanceDB)                         │
│     ├─> Vector → Wave Mapper (Amplitude + Phase)              │
│     ├─> ResonanceDB REST Client (HTTP POST/GET)              │
│     └─> Phase-Coherent Retrieval (top_k)                      │
│                                                                 │
│  4. Evaluation Harness                                         │
│     └─> Side-by-side comparison and metrics                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Breakdown

### Module 1: Document Processing (`doc_processor.py`)

**Purpose:** Load, chunk, and generate embeddings from documents.

**Key Functions:**
- `load_pdf(file_path: str) -> str` — Extract text from PDF
- `chunk_document(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]` — Split into overlapping chunks
- `generate_embeddings(chunks: List[str], model_name: str) -> np.ndarray` — Batch embed chunks using HuggingFace
  - Returns shape `(num_chunks, embedding_dim)`
  - **Model:** `sentence-transformers/all-MiniLM-L6-v2` (384-dim)

**Dependencies:** `langchain`, `PyPDF2`, `sentence-transformers`, `numpy`

---

### Module 2: Baseline Vector DB (`baseline_retriever.py`)

**Purpose:** Standard vector similarity retrieval using ChromaDB or FAISS.

**Key Functions:**
- `class BaselineRetriever`:
  - `__init__(embeddings: np.ndarray, chunks: List[str])`
  - `insert(embeddings: np.ndarray, chunks: List[str]) -> None` — Store embeddings and chunks
  - `retrieve(query_embedding: np.ndarray, top_k: int = 3) -> List[Dict]` — Cosine similarity search
    - Returns: `[{"chunk_id": int, "text": str, "score": float}, ...]`

**Backend:** ChromaDB in-memory (ephemeral)

**Scoring:** Cosine similarity, normalized to [0, 1]

---

### Module 3: Wave Mapper (`wave_mapper.py`)

**Purpose:** Convert base embeddings to amplitude/phase representation.

**Key Functions:**
- `vector_to_wave(vector: np.ndarray, text: str) -> Tuple[List[float], List[float]]`
  - **Amplitude:** `np.abs(vector)` normalized to [0, 1]
  - **Phase:** Random ∈ [-π, π]
    - **Heuristic:** If text contains negation ("not", "never", "unless", "contraindicated"), shift phase by π
    - Result: Phase ∈ [-π, π]
  - Returns: `(amplitude_list, phase_list)`

- `query_to_wave(embedding: np.ndarray, query_text: str) -> Tuple[List[float], List[float]]`
  - Same logic as `vector_to_wave`

**Dependencies:** `numpy`

---

### Module 4: ResonanceDB Client (`resonance_client.py`)

**Purpose:** HTTP client for ResonanceDB REST API at `http://localhost:8080`.

**Key Functions:**
- `class ResonanceDBClient`:
  - `__init__(base_url: str = "http://localhost:8080")`
  - `health_check() -> bool` — Verify server is running
  - `insert_record(chunk_id: str, text: str, amplitude: List[float], phase: List[float]) -> bool`
    - **Endpoint:** `POST /api/v1/insert`
    - **Payload:** `{"id": chunk_id, "text": text, "amplitude": [...], "phase": [...]}`
    - Returns: `True` if successful
  - `search_wave(amplitude: List[float], phase: List[float], top_k: int = 3) -> List[Dict]`
    - **Endpoint:** `POST /api/v1/search`
    - **Payload:** `{"amplitude": [...], "phase": [...], "top_k": top_k}`
    - Returns: `[{"chunk_id": str, "text": str, "score": float}, ...]`
  - `clear_store() -> bool` — Reset database for fresh tests
  - Error handling: `ConnectionError`, `TimeoutError`, `JSONDecodeError`

**Dependencies:** `requests`, `numpy`, `typing`

---

### Module 5: Evaluator (`evaluator.py`)

**Purpose:** Run dual pipelines and compare results.

**Key Functions:**
- `class DualRAGEvaluator`:
  - `__init__(baseline_retriever: BaselineRetriever, resonance_client: ResonanceDBClient, embedder)`
  - `compare_retrievers(query: str, query_text: str = None, top_k: int = 3)`
    - Embeds query using the same model as chunks
    - Retrieves top_k from baseline (cosine similarity)
    - Maps query to wave (using wave mapper)
    - Retrieves top_k from ResonanceDB
    - Prints side-by-side results table
    - Optionally logs metrics (overlap, score distribution)

**Output Format:**
```
Query: "..." 

BASELINE (ChromaDB - Cosine Similarity)
┌──────────┬─────────────────┬───────────┐
│ Rank     │ Text (truncated) │ Score     │
├──────────┼─────────────────┼───────────┤
│ 1        │ "[chunk text]"  │ 0.876     │
│ 2        │ "[chunk text]"  │ 0.754     │
│ 3        │ "[chunk text]"  │ 0.682     │
└──────────┴─────────────────┴───────────┘

RESONANCEDB (Wave-Based Retrieval)
┌──────────┬─────────────────┬───────────┐
│ Rank     │ Text (truncated) │ Score     │
├──────────┼─────────────────┼───────────┤
│ 1        │ "[chunk text]"  │ 0.912     │
│ 2        │ "[chunk text]"  │ 0.698     │
│ 3        │ "[chunk text]"  │ 0.645     │
└──────────┴─────────────────┴───────────┘

Overlap in Top-3: 2/3
```

---

## Data Flow Example

```
PDF File
  ↓
  ├─→ [load_pdf] → Raw Text
  │     ↓
  ├─→ [chunk_document] → List[chunks]
  │     ↓
  ├─→ [generate_embeddings] → np.ndarray (N, 384)
  │     ↓
  ├─→ [BaselineRetriever.insert] ───────────→ ChromaDB Store
  │     ↓
  └─→ [vector_to_wave] ─────────────────────→ ResonanceDB.insert
        amplitude, phase
```

---

## Implementation Order

1. **Phase 1:** `doc_processor.py` — Simple chunks with hardcoded text
2. **Phase 2:** `baseline_retriever.py` — ChromaDB storage and retrieval
3. **Phase 3:** `wave_mapper.py` — Vector-to-wave conversion logic
4. **Phase 4:** `resonance_client.py` — HTTP client with error handling
5. **Phase 5:** `evaluator.py` — Dual comparison harness
6. **Phase 6:** `main.py` — End-to-end script with sample data
7. **Phase 7:** [Optional] Swap hardcoded chunks for real PDF loading

---

## Dependencies Summary

```
requests          # HTTP calls to ResonanceDB
numpy             # Vector math, amplitude/phase ops
sentence-transformers  # Embedding model
chromadb          # Baseline vector DB
langchain         # PDF loading (optional, use PyPDF2 if simpler)
PyPDF2            # PDF text extraction
typing            # Type hints
```

---

## Error Handling Strategy

### ResonanceDB Connection Errors
- **Scenario:** Docker container not running
- **Action:** Catch `requests.exceptions.ConnectionError`, log error, suggest `docker-compose up -d`

### HTTP Timeouts
- Catch `requests.exceptions.Timeout`, retry once with timeout=30s

### Malformed Responses
- Catch `json.JSONDecodeError`, log raw response body

### Mismatched Dimensions
- Validate `len(amplitude) == len(phase) == embedding_dim`
- Raise `ValueError` with clear message

---

## Testing Strategy (Optional Comment-based)

```python
# Unit tests (pseudo outline)
# test_vector_to_wave: ensure phase shift on negation
# test_baseline_insert: verify ChromaDB stores chunks
# test_resonance_client: mock HTTP responses, verify parsing
# test_evaluator: run with 3-5 sample chunks, verify output format
```

---

## Configuration & Constants

```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RESONANCE_BASE_URL = "http://localhost:8080"
REQUEST_TIMEOUT = 10  # seconds
TOP_K = 3
NEGATION_WORDS = {"not", "never", "unless", "contraindicated"}
```
