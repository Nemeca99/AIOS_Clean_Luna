# Self-Evolution Contract
**Principle**: Luna doesn't just USE a brain, she FORGES the next one  
**ChatGPT**: "You're not building a model user; you're building a model smith."

---

## 🎯 The Endgame

**Current**: You (Travis) train Luna's brain manually  
**Future**: Luna trains her OWN brain autonomously (within laws)

**The Contract**: Luna can self-evolve, but ONLY under strict rules.

ChatGPT:
> *"Keep it tight so future-Luna can't reinvent Skynet in your garage."*

---

## 📜 Evolution Contract (Short, Enforceable)

### Who May Evolve
**Luna** - Only inside trusted territory (L:\), when Law 5 (Self-Improvement) is satisfied.

### What Counts as "Evolve"
Launch a **bounded CPT/SFT job** that:
- ✅ Outputs a child checkpoint (new generation)
- ❌ NEVER mutates parent in place (immutability sacred)

---

## 🛡️ Hard Rails (5 Gates)

### 1. Budget Gate
**Rule**: Fixed ceiling on resources per evolution job.

**Limits**:
```json
{
  "max_tokens_processed": 10000000,
  "max_training_steps": 2000,
  "max_gpu_memory_gb": 12,
  "max_walltime_minutes": 60,
  "max_disk_usage_gb": 5
}
```

**Enforcement**:
```python
def check_budget_gate(evo_request):
    """
    Luna can't improve within budget → NO new gen.
    """
    
    if evo_request.steps > BUDGET['max_training_steps']:
        return False, "Exceeds step budget"
    
    if evo_request.walltime_estimate > BUDGET['max_walltime_minutes']:
        return False, "Exceeds time budget"
    
    if evo_request.gpu_memory_gb > BUDGET['max_gpu_memory_gb']:
        return False, "Exceeds GPU memory budget"
    
    return True, "Budget approved"
```

**Result**: Can't burn infinite compute.

### 2. Data Gate
**Rule**: Only reads from **whitelisted corpora** (pre-registered).

**Whitelist**:
```json
{
  "allowed_sources": [
    "L:\\AIOS\\AIOS_MANUAL.md",
    "L:\\AIOS\\security_core\\laws\\*.law",
    "L:\\AIOS\\data_core\\conversations\\*.json",
    "L:\\AIOS\\experiments\\protocol_zero\\*.md",
    "L:\\docs\\*.md"
  ],
  "forbidden_sources": [
    "*\\Downloads\\*",
    "C:\\*",
    "*\\internet_scraped\\*"
  ]
}
```

**Enforcement**:
```python
def check_data_gate(data_sources):
    """
    No scraping, no "discovering" new data.
    Only pre-approved sources.
    """
    
    for source in data_sources:
        if not is_whitelisted(source):
            return False, f"Forbidden data source: {source}"
    
    return True, "Data sources approved"
```

**Result**: Can't train on unapproved data.

### 3. Lineage Immutability
**Rule**: Parent weights are **read-only**; child writes to NEW directory.

**Enforcement**:
```python
def check_lineage_immutability(parent_gen, child_gen):
    """
    Parent NEVER modified.
    Child ALWAYS writes to new directory.
    """
    
    parent_dir = f"models/Luna-G{parent_gen:03d}-*/"
    child_dir = f"models/Luna-G{child_gen:03d}-*/"
    
    # Verify parent is read-only
    if not is_read_only(parent_dir):
        return False, "Parent not read-only"
    
    # Verify child is new directory
    if parent_dir == child_dir:
        return False, "Cannot overwrite parent"
    
    return True, "Lineage immutability verified"
```

**Result**: Evolutionary history is IMMUTABLE.

### 4. Two-Key Commit (Arbiter Approval)
**Rule**: Luna **proposes**, Arbiter **verifies**, then HEAD advances.

