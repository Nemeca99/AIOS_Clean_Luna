#!/usr/bin/env python3
"""
Benchmark Embedder Performance
Compare LM Studio API vs Local SentenceTransformers with caching
"""

import sys
import time
import numpy as np
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

def benchmark_lm_studio_api():
    """Benchmark LM Studio API embeddings"""
    print("\n" + "="*60)
    print("BENCHMARKING: LM Studio API (Nomic v1.5)")
    print("="*60)
    
    import requests
    
    lm_studio_url = "http://localhost:1234"
    embedding_model = "nomic-ai/nomic-embed-text-v1.5-GGUF"
    
    test_texts = [
        "How do I optimize CARMA memory performance?",
        "Luna personality configuration and setup",
        "Audit system features and capabilities",
        "Dream consolidation process explained",
        "Fractal routing algorithm implementation"
    ]
    
    def get_embedding_api(text):
        response = requests.post(
            f"{lm_studio_url}/v1/embeddings",
            json={"input": text, "model": embedding_model},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return np.array(data['data'][0]['embedding'])
        return None
    
    # Warmup
    print("\n1. Warming up API...")
    start = time.perf_counter()
    _ = get_embedding_api("warmup")
    warmup_time = (time.perf_counter() - start) * 1000
    print(f"   Warmup: {warmup_time:.1f}ms")
    
    # Single embedding benchmark
    print("\n2. Single embedding test...")
    times = []
    for i, text in enumerate(test_texts, 1):
        start = time.perf_counter()
        embedding = get_embedding_api(text)
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        print(f"   Text {i}: {elapsed:.1f}ms (dim: {len(embedding) if embedding is not None else 0})")
    
    avg_time = np.mean(times)
    print(f"\n   Average: {avg_time:.1f}ms")
    print(f"   Min: {min(times):.1f}ms")
    print(f"   Max: {max(times):.1f}ms")
    
    # Batch test (sequential)
    print("\n3. Batch test (5 texts, sequential)...")
    start = time.perf_counter()
    embeddings = [get_embedding_api(text) for text in test_texts]
    batch_time = (time.perf_counter() - start) * 1000
    print(f"   Total: {batch_time:.1f}ms")
    print(f"   Per-text: {batch_time/len(test_texts):.1f}ms")
    
    return {
        'method': 'LM Studio API',
        'warmup_ms': warmup_time,
        'avg_single_ms': avg_time,
        'batch_total_ms': batch_time,
        'batch_per_text_ms': batch_time / len(test_texts)
    }

def benchmark_local_transformers():
    """Benchmark local SentenceTransformers"""
    print("\n" + "="*60)
    print("BENCHMARKING: Local SentenceTransformers")
    print("="*60)
    
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("   ERROR: sentence-transformers not installed")
        return None
    
    test_texts = [
        "How do I optimize CARMA memory performance?",
        "Luna personality configuration and setup",
        "Audit system features and capabilities",
        "Dream consolidation process explained",
        "Fractal routing algorithm implementation"
    ]
    
    # Load model
    print("\n1. Loading model...")
    start = time.perf_counter()
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight 384-dim model
    load_time = (time.perf_counter() - start) * 1000
    print(f"   Load time: {load_time:.1f}ms")
    
    # Warmup
    print("\n2. Warming up model...")
    start = time.perf_counter()
    _ = model.encode("warmup", convert_to_numpy=True)
    warmup_time = (time.perf_counter() - start) * 1000
    print(f"   Warmup: {warmup_time:.1f}ms")
    
    # Single embedding benchmark
    print("\n3. Single embedding test...")
    times = []
    for i, text in enumerate(test_texts, 1):
        start = time.perf_counter()
        embedding = model.encode(text, convert_to_numpy=True)
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        print(f"   Text {i}: {elapsed:.1f}ms (dim: {len(embedding)})")
    
    avg_time = np.mean(times)
    print(f"\n   Average: {avg_time:.1f}ms")
    print(f"   Min: {min(times):.1f}ms")
    print(f"   Max: {max(times):.1f}ms")
    
    # Batch test (true batching)
    print("\n4. Batch test (5 texts, batched)...")
    start = time.perf_counter()
    embeddings = model.encode(test_texts, convert_to_numpy=True, batch_size=5)
    batch_time = (time.perf_counter() - start) * 1000
    print(f"   Total: {batch_time:.1f}ms")
    print(f"   Per-text: {batch_time/len(test_texts):.1f}ms")
    
    return {
        'method': 'Local SentenceTransformers',
        'load_ms': load_time,
        'warmup_ms': warmup_time,
        'avg_single_ms': avg_time,
        'batch_total_ms': batch_time,
        'batch_per_text_ms': batch_time / len(test_texts)
    }

def benchmark_with_caching():
    """Benchmark cached embeddings"""
    print("\n" + "="*60)
    print("BENCHMARKING: Cached Embeddings (Pre-computed)")
    print("="*60)
    
    # Simulate cache
    cache = {}
    test_texts = [
        "How do I optimize CARMA memory performance?",
        "Luna personality configuration and setup",
        "Audit system features and capabilities",
        "Dream consolidation process explained",
        "Fractal routing algorithm implementation"
    ]
    
    # Pre-populate cache
    print("\n1. Pre-populating cache...")
    for text in test_texts:
        cache[text] = np.random.rand(768)  # Simulate embedding
    print(f"   Cached {len(cache)} embeddings")
    
    # Cache lookup benchmark
    print("\n2. Cache lookup test...")
    times = []
    for i, text in enumerate(test_texts, 1):
        start = time.perf_counter()
        embedding = cache.get(text)
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        print(f"   Text {i}: {elapsed:.4f}ms")
    
    avg_time = np.mean(times)
    print(f"\n   Average: {avg_time:.4f}ms")
    
    # Similarity calculation
    print("\n3. Similarity calculation test...")
    query_embedding = np.random.rand(768)
    times = []
    for i, text in enumerate(test_texts, 1):
        start = time.perf_counter()
        cached_embedding = cache[text]
        similarity = np.dot(query_embedding, cached_embedding)
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        print(f"   Text {i}: {elapsed:.4f}ms (similarity: {similarity:.3f})")
    
    avg_similarity_time = np.mean(times)
    print(f"\n   Average: {avg_similarity_time:.4f}ms")
    
    return {
        'method': 'Cached (Pre-computed)',
        'lookup_ms': avg_time,
        'similarity_ms': avg_similarity_time,
        'total_per_search_ms': avg_time + avg_similarity_time
    }

def main():
    """Run all benchmarks and compare"""
    print("\n" + "="*60)
    print("EMBEDDER PERFORMANCE BENCHMARK")
    print("="*60)
    
    results = []
    
    # Test LM Studio API
    try:
        api_result = benchmark_lm_studio_api()
        results.append(api_result)
    except Exception as e:
        print(f"\n   ERROR testing LM Studio API: {e}")
    
    # Test Local SentenceTransformers
    try:
        local_result = benchmark_local_transformers()
        if local_result:
            results.append(local_result)
    except Exception as e:
        print(f"\n   ERROR testing local transformers: {e}")
    
    # Test Caching
    try:
        cache_result = benchmark_with_caching()
        results.append(cache_result)
    except Exception as e:
        print(f"\n   ERROR testing caching: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY & RECOMMENDATIONS")
    print("="*60)
    
    for result in results:
        print(f"\n{result['method']}:")
        for key, value in result.items():
            if key != 'method':
                print(f"  {key:25s}: {value:8.2f}ms")
    
    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDATION:")
    print("="*60)
    
    if len(results) >= 2:
        api_time = results[0].get('avg_single_ms', 1000)
        
        if len(results) > 1 and 'avg_single_ms' in results[1]:
            local_time = results[1]['avg_single_ms']
            speedup = api_time / local_time
            
            print(f"\nLocal SentenceTransformers is {speedup:.1f}x FASTER than API")
            
            if speedup > 3:
                print("\n✅ RECOMMENDED: Use Local SentenceTransformers")
                print("   - 3x+ faster than API")
                print("   - Better batching support")
                print("   - No network overhead")
            else:
                print("\n⚖️  RECOMMENDED: Keep LM Studio API")
                print("   - Speed difference minimal")
                print("   - Simpler setup")
                print("   - Reuses loaded model")
        
        if len(results) > 2:
            cache_time = results[2].get('total_per_search_ms', 0.01)
            cache_speedup = api_time / cache_time
            
            print(f"\nCached lookups are {cache_speedup:.0f}x FASTER than API")
            print("\n✅ HIGHLY RECOMMENDED: Pre-compute & cache embeddings")
            print("   - 100-1000x faster for searches")
            print("   - One-time computation cost")
            print("   - Minimal disk space (~38MB for manual)")

if __name__ == "__main__":
    main()
