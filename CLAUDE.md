## Spec-Linear Workflow

This project uses spec-linear for spec-driven development with Linear integration.

### Commands

| Command | Purpose |
|---------|---------|
| `/speclinear.constitute` | Establish project governing principles (constitution) |
| `/speclinear.specify` | Create feature branch + parent Linear issue + spec sub-issue |
| `/speclinear.clarify` | Clarify ambiguities in the spec via Q&A |
| `/speclinear.plan` | Generate technical plan + task sub-issues |
| `/speclinear.implement` | Execute tasks and update Linear statuses |

### Linear Context

- **Team**: Spec Driven Development Demo
- **Project**: demo-python-sdd
- **SDD Labels**: SDD - Feature, SDD - Spec, SDD - Plan, SDD - Task

### Project Conventions

- **Language**: Python 3.13
- **Package Manager**: uv (with `uv.lock` and `pyproject.toml`)
- **Project Type**: CLI + web server (`main.py` CLI, `server.py` web)
- **Virtual Environment**: `.venv/` (managed by uv)
- **Dependencies**: stdlib only (runtime); pytest (dev)
- **Directory Structure**: Flat — `weather.py` (shared logic), `main.py` (CLI), `server.py` (web), `templates/` (HTML), `tests/` (pytest)

## Project Principles

1. **Simplicity** — Prefer the simplest solution; use stdlib first, avoid unnecessary abstractions
2. **Type Safety** — Type hints on all function signatures; use typed structures (`TypedDict`/`dataclass`) over plain dicts; run a type checker
3. **Good Test Coverage** — Test all public functions with pytest; mock external APIs; fast and deterministic tests

Full constitution: `.specify/memory/constitution.md`
