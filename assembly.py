"""Demo assembly: cold cylinder + piston, with free-piston motion spec.

Each entry: part module, color, base position, sinusoidal motion
(axis, amplitude, phase) and explode direction for the viewer.
"""
import math
from params import MOTION, PISTON

STROKE = MOTION["stroke"]

SPEC = [
    dict(module="cold_cylinder", color="#7d8fa3", pos=(0, 0, 0),
         motion=None, explode=(0, 0, -60)),
    # piston mid-stroke inside the bore, oscillating along +Z
    dict(module="piston", color="#d98e32",
         pos=(0, 0, 35),
         motion=dict(axis=(0, 0, 1), amp=STROKE / 2, phase=0.0),
         explode=(0, 0, 140)),
]


def positions(theta):
    """Kinematics: part z-offsets at phase angle theta (rad). Extend as the
    mechanism grows (displacer lead, alternator mover, etc.)."""
    return {"piston": STROKE / 2 * math.sin(theta)}