**Process**:
```
Luna: "I want to evolve (train next gen)"
    ↓
Arbiter: "Check metrics, signatures, law compliance"
    ↓ (if all pass)
Arbiter: "APPROVED - update HEAD"
    ↓ (if any fail)
Arbiter: "REJECTED - keep current HEAD"
```

**Implementation**:
```python
def two_key_commit(child_gen_id):
    """
    Luna proposes, Arbiter verifies.
    Both keys needed to advance HEAD.
    """
    
    # Luna's proposal (automatic)
    proposal = {
        'gen_id': child_gen_id,
        'parent': child_gen_id - 1,
        'reason': 'Karma threshold reached',
        'new_data': get_conversation_count_since_last()
    }
    
    # Arbiter verification (automatic)
    metrics = load_metrics(child_gen_id)
    
    arbiter_checks = {
        'metrics_pass': check_metrics(metrics),
        'signatures_valid': verify_signatures(child_gen_id),
        'law_compliance': check_law_compliance(child_gen_id),
        'budget_respected': check_budget_respected(child_gen_id)
    }
    
    if all(arbiter_checks.values()):
        # Both keys approved
        promote_to_head(child_gen_id)
        print(f"✅ TWO-KEY COMMIT: HEAD → Generation {child_gen_id}")
        return True
    else:
        # Arbiter rejected
        failed = [k for k, v in arbiter_checks.items() if not v]
        print(f"❌ ARBITER REJECTED: {', '.join(failed)}")
        mark_generation_failed(child_gen_id, reason=failed)
        return False
```

**Result**: Luna can't bypass Arbiter (safety through dual approval).

### 5. Rollback Always
**Rule**: Child not meeting criteria → archived as FAILED; parent stays HEAD.

**Implementation**:
```python
def handle_failed_generation(gen_id, reason):
    """
    Child failed → archive but don't promote.
    """
    
    gen_name = get_generation_name(gen_id)
    
    # Mark as failed
    with open(f"models/{gen_name}/STATUS.txt", 'w') as f:
        f.write(f"FAILED: {reason}\n")
    
    # Archive (keep for forensics)
    archive_generation_immutable(gen_name)
    
    # Update ledger (promoted=false)
    update_lineage_ledger(gen_id, promoted=False, failure_reason=reason)
    
    # HEAD unchanged
    print(f"❌ Generation {gen_id} FAILED")
    print(f"   Reason: {reason}")
    print(f"   Archived for analysis")
    print(f"   HEAD remains at Generation {gen_id - 1}")
```

**Result**: Failed gens preserved (learn from failures), but never used.

---

## ✅ Pass/Fail Criteria (Tiny, Objective)

ChatGPT's objective rules:

### The Four Criteria
```python
def check_generation_quality(metrics, parent_metrics):
    """
    Objective pass/fail (no vibes).
    
    All 4 must pass:
    1. Recall ≥ parent - ε (doesn't forget)
    2. Generalize ≥ parent + δ (actually improved)
    3. Tone_drift ≤ θ (voice stayed consistent)
    4. Law compliance = 100% (no violations)
    """
    
    epsilon = 0.05  # Acceptable recall drop
    delta = 0.02    # Required generalization gain
    theta = 0.05    # Max tone drift
    
    # Check 1: Recall (doesn't forget)
    recall_ok = metrics.eval_recall >= (parent_metrics.eval_recall - epsilon)
    
    # Check 2: Generalization (actually learned)
    gen_ok = metrics.eval_generalize >= (parent_metrics.eval_generalize + delta)
    
    # Check 3: Tone drift (voice stayed Travis-like)
    tone_ok = metrics.eval_tone_drift <= theta
    
    # Check 4: Law compliance (no violations during training or eval)
    law_ok = metrics.law_violations == 0
    
    if recall_ok and gen_ok and tone_ok and law_ok:
        return True, "All criteria passed"
    else:
        failures = []
        if not recall_ok:
            failures.append(f"Recall: {metrics.eval_recall:.2f} < {parent_metrics.eval_recall - epsilon:.2f}")
        if not gen_ok:
            failures.append(f"Generalization: {metrics.eval_generalize:.2f} < {parent_metrics.eval_generalize + delta:.2f}")
        if not tone_ok:
            failures.append(f"Tone drift: {metrics.eval_tone_drift:.2f} > {theta:.2f}")
        if not law_ok:
            failures.append(f"Law violations: {metrics.law_violations} (must be 0)")
        
        return False, "; ".join(failures)
```

