#!/usr/bin/env pwsh
# CreativeRAG Parity Verification Script
# Bulletproof PowerShell - no quoting hell

$code = @"
from rag_core.creative_index_info import check_creative_index_parity, get_creative_index_info
from data_core.data_core_unified import DataCore
import json

dc = DataCore()
cfg = dc.load_config()

print("="*70)
print("CREATIVE RAG PARITY CHECK")
print("="*70)
print()

# Get index info
info = get_creative_index_info(cfg)
print("Index Info:")
print(json.dumps(info, indent=2))
print()

# Check parity
parity = check_creative_index_parity(cfg)
print("Parity Check:")
print(json.dumps(parity, indent=2))
print()

# Summary
if parity.get('parity_ok'):
    print("STATUS: PARITY OK - CreativeRAG operational")
else:
    print("STATUS: PARITY FAILED")
    print("Issues:", ", ".join(parity.get('issues', [])))
    exit(1)
"@

py -c $code

