---
name: python-dev
description: Use this skill when the user asks to run pytest, install requirements, activate venv, run python scripts, or discusses Python development, virtual environments, pip, or testing for TheRock, mlse-tools, or dnn-benchmarking projects.
version: 1.0.0
---

# Python Development Patterns

## Virtual Environment Locations

| Project | Venv Path |
|---------|-----------|
| TheRock (main) | /home/AMD/sareeder/TheRock/.venv |
| therock-consumption | /home/AMD/sareeder/therock-consumption/.venv |
| therock-miopen-plugin | /home/AMD/sareeder/therock-miopen-plugin-move/.venv |
| dnn-benchmarking | /home/AMD/sareeder/dnn-benchmarking/.venv |
| mlse-tools | None (use system Python) |
| rocm-libraries | None (C++ project) |

## Running Python Commands

Always activate venv or use venv's Python directly:

### Option 1: Inline activation
```bash
source /home/AMD/sareeder/TheRock/.venv/bin/activate && python3 script.py
```

### Option 2: Direct path
```bash
/home/AMD/sareeder/TheRock/.venv/bin/python3 script.py
```

### Option 3: For pip
```bash
/home/AMD/sareeder/TheRock/.venv/bin/pip install -r requirements.txt
```

## pytest Patterns

### TheRock
```bash
source /home/AMD/sareeder/TheRock/.venv/bin/activate
pytest /home/AMD/sareeder/TheRock/tests/
```

### dnn-benchmarking
```bash
cd /home/AMD/sareeder/dnn-benchmarking
source .venv/bin/activate
pytest -m "not gpu"              # Non-GPU tests only
pytest                            # All tests (requires hipDNN)
pytest --cov=dnn_benchmarking    # With coverage
pytest -k "test_name"            # Filter by name
```

## Environment Variables

For hipDNN/ROCm Python work:
```bash
export THEROCK_DIST_DIR=/home/AMD/sareeder/TheRock/build/dist/rocm
export HIPDNN_PLUGIN_DIR=<build>/lib/hipdnn_plugins/engines
export LD_LIBRARY_PATH=$THEROCK_DIST_DIR/lib:$LD_LIBRARY_PATH
```

## Creating New Venv

When setting up a worktree or project:
```bash
cd <project-path>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists
pip install -e .  # If pyproject.toml exists (editable install)
```

## Worktree Venv Isolation

**CRITICAL**: Each worktree must have its own .venv. Never share venvs between worktrees.

If entering a worktree without .venv, create one:
```bash
cd /home/AMD/sareeder/therock-consumption
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
