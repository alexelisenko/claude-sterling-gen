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
    working_gas="helium 20 bar (commission on air 7 bar)",
)

# ------------------------------------------------- Phase 1 sizing (LOCKED)
# Scenario E of sizing.py, locked 2026-07-25. Regenerate the derivation with
# `python3 sizing.py`; do not edit these numbers without re-running it.
SIZING = dict(
    per_side_brake_W=588,     # 1000 We pair / 0.85 alternator / 2 sides
    gas="helium", p_mean_bar=20.0, p_shell_rating_bar=30.0, freq_hz=50.0,
    Th_K=873.0, Tk_K=330.0,
    bore=60.0,                # power piston bore
    piston_stroke=24.3,       # amplitude 12.15
    disp_stroke=26.7,         # amplitude 13.35 (1.1x piston swept)
    disp_phase_deg=70.0,      # displacer leads piston
    p_max_bar=25.0, p_min_bar=16.0,   # Schmidt pressure wave
    Q_in_side_W=2100.0,       # heater duty per side (fire ~7 kW for pair)
    heater_gas_area_cm2=420,  # gas-side, needs extended surface
    heater_flame_area_cm2=1051,
    cooler_area_cm2=673,      # water-side
    regen_void_cc=48, regen_id=72.0, regen_radial=12.0, regen_len=22.0,
    bounce_vol_cc=103, mover_mass_kg=2.62, gas_spring_N_mm=259.0,
    air_commissioning="7 bar air -> 27 Hz, ~120 We pair",
)

