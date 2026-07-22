"""Fabrication exports per part: STEP (CNC/outsource), STL (3D print),
DXF (router/laser profiles)."""
from pathlib import Path
from build123d import export_step, export_stl, ExportDXF, Unit, Plane, section


def export_part(part, name, out_dir, dxf_plane=None):
    """Write step/ stl/ (and optional dxf/ profile section) for a part."""
    out = Path(out_dir)
    paths = {}
    for sub in ("step", "stl", "dxf"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    p = out / "step" / f"{name}.step"
    export_step(part, str(p))
    paths["step"] = p
    p = out / "stl" / f"{name}.stl"
    export_stl(part, str(p), tolerance=0.02)
    paths["stl"] = p
    if dxf_plane is not None:
        sec = section(part, section_by=dxf_plane)
        exp = ExportDXF(unit=Unit.MM)
        exp.add_shape(sec)
        p = out / "dxf" / f"{name}.dxf"
        exp.write(str(p))
        paths["dxf"] = p
    return paths
