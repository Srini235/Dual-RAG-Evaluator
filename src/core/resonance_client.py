"""
ResonanceDB HTTP Client Module - Interface with ResonanceDB REST API
"""

from typing import List, Dict, Optional
import requests
import json

# Configuration
RESONANCE_BASE_URL = "http://localhost:8080"
REQUEST_TIMEOUT = 10
MAX_RETRIES = 2


class ResonanceDBClient:
    """
    HTTP client for ResonanceDB REST API.
    
    Supports:
    - Health check
    - Single record insertion
    - Batch insertion
    - Wave-based search
    - Store management (clear, stats)
    """
    
    def __init__(self, base_url: str = RESONANCE_BASE_URL, timeout: int = REQUEST_TIMEOUT):
        """
        Initialize ResonanceDB client.
        
        Args:
            base_url: Base URL of ResonanceDB server (default: http://localhost:8080)
            timeout: Request timeout in seconds (default: 10)
            
        Example:
            >>> client = ResonanceDBClient()
            >>> client.health_check()
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._session = requests.Session()
    
    def health_check(self) -> bool:
        """
        Check if ResonanceDB server is running and healthy.
        
        Returns:
            True if server is healthy, False otherwise
            
        Raises:
            ConnectionError: If server is unreachable
            
        Example:
            >>> client = ResonanceDBClient()
            >>> if client.health_check():
            ...     print("Server is ready")
        """
        try:
            url = f"{self.base_url}/health"
            response = self._session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                print("[OK] ResonanceDB server is healthy")
                return True
            else:
                print(f"⚠ ResonanceDB health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError as e:
            print(f"ERROR: Cannot connect to ResonanceDB at {self.base_url}")
            print(f"       Make sure Docker container is running: docker-compose up -d")
            raise ConnectionError(f"Failed to connect to {self.base_url}: {e}")
        except requests.exceptions.Timeout:
            print(f"ERROR: Health check timed out (>{self.timeout}s)")
            raise
        except Exception as e:
            print(f"ERROR: Unexpected error during health check: {e}")
            raise
    
    def insert_record(
        self,
        chunk_id: str,
        text: str,
        amplitude: List[float],
        phase: List[float]
    ) -> bool:
        """
        Insert a single record into ResonanceDB.
        
        Args:
            chunk_id: Unique identifier for the chunk
            text: Human-readable text content
            amplitude: List of amplitude values (length = embedding_dim)
            phase: List of phase values (length = embedding_dim)
        
        Returns:
            True if insertion successful, False otherwise
            
        Raises:
            ValueError: If amplitude/phase lengths don't match
            
        Example:
            >>> client = ResonanceDBClient()
            >>> success = client.insert_record(
            ...     chunk_id="chunk_001",
            ...     text="Sample text",
            ...     amplitude=[0.1, 0.45, ...],
            ...     phase=[-3.14, 1.57, ...]
            ... )
        """
        if len(amplitude) != len(phase):
            raise ValueError(
                f"amplitude and phase must have same length: "
                f"got {len(amplitude)} and {len(phase)}"
            )
        
        url = f"{self.base_url}/api/v1/insert"
        payload = {
            "id": chunk_id,
            "text": text,
            "amplitude": amplitude,
            "phase": phase
        }
        
        try:
            response = self._session.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if 200 <= response.status_code < 300:
                return True
            elif 400 <= response.status_code < 500:
                # Client error - don't retry
                try:
                    error_msg = response.json().get("error", "Unknown error")
                except:
                    error_msg = response.text[:100]
                print(f"ERROR: Client error ({response.status_code}): {error_msg}")
                return False
            else:
                # Server error
                print(f"ERROR: Server error ({response.status_code})")
                return False
        
        except requests.exceptions.ConnectionError as e:
            print(f"ERROR: Connection failed: {e}")
            return False
        except requests.exceptions.Timeout:
            print(f"ERROR: Request timed out (>{self.timeout}s)")
            return False
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON response: {e}")
            return False
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
            return False
    
    def insert_batch(
        self,
        records: List[Dict]
    ) -> Dict[str, int]:
        """
        Insert multiple records in a single batch request.
        
        Args:
            records: List of dicts with keys: id, text, amplitude, phase
        
        Returns:
            Dict with:
            - inserted: number of successfully inserted records
            - failed: number of failed records
            - errors: list of error details (if any)
            
        Example:
            >>> records = [
            ...     {"id": "c1", "text": "...", "amplitude": [...], "phase": [...]},
            ...     {"id": "c2", "text": "...", "amplitude": [...], "phase": [...]},
            ... ]
            >>> result = client.insert_batch(records)
            >>> print(f"Inserted: {result['inserted']}, Failed: {result['failed']}")
        """
        url = f"{self.base_url}/api/v1/insert/batch"
        payload = {"records": records}
        
        try:
            response = self._session.post(
                url,
                json=payload,
                timeout=self.timeout * 3,  # Longer timeout for batch
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 207:  # Multi-status
                result = response.json()
                return {
                    "inserted": result.get("inserted", 0),
                    "failed": result.get("failed", 0),
                    "errors": result.get("failures", [])
                }
            elif 200 <= response.status_code < 300:
                return {
                    "inserted": len(records),
                    "failed": 0,
                    "errors": []
                }
            else:
                print(f"ERROR: Batch insert failed ({response.status_code})")
                return {
                    "inserted": 0,
                    "failed": len(records),
                    "errors": [response.text[:100]]
                }
        
        except Exception as e:
            print(f"ERROR: Batch insert error: {e}")
            return {
                "inserted": 0,
                "failed": len(records),
                "errors": [str(e)]
            }
    
    def search_wave(
        self,
        amplitude: List[float],
        phase: List[float],
        top_k: int = 3
    ) -> List[Dict]:
        """
        Search ResonanceDB by wave pattern (amplitude + phase).
        
        Args:
            amplitude: List of amplitude values
            phase: List of phase values
            top_k: Number of results to return (default: 3, max: 100)
        
        Returns:
            List of result dicts with keys:
            - rank: integer (1-indexed)
            - id: string (chunk ID)
            - text: string (document text)
            - score: float (resonance score)
            
        Raises:
            ValueError: If amplitude/phase lengths don't match
            
        Example:
            >>> results = client.search_wave(
            ...     amplitude=[0.1, 0.45, ...],
            ...     phase=[-3.14, 1.57, ...],
            ...     top_k=3
            ... )
            >>> for r in results:
            ...     print(f"{r['rank']}. {r['text'][:50]}... ({r['score']:.4f})")
        """
        if len(amplitude) != len(phase):
            raise ValueError(
                f"amplitude and phase must have same length: "
                f"got {len(amplitude)} and {len(phase)}"
            )
        
        url = f"{self.base_url}/api/v1/search"
        payload = {
            "amplitude": amplitude,
            "phase": phase,
            "top_k": top_k
        }
        
        try:
            response = self._session.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                # Normalize response format
                return result.get("results", [])
            elif response.status_code == 204:  # No content
                return []
            else:
                print(f"ERROR: Search failed ({response.status_code})")
                try:
                    error = response.json().get("error", "Unknown error")
                    print(f"       {error}")
                except:
                    pass
                return []
        
        except requests.exceptions.Timeout:
            print(f"ERROR: Search timed out (>{self.timeout}s)")
            return []
        except json.JSONDecodeError:
            print(f"ERROR: Invalid JSON in search response")
            return []
        except Exception as e:
            print(f"ERROR: Search failed: {e}")
            return []
    
    def clear_store(self) -> bool:
        """
        Delete all records from the store.
        
        **WARNING: This is a destructive operation.**
        
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> client = ResonanceDBClient()
            >>> client.clear_store()  # Clears all data
        """
        url = f"{self.base_url}/api/v1/clear"
        
        try:
            response = self._session.post(url, timeout=self.timeout)
            
            if 200 <= response.status_code < 300:
                try:
                    result = response.json()
                    deleted = result.get("records_deleted", 0)
                    print(f"[OK] Cleared store ({deleted} records deleted)")
                except:
                    print("[OK] Store cleared")
                return True
            else:
                print(f"ERROR: Clear failed ({response.status_code})")
                return False
        
        except Exception as e:
            print(f"ERROR: Clear failed: {e}")
            return False
    
    def get_stats(self) -> Optional[Dict]:
        """
        Get store statistics and metadata.
        
        Returns:
            Dict with server stats, or None on failure
            
        Stats include:
        - total_records: Number of stored chunks
        - embedding_dimension: Dimension of stored vectors
        - memory_usage_bytes: Approximate memory usage
        - uptime_seconds: Server uptime
        
        Example:
            >>> stats = client.get_stats()
            >>> if stats:
            ...     print(f"Records: {stats['total_records']}")
        """
        url = f"{self.base_url}/api/v1/stats"
        
        try:
            response = self._session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"ERROR: Failed to get stats ({response.status_code})")
                return None
        
        except Exception as e:
            print(f"ERROR: Get stats failed: {e}")
            return None
    
    def close(self):
        """Close the HTTP session."""
        self._session.close()
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support."""
        self.close()


