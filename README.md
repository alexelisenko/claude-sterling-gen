# Stirling Generator — 1 kW opposed free-piston, wood-fired

Code-driven parametric CAD for a complete machine: two beta-type
free-piston Stirling engines opposed on a horizontal axis, sharing a
central wood firebox, each driving a moving-magnet linear alternator.
Every dimension lives in `params.py`; one command regenerates all
geometry, visuals, audits and fabrication files, so nothing drifts.

## Resuming a session (any machine)

State lives in **`PROJECT_STATE.md`** — current phase, next action,
decision log, session log. Every session: connect this folder in Cowork,
Claude reads that file, runs `bash bootstrap.sh`, and picks up where the
log left off. Every session ends by updating it. Git is run by Alex on
the host (pull before / commit+push after), never from inside a session.

## The machine (locked design point — sizing scenario E)

- 1000 We pair → 588 W brake per side; helium **20 bar / 50 Hz**
  (shell rated 30 bar); commission on air at 7 bar ≈ 120 We @ 27 Hz.
- Bore 60, piston stroke 24.3 (amp 12.15), displacer stroke 26.7
  leading 70°; Th 873 K / Tk 330 K; pair heat input ~4.2 kW (fire ~7 kW).
- Free pistons: nothing is cranked. Radial support = honed liner +
  PTFE bands (piston) and displacer cylinder + bands (displacer). Axial =
  resonance: working gas ≈ 79 kN/m + dedicated Ø50 center-post gas
  spring ≈ 180 kN/m = 259 kN/m for the 2.62 kg mover at 50 Hz.
- Gas loop per side: expansion space (dome) → heater annulus (finned
  fire tube) → regenerator matrix → cooler insert → cold-head axial
  ports → liner-lip relief groove → compression space. Regenerator and
  cooler sit IN the annulus — all working gas passes through both.
- Cooling water: barbed bosses → annular gallery in the cold head OD
  (outside the bolt circle, closed by an o-ring'd sleeve) → 8 radial
  fingers reaching to 3 mm from the cooler insert.
- Combustion: firebox (log door, slotted grate, ash drawer) below; a
  close shroud (~20 mm over the fin tips) forces flue gas through the
  fins; flue on top. Each bench-assembled engine side slides in
  horizontally dome-first through a 160x150 wall aperture (insertion
  path verified by swept-collision check); saddle blocks then drop in
  under the necks and split panels clamp around the fire tubes.

## Part tree (per side unless noted)

| Dwg | Part | Material | Fabrication |
|-----|------|----------|-------------|
| SG-201 | Hot cap / pressure wall | 310S/253MA | 3-piece TIG weldment: dome, finned fire tube, flanged collar |
| SG-202 | Regenerator matrix | 304 mesh stack | stacked screen rings, 70% porosity |
| SG-203 | Cooler insert | C110 copper | 68 drilled Ø5 axial gas passages (revolver-cylinder), pressed/brazed into cold head |
| SG-204 | Pressure hull | 4130/6082 | one piece, all bores from the two ends (or tube + welded end rings) |
| SG-205 | Bounce cap | 6082 | turned; carries spigot, gas-spring post, feedthrough, charge valve |
| SG-206 | Displacer | thin-wall 304 | can + rod; conformal nose |
| SG-207 | Piston + mover structure | 2014/4032 Al | piston, skirt, disc, magnet carrier, spring sleeve |
| SG-208 | Firebox + plenum shroud (1 off) | mild steel + refractory | folded/welded plate |
| SG-209 | Displacer cylinder | thin-wall 304 | tube; press + Loctite 620 into cold head spigot |
| SG-210 | Cold head | 6082-T6 Ø180 | THE reference part: bores, ports, gallery, glands, bolt circles |
| SG-211A/B | Stator core halves | M-19 laminations | split at coil centre so the coil can be installed |
| SG-212 | Stator coil | enamelled Cu | wound + potted, drops into core recess |
| SG-213 | Magnet cage (14-slot Halbach) | 6082 | FULL-LENGTH open slots, square end mill through-passes - zero internal corners, no dog-bone relief |
| SG-213MR | Halbach blocks, radial bands | 28x N42SH 20x10x6, M through 6 | bands 1 & 3; polarity alternates out/in |
| SG-213MA | Halbach blocks, axial bands | 28x N42SH 20x10x6, M through 10 (custom direction) | bands 2 & 4; same pocket, different magnetisation SKU |
| SG-213B | Banding sleeve | inconel / CF wrap | retains blocks, closes pockets, OD 120 running envelope |
| SG-214/215 | Rider bands (2+2) | PTFE 25% glass | scarf-cut rings in grooves |
| SG-216 | Water-gallery sleeve | 6082/304 | slides on from the hull side, 2 o-rings, 3×M3 |
| SG-217 | Cylinder liner | GG25 / nitrided 4130 | pressed, lip clamped by cold head, honed after pressing |
| SG-218 | Gas-spring gland band | PTFE 25% glass | on the bounce-cap post tip |
| SG-219 | Engine saddle blocks (2 off) | mild steel | drop onto pedestals after the engine slides in |
| SG-220 | Plenum closing panels (2 off) | mild steel | SPLIT halves, clamp around the fire tube, rope-packed bore |
| SG-221 | Gas-spring post | 6082/4140 | turned; Ø68 shoulder + M20 stud into the bounce-cap floor; shim plug in its bore tunes resonance |

Joints: hot cap→cold head 8×M8 BCD140 (o-ring Ø110); hull→cold head
8 studs BCD140 (clocked 22.5°); bounce cap→hull 8×M10 BCD200 on Ø222
flanges (o-ring Ø170, register spigot) — M10 sized from the 68 kN
separation load at 30 bar. Assembly order is documented step-by-step
in `PROJECT_STATE.md`.

## Loads & materials (30 bar rated / 20 bar working, quick-calc)

**Pressure boundary** (full ΔP to ambient — must be metal):

| Part | Stress | Temp | Verdict |
|------|--------|------|---------|
| Hot cap fire tube Ø88/t6 | hoop ~21 MPa | metal ≤700 °C | 310S creep ~60 MPa @650 °C → SF ~3. THE life-limiting part: keep hot-face ≤650-700 °C |
| Hot cap dome r44/t6 | ~11 MPa | ≤700 °C | ✓ |
| Hot cap regen zone Ø108/t6 | ~26 MPa | ≤300 °C | SF ~7 ✓ |
| Cold head Ø180 (6082-T6) | thin sections < 50 MPa | ~60 °C | SF ≥5 ✓; hot-cap joint separation 28 kN / 8×M8 → SF ~4 |
| Hull Ø180/t10 (6082) | hoop ~26 MPa | ~70 °C | SF ~9 ✓; bounce joint 68 kN / 8×M10 → SF 2.7 |
| Bounce cap Ø180/t10 | ~13 MPa | ambient | ✓ |

**Water boundary only** (1.5 bar): water sleeve — hoop ~3 MPa at 90 °C →
**polymer candidate** (GF nylon / PETG-CF); default 6082 (o-ring creep).

**Pressure-balanced internals** (gas both sides; see only the ±4.5 bar
cycle swing or flow ΔP): displacer + displacer cylinder (600 °C — metal
mandatory, thin 304 to cut conduction), regenerator (304 mesh),
cooler (copper — conductivity), piston/carrier (±1.3 kN cyclic @ 50 Hz —
aluminium), spring post (±4 kN on its M20, hoop ~2 MPa — PEEK possible
but pointless: it's static, so mass doesn't matter; CTE would eat the
gland clearance; stays 6082). Stator M-19 (magnetics), coil Cu, magnets
NdFeB **SH grade** (alternator cavity runs warm), bands/glands already
PTFE, liner cast iron / nitrided (wear; hard-anodised 6082 acceptable).

Bottom line: the only sensible non-metal swaps are the water sleeve and
the already-PTFE parts; everything else is metal for temperature,
conductivity, magnetics, wear, or because it IS the pressure vessel.

## Magnet ring = segmented Halbach cage (SG-213)

Machined 6082 cage with 14 FULL-LENGTH axial slots (not closed pockets:
56 pockets would mean 224 internal corners needing dog-bone relief the
thin lands can't afford - every slot is a straight through-pass with a
square end mill). 4 blocks stack in each slot = 56 NdFeB 20x10x6 blocks,
axially spaced by bonded end/interband strips. The Halbach rotation
(radial-out, axial+, radial-in, axial-) comes from TWO magnetisation
SKUs of the same block:
M-through-6 mm for the radial bands, M-through-10 mm (custom direction,
readily ordered) for the axial bands — this is what fits the 8.75 mm
radial wall budget; physically rotating standard blocks would need
10 mm of depth. Flux focuses outward into the coil, cancels at the
carrier: no mover back-iron. Flats vs arcs: 14 flat segments/band cost
~10% field (facet + chord-corner sinking: corners swing to r57.9 under
the Ø118 band, hence 6-thick blocks) — accepted for v1 since Halbach
buys ~+35%; true arc segments are a drop-in upgrade in the same cage.
Blocks bond in, Ø120 banding sleeve retains. Final grade/count locked
by the coil electrical design.

## The iteration loop

1. Edit `params.py` (or a part module in `parts/`)
2. `python3 make.py all` — parts, renders, viewer, exports, **clearance
   audit** (pairwise interference at mover extremes, lockstep-aware)
3. Review:
   - `out/viewer/assembly.html` — orbit/zoom/pan, per-part toggles,
     exploded view, half-section, animated kinematics, gas-flow and
     cooling-water particle streams, **click any part to inspect it**
     (isolates it, fits camera, shows drawing/material/stock)
   - `out/renders/assembly.png`, `hot_end_section.png`,
     `cold_end_section.png` — review sections, open side toward camera
4. `python3 make.py volumes` — Schmidt margin with as-built CAD dead
   volumes (keep > ~2.0× brake target; currently 1.87×, recovery items
   in PROJECT_STATE)
5. `python3 sizing.py` — regenerate the full sizing study / report

Other targets: `make.py part <name>` (one part), `viewer`, `audit`.

## Layout

```
params.py        all dimensions (mm), single source of truth
sizing.py        thermo: West/Beale + numerical Schmidt, scenarios,
                 as_built_check() = CAD-vs-sizing dead-volume margin
parts/           one module per part: META + build(); demo parts
                 (cold_cylinder, piston) keep drawing() as the template
assembly.py      SPEC (positions, colors, motion, explode), GAS_PATH,
                 WATER_PATH, kinematics
make.py          runner: all | part <n> | viewer | audit | volumes
pipeline/
  render.py      hidden-line SVG/PNG projections + half-sections
  sheet.py       A3/A4 dimensioned drawing sheets (title block, dims)
  viewer.py      self-contained interactive 3D HTML (three.js)
  export.py      STEP / STL / DXF
  audit.py       boolean interference audit at mover extremes
out/             everything generated (gitignored, always rebuildable)
```

## Toolchain

build123d 0.11 (OCCT 7.9 B-rep kernel) + ezdxf + cairosvg, pure Python.
Drawings follow ISO 2768-mK default tolerancing; fits (H7/g6 etc.) per
feature in each part's `drawing()`.

## Status & roadmap

Phase 1 (sizing) locked. Phase 2 (architecture) done. Phase 3 (detail
design) in progress: geometry is joint-complete and assemblable, audit
clean. Open items before drawings: dead-volume recovery (>2.0×),
displacer resonance budget + centering ports, coil electrical design,
magnet retention. **Then: dimensioned fabrication drawings for every
SG-2xx part via each module's `drawing()` (pipeline already proven on
the demo parts), starting with the cold head SG-210** — the reference
part everything registers to. Fabrication files (STEP/STL/DXF) already
regenerate on every build.