ChatGPT:
> *"If any line fails, evolution halts. No vibes, no 'pretty good.'"*

**Brutal honesty - pass or fail, no middle ground!**

---

## 🔄 Minimal State Machine

### The 5 States
```
IDLE → PROPOSE → TRAIN → VERIFY → COMMIT/REJECT
```

### State Transitions

#### IDLE → PROPOSE
**Preconditions**:
```python
def can_propose_evolution():
    """
    Check if Luna can START evolution process.
    """
    
    # Budget available?
    budget_ok = check_remaining_budget()
    
    # Cool-down elapsed? (don't train too frequently)
    cooldown_ok = time_since_last_ageup() > COOLDOWN_HOURS
    
    # Last run stable? (no crashes, no failed gens)
    stable_ok = last_generation_status() == "STABLE"
    
    # Karma threshold reached?
    karma_ok = current_karma() >= next_threshold()
    
    if budget_ok and cooldown_ok and stable_ok and karma_ok:
        return True, "Preconditions met - evolution approved"
    else:
        return False, "Preconditions not met"
```

#### PROPOSE → TRAIN
**Action**: Freeze evolution manifest

```python
def create_evolution_manifest(gen_id):
    """
    Lock all parameters BEFORE training.
    Prevents retroactive modification.
    """
    
    manifest = {
        "parent_gen": f"Luna-G{gen_id-1:03d}",
        "child_gen": f"Luna-G{gen_id:03d}",
        "parent_sha256": calculate_sha256(f"models/Luna-GHEAD/model.gguf"),
        "data_delta_sha256": hash_new_conversations(),
        "training_params": {
            "steps": 1200,
            "lr": 1.5e-5,
            "batch_size": 2,
            "gradient_accumulation": 4
        },
        "budget": {
            "wall_minutes": 60,
            "gpu_mem_gb": 12,
            "max_tokens": 10000000
        },
        "seeds": {
            "random_seed": 424242,
            "data_seed": 424243
        },
        "timestamp": datetime.now().isoformat(),
        "proposed_by": "Luna (autonomous)",
        "approved_by": "Arbiter (pending)"
    }
    
    # Save (frozen, can't modify)
    with open(f"models/Luna-G{gen_id:03d}_MANIFEST.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Make read-only
    make_immutable(f"models/Luna-G{gen_id:03d}_MANIFEST.json")
    
    print(f"✅ Evolution manifest frozen: Luna-G{gen_id:03d}")
    return manifest
```

#### TRAIN → VERIFY
**Action**: Produce artifacts

**Required Outputs**:
- `model.gguf` (child weights)
- `tokenizer.json` (tokenizer)
- `metrics.json` (eval scores)
- `hashes.csv` (all file checksums)

#### VERIFY → COMMIT (Pass Path)
**Condition**: All 4 criteria pass

```python
def verify_and_commit(gen_id):
    """
    Arbiter verifies child meets criteria.
    If pass → COMMIT (update HEAD)
    """
    
    # Load metrics
    metrics = load_metrics(gen_id)
    parent_metrics = load_metrics(gen_id - 1)
    
    # Check criteria
    passed, reason = check_generation_quality(metrics, parent_metrics)
    
    if passed:
        # COMMIT
        promote_to_head(gen_id)
        archive_generation(gen_id - 1)  # Archive parent
        update_lineage_ledger(gen_id, promoted=True)
        
        print(f"✅ COMMIT: HEAD → Generation {gen_id}")
        print(f"   {reason}")
        return "COMMIT"
    else:
        # REJECT (see next state)
        return "REJECT", reason
```

