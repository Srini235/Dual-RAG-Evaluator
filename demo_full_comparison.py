#!/usr/bin/env python
"""
Dual Model Comparison: ChromaDB vs ResonanceDB
Generates detailed performance metrics and comparison statistics
"""
import sys
import numpy as np
from datetime import datetime
from typing import Dict, List
sys.path.insert(0, 'src')

from config import get_settings
from core import DocumentProcessor, BaselineRetriever, DualRAGEvaluator
from core.resonance_client import MockResonanceDBClient
from core.wave_mapper import query_to_wave

# Output handling
output_file = open('demo_comparison_results.txt', 'w', encoding='utf-8')

def log(msg):
    """Print to both console and file"""
    print(msg)
    output_file.write(msg + '\n')
    output_file.flush()

log('=' * 100)
log('EXTENDED NEGATION TEST: ChromaDB vs ResonanceDB Comparison')
log('21 Query Pairs Across 5 Test Categories')
log('=' * 100)
log(f'Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')

# Initialize
settings = get_settings()
doc_processor = DocumentProcessor()
baseline_retriever = BaselineRetriever()
resonance_client = MockResonanceDBClient()
evaluator = DualRAGEvaluator(baseline_retriever, resonance_client, doc_processor)

# Sample documents (15 total, 3 per category)
sample_docs = {
    'Basic Negations (5 queries)': [
        'Machine learning enables computers to learn from data without explicit programming.',
        'AI systems are not designed for every single task in the world.',
        'Neural networks cannot process information the same way as biological brains do.',
    ],
    'Multiple Negations (5 queries)': [
        'Deep learning models are not simple but they are not impossible to understand.',
        'The algorithm neither relies on labels nor requires human intervention.',
        'This approach does not exclude other methods and is not limited to one domain.',
    ],
    'Partial Negations (5 queries)': [
        'Some machine learning models require less data than others.',
        'Not all neural networks need the same computational resources.',
        'Few algorithms work without any preprocessing steps.',
    ],
    'Drug/Medication (5 queries)': [
        'Aspirin is not recommended for every patient though it helps many people.',
        'The medication does not cure the disease but can reduce symptoms.',
        'Treatment is not a silver bullet and cannot ignore other factors.',
    ],
    'Complex Scenarios (1 query)': [
        'While AI is not perfect, it is not useless either for complex analysis.',
        'The system cannot guarantee 100% accuracy and should not be trusted blindly.',
        'This technique is neither new nor completely obsolete in modern applications.',
    ]
}

# Flatten documents
all_docs = []
for category, docs in sample_docs.items():
    all_docs.extend(docs)

log(f'[INIT] Loading {len(all_docs)} sample documents...')

# Embed and store in both retrievers
embedded_docs = doc_processor.embed_chunks(all_docs)
embeddings_array = np.array(embedded_docs, dtype=np.float32)
baseline_retriever.insert(embeddings_array, all_docs)

# Also populate ResonanceDB with the same documents
for i, doc in enumerate(all_docs):
    embedding = embedded_docs[i]
    amplitude, phase = query_to_wave(embedding, doc)
    resonance_client.insert_record(
        chunk_id=f'doc_{i}',
        text=doc,
        amplitude=amplitude.tolist() if isinstance(amplitude, np.ndarray) else amplitude,
        phase=phase.tolist() if isinstance(phase, np.ndarray) else phase
    )

log(f'  [OK] Loaded {len(all_docs)} documents')
log(f'  [OK] Indexed in ChromaDB (cosine similarity)')
log(f'  [OK] Indexed in ResonanceDB (wave-based amplitudes)\n')

# Test queries
queries = [
    # Basic Negations
    ('What is machine learning?', 'Basic Negations'),
    ('Can systems learn without programming?', 'Basic Negations'),
    ('Are AI systems universal?', 'Basic Negations'),
    ('How do neural networks work differently?', 'Basic Negations'),
    ('Is explicit programming needed for AI?', 'Basic Negations'),
    
    # Multiple Negations
    ('Can deep learning be simple?', 'Multiple Negations'),
    ('Does the algorithm need labels?', 'Multiple Negations'),
    ('Is this approach exclusive?', 'Multiple Negations'),
    ('What methods are neither included nor excluded?', 'Multiple Negations'),
    ('Are limitations important to understand?', 'Multiple Negations'),
    
    # Partial Negations
    ('Which models need less data?', 'Partial Negations'),
    ('What computational resources are needed?', 'Partial Negations'),
    ('Do algorithms need preprocessing?', 'Partial Negations'),
    ('What constraints exist?', 'Partial Negations'),
    ('Are all systems equal in requirements?', 'Partial Negations'),
    
    # Drug/Medication
    ('When should aspirin not be used?', 'Drug/Medication'),
    ('What are medication limitations?', 'Drug/Medication'),
    ('Can treatment solve everything?', 'Drug/Medication'),
    ('What other factors matter?', 'Drug/Medication'),
    ('Is aspirin safe for everyone?', 'Drug/Medication'),
    
    # Complex Scenarios
    ('Is AI imperfect?', 'Complex Scenarios'),
]

