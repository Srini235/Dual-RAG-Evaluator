# API Integration Debug Guide

Comprehensive debugging guide for ResonanceDB HTTP integration.

---

## Quick Diagnostics

### Check ResonanceDB Server Status

```bash
# From PowerShell
curl.exe -X GET http://localhost:8080/health

# Or Python
python -c "import requests; print(requests.get('http://localhost:8080/health').status_code)"
```

**Expected Response (200 OK):**
```json
{
  "status": "ok",
  "timestamp": "2026-03-14T10:30:45Z"
}
```

**Common Issues:**
- **Connection refused (0):** Server not running
  - Solution: `docker run -p 8080:8080 resonance-db`
- **Timeout:** Server running but slow
  - Check Docker logs: `docker logs <container-id>`
- **Invalid certificate:** SSL/TLS issue
  - Not applicable for localhost (HTTP only)

---

## Request/Response Inspection

### Using Python Requests

```python
import requests
import json

# Insert request
payload = {
    "id": "test_chunk",
    "text": "Sample medical text",
    "amplitude": [0.1, 0.45, 0.67, ...],  # 384 values
    "phase": [-3.14, 1.57, 0.5, ...]      # 384 values
}

try:
    response = requests.post(
        "http://localhost:8080/api/v1/insert",
        json=payload,
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    
except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: {e}")
except requests.exceptions.Timeout as e:
    print(f"Timeout Error: {e}")
except json.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")
    print(f"Raw Response: {response.text}")

except Exception as e:
    print(f"Unexpected Error: {e}")
```

### Using cURL (PowerShell)

```powershell
# Health check
$response = curl.exe -X GET http://localhost:8080/health
Write-Host "Status: $response"

# Insert record
$payload = @{
    id = "test_001"
    text = "Sample text"
    amplitude = @([0.1, 0.45, 0.67] * 128)
    phase = @([-3.14, 1.57, 0.5] * 128)
} | ConvertTo-Json

$response = curl.exe -X POST `
    -Header "Content-Type: application/json" `
    -Data $payload `
    http://localhost:8080/api/v1/insert

Write-Host "Response: $response"
```

---

## Common Error Messages & Solutions

### 400 - Bad Request

**Error:** `{"error": "Dimension mismatch: expected 384, got 256", "field": "amplitude"}`

**Cause:** Amplitude or phase array size doesn't match expected embedding dimension (384)

**Solution:**
```python
# Verify dimensions
print(f"Amplitude length: {len(amplitude)}")
print(f"Phase length: {len(phase)}")

# Should be 384 for all-MiniLM-L6-v2
if len(amplitude) != 384:
    # Pad or truncate
    amplitude = amplitude[:384] if len(amplitude) > 384 else amplitude + [0.0] * (384 - len(amplitude))
```

---

### 409 - Conflict

**Error:** `{"error": "Record already exists", "id": "chunk_001"}`

**Cause:** Trying to insert duplicate chunk ID

**Solution:**
```python
# Clear store before re-inserting
client.clear_store()

# Or use unique IDs
chunk_id = f"chunk_{timestamp}_{uuid.uuid4()}"
```

---

### 503 - Service Unavailable

**Error:** `{"error": "Store initialization in progress"}`

**Cause:** Server is still starting up

**Solution:**
```python
import time

def wait_for_server(max_retries=10, delay=2):
    """Wait for server to be ready."""
    for attempt in range(max_retries):
        try:
            response = requests.get("http://localhost:8080/health", timeout=2)
            if response.status_code == 200:
                print("✓ Server is ready")
                return True
        except:
            pass
        
        print(f"Waiting for server... (attempt {attempt + 1}/{max_retries})")
        time.sleep(delay)
    
    return False

wait_for_server()
```

---

### Connection Timeout

**Error:** `requests.exceptions.Timeout: HTTPConnectionPool(host='localhost', port=8080): Read timed out`

**Cause:**
- Server is overloaded
- Network latency
- Large batch request (>1000 records)

**Solution:**
```python
# Increase timeout for batch operations
client = ResonanceDBClient(timeout=30)  # 30 seconds for batch

# Or split batch into smaller chunks
records_per_batch = 100
for i in range(0, len(records), records_per_batch):
    batch = records[i:i + records_per_batch]
    result = client.insert_batch(batch)
    print(f"Inserted batch {i//records_per_batch + 1}")
```

---

## Dimension Mismatch Debugging

### Why 384?

The embedding model `sentence-transformers/all-MiniLM-L6-v2` produces **384-dimensional vectors**.

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embedding = model.encode("Sample text")
print(f"Embedding dimension: {len(embedding)}")  # Output: 384
```

### How to Check Your Data

```python
import numpy as np

# Check embeddings shape
embeddings = np.random.randn(10, 384)
print(f"Shape: {embeddings.shape}")  # Should be (N, 384)

# Check after conversion to wave
amplitude, phase = vector_to_wave(embeddings[0], "text")
print(f"Amplitude length: {len(amplitude)}")  # Should be 384
print(f"Phase length: {len(phase)}")           # Should be 384

# Validate ranges
print(f"Amplitude range: [{min(amplitude):.3f}, {max(amplitude):.3f}]")  # Should be [0, 1]
print(f"Phase range: [{min(phase):.3f}, {max(phase):.3f}]")  # Should be [-π, π]
```