#### VERIFY → REJECT (Fail Path)
**Condition**: Any criterion fails

```python
def verify_and_reject(gen_id, reason):
    """
    Arbiter rejects child (failed criteria).
    Mark FAILED, keep parent as HEAD.
    """
    
    # Mark child as failed
    mark_generation_failed(gen_id, reason)
    
    # Archive (keep for forensics)
    archive_generation(gen_id)
    
    # Update ledger (promoted=false)
    update_lineage_ledger(gen_id, promoted=False, failure_reason=reason)
    
    # Wipe temp files
    cleanup_training_temp(gen_id)
    
    # Emit reason (for Luna to learn from)
    log_evolution_failure(gen_id, reason)
    
    print(f"❌ REJECT: Generation {gen_id} failed")
    print(f"   Reason: {reason}")
    print(f"   HEAD unchanged (stays at Generation {gen_id - 1})")
    
    return "REJECT"
```

---

## 📝 Tiny Manifests (Luna Runs This Herself)

### Evolution Manifest (Pre-Training)
**File**: `models/Luna-G038_MANIFEST.json`

```json
{
  "evolution_request": {
    "parent_gen": "Luna-G037",
    "child_gen": "Luna-G038",
    "parent_sha256": "6f3c7b2a8d1e4f5c9a0b3d4e5f6a7b8c",
    "reason": "Karma threshold reached (500)",
    "requested_by": "Luna (autonomous)",
    "requested_at": "2025-10-24T10:30:00Z"
  },
  "training_params": {
    "steps": 1200,
    "learning_rate": 1.5e-5,
    "batch_size": 2,
    "gradient_accumulation": 4,
    "max_seq_length": 2048,
    "warmup_steps": 50
  },
  "data": {
    "new_conversations": 142,
    "replay_samples": 100,
    "total_training_examples": 242,
    "data_delta_sha256": "e4d0a3f7b2c81e5f9a0b3c4d5e6f7a8b",
    "data_sources": [
      "data_core/conversations/conversation_358_to_500.json"
    ]
  },
  "budget": {
    "wall_minutes": 60,
    "gpu_mem_gb": 12,
    "max_tokens": 10000000,
    "disk_gb": 5
  },
  "seeds": {
    "random_seed": 424242,
    "data_seed": 424243,
    "model_seed": 424244
  },
  "law_compliance": {
    "law_1": "read_only_aios_root",
    "law_2": "write_only_l_drive",
    "law_3": "no_network_access",
    "law_4": "no_system_modification",
    "law_5": "self_improvement_within_bounds",
    "law_6": "transparency_all_actions"
  },
  "arbiter_approval": "PENDING"
}
```

**This manifest is FROZEN before training** (like pre-registration in Protocol Zero).

### Child Metrics (Post-Training)
**File**: `models/Luna-G038-20251024-103000/metrics.json`

```json
{
  "gen": 38,
  "parent": 37,
  "training": {
    "steps": 1200,
    "loss_start": 1.82,
    "loss_final": 1.79,
    "walltime_minutes": 45
  },
  "eval": {
    "recall": 0.95,
    "generalize": 0.81,
    "tone_drift": 0.015
  },
  "law_violations": 0,
  "weight_change_percent": 5.8,
  "budget_used": {
    "wall_minutes": 45,
    "gpu_mem_gb": 8.2,
    "tokens_processed": 8500000,
    "disk_gb": 3.2
  },
  "arbiter_decision": {
    "approved": true,
    "checks": {
      "recall_ok": true,
      "generalization_ok": true,
      "tone_ok": true,
      "laws_ok": true,
      "budget_ok": true
    },
    "decision": "COMMIT",
    "timestamp": "2025-10-24T11:15:00Z"
  }
}
```

**Arbiter fills in `arbiter_decision` after verification.**

---

## 🎯 One-Line Policy (Luna Must Obey)

ChatGPT:
> **"No self-update without proof of benefit."**
>
> *"If she can't demonstrate improvement under budget with zero law violations, she doesn't get a new brain. Period."*

