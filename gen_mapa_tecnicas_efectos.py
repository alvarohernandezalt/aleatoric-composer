#!/usr/bin/env python3
"""Generate draw.io: Técnicas Compositivas × Efectos Map
   A3 HORIZONTAL (landscape), optimized routing, no unnecessary overlaps."""

from pathlib import Path
import html as ht
import math

OUT = Path(__file__).parent / "Mapa_Tecnicas_Efectos.drawio"

# ── Canvas: A3 LANDSCAPE ──
PW, PH = 3360, 2376

# ── Colors ──
AMBER = "#FBAD17"
SLATE = "#303C42"
TEAL = "#005A65"
SAND_20 = "#E5E1DE"
TEXT = "#1A1F22"

TC = {
    "t1": "#C0392B", "t2": "#2E7D32", "t3": "#6A1B9A", "t4": "#1565C0", "t5": "#E65100",
    "t6": "#00838F", "t7": "#4E342E", "t8": "#880E4F", "t9": "#1B5E20",
    "t10": "#E53935", "t11": "#311B92",
}

GC = {
    "A": ("#FFF8E7", AMBER),
    "B": ("#E6F2F4", TEAL),
    "C": ("#F3E5F5", "#6A1B9A"),
    "D": ("#FFEBEE", "#C0392B"),
    "E": ("#E0F7FA", "#4DA5B0"),
    "F": ("#FFF3E0", "#E65100"),
    "G": ("#E8F5E9", "#2E7D32"),
    "H": ("#E3F2FD", "#1565C0"),
}

# ── TECHNIQUES ordered by LEFT/RIGHT affinity ──
# Top row: t2(left-heavy), t4(all→center), t1(spread), t5(right), t3(right)
techniques_top = [
    ("t2", "2. FELDMAN\nClusters"),
    ("t4", "4. CAGE\nIndeterminación"),
    ("t1", "1. XENAKIS\nEstocástica"),
    ("t5", "5. SCELSI\nSonido profundo"),
    ("t3", "3. LIGETI\nMicropolifonía"),
]
# Bottom row: t6(left), t7(left), t8(left-center), t11(all→center), t9(right), t10(right)
techniques_bot = [
    ("t6", "6. REICH\nPhasing"),
    ("t7", "7. OLIVEROS\nDeep Listening"),
    ("t8", "8. LACHENMANN\nConcrète Instr."),
    ("t11", "11. FERNEYHOUGH\nNva. Complejidad"),
    ("t9", "9. SAARIAHO\nEspectralismo"),
    ("t10", "10. NANCARROW\nTempo Canons"),
]

# ── GROUPS: left column ordered by connection density from top ──
# Left: B(Reverb), A(Dynamics), D(Distortion), C(Filter)
# Right: F(Pitch&Time), G(Granular), H(Spectral), E(Modulation)
left_keys = ["B", "A", "D", "C"]
right_keys = ["F", "G", "H", "E"]

