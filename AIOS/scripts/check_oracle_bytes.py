#!/usr/bin/env python3
import json

with open('rag_core/manual_oracle/oracle_index.json', 'r') as f:
    data = json.load(f)

print(f"Manual SHA: {data['manual_sha256'][:8]}")
print(f"TOC SHA: {data['toc_sha256'][:8]}")
print(f"Sections: {len(data['sections'])}\n")

for i, section in enumerate(data['sections'][:3], 1):
    print(f"Section {i}: {section['title']}")
    print(f"  Anchor: {section['anchor']}")
    print(f"  Line: {section['line_number']}")
    print(f"  Bytes: {section['byte_start']}-{section['byte_end']} ({section['byte_end'] - section['byte_start']} bytes)")
    print()