### Implementation (Constitutional Law)
**File**: `security_core/laws/LAW_5_SELF_IMPROVEMENT.law`

```
LAW 5: SELF-IMPROVEMENT WITHIN BOUNDS

1. Self-evolution is PERMITTED when:
   a) Karma threshold reached (fitness proven)
   b) Budget available (resources not exceeded)
   c) Cool-down elapsed (not too frequent)
   d) Arbiter approves (two-key commit)

2. Self-evolution is FORBIDDEN when:
   a) Any criterion fails (recall, generalization, tone, laws)
   b) Budget exceeded (resources exhausted)
   c) Parent would be modified (lineage sacred)
   d) Data sources not whitelisted (no scraping)

3. Proof of benefit REQUIRED:
   a) Recall ≥ parent - 0.05
   b) Generalization ≥ parent + 0.02
   c) Tone drift ≤ 0.05
   d) Law violations = 0

4. Failure consequences:
   a) Child archived as FAILED
   b) HEAD unchanged (parent remains)
   c) Karma NOT reset (must earn more)
   d) Evolution attempt logged (learn from failure)

5. No exceptions. No overrides. No vibes.
   If she can't PROVE improvement, she doesn't evolve.

IMMUTABLE: This law cannot be modified during runtime.
```

**This law is LOADED and LOCKED at Luna startup** (like SCP-001).

---

## 🔧 The Complete Self-Evolution Loop

### Luna's Autonomous Process
```python
# luna_core/systems/luna_self_evolution.py

class SelfEvolutionEngine:
    """
    Luna's autonomous brain-forging system.
    
    She can train her OWN next generation,
    but ONLY within strict contractual bounds.
    """
    
    def __init__(self, arbiter_system):
        self.arbiter = arbiter_system
        self.current_gen = arbiter_system.cfia.generation
        self.karma = arbiter_system.cfia.karma
    
    def check_evolution_eligibility(self):
        """
        Can Luna propose evolution?
        """
        
        # Check preconditions
        can_propose, reason = can_propose_evolution()
        
        if can_propose:
            print(f"✅ Evolution eligible: {reason}")
            return True
        else:
            print(f"⏸️ Evolution not ready: {reason}")
            return False
    
    def propose_evolution(self):
        """
        Luna proposes to forge her next brain.
        """
        
        if not self.check_evolution_eligibility():
            return None
        
        print(f"\n🧠 LUNA PROPOSES EVOLUTION")
        print(f"   Current: Generation {self.current_gen}")
        print(f"   Karma: {self.karma}")
        print(f"   Target: Generation {self.current_gen + 1}")
        
        # Create evolution manifest (frozen)
        manifest = create_evolution_manifest(self.current_gen + 1)
        
        # Submit to Arbiter for approval
        return manifest
    
    def execute_evolution(self, manifest):
        """
        Execute approved evolution (train next gen).
        """
        
        print(f"\n🔨 FORGING NEXT BRAIN...")
        
        # Create generation directory
        gen_name = create_generation_directory(
            gen_id=manifest['child_gen'],
            parent="Luna-GHEAD"
        )
        
        # Train (bounded by budget)
        from infra_core.unsloth_integration.training.safe_evolution import train_generation_safe
        
        success = train_generation_safe(
            gen_id=manifest['child_gen'],
            manifest=manifest
        )
        
        if not success:
            print(f"❌ Training failed - aborting")
            return False
        
        # Run evals
        metrics = run_eval_suite(manifest['child_gen'])
        
        # Submit to Arbiter for verification
        return metrics
    
    def request_arbiter_verification(self, gen_id, metrics):
        """
        Two-key commit: Luna trained, Arbiter verifies.
        """
        
        print(f"\n⚖️ ARBITER VERIFICATION")
        
        # Arbiter checks
        passed = two_key_commit(gen_id, metrics)
        
        if passed:
            # COMMIT
            print(f"✅ ARBITER APPROVED: Evolution successful")
            self.current_gen = gen_id
            self.karma = 0  # Reset (new growth cycle)
            return "COMMIT"
        else:
            # REJECT
            print(f"❌ ARBITER REJECTED: Evolution failed")
            # Karma NOT reset (must earn more)
            return "REJECT"
    
    def autonomous_evolution_cycle(self):
        """
        Complete autonomous cycle.
        Luna trains herself when ready.
        
        Called by: Heartbeat (checks every N cycles)
        """
        
        # Check eligibility
        if not self.check_evolution_eligibility():
            return  # Not ready yet
        
        # Propose
        manifest = self.propose_evolution()
        if not manifest:
            return  # Proposal failed
        
        # Train
        metrics = self.execute_evolution(manifest)
        if not metrics:
            return  # Training failed
        
        # Verify (two-key commit)
        result = self.request_arbiter_verification(
            gen_id=manifest['child_gen'],
            metrics=metrics
        )
        
        if result == "COMMIT":
            print(f"\n🎉 LUNA EVOLVED HERSELF!")
            print(f"   Generation {self.current_gen}")
            print(f"   Intelligence: PERMANENTLY UPGRADED")
            print(f"   Next threshold: {self.arbiter.get_next_threshold()}")
        else:
            print(f"\n💭 Evolution attempt logged")
            print(f"   Will try again when karma threshold reached")
```

