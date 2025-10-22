# Blackwall File Structure Setup

## One Source of Truth: /core/

All critical Blackwall files now live in the `/core/` directory. There are **no symlinks or file copies** in `/lexicon/` or elsewhere. This is the simplest, most robust setup.

### How to Import

Always import from `core`:
- `from core.llm_service import LLMService`
- `from core.error_handler import error_handler`
- `from core.blackwall_pipeline import BlackwallPipeline`

Or, if your `sys.path` includes `/core/`:
- `import llm_service`
- `import error_handler`

### Do NOT use or expect:
- `from lexicon.llm_service import ...`
- `from lexicon.error_handler import ...`
- Any symlinks or file copies in `/lexicon/`

### Why?
- **Simplicity:** Only one copy to maintain.
- **No import confusion:** Python always finds the right file.
- **No legacy hacks:** All code is modern and maintainable.

### Verifying the Setup

To verify your file structure is correct:

```bash
ls core/llm_service.py core/error_handler.py core/blackwall_pipeline.py
```

If those files exist, you are good to go!

### Troubleshooting

If you see import errors, make sure:
- You are importing from `core`.
- You do **not** have old symlinks or file copies in `/lexicon/`.
- Your `sys.path` includes the project root and/or `/core/`.

---

**This is the recommended and supported structure for all future Blackwall development.**
