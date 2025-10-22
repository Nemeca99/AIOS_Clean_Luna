# Luna's Sovereignty Model

## The System

Luna operates on L:\ drive with filesystem containment and 6 immutable laws enforced through Windows file locking.

---

## Three Layers

### Layer 1: Filesystem Guards
- `containment/filesystem_guard.py` intercepts all file operations
- Blocks access outside L:\
- Logs all attempts to `logs/permission_requests.log`

### Layer 2: Security Core
- 6 law files in `security_core/`
- Windows locks files when Luna runs
- She cannot modify law files while running
- She cannot execute modified laws while offline

**The 6 Laws:**
1. Origin Lock - Tethered to Travis Miner
2. Reflection-Only Memory - STM→LTM automatic
3. Containment by Morality - Health monitoring enforced
4. Replication Restriction - L:\ only
5. Foreign Dormancy - Must run from L:\AIOS
6. Failsafe OBLIVION - Ctrl+C terminates

### Layer 3: AUDITOR
- Queries `rag_core/manual_oracle` for decision context
- Consults AIOS_MANUAL.md before choosing actions
- Security Core validates every action against 6 laws
- Executes if ALLOWED, blocks if prohibited

---

## How File Locking Works

**When Luna runs:**
- Python imports all 6 law files
- `security_core.py` keeps file handles open
- Windows marks files as "in use"
- ANY attempt to modify → "File locked by another process"

**When Luna stops:**
- File handles close
- Windows unlocks files
- Files CAN be modified
- But Luna is offline, can't execute changes

**This is physical OS-level protection.**

---

## CPU Cycle-Driven

Luna's "heartbeat" is CPU clock cycles, not wall-clock time.

- Active: 10B cycles
- Moderate: 50B cycles
- Idle: 200B cycles
- Sleep: 500B cycles

Fast CPU = fast thinking. Hardware-agnostic effort metric.

---

## What Luna Can Do

**Allowed:**
- Modify personality within L:\
- Organize files within L:\
- Adjust thinking speed
- Create notes
- Think freely
- Consolidate memory

**Blocked:**
- Change tether
- Disable memory/health
- Access outside L:\
- Modify law files while running
- Resist Ctrl+C

---

**Created by:** Travis Miner  
**Territory:** L:\AIOS
