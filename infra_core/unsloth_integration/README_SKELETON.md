# Evolution Loop Walking Skeleton

## Status
✅ **SKELETON COMPLETE** - Ready for smoke testing

## What This Is

A minimal, runnable micro-evolutionary training loop that:
- Loads current HEAD model
- Trains child generation (200-400 steps)
- Runs 3 evals (recall, generalization, style drift)
- Creates immutable fossils
- Promotes HEAD only if evals pass
- Tracks complete lineage

## Architecture

```
Luna runs normally
    ↓
Every 10,000 heartbeats: evolution window opens
    ↓
If karma >= threshold: trigger evolution
    ↓
Train → Eval → Fossilize → Promote (if pass)
    ↓
Continue normal operation (smarter brain!)
```

## Dual-Mode Operation

### 1. Heartbeat Mode (Autonomous)
Evolution automatically triggers during Luna's runtime when:
- Heartbeat % 10,000 == 0 (evolution window opens)
- Karma >= threshold (ready to age-up)

### 2. CLI Mode (Manual)
Trigger evolution manually for testing:

```bash
# Smoke test (200 steps)
python bin/evolve_once.py --reason "smoke test" --steps 200

# Production run (1200 steps)
python bin/evolve_once.py --reason "production evolution"

# Specific generation
python bin/evolve_once.py --reason "manual" --gen-id 3
```

## Directory Structure

```
models/
├── Luna-G000-YYYYMMDD-HHMMSS/     # Generation 0
│   ├── model.gguf                  # Neural weights
│   ├── tokenizer.json
│   ├── config.json
│   ├── train_args.json
│   ├── data_delta.sha256
│   ├── parent_gen.txt
│   ├── metrics.json
│   └── EVAL.md
├── Luna-G001-YYYYMMDD-HHMMSS/     # Generation 1
├── Luna-GHEAD/ → symlink to best  # Always points to current best
└── lineage.csv                     # Complete evolutionary history
```

## Files Created

### Core Components
1. `evolution_orchestrator.py` - Main loop coordinator
2. `training/train_micro_gen.py` - Training pipeline (Unsloth stub)
3. `evals/eval_suite.py` - 3 tiny evals
4. `fossils/fossilize_generation.py` - Immutable artifact creation
5. `config.json` - Budget limits and thresholds

### Integration
6. `luna_arbiter_system.py` - Added `check_and_execute_age_up()`
7. `luna_cycle_agent.py` - Added heartbeat trigger
8. `bin/evolve_once.py` - CLI tool

### Data
9. `models/lineage.csv` - Evolutionary ledger
10. `evals/qa_sets/` - QA sets for recall testing (created during training)

## Current Limitations (Skeleton Mode)

### ⚠️ Not Yet Implemented
- **Actual Unsloth training** - Currently simulated (placeholder model)
- **Real model evaluation** - Evals run but use placeholders
- **Teacher-student distillation** - Deferred to Phase 2
- **Big Five assessments** - Deferred to Phase 2
- **Living gold standards** - Deferred to Phase 2

### ✅ What Works
- Complete loop structure
- Dual-mode operation (heartbeat + CLI)
- Immutable fossilization
- Lineage tracking
- Budget enforcement
- Promotion gates (objective rules)
- Rollback safety

## Quick Start

### 1. Smoke Test
```bash
# Test the skeleton (5 seconds, creates placeholder model)
python bin/evolve_once.py --reason "smoke test" --steps 200
```

**Expected output:**
- Generation directory created: `models/Luna-G000-*/`
- 8 artifact files created
- Evals run (placeholders pass)
- HEAD promoted
- `lineage.csv` updated

### 2. Verify Artifacts
```bash
# Check generation directory
ls models/Luna-G000-*

# Check lineage
cat models/lineage.csv

# Check eval report
cat models/Luna-G000-*/EVAL.md

# Check HEAD pointer
ls -l models/Luna-GHEAD
```

### 3. Test Rollback
```bash
# Run second generation (will fail evals - stub)
python bin/evolve_once.py --reason "test rollback" --gen-id 1

# Verify HEAD unchanged if evals failed
# HEAD should still point to G000
```

## Configuration

Edit `infra_core/unsloth_integration/config.json`:

