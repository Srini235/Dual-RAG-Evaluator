"""
Baseline Retriever Module - ChromaDB vector similarity search
"""

from typing import List, Dict
import chromadb
import numpy as np


class BaselineRetriever:
    """
    In-memory ChromaDB store with cosine similarity retrieval.
    
    This serves as the baseline for comparing against ResonanceDB's
    wave-based retrieval.
    """
    
    def __init__(self, embeddings: np.ndarray = None, texts: List[str] = None):
        """
        Initialize ChromaDB client and optionally pre-populate with data.
        
        Args:
            embeddings: Optional (N, embedding_dim) array of float32
            texts: Optional list of N text chunks
            
        Example:
            >>> embeddings = np.random.randn(10, 384).astype(np.float32)
            >>> texts = ["chunk1", "chunk2", ...]
            >>> retriever = BaselineRetriever(embeddings, texts)
        """
        try:
            self.client = chromadb.EphemeralClient()
            self.collection = self.client.create_collection(
                name="baseline_chunks",
                metadata={"hnsw:space": "cosine"}
            )
            print("[OK] Initialized ChromaDB (in-memory)")
        except Exception as e:
            print(f"ERROR: Failed to initialize ChromaDB: {e}")
            raise
        
        if embeddings is not None and texts is not None:
            self.insert(embeddings, texts)
    
    def insert(self, embeddings: np.ndarray, texts: List[str]) -> None:
        """
        Store embeddings and text chunks in ChromaDB.
        
        Args:
            embeddings: (N, embedding_dim) array of float32 values
            texts: List of N text strings
            
        Raises:
            ValueError: If embeddings and texts have mismatched lengths
            Exception: If insertion fails
            
        Note:
            ChromaDB requires embeddings as nested lists (will auto-convert).
        """
        if len(embeddings) != len(texts):
            raise ValueError(
                f"Embeddings and texts must have same length: "
                f"got {len(embeddings)} embeddings, {len(texts)} texts"
            )
        
        try:
            # Generate IDs for chunks
            ids = [f"chunk_{i:04d}" for i in range(len(texts))]
            
            # Convert embeddings to lists (ChromaDB requirement)
            embedding_lists = embeddings.tolist()
            
            # Insert into ChromaDB
            self.collection.add(
                ids=ids,
                embeddings=embedding_lists,
                metadatas=[{"text": text} for text in texts],
                documents=texts
            )
            print(f"[OK] Inserted {len(texts)} chunks into ChromaDB")
        except Exception as e:
            print(f"ERROR: Failed to insert chunks: {e}")
            raise
    
    def retrieve(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top_k similar chunks using cosine similarity.
        
        Args:
            query_embedding: 1D array of shape (embedding_dim,) with float32 values
            top_k: Number of results to return (default: 3)
        
        Returns:
            List of dicts with keys:
            - chunk_id: str (e.g., "chunk_0000")
            - text: str (the document chunk)
            - score: float (similarity score in range [0, 1])
            
        Raises:
            ValueError: If query_embedding has wrong shape
            Exception: If query fails
            
        Example:
            >>> query_vec = np.random.randn(384).astype(np.float32)
            >>> results = retriever.retrieve(query_vec, top_k=3)
            >>> for r in results:
            ...     print(f"{r['chunk_id']}: {r['score']:.4f}")
        """
        if query_embedding.ndim != 1:
            raise ValueError(
                f"query_embedding must be 1D, got shape {query_embedding.shape}"
            )
        
        try:
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )
            
            # Parse results
            output = []
            
            # ChromaDB returns nested lists for single query
            ids = results["ids"][0] if results["ids"] else []
            distances = results["distances"][0] if results["distances"] else []
            documents = results["documents"][0] if results["documents"] else []
            
            for idx, (chunk_id, distance, text) in enumerate(
                zip(ids, distances, documents)
            ):
                # ChromaDB cosine distance is 1 - cosine_similarity
                # Convert back to similarity score [0, 1]
                score = 1.0 - distance
                
                output.append({
                    "chunk_id": chunk_id,
                    "text": text,
                    "score": float(max(0.0, score))  # Clamp to [0, 1]
                })
            
            return output
        except Exception as e:
            print(f"ERROR: Query failed: {e}")
            raise
    
    def clear(self) -> None:
        """
        Delete all records from the store.
        
        Note:
            This recreates the collection, which is a simple way to clear.
        """
        try:
            self.client.delete_collection(name="baseline_chunks")
            self.collection = self.client.create_collection(
                name="baseline_chunks",
                metadata={"hnsw:space": "cosine"}
            )
            print("[OK] Cleared ChromaDB store")
        except Exception as e:
            print(f"ERROR: Failed to clear store: {e}")
            raise
    
    def get_collection_count(self) -> int:
        """
        Get number of records in the collection.
        
        Returns:
            Number of stored chunks
        """
        try:
            return self.collection.count()
        except Exception as e:
            print(f"ERROR: Failed to get collection count: {e}")
            return 0
