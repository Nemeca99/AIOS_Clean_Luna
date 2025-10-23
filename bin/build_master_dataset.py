#!/usr/bin/env python3
"""Build Luna's master training dataset from all available sources."""

import json
import random
from pathlib import Path
from typing import List, Dict

# Set seed for reproducibility
random.seed(42)

def load_wikipedia_samples(max_articles: int = 1000) -> List[Dict]:
    """Sample Wikipedia articles and create Q&A pairs."""
    examples = []
    wiki_base = Path("D:/Dataset/wikipedia_deduplicated")
    
    if not wiki_base.exists():
        print("⚠️ Wikipedia dataset not found")
        return []
    
    # Get all batches
    batches = sorted([b for b in wiki_base.iterdir() if b.is_dir()])
    
    articles_sampled = 0
    for batch in batches[:10]:  # Sample from first 10 batches
        articles = list(batch.glob("*.txt"))
        random.shuffle(articles)
        
        for article_path in articles[:100]:  # 100 from each batch
            if articles_sampled >= max_articles:
                break
                
            try:
                content = article_path.read_text(encoding='utf-8', errors='ignore')
                # Extract title from filename
                title = article_path.stem.split('_', 1)[1] if '_' in article_path.stem else article_path.stem
                title = title.replace('_', ' ')
                
                # Skip very short articles
                if len(content) < 100:
                    continue
                
                # Create Q&A from first paragraph
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                if paragraphs:
                    first_para = paragraphs[0][:500]  # First 500 chars
                    examples.append({
                        "prompt": f"What is {title}?",
                        "response": first_para
                    })
                    articles_sampled += 1
                    
            except Exception as e:
                continue
        
        if articles_sampled >= max_articles:
            break
    
    print(f"✅ Loaded {len(examples)} Wikipedia samples")
    return examples

def load_advanced_ai_knowledge() -> List[Dict]:
    """Load advanced AI knowledge markdown files."""
    examples = []
    ai_base = Path("D:/Shadow_Broker/datasets/advanced_ai_knowledge")
    
    if not ai_base.exists():
        print("⚠️ Advanced AI knowledge not found")
        return []
    
    for md_file in ai_base.glob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8', errors='ignore')
            topic = md_file.stem.replace('_', ' ').title()
            
            # Extract sections
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('##'):
                    section = line.replace('##', '').strip()
                    # Get next few lines as content
                    section_content = []
                    for j in range(i+1, min(i+10, len(lines))):
                        if lines[j].startswith('#'):
                            break
                        if lines[j].strip():
                            section_content.append(lines[j].strip())
                    
                    if section_content:
                        examples.append({
                            "prompt": f"Explain {section}",
                            "response": ' '.join(section_content)[:500]
                        })
        except Exception as e:
            continue
    
    print(f"✅ Loaded {len(examples)} advanced AI examples")
    return examples

def load_huggingface_datasets() -> List[Dict]:
    """Load pre-made HuggingFace datasets."""
    examples = []
    hf_base = Path("D:/Shadow_Broker/datasets/hugging_face")
    
    if not hf_base.exists():
        print("⚠️ HuggingFace datasets not found")
        return []
    
    # Check for JSONL files in subdirectories
    for dataset_dir in hf_base.iterdir():
        if not dataset_dir.is_dir():
            continue
        
        for jsonl_file in dataset_dir.rglob("*.jsonl"):
            try:
                with open(jsonl_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            # Try common HF formats
                            if 'prompt' in data and 'response' in data:
                                examples.append(data)
                            elif 'question' in data and 'answer' in data:
                                examples.append({
                                    "prompt": data['question'],
                                    "response": data['answer']
                                })
                            elif 'input' in data and 'output' in data:
                                examples.append({
                                    "prompt": data['input'],
                                    "response": data['output']
                                })
                        except:
                            continue
            except Exception as e:
                continue
        
        # Also check for parquet files
        for parquet_file in dataset_dir.rglob("*.parquet"):
            # We'd need pandas/pyarrow for this, skip for now
            pass
    
    print(f"✅ Loaded {len(examples)} HuggingFace examples")
    return examples[:500]  # Limit to 500

def load_aios_knowledge() -> List[Dict]:
    """Load AIOS-specific knowledge."""
    aios_file = Path("infra_core/unsloth_integration/data/aios_knowledge.jsonl")
    examples = []
    
    if aios_file.exists():
        with open(aios_file, 'r', encoding='utf-8') as f:
            for line in f:
                examples.append(json.loads(line))
    
    print(f"✅ Loaded {len(examples)} AIOS examples")
    return examples

def load_current_training() -> List[Dict]:
    """Load current training data."""
    current_file = Path("infra_core/unsloth_integration/data/train.jsonl")
    examples = []
    
    if current_file.exists():
        with open(current_file, 'r', encoding='utf-8') as f:
            for line in f:
                examples.append(json.loads(line))
    
    print(f"✅ Loaded {len(examples)} current training examples")
    return examples

def deduplicate(examples: List[Dict]) -> List[Dict]:
    """Remove duplicate prompts."""
    seen = set()
    unique = []
    
    for ex in examples:
        prompt_lower = ex['prompt'].lower().strip()
        if prompt_lower not in seen:
            seen.add(prompt_lower)
            unique.append(ex)
    
    print(f"✅ Deduplicated: {len(examples)} → {len(unique)}")
    return unique

def main():
    print("\n" + "="*60)
    print("BUILDING LUNA'S MASTER TRAINING DATASET")
    print("="*60 + "\n")
    
    all_examples = []
    
    # Load from all sources
    print("📚 Loading data sources...\n")
    all_examples.extend(load_aios_knowledge())
    all_examples.extend(load_current_training())
    all_examples.extend(load_advanced_ai_knowledge())
    all_examples.extend(load_wikipedia_samples(max_articles=2000))
    all_examples.extend(load_huggingface_datasets())
    
    print(f"\n📊 Total raw examples: {len(all_examples)}")
    
    # Deduplicate
    all_examples = deduplicate(all_examples)
    
    # Shuffle
    random.shuffle(all_examples)
    
    # Filter out empty or too short
    all_examples = [
        ex for ex in all_examples
        if ex.get('prompt') and ex.get('response')
        and len(ex['prompt']) > 5
        and len(ex['response']) > 10
    ]
    
    print(f"📊 After filtering: {len(all_examples)}")
    
    # Save master dataset
    output = Path("infra_core/unsloth_integration/data/train.jsonl")
    with open(output, 'w', encoding='utf-8') as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')
    
    print(f"\n✅ Master dataset saved: {output}")
    print(f"📊 Total examples: {len(all_examples)}")
    
    # Show sample
    print("\n" + "="*60)
    print("SAMPLE EXAMPLES")
    print("="*60)
    for i, ex in enumerate(random.sample(all_examples, min(5, len(all_examples)))):
        print(f"\n[{i+1}] Q: {ex['prompt'][:80]}...")
        print(f"    A: {ex['response'][:80]}...")

if __name__ == "__main__":
    main()

