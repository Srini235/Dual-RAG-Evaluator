"""
Wave Mapper Module - Convert embeddings to amplitude and phase representation
"""

import numpy as np
import math
from typing import List, Tuple

# Configuration
NEGATION_WORDS = {
    "not", "never", "unless", "contraindicated",
    "no", "none", "without", "absence", "lack",
    "absent", "negative", "fail", "cannot", "cant",
    "shouldn't", "shouldn't", "wont", "won't"
}


def vector_to_wave(
    vector: np.ndarray,
    text: str,
    seed: int = None
) -> Tuple[List[float], List[float]]:
    """
    Convert a base embedding vector to amplitude and phase representation.
    
    This implements a heuristic mapping for POC:
    - Amplitude: Normalized absolute values of the base vector
    - Phase: Random values in [-π, π], with heuristic for negation words
    
    Args:
        vector: 1D numpy array of floats (shape: (embedding_dim,))
        text: Associated text (used for negation heuristic)
        seed: Optional random seed for reproducibility (for testing)
    
    Returns:
        Tuple of (amplitude_list, phase_list)
        - amplitude_list: List of floats in range [0, 1]
        - phase_list: List of floats in range [-π, π]
    
    Raises:
        ValueError: If vector is not 1D
        Exception: If amplitude/phase generation fails
    
    Heuristic Details:
        - Negation Detection: If text contains negation words, phase is shifted by π
          This simulates destructive interference in wave-based retrieval
        - Amplitude: |vector| / max(|vector|)
        - Phase: Uniformly random in [-π, π], optionally shifted by π for negation
    
    Example:
        >>> vector = np.array([0.1, 0.45, 0.67, ...])
        >>> text = "This is never false"
        >>> amplitude, phase = vector_to_wave(vector, text)
        >>> print(len(amplitude), len(phase))
        384 384
    """
    if vector.ndim != 1:
        raise ValueError(f"vector must be 1D, got shape {vector.shape}")
    
    try:
        # Amplitude: normalized absolute values
        amplitude = np.abs(vector)
        max_amp = np.max(amplitude)
        if max_amp > 0:
            amplitude = amplitude / max_amp
        else:
            amplitude = np.zeros_like(amplitude)
        
        # Phase: random in [-π, π]
        if seed is not None:
            np.random.seed(seed)
        
        phase = np.random.uniform(-math.pi, math.pi, size=vector.shape[0])
        
        # Heuristic: detect negation in text
        text_lower = text.lower()
        has_negation = any(word in text_lower for word in NEGATION_WORDS)
        
        if has_negation:
            # Shift phase by π (destructive interference)
            phase = (phase + math.pi) % (2 * math.pi)
            # Map back to [-π, π]
            phase = np.where(phase > math.pi, phase - 2 * math.pi, phase)
        
        # Convert to lists for JSON serialization
        amplitude_list = amplitude.tolist()
        phase_list = phase.tolist()
        
        return amplitude_list, phase_list
    
    except Exception as e:
        raise Exception(f"Failed to convert vector to wave: {e}")


def query_to_wave(
    embedding: np.ndarray,
    query_text: str = None,
    seed: int = None
) -> Tuple[List[float], List[float]]:
    """
    Convert query embedding to amplitude and phase.
    
    Args:
        embedding: 1D numpy array (e.g., from embedding model)
        query_text: Optional query text for negation heuristic
        seed: Optional random seed for reproducibility
    
    Returns:
        Tuple of (amplitude_list, phase_list)
    
    Note:
        Same logic as vector_to_wave. Separate function for clarity.
    """
    query_text = query_text or ""
    return vector_to_wave(embedding, query_text, seed=seed)