# --------------------------------------- Phase 2 envelope layout (provisional)
# Axial stack per side, s = distance from engine centre along the axis (mm).
# Side B mirrors. The engine axis is HORIZONTAL (world X in the assembly,
# Z up); the firebox sits below, plenum around the hot ends, flue on top.
# Envelope-level: proportions for the viewer model, refined in Phase 3.
LAYOUT = dict(
    flame_gap=70.0,           # clear space between the two hot-cap dome tips
    hotcap_z=35.0,            # hot cap inboard (dome tip) position
    hotcap_len=114.0,         # dome + stepped wall to cold flange (s 35..149)
    # -- annular gas path (expansion -> heater -> regen -> cooler -> compression)
    dome_or=44.0, dome_wall=6.0,            # dome outer shell
    dome_cav_r=31.5,                        # conformal cavity over the Ø57
                                            # displacer nose (3 mm gap) +
                                            # cone out to the Ø76 annulus
    fire_tube_id=76.0, fire_tube_od=88.0,   # heater zone outer wall (in fire)
    step_s=126.0,                           # wall steps out here (outboard of
                                            # the plenum wall + panel zone)
    regen_zone_id=96.0, regen_zone_od=108.0,  # outer wall over regen matrix
    disp_cyl=(78.0, 171.0), disp_cyl_id=60.0, disp_cyl_od=68.0,  # inner wall;
                                            # seats on the cold head Ø68
                                            # shoulder, press fit + Loctite
                                            # 620 (or TIG tack) at assembly
    fin_od=130.0, fin_zone=(80.0, 106.0),   # heater fins on fire tube
    regen_ring=(127.0, 149.0),              # matrix len 22 per sizing
    regen_matrix_id=70.0, regen_matrix_od=94.0,
    # -- cold head: billet joining hot cap to hull, carries cooler + ports
    #    (assembly: inserts slide over the displacer cylinder onto the cold
    #     head; the hot cap slides over the stack and bolts down)
    ch_span=(149.0, 175.0),                 # cold head axial span
    ch_bores=((94.0, 165.0), (68.0, 171.0), (60.0, 175.0)),  # (ID, to-s) steps
    cooler_ring=(150.0, 164.0),             # annular cooler insert inside ch
    # gas passes THROUGH the cooler via drilled axial passages (a solid
    # ring would block the annulus): 32+36 x Ø5 on two hole circles.
    # flow area ~1335 mm2 -> ~8 m/s peak; gas-side area ~150 cm2
    cooler_holes=((32, 78.0), (36, 88.0)), cooler_hole_d=5.0,
    port_n=8, port_d=8.0, port_pcd=76.0,    # axial gas ports to the hull face
    relief_r=(30.0, 41.0), relief_depth=4.0,  # ring groove in the LINER lip
                                              # face: gas turns ports -> bore
    # water gallery: cold head body is Ø180; the gallery lives OUTSIDE the
    # bolt circle (groove Ø160..172, s 157..163) with the Ø172 land open to
    # the OUTBOARD face, so the sleeve (SG-216, ID172/OD180) slides on from
    # the hull side before the hull is fitted - assemblable, and the bolt
    # holes stay clear. 8 radial Ø8 fingers (clocked between the studs)
    # carry water from the gallery down to r50, 3 mm from the cooler insert.
    ch_od=180.0,
    water_land=(153.0, 175.0), water_land_d=172.0,
    water_groove=(160.0, 172.0), water_span=(157.0, 163.0),
    sleeve_span=(153.0, 170.0),
    gland_w=3.0, gland_floor=166.0, gland_s=(153.5, 165.5),
    finger_n=8, finger_d=8.0, finger_r=50.0, finger_s=160.0,
    boss_d=16.0, boss_hole=10.0,            # water bosses on the sleeve, +/-Y
    flange_od=156.0, bcd=140.0, bolt_n=8, bolt_hole=9.0,   # M8 pattern
    oring_d=110.0, oring_w=4.5, oring_depth=2.8,
    # -- cold side
    neck_od=156.0,                          # hull neck (mates flange)
    bcd2=200.0, oring2_d=170.0,             # bounce-cap joint on Ø180 flange
    hull_z=175.0, hull_len=180.0,           # cold hull: piston + alternator
    alt_od=180.0, alt_zone=(235.0, 355.0),  # alternator housing section
    # -- linear alternator (moving magnet): stator clamped in the hull bore
    #    between an integral stop ring and the bounce cap spigot (+ wave
    #    spring); mover = radially-magnetised NdFeB ring on the piston skirt
    #    Core is axially SPLIT at the coil centre: the pre-wound potted
    #    coil drops into the open recess, halves clamp around it, the
    #    assembly slides into the hull.
    stator_core=(253.0, 343.0), core_split=298.0, core_od=159.0, core_id=122.0,
    coil_span=(283.0, 313.0), coil_od=150.0, coil_id=124.0, groove_id=152.0,
    # hull interior: Ø160 bore from the outboard face to 253, Ø150 to 235 -
    # the Ø160/Ø150 step is the stator seat (no undercut, lathe-friendly)
    bore_step=253.0, cavity_id=150.0, cavity_end=235.0,
    spigot_len=8.0, spigot_od=158.0, spigot_id=142.0,
    bolt2_hole=11.0,                        # M10 on the bounce joint (30 bar
                                            # separation load 68 kN over Ø170)
    # pressed honed liner (SG-217): lip clamped by the cold head, carries the
    # gas-turn relief groove in its lip face; hone after pressing
    liner_od=73.0, liner_lip_od=84.0, liner_lip_t=8.0,
    # piston gas spring: Ø50 post on the bounce cap runs in a sleeve on the
    # piston disc; sealed pocket ~71 cc adds ~180 kN/m (resonance budget:
    # working gas 79 + spring 180 = 259 kN/m for 2.62 kg at 50 Hz)
    post_od=49.8, post_tip=292.0, post_bore=30.0, post_bore_depth=57.0,
    post_stud_d=20.0, post_root=390.0,      # shoulder seats on the cap's
                                            # interior floor; M20 stud
    # (tip = disc face at max outstroke + 4 mm; mean gap 16 mm x Ø50 +
    #  internal bore = ~71 cc pocket, swings ~47..95 cc over the stroke)
    spring_sleeve_id=50.0, spring_sleeve_od=60.0, spring_sleeve_len=50.0,
    # -- mover: piston -> skirt -> end disc -> carrier tube -> magnet ring
    #    (NdFeB segments on the carrier OD, banded; separate part SG-213)
    skirt_len=35.0, disc_span=(80.0, 86.0),         # local, from piston face
    carrier_od=100.0, carrier_id=90.0, magnet_local=86.0,
    liner_ext=(235.0, 252.0), liner_ext_od=72.0,    # hull liner extension:
                                                    # rear band stays in the
                                                    # bore at full outstroke
    # -- PTFE rider bands (own parts; grooves in piston/displacer)
    band_w=8.0,
    piston_bands_local=(4.0, 33.0), piston_band_od=59.95, piston_band_id=54.0,
    disp_bands_local=(36.0, 70.0), disp_band_od=59.9, disp_band_id=53.0,
    bounce_z=355.0, bounce_len=55.0,
    disp_len=85.0, disp_od=59.0, disp_rod_d=12.0,
    disp_face_z=58.0,         # displacer inboard face, mean position
    piston_len=45.0, piston_od=59.8,
    magnet_od=120.0, magnet_len=50.0,
    piston_face_z=190.0,      # piston inboard face, mean position
    # -- firebox + plenum (world frame: X = engine axis, Z up, door on +Y)
    plenum_x=118.0,           # plenum outer half-length along axis (wall 8)
    plenum_y=95.0,            # half-width: close shroud over the Ø130 fins
    plenum_top=90.0, plenum_bot=-140.0,     # ~20 mm over the fin tips: flue
                                            # gas is forced THROUGH the fins,
                                            # not around them
    box_wall=8.0,
    firebox_top=-140.0, firebox_bot=-440.0, firebox_x=140.0, firebox_y=180.0,
    grate_z=-360.0,           # grate plate; ash pit below
    door_w=200.0, door_h=160.0, door_cz=-250.0,   # on +Y face
    flue_d=90.0, flue_h=80.0,
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
    stroke=24.3,          # piston stroke (sizing scenario E)
    freq_hz=0.5,          # viewer animation speed (visual, not engine speed)
)

# ------------------------------------------------------------------ title block
PROJECT = dict(
    name="Stirling Generator 1kW",
    author="Alex",
    units="mm",
    standard="ISO 2768-mK unless noted",
)