log('[QUERIES] Running side-by-side comparison...')
log('=' * 100)

# Storage for analysis
comparison_data = []
category_stats = {}

for idx, (query, category) in enumerate(queries, 1):
    log(f'\n[QUERY {idx:2d}] "{query}"')
    log(f'         Category: {category}')
    log('-' * 100)
    
    # Embed query
    query_embedding = doc_processor.embed_chunks([query])[0]
    
    # ChromaDB retrieval
    baseline_results = baseline_retriever.retrieve(query_embedding, top_k=3)
    
    # ResonanceDB retrieval
    amplitude, phase = query_to_wave(query_embedding, query)
    resonance_results = resonance_client.search_wave(amplitude, phase, top_k=3)
    
    # Extract scores
    baseline_scores = [r.get('score', 0) for r in baseline_results]
    resonance_scores = [r.get('score', 0) for r in resonance_results]
    
    baseline_avg = np.mean(baseline_scores) if baseline_scores else 0
    resonance_avg = np.mean(resonance_scores) if resonance_scores else 0
    
    # Calculate improvement
    if baseline_avg != 0:
        improvement = ((resonance_avg - baseline_avg) / baseline_avg) * 100
    else:
        improvement = 0
    
    # Print results
    log(f'  ChromaDB Results:')
    for rank, result in enumerate(baseline_results, 1):
        text = result.get('text', 'N/A')[:65]
        score = result.get('score', 0)
        log(f'    [{rank}] {score:.4f} | {text}...')
    log(f'    AVG SCORE: {baseline_avg:.4f}')
    
    log(f'\n  ResonanceDB Results:')
    for rank, result in enumerate(resonance_results, 1):
        text = result.get('text', 'N/A')[:65]
        score = result.get('score', 0)
        log(f'    [{rank}] {score:.4f} | {text}...')
    log(f'    AVG SCORE: {resonance_avg:.4f}')
    
    log(f'\n  COMPARISON:')
    log(f'    ResonanceDB vs ChromaDB: {improvement:+.1f}%')
    
    # Track stats
    comparison_data.append({
        'query': query,
        'category': category,
        'chromadb_avg': baseline_avg,
        'resonancedb_avg': resonance_avg,
        'improvement': improvement
    })
    
    if category not in category_stats:
        category_stats[category] = []
    category_stats[category].append(improvement)

# Calculate summary statistics
log('\n' + '=' * 100)
log('COMPARISON SUMMARY STATISTICS')
log('=' * 100)

total_improvement = np.mean([d['improvement'] for d in comparison_data])
log(f'\nOverall Average Improvement (ResonanceDB vs ChromaDB): {total_improvement:+.1f}%')

log('\nImprovement by Category:')
for category in sorted(set(d['category'] for d in comparison_data)):
    improvements = [d['improvement'] for d in comparison_data if d['category'] == category]
    avg_improvement = np.mean(improvements)
    log(f'  {category:<30} {avg_improvement:+6.1f}%')

log('\n\nDetailed Query Results:')
log(f'{"Query":<50} {"ChromaDB":>12} {"ResonanceDB":>12} {"Improvement":>12}')
log('-' * 100)
for data in comparison_data:
    query_short = data['query'][:47] + '...' if len(data['query']) > 50 else data['query']
    log(f'{query_short:<50} {data["chromadb_avg"]:>11.4f} {data["resonancedb_avg"]:>12.4f} {data["improvement"]:>11.1f}%')

# Category winners
log('\n\nCategory Performance Analysis:')
log('-' * 100)
for category in sorted(category_stats.keys()):
    improvements = category_stats[category]
    better_queries = sum(1 for imp in improvements if imp > 0)
    log(f'{category:<30} ResonanceDB better in {better_queries}/{len(improvements)} queries')

log('\n' + '=' * 100)
log('[OK] SUCCESS! Comprehensive comparison generated.')
log('=' * 100)

output_file.close()
print(f'\n[OK] Full Report saved to: demo_comparison_results.txt')
