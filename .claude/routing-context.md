## Environment
Controller host: HPE (`hpe-sjc2-43`) when deployed. Verify the current host with `hostname` before assuming local paths.

Check `.claude/registry/machines.json` for machine-specific context.
Verify paths with `test -d` before accessing — SSH may be needed.

## Execution routing
- Teams harness agents run locally on the HPE/controller host by default.
- Ordinary code reading, editing, review, planning, and research should use the HPE-local checkout/state.
- ROCm builds/tests/benchmarks, CMake/Ninja/ctest, provider verification, hipcc, rocminfo, rocm-smi, and GPU runtime work must run through durable Alola sessions, not directly on HPE.
- Use `workspace/scripts/alola-session run -- <command>` for the default Alola login-node enroot session (`node=03`, `asic=gfx90a`).
- Use `workspace/scripts/alola-session run --target <asic> -- <command>` for a non-exclusive GPU allocation. GPU constraints default to `MARKHAM&<ASIC_UPPER>` and images follow `/cluster/images/hipdnn/hipdnn_latest_<asic>.sqsh`.

## Projects
- **TheRock** (rock, therock, hip, rocm-build, superbuild) — `/home/AMD/sareeder/TheRock`
- **rocm-libraries** (libs, rocmlibs, libraries, hipdnn, miopen-provider, hipblaslt-provider) — `/home/AMD/sareeder/full/rocm-libraries`
- **mlse-tools-internal** (mlse, tools, automation, alola, slurm, kubernetes, staging, promote) — `/home/AMD/sareeder/mlse-tools-internal`
- **dnn-benchmarking** (bench, benchmark, dnn-bench, perf, benchmarking) — `/home/AMD/sareeder/dnn-benchmarking`
- **cudnn-frontend** (cudnn, cudnn-fe, frontend) — `/home/AMD/sareeder/cudnn-frontend`

## Machines
- **Alola Cluster** (nodes: 03, 04) — SSH: `scripts/ssh/ssh-alola.sh <node> "<cmd>"`, session CLI: `workspace/scripts/alola-session`, context: `docs/machines/alola.md`

## Jira: ALMIOPEN→rocm-libraries, THEROCK→therock, MLSE→mlse-tools

Use `.claude/registry/projects.json` to resolve project context. Read machine context docs before working on remote machines.