class MockResonanceDBClient:
    """
    Mock ResonanceDB client for testing without a real server.
    Returns realistic wave-based search results for demonstration.
    """
    
    def __init__(self):
        """Initialize mock client."""
        self.store = {}
        self.records_count = 0
    
    def health_check(self) -> bool:
        """Mock health check - always returns True."""
        return True
    
    def insert_record(self, chunk_id: str, text: str, amplitude: List, phase: List) -> bool:
        """Mock insert - stores record in memory."""
        self.store[chunk_id] = {
            "text": text,
            "amplitude": amplitude,
            "phase": phase
        }
        self.records_count += 1
        return True
    
    def insert_batch(self, records: List[Dict]) -> Dict:
        """Mock batch insert."""
        for record in records:
            self.insert_record(
                chunk_id=record.get("chunk_id", f"chunk_{len(self.store)}"),
                text=record.get("text", ""),
                amplitude=record.get("amplitude", []),
                phase=record.get("phase", [])
            )
        return {"inserted": len(records), "failed": 0}
    
    def search_wave(self, amplitude: List, phase: List, top_k: int = 3) -> List[Dict]:
        """Mock search - returns top records with realistic scores."""
        import random
        results = []
        
        # Return mock results with realistic scores
        for i, (chunk_id, record) in enumerate(list(self.store.items())[:top_k]):
            # Vary scores realistically (0.7-0.95)
            score = 0.73 + (i * 0.08) + random.uniform(-0.02, 0.05)
            score = min(0.99, max(0.70, score))
            
            results.append({
                "id": chunk_id,
                "text": record["text"],
                "score": round(score, 4)
            })
        
        return results
    
    def clear_store(self) -> bool:
        """Mock clear - empties storage."""
        self.store.clear()
        self.records_count = 0
        return True
    
    def get_stats(self) -> Dict:
        """Mock stats - returns store information."""
        return {
            "records_count": self.records_count,
            "status": "mock"
        }
    
    def close(self):
        """No-op for mock client."""
        pass
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support."""
        self.close()
