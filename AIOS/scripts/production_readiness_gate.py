#!/usr/bin/env python3
"""
Production Readiness Gate
HARD STOPS - No lies, no green banners for red reality
"""

import sys
import json
from pathlib import Path

repo_root = Path.cwd()
sys.path.insert(0, str(repo_root))

def main():
    print("=" * 70)
    print("PRODUCTION READINESS GATE")
    print("=" * 70)
    
    failures = []
    warnings = []
    
    # Gate 1: Standards Score
    print("\n[GATE 1] Architectural Standards...")
    try:
        from main_core.audit_core.checks.standards_check import StandardsCheck
        check = StandardsCheck()
        
        test_cores = ['carma_core', 'rag_core', 'luna_core', 'data_core']
        scores = []
        
        for core_name in test_cores:
            core_path = repo_root / core_name
            if core_path.exists():
                result = check.run(core_path, core_name)
                score = result.details.get('score', 0)
                violations = result.details.get('total_violations', 0)
                critical = result.details.get('critical_violations', 0)
                
                scores.append((core_name, score, violations, critical))
                
                if score < 85:
                    failures.append(f"STANDARDS: {core_name} score={score}/100 (< 85 minimum)")
                if critical > 0:
                    failures.append(f"STANDARDS: {core_name} has {critical} CRITICAL violations")
        
        avg_score = sum(s[1] for s in scores) / len(scores) if scores else 0
        print(f"   Average score: {avg_score:.1f}/100")
        for core, score, violations, critical in scores:
            status = "✅" if score >= 85 and critical == 0 else "❌"
            print(f"   {status} {core}: {score}/100 ({violations} violations, {critical} critical)")
    
    except Exception as e:
        failures.append(f"STANDARDS: Check failed - {e}")
    
    # Gate 2: Oracle Index Size
    print("\n[GATE 2] Manual Oracle Index...")
    try:
        oracle_path = repo_root / "rag_core" / "manual_oracle" / "oracle_index.json"
        if oracle_path.exists():
            with open(oracle_path, 'r') as f:
                data = json.load(f)
            
            chunks = len(data.get('sections', []))
            manual_sha = data.get('manual_sha256', '')[:8]
            toc_sha = data.get('toc_sha256', '')[:8]
            
            # Calculate avg tokens
            sections = data.get('sections', [])
            if sections:
                total_bytes = sum(
                    s.get('byte_end', 0) - s.get('byte_start', 0) 
                    for s in sections 
                    if s.get('byte_start') and s.get('byte_end')
                )
                avg_bytes = total_bytes / len(sections)
                avg_tokens = int(avg_bytes / 4)
            else:
                avg_tokens = 0
            
            print(f"   Chunks: {chunks}")
            print(f"   Avg tokens: {avg_tokens}")
            print(f"   Manual SHA: {manual_sha}")
            print(f"   TOC SHA: {toc_sha}")
            print(f"   First anchor: {sections[0]['anchor'] if sections else 'N/A'}")
            print(f"   Last anchor: {sections[-1]['anchor'] if sections else 'N/A'}")
            
            if chunks < 100:
                failures.append(f"INDEX: Only {chunks} chunks (< 100 minimum)")
            elif chunks < 200:
                warnings.append(f"INDEX: Only {chunks} chunks (< 200 recommended)")
        else:
            failures.append("INDEX: Oracle index file not found")
    
    except Exception as e:
        failures.append(f"INDEX: Check failed - {e}")
    
    # Gate 3: CARMA Integrity
    print("\n[GATE 3] CARMA Integrity...")
    try:
        from carma_core.carma_core import CARMASystem
        system = CARMASystem()
        stats = system.get_integrity_stats()
        
        total_hashes = stats.get('total_hashes', 0)
        file_hashes = stats.get('file_hashes', 0)
        fragment_hashes = stats.get('fragment_hashes', 0)
        
        print(f"   Total hashes: {total_hashes}")
        print(f"   File hashes: {file_hashes}")
        print(f"   Fragment hashes: {fragment_hashes}")
        
        # This will be low until cache is populated - that's OK for now
        if total_hashes == 0:
            warnings.append(f"INTEGRITY: No hashes tracked yet (cache empty)")
    
    except Exception as e:
        failures.append(f"INTEGRITY: Check failed - {e}")
    
    # Gate 4: RAG Ranking (smoke test)
    print("\n[GATE 4] RAG Ranking Validation...")
    try:
        from rag_core.rag_core import RAGCore
        rag = RAGCore()
        
        # Two different queries
        results1 = rag.search_manual("Luna personality", top_k=3)
        results2 = rag.search_manual("CARMA memory optimization", top_k=3)
        
        # Check if rankings differ
        if results1 and results2:
            top1_anchor = results1[0].get('anchor', '')
            top2_anchor = results2[0].get('anchor', '')
            
            top1_score = results1[0].get('search_score', 0)
            top2_score = results2[0].get('search_score', 0)
            
            print(f"   Query 1 top result: {top1_anchor} (score={top1_score:.4f})")
            print(f"   Query 2 top result: {top2_anchor} (score={top2_score:.4f})")
            
            if top1_anchor == top2_anchor and abs(top1_score - top2_score) < 0.01:
                failures.append(f"RAG: Rankings flatlined (same result for different queries)")
            else:
                print(f"   ✅ Rankings vary correctly")
        else:
            failures.append(f"RAG: No results returned")
    
    except Exception as e:
        failures.append(f"RAG: Check failed - {e}")
    
    # Gate 5: GPU Detection
    print("\n[GATE 5] GPU Acceleration...")
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            gpu_name = torch.cuda.get_device_name(0)
            print(f"   ✅ GPU: {gpu_name}")
        else:
            print(f"   ⚠️  GPU: Not available (CPU fallback)")
            warnings.append("GPU: CUDA not available (using CPU)")
    
    except Exception as e:
        warnings.append(f"GPU: Check failed - {e}")
    
    # FINAL VERDICT
    print("\n" + "=" * 70)
    print("PRODUCTION READINESS VERDICT")
    print("=" * 70)
    
    if failures:
        print("\n❌ READY: NO")
        print(f"\nFailing gates ({len(failures)}):")
        for failure in failures:
            print(f"  - {failure}")
    else:
        print("\n✅ READY: YES (all gates passed)")
    
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
    
    # Print summary line (for scripts to parse)
    print(f"\nSummary:")
    print(f"  manual_sha={manual_sha if 'manual_sha' in locals() else 'unknown'}")
    print(f"  toc_sha={toc_sha if 'toc_sha' in locals() else 'unknown'}")
    print(f"  chunks={chunks if 'chunks' in locals() else 0}")
    print(f"  avg_tokens={avg_tokens if 'avg_tokens' in locals() else 0}")
    print(f"  avg_standards_score={avg_score if 'avg_score' in locals() else 0:.1f}")
    print(f"  failures={len(failures)}")
    print(f"  warnings={len(warnings)}")
    
    # Exit code: 0 if ready, 1 if not
    sys.exit(1 if failures else 0)

if __name__ == "__main__":
    main()

