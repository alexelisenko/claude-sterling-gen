"""ISO-style drawing sheets with real dimensions, rendered to SVG/PDF/PNG.

A Sheet is an A3/A4 landscape page with border + title block. Views are
build123d SVG projections placed at a sheet location; each View maps *part
coordinates* (mm on the projection plane, y up) to sheet coordinates, so
dimensions are declared with actual model values and stay in sync with
params.py.
"""
import re
import datetime
from pathlib import Path

SIZES = {"A4": (297.0, 210.0), "A3": (420.0, 297.0)}
FONT = "DejaVu Sans, Arial, sans-serif"
TXT = 3.2          # dimension text height, mm
ARROW = 2.8        # arrowhead length, mm


def _fmt(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s


VIEW_AXES = {  # projection-plane axes per view: (screen-x, screen-y), part axes
    "front": ("X", "Z"), "top": ("X", "Y"), "right": ("Y", "Z"),
}


class View:
    """A projection placed on a sheet, anchored by its geometry bounding box.
    Dim methods take *part coordinates* on the projection plane (y up)."""

    def __init__(self, sheet, at, scale, pmin, pmax):
        self.s, self.at, self.k = sheet, at, scale
        self.px_min, self.py_max = pmin, pmax

    def map(self, px, py):
        return (self.at[0] + (px - self.px_min) * self.k,
                self.at[1] + (self.py_max - py) * self.k)

    # -- dimensions (part coords) ------------------------------------------
    def hdim(self, x1, x2, y, text=None, prefix=""):
        """Horizontal dimension between x1..x2, dim line at part-y `y`."""
        (X1, _), (X2, _) = self.map(x1, 0), self.map(x2, 0)
        _, Y = self.map(0, y)
        if X1 > X2:
            X1, X2 = X2, X1
        t = text or prefix + _fmt(abs(x2 - x1))
        e = self.s._el
        e.append(f'<line x1="{X1}" y1="{Y}" x2="{X2}" y2="{Y}" class="dim"/>')
        e.append(self.s._arrow(X1, Y, 0))
        e.append(self.s._arrow(X2, Y, 180))
        e.append(f'<text x="{(X1+X2)/2}" y="{Y-1.2}" class="dtx" text-anchor="middle">{t}</text>')

    def vdim(self, y1, y2, x, text=None, prefix="", rotate=True):
        _, Y1 = self.map(0, y1)
        _, Y2 = self.map(0, y2)
        X, _ = self.map(x, 0)
        if Y1 > Y2:
            Y1, Y2 = Y2, Y1
        t = text or prefix + _fmt(abs(y2 - y1))
        e = self.s._el
        e.append(f'<line x1="{X}" y1="{Y1}" x2="{X}" y2="{Y2}" class="dim"/>')
        e.append(self.s._arrow(X, Y1, 90))
        e.append(self.s._arrow(X, Y2, 270))
        if rotate:
            e.append(f'<text x="{X-1.2}" y="{(Y1+Y2)/2}" class="dtx" text-anchor="middle" '
                     f'transform="rotate(-90 {X-1.2} {(Y1+Y2)/2})">{t}</text>')
        else:
            e.append(f'<text x="{X+1.5}" y="{(Y1+Y2)/2+1.2}" class="dtx">{t}</text>')

    def ext(self, px, py, px2, py2):
        """Extension line from feature to dimension line (part coords)."""
        X1, Y1 = self.map(px, py)
        X2, Y2 = self.map(px2, py2)
        self.s._el.append(f'<line x1="{X1}" y1="{Y1}" x2="{X2}" y2="{Y2}" class="ext"/>')

    def leader(self, px, py, tx, ty, text):
        """Leader with arrow at (px,py), text at (tx,ty). Part coords."""
        X1, Y1 = self.map(px, py)
        X2, Y2 = self.map(tx, ty)
        import math
        ang = math.degrees(math.atan2(Y1 - Y2, X1 - X2))
        e = self.s._el
        e.append(f'<line x1="{X1}" y1="{Y1}" x2="{X2}" y2="{Y2}" class="dim"/>')
        e.append(self.s._arrow(X1, Y1, ang + 180))
        anchor = "start" if X2 >= X1 else "end"
        dx = 1.0 if anchor == "start" else -1.0
        e.append(f'<line x1="{X2}" y1="{Y2}" x2="{X2+8*dx}" y2="{Y2}" class="dim"/>')
        e.append(f'<text x="{X2+dx*1.5}" y="{Y2-1.2}" class="dtx" text-anchor="{anchor}">{text}</text>')

    def cl(self, x1, y1, x2, y2):
        """Centerline (dash-dot), part coords."""
        X1, Y1 = self.map(x1, y1)
        X2, Y2 = self.map(x2, y2)
        self.s._el.append(f'<line x1="{X1}" y1="{Y1}" x2="{X2}" y2="{Y2}" class="cl"/>')

    def label(self, text, dy=10.0):
        X = self.at[0] + getattr(self, "_w", 0) / 2
        Y = self.at[1] + getattr(self, "_h", 0) + dy
        self.s._el.append(f'<text x="{X}" y="{Y}" class="vlab" text-anchor="middle">{text}</text>')


class Sheet:
    def __init__(self, size="A3", part_name="", drawing_no="", material="",
                 scale="1:1", stock="", notes=(), project=None):
        self.W, self.H = SIZES[size]
        self.size_name = size
        self.meta = dict(part_name=part_name, drawing_no=drawing_no,
                         material=material, scale=scale, stock=stock)
        self.notes = list(notes)
        self.project = project or {}
        self._el = []

    # -- low level ----------------------------------------------------------
    def _arrow(self, x, y, ang):
        return (f'<path d="M0,0 L{ARROW},{ARROW*0.28} L{ARROW},-{ARROW*0.28} Z" '
                f'transform="translate({x},{y}) rotate({ang})" fill="black"/>')

    def text(self, x, y, s, size=TXT, anchor="start", bold=False):
        w = ' font-weight="bold"' if bold else ""
        self._el.append(f'<text x="{x}" y="{y}" font-size="{size}"{w} '
                        f'font-family="{FONT}" text-anchor="{anchor}">{s}</text>')

    # -- views ---------------------------------------------------------------
    def place_view(self, svg_path, at, part, view="front", scale=1.0, label=None):
        """Inline a build123d ExportSVG projection of `part`. `at` = sheet mm
        position of the projection's top-left (min-x, max-y of geometry).
        Returns a View whose dim methods take part coordinates."""
        src = Path(svg_path).read_text()
        vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
        m = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S)
        inner = re.sub(r"<\?xml[^>]*\?>", "", m.group(1))
        self._el.append(
            f'<g transform="translate({at[0] - vb[0]},{at[1] - vb[1]})">{inner}</g>')
        bb = part.bounding_box()
        ax, ay = VIEW_AXES[view]
        pmin = getattr(bb.min, ax)
        pmax = getattr(bb.max, ay)
        v = View(self, at, scale, pmin, pmax)
        v._w = (getattr(bb.max, ax) - getattr(bb.min, ax)) * scale
        v._h = (getattr(bb.max, ay) - getattr(bb.min, ay)) * scale
        if label:
            v.label(label)
        return v

    # -- output ---------------------------------------------------------------
    def _frame(self):
        W, H, m = self.W, self.H, 8.0
        el = [f'<rect x="{m}" y="{m}" width="{W-2*m}" height="{H-2*m}" '
              f'fill="none" stroke="black" stroke-width="0.5"/>']
        # title block, bottom right
        tw, th = 130.0, 34.0
        x0, y0 = W - m - tw, H - m - th
        el.append(f'<rect x="{x0}" y="{y0}" width="{tw}" height="{th}" fill="white" stroke="black" stroke-width="0.5"/>')
        rows = [y0 + 8.5, y0 + 17, y0 + 25.5]
        for r in rows:
            el.append(f'<line x1="{x0}" y1="{r}" x2="{x0+tw}" y2="{r}" stroke="black" stroke-width="0.25"/>')
        el.append(f'<line x1="{x0+65}" y1="{rows[0]}" x2="{x0+65}" y2="{y0+th}" stroke="black" stroke-width="0.25"/>')
        p, mt = self.project, self.meta
        t = lambda x, y, s, sz=2.6, b=False: el.append(
            f'<text x="{x}" y="{y}" font-size="{sz}" font-family="{FONT}"'
            f'{" font-weight=&quot;bold&quot;".replace("&quot;", chr(34)) if b else ""}>{s}</text>')
        t(x0 + 2, y0 + 5.7, f'{p.get("name","")} — {mt["part_name"]}', 3.6, True)
        t(x0 + 2, rows[0] + 5.5, f'DWG {mt["drawing_no"]}', 3.0, True)
        t(x0 + 67, rows[0] + 5.5, f'SCALE {mt["scale"]}   UNITS {p.get("units","mm")}')
        t(x0 + 2, rows[1] + 5.5, f'MATL: {mt["material"]}')
        t(x0 + 67, rows[1] + 5.5, f'STOCK: {mt["stock"]}')
        t(x0 + 2, rows[2] + 5.5, p.get("standard", ""))
        t(x0 + 67, rows[2] + 5.5, f'{p.get("author","")}  {datetime.date.today().isoformat()}')
        return el

    def _notes(self):
        el = []
        if self.notes:
            x, y = 12.0, self.H - 14.0 - 4.5 * len(self.notes)
            el.append(f'<text x="{x}" y="{y}" font-size="3.0" font-weight="bold" font-family="{FONT}">NOTES:</text>')
            for i, n in enumerate(self.notes):
                el.append(f'<text x="{x}" y="{y+4.5*(i+1)}" font-size="2.8" font-family="{FONT}">{i+1}. {n}</text>')
        return el

    def svg(self):
        style = (f'<style>.dim,.ext,.cl{{stroke:black;fill:none}}'
                 f'.dim{{stroke-width:0.18}}.ext{{stroke-width:0.13}}'
                 f'.cl{{stroke-width:0.13;stroke-dasharray:6 1.2 1.2 1.2}}'
                 f'.dtx{{font-size:{TXT}px;font-family:{FONT}}}'
                 f'.vlab{{font-size:3.8px;font-weight:bold;font-family:{FONT}}}</style>')
        body = "".join(self._frame() + self._el + self._notes())
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}mm" height="{self.H}mm" '
                f'viewBox="0 0 {self.W} {self.H}">{style}'
                f'<rect width="{self.W}" height="{self.H}" fill="white"/>{body}</svg>')

    def save(self, out_base):
        """Writes .svg, .pdf and a .png preview. `out_base` without extension."""
        import cairosvg
        base = Path(out_base)
        base.parent.mkdir(parents=True, exist_ok=True)
        svg = self.svg()
        base.with_suffix(".svg").write_text(svg)
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=str(base.with_suffix(".pdf")))
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(base.with_suffix(".png")),
                         output_width=2200, background_color="white")
        return base.with_suffix(".pdf")
