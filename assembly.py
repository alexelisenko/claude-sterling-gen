"""Full-engine envelope assembly: opposed free-piston pair over a firebox.

World frame: engine axis = X (horizontal), Z up, firebox below the
centre, log door on +Y. Side A extends +X (parts built along local +Z,
rotated (0,+90,0)); side B mirrors with (0,-90,0). Movers animate with
sizing scenario E kinematics: displacer leads the piston by 70 deg; the
sides move in mirror symmetry (dynamically balanced).

Each SPEC entry: name (unique), module (parts/<module>.py), color,
pos, optional rot (deg XYZ), motion (axis world-frame, amp, phase)
and explode direction for the viewer.
"""
import math
from params import LAYOUT as L, SIZING as S, MOTION

XP = S["piston_stroke"] / 2          # piston amplitude
XD = S["disp_stroke"] / 2            # displacer amplitude
PH = math.radians(S["disp_phase_deg"])

_STATIC = [
    # module, color, inboard-s, explode outward
    ("hot_cap",       "#b0413e", L["hotcap_z"], 60),
    ("disp_cylinder", "#c8ccd2", L["disp_cyl"][0], 150),
    ("regen_housing", "#a67c3d", L["regen_ring"][0], 230),
    ("cooler_jacket", "#d47f3f", L["cooler_ring"][0], 300),
    ("cold_head",       "#5d8aa8", L["ch_span"][0], 370),
    ("water_sleeve",    "#7a8288", L["sleeve_span"][0], 410),
    ("pressure_hull",   "#7d8fa3", L["hull_z"], 470),
    ("cylinder_liner",  "#c2c8ce", L["hull_z"], 520),
    ("stator_core",     "#9099a3", L["stator_core"][0], 570),
    ("stator_coil",     "#b87333", L["coil_span"][0], 610),
    ("stator_core_out", "#9099a3", L["core_split"], 650),
    ("spring_post",     "#8a94a0", L["post_tip"], 690),
    ("spring_band",     "#e8e4d8", L["post_tip"] + 4, 730),
    ("bounce_cap",      "#566573", L["hull_z"] + L["hull_len"], 780),
]

_MOVERS = [
    # module, color, mean-s, amplitude, phase
    ("displacer",    "#e67e22", L["disp_face_z"], XD, PH),
    ("piston_mover", "#d4a50d", L["piston_face_z"], XP, 0.0),
    ("magnet_ring",  "#9aa4ae", L["piston_face_z"] + L["magnet_local"], XP, 0.0),
    ("magnet_set",   "#a03a45", L["piston_face_z"] + L["magnet_local"], XP, 0.0),
    ("magnet_set_axial", "#3a5f9e",
     L["piston_face_z"] + L["magnet_local"], XP, 0.0),
    ("magnet_band",  "#6b7480", L["piston_face_z"] + L["magnet_local"], XP, 0.0),
]

# PTFE bands ride with their parent mover (name, module, mean-s, amp, phase)
_BANDS = (
    [("piston_band", L["piston_face_z"] + b, XP, 0.0)
     for b in L["piston_bands_local"]]
    + [("disp_band", L["disp_face_z"] + b, XD, PH)
       for b in L["disp_bands_local"]]
)


def _sides():
    spec = [dict(name="firebox_plenum", module="combustion_shell",
                 color="#4d4d4d", pos=(0, 0, 0), motion=None,
                 explode=(0, 0, -300))]
    for side, sgn in (("a", +1), ("b", -1)):
        spec.append(dict(name=f"saddle_{side}", module="saddle",
                         color="#6e6e6e", pos=(sgn * 208, 0, -97.5),
                         motion=None, explode=(0, 0, -160)))
        spec.append(dict(name=f"plenum_panel_{side}", module="plenum_panel",
                         color="#5e6a72", pos=(sgn * (L["plenum_x"] + 0.5), 0, 0),
                         rot=(0, sgn * 90, 0), motion=None,
                         explode=(sgn * 90, 0, 0)))
    for side, sgn in (("a", +1), ("b", -1)):
        rot = (0, sgn * 90, 0)               # local +Z -> world +/-X
        for mod, col, s, ex in _STATIC:
            spec.append(dict(name=f"{mod}_{side}", module=mod, color=col,
                             pos=(sgn * s, 0, 0), rot=rot, motion=None,
                             explode=(sgn * ex, 0, 0)))
        for k, (mod, col, s, amp, ph) in enumerate(_MOVERS):
            spec.append(dict(name=f"{mod}_{side}", module=mod, color=col,
                             pos=(sgn * s, 0, 0), rot=rot,
                             motion=dict(axis=(sgn, 0, 0), amp=amp, phase=ph),
                             explode=(sgn * (L["hull_len"] + 340 + 55 * k),
                                      0, 0)))
        for i, (mod, s, amp, ph) in enumerate(_BANDS):
            spec.append(dict(name=f"{mod}{i%2+1}_{side}", module=mod,
                             color="#e8e4d8", pos=(sgn * s, 0, 0), rot=rot,
                             motion=dict(axis=(sgn, 0, 0), amp=amp, phase=ph),
                             explode=(sgn * (L["hull_len"] + 440), 0, 0)))
    return spec


SPEC = _sides()


def positions(theta):
    """Kinematics: mover offsets (side A frame, mm) at phase angle theta."""
    return {
        "displacer": XD * math.sin(theta + PH),
        "piston_mover": XP * math.sin(theta),
    }


# Gas-loop centreline for the viewer's particle flow, side A, as (s, r)
# points (axial position, radius). Mirrored for side B in the viewer.
# expansion space -> dome -> heater annulus -> regen matrix -> cooler ->
# cold-head ports -> relief groove -> compression space.
GAS_PATH = dict(
    pts=[(46, 6), (58, 24), (78, 36), (125, 36),      # dome + heater annulus
         (129, 41), (149, 41), (163, 41),             # regen + cooler
         (166, 38.5), (174, 38.5),                    # axial ports
         (176, 34), (179, 26), (188, 14)],            # relief turn + compression
    streams=10,          # azimuthal streams
    per=14,              # particles per stream
    amp=0.085,           # oscillation amplitude, fraction of path length
    phase=PH + math.pi / 2,   # gas surge phase vs piston (illustrative)
    hot_end_s=126.0, cool_span=(127.0, 163.0),        # for temperature colors
)

# Cooling-water circuit for the viewer: in the +Y boss, around the annular
# gallery (both azimuthal branches), out the -Y boss. Steady circulation.
WATER_PATH = dict(
    s=(L["water_span"][0] + L["water_span"][1]) / 2,   # gallery axial centre
    r_gal=(L["water_groove"][0] + L["water_groove"][1]) / 4,  # mid radius
    r_boss=125.0,        # hose end of the boss
    per=26,              # particles per branch per side
)
