# ResonanceDB REST API Reference

## Server Information

- **Base URL:** `http://localhost:8080`
- **Default Port:** 8080
- **Content-Type:** `application/json`
- **Response Format:** JSON

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Verify ResonanceDB server is running.

**Request:**
```bash
curl -X GET http://localhost:8080/health
```

**Response (Success 200):**
```json
{
  "status": "ok",
  "timestamp": "2026-03-14T10:30:45Z"
}
```

**Response (Failure 503):**
```json
{
  "status": "unavailable",
  "error": "Store initialization in progress"
}
```

---

### 2. Insert Record

**Endpoint:** `POST /api/v1/insert`

**Description:** Store a single record (chunk + metadata + amplitude + phase).

**Request:**
```json
{
  "id": "chunk_001",
  "text": "Chronic Kidney Disease (CKD) is a condition...",
  "amplitude": [0.1, 0.45, 0.67, 0.89, 0.23, ...],
  "phase": [-3.14, 1.57, 0.5, -2.0, 3.14, ...]
}
```

**Parameters:**
- `id` (string, required): Unique identifier for the chunk
- `text` (string, required): Human-readable text of the chunk
- `amplitude` (array of floats, required): Amplitude values ∈ [0, 1]
  - Length must equal embedding dimension (384 for all-MiniLM-L6-v2)
- `phase` (array of floats, required): Phase values ∈ [-π, π]
  - Length must equal embedding dimension (384 for all-MiniLM-L6-v2)

**Response (Success 200):**
```json
{
  "id": "chunk_001",
  "status": "inserted",
  "timestamp": "2026-03-14T10:30:45Z"
}
```

**Response (Validation Error 400):**
```json
{
  "error": "Dimension mismatch: expected 384, got 256",
  "field": "amplitude"
}
```

**Response (Conflict 409 - ID already exists):**
```json
{
  "error": "Record already exists",
  "id": "chunk_001"
}
```

---

### 3. Batch Insert

**Endpoint:** `POST /api/v1/insert/batch`

**Description:** Store multiple records in a single request (more efficient).

**Request:**
```json
{
  "records": [
    {
      "id": "chunk_001",
      "text": "CKD Stage 1...",
      "amplitude": [...],
      "phase": [...]
    },
    {
      "id": "chunk_002",
      "text": "CKD Stage 2...",
      "amplitude": [...],
      "phase": [...]
    }
  ]
}
```

**Response (Partial Success 207 Multi-Status):**
```json
{
  "inserted": 50,
  "failed": 1,
  "failures": [
    {
      "id": "chunk_005",
      "error": "Dimension mismatch"
    }
  ]
}
```

---

### 4. Search by Wave

**Endpoint:** `POST /api/v1/search`

**Description:** Retrieve records by phase-coherent resonance matching.

**Request:**
```json
{
  "amplitude": [0.15, 0.48, 0.65, ...],
  "phase": [-2.5, 1.2, 0.8, ...],
  "top_k": 3
}
```

**Parameters:**
- `amplitude` (array of floats, required): Query amplitude ∈ [0, 1]
- `phase` (array of floats, required): Query phase ∈ [-π, π]
- `top_k` (integer, optional): Number of results to return (default: 3, max: 100)

**Response (Success 200):**
```json
{
  "query_timestamp": "2026-03-14T10:30:45Z",
  "top_k": 3,
  "results": [
    {
      "rank": 1,
      "id": "chunk_042",
      "text": "CKD is characterized by reduced GFR...",
      "score": 0.876,
      "phase_coherence": 0.92,
      "amplitude_balance": 0.88
    },
    {
      "rank": 2,
      "id": "chunk_035",
      "text": "Proteinuria is a key marker of kidney damage...",
      "score": 0.754,
      "phase_coherence": 0.81,
      "amplitude_balance": 0.79
    },
    {
      "rank": 3,
      "id": "chunk_018",
      "text": "Hypertension is a common comorbidity...",
      "score": 0.682,
      "phase_coherence": 0.72,
      "amplitude_balance": 0.75
    }
  ]
}
```

**Response (Empty Results 200):**
```json
{
  "query_timestamp": "2026-03-14T10:30:45Z",
  "top_k": 3,
  "results": []
}
```

