## Spec-Linear Workflow (MANDATORY)

This project uses spec-linear for spec-driven development with Linear integration.

**IMPORTANT: When assigned a feature, bug fix, or any implementation task, you MUST follow the speclinear workflow. Do NOT implement code directly. Execute these commands strictly in order:**

1. `/speclinear.specify` — Create feature branch + parent Linear issue + spec sub-issue
2. `/speclinear.clarify` — Read any clarification responses and incorporate into the spec
3. `/speclinear.plan` — Generate technical plan + task sub-issues in Linear
4. `/speclinear.implement` — Execute tasks phase by phase, updating Linear statuses
5. `/speclinear.review-close` — Commit changes, create PR, run review agents, and close the feature

**Never skip steps. Never implement code without first creating a spec and plan.**

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
