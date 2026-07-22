"""Cold-end cylinder (demo part) - finned aluminium lathe part.

Every part module exposes:
  build()   -> build123d Part
  drawing() -> Sheet with dimensioned views
  META      -> name, drawing number, material, stock
"""
from build123d import *
from params import COLD_CYL as P, PROJECT

META = dict(name="cold_cylinder", title="Cold-end cylinder", dwg="SG-101",
            material=P["material"], stock=P["stock"])


def build():
    bore_r = P["bore"] / 2
    body_or = bore_r + P["wall"]
    with BuildPart() as bp:
        # flange at z=0, body upward (+z toward hot end)
        Cylinder(P["flange_od"] / 2, P["flange_t"],
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
        Cylinder(body_or, P["length"], align=(Align.CENTER, Align.CENTER, Align.MIN))
        # register spigot below flange
        with Locations((0, 0, 0)):
            Cylinder(P["spigot_od"] / 2, P["spigot_len"],
                     align=(Align.CENTER, Align.CENTER, Align.MAX))
        # fins: annular disks along the fin zone
        pitch = P["fin_t"] + P["fin_gap"]
        n_fins = int(P["fin_zone"] // pitch)
        z0 = P["flange_t"] + P["fin_gap"]
        for i in range(n_fins):
            with Locations((0, 0, z0 + i * pitch)):
                Cylinder(P["fin_od"] / 2, P["fin_t"],
                         align=(Align.CENTER, Align.CENTER, Align.MIN))
        # bore through everything
        Cylinder(bore_r, 500, mode=Mode.SUBTRACT)
        # flange bolt holes
        with Locations(Plane.XY.offset(P["flange_t"])):
            with PolarLocations(P["bolt_circle"] / 2, P["n_bolts"]):
                Hole(P["bolt_d"] / 2, depth=P["flange_t"] + P["spigot_len"])
    part = bp.part
    part.label = META["title"]
    return part


def drawing(part, view_svgs):
    """view_svgs: dict of pre-generated view svg paths from make.py"""
    from pipeline.sheet import Sheet
    s = Sheet(size="A3", part_name=META["title"], drawing_no=META["dwg"],
              material=META["material"], stock=META["stock"], scale="1:1",
              project=PROJECT,
              notes=[
                  f'Bore &#8960;{P["bore"]:.2f} H8: hone after boring. Ra 0.4 max.',
                  f'Spigot &#8960;{P["spigot_od"]:.2f} g6, locates in hot-section counterbore.',
                  f'{P["n_bolts"]}x &#8960;{P["bolt_d"]:.1f} equally spaced on &#8960;{P["bolt_circle"]:.0f} B.C.',
                  "Deburr all edges 0.3 x 45&#176;. Fins: do not nick roots.",
              ])
    L, FT, SP = P["length"], P["flange_t"], P["spigot_len"]
    fr, br = P["flange_od"] / 2, P["bore"] / 2
    fo, bo = P["fin_od"] / 2, P["bore"] / 2 + P["wall"]

    # front view (x right, z up) placed left; part origin = flange bottom, on cl.
    v = s.place_view(view_svgs["front"], at=(60, 55), part=part, view="front",
                     label="FRONT")
    v.cl(0, -SP - 8, 0, L + 8)                                   # axis centerline
    v.vdim(0, L, -fr - 14, prefix="")                            # overall length
    v.ext(-fr, 0, -fr - 16, 0); v.ext(-bo, L, -fr - 16, L)
    v.vdim(0, FT, fr + 12)                                       # flange thickness
    v.ext(fr, 0, fr + 14, 0); v.ext(fr, FT, fr + 14, FT)
    v.vdim(-SP, 0, fr + 26)                                      # spigot length
    v.hdim(-fr, fr, -SP - 18, prefix="&#8960;")                  # flange OD
    v.hdim(-fo, fo, L + 14, prefix="&#8960;")                    # fin OD
    v.leader(br, L - 5, fo + 18, L + 26, f'&#8960;{P["bore"]:.2f} H8 THRU')
    v.leader(P["spigot_od"] / 2, -SP / 2, fr + 30, -SP - 30,
             f'&#8960;{P["spigot_od"]:.2f} g6')
    v.leader(bo, L - 25, fo + 24, L - 46,
             f'FINS: {int(P["fin_zone"] // (P["fin_t"] + P["fin_gap"]))}x '
             f'{P["fin_t"]:.0f} THK, {P["fin_gap"]:.0f} GAP')

    # top view (x right, y up) placed right - bolt circle
    v2 = s.place_view(view_svgs["top"], at=(245, 45), part=part, view="top",
                      label="TOP")
    v2.cl(-fr - 6, 0, fr + 6, 0); v2.cl(0, -fr - 6, 0, fr + 6)
    v2.hdim(-P["bolt_circle"] / 2, P["bolt_circle"] / 2, -fr - 26, prefix="&#8960;")
    v2.ext(-P["bolt_circle"] / 2 * 0.7071, -P["bolt_circle"] / 2 * 0.7071,
           -P["bolt_circle"] / 2, -fr - 28)
    v2.ext(P["bolt_circle"] / 2 * 0.7071, -P["bolt_circle"] / 2 * 0.7071,
           P["bolt_circle"] / 2, -fr - 28)
    v2.leader(P["bolt_circle"] / 2 * 0.7071, P["bolt_circle"] / 2 * 0.7071,
              -40, fr + 15,
              f'{P["n_bolts"]}x &#8960;{P["bolt_d"]:.1f} EQ SP')
    return s
