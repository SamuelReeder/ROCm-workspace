# Python Style Guide

Coding standards for Python across ROCm workspace projects (mlse-tools, dnn-benchmarking, TheRock scripts).

## Core Principles

### 1. Fail Fast, Fail Loud
Raise exceptions immediately on invalid input. Never silently return `None` or empty results.

```python
# Good
def get_device(device_id: int) -> Device:
    if device_id < 0:
        raise ValueError(f"Invalid device_id: {device_id}")
    ...

# Bad
def get_device(device_id: int) -> Device | None:
    if device_id < 0:
        return None  # Caller has no idea why
```

### 2. Use Dataclasses, Not Tuples or Dicts
Structured data gets a dataclass. Tuples are for genuinely unnamed pairs.

```python
# Good
@dataclass
class BenchmarkResult:
    kernel: str
    elapsed_ms: float
    memory_mb: float

# Bad
result = ("conv2d", 12.5, 256.0)  # What is 256.0?
result = {"kernel": "conv2d", "elapsed_ms": 12.5}  # No validation
```

### 3. Modern Type Syntax
Use Python 3.10+ union syntax. No `Optional`, no `Union`.

```python
# Good
def find_config(name: str) -> Config | None: ...
def process(data: list[int] | tuple[int, ...]): ...

# Bad
def find_config(name: str) -> Optional[Config]: ...
def process(data: Union[List[int], Tuple[int, ...]]): ...
```

### 4. Pathlib Over os.path
Use `pathlib.Path` for all path operations.

```python
# Good
config_path = Path(project_dir) / "build" / "config.cmake"
if config_path.exists():
    content = config_path.read_text()

# Bad
config_path = os.path.join(project_dir, "build", "config.cmake")
if os.path.exists(config_path):
    with open(config_path) as f:
        content = f.read()
```

### 5. Explicit Imports
Import specific names. No wildcard imports. No aliasing standard modules to cryptic names.

```python
# Good
from pathlib import Path
from collections import defaultdict

# Bad
from pathlib import *
import collections as c
```

### 6. String Formatting: f-strings
Use f-strings for interpolation. Use `.format()` only for reusable templates.

```python
# Good
msg = f"Build failed for {component} in {elapsed:.1f}s"

# Bad
msg = "Build failed for %s in %.1fs" % (component, elapsed)
msg = "Build failed for {} in {:.1f}s".format(component, elapsed)
```

### 7. Guard Clauses Over Nested Ifs
Return/raise early to reduce nesting.

```python
# Good
def validate_gpu(device_id: int) -> GPUInfo:
    if device_id < 0:
        raise ValueError("Negative device ID")
    info = query_rocm(device_id)
    if info is None:
        raise RuntimeError(f"GPU {device_id} not found")
    return info

# Bad
def validate_gpu(device_id: int) -> GPUInfo:
    if device_id >= 0:
        info = query_rocm(device_id)
        if info is not None:
            return info
        else:
            raise RuntimeError(f"GPU {device_id} not found")
    else:
        raise ValueError("Negative device ID")
```

### 8. Subprocess: Use list Form
Always pass commands as lists, never shell strings.

```python
# Good
result = subprocess.run(
    ["ninja", "-C", str(build_dir), target],
    capture_output=True, text=True, check=True,
)

# Bad
result = subprocess.run(
    f"ninja -C {build_dir} {target}",
    shell=True, capture_output=True,
)
```

### 9. Context Managers for Resources
Use `with` for files, connections, temporary directories.

```python
# Good
with tempfile.TemporaryDirectory() as tmpdir:
    build_path = Path(tmpdir) / "build"
    run_cmake(build_path)

# Bad
tmpdir = tempfile.mkdtemp()
try:
    build_path = os.path.join(tmpdir, "build")
    run_cmake(build_path)
finally:
    shutil.rmtree(tmpdir)
```

### 10. Constants at Module Level
Define constants at the top of the module, not inside functions.

```python
# Good
DEFAULT_BUILD_JOBS = 8
ROCM_DEFAULT_PATH = Path("/opt/rocm")

def configure_build(jobs: int = DEFAULT_BUILD_JOBS): ...

# Bad
def configure_build(jobs: int = 8): ...  # Magic number
```

### 11. Logging Over Print
Use `logging` for operational output. Reserve `print` for CLI user-facing output.

```python
# Good
import logging
logger = logging.getLogger(__name__)
logger.info("Build started for %s", component)

# Bad (in library/automation code)
print(f"Build started for {component}")
```

### 12. Docstrings for Public APIs Only
Document public functions and classes. Skip docstrings for internal/private helpers if the name and signature are self-explanatory.

```python
# Good — public API
def run_benchmark(config: BenchmarkConfig) -> list[BenchmarkResult]:
    """Execute benchmarks defined in config and return results."""
    ...

# Good — private helper, no docstring needed
def _parse_csv_row(row: list[str]) -> BenchmarkResult:
    ...
```

## Testing

- Use `pytest` exclusively (no `unittest.TestCase`)
- Name test files `test_<module>.py`
- Name test functions `test_<behavior>`
- Use fixtures for shared setup, not `setUp`/`tearDown`
- Mark GPU-dependent tests with `@pytest.mark.gpu`

## Project-Specific Notes

### dnn-benchmarking
- Editable install: `pip install -e .`
- Non-GPU tests: `pytest -m "not gpu"`

### mlse-tools
- Uses system Python (no venv)
- Scripts are standalone — keep imports minimal

### TheRock scripts
- Venv at `.venv` in each worktree
- Scripts interact with CMake build system — use `subprocess.run` with list form
