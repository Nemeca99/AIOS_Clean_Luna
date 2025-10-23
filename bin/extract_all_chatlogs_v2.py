#!/usr/bin/env python3
"""Extract ALL chatlogs - optimized for Travis's actual markdown format."""

import json
import random
import re
from pathlib import Path
from typing import List, Dict, Tuple

random.seed(42)

def extract_conversation_blocks(content: str) -> List[Tuple[str, str]]:
    """Extract conversation blocks from raw text/markdown."""
    conversations = []
    
    # Split by multiple newlines to get blocks
    blocks = re.split(r'\n{3,}', content)
    
    user_block = None
    for block in blocks:
        block = block.strip()
        
        # Skip very short blocks, "Edit", "Retry", timestamps
        if len(block) < 20:
            continue
        if block in ['Edit', 'Retry', 'Copy'] or block.endswith('s'):
            continue
        if re.match(r'^\d+s$', block):
            continue
        
        # Heuristic: Blocks with questions or starting with common user phrases are user
        is_user = (
            '?' in block[:100] or
            block.startswith(('So ', 'I ', 'Can ', 'How ', 'What ', 'Why ', 'When ', 'Where ',
                            'But ', 'And ', 'Also ', 'Plus ', 'Well ', 'Yeah ', 'Ok ', 'Okay ',
                            'Tell ', 'Show ', 'Help ', 'Do ', 'Does ', 'Is ', 'Are ', 'Will '))
        )
        
        # Or if previous was AI response
        if user_block is None:
            user_block = block
        elif is_user or len(user_block) > len(block) * 2:
            # Current block is user, previous was AI
            if user_block and len(user_block) > 20 and len(block) > 20:
                conversations.append((user_block[:2000], block[:2000]))
            user_block = None
        else:
            # Current block is AI response to previous user block
            if len(block) > 20:
                conversations.append((user_block[:2000], block[:2000]))
            user_block = None
    
    return conversations

def extract_markdown_structured(content: str) -> List[Tuple[str, str]]:
    """Extract from structured markdown (User:/AI: format)."""
    conversations = []
    
    # Pattern: Multiple variations
    patterns = [
        r'(?:^|\n)(?:User|Travis|Human|You):\s*(.*?)\s*(?:^|\n)(?:Assistant|AI|Luna|Lyra|Nova|Claude|ChatGPT):\s*(.*?)(?=(?:^|\n)(?:User|Travis|Human|You):|\Z)',
        r'\*\*(?:User|Travis|Human):\*\*\s*(.*?)\s*\*\*(?:Assistant|AI|Luna|Lyra|Nova):\*\*\s*(.*?)(?=\*\*(?:User|Travis|Human):\*\*|\Z)',
        r'#{1,3}\s*(?:User|Travis|Human)[^\n]*\n(.*?)\n#{1,3}\s*(?:Assistant|AI|Luna|Lyra|Nova)[^\n]*\n(.*?)(?=\n#{1,3}|\Z)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for user, ai in matches:
            user = user.strip()[:2000]
            ai = ai.strip()[:2000]
            if len(user) > 20 and len(ai) > 20:
                conversations.append((user, ai))
    
    return conversations

def extract_from_file(file_path: Path) -> List[Dict]:
    """Extract Q&A from any file format."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        
        # Skip files that are clearly not chatlogs
        if len(content) < 100:
            return []
        
        conversations = []
        
        # Try structured formats first
        structured = extract_markdown_structured(content)
        conversations.extend(structured)
        
        # If we got few results, try block extraction
        if len(structured) < 5:
            blocks = extract_conversation_blocks(content)
            conversations.extend(blocks)
        
        # Try JSON
        if file_path.suffix in ['.json', '.jsonl']:
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            if 'prompt' in item and 'response' in item:
                                conversations.append((item['prompt'], item['response']))
                            elif 'user' in item and 'assistant' in item:
                                conversations.append((item['user'], item['assistant']))
            except:
                pass
        
        # Convert to dict format
        examples = []
        for user, ai in conversations:
            if len(user) > 10 and len(ai) > 10:
                examples.append({
                    "prompt": user.strip(),
                    "response": ai.strip()
                })
        
        return examples
        
    except Exception as e:
        return []

def main():
    print("\n" + "="*60)
    print("EXTRACTING ALL TRAVIS CHATLOGS V2")
    print("="*60 + "\n")
    
    personal_base = Path("D:/Shadow_Broker/datasets/personal")
    
    if not personal_base.exists():
        print("❌ Personal datasets not found!")
        return
    
    all_examples = []
    files_processed = 0
    
    # Get all relevant files
    extensions = ['*.md', '*.txt', '*.json', '*.jsonl']
    all_files = []
    
    for ext in extensions:
        files = list(personal_base.rglob(ext))
        print(f"📄 Found {len(files)} {ext} files")
        all_files.extend(files)
    
    print(f"\n📊 Total files to process: {len(all_files)}")
    print("🔄 Processing (skipping files > 50MB)...\n")
    
    for file_path in all_files:
        # Skip very large files
        if file_path.stat().st_size > 50_000_000:
            continue
        
        examples = extract_from_file(file_path)
        if examples:
            all_examples.extend(examples)
            files_processed += 1
            
            if files_processed % 50 == 0:
                print(f"   Processed {files_processed} files, {len(all_examples)} examples...")
    
    print(f"\n✅ Processed {files_processed} files")
    print(f"📊 Total raw examples: {len(all_examples)}")
    
    # Deduplicate
    print("\n🔄 Deduplicating...")
    seen = set()
    unique = []
    for ex in all_examples:
        key = (ex['prompt'][:50].lower(), ex['response'][:50].lower())
        if key not in seen:
            seen.add(key)
            unique.append(ex)
    
    print(f"   ✅ {len(unique)} unique pairs")
    
    # Filter quality
    filtered = [
        ex for ex in unique
        if 10 <= len(ex['prompt']) <= 2000
        and 10 <= len(ex['response']) <= 2000
    ]
    
    print(f"   ✅ {len(filtered)} after quality filter")
    
    # Shuffle
    random.shuffle(filtered)
    
    # Save to L: drive
    output = Path("L:/infra_core/unsloth_integration/data/travis_all_chatlogs_v2.jsonl")
    with open(output, 'w', encoding='utf-8') as f:
        for ex in filtered:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')
    
    print(f"\n✅ Saved to: {output}")
    print(f"📊 Total examples: {len(filtered)}")
    
    # Show samples
    print("\n" + "="*60)
    print("SAMPLE EXAMPLES")
    print("="*60)
    for i, ex in enumerate(random.sample(filtered, min(5, len(filtered)))):
        print(f"\n[{i+1}] User: {ex['prompt'][:80]}...")
        print(f"    AI:   {ex['response'][:80]}...")

if __name__ == "__main__":
    main()