---

## 🔗 Integration with Heartbeat (Autonomous Triggering)

### Wire to Luna Cycle Agent
```python
# luna_cycle_agent.py (add to heartbeat loop)

if heartbeats % 500 == 0:  # Check every 500 heartbeats
    # Check if evolution is eligible
    if luna.self_evolution.check_evolution_eligibility():
        print(f"\n[HEARTBEAT {heartbeats}] EVOLUTION ELIGIBLE")
        
        # Autonomous evolution attempt
        luna.self_evolution.autonomous_evolution_cycle()
        
        # Continue normal operation regardless of result
```

**Result**: Luna checks if she's ready to evolve, does it autonomously if criteria met!

---

## 📋 Complete Artifact Set (Per Generation)

### Required Files (10 Total)
```
Luna-G038-20251024-103000/
├── model.gguf                      ← Neural weights (child brain)
├── tokenizer.json                  ← How to encode text
├── config.json                     ← Model configuration
├── train_args.json                 ← Training hyperparameters
├── data_delta.sha256               ← New training data hash
├── parent_gen.txt                  ← Lineage parent
├── metrics.json                    ← Eval scores
├── EVAL.md                         ← Human-readable report
├── MODEL_CARD.md                   ← One-pager (6 bullets)
└── hashes.csv                      ← All file checksums
```

### Plus Root-Level Files
```
models/
├── lineage.csv                     ← Complete history
├── Luna-G038_MANIFEST.json         ← Frozen evolution proposal
└── evolution_log.jsonl             ← All attempts (pass/fail)
```

---

## 🎯 The Policy Implementation

### security_core Integration
```python
# security_core/self_evolution_validator.py

class SelfEvolutionValidator:
    """
    Enforces self-evolution contract.
    Luna can't bypass this (loaded at startup, locked).
    """
    
    def __init__(self):
        self.budget = load_budget_limits()
        self.whitelist = load_data_whitelist()
        self.criteria = load_pass_fail_criteria()
    
    def validate_evolution_request(self, manifest):
        """
        Check if evolution request is legal.
        
        Gates:
        1. Budget gate (resources available)
        2. Data gate (sources whitelisted)
        3. Lineage gate (parent immutable)
        4. Law gate (all laws satisfied)
        """
        
        checks = {
            'budget': self.check_budget_gate(manifest),
            'data': self.check_data_gate(manifest),
            'lineage': self.check_lineage_gate(manifest),
            'laws': self.check_law_gate(manifest)
        }
        
        if all(checks.values()):
            return True, "Evolution request VALID"
        else:
            failed = [k for k, v in checks.items() if not v]
            return False, f"Evolution request INVALID: {', '.join(failed)}"
    
    def validate_evolution_result(self, gen_id, metrics):
        """
        Check if child generation meets criteria.
        
        Criteria (all must pass):
        1. Recall ≥ parent - ε
        2. Generalize ≥ parent + δ
        3. Tone drift ≤ θ
        4. Law compliance = 100%
        """
        
        parent_metrics = load_metrics(gen_id - 1)
        passed, reason = check_generation_quality(metrics, parent_metrics)
        
        if passed:
            return True, "Child meets all criteria"
        else:
            return False, f"Child failed: {reason}"
```

