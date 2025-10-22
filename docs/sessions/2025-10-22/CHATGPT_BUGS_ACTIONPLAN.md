# ChatGPT Triage - Action Plan
**Brutal truth from ChatGPT - now fixing properly**

---

## ✅ BUG #3: Multiple Init Paths [FIXED]
**File**: `luna_core/core/luna_core.py`  
**Fix**: Added singleton pattern with `__new__` and `_initialized` flag  
**Result**: Only ONE "Initializing Unified Luna System" in logs ✅

---

## 🔥 BUG #4: CARMA State Race (0 fragments vs 349 interactions) [NEXT]
**Problem**: CARMA prints "0 fragments" while memory shows "349 interactions"  
**Root cause**: CARMA snapshot taken before restore completes  
**Fix needed**: Force restore sequence:
1. Load CARMA store
2. Verify fragment count
3. THEN expose persona

**File to fix**: `luna_core/core/luna_core.py` - init sequence

---

## 🔥 BUG #5: Experimental Feature Gates Broken [NEXT]
**Problem**: `utils_core.timestamp_validator` missing but code tries to import  
**Fix needed**: Wrap in proper config check:
```python
if config.experimental.voice_mining:
    try:
        from utils_core.timestamp_validator import validate_timestamp
    except ImportError:
        logger.warning("Voice mining disabled: missing dependency")
        config.experimental.voice_mining = False
```

**File to fix**: `luna_core/systems/luna_personality_system.py`

---

## 🔥 BUG #6: Efficiency Path Disabled for Debugging [NEXT]
**Problem**: `EMBEDDER CLEANUP: DISABLED` and `Maximum Impact Density disabled`  
**Result**: RVC gives F grade (efficiency 0.133)  
**Fix needed**: Re-enable for TRIVIAL tier by default

**Files to check**:
- `luna_core/core/response_generator.py`
- Look for debug flags

---

## 🔥 BUG #7: Governor Math Broken for Trivial [NEXT]
**Problem**: "Resource State: critical" for 5-token prompt  
**Fix needed**:
```python
if complexity == "TRIVIAL":
    tte_base = min(tte_base, 64)
    resource_state = "normal"
```

**File**: `luna_core/systems/luna_custom_inference_controller.py`

---

## 🔥 BUG #8: Inbox Scan Not Wired to Heartbeat [CRITICAL]
**Problem**: Challenge cards never discovered in sealed runs  
**Fix needed**: Wire `scan_inbox` to cycle heartbeat, not user prompts  
**Use modulo on cycle_id**, not wall time

**Files**:
- `luna_cycle_agent.py` - already has heartbeat % 200 check
- Verify it's actually calling scan

---

## Priority Order
1. ✅ Multiple init (DONE)
2. 🔥 CARMA state race
3. 🔥 Governor math for trivial
4. 🔥 Efficiency path re-enable
5. 🔥 Experimental feature gates
6. 🔥 Inbox scan wiring

---

## Testing Protocol
After each fix:
```bash
.venv\Scripts\python.exe luna_chat.py "Hi" 2>&1 | Select-String -Pattern "[BUG_PATTERN]"
```

Then count repeats:
```powershell
Select-String -Path test.log -Pattern "Unified Luna System Initialized" | Measure-Object
```

Expected: Count = 1 ✅

---

## Validation Criteria (ChatGPT's Requirements)
- [ ] Exactly ONE "Unified Luna System Initialized"
- [ ] CARMA count BEFORE first "Generating response"
- [ ] NO "Voice mining" warning unless feature enabled
- [ ] TRIVIAL must NOT print "Resource State: critical" for q_len <= 8
- [ ] RVC ≥ 0.6 once cleanup/compression enabled
- [ ] Sealed run: challenge cards discovered via heartbeat

**When all ✅ → Protocol Zero demos will work**

