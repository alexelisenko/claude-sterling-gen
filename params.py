"""Single source of truth for every dimension in the engine (mm, degrees).

Change a value here, rerun `python3 make.py all`, and every model, render,
viewer, drawing and export regenerates in sync.

STATUS: provisional demo dimensions. Final sizing comes from the thermo
(Schmidt) model before drawings are released for fabrication.
"""

# ---------------------------------------------------------------- engine level
ENGINE = dict(
    target_power_W=1000,          # electrical output target
    layout="opposed free-piston, central heat zone",
    working_gas="air (helium later)",
)

# ------------------------------------------------------- demo: cold-end cylinder
# Finned cold-end cylinder, one per side. Lathe part, aluminium.
COLD_CYL = dict(
    bore=70.0,            # piston bore
    wall=6.0,             # wall under fins
    length=120.0,         # overall length
    fin_od=140.0,         # fin outside diameter
    fin_t=3.0,            # fin thickness
    fin_gap=5.0,          # gap between fins
    fin_zone=80.0,        # finned length, from flange end
    flange_od=160.0,      # mounting flange OD
    flange_t=12.0,        # flange thickness
    bolt_circle=148.0,    # flange bolt circle diameter
    bolt_d=9.0,           # clearance holes for M8
    n_bolts=8,
    spigot_od=110.0,      # register spigot into hot section
    spigot_len=6.0,
    material="6061-T6 aluminium",
    stock="Ø165 x 125 bar",
)

# ------------------------------------------------------------------ demo: piston
PISTON = dict(
    od=69.90,             # running clearance to bore
    length=60.0,
    rod_d=16.0,
    rod_len=90.0,
    skirt_bore=58.0,      # internal lightening bore
    skirt_depth=45.0,
    crown_t=8.0,
    material="4032 aluminium or cast iron",
    stock="Ø75 x 160 bar",
)

# ------------------------------------------------------------------- kinematics
MOTION = dict(
    stroke=40.0,          # piston stroke
    freq_hz=1.0,          # viewer animation speed (visual, not engine speed)
)

# ------------------------------------------------------------------ title block
PROJECT = dict(
    name="Stirling Generator 1kW",
    author="Alex",
    units="mm",
    standard="ISO 2768-mK unless noted",
)
