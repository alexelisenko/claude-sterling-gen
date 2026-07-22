"""Power piston with rod (demo part) - lathe part."""
from build123d import *
from params import PISTON as P, PROJECT

META = dict(name="piston", title="Power piston", dwg="SG-102",
            material=P["material"], stock=P["stock"])


def build():
    with BuildPart() as bp:
        # crown at top (z = length), skirt down
        Cylinder(P["od"] / 2, P["length"], align=(Align.CENTER, Align.CENTER, Align.MIN))
        # lightening bore from below
        with Locations((0, 0, 0)):
            Cylinder(P["skirt_bore"] / 2, P["skirt_depth"], mode=Mode.SUBTRACT,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        # rod downward
        Cylinder(P["rod_d"] / 2, P["rod_len"],
                 align=(Align.CENTER, Align.CENTER, Align.MAX))
        fillet(bp.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0], 2)
    part = bp.part
    part.label = META["title"]
    return part


def drawing(part, view_svgs):
    from pipeline.sheet import Sheet
    s = Sheet(size="A3", part_name=META["title"], drawing_no=META["dwg"],
              material=META["material"], stock=META["stock"], scale="1:1",
              project=PROJECT,
              notes=[
                  f'OD &#8960;{P["od"]:.2f} f7: finish-turn to bore fit, 0.05-0.10 clearance.',
                  "Rod blend R2, polish. Concentricity rod to OD 0.02 TIR.",
              ])
    v = s.place_view(view_svgs["front"], at=(140, 60), part=part, view="front",
                     label="FRONT")
    r, L, RL = P["od"] / 2, P["length"], P["rod_len"]
    v.cl(0, -RL - 8, 0, L + 8)
    v.vdim(0, L, -r - 14)                                       # piston length
    v.ext(-r, 0, -r - 16, 0); v.ext(-r, L, -r - 16, L)
    v.vdim(-RL, 0, r + 14)                                      # rod length
    v.ext(r, 0, r + 16, 0); v.ext(P["rod_d"] / 2, -RL, r + 16, -RL)
    v.hdim(-r, r, L + 12, prefix="&#8960;")                     # OD
    v.hdim(-P["rod_d"] / 2, P["rod_d"] / 2, -RL - 24, prefix="&#8960;")
    v.ext(-P["rod_d"] / 2, -RL, -P["rod_d"] / 2, -RL - 26)
    v.ext(P["rod_d"] / 2, -RL, P["rod_d"] / 2, -RL - 26)
    v.leader(P["skirt_bore"] / 2 - 2, P["skirt_depth"] / 2, r + 30, -30,
             f'&#8960;{P["skirt_bore"]:.1f} x {P["skirt_depth"]:.0f} DP')
    v.leader(-r, L - P["crown_t"] / 2, -r - 26, L + 22,
             f'CROWN {P["crown_t"]:.0f} THK')
    return s