def batch_vector_to_wave(
    vectors: np.ndarray,
    texts: List[str],
    seed: int = None
) -> Tuple[List[List[float]], List[List[float]]]:
    """
    Convert multiple vectors to amplitude/phase in batch.
    
    Args:
        vectors: (N, embedding_dim) array of float32
        texts: List of N text strings (for negation heuristic)
        seed: Optional random seed
    
    Returns:
        Tuple of (amplitude_batch, phase_batch)
        - amplitude_batch: List of N amplitude lists
        - phase_batch: List of N phase lists
    
    Raises:
        ValueError: If vectors and texts have mismatched lengths
    
    Example:
        >>> vectors = np.random.randn(10, 384).astype(np.float32)
        >>> texts = ["chunk_" + str(i) for i in range(10)]
        >>> amps, phases = batch_vector_to_wave(vectors, texts)
        >>> len(amps), len(phases)
        (10, 10)
    """
    if len(vectors) != len(texts):
        raise ValueError(
            f"vectors and texts must have same length: "
            f"got {len(vectors)} vectors, {len(texts)} texts"
        )
    
    amplitude_batch = []
    phase_batch = []
    
    for vector, text in zip(vectors, texts):
        amp, phase = vector_to_wave(vector, text, seed=seed)
        amplitude_batch.append(amp)
        phase_batch.append(phase)
    
    return amplitude_batch, phase_batch


def validate_wave_pattern(
    amplitude: List[float],
    phase: List[float],
    expected_dim: int = 384
) -> bool:
    """
    Validate that amplitude and phase have correct dimensions.
    
    Args:
        amplitude: List of amplitude values
        phase: List of phase values
        expected_dim: Expected dimension (default 384)
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If dimensions don't match or values out of range
    """
    # Check lengths
    if len(amplitude) != expected_dim:
        raise ValueError(
            f"amplitude dimension mismatch: expected {expected_dim}, got {len(amplitude)}"
        )
    
    if len(phase) != expected_dim:
        raise ValueError(
            f"phase dimension mismatch: expected {expected_dim}, got {len(phase)}"
        )
    
    # Check value ranges
    amp_array = np.array(amplitude)
    phase_array = np.array(phase)
    
    if np.any(amp_array < -0.01) or np.any(amp_array > 1.01):
        print(f"WARNING: amplitude values out of expected range [0, 1]:")
        print(f"  min: {np.min(amp_array):.4f}, max: {np.max(amp_array):.4f}")
    
    if np.any(phase_array < -math.pi - 0.01) or np.any(phase_array > math.pi + 0.01):
        print(f"WARNING: phase values out of expected range [-π, π]:")
        print(f"  min: {np.min(phase_array):.4f}, max: {np.max(phase_array):.4f}")
    
    return True


def detect_negation(text: str) -> bool:
    """
    Check if text contains negation words.
    
    Args:
        text: Input text
    
    Returns:
        True if negation detected
    """
    text_lower = text.lower()
    return any(word in text_lower for word in NEGATION_WORDS)


def get_negation_words() -> set:
    """
    Get set of negation words used in heuristic.
    
    Returns:
        Set of negation keywords
    """
    return NEGATION_WORDS.copy()


class WaveMapper:
    """
    Wave mapping functionality wrapper.
    
    Provides methods for converting embeddings to wave representations
    and handling wave-based retrieval operations.
    """
    
    @staticmethod
    def vector_to_wave(
        vector: np.ndarray,
        text: str,
        seed: int = None
    ) -> Tuple[List[float], List[float]]:
        """Convert a vector to amplitude and phase representation."""
        return vector_to_wave(vector, text, seed)
    
    @staticmethod
    def query_to_wave(
        query: str,
        embedding_fn: callable,
        seed: int = None
    ) -> Tuple[List[float], List[float]]:
        """Convert a query to amplitude and phase representation."""
        return query_to_wave(query, embedding_fn, seed)
    
    @staticmethod
    def batch_vector_to_wave(
        vectors: List[np.ndarray],
        texts: List[str],
        seed: int = None
    ) -> Tuple[List[List[float]], List[List[float]]]:
        """Convert multiple vectors to wave representations."""
        return batch_vector_to_wave(vectors, texts, seed)
    
    @staticmethod
    def validate_wave_pattern(
        amplitude: List[float],
        phase: List[float]
    ) -> bool:
        """Validate a wave pattern."""
        return validate_wave_pattern(amplitude, phase)
    
    @staticmethod
    def detect_negation(text: str) -> bool:
        """Detect if text contains negation words."""
        return detect_negation(text)
    
    @staticmethod
    def get_negation_words() -> set:
        """Get set of negation words."""
        return get_negation_words()
