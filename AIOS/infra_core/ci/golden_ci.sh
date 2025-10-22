#!/usr/bin/env bash
# Golden Test CI Gate
# Fails build on regression

set -euo pipefail

echo "======================================================================"
echo "GOLDEN TEST CI GATE"
echo "======================================================================"

# Configuration
SET=${1:-data_core/goldens/sample_set.json}
BASE=${2:-data_core/goldens/baseline_results.json}

# Use python3 for CI (Linux), fallback to python
PYTHON_CMD="python3"

# Check if baseline exists
if [[ ! -f "$BASE" ]]; then
    echo "[golden] no baseline; recording initial baseline"
    $PYTHON_CMD tools/golden_runner.py record --set "$SET" --out "$BASE"
    echo "✅ Baseline recorded"
    exit 0
fi

# Run comparison with thresholds
echo ""
echo "📊 Running golden test comparison..."
echo "   Baseline: $BASE"
echo "   Golden Set: $SET"
echo ""

$PYTHON_CMD tools/golden_runner.py compare \
  --set "$SET" \
  --baseline "$BASE" \
  --threshold 0.25

# Exit code from compare determines CI status
# 0 = PASS, 1 = FAIL