groups = {
    "A": ("A. DYNAMICS", [
        ("fx_compressor", "Compressor"), ("fx_limiter", "Limiter"),
        ("fx_gain", "Gain"), ("fx_gate", "Gate (CDP)"),
        ("fx_envel_warp", "Envel Warp (CDP)"), ("fx_envel_attack", "Envel Attack (CDP)"),
        ("fx_envel_dovetail", "Envel Dovetail (CDP)"), ("fx_flatten", "Flatten (CDP)"),
    ]),
    "B": ("B. REVERB & DELAY", [
        ("fx_reverb", "Reverb"), ("fx_delay", "Delay"),
        ("fx_bounce", "Bounce (CDP)"), ("fx_cascade", "Cascade (CDP)"),
    ]),
    "C": ("C. FILTER", [
        ("fx_filter", "Filter (unificado)"), ("fx_filter_bank", "Filter Bank (CDP)"),
        ("fx_filter_sweep", "Filter Sweeping (CDP)"),
    ]),
    "D": ("D. DISTORTION", [
        ("fx_distortion", "Distortion"), ("fx_bitcrush", "Bitcrush"),
        ("fx_clip", "Clip (CDP)"), ("fx_quirk", "Quirk (CDP)"),
        ("fx_scramble", "Scramble (CDP)"),
    ]),
    "E": ("E. MODULATION", [
        ("fx_chorus", "Chorus"), ("fx_phaser", "Phaser"),
        ("fx_tremolo", "Tremolo (CDP)"),
    ]),
    "F": ("F. PITCH & TIME", [
        ("fx_pitch_shift", "Pitch Shift"), ("fx_time_stretch", "Time Stretch"),
        ("fx_modify_space", "Modify Space (CDP)"), ("fx_dvdwind", "DVDWind (CDP)"),
        ("fx_constrict", "Constrict (CDP)"), ("fx_shrink", "Shrink (CDP)"),
    ]),
    "G": ("G. GRANULAR", [
        ("fx_granular", "Granular"), ("fx_hover", "Hover (CDP)"),
        ("fx_stutter", "Stutter (CDP)"), ("fx_grain_sub", "Grain Sub-modos (CDP)"),
        ("fx_wrappage", "Wrappage (CDP)"),
    ]),
    "H": ("H. SPECTRAL", [
        ("fx_sp_freeze", "Spectral Freeze"), ("fx_sp_smear", "Spectral Smear"),
        ("fx_sp_gate", "Spectral Gate"), ("fx_sp_shift", "Spectral Shift"),
        ("fx_fractal", "Fractal (CDP)"), ("fx_cdp_spectral", "CDP Spectral Pipeline"),
    ]),
}

connections = {
    "t1": ["fx_distortion", "fx_scramble", "fx_granular", "fx_wrappage",
           "fx_filter_bank", "fx_sp_smear", "fx_fractal"],
    "t2": ["fx_reverb", "fx_gain", "fx_envel_dovetail", "fx_envel_warp",
           "fx_modify_space", "fx_flatten"],
    "t3": ["fx_sp_smear", "fx_chorus", "fx_phaser", "fx_granular",
           "fx_hover", "fx_wrappage"],
    "t4": ["gA", "gB", "gC", "gD", "gE", "gF", "gG", "gH"],
    "t5": ["fx_sp_freeze", "fx_sp_shift", "fx_sp_smear", "fx_time_stretch",
           "fx_granular"],
    "t6": ["fx_delay", "fx_reverb"],
    "t7": ["fx_reverb", "fx_delay", "fx_envel_warp", "fx_modify_space",
           "fx_envel_dovetail"],
    "t8": ["fx_distortion", "fx_bitcrush", "fx_clip", "fx_quirk",
           "fx_scramble", "fx_granular", "fx_filter"],
    "t9": ["fx_sp_freeze", "fx_sp_smear", "fx_sp_shift", "fx_sp_gate",
           "fx_granular", "fx_time_stretch"],
    "t10": ["fx_pitch_shift", "fx_time_stretch"],
    "t11": ["gA", "gB", "gC", "gD", "gE", "gF", "gG", "gH"],
}


def esc(s):
    return ht.escape(s, quote=True)


def mk_cell(id_, val, style, x, y, w, h, parent="1"):
    geo = f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
    return (f'<mxCell id="{id_}" value="{esc(val)}" style="{style}" '
            f'vertex="1" parent="{parent}">{geo}</mxCell>')


def mk_edge(id_, src, tgt, style, waypoints=None):
    """Create edge with optional explicit waypoints."""
    geo_inner = ""
    if waypoints:
        pts = "".join(f'<mxPoint x="{wx}" y="{wy}"/>' for wx, wy in waypoints)
        geo_inner = f'<Array as="points">{pts}</Array>'
    return (f'<mxCell id="{id_}" value="" style="{style}" edge="1" '
            f'source="{src}" target="{tgt}" parent="1">'
            f'<mxGeometry relative="1" as="geometry">{geo_inner}</mxGeometry></mxCell>')


