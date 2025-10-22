#!/usr/bin/env python3
"""
Creative Corpus Seeding Script
Generates synthetic creative samples using dolphin-mistral-24b

V5.1 CreativeRAG Integration
Travis Miner | AIOS_clean
"""

import sys
import time
import json
import requests
from pathlib import Path
from typing import Dict, Optional

# Add AIOS root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import data_core for persistence
from data_core.data_core_unified import DataCore

# Creative taxonomy for diverse corpus
TAXONOMY = {
    "genres": [
        "dark fantasy", "sci-fi noir", "folklore", "cosmic horror",
        "urban fantasy", "post-apocalyptic", "magical realism", "cyberpunk"
    ],
    "moods": [
        "haunting", "whimsical", "tense", "dreamlike",
        "melancholic", "eerie", "hopeful", "surreal"
    ],
    "lengths": [
        "micro (50-100 words)",
        "flash (100-200 words)"
    ]
}


def generate_sample(genre: str, mood: str, length: str, model: str, lm_studio_url: str) -> Optional[Dict]:
    """
    Generate one creative sample using dolphin-mistral-24b
    
    Args:
        genre: Creative genre
        mood: Emotional tone
        length: Target length specification
        model: LM Studio model name
        lm_studio_url: LM Studio base URL
    
    Returns:
        Sample dict or None if generation failed
    """
    prompt = f"Write a {mood} {genre} {length} story. Be creative and vivid."
    
    try:
        resp = requests.post(
            f"{lm_studio_url}/v1/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.9,
                "max_tokens": 350,
                "top_p": 0.95
            },
            timeout=90
        )
        
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            return {
                "prompt": {"genre": genre, "mood": mood, "length": length},
                "content": content.strip(),
                "model": model,
                "timestamp": time.time()
            }
        else:
            print(f"  [HTTP {resp.status_code}] Failed for {genre} x {mood}")
            
    except requests.exceptions.Timeout:
        print(f"  [TIMEOUT] {genre} x {mood}")
    except Exception as e:
        print(f"  [ERROR] {genre} x {mood}: {e}")
    
    return None


def main():
    """Seed creative corpus with synthetic samples"""
    print("="*60)
    print("Creative Corpus Seeding - dolphin-mistral-24b")
    print("="*60)
    
    # Initialize data_core
    dc = DataCore()
    cfg = dc.load_config()
    cm = cfg.get("creative_mode", {})
    
    model = cm.get("model", "cognitivecomputations_dolphin-mistral-24b-venice-edition")
    lm_studio_url = "http://localhost:1234"
    
    total_target = len(TAXONOMY['genres']) * len(TAXONOMY['moods']) * len(TAXONOMY['lengths'])
    count = 0
    failed = 0
    
    print(f"\nModel: {model}")
    print(f"Target: {total_target} samples")
    print(f"Taxonomy: {len(TAXONOMY['genres'])} genres x {len(TAXONOMY['moods'])} moods x {len(TAXONOMY['lengths'])} lengths")
    print()
    
    start_time = time.time()
    
    for genre in TAXONOMY["genres"]:
        for mood in TAXONOMY["moods"]:
            for length in TAXONOMY["lengths"]:
                sample = generate_sample(genre, mood, length, model, lm_studio_url)
                
                if sample:
                    dc.record_creative_sample(sample)
                    count += 1
                    print(f"[{count}/{total_target}] {genre} x {mood} x {length}")
                else:
                    failed += 1
                    print(f"[FAIL {failed}] {genre} x {mood} x {length}")
                
                time.sleep(0.5)  # Rate limit (auditor requirement - no API spam)
    
    elapsed = time.time() - start_time
    
    print()
    print("="*60)
    print("CORPUS SEEDING COMPLETE")
    print("="*60)
    print(f"\nGenerated: {count} samples")
    print(f"Failed: {failed} samples")
    print(f"Success rate: {count / total_target * 100:.1f}%")
    print(f"Time: {elapsed / 60:.1f} minutes")
    
    paths = dc.creative_paths()
    print(f"\nStored in: {paths['raw_dir']}/creative_samples.jsonl")
    print(f"\nNext steps:")
    print("  1. Run Dream compression job:")
    print("     python -c \"from dream_core.dream_core import DreamCore; from data_core.data_core_unified import DataCore; dc=DataCore(); d=DreamCore(); print(d.run_creative_compression(dc))\"")
    print("  2. Enable creative_mode in config:")
    print("     Set creative_mode.enabled = true in data_core/config/aios_config.json")
    print("  3. Test creative generation:")
    print("     python luna_chat.py \"#creative write a dark fairy tale\"")


if __name__ == "__main__":
    main()

