"""Fast engineering renders: hidden-line projections -> SVG -> PNG.

Used two ways:
  * review renders (iso / front / section) so every change can be eyeballed
  * orthographic view SVGs consumed by sheet.py for dimensioned drawings
"""
from pathlib import Path
from build123d import ExportSVG, LineType, Plane, Box, Location

# standard viewport directions (camera position; +Z up unless noted)
DIRS = {
    "iso":   ((100, -100, 70), (0, 0, 1)),
    "front": ((0, -100, 0),    (0, 0, 1)),   # looking +Y: x right, z up
    "back":  ((0, 100, 0),     (0, 0, 1)),
    "right": ((100, 0, 0),     (0, 0, 1)),   # looking -X: y right... (z up)
    "top":   ((0, 0, 100),     (0, 1, 0)),   # x right, y up
    "bottom": ((0, 0, -100),   (0, 1, 0)),
}


def view_svg(shape, view, out_svg, scale=1.0, hidden=True):
    """Write a single hidden-line projection SVG. Returns path.

    OCCT's HLR can return ZERO edges from eye positions that align
    exactly with model faces (degenerate silhouettes); if that happens,
    retry with the eye jittered off-axis."""
    d, up = DIRS[view]
    c = shape.bounding_box().center()
    origin = (c.X + d[0] * 20, c.Y + d[1] * 20, c.Z + d[2] * 20)
    vis, hid = shape.project_to_viewport(origin, viewport_up=up)
    if not vis:
        jit = [25.0 if abs(k) < 1e-9 else 0.0 for k in d]
        origin = (origin[0] + jit[0], origin[1] + jit[1], origin[2] + jit[2])
        vis, hid = shape.project_to_viewport(origin, viewport_up=up)
    exp = ExportSVG(scale=scale, margin=0, line_weight=0.30)
    exp.add_layer("hidden", line_type=LineType.HIDDEN, line_weight=0.15)
    exp.add_shape(vis)
    if hidden and hid:
        exp.add_shape(hid, layer="hidden")
    Path(out_svg).parent.mkdir(parents=True, exist_ok=True)
    exp.write(str(out_svg))
    return out_svg


def render_png(shape, out_png, views=("iso", "front"), width=1100, hidden=True):
    """Multi-view PNG strip for quick visual review."""
    import cairosvg
    import tempfile
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmpd = Path(tempfile.mkdtemp())
    tiles = []
    for v in views:
        tmp = tmpd / f"{v}.svg"
        view_svg(shape, v, tmp, hidden=hidden)
        png = tmpd / f"{v}.png"
        cairosvg.svg2png(url=str(tmp), write_to=str(png),
                         output_width=width // len(views), background_color="white")
        tiles.append(png)
    from PIL import Image
    ims = [Image.open(t) for t in tiles]
    h = max(i.height for i in ims)
    W = sum(i.width for i in ims)
    canvas = Image.new("RGB", (W, h), "white")
    x = 0
    for im in ims:
        canvas.paste(im, (x, (h - im.height) // 2))
        x += im.width
    canvas.save(out)
    return out


def section(shape, plane="XZ"):
    """Half-section: cut the +normal half away to expose internals."""
    big = 10_000
    if plane == "XZ":
        # remove y<0 so the open face looks toward the default cameras (-Y)
        cutter = Box(big, big, big).located(Location((0, -big / 2, 0)))
    elif plane == "YZ":
        cutter = Box(big, big, big).located(Location((big / 2, 0, 0)))
    else:  # XY
        cutter = Box(big, big, big).located(Location((0, 0, big / 2)))
    return shape - cutter
