# Forbidden Paths

Repo-specific files and directories that must not be staged or committed unless the human explicitly changes the rule.

- `dist/`
- `.cache/`
- `.venv/`
- `node_modules/`
- `frontend/dist/`
- `native/build/`
- logs
- recordings
- model weight caches
- secrets
- `ai-md-condidates/` additions, modifications, or deletions unless explicitly requested

The cycle validator checks common forbidden paths:

```bash
scripts/ai-cycle-validate.sh
```

