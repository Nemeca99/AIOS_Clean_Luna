#!/usr/bin/env python3
import json

with open('rag_core/manual_oracle/oracle_index.json', 'r') as f:
    d = json.load(f)

sections = d['sections']
print(f'Chunks: {len(sections)}')
print(f'Manual SHA: {d["manual_sha256"][:8]}')
print(f'TOC SHA: {d["toc_sha256"][:8]}')
print(f'First: {sections[0]["anchor"]}')
print(f'Last: {sections[-1]["anchor"]}')

# Calculate avg tokens
if sections:
    total_bytes = sum(s.get('byte_end', 0) - s.get('byte_start', 0) for s in sections if s.get('byte_start') and s.get('byte_end'))
    avg_bytes = total_bytes / len(sections)
    avg_tokens = int(avg_bytes / 4)
    print(f'Avg tokens: {avg_tokens}')

