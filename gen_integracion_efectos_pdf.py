#!/usr/bin/env python3
"""
Genera PDF: Análisis de Integración de Efectos v0.1 → v0.2
Compara efectos actuales (pedalboard/spectral/granular) con CDP.
Usa la paleta de diseño: Amber, Slate, Teal, Sand.
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, ListFlowable, ListItem
)

# ── Design System Colors ──
AMBER = HexColor("#FBAD17")
AMBER_10 = HexColor("#FFF8E7")
AMBER_20 = HexColor("#FEEFC3")
AMBER_120 = HexColor("#D9920A")
AMBER_140 = HexColor("#A86E07")

SLATE = HexColor("#303C42")
SLATE_10 = HexColor("#EEF0F1")
SLATE_20 = HexColor("#CDD1D4")
SLATE_40 = HexColor("#8D969C")
SLATE_60 = HexColor("#566066")
SLATE_80 = HexColor("#3D4A51")
SLATE_120 = HexColor("#1E282D")
SLATE_140 = HexColor("#101518")

TEAL = HexColor("#005A65")
TEAL_10 = HexColor("#E6F2F4")
TEAL_20 = HexColor("#B3D9DE")
TEAL_40 = HexColor("#4DA5B0")
TEAL_60 = HexColor("#007D8C")

SAND = HexColor("#A69C95")
SAND_10 = HexColor("#F6F4F2")
SAND_20 = HexColor("#E5E1DE")
SAND_40 = HexColor("#C7BFB9")
SAND_120 = HexColor("#857870")
SAND_140 = HexColor("#5E534C")

BG = HexColor("#F8F6F3")
WHITE = HexColor("#FFFFFF")
TEXT = HexColor("#1A1F22")
TEXT_MUTED = HexColor("#6B7780")

# Status colors
KEEP = HexColor("#1A7A4A")       # green - keep
REPLACE = HexColor("#C0392B")    # red - replace
UPGRADE = TEAL                   # teal - upgrade/enhance
NEW = AMBER_120                  # amber dark - new from CDP

OUT_PATH = Path(__file__).parent / "Integracion_Efectos_v02.pdf"


def styles():
    s = getSampleStyleSheet()

    s.add(ParagraphStyle('DocTitle', fontSize=26, leading=32, textColor=white,
                         spaceAfter=4*mm, alignment=TA_CENTER, fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('DocSub', fontSize=11, leading=15, textColor=SAND_40,
                         spaceAfter=8*mm, alignment=TA_CENTER, fontName='Helvetica'))
    s.add(ParagraphStyle('SectionH', fontSize=15, leading=20, textColor=white,
                         spaceBefore=6*mm, spaceAfter=4*mm, fontName='Helvetica-Bold',
                         backColor=SLATE, borderPadding=(3*mm, 4*mm, 3*mm, 4*mm)))
    s.add(ParagraphStyle('SubH', fontSize=12, leading=16, textColor=TEAL,
                         spaceBefore=5*mm, spaceAfter=2*mm, fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('Body', fontSize=9.5, leading=14, textColor=TEXT,
                         spaceAfter=2*mm, fontName='Helvetica', alignment=TA_JUSTIFY))
    s.add(ParagraphStyle('BodyBold', fontSize=9.5, leading=14, textColor=TEXT,
                         spaceAfter=2*mm, fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('SmallNote', fontSize=8, leading=11, textColor=TEXT_MUTED,
                         spaceAfter=2*mm, fontName='Helvetica-Oblique'))
    s.add(ParagraphStyle('TCell', fontSize=8.5, leading=11, textColor=TEXT,
                         fontName='Helvetica'))
    s.add(ParagraphStyle('TCellBold', fontSize=8.5, leading=11, textColor=TEXT,
                         fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('THead', fontSize=8.5, leading=11, textColor=white,
                         fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('Decision', fontSize=10, leading=14, textColor=SLATE,
                         spaceBefore=3*mm, spaceAfter=2*mm, fontName='Helvetica-Bold',
                         backColor=AMBER_10, borderPadding=(2*mm, 3*mm, 2*mm, 3*mm)))
    s.add(ParagraphStyle('GroupTitle', fontSize=13, leading=17, textColor=AMBER_140,
                         spaceBefore=6*mm, spaceAfter=3*mm, fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('FxBullet', fontSize=9.5, leading=14, textColor=TEXT,
                         leftIndent=10*mm, bulletIndent=4*mm, spaceAfter=1*mm,
                         fontName='Helvetica'))
    return s


def make_table(headers, rows, st, col_widths=None):
    """Build a styled table."""
    avail = 170 * mm
    ncols = len(headers)
    if not col_widths:
        col_widths = [avail / ncols] * ncols

    data = [[Paragraph(h, st['THead']) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), st['TCell']) for c in row])

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SLATE),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2*mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 2*mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2*mm),
        ('GRID', (0, 0), (-1, -1), 0.4, SAND_20),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, SAND_10]),
    ]))
    return t


def status_tag(text, color):
    return f'<font color="{color.hexval()}"><b>{text}</b></font>'


def build(st):
    e = []
    W = 170 * mm

    # ═══════════════════════════════════════════════════
    # COVER
    # ═══════════════════════════════════════════════════
    e.append(Spacer(1, 35*mm))
    e.append(Paragraph("Integración de Efectos", st['DocTitle']))
    e.append(Paragraph("Aleatoric Composer v0.1 → v0.2", st['DocSub']))
    e.append(Spacer(1, 8*mm))
    e.append(HRFlowable(width="50%", thickness=2, color=AMBER, spaceAfter=8*mm))
    e.append(Spacer(1, 4*mm))

    legend_data = [
        [status_tag("MANTENER", KEEP), "Efecto actual que se conserva tal cual"],
        [status_tag("REEMPLAZAR", REPLACE), "Efecto actual que se sustituye por CDP"],
        [status_tag("MEJORAR", UPGRADE), "Efecto actual que se potencia con CDP"],
        [status_tag("NUEVO", NEW), "Efecto CDP sin equivalente actual — se añade"],
    ]
    for tag, desc in legend_data:
        e.append(Paragraph(f"{tag}  —  {desc}", st['Body']))
    e.append(Spacer(1, 6*mm))

    e.append(Paragraph(
        "Este documento analiza los 18 efectos actuales de v0.1, evalúa cuáles conviven con los "
        "efectos CDP, cuáles se reemplazan, y propone la nueva agrupación para v0.2.",
        st['Body']
    ))

    # ═══════════════════════════════════════════════════
    # 1. INVENTARIO ACTUAL v0.1
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("1. Inventario de Efectos Actuales (v0.1)", st['SectionH']))
    e.append(Spacer(1, 3*mm))

    e.append(Paragraph("La app cuenta con 18 efectos en 4 backends:", st['Body']))

    e.append(Paragraph("1.1 Pedalboard (Spotify) — 12 efectos", st['SubH']))
    pb_rows = [
        ["reverb", "room_size, damping, wet/dry, width", "Reverb algorítmico básico"],
        ["delay", "delay_seconds, feedback, mix", "Delay simple con feedback"],
        ["pitch_shift", "semitones (-24 a +24)", "Pitch shift (no time-stretch)"],
        ["distortion", "drive_db (0-100)", "Distorsión simple por saturación"],
        ["compressor", "threshold, ratio, attack, release", "Compresor dinámico"],
        ["gain", "gain_db (-60 a +30)", "Control de ganancia"],
        ["limiter", "threshold_db, release_ms", "Limitador de picos"],
        ["chorus", "rate_hz, depth, mix", "Chorus básico"],
        ["phaser", "rate_hz, depth, mix", "Phaser básico"],
        ["highpass_filter", "cutoff_frequency_hz", "HPF simple (1 param)"],
        ["lowpass_filter", "cutoff_frequency_hz", "LPF simple (1 param)"],
        ["bitcrush", "bit_depth (1-24)", "Reducción de bit depth"],
    ]
    e.append(make_table(["Efecto", "Parámetros", "Descripción"], pb_rows, st,
                        col_widths=[W*0.18, W*0.40, W*0.42]))

    e.append(Paragraph("1.2 Spectral (librosa STFT) — 4 efectos", st['SubH']))
    sp_rows = [
        ["spectral_freeze", "freeze_position, output_duration", "Congela un frame STFT y lo sostiene"],
        ["spectral_smear", "smear_amount, time_smear", "Blur gaussiano en frecuencia"],
        ["spectral_gate", "threshold (0-1)", "Zeroes bins bajo umbral"],
        ["spectral_shift", "shift_bins (-200 a +200)", "Desplaza bins (inarmónico)"],
    ]
    e.append(make_table(["Efecto", "Parámetros", "Descripción"], sp_rows, st,
                        col_widths=[W*0.20, W*0.38, W*0.42]))

    e.append(Paragraph("1.3 Granular — 1 efecto", st['SubH']))
    gr_rows = [
        ["granular", "grain_size, density, scatter, position_random, pitch_random, amp_random, reverse_prob",
         "Granulador con 7 parámetros expuestos + 6 ocultos"],
    ]
    e.append(make_table(["Efecto", "Parámetros", "Descripción"], gr_rows, st,
                        col_widths=[W*0.15, W*0.50, W*0.35]))

    e.append(Paragraph("1.4 Time Stretch — 1 efecto", st['SubH']))
    ts_rows = [
        ["time_stretch", "rate (0.1-4.0)", "Phase vocoder vía librosa (preserva pitch)"],
    ]
    e.append(make_table(["Efecto", "Parámetros", "Descripción"], ts_rows, st,
                        col_widths=[W*0.18, W*0.32, W*0.50]))

    # ═══════════════════════════════════════════════════
    # 2. ANÁLISIS EFECTO POR EFECTO
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("2. Análisis Efecto por Efecto: Qué Pasa con Cada Uno", st['SectionH']))
    e.append(Spacer(1, 3*mm))

    decisions = [
        # (nombre, estado, color, explicación)
        ("reverb", "MEJORAR", UPGRADE,
         "El reverb de Pedalboard es funcional pero básico. CDP ofrece <b>reverb</b> (multicanal con absorción HF, predelay, LP/HP), "
         "<b>rmverb</b> (simulación de sala) y <b>fastconv</b> (convolución). "
         "Propuesta: mantener el reverb actual como opción rápida y añadir los CDP como variantes avanzadas."),

        ("delay", "MEJORAR", UPGRADE,
         "El delay actual es mono-tap simple. CDP tiene <b>sfecho</b> (echo con randomización), "
         "<b>tapdelay</b> (multi-tap stereo con panning), <b>newdelay</b> (pitch-based) y "
         "<b>modify revecho</b> (3 modos: estándar, LFO, stadium). "
         "Propuesta: conservar delay actual como 'Simple Delay' y añadir versiones CDP como variantes."),

        ("pitch_shift", "REEMPLAZAR", REPLACE,
         "El pitch_shift de Pedalboard solo tiene 1 parámetro (semitones) y no preserva tiempo. "
         "CDP <b>modify speed</b> ofrece 4 modos (multiplicador, semitonos, aceleración, vibrato) "
         "y <b>strans multi</b> añade soporte multicanal. "
         "Propuesta: reemplazar por modify speed (más versátil) con UI simplificada."),

        ("distortion", "REEMPLAZAR", REPLACE,
         "Distorsión actual: un solo parámetro (drive_db). CDP <b>distort</b> tiene 21 sub-modos: "
         "fractal, harmonic, overload, reform (8 waveshapes), pitch, pulsed... "
         "Además: <b>clip</b>, <b>quirk</b> (potencia de muestras), <b>scramble</b> (reordena wavesets). "
         "Propuesta: reemplazar por un panel 'Distortion' con los sub-modos CDP más útiles."),

        ("compressor", "MANTENER", KEEP,
         "No hay equivalente directo en CDP. El compresor de Pedalboard es sólido con threshold, ratio, "
         "attack y release. Se mantiene tal cual."),

        ("gain", "MANTENER", KEEP,
         "Utilidad básica esencial. No tiene sentido reemplazar. Se conserva."),

        ("limiter", "MANTENER", KEEP,
         "Igual que gain y compressor: utility indispensable sin equivalente CDP. Se conserva."),

        ("chorus", "MEJORAR", UPGRADE,
         "El chorus actual tiene 3 params expuestos (rate, depth, mix). CDP <b>blur chorus</b> (spectral) ofrece "
         "7 modos de chorusing con control de amp_spread y freq_spread. "
         "Propuesta: mantener chorus rápido + añadir Spectral Chorus como variante."),

        ("phaser", "MEJORAR", UPGRADE,
         "El phaser actual es básico (rate, depth, mix). CDP <b>filter phasing</b> tiene 2 modos (allpass, clásico) "
         "y <b>phasor</b> genera phasing por 2-8 streams con spatial output. "
         "Propuesta: mantener phaser rápido + añadir variantes CDP."),

        ("highpass_filter", "REEMPLAZAR", REPLACE,
         "Solo 1 parámetro (cutoff). CDP <b>filter variable</b> (modo 4=HP) con acuity y gain, "
         "<b>filter sweeping</b> (HP con sweep LFO), <b>filter lohi</b> (HP/LP con rolloff). "
         "Propuesta: reemplazar por un módulo Filter unificado con modo HP/LP/BP/Notch."),

        ("lowpass_filter", "REEMPLAZAR", REPLACE,
         "Misma situación que highpass. Se fusiona en el módulo Filter unificado con los CDP."),

        ("bitcrush", "MANTENER", KEEP,
         "Efecto único sin equivalente CDP. Lo-fi / retro. Se conserva."),

        ("spectral_freeze", "MANTENER", KEEP,
         "Implementación propia con librosa STFT. CDP <b>focus freeze</b> existe pero requiere pipeline "
         "specanal→pvoc. La versión actual es más directa. Se conserva, quizá con mejoras internas."),

        ("spectral_smear", "MEJORAR", UPGRADE,
         "Blur gaussiano propio. CDP <b>blur blur</b> y <b>blur avrg</b> ofrecen más control (temporal averaging, "
         "N canales adyacentes). Pero requieren pipeline spectral. "
         "Propuesta: mantener la versión directa + ofrecer versiones CDP como 'Spectral Smear (Advanced)'."),

        ("spectral_gate", "MANTENER", KEEP,
         "Implementación directa vía STFT. CDP tiene gate pero orientado a envelope, no espectral. "
         "Se conserva con posible refinamiento."),

        ("spectral_shift", "MANTENER", KEEP,
         "Desplazamiento de bins (inarmónico). Sin equivalente directo en CDP WAV. Se conserva."),

        ("granular", "MEJORAR", UPGRADE,
         "El granulador actual tiene 7+6 parámetros. CDP ofrece: <b>grain</b> (16 sub-modos), "
         "<b>wrappage</b> (granulación multicanal completa), <b>hover</b>/<b>hover2</b> (zigzag), "
         "<b>stutter</b> (tartamudeo), <b>modify brassage</b> (Wishart). "
         "Propuesta: mantener granulador actual como modo 'Simple' y añadir sub-modos CDP."),

        ("time_stretch", "MEJORAR", UPGRADE,
         "Phase vocoder vía librosa. CDP <b>modify speed</b> y <b>spectstr</b> (anti-artefactos) ofrecen más opciones. "
         "Propuesta: mantener como default y añadir variante CDP para stretch largos."),
    ]

    for name, status, color, explanation in decisions:
        block = []
        tag = status_tag(status, color)
        block.append(Paragraph(f"{tag}  <b>{name}</b>", st['SubH']))
        block.append(Paragraph(explanation, st['Body']))
        block.append(HRFlowable(width="100%", thickness=0.3, color=SAND_20, spaceAfter=1*mm))
        e.append(KeepTogether(block))

    # ═══════════════════════════════════════════════════
    # 3. RESUMEN DE DECISIONES
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("3. Resumen de Decisiones", st['SectionH']))
    e.append(Spacer(1, 3*mm))

    summary_rows = [
        [status_tag("MANTENER", KEEP), "compressor, gain, limiter, bitcrush, spectral_freeze, spectral_gate, spectral_shift", "7"],
        [status_tag("MEJORAR", UPGRADE), "reverb, delay, chorus, phaser, spectral_smear, granular, time_stretch", "7"],
        [status_tag("REEMPLAZAR", REPLACE), "pitch_shift, distortion, highpass_filter, lowpass_filter", "4"],
    ]
    e.append(make_table(["Estado", "Efectos", "#"], summary_rows, st,
                        col_widths=[W*0.15, W*0.72, W*0.13]))

    e.append(Spacer(1, 4*mm))
    e.append(Paragraph("Resultado: 0 efectos eliminados. Los 18 se conservan o evolucionan.", st['Decision']))

    # ═══════════════════════════════════════════════════
    # 4. EFECTOS CDP NUEVOS PROPUESTOS
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("4. Efectos CDP Nuevos (Sin Equivalente Actual)", st['SectionH']))
    e.append(Spacer(1, 3*mm))

    e.append(Paragraph(
        "Estos efectos no tienen equivalente en v0.1 y se proponen como adiciones nuevas para v0.2. "
        "Se dividen en dos prioridades:", st['Body']
    ))

    e.append(Paragraph("4.1 Prioridad ALTA — Integrar en v0.2", st['SubH']))
    p1_rows = [
        ["bounce", "WAV", "Rebotes con aceleración y decaimiento", "Baja"],
        ["constrict", "WAV", "Acortar silencios (compresión temporal)", "Baja"],
        ["fractal", "WAV", "Capas fractales de sonido", "Baja"],
        ["dvdwind", "WAV", "Contracción por read-skip", "Baja"],
        ["envel warp", "WAV", "15 modos de deformación de envelope", "Media"],
        ["envel attack", "WAV", "Enfatizar/exagerar ataque", "Baja"],
        ["envel dovetail", "WAV", "Fade in/out con curvas", "Baja"],
        ["tremolo", "WAV", "Tremolo con narrowing", "Baja"],
        ["modify space", "WAV", "Pan stereo (3 modos)", "Baja"],
        ["scramble", "WAV", "Reordenar wavesets (6 modos)", "Baja"],
        ["shrink", "WAV", "Repetir acortando progresivamente", "Baja"],
        ["hover", "WAV", "Lectura granular zigzag", "Media"],
        ["stutter", "WAV", "Tartamudeo de sílabas", "Media"],
    ]
    e.append(make_table(["Efecto CDP", "Tipo", "Descripción", "Complejidad"], p1_rows, st,
                        col_widths=[W*0.17, W*0.08, W*0.55, W*0.20]))

    e.append(Paragraph("4.2 Prioridad MEDIA — Evaluar para v0.2 o v0.3", st['SubH']))
    p2_rows = [
        ["filter bank", "WAV", "Banco de filtros con Q variable (6 modos)", "Media"],
        ["filter sweeping", "WAV", "Filtro con barrido LFO", "Media"],
        ["filter varibank", "WAV", "Banco de filtros variable en el tiempo", "Alta"],
        ["distort fractal", "WAV", "Miniatura del wavecycle sobre sí mismo", "Baja"],
        ["distort reform", "WAV", "Cambia waveshape (8 tipos)", "Baja"],
        ["distort overload", "WAV", "Clip con ruido o waveform", "Baja"],
        ["distort pulsed", "WAV", "Tren de impulsos sobre la fuente", "Media"],
        ["grain omit", "WAV", "Omitir proporción de granos", "Baja"],
        ["grain timewarp", "WAV", "Stretch sin estirar granos", "Baja"],
        ["grain reverse", "WAV", "Invertir orden de granos", "Baja"],
        ["wrappage", "WAV", "Granulación multicanal completa", "Alta"],
        ["cascade", "WAV", "Echo-cascada de segmentos", "Media"],
        ["motor", "WAV", "Pulsos rápidos dentro de pulsos lentos", "Media"],
        ["cantor", "WAV", "Conjunto de Cantor (fractal)", "Baja"],
        ["brownian", "WAV", "Textura browniana multicanal", "Media"],
    ]
    e.append(make_table(["Efecto CDP", "Tipo", "Descripción", "Complejidad"], p2_rows, st,
                        col_widths=[W*0.17, W*0.08, W*0.55, W*0.20]))

    e.append(Paragraph("4.3 Spectral CDP — Requieren pipeline specanal→pvoc", st['SubH']))
    e.append(Paragraph(
        "Los efectos espectrales CDP (blur, morph, focus, hilite, specfnu, stretch...) son potentísimos "
        "pero requieren un pipeline de 3 pasos: specanal → efecto → pvoc. Esto implica escribir archivos temporales "
        "y un tiempo de proceso mayor. Se recomienda implementar el pipeline spectral como infraestructura en v0.2 "
        "y luego ir habilitando efectos spectrales incrementalmente.", st['Body']
    ))

    spec_rows = [
        ["blur (10 modos)", "Difuminado espectral: averaging, chorus, drunk walk, shuffle, noise..."],
        ["morph / newmorph", "Morphing entre dos espectros"],
        ["focus (7 modos)", "Enfoque espectral: accumulate, exaggerate, freeze, hold, step..."],
        ["hilite (8 modos)", "Resaltado: filter, arpeg, pluck, trace, vowels..."],
        ["specfnu (23 modos)", "Manipulación de formantes: estrechar, invertir, rotar, arpegiar..."],
        ["stretch", "Stretch de frecuencias y temporal"],
        ["glisten", "Partición aleatoria del espectro"],
    ]
    e.append(make_table(["Efecto Spectral", "Descripción"], spec_rows, st,
                        col_widths=[W*0.25, W*0.75]))

    # ═══════════════════════════════════════════════════
    # 5. PROPUESTA DE AGRUPACIÓN v0.2
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("5. Propuesta de Agrupación para v0.2", st['SectionH']))
    e.append(Spacer(1, 3*mm))

    e.append(Paragraph(
        "En v0.1 los 18 efectos aparecen en una lista plana en el panel Effects Palette. "
        "Para v0.2 se proponen 8 grupos temáticos que mezclan efectos actuales y CDP:", st['Body']
    ))

    groups = [
        ("A. DYNAMICS", AMBER,
         [("compressor", "MANTENER — Pedalboard"),
          ("limiter", "MANTENER — Pedalboard"),
          ("gain", "MANTENER — Pedalboard"),
          ("gate (CDP)", "NUEVO — Puerta de ruido"),
          ("envel warp (CDP)", "NUEVO — 15 modos de envelope"),
          ("envel attack (CDP)", "NUEVO — Enfatizar ataque"),
          ("envel dovetail (CDP)", "NUEVO — Fade in/out"),
          ("flatten (CDP)", "NUEVO — Ecualizar nivel de elementos"),
         ]),
        ("B. REVERB &amp; DELAY", TEAL,
         [("reverb", "MEJORAR — Actual + CDP reverb/rmverb"),
          ("delay", "MEJORAR — Actual + sfecho/tapdelay/revecho"),
          ("bounce (CDP)", "NUEVO — Rebotes con aceleración"),
          ("cascade (CDP)", "NUEVO — Echo-cascada"),
         ]),
        ("C. FILTER", SLATE_60,
         [("filter (unificado)", "REEMPLAZAR — LP/HP/BP/Notch con acuity, gain, sweep"),
          ("filter bank (CDP)", "NUEVO — Banco con Q variable"),
          ("filter sweeping (CDP)", "NUEVO — Sweep LFO"),
         ]),
        ("D. DISTORTION", HexColor("#C0392B"),
         [("distortion", "REEMPLAZAR — CDP distort sub-modos"),
          ("bitcrush", "MANTENER — Pedalboard"),
          ("clip (CDP)", "NUEVO — Recorte de señal"),
          ("quirk (CDP)", "NUEVO — Distorsión por potencia"),
          ("scramble (CDP)", "NUEVO — Reordenar wavesets"),
         ]),
        ("E. MODULATION", TEAL_40,
         [("chorus", "MEJORAR — Actual + blur chorus spectral"),
          ("phaser", "MEJORAR — Actual + CDP phasing/phasor"),
          ("tremolo (CDP)", "NUEVO — Tremolo con narrowing"),
         ]),
        ("F. PITCH &amp; TIME", AMBER_120,
         [("pitch_shift", "REEMPLAZAR — CDP modify speed (4 modos)"),
          ("time_stretch", "MEJORAR — Actual + CDP stretch"),
          ("modify space (CDP)", "NUEVO — Pan stereo 3 modos"),
          ("dvdwind (CDP)", "NUEVO — Contracción read-skip"),
          ("constrict (CDP)", "NUEVO — Acortar silencios"),
          ("shrink (CDP)", "NUEVO — Repetir acortando"),
         ]),
        ("G. GRANULAR", HexColor("#1A7A4A"),
         [("granular", "MEJORAR — Actual (modo Simple) + CDP sub-modos"),
          ("hover (CDP)", "NUEVO — Lectura zigzag"),
          ("stutter (CDP)", "NUEVO — Tartamudeo"),
          ("grain sub-modos (CDP)", "NUEVO — omit, timewarp, reverse, duplicate..."),
          ("wrappage (CDP)", "NUEVO — Granulación multicanal"),
         ]),
        ("H. SPECTRAL", HexColor("#7B2D8E"),
         [("spectral_freeze", "MANTENER — librosa STFT"),
          ("spectral_smear", "MEJORAR — Actual + blur CDP"),
          ("spectral_gate", "MANTENER — librosa STFT"),
          ("spectral_shift", "MANTENER — librosa STFT"),
          ("fractal (CDP)", "NUEVO — Capas fractales"),
          ("CDP spectral pipeline", "FUTURO — blur, morph, focus, hilite, specfnu..."),
         ]),
    ]

    for group_name, color, effects in groups:
        block = []
        block.append(Paragraph(
            f'<font color="{color.hexval()}">{group_name}</font>',
            st['GroupTitle']
        ))
        for fx_name, fx_desc in effects:
            # Color the status word
            if "MANTENER" in fx_desc:
                fx_desc = fx_desc.replace("MANTENER", status_tag("MANTENER", KEEP))
            elif "MEJORAR" in fx_desc:
                fx_desc = fx_desc.replace("MEJORAR", status_tag("MEJORAR", UPGRADE))
            elif "REEMPLAZAR" in fx_desc:
                fx_desc = fx_desc.replace("REEMPLAZAR", status_tag("REEMPLAZAR", REPLACE))
            elif "NUEVO" in fx_desc:
                fx_desc = fx_desc.replace("NUEVO", status_tag("NUEVO", NEW))
            elif "FUTURO" in fx_desc:
                fx_desc = fx_desc.replace("FUTURO", status_tag("FUTURO", TEXT_MUTED))

            block.append(Paragraph(f"<bullet>&bull;</bullet><b>{fx_name}</b> — {fx_desc}", st['FxBullet']))

        block.append(Spacer(1, 2*mm))
        e.append(KeepTogether(block))

    # ═══════════════════════════════════════════════════
    # 6. CONTEO FINAL
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("6. Conteo y Arquitectura Final", st['SectionH']))
    e.append(Spacer(1, 3*mm))

    count_rows = [
        ["Efectos actuales (v0.1)", "18", "12 pedalboard + 4 spectral + 1 granular + 1 time_stretch"],
        ["Se mantienen sin cambios", "7", "compressor, gain, limiter, bitcrush, sp_freeze, sp_gate, sp_shift"],
        ["Se mejoran (actual + CDP)", "7", "reverb, delay, chorus, phaser, sp_smear, granular, time_stretch"],
        ["Se reemplazan por CDP", "4", "pitch_shift, distortion, highpass_filter, lowpass_filter"],
        ["Efectos CDP nuevos (prio alta)", "13", "bounce, constrict, fractal, dvdwind, envel×3, tremolo, space, scramble, shrink, hover, stutter"],
        ["Efectos CDP nuevos (prio media)", "15", "filter bank/sweep/vari, distort×4, grain×3, wrappage, cascade, motor, cantor, brownian"],
        ["Total estimado v0.2", "~45-50", "18 actuales (evolucionados) + ~28 CDP nuevos"],
    ]
    e.append(make_table(["Concepto", "#", "Detalle"], count_rows, st,
                        col_widths=[W*0.28, W*0.07, W*0.65]))

    e.append(Spacer(1, 6*mm))
    e.append(Paragraph("6.1 Arquitectura de backends", st['SubH']))

    arch_rows = [
        ["Pedalboard (Spotify)", "Efectos DSP nativos de baja latencia", "reverb, delay, compressor, gain, limiter, chorus, phaser, bitcrush"],
        ["librosa STFT", "Procesamiento spectral directo (Python)", "spectral_freeze, spectral_smear, spectral_gate, spectral_shift"],
        ["CDP (subprocess)", "Ejecutables CLI de CDP Release 8", "Todos los efectos CDP nuevos — se invocan como subprocesos con archivos WAV temporales"],
        ["Granular (Python)", "Motor granular propio", "granular (expandido con sub-modos inspirados en CDP grain)"],
    ]
    e.append(make_table(["Backend", "Método", "Efectos"], arch_rows, st,
                        col_widths=[W*0.18, W*0.35, W*0.47]))

    e.append(Spacer(1, 6*mm))
    e.append(Paragraph("6.2 Pipeline CDP: cómo se integran", st['SubH']))
    e.append(Paragraph(
        "Los efectos CDP se ejecutan como subprocesos externos. El flujo es:", st['Body']
    ))
    pipeline_steps = [
        "1. Exportar el segmento de audio a un archivo WAV temporal (16-bit o 32-bit float)",
        "2. Ejecutar el programa CDP con los parámetros correspondientes",
        "3. Leer el archivo WAV de salida de vuelta a un numpy array",
        "4. Continuar el pipeline de efectos con el resultado",
    ]
    for step in pipeline_steps:
        e.append(Paragraph(step, st['Body']))

    e.append(Spacer(1, 3*mm))
    e.append(Paragraph(
        "Para efectos SPECTRAL de CDP, se añaden 2 pasos extra: specanal antes del proceso y pvoc después. "
        "Esto aumenta el tiempo de proceso pero ofrece resultados imposibles con DSP convencional.",
        st['SmallNote']
    ))

    # ═══════════════════════════════════════════════════
    # 7. PREGUNTAS PARA DECIDIR
    # ═══════════════════════════════════════════════════
    e.append(Spacer(1, 8*mm))
    e.append(Paragraph("7. Preguntas Abiertas para tu Decisión", st['SectionH']))
    e.append(Spacer(1, 3*mm))

    questions = [
        ("Prioridad de CDP spectrales",
         "¿Implementamos el pipeline specanal→pvoc ya en v0.2 o lo dejamos para v0.3? "
         "Es la pieza de infraestructura más grande."),
        ("UI del panel de efectos",
         "¿Mantenemos un panel plano con scroll o pasamos a pestañas por grupo (A-H)? "
         "¿O un grid visual con iconos por grupo?"),
        ("Efectos por evento vs. por track",
         "Actualmente los efectos se asignan aleatoriamente a cada AudioEvent. "
         "¿En v0.2 queremos también efectos a nivel de track/bus?"),
        ("Presets de combinaciones",
         "¿Quieres presets de cadenas de efectos predefinidas? Ej: 'Lo-fi' = bitcrush + LP filter + tape delay."),
        ("Cantidad de CDP nuevos en v0.2",
         "¿Integramos los 13 de prioridad alta? ¿También los 15 de prioridad media? "
         "¿O empezamos con un subset más conservador?"),
        ("Síntesis CDP (brownian, chirikov, crystal, motor, synspline)",
         "¿Los incluimos como efectos o como nuevos 'generadores' de audio (fuentes sin input)?"),
    ]

    for q_title, q_body in questions:
        block = []
        block.append(Paragraph(f"☐  {q_title}", st['BodyBold']))
        block.append(Paragraph(q_body, st['Body']))
        block.append(Spacer(1, 2*mm))
        e.append(KeepTogether(block))

    return e


def header_footer(canvas, doc):
    canvas.saveState()
    # Header bar
    canvas.setFillColor(SLATE)
    canvas.rect(0, A4[1] - 11*mm, A4[0], 11*mm, fill=1, stroke=0)
    # Amber accent line
    canvas.setFillColor(AMBER)
    canvas.rect(0, A4[1] - 11.8*mm, A4[0], 0.8*mm, fill=1, stroke=0)
    # Header text
    canvas.setFillColor(white)
    canvas.setFont('Helvetica-Bold', 7.5)
    canvas.drawString(15*mm, A4[1] - 7.5*mm, "Aleatoric Composer — Integración de Efectos v0.1 → v0.2")
    canvas.setFillColor(AMBER)
    canvas.drawRightString(A4[0] - 15*mm, A4[1] - 7.5*mm, f"Pág. {doc.page}")
    # Footer
    canvas.setFillColor(TEXT_MUTED)
    canvas.setFont('Helvetica', 6.5)
    canvas.drawCentredString(A4[0] / 2, 7*mm, "Documento de trabajo interno — .design/")
    canvas.restoreState()


def first_page(canvas, doc):
    """Cover page: dark background + standard header."""
    canvas.saveState()
    # Dark cover background
    canvas.setFillColor(SLATE_120)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    # Amber circle decoration
    canvas.setFillColor(AMBER)
    canvas.setFillAlpha(0.08)
    canvas.circle(A4[0] - 40*mm, A4[1] - 60*mm, 120*mm, fill=1, stroke=0)
    canvas.setFillAlpha(0.06)
    canvas.setFillColor(TEAL)
    canvas.circle(60*mm, 80*mm, 80*mm, fill=1, stroke=0)
    canvas.restoreState()
    # Standard header
    header_footer(canvas, doc)


def main():
    st = styles()
    doc = SimpleDocTemplate(
        str(OUT_PATH), pagesize=A4,
        topMargin=17*mm, bottomMargin=14*mm,
        leftMargin=15*mm, rightMargin=15*mm,
        title="Integración de Efectos — Aleatoric Composer v0.2",
        author="Aleatoric Composer Team",
    )
    elements = build(st)
    doc.build(elements, onFirstPage=first_page, onLaterPages=header_footer)
    print(f"PDF generado: {OUT_PATH}")
    print(f"  Tamaño: {OUT_PATH.stat().st_size / 1024:.0f} KB")


if __name__ == '__main__':
    main()