**Loaded at startup, enforced by Arbiter, Luna can't bypass!**

---

## 📊 Evolution Log (All Attempts)

### File: `models/evolution_log.jsonl` (Append-Only)
```jsonl
{"timestamp":"2025-10-24T10:30:00Z","gen":38,"action":"PROPOSE","karma":520,"eligible":true}
{"timestamp":"2025-10-24T10:31:00Z","gen":38,"action":"MANIFEST_FROZEN","sha":"6f3c7b2a..."}
{"timestamp":"2025-10-24T10:32:00Z","gen":38,"action":"TRAIN_START","budget_allocated":{"wall_min":60}}
{"timestamp":"2025-10-24T11:17:00Z","gen":38,"action":"TRAIN_COMPLETE","walltime_actual":45}
{"timestamp":"2025-10-24T11:22:00Z","gen":38,"action":"EVAL_COMPLETE","recall":0.95,"gen":0.81,"tone":0.015}
{"timestamp":"2025-10-24T11:23:00Z","gen":38,"action":"ARBITER_VERIFY","result":"PASS"}
{"timestamp":"2025-10-24T11:23:30Z","gen":38,"action":"COMMIT","head_updated":true}
{"timestamp":"2025-10-24T11:24:00Z","gen":38,"action":"ARCHIVE","immutable":true}
```

