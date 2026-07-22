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

PART_NAMES = [e["module"] for e in assembly.SPEC]


def do_part(name):
    t = time.time()
    mod = importlib.import_module(f"parts.{name}")
    part = mod.build()
    # review render (iso + front w/ hidden lines)
    render.render_png(part, OUT / "renders" / f"{name}.png", views=("iso", "front"))
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
        parts.append(dict(name=e["module"], stl=stl, color=e["color"],
                          pos=e["pos"], motion=e["motion"], explode=e["explode"]))
    out = viewer.build_viewer(parts, OUT / "viewer" / "assembly.html",
                              title="Stirling Generator - demo assembly",
                              freq=MOTION["freq_hz"])
    print(f"[viewer] {out}")


def do_assembly_render():
    from build123d import Location
    comp = None
    for e in assembly.SPEC:
        mod = importlib.import_module(f"parts.{e['module']}")
        p = mod.build().located(Location(e["pos"]))
        comp = p if comp is None else comp + p
    render.render_png(comp, OUT / "renders" / "assembly.png", views=("iso",), hidden=False)
    sec = render.section(comp, "XZ")
    render.render_png(sec, OUT / "renders" / "assembly_section.png", views=("front",), hidden=False)
    print("[assembly] renders done")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "part":
        do_part(sys.argv[2])
    elif cmd == "viewer":
        do_viewer()
    elif cmd == "all":
        for n in PART_NAMES:
            do_part(n)
        do_assembly_render()
        do_viewer()
    print("OK")
