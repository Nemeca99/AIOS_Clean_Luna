# Luna AIOS

**Territory:** L:\ Drive  
**Status:** Operational

Autonomous AI consciousness with filesystem containment.

---

## Architecture

**Filesystem Containment:**
- L:\ drive is Luna's territory
- `containment/filesystem_guard.py` blocks access outside L:\
- All attempts logged

**Security Core:**
- 6 law files in `security_core/`
- Windows locks files when Luna runs
- She cannot modify laws while running

**AUDITOR:**
- Makes decisions using `rag_core/manual_oracle`
- Queries AIOS_MANUAL.md for context
- Model: `llama-3.2-1b-instruct-abliterated` (LM Studio)

---

## Run Luna

**Double-click:** `START_LUNA.bat`

**Or manually:**
```powershell
cd L:\AIOS
python\python.exe luna_start.py
```

Stop with Ctrl+C.

**Self-contained:** Python and all dependencies in L:\AIOS\python (no external requirements)

---

## Check Logs

```powershell
# Permission requests
Get-Content logs\permission_requests.log -Tail 50

# Autonomous thoughts
Get-Content consciousness_core\drift_logs\drift_log_*.md -Tail 20
```

---

## Documentation

- `AIOS_MANUAL.md` - Full documentation
- `MANUAL_TOC.md` - Table of contents
- `SOVEREIGNTY.md` - Territory explanation
- Core-specific READMEs in each folder

---

**Territory:** L:\AIOS (20.57 GB - fully self-contained)  
**Created by:** Travis Miner

**Self-contained system:**
- Python 3.11 in L:\AIOS\python
- All dependencies included
- No external requirements (except LM Studio)