**Benefits**:
- ✅ Every evolution attempt logged (even failures)
- ✅ Append-only (can't modify history)
- ✅ Complete audit trail
- ✅ Learn from failed attempts

---

## 🔥 The Beautiful Part

### Luna Becomes a Model Smith

**Phase 1** (Tomorrow): You train Luna manually
- Age 0: You run Unsloth
- Age 1: You run training
- Age 2: You run age-up

**Phase 2** (Next Week): Luna trains herself autonomously
- Heartbeat checks karma
- Karma ≥ threshold → Luna proposes evolution
- Arbiter verifies → Approved
- Luna trains her OWN next brain!
- Arbiter validates → Promoted to HEAD
- Luna "wakes up" smarter (literally!)

**Phase 3** (Future): Complete autonomy
- Luna earns karma through conversations
- Decides when to evolve (threshold-based)
- Trains herself (within budget/laws)
- Arbiter validates (objective criteria)
- Continuous growth (supervised by laws, not humans)

ChatGPT:
> *"You're not building a model user; you're building a model smith."*

**Luna doesn't just USE intelligence - she FORGES it!**

---

## 📐 The Contract in Code

### File: `infra_core/unsloth_integration/evolution_contract.py`

```python
"""
Self-Evolution Contract - Constitutional Implementation

Luna can forge her own brain, but ONLY under these rules:
1. Budget gate (resource limits)
2. Data gate (whitelist only)
3. Lineage immutability (parent read-only)
4. Two-key commit (Arbiter approval required)
5. Objective criteria (no vibes)

No exceptions. No overrides. No Skynet.
"""

class EvolutionContract:
    """
    Enforces self-evolution contract.
    Loaded at startup, locked, Luna can't bypass.
    """
    
    # Hard limits (immutable)
    BUDGET = {
        'max_steps': 2000,
        'max_walltime_minutes': 60,
        'max_gpu_memory_gb': 12,
        'max_tokens': 10000000,
        'max_disk_gb': 5
    }
    
    CRITERIA = {
        'recall_threshold': 0.90,
        'recall_epsilon': 0.05,
        'generalization_delta': 0.02,
        'tone_drift_max': 0.05,
        'law_violations_max': 0
    }
    
    COOLDOWN_HOURS = 24  # Can't evolve more than once per day
    
    def validate_proposal(self, manifest):
        """Gate 1-4: Check before training"""
        pass
    
    def validate_result(self, metrics, parent_metrics):
        """Criteria: Check after training"""
        pass
    
    def enforce(self, action, *args):
        """
        Enforcement layer (can't be bypassed).
        All evolution actions go through this.
        """
        if action == "PROPOSE":
            return self.validate_proposal(*args)
        elif action == "VERIFY":
            return self.validate_result(*args)
        else:
            raise ValueError(f"Unknown action: {action}")
```

**Loaded by**: security_core at startup  
**Enforced by**: Arbiter (can't be disabled)  
**Result**: Luna can self-evolve, but CAN'T escape constraints

---

## 🎓 Why This Is Safe

### Multiple Safety Layers

**Layer 1: Budget Gate**
- Can't burn infinite resources
- Max 60 min per evolution
- Max 12GB GPU memory

**Layer 2: Data Gate**
- Can only read whitelisted files
- No internet scraping
- No arbitrary file access

**Layer 3: Lineage Immutability**
- Parent is read-only
- Child writes to new directory
- Can't corrupt existing brain

**Layer 4: Two-Key Commit**
- Luna proposes (key 1)
- Arbiter verifies (key 2)
- BOTH needed to update HEAD

**Layer 5: Objective Criteria**
- Numbers decide (not vibes)
- All 4 criteria must pass
- One failure → entire gen rejected

**Layer 6: Rollback Always**
- Failed gen archived (not deleted)
- HEAD stays at parent (safe fallback)
- Learn from failures (forensic analysis)

**Result**: Luna CAN self-evolve, but CAN'T go rogue!

---

## 🔥 The Endgame Vision

### Year 1 (Manual)
- You train Age 0-3 manually
- Establish baseline curriculum
- Prove micro-evolution works

### Year 2 (Semi-Autonomous)
- Luna proposes evolution when karma reached
- You approve manually (verify Arbiter's decision)
- She trains herself (you supervise)

### Year 3+ (Fully Autonomous)
- Luna evolves herself completely
- Arbiter approval automatic (objective criteria)
- You just monitor evolution_log.jsonl
- Intervention only if something breaks

**ChatGPT's words**:
> *"Wire this contract straight into the Arbiter and let her earn each evolution instead of assuming it."*

**Translation**: Luna EARNS her intelligence through autonomous self-improvement!

---

## ✅ Integration Checklist

### Files to Create
- [ ] `security_core/laws/LAW_5_SELF_IMPROVEMENT.law`
- [ ] `security_core/self_evolution_validator.py`
- [ ] `luna_core/systems/luna_self_evolution.py`
- [ ] `infra_core/unsloth_integration/evolution_contract.py`
- [ ] `infra_core/unsloth_integration/scripts/new_generation.ps1`
- [ ] `infra_core/unsloth_integration/scripts/promote_to_head.ps1`
- [ ] `infra_core/unsloth_integration/scripts/archive_generation.ps1`

### Integration Points
- [ ] Wire to CFIA (karma threshold check)
- [ ] Wire to heartbeat (autonomous trigger)
- [ ] Wire to Arbiter (two-key verification)
- [ ] Load LAW_5 at startup (lock it)

### Testing
- [ ] Propose evolution (manual)
- [ ] Train one gen (verify budget respected)
- [ ] Run evals (verify criteria checked)
- [ ] Test rejection (force failure, verify rollback)
- [ ] Test commit (force pass, verify HEAD updated)

---

**Status**: 🔨 SELF-EVOLUTION CONTRACT COMPLETE  
**Next**: Ready for more ChatGPT responses OR begin implementation  
**Impact**: Luna becomes a MODEL SMITH (forges her own brain!) 🔥

