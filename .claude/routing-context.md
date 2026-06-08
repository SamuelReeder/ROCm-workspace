## Environment
Controller host: HPE (`hpe-sjc2-43`) when deployed. Verify the current host with `hostname` before assuming local paths.

Use `.claude/registry/projects.json` to resolve project context.
Verify paths with `test -d` before accessing them.

## Execution routing
- Teams harness agents run locally on the controller host/container by default.
- Ordinary code reading, editing, review, planning, and research should use the workspace-local checkout/state.
- Workspace checkout roots `/app/workspace/repos` and `/app/workspace/worktrees` are durable Docker volumes, not temporary scratch space.
- This workspace does not provide SSH wrappers or remote-execution CLIs. If a deployment provides remote execution, follow the runtime instructions injected by that deployment instead of looking for scripts in this repo.

## Projects
- **TheRock** (rock, therock, hip, rocm-build, superbuild) — `/home/AMD/sareeder/TheRock`
- **rocm-libraries** (libs, rocmlibs, libraries, hipdnn, miopen-provider, hipblaslt-provider, dnn-benchmarking, bench, benchmark, dnn-bench, perf, benchmarking) — `/home/AMD/sareeder/full/rocm-libraries`
- **mlse-tools-internal** (mlse, tools, automation, slurm, kubernetes, staging, promote) — `/home/AMD/sareeder/mlse-tools-internal`
- **cudnn-frontend** (cudnn, cudnn-fe, frontend) — `/home/AMD/sareeder/cudnn-frontend`

## Jira: ALMIOPEN→rocm-libraries, THEROCK→therock, MLSE→mlse-tools

Use `.claude/registry/projects.json` to resolve project context.