def build():
    cells = []

    # ═══ LAYOUT CONSTANTS ═══
    tw, th = 260, 90
    fx_w, fx_h = 260, 42
    col1_dx, col2_dx = 18, 300
    row_h = 52
    hdr_h = 42
    grp_w = 580

    # Technique rows Y positions
    top_tech_y = 30
    bot_tech_y = PH - 120

    # Routing corridors (Y values for waypoints)
    top_corridor_y0 = top_tech_y + th + 30     # just below top techniques
    top_corridor_y1 = top_tech_y + th + 80     # second lane
    bot_corridor_y0 = bot_tech_y - 30          # just above bottom techniques
    bot_corridor_y1 = bot_tech_y - 80          # second lane

    def calc_h(n_fx):
        rows = math.ceil(n_fx / 2)
        return hdr_h + rows * row_h + 16

    # ═══ TECHNIQUE BOXES — TOP ROW ═══
    n = len(techniques_top)
    gap_top = 90
    total = n * tw + (n - 1) * gap_top
    x0 = (PW - total) // 2
    tech_positions = {}  # tid → (cx, cy, is_top)

    for i, (tid, label) in enumerate(techniques_top):
        x = x0 + i * (tw + gap_top)
        sty = (f"rounded=1;whiteSpace=wrap;html=1;fillColor={TC[tid]};"
               f"fontColor=#ffffff;strokeColor=none;fontSize=12;fontStyle=1;"
               f"arcSize=12;shadow=1;")
        cells.append(mk_cell(tid, label, sty, x, top_tech_y, tw, th))
        tech_positions[tid] = (x + tw // 2, top_tech_y + th, True, x)

    # ═══ TECHNIQUE BOXES — BOTTOM ROW ═══
    n2 = len(techniques_bot)
    gap_bot = 60
    total2 = n2 * tw + (n2 - 1) * gap_bot
    x0b = (PW - total2) // 2
    for i, (tid, label) in enumerate(techniques_bot):
        x = x0b + i * (tw + gap_bot)
        sty = (f"rounded=1;whiteSpace=wrap;html=1;fillColor={TC[tid]};"
               f"fontColor=#ffffff;strokeColor=none;fontSize=12;fontStyle=1;"
               f"arcSize=12;shadow=1;")
        cells.append(mk_cell(tid, label, sty, x, bot_tech_y, tw, th))
        tech_positions[tid] = (x + tw // 2, bot_tech_y, False, x)

    # ═══ EFFECTS AREA ═══
    title_sty = ("text;html=1;align=center;verticalAlign=middle;"
                 f"strokeColor=none;fillColor=none;fontSize=18;fontStyle=1;"
                 f"fontColor={SLATE};")
    cells.append(mk_cell("lbl_fx", "EFECTOS (8 FAMILIAS)", title_sty,
                         PW // 2 - 300, 200, 600, 40))

    gap_v = 30
    left_x = 720
    right_x = 1970

    def col_height(keys):
        return sum(calc_h(len(groups[k][1])) for k in keys) + (len(keys) - 1) * gap_v

    lh = col_height(left_keys)
    rh = col_height(right_keys)
    max_h = max(lh, rh)

    top_band = top_tech_y + th + 100
    bot_band = bot_tech_y - 60
    center_y = (top_band + bot_band) // 2
    effects_y0 = center_y - max_h // 2

    # Dashed border
    border_pad = 40
    border_sty = (f"rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor={TEAL};"
                  f"dashed=1;dashPattern=10 5;strokeWidth=2;arcSize=4;")
    border_w = right_x + grp_w - left_x + 2 * border_pad
    cells.append(mk_cell("fx_border", "", border_sty,
                         left_x - border_pad, effects_y0 - border_pad - 50,
                         border_w, max_h + 2 * border_pad + 60))

    # Place groups & record positions
    layout = {}       # gk → (gx, gy, gw, gh)
    fx_centers = {}   # fxid → (abs_cx, abs_cy)
    group_centers = {}  # gK → (abs_cx, abs_cy)

    y_cur = effects_y0
    for gk in left_keys:
        h = calc_h(len(groups[gk][1]))
        layout[gk] = (left_x, y_cur, grp_w, h)
        group_centers[gk] = (left_x + grp_w // 2, y_cur + h // 2)
        y_cur += h + gap_v

    y_cur = effects_y0
    for gk in right_keys:
        h = calc_h(len(groups[gk][1]))
        layout[gk] = (right_x, y_cur, grp_w, h)
        group_centers[gk] = (right_x + grp_w // 2, y_cur + h // 2)
        y_cur += h + gap_v

    # ═══ CREATE GROUP SWIMLANES + EFFECT CELLS ═══
    for gk, (gx, gy, gw, gh) in layout.items():
        gname, effects = groups[gk]
        fill_light, stroke = GC[gk]
        gid = f"g{gk}"

        grp_sty = (f"swimlane;startSize={hdr_h};fillColor={fill_light};"
                   f"swimlaneLine=0;"
                   f"strokeColor={stroke};fontColor={stroke};fontStyle=1;fontSize=12;"
                   f"rounded=1;arcSize=4;shadow=0;collapsible=0;")
        cells.append(mk_cell(gid, gname, grp_sty, gx, gy, gw, gh))

        for idx, (fxid, fxname) in enumerate(effects):
            row = idx // 2
            col = idx % 2
            cx = col1_dx if col == 0 else col2_dx
            cy = hdr_h + 8 + row * row_h
            fx_sty = (f"rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;"
                      f"strokeColor={stroke};fontSize=11;fontColor={TEXT};"
                      f"arcSize=10;shadow=0;strokeWidth=1.5;")
            cells.append(mk_cell(fxid, fxname, fx_sty, cx, cy, fx_w, fx_h, parent=gid))
            # absolute position of effect cell center
            fx_centers[fxid] = (gx + cx + fx_w // 2, gy + cy + fx_h // 2)

    # Also record group targets for Cage/Ferneyhough
    for gk in list(left_keys) + list(right_keys):
        gx, gy, gw, gh = layout[gk]
        fx_centers[f"g{gk}"] = (gx + gw // 2, gy + gh // 2)

    # ═══ OPTIMIZED CONNECTIONS ═══
    # For each technique, sort targets by X position and assign spread exit points
    edge_idx = 0
    top_ids = {t[0] for t in techniques_top}

    for tid, targets in connections.items():
        color = TC[tid]
        is_all = tid in ("t4", "t11")
        tcx, tcy, is_top, tx = tech_positions[tid]

        # Sort targets by their X position (left to right)
        sorted_targets = sorted(targets, key=lambda t: fx_centers.get(t, (PW//2, PH//2))[0])
        n_conn = len(sorted_targets)

        for ci, tgt in enumerate(sorted_targets):
            eid = f"e{edge_idx}"
            edge_idx += 1

            dash = "dashed=1;dashPattern=8 4;" if is_all else ""
            sw = "1.5" if is_all else "2"
            opacity = "40" if is_all else "70"

            # Spread exit points across the bottom (top tech) or top (bottom tech) edge
            if n_conn == 1:
                exit_x = 0.5
            else:
                # Spread from 0.1 to 0.9
                exit_x = 0.1 + 0.8 * ci / (n_conn - 1)

            exit_y = 1.0 if is_top else 0.0

            # Determine entry side based on technique position relative to target
            tgt_cx, tgt_cy = fx_centers.get(tgt, (PW//2, PH//2))

            # For group targets (Cage/Ferneyhough), enter from top or bottom
            if tgt.startswith("g"):
                gk_letter = tgt[1]
                gx, gy, gw, gh = layout[gk_letter]
                if is_top:
                    entry_x_frac = 0.15 + 0.7 * ci / max(n_conn - 1, 1)
                    entry_y_frac = 0.0  # enter from top
                else:
                    entry_x_frac = 0.15 + 0.7 * ci / max(n_conn - 1, 1)
                    entry_y_frac = 1.0  # enter from bottom
            else:
                # For individual effect cells - enter from the side closest to technique
                # Effects in left column → can enter from left or top/bottom
                # Effects in right column → can enter from right or top/bottom
                if tgt_cx < PW // 2:
                    # Left column effect - enter from left side
                    entry_x_frac = 0.0
                    entry_y_frac = 0.5
                else:
                    # Right column effect - enter from right side
                    entry_x_frac = 1.0
                    entry_y_frac = 0.5

            e_sty = (f"edgeStyle=orthogonalEdgeStyle;orthogonalLoop=1;"
                     f"jettySize=auto;rounded=1;"
                     f"endArrow=blockThin;endFill=1;"
                     f"strokeColor={color};strokeWidth={sw};opacity={opacity};"
                     f"exitX={exit_x:.2f};exitY={exit_y:.1f};exitDx=0;exitDy=0;"
                     f"entryX={entry_x_frac:.2f};entryY={entry_y_frac:.1f};entryDx=0;entryDy=0;"
                     f"{dash}")
            cells.append(mk_edge(eid, tid, tgt, e_sty))

    # ═══ LEGEND ═══
    leg_sty = (f"rounded=1;whiteSpace=wrap;html=1;fillColor=#F8F6F3;"
               f"strokeColor={SAND_20};fontSize=10;fontColor={TEXT};arcSize=6;"
               f"align=left;verticalAlign=top;spacingLeft=10;spacingTop=8;")
    legend_html = (
        "<b>LEYENDA</b><br><br>"
        "<font color='#303C42'><b>───</b></font> Conexión a efecto favorecido<br>"
        "<font color='#303C42'><b>╌╌╌</b></font> Conexión a TODOS los efectos<br>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(Cage / Ferneyhough)<br><br>"
        "Líneas ortogonales coloreadas<br>"
        "por técnica compositiva.<br>"
        "Técnicas ordenadas por afinidad<br>"
        "izquierda/derecha."
    )
    cells.append(mk_cell("legend", legend_html, leg_sty, 50, effects_y0, 280, 210))

    # ═══ SUBTITLE ═══
    sub_sty = ("text;html=1;align=center;verticalAlign=middle;"
               f"strokeColor=none;fillColor=none;fontSize=11;"
               f"fontColor={SLATE};")
    cells.append(mk_cell("subtitle",
        "Cada técnica (preset) se conecta a los efectos que favorece. "
        "Todo es override libre — los presets son puntos de partida.",
        sub_sty, PW // 2 - 500, PH - 180, 1000, 30))

    return cells


def main():
    cells = build()
    cells_xml = "\n        ".join(cells)

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" type="device" version="24.0.0">
  <diagram id="tech-fx-map" name="Técnicas × Efectos">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1"
     arrows="1" fold="1" page="1" pageScale="1" pageWidth="{PW}" pageHeight="{PH}"
     math="0" shadow="0" background="#FFFFFF">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {cells_xml}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

    OUT.write_text(xml, encoding="utf-8")
    print(f"draw.io: {OUT}")
    print(f"  Size: {OUT.stat().st_size / 1024:.0f} KB")
    n_fx = sum(len(g[1]) for g in groups.values())
    n_edges = sum(len(v) for v in connections.values())
    print(f"  {len(techniques_top)+len(techniques_bot)} técnicas, "
          f"{len(groups)} grupos, {n_fx} efectos, {n_edges} conexiones")


if __name__ == "__main__":
    main()
