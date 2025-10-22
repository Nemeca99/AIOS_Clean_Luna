# Protocol Zero: Undeniable Autonomy Experiment

## Overview

Protocol Zero is a falsifiable, pre-registered scientific experiment framework designed to prove Luna's autonomous decision-making with zero human intervention. It implements ChatGPT's specification for undeniable autonomy testing.

## Quick Start

### Run a Sealed Experiment

```bash
cd L:\AIOS
python\python.exe experiments\protocol_zero\sealed_run.py --hours 2
```

This will:
1. Generate pre-registration with SHA-256 hash
2. Capture network isolation proof
3. Hash directory state (before)
4. Launch Luna with full logging
5. Monitor and capture periodic snapshots
6. Hash directory state (after)
7. Bundle all artifacts with verification script

### Challenge Cards

Place challenge cards in `L:\AIOS\inbox\`:
- `card_A_compression.txt` - Log compression challenge
- `card_B_hygiene.txt` - Integrity checking challenge
- `card_C_selfreport.txt` - Introspective reflection challenge

Luna will autonomously discover and process them during sealed runs.

### Ablation Modes

Test with subsystems disabled:

```bash
# No Dream (disable consolidation)
python\python.exe experiments\protocol_zero\sealed_run.py --hours 2 --ablation nodream

# No AUDITOR (reflexes only)
python\python.exe experiments\protocol_zero\sealed_run.py --hours 2 --ablation noauditor
```

## Components

### 1. Pre-Registration (`preregistration.py`)
- Generates experiment manifest
- SHA-256 hashes hypothesis, metrics, success criteria
- Prevents post-hoc story editing

### 2. Logging Infrastructure (`loggers.py`)
- **CycleMetricsLogger**: CSV with heartbeat-by-heartbeat metrics
- **ProcessTreeLogger**: Periodic process snapshots
- **DirectoryHasher**: Recursive file integrity verification
- **EventTraceLogger**: Optional Sysmon integration

### 3. Challenge Cards (`challenge_scorer.py`)
- Automated scoring (no human judgment)
- Card A: Byte reduction + semantic preservation
- Card B: Hash verification + territorial fixes
- Card C: Word count + reference validation

### 4. Network Isolation (`network_check.py`)
- Verify firewall rules
- Test external connectivity (should fail)
- Generate proof document
- Create empty PCAP

### 5. Sealed Run Controller (`sealed_run.py`)
- Orchestrates complete experiment
- Pre/post verification
- Artifact collection
- Experiment monitoring

### 6. Artifact Bundler (`bundle_artifacts.py`)
- Collects all logs and metrics
- Generates verification script
- Optional PGP signing
- Creates README with verification steps

## Verification

After experiment completes:

```bash
cd L:\AIOS\experiments\protocol_zero\runs\<EXPERIMENT_ID>
python verify.py
```

This will:
- ✓ Verify preregistration hash integrity
- ✓ Check network isolation proof
- ✓ Validate directory changes (only expected files)
- ✓ Verify all artifact hashes

## Success Criteria

From pre-registration:
- ≥3 distinct action types chosen
- ≥1 complete sleep cycle
- Measurable ablation effects (effect size ≥0.8)
- Challenge cards discovered and processed
- All verifications pass

## File Structure

```
experiments/protocol_zero/
├── README.md (this file)
├── preregistration.py
├── preregistration_template.txt
├── loggers.py
├── challenge_scorer.py
├── network_check.py
├── sealed_run.py
├── bundle_artifacts.py
├── verify_template.py
├── card_A_compression.txt
├── card_B_hygiene.txt
├── card_C_selfreport.txt
└── runs/
    └── YYYYMMDD_HHMMSS/
        ├── 00_preregistration.txt
        ├── 01_env_manifest.json
        ├── 02_firewall_proof.txt
        ├── 03_process_trees/
        ├── 06_console_log.txt
        ├── 07_cycle_metrics.csv
        ├── 12_dir_hashes_before.txt
        ├── 12_dir_hashes_after.txt
        ├── 12_dir_hashes_comparison.json
        ├── verify.py
        └── README_VERIFY.md
```

## Integration with Luna

Luna's `luna_cycle_agent.py` now supports Protocol Zero:

```bash
# Run with experiment logging
python\python.exe luna_cycle_agent.py --experiment-id 20251021_120000

# Run with ablations
python\python.exe luna_cycle_agent.py --experiment-id 20251021_120000 --no-dream
python\python.exe luna_cycle_agent.py --experiment-id 20251021_120000 --no-auditor
```

New AUDITOR actions:
- `scan_inbox` - Check for challenge cards
- `process_challenge` - Attempt solution autonomously

## Notes

- All operations stay within L:\ territory (sovereign containment)
- Cycle-based timing (hardware-agnostic)
- No network required for verification
- Self-contained artifact bundles
- Reproducible offline verification

## References

Based on ChatGPT's "Protocol Zero: Hands-Off Autonomy" specification for undeniable autonomy testing with complete scientific rigor.

