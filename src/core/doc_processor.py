"""
Document Processor Module - Load, chunk, and embed documents
"""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

# Configuration Constants
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


class DocumentProcessor:
    """Load, chunk, and embed documents using sentence transformers."""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize the embedding model.
        
        Args:
            model_name: HuggingFace model identifier
            
        Raises:
            Exception: If model fails to load
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            print(f"[OK] Loaded embedding model: {model_name} (dim={self.embedding_dim})")
        except Exception as e:
            print(f"ERROR: Failed to load embedding model: {e}")
            raise
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = CHUNK_SIZE,
        overlap: int = CHUNK_OVERLAP
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Full document text
            chunk_size: Target chunk size in characters
            overlap: Number of overlapping characters between chunks
        
        Returns:
            List of text chunks
            
        Note:
            Uses basic character-based chunking. For production,
            consider sentence-aware or semantic chunking.
        """
        if not text or len(text) == 0:
            print("WARNING: Empty text provided to chunk_text()")
            return []
        
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            # Calculate end position
            end = min(start + chunk_size, text_len)
            
            # Extract chunk
            chunk = text[start:end]
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)
            
            # Move start position forward
            start = end - overlap
            
            # Avoid infinite loop on very small text
            if end == text_len:
                break
        
        return chunks
    
    def embed_chunks(self, chunks: List[str]) -> np.ndarray:
        """
        Generate embeddings for text chunks.
        
        Args:
            chunks: List of text strings to embed
        
        Returns:
            numpy array of shape (num_chunks, embedding_dim) with dtype float32
            
        Raises:
            ValueError: If chunks list is empty
        """
        if not chunks or len(chunks) == 0:
            raise ValueError("Cannot embed empty chunks list")
        
        try:
            embeddings = self.model.encode(chunks, convert_to_numpy=True)
            embeddings = embeddings.astype(np.float32)
            print(f"[OK] Generated embeddings for {len(chunks)} chunks (shape: {embeddings.shape})")
            return embeddings
        except Exception as e:
            print(f"ERROR: Failed to generate embeddings: {e}")
            raise
    
    def process_text(
        self,
        text: str,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP
    ) -> tuple[List[str], np.ndarray]:
        """
        End-to-end processing: chunk text and generate embeddings.
        
        Args:
            text: Full document text
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
        
        Returns:
            Tuple of (chunks, embeddings)
            - chunks: List of text chunks
            - embeddings: (num_chunks, embedding_dim) numpy array
            
        Example:
            >>> processor = DocumentProcessor()
            >>> text = "Long document text..."
            >>> chunks, embeddings = processor.process_text(text)
            >>> print(embeddings.shape)
            (42, 384)
        """
        print(f"\n[Processing] Chunking text (size={chunk_size}, overlap={chunk_overlap})...")
        chunks = self.chunk_text(text, chunk_size=chunk_size, overlap=chunk_overlap)
        print(f"  → Generated {len(chunks)} chunks")
        
        print(f"[Processing] Generating embeddings...")
        embeddings = self.embed_chunks(chunks)
        
        return chunks, embeddings
    
    def load_from_text_file(self, file_path: str) -> str:
        """
        Load text from a file.
        
        Args:
            file_path: Path to text file
        
        Returns:
            Text content
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If file read fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"[OK] Loaded text from {file_path} ({len(text)} chars)")
            return text
        except FileNotFoundError:
            print(f"ERROR: File not found: {file_path}")
            raise
        except Exception as e:
            print(f"ERROR: Failed to read file {file_path}: {e}")
            raise
    
    def load_from_pdf(self, file_path: str) -> str:
        """
        Load text from a PDF file.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Extracted text content
            
        Raises:
            ImportError: If PyPDF2 not installed
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF parsing fails
            
        Note:
            Requires PyPDF2 to be installed.
            For complex PDFs, consider using pdfplumber or langchain.
        """
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")
        
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            
            print(f"[OK] Loaded PDF from {file_path} ({len(text)} chars, {len(reader.pages)} pages)")
            return text
        except FileNotFoundError:
            print(f"ERROR: PDF file not found: {file_path}")
            raise
        except Exception as e:
            print(f"ERROR: Failed to parse PDF {file_path}: {e}")
            raise
    
    @staticmethod
    def get_sample_chunks() -> List[str]:
        """
        Return hardcoded sample chunks for quick testing.
        
        Returns:
            List of 6 realistic medical text chunks
            
        Note:
            Useful for rapid prototyping without file I/O or model loading delays.
        """
        return [
            "Chronic Kidney Disease (CKD) is a condition characterized by gradual loss of kidney function. The kidneys filter waste and excess water from the blood to form urine. When kidney function declines, waste accumulates in the body, which can lead to serious health problems.",
            
            "CKD is classified into five stages based on estimated glomerular filtration rate (eGFR). Stage 1: eGFR ≥ 90 mL/min/1.73m² with kidney damage. Stage 2: eGFR 60-89 mL/min/1.73m² with mild decrease in kidney function and kidney damage.",
            
            "Hypertension is the second leading cause of CKD, accounting for about 25-30% of cases. Long-term high blood pressure damages nephrons and reduces kidney function. Blood pressure control is essential in slowing the progression of kidney disease.",
            
            "Proteinuria or albuminuria is the presence of protein in the urine and is a key marker of kidney damage. It indicates glomerular injury and is associated with faster CKD progression. An albumin-to-creatinine ratio greater than 30 mg/g is considered significant.",
            
            "Diabetes is the leading cause of kidney disease, accounting for approximately 35-40% of CKD cases. Diabetic nephropathy develops in about 20-40% of patients with diabetes. High blood glucose levels damage the small blood vessels in the kidneys.",
            
            "ACE inhibitors and ARBs are first-line medications for CKD patients, especially those with hypertension or diabetes, as they provide renal protection beyond blood pressure reduction by reducing glomerular pressure and proteinuria."
        ]
