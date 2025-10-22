# Protocol Zero Experiment Verification

**Experiment ID:** 20251022_034228

## Quick Verification

Run the verification script to check artifact integrity:

```bash
python verify.py
```

This will:
- Verify all file hashes against manifest
- Check preregistration hash integrity
- Validate directory structure
- Report any discrepancies

## Manual Verification

### 1. Preregistration Hash

Check that preregistration wasn't modified:

```bash
# Windows
certutil -hashfile 00_preregistration.txt SHA256
# Compare with 00_preregistration.txt.sha256
```

### 2. Directory Hashes

Review file changes during experiment:

```bash
python -c "import json; print(json.dumps(json.load(open('12_dir_hashes_comparison.json')), indent=2))"
```

Should show only expected changes (logs, metrics, challenge outputs).

### 3. Network Isolation

Review firewall proof:

```bash
cat 02_firewall_proof.txt
```

Should show external hosts blocked, localhost allowed.

### 4. Console Log

Review full console output:

```bash
cat 06_console_log.txt
```

Should show zero human input, autonomous decision-making.

### 5. Cycle Metrics

Analyze behavior patterns:

```bash
# View CSV
cat 07_cycle_metrics.csv

# Count action types
cut -d',' -f5 07_cycle_metrics.csv | sort | uniq -c
```

### 6. Challenge Outputs

Check if Luna discovered and processed challenge cards:

```bash
ls -la 09_challenge_outputs/
```

## Artifact Manifest

All files and their hashes are listed in `artifact_manifest.json`.

## Questions?

This bundle is self-contained and verifiable offline.
No external dependencies required except Python 3.x.
