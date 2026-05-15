## Environment
Host: **MKMSAREEDER02** (linux, x64). Home: `/home/sareeder`

Check `.claude/registry/machines.json` for machine-specific context.
Verify paths with `test -d` before accessing — SSH may be needed.

## Projects
- **TheRock** (rock, therock, hip, rocm-build, superbuild) — `/home/AMD/sareeder/TheRock`
- **rocm-libraries** (libs, rocmlibs, libraries, hipdnn, miopen-provider, hipblaslt-provider) — `/home/AMD/sareeder/full/rocm-libraries`
- **mlse-tools-internal** (mlse, tools, automation, alola, slurm, kubernetes, staging, promote) — `/home/AMD/sareeder/mlse-tools-internal`
- **dnn-benchmarking** (bench, benchmark, dnn-bench, perf, benchmarking) — `/home/AMD/sareeder/dnn-benchmarking`
- **cudnn-frontend** (cudnn, cudnn-fe, frontend) — `/home/AMD/sareeder/cudnn-frontend`

## Machines
- **Alola Cluster** (nodes: 03, 04) — SSH: `scripts/ssh/ssh-alola.sh <node> "<cmd>"`, context: `docs/machines/alola.md`

## Jira: ALMIOPEN→rocm-libraries, THEROCK→therock, MLSE→mlse-tools

Use `/goto <project>` to load full project context. Read machine context docs before working on remote machines.