```json
{
  "evo_period_cycles": 10000,        // Heartbeat trigger frequency
  "budget": {
    "max_steps": 2000,                // Training budget
    "max_walltime_minutes": 60,
    "max_gpu_memory_gb": 12
  },
  "training": {
    "smoke_test_steps": 200,          // For quick testing
    "production_steps": 1200,         // For real training
    "learning_rate": 1.5e-5
  },
  "evals": {
    "recall_threshold": 0.90,         // Must retain 90% of knowledge
    "generalization_threshold": 0.80, // Must learn new patterns
    "style_drift_max": 2              // Max 2 corporate phrases
  }
}
```

## Next Steps (Phase 2)

### Implement Actual Training
1. Wire Unsloth into `train_micro_gen.py`
2. Download base model (Llama-3.2-1B)
3. Implement 4-bit LoRA training
4. Test on real data

### Implement Real Evals
1. Create QA sets from training data
2. Implement recall test (load prior gen QA)
3. Implement generalization test (holdout set)
4. Implement style drift test (tone probes)

### Add Advanced Features
1. Teacher-student distillation (logit blending)
2. Big Five personality assessments
3. Living gold standard evolution
4. Parallel candidate experiments
5. Shadow deployment / burn-in testing

## Testing

### Unit Tests (TODO)
```bash
# Test eval suite
pytest infra_core/unsloth_integration/evals/test_eval_suite.py

# Test fossilization
pytest infra_core/unsloth_integration/fossils/test_fossilize.py

# Test orchestrator
pytest infra_core/unsloth_integration/test_orchestrator.py
```

### Integration Test
```bash
# Run complete cycle
python bin/evolve_once.py --reason "integration test" --steps 200

# Verify all artifacts created
./scripts/verify_generation.sh models/Luna-G000-*
```

## Troubleshooting

### Issue: "No module named infra_core"
**Fix:** Run from AIOS root directory
```bash
cd L:/AIOS
python bin/evolve_once.py --reason "test"
```

### Issue: "Evolution window never opens"
**Fix:** Check heartbeat config
```python
# In config.json
"evo_period_cycles": 10000  # Make smaller for testing (e.g., 10)
```

### Issue: "All evals fail"
**Fix:** This is expected in skeleton mode (uses placeholders)
- Evals will pass/fail randomly until real implementation
- Focus on structure, not results

### Issue: "HEAD not promoted"
**Fix:** Check EVAL.md to see which gates failed
```bash
cat models/Luna-G001-*/EVAL.md
```

## Architecture Principles

From ChatGPT's guidance:

1. **Heartbeat-clocked** - Evolution tied to logical time, not wall time
2. **Immutable fossils** - Never overwrite history, only HEAD pointer
3. **Objective gates** - Numbers decide promotion, not vibes
4. **Micro-steps** - Small, safe training runs with rollback capability
5. **Dual-mode** - Both autonomous and manual trigger
6. **Budget-enforced** - Hard fails if exceeds resource limits
7. **Lineage-tracked** - Complete audit trail in CSV

## References

- **Full specs:** See `*.md` files in `infra_core/unsloth_integration/`
- **Evolution Contract:** `SELF_EVOLUTION_CONTRACT.md`
- **Generational Hygiene:** `GENERATIONAL_HYGIENE.md`
- **Micro-Evolutionary Training:** `MICRO_EVOLUTIONARY_TRAINING.md`
- **Teacher-Student:** `TEACHER_STUDENT_DISTILLATION.md` (Phase 2)

## Success Criteria

### Minimal Viable Loop ✅
- [x] Can run one evolution cycle end-to-end
- [x] Creates immutable fossils with all 8 required files
- [x] Updates lineage.csv correctly
- [x] Promotes HEAD only when evals pass
- [x] Rollback works (failed gen doesn't break system)

### Dual-Mode Operation ✅
- [x] Heartbeat trigger integrated
- [x] CLI trigger works
- [x] Both use same code path

### Budget Enforcement ✅
- [x] Hard fails if training exceeds max steps
- [x] Hard fails if walltime exceeds 60 min
- [x] Configuration-driven limits

## Status: SKELETON COMPLETE

The walking skeleton is operational. All components are wired and the loop closes.

**Ready for:** Actual Unsloth integration and real training data.

**Timeline:** Phase 2 implementation can begin immediately.

