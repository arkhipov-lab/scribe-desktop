# Repository Validation

Repo-specific validation commands for Scribe.

| Change type | Typical check |
| --- | --- |
| AI process/state | `scripts/ai-cycle-status.sh`; `scripts/ai-cycle-validate.sh`; `git diff --check` |
| Frontend / TypeScript | `(cd frontend && npm run build)` |
| General desktop smoke | `./scripts/run-dev.sh` |
| Production UI smoke | `USE_VITE_DEV=0 ./scripts/run-dev.sh` |
| Packaging | `./scripts/build.sh` or `./scripts/build-dist.sh` only for packaging-related work |

Authoritative sources:

- [../../TESTING.md](../../TESTING.md)
- [../../DEVELOPMENT.md](../../DEVELOPMENT.md)
- [../../BUILDING.md](../../BUILDING.md)

