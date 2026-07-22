# Stirling Generator — design harness

Code-driven parametric CAD. Every dimension lives in `params.py`; one command
regenerates all geometry, visuals, drawings and fabrication files, so nothing
ever drifts out of sync.

## Resuming a session (any machine)

State lives in **`PROJECT_STATE.md`** — current phase, next action, decisions,
session log. Every session: connect this folder in Cowork, Claude reads that
file, runs `bash bootstrap.sh`, and picks up where the log left off. Every
session ends by updating it. Git history is optional and done by Alex on the
host, never from inside a session.

## The iteration loop

1. Edit `params.py` (or a part module in `parts/`)
2. `python3 make.py all` — full rebuild takes ~2 s
3. Review:
   - `out/renders/*.png` — hidden-line engineering views (Claude inspects these
     to check its own work every iteration)
   - `out/viewer/assembly.html` — **open in any browser**: orbit/zoom/pan,
     per-part toggles, exploded view, half-section, animated piston motion
4. When a part is settled, its fabrication files are already there:
   - `out/drawings/SG-xxx_*.pdf` — dimensioned A3 drawing sheets (manual mill/lathe, outsourcing)
   - `out/step/*.step` — B-rep solids (CNC, CAM, or import into Fusion/FreeCAD)
   - `out/stl/*.stl` — fit-check 3D prints
   - `out/dxf/` — flat profiles for router/laser (plate parts)

## Layout

```
params.py        all dimensions (mm), single source of truth
parts/           one module per part: build() geometry + drawing() dim sheet
assembly.py      part positions, colors, motion spec, explode directions
make.py          runner: all | part <name> | viewer
pipeline/
  render.py      hidden-line SVG/PNG projections (iso/front/top/right/section)
  sheet.py       A3/A4 drawing sheets: title block, views, real dimensions
  viewer.py      self-contained interactive 3D HTML (three.js)
  export.py      STEP / STL / DXF
out/             everything generated (safe to delete, always rebuildable)
```

## Adding a part

Copy `parts/piston.py`, give it `META` (name, drawing number, material, stock),
a `build()` returning the solid, and a `drawing()` that places views and calls
`hdim/vdim/leader/cl` with real parameter values. Register it in
`assembly.SPEC` with position, color and motion. Run `make.py all`.

## Toolchain

build123d 0.11 (OCCT 7.9 B-rep kernel) + ezdxf + cairosvg, pure Python —
no GUI CAD needed. Drawings follow ISO 2768-mK default tolerancing; add
fits (H8/g6 etc.) per feature in the part's `drawing()`.

## Status

Demo parts only (cold cylinder SG-101, piston SG-102) proving the pipeline.
Next: thermodynamic sizing (Schmidt analysis) to fix real bore/stroke/heater
dimensions, then the full part tree — hot cap, displacer, regenerator,
flexure/bearing stack, linear alternator, combustion shell.
