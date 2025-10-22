# Audit Core Scripts

Automated fix scripts for improving AIOS system health and production readiness.

## Available Scripts

### Critical Fixes

**`fix_critical_breaks.py`**
- Fixes import errors and uninitialized variables
- Targets: CARMA analytics.py, Fractal safety_rails.py
- Impact: Prevents system crashes
- Status: ✅ COMPLETE

### Performance Fixes

**`fix_carma_caching.py`**
- Adds conversation embedding cache to CARMA
- Prevents N+1 embedding calls per query
- Impact: ~100x performance improvement for repeated queries
- Status: 🚧 IN PROGRESS

**`fix_luna_arbiter_caching.py`** (planned)
- Adds gold standard and quality assessment caching
- Prevents 2 HTTP calls per response
- Impact: ~50% latency reduction

### Safety Improvements

**`replace_print_with_log.py`** (planned)
- Replaces print() with proper logging in production code
- Targets: All cores (41 safety gaps detected)
- Impact: Better error tracking and debugging

**`add_idempotency_keys.py`** (planned)
- Adds idempotency to mutating operations
- Targets: CARMA, Dream, Fractal consolidation/optimization
- Impact: Prevents duplicate executions

### Master Runner

**`run_all_fixes.py`**
- Runs all fix scripts in priority order
- Tracks score improvement
- Shows before/after comparison
- Usage: `py main_core/audit_core/scripts/run_all_fixes.py`

## Usage

### Run Single Fix

```bash
py main_core/audit_core/scripts/fix_critical_breaks.py
```

### Run All Fixes

```bash
py main_core/audit_core/scripts/run_all_fixes.py
```

### Verify Improvements

```bash
python main.py --audit
```

## Score Improvement Tracker

| Fix Applied | Before | After | Delta | Status |
|-------------|--------|-------|-------|--------|
| Critical breaks fixed | 50.7 | 53.9 | +3.2 | ✅ Done |
| CARMA caching | 53.9 | TBD | TBD | 🚧 In progress |
| Luna caching | TBD | TBD | TBD | 📋 Planned |
| Print→Log | TBD | TBD | TBD | 📋 Planned |
| Idempotency | TBD | TBD | TBD | 📋 Planned |

**Target:** 85/100 (production ready)
**Current:** 53.9/100
**Remaining:** 31.1 points needed

## Development Workflow

1. **Run audit:** `python main.py --audit`
2. **Check fixes:** `python main.py --audit --fixes`
3. **Apply fixes:** `py main_core/audit_core/scripts/run_all_fixes.py`
4. **Verify:** `python main.py --audit`
5. **Repeat** until production ready (85+)

## Notes

- All scripts are idempotent (safe to re-run)
- Scripts check if fix is already applied before modifying
- Backup your code before running automated fixes (or use git)
- Each script can be run standalone or via master runner

