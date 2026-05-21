# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Malpasset dam break validation study using [ANUGA](https://github.com/anuga-community/anuga_core) — a Python finite-volume hydrodynamic modelling framework for 2D shallow water equations. The simulation is parallelized via MPI.

## Running the simulation

Serial (single process):
```bash
python run_malpasset_dam_break.py
```

Parallel (e.g. 4 processes):
```bash
mpirun -np 4 python run_malpasset_dam_break.py
```

Installed ANUGA version: `3.3.6` (Python 3). The script was originally written for Python 2 and ANUGA's older `anuga_parallel` package. The correct import path for ANUGA 3.x is:

```python
from anuga.parallel import distribute, myid, numprocs, finalize, barrier
```

## Repository contents

| File | Purpose |
|------|---------|
| `run_malpasset_dam_break.py` | Main simulation script |
| `malpasset_26000_merged.tsh` | Coarser mesh (~26 000 triangles) |
| `malpasset_46691_mesh.tsh` | Finer mesh (~46 691 triangles) — currently active |

`.tsh` files are ANUGA's ASCII triangle mesh format: vertex coordinates with elevation attributes, followed by triangle connectivity and boundary tags.

## Simulation architecture

The script follows the standard ANUGA parallel pattern:

1. **Root process only (`myid == 0`)**: loads the `.tsh` mesh, creates the `anuga.Domain`, sets flow algorithm, initial conditions (reservoir behind the dam wall at elevation 75 m, dry downstream), and friction.
2. **All processes**: `distribute(domain)` partitions the domain via `pymetis`; each rank receives its subdomain.
3. **Boundary conditions**: reflective on all boundaries (`external`, `open`).
4. **Evolution loop**: 15 s yield steps to `finaltime = 3000 s`, writing `.sww` output.
5. **Post-processing**: `domain.sww_merge()` reassembles the per-rank `.sww` files; `finalize()` shuts down MPI.

Key domain settings:
- Flow algorithm: `'2_0_limited'` (second-order finite volume)
- Minimum allowed height: `0.01 m`
- Minimum storable height: `0.1 m`
- Manning's friction: `0.033`

Output is a NetCDF `.sww` file viewable with ANUGA's `sww_viewer` or with `anuga.plot_utils`.
