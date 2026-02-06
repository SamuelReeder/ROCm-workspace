---
name: cmake-build
description: Use this skill when the user asks to build, compile, configure, run ninja, rebuild components, expunge, or discusses CMake configuration, build targets, or compilation for TheRock or rocm-libraries projects. Activates on keywords like ninja, cmake, build, compile, component names (miopen, hipDNN, rocblas, etc.).
version: 1.0.0
---

# CMake Superbuild Patterns

## TheRock Build System

TheRock uses an ExternalProject-based superbuild with component targets.

### Build Directory Structure
```
<worktree>/build/
├── <component>/
│   ├── build/    # CMake build tree
│   ├── stage/    # Install tree (this component only)
│   ├── dist/     # stage/ + runtime dependencies merged
│   └── stamp/    # Incremental build tracking
└── dist/rocm/    # Unified ROCm installation
```

### Component Targets

| Target | Purpose |
|--------|---------|
| `ninja <component>` | Full build (configure + build + stage + dist) |
| `ninja <component>+build` | Rebuild after source changes |
| `ninja <component>+dist` | Update artifacts without rebuild |
| `ninja <component>+expunge` | Clean slate rebuild |

### Common Components
hipify, clr, rocblas, rocfft, miopen, hipDNN, composable_kernel, rccl, rocprofiler

### TheRock Configuration

These configurations are for TheRock only (not rocm-libraries).

**hipDNN + MIOpen Provider development:**
```bash
cmake -B build -GNinja \
  -DTHEROCK_ENABLE_ALL=OFF \
  -DTHEROCK_ENABLE_HIPDNN=ON \
  -DTHEROCK_ENABLE_MIOPEN_PROVIDER=ON \
  -DMIOPEN_USE_COMPOSABLEKERNEL=ON \
  -DTHEROCK_AMDGPU_FAMILIES=gfx90a
```

**Full ROCm build:**
```bash
cmake -B build -GNinja \
  -DTHEROCK_AMDGPU_FAMILIES=gfx90a \
  -DCMAKE_C_COMPILER_LAUNCHER=ccache \
  -DCMAKE_CXX_COMPILER_LAUNCHER=ccache
```

### Fetching Sources
```bash
./build_tools/fetch_sources.py
```

## rocm-libraries Build System

Standard CMake with Ninja:
```bash
cd /home/AMD/sareeder/full/rocm-libraries
cmake -B build -GNinja
ninja -C build           # Build all
ninja -C build check     # Run all tests
ninja -C build unit-check # Unit tests only
ninja -C build format    # Auto-format code
ninja -C build clang-tidy # Static analysis
```

### Test Binaries
Located at: `build/bin/`
- hipdnn_backend_tests
- hipdnn_frontend_tests
- miopen_plugin_integration_test

## Worktree Build Isolation

**CRITICAL**: Each worktree has its own build directory. Never reference another worktree's build.

| Worktree | Build Path |
|----------|------------|
| TheRock main | /home/AMD/sareeder/TheRock/build |
| therock-consumption | /home/AMD/sareeder/therock-consumption/build |
| therock-miopen-plugin-move | /home/AMD/sareeder/therock-miopen-plugin-move/build |
| rocm-libraries | /home/AMD/sareeder/full/rocm-libraries/build |

## Build Commands

Always use `-C` with absolute path:
```bash
ninja -C /home/AMD/sareeder/TheRock/build <target>
ninja -C /home/AMD/sareeder/therock-consumption/build <target>
ninja -C /home/AMD/sareeder/full/rocm-libraries/build <target>
```
