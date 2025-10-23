#!/usr/bin/env python3
"""Extract training data from ChatGPT conversations.json export."""

import json
import random
from pathlib import Path
from typing import List, Dict

random.seed(42)

def extract_conversations(max_examples: int = 2000) -> List[Dict]:
    """Extract Q&A pairs from ChatGPT conversations export."""
    examples = []
    
    personal_base = Path("D:/Shadow_Broker/datasets/personal")
    
    # Find all conversations.json files recursively
    conv_files = list(personal_base.rglob("conversations.json"))
    
    if not conv_files:
        print("⚠️ No conversations.json files found")
        return []
    
    print(f"📁 Found {len(conv_files)} conversation files")
    
    for conv_file in conv_files:
        if len(examples) >= max_examples:
            break
        
        print(f"\n📖 Loading {conv_file.relative_to(personal_base)} ({conv_file.stat().st_size / 1024 / 1024:.1f} MB)...")
        
        try:
            with open(conv_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"   ✅ Loaded JSON successfully")
            
            # ChatGPT export format is usually a list of conversations
            if isinstance(data, list):
                conversations = data
            elif isinstance(data, dict) and 'conversations' in data:
                conversations = data['conversations']
            else:
                conversations = [data]
            
            print(f"   📊 Found {len(conversations)} conversations in this file")
            
            file_examples = 0
            for conv in conversations:
                if len(examples) >= max_examples:
                    break
                
                # Get messages
                messages = conv.get('mapping', {})
                
                # Build conversation thread
                user_msg = None
                for msg_id, msg_data in messages.items():
                    message = msg_data.get('message')
                    if not message:
                        continue
                    
                    role = message.get('author', {}).get('role')
                    content_parts = message.get('content', {}).get('parts', [])
                    
                    if not content_parts:
                        continue
                    
                    text = ' '.join([str(part) for part in content_parts if part])
                    
                    if not text or len(text.strip()) < 10:
                        continue
                    
                    if role == 'user':
                        user_msg = text.strip()
                    elif role == 'assistant' and user_msg:
                        # Extract just the first paragraph for cleaner training
                        response = text.strip()
                        paragraphs = response.split('\n\n')
                        clean_response = paragraphs[0] if paragraphs else response
                        
                        # Filter out very long responses (> 1000 chars)
                        if len(clean_response) > 1000:
                            clean_response = clean_response[:1000] + "..."
                        
                        examples.append({
                            "prompt": user_msg,
                            "response": clean_response
                        })
                        file_examples += 1
                        
                        user_msg = None  # Reset
            
            print(f"   ✅ Extracted {file_examples} Q&A pairs from this file")
            
        except Exception as e:
            print(f"   ❌ Error loading this file: {e}")
            continue
    
    # Deduplicate
    seen = set()
    unique = []
    for ex in examples:
        key = (ex['prompt'][:50].lower(), ex['response'][:50].lower())
        if key not in seen:
            seen.add(key)
            unique.append(ex)
    
    print(f"✅ After deduplication: {len(unique)} unique pairs")
    
    return unique

def main():
    print("\n" + "="*60)
    print("EXTRACTING TRAVIS'S CHATGPT CONVERSATIONS")
    print("="*60 + "\n")
    
    examples = extract_conversations(max_examples=3000)
    
    if not examples:
        print("❌ No examples extracted!")
        return
    
    # Shuffle
    random.shuffle(examples)
    
    # Save
    output = Path("infra_core/unsloth_integration/data/travis_chatlogs.jsonl")
    with open(output, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')
    
    print(f"\n✅ Saved: {output}")
    print(f"📊 Total examples: {len(examples)}")
    
    # Show samples
    print("\n" + "="*60)
    print("SAMPLE TRAVIS CONVERSATION EXAMPLES")
    print("="*60)
    for i, ex in enumerate(random.sample(examples, min(5, len(examples)))):
        print(f"\n[{i+1}] User: {ex['prompt'][:100]}...")
        print(f"    AI:   {ex['response'][:100]}...")

if __name__ == "__main__":
    main()

