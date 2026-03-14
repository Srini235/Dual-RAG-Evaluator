# Dual RAG Implementation Spec: Vector DB vs. ResonanceDB

## Objective
Generate a Python script to compare standard vector retrieval (using ChromaDB/FAISS) against wave-based semantic retrieval using a local ResonanceDB Docker container.

## Architecture

### 1. Document Processing
* Use `langchain` or `PyPDF2` to load a medical PDF (e.g., CKD Clinical Guidelines).
* Chunk the document using `RecursiveCharacterTextSplitter` (chunk_size=500, chunk_overlap=50).

### 2. Embedding Generation
* Use a local HuggingFace embedding model (e.g., `sentence-transformers/all-MiniLM-L6-v2`) to generate base 1D float vectors.

### 3. Baseline Pipeline (Traditional Vector DB)
* Store the chunks and base embeddings in an in-memory ChromaDB instance or FAISS index.
* Implement a `retrieve_baseline(query, top_k=3)` function using standard cosine similarity.

### 4. ResonanceDB Pipeline (Wave-Based DB)
* The ResonanceDB server is running locally via Docker at `http://localhost:8080`.
* **The Wave Mapper:** Create a utility function `vector_to_wave(vector, text)`. Since we lack the proprietary EchoThesis codec, implement a heuristic mapping for this POC:
  * `Amplitude`: Use the absolute values or normalized magnitudes of the base vector.
  * `Phase`: Generate a phase array (values between $-\pi$ and $\pi$). Add a heuristic: if the `text` contains negation words ("not", "never", "unless", "contraindicated"), shift the phase of the vector by $\pi$ (180 degrees) to simulate destructive interference.
* **Database Client:** Create a Python class `ResonanceDBClient`:
  * `insert_record(chunk_id, text, amplitude, phase)`: Sends a `POST` request to `http://localhost:8080/api/v1/insert` (JSON payload: `{"id": chunk_id, "text": text, "amplitude": [...], "phase": [...]}`).
  * `search_wave(amplitude, phase, top_k=3)`: Sends a `POST` request to `http://localhost:8080/api/v1/search` (JSON payload: `{"amplitude": [...], "phase": [...], "top_k": 3}`). Returns the matched chunks.

### 5. Evaluation Harness
* Create a function `compare_retrievers(query)` that:
  1. Embeds the query.
  2. Retrieves `top_k` from the Baseline.
  3. Maps query to wave and retrieves `top_k` from ResonanceDBClient.
  4. Prints the results side-by-side for manual inspection.

## Constraints & Requirements
* Use `requests` for the ResonanceDB HTTP client.
* Include error handling for the `requests` calls (e.g., ConnectionError if the Docker container isn't running).
* Use `numpy` for the vector-to-wave math operations.
* Write clean, typed Python code. Do not implement the LLM generation step yet; focus purely on the retrieval and comparison logic.