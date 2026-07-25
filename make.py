#!/usr/bin/env python3
"""Regenerate everything from params.py.

  python3 make.py all                    # parts + renders + viewer + drawings + exports
  python3 make.py part cold_cylinder     # one part: render + drawing + exports
  python3 make.py viewer                 # just the interactive assembly viewer
"""
import importlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "out"

import assembly
from pipeline import render, viewer, export
from params import MOTION

PART_NAMES = list(dict.fromkeys(e["module"] for e in assembly.SPEC))


def do_part(name):
    t = time.time()
    mod = importlib.import_module(f"parts.{name}")
    part = mod.build()
    # review render (iso + front w/ hidden lines)
    render.render_png(part, OUT / "renders" / f"{name}.png", views=("iso", "front"))
    if hasattr(mod, "drawing"):     # envelope parts have no dim sheet yet
        # orthographic views for the drawing sheet
        svgs = {v: render.view_svg(part, v, OUT / "views" / f"{name}_{v}.svg")
                for v in ("front", "top", "right")}
        sheet = mod.drawing(part, svgs)
        sheet.save(OUT / "drawings" / f"{mod.META['dwg']}_{name}")
    # fabrication exports
    export.export_part(part, name, OUT)
    print(f"[{name}] done in {time.time()-t:.1f}s")
    return part


def do_viewer():
    parts = []
    for e in assembly.SPEC:
        stl = OUT / "stl" / f"{e['module']}.stl"
        if not stl.exists():
            do_part(e["module"])
        meta = importlib.import_module(f"parts.{e['module']}").META
        parts.append(dict(name=e.get("name", e["module"]), stl=stl,
                          color=e["color"], pos=e["pos"],
                          rot=e.get("rot", (0, 0, 0)),
                          motion=e["motion"], explode=e["explode"],
                          meta={k: meta.get(k, "") for k in
                                ("title", "dwg", "material", "stock")}))
    out = viewer.build_viewer(parts, OUT / "viewer" / "assembly.html",
                              title="Stirling Generator 1kW",
                              freq=MOTION["freq_hz"],
                              gas=getattr(assembly, "GAS_PATH", None),
                              water=getattr(assembly, "WATER_PATH", None))
    print(f"[viewer] {out}")


def do_assembly_render():
    from build123d import Location, Compound
    builds = {}
    located = []
    for e in assembly.SPEC:
        if e["module"] not in builds:
            builds[e["module"]] = importlib.import_module(
                f"parts.{e['module']}").build()
        located.append(builds[e["module"]].located(
            Location(e["pos"], e.get("rot", (0, 0, 0)))))
    comp = Compound(located)
    render.render_png(comp, OUT / "renders" / "assembly.png", views=("iso",), hidden=False)
    # half-section: cut each part separately (a fused union would swallow
    # the movers), then view from the open side
    sec = Compound([render.section(p, "XZ") for p in located])
    render.render_png(sec, OUT / "renders" / "assembly_section.png",
                      views=("iso", "front"), hidden=False)
    print("[assembly] renders done")


def do_hot_end():
    """Close-up half-section of one hot-end stack - the gas-path review view."""
    from build123d import Location, Compound
    from params import LAYOUT as L
    stack = [("hot_cap", L["hotcap_z"]), ("disp_cylinder", L["disp_cyl"][0]),
             ("regen_housing", L["regen_ring"][0]),
             ("cooler_jacket", L["cooler_ring"][0]),
             ("cold_head", L["ch_span"][0]),
             ("displacer", L["disp_face_z"]),
             ("piston_mover", L["piston_face_z"]),
             ("pressure_hull", L["hull_z"])]
    parts = []
    for mod, s in stack:
        p = importlib.import_module(f"parts.{mod}").build().located(
            Location((0, 0, s)))
        parts.append(render.section(p, "XZ"))
    render.render_png(Compound(parts), OUT / "renders" / "hot_end_section.png",
                      views=("iso",), hidden=False)
    print("[hot-end] section render done")
    # cold end: alternator stack review view
    stack2 = [("pressure_hull", L["hull_z"]),
              ("stator_core", L["stator_core"][0]),
              ("stator_coil", L["coil_span"][0]),
              ("stator_core_out", L["core_split"]),
              ("piston_mover", L["piston_face_z"]),
              ("magnet_ring", L["piston_face_z"] + L["magnet_local"]),
              ("piston_band", L["piston_face_z"] + L["piston_bands_local"][0]),
              ("spring_post", L["post_tip"]),
              ("spring_band", L["post_tip"] + 4),
              ("bounce_cap", L["hull_z"] + L["hull_len"])]
    parts2 = []
    for mod, s in stack2:
        p = importlib.import_module(f"parts.{mod}").build().located(
            Location((0, 0, s)))
        parts2.append(render.section(p, "XZ"))
    render.render_png(Compound(parts2), OUT / "renders" / "cold_end_section.png",
                      views=("iso",), hidden=False)
    print("[cold-end] section render done")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "part":
        do_part(sys.argv[2])
    elif cmd == "viewer":
        do_viewer()
    elif cmd == "audit":
        from pipeline import audit
        audit.run(assembly.SPEC)
    elif cmd == "volumes":
        import sizing
        sizing.as_built_check()
    elif cmd == "all":
        for n in PART_NAMES:
            do_part(n)
        do_assembly_render()
        do_hot_end()
        do_viewer()
        from pipeline import audit
        audit.run(assembly.SPEC)
    print("OK")
