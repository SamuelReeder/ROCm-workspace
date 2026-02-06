# Debugging Tips

Techniques for debugging across ROCm workspace projects.

## CMake Debug Output

### TheRock / rocm-libraries

Enable verbose CMake configuration:
```bash
cmake -S . -B build -DCMAKE_VERBOSE_MAKEFILE=ON
```

Print CMake variables during configuration:
```cmake
message(STATUS "Variable: ${MY_VAR}")
```

Trace CMake processing:
```bash
cmake --trace-expand -S . -B build 2>&1 | grep "pattern"
```

### Ninja verbose build
```bash
ninja -C build -v target_name    # Show full compiler commands
ninja -C build -j1 target_name   # Single-threaded for readable output
```

## Dependency Debugging

### Find what pulls in a dependency
```bash
# In TheRock or rocm-libraries build dir:
ninja -C build -t deps target_name
ninja -C build -t graph target_name | dot -Tpng -o deps.png
```

### CMake target dependency graph
```bash
cmake --graphviz=deps.dot build/
```

### Check shared library dependencies
```bash
ldd build/lib/libhipdnn.so
readelf -d build/lib/libhipdnn.so | grep NEEDED
```

## ROCm Runtime Debugging

### GPU visibility
```bash
rocm-smi                          # GPU status and utilization
rocminfo                          # Detailed GPU info
hip-config --check                # HIP configuration check
```

### HIP runtime debug
```bash
export HIP_VISIBLE_DEVICES=0      # Limit to specific GPU
export AMD_LOG_LEVEL=4             # Maximum HIP logging
export HIP_LAUNCH_BLOCKING=1      # Synchronous kernel launches
```

### MIOpen debug
```bash
export MIOPEN_ENABLE_LOGGING=1     # Log MIOpen API calls
export MIOPEN_ENABLE_LOGGING_CMD=1 # Log MIOpen driver commands
export MIOPEN_LOG_LEVEL=6          # Maximum logging
```

## Python Debugging

### dnn-benchmarking / mlse-tools
```bash
# Run single test with verbose output
pytest -xvs tests/test_specific.py::test_name

# Debug with pdb
pytest --pdb tests/test_specific.py

# Check import issues
python -c "import module_name; print(module_name.__file__)"
```

### Virtual environment issues
```bash
# Verify correct venv is active
which python3
python3 -m site --user-site

# Reinstall from scratch
rm -rf .venv && python3 -m venv .venv
source .venv/bin/activate && pip install -r requirements.txt
```

## Build Failures

### Common patterns

**Missing ROCm component**: Check `THEROCK_DIST_DIR` points to a completed build:
```bash
ls $THEROCK_DIST_DIR/lib/ | grep <component>
```

**ABI mismatch**: Ensure all components built with same compiler:
```bash
readelf -p .comment build/lib/libfoo.so
```

**Out-of-memory during build**: Reduce parallelism:
```bash
ninja -C build -j4 target_name   # Instead of default (all cores)
```