---

## Performance Profiling

### Measuring Request Latency

```python
import time
import requests

def measure_request(method, url, json=None, timeout=10):
    """Measure request latency."""
    start = time.time()
    
    try:
        if method == "POST":
            response = requests.post(url, json=json, timeout=timeout)
        else:
            response = requests.get(url, timeout=timeout)
        
        elapsed = time.time() - start
        
        return {
            "status_code": response.status_code,
            "latency_ms": elapsed * 1000,
            "size_bytes": len(response.content)
        }
    
    except Exception as e:
        elapsed = time.time() - start
        return {
            "error": str(e),
            "latency_ms": elapsed * 1000
        }

# Profile operations
health_perf = measure_request("GET", "http://localhost:8080/health")
print(f"Health check: {health_perf['latency_ms']:.1f}ms")

insert_payload = {
    "id": "test",
    "text": "text",
    "amplitude": [0.5] * 384,
    "phase": [0.0] * 384
}
insert_perf = measure_request("POST", "http://localhost:8080/api/v1/insert", json=insert_payload)
print(f"Insert: {insert_perf['latency_ms']:.1f}ms")
```

---

## Docker Troubleshooting

### Check Container Status

```bash
# List running containers
docker ps | grep resonance

# Check container logs
docker logs <container-id> --tail=50 --follow

# Inspect container network
docker inspect <container-id> | grep -A 5 NetworkSettings
```

### Check Port Binding

```powershell
# PowerShell: check if port 8080 is in use
Get-NetTCPConnection -State Listen | Where-Object {$_.LocalPort -eq 8080}

# Output should show java.exe or similar
```

### Rebuild from Scratch

```bash
# Remove old container
docker rm -f resonance-db

# Rebuild image
docker build -t resonance-db .

# Run with verbose output
docker run -p 8080:8080 -e DEBUG=true resonance-db
```

---

## Wave Pattern Validation

### Check Dimension Mismatch

```python
from doc_processor import DocumentProcessor
from wave_mapper import validate_wave_pattern

processor = DocumentProcessor()

# Embed some text
text = "Sample medical text"
embedding = processor.embed_chunks([text])[0]

# Convert to wave
amplitude, phase = vector_to_wave(embedding, text)

# Validate
try:
    validate_wave_pattern(amplitude, phase, expected_dim=384)
    print("✓ Wave pattern valid")
except ValueError as e:
    print(f"✗ Validation failed: {e}")

# Check value ranges
import numpy as np
amp_array = np.array(amplitude)
phase_array = np.array(phase)

print(f"Amplitude: min={amp_array.min():.3f}, max={amp_array.max():.3f}")
print(f"Phase: min={phase_array.min():.3f}, max={phase_array.max():.3f}")
```

---

## Integration Test Checklist

### Before Running main.py

- [ ] Python 3.9+ installed
- [ ] `pip install -r requirements.txt` completed
- [ ] ResonanceDB Docker container **running** at :8080
- [ ] `http://localhost:8080/health` returns 200
- [ ] Model `sentence-transformers/all-MiniLM-L6-v2` downloads on first run (120MB)

### During Execution

- [ ] No embedding dimension errors
- [ ] No connection timeouts to :8080
- [ ] Both baseline and resonance retrievers working
- [ ] Side-by-side results printing correctly

### After Execution

- [ ] All queries returned results
- [ ] Overlap metrics computed
- [ ] No uncaught exceptions

---

## Logging & Monitoring

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now all requests logged
import requests
requests.logging.getLogger("urllib3").setLevel(logging.DEBUG)
```

### Custom Logging in Client

```python
import logging

logger = logging.getLogger(__name__)

class DebugResonanceDBClient(ResonanceDBClient):
    def search_wave(self, amplitude, phase, top_k=3):
        logger.debug(f"Searching: amplitude_len={len(amplitude)}, phase_len={len(phase)}, top_k={top_k}")
        
        result = super().search_wave(amplitude, phase, top_k)
        
        logger.debug(f"Results: count={len(result)}, top_score={result[0]['score'] if result else 'N/A'}")
        
        return result
```

---

## Performance Expectations

### Typical Latencies (with 1000 records in store)

| Operation | Expected (ms) | Timeout (s) |
|-----------|---------------|------------|
| Health check | 1-5 | 2 |
| Single insert | 5-20 | 10 |
| Batch insert (100 records) | 50-200 | 30 |
| Search (top-3) | 10-50 | 10 |
| Clear store | 100-500 | 30 |

---

## Getting Help

### Useful Debug Commands

```python
# Test connection and basic functionality
from resonance_client import ResonanceDBClient

client = ResonanceDBClient()

# 1. Health check
try:
    is_healthy = client.health_check()
    print(f"Health: {is_healthy}")
except Exception as e:
    print(f"Health check failed: {e}")

# 2. Get stats
stats = client.get_stats()
if stats:
    print(f"Store stats: {stats}")
else:
    print("Failed to get stats")

# 3. Test insert
test_amp = [0.5] * 384
test_phase = [0.0] * 384
success = client.insert_record("test_id", "test text", test_amp, test_phase)
print(f"Insert test: {success}")

# 4. Test search
results = client.search_wave(test_amp, test_phase, top_k=1)
print(f"Search test: {len(results)} results")
```
