#!/usr/bin/env python3
"""Extract ALL chatlogs from Travis's personal datasets."""

import json
import random
import re
from pathlib import Path
from typing import List, Dict

random.seed(42)

def extract_from_markdown(file_path: Path) -> List[Dict]:
    """Extract Q&A from markdown files."""
    examples = []
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        # Pattern 1: **User:** ... **Assistant:**
        pattern1 = r'\*\*(?:User|Travis|Human):\*\*\s*(.*?)\s*\*\*(?:Assistant|AI|Luna|Lyra|Nova):\*\*\s*(.*?)(?=\*\*(?:User|Travis|Human):\*\*|\Z)'
        matches = re.findall(pattern1, content, re.DOTALL | re.IGNORECASE)
        for user, assistant in matches:
            user = user.strip()[:2000]
            assistant = assistant.strip()[:2000]
            if len(user) > 10 and len(assistant) > 10:
                examples.append({"prompt": user, "response": assistant})
        
        # Pattern 2: User: ... \n Assistant:
        pattern2 = r'(?:^|\n)(?:User|Travis|Human):\s*(.*?)\s*(?:^|\n)(?:Assistant|AI|Luna|Lyra|Nova):\s*(.*?)(?=(?:^|\n)(?:User|Travis|Human):|\Z)'
        matches = re.findall(pattern2, content, re.DOTALL | re.IGNORECASE)
        for user, assistant in matches:
            user = user.strip()[:2000]
            assistant = assistant.strip()[:2000]
            if len(user) > 10 and len(assistant) > 10:
                examples.append({"prompt": user, "response": assistant})
        
        # Pattern 3: ## User ... ## Assistant
        pattern3 = r'##\s*(?:User|Travis|Human)[^\n]*\n(.*?)\n##\s*(?:Assistant|AI|Luna|Lyra|Nova)[^\n]*\n(.*?)(?=\n##|\Z)'
        matches = re.findall(pattern3, content, re.DOTALL | re.IGNORECASE)
        for user, assistant in matches:
            user = user.strip()[:2000]
            assistant = assistant.strip()[:2000]
            if len(user) > 10 and len(assistant) > 10:
                examples.append({"prompt": user, "response": assistant})
                
    except Exception as e:
        pass
    
    return examples

def extract_from_txt(file_path: Path) -> List[Dict]:
    """Extract Q&A from text files."""
    examples = []
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        # Try JSON lines first
        if '{' in content and '"' in content:
            for line in content.split('\n'):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if isinstance(data, dict):
                        # Common formats
                        if 'prompt' in data and 'response' in data:
                            examples.append({"prompt": str(data['prompt'])[:2000], "response": str(data['response'])[:2000]})
                        elif 'user' in data and 'assistant' in data:
                            examples.append({"prompt": str(data['user'])[:2000], "response": str(data['assistant'])[:2000]})
                        elif 'question' in data and 'answer' in data:
                            examples.append({"prompt": str(data['question'])[:2000], "response": str(data['answer'])[:2000]})
                except:
                    pass
        
        # Pattern matching for plain text
        # Pattern: "Q: ... A: ..."
        pattern1 = r'Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|\Z)'
        matches = re.findall(pattern1, content, re.DOTALL | re.IGNORECASE)
        for q, a in matches:
            q = q.strip()[:2000]
            a = a.strip()[:2000]
            if len(q) > 10 and len(a) > 10:
                examples.append({"prompt": q, "response": a})
        
        # Pattern: "You: ... AI: ..."
        pattern2 = r'(?:You|Travis|Human):\s*(.*?)\s*(?:AI|Assistant|Luna|Lyra|Nova):\s*(.*?)(?=(?:You|Travis|Human):|\Z)'
        matches = re.findall(pattern2, content, re.DOTALL | re.IGNORECASE)
        for user, ai in matches:
            user = user.strip()[:2000]
            ai = ai.strip()[:2000]
            if len(user) > 10 and len(ai) > 10:
                examples.append({"prompt": user, "response": ai})
                
    except Exception as e:
        pass
    
    return examples

def main():
    print("\n" + "="*60)
    print("EXTRACTING ALL TRAVIS CHATLOGS")
    print("="*60 + "\n")
    
    personal_base = Path("D:/Shadow_Broker/datasets/personal")
    
    if not personal_base.exists():
        print("❌ Personal datasets not found!")
        return
    
    all_examples = []
    files_processed = 0
    
    # Process markdown files
    print("📄 Processing markdown files...")
    md_files = list(personal_base.rglob("*.md"))
    print(f"   Found {len(md_files)} markdown files")
    
    for md_file in md_files:
        # Skip very large files (> 50MB) to avoid memory issues
        if md_file.stat().st_size > 50_000_000:
            print(f"   ⚠️ Skipping {md_file.name} (too large: {md_file.stat().st_size / 1024 / 1024:.1f} MB)")
            continue
        
        examples = extract_from_markdown(md_file)
        if examples:
            all_examples.extend(examples)
            files_processed += 1
            if files_processed % 10 == 0:
                print(f"   Processed {files_processed} files, {len(all_examples)} examples so far...")
    
    print(f"   ✅ Extracted {len(all_examples)} examples from markdown")
    
    # Process text files
    print("\n📄 Processing text files...")
    txt_files = list(personal_base.rglob("*.txt"))
    print(f"   Found {len(txt_files)} text files")
    
    txt_examples_start = len(all_examples)
    for txt_file in txt_files:
        # Skip very large files (> 50MB)
        if txt_file.stat().st_size > 50_000_000:
            print(f"   ⚠️ Skipping {txt_file.name} (too large: {txt_file.stat().st_size / 1024 / 1024:.1f} MB)")
            continue
        
        examples = extract_from_txt(txt_file)
        if examples:
            all_examples.extend(examples)
            files_processed += 1
            if files_processed % 10 == 0:
                print(f"   Processed {files_processed} total files, {len(all_examples)} examples so far...")
    
    print(f"   ✅ Extracted {len(all_examples) - txt_examples_start} examples from text files")
    
    print(f"\n📊 Total raw examples: {len(all_examples)}")
    
    # Deduplicate
    print("\n🔄 Deduplicating...")
    seen = set()
    unique = []
    for ex in all_examples:
        if not ex.get('prompt') or not ex.get('response'):
            continue
        key = (ex['prompt'][:50].lower(), ex['response'][:50].lower())
        if key not in seen:
            seen.add(key)
            unique.append(ex)
    
    print(f"   ✅ After deduplication: {len(unique)} unique pairs")
    
    # Filter quality
    print("\n🔍 Filtering for quality...")
    filtered = [
        ex for ex in unique
        if len(ex['prompt']) >= 10 
        and len(ex['response']) >= 10
        and len(ex['prompt']) <= 2000
        and len(ex['response']) <= 2000
    ]
    
    print(f"   ✅ After quality filter: {len(filtered)} examples")
    
    # Shuffle
    random.shuffle(filtered)
    
    # Save to L: drive
    output = Path("L:/infra_core/unsloth_integration/data/travis_all_chatlogs.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output, 'w', encoding='utf-8') as f:
        for ex in filtered:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')
    
    print(f"\n✅ Saved to L: drive: {output}")
    print(f"📊 Total examples: {len(filtered)}")
    
    # Show samples
    print("\n" + "="*60)
    print("SAMPLE EXAMPLES")
    print("="*60)
    for i, ex in enumerate(random.sample(filtered, min(5, len(filtered)))):
        print(f"\n[{i+1}] User: {ex['prompt'][:100]}...")
        print(f"    AI:   {ex['response'][:100]}...")

if __name__ == "__main__":
    main()