**Response (Validation Error 400):**
```json
{
  "error": "Dimension mismatch: expected 384, got 256",
  "field": "phase"
}
```

---

### 5. Search by ID

**Endpoint:** `GET /api/v1/search/byid/{id}`

**Description:** Retrieve a single record by ID.

**Request:**
```bash
curl -X GET http://localhost:8080/api/v1/search/byid/chunk_042
```

**Response (Success 200):**
```json
{
  "id": "chunk_042",
  "text": "CKD is characterized by...",
  "amplitude": [0.1, 0.45, ...],
  "phase": [-3.14, 1.57, ...],
  "stored_at": "2026-03-14T10:25:30Z"
}
```

**Response (Not Found 404):**
```json
{
  "error": "Record not found",
  "id": "chunk_042"
}
```

---

### 6. Clear Store

**Endpoint:** `POST /api/v1/clear`

**Description:** Delete all records (useful for testing). **DESTRUCTIVE OPERATION.**

**Request:**
```bash
curl -X POST http://localhost:8080/api/v1/clear
```

**Response (Success 200):**
```json
{
  "status": "cleared",
  "records_deleted": 12345,
  "timestamp": "2026-03-14T10:30:45Z"
}
```

---

### 7. Get Store Statistics

**Endpoint:** `GET /api/v1/stats`

**Description:** Retrieve metadata about the store.

**Response (Success 200):**
```json
{
  "total_records": 12345,
  "embedding_dimension": 384,
  "store_version": "1.0.0",
  "phase_shards": 64,
  "memory_usage_bytes": 1073741824,
  "uptime_seconds": 3600
}
```

---

## Error Codes

| Code | Meaning | When It Occurs |
| ---- | ------- | -------------- |
| 200  | OK | Request succeeded |
| 207  | Multi-Status | Batch insert with partial failures |
| 400  | Bad Request | Missing/invalid fields, dimension mismatch |
| 404  | Not Found | Record ID doesn't exist |
| 409  | Conflict | Record ID already exists (insert) |
| 500  | Internal Server Error | Unexpected store error |
| 503  | Service Unavailable | Server not ready |

---

## Common Patterns

### Insert + Search Flow
```
1. POST /api/v1/insert (chunk_001, amplitude, phase)
   → Response: inserted
2. POST /api/v1/search (amplitude=chunk_001's, phase=chunk_001's, top_k=3)
   → Response: chunk_001 + 2 similar chunks (if they exist)
```

### Batch Pre-populate + Query
```
1. POST /api/v1/insert/batch (50 records)
   → Response: 50 inserted
2. POST /api/v1/search (query wave, top_k=3)
   → Response: 3 best matches
```

### Health Check with Retry
```
1. GET /health
   → Response: 503 (not ready)
   → Wait 1 second
   → GET /health
   → Response: 200 (ready)
```

---

## Request/Response Size Limits

- **Max Request Body:** 8 MB (configurable via `resonance.rest.maxBodyBytes`)
- **Max Batch Insert:** ~1000 records per request (depends on embedding_dim)
- **Max top_k:** 100 results

---

## Timeout Recommendations

- **Standard Insert:** 5 seconds
- **Batch Insert (1000 records):** 30 seconds
- **Search:** 10 seconds
- **Health Check:** 2 seconds

---

## Example: Complete Insert + Search Cycle (cURL)

```bash
# 1. Check health
curl -X GET http://localhost:8080/health

# 2. Insert a record
curl -X POST http://localhost:8080/api/v1/insert \
  -H "Content-Type: application/json" \
  -d '{
    "id": "chunk_001",
    "text": "Chronic Kidney Disease (CKD) staging",
    "amplitude": [0.1, 0.2, 0.3, ... 0.15],
    "phase": [-3.14, -1.57, 0.0, ... 1.57]
  }'

# 3. Search by same wave
curl -X POST http://localhost:8080/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "amplitude": [0.1, 0.2, 0.3, ... 0.15],
    "phase": [-3.14, -1.57, 0.0, ... 1.57],
    "top_k": 3
  }'

# 4. Clear store
curl -X POST http://localhost:8080/api/v1/clear

# 5. Get stats
curl -X GET http://localhost:8080/api/v1/stats
```
