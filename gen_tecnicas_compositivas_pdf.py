#!/usr/bin/env python3
"""
Genera PDF: Técnicas Compositivas — Aleatoric Composer v0.2
11 técnicas (Xenakis→Ferneyhough) como PRESETS abiertos.
Paleta de diseño: Amber/Slate/Teal/Sand.
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
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
SAND = HexColor("#A69C95")
SAND_10 = HexColor("#F6F4F2")
SAND_20 = HexColor("#E5E1DE")
SAND_40 = HexColor("#C7BFB9")
SAND_120 = HexColor("#857870")
SAND_140 = HexColor("#5E534C")
TEXT = HexColor("#1A1F22")
TEXT_MUTED = HexColor("#6B7780")

# Per-composer colors
C_XEN = HexColor("#C0392B")
C_FEL = HexColor("#2E7D32")
C_LIG = HexColor("#6A1B9A")
C_CAG = HexColor("#1565C0")
C_SCE = HexColor("#E65100")
C_REI = HexColor("#00838F")
C_OLI = HexColor("#4E342E")
C_LAC = HexColor("#880E4F")
C_SAA = HexColor("#1B5E20")
C_NAN = HexColor("#E53935")
C_FER = HexColor("#311B92")

OUT = Path(__file__).parent / "Tecnicas_Compositivas_v02.pdf"
W = 170 * mm


def styles():
    s = getSampleStyleSheet()
    def a(name, **kw):
        if name in [st.name for st in s.byName.values()]:
            return
        s.add(ParagraphStyle(name, **kw))
    a('DocTitle', fontSize=28, leading=34, textColor=white, spaceAfter=4*mm,
      alignment=TA_CENTER, fontName='Helvetica-Bold')
    a('DocSub', fontSize=12, leading=16, textColor=SAND_40, spaceAfter=6*mm,
      alignment=TA_CENTER, fontName='Helvetica')
    a('S1', fontSize=16, leading=20, textColor=white, spaceBefore=6*mm, spaceAfter=4*mm,
      fontName='Helvetica-Bold', backColor=SLATE, borderPadding=(3*mm, 4*mm, 3*mm, 4*mm))
    a('S2', fontSize=13, leading=17, textColor=TEAL, spaceBefore=5*mm, spaceAfter=2*mm,
      fontName='Helvetica-Bold')
    a('S3', fontSize=11, leading=15, textColor=AMBER_140, spaceBefore=4*mm, spaceAfter=2*mm,
      fontName='Helvetica-Bold')
    a('B', fontSize=9.5, leading=14, textColor=TEXT, spaceAfter=2*mm, fontName='Helvetica',
      alignment=TA_JUSTIFY)
    a('BB', fontSize=9.5, leading=14, textColor=TEXT, spaceAfter=2*mm, fontName='Helvetica-Bold')
    a('Note', fontSize=8.5, leading=12, textColor=TEXT_MUTED, spaceAfter=2*mm,
      fontName='Helvetica-Oblique', leftIndent=6*mm)
    a('Bul', fontSize=9.5, leading=14, textColor=TEXT, leftIndent=10*mm, bulletIndent=4*mm,
      spaceAfter=1.5*mm, fontName='Helvetica')
    a('TC', fontSize=8.5, leading=11, textColor=TEXT, fontName='Helvetica')
    a('TH', fontSize=8.5, leading=11, textColor=white, fontName='Helvetica-Bold')
    a('Callout', fontSize=10, leading=14, textColor=SLATE, spaceBefore=3*mm, spaceAfter=3*mm,
      fontName='Helvetica-Bold', backColor=AMBER_10, borderPadding=(2.5*mm, 3*mm, 2.5*mm, 3*mm))
    a('Callout2', fontSize=10, leading=14, textColor=TEAL, spaceBefore=3*mm, spaceAfter=3*mm,
      fontName='Helvetica-Bold', backColor=TEAL_10, borderPadding=(2.5*mm, 3*mm, 2.5*mm, 3*mm))
    a('Pipe', fontSize=9, leading=13, textColor=SLATE, alignment=TA_CENTER,
      fontName='Helvetica-Bold', spaceBefore=2*mm, spaceAfter=2*mm)
    a('CompName', fontSize=11, leading=15, textColor=TEXT, spaceBefore=4*mm, spaceAfter=1*mm,
      fontName='Helvetica-Bold')
    return s


def tbl(headers, rows, st, cw=None):
    nc = len(headers)
    if not cw: cw = [W/nc]*nc
    data = [[Paragraph(h, st['TH']) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), st['TC']) for c in row])
    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SLATE),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2*mm),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2*mm),
        ('LEFTPADDING', (0,0), (-1,-1), 2*mm),
        ('RIGHTPADDING', (0,0), (-1,-1), 2*mm),
        ('GRID', (0,0), (-1,-1), 0.4, SAND_20),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, SAND_10]),
    ]))
    return t


def ct(name, color):
    return f'<font color="{color.hexval()}"><b>{name}</b></font>'


# ═══════════════════════════════════════════════════════════════
# COMPOSER TECHNIQUE CARDS — each returns list of flowables
# ═══════════════════════════════════════════════════════════════

def _card(st, name, color, subtitle, concept, params, strategies, structure, effects, note=""):
    """Generic technique card builder."""
    els = []
    els.append(Paragraph(f"{ct(name, color)} — {subtitle}", st['CompName']))
    els.append(HRFlowable(width="100%", thickness=1, color=color, spaceAfter=2*mm))
    els.append(Paragraph(concept, st['B']))
    els.append(tbl(
        ["Parámetro", "Preset por defecto (override libre)"],
        params, st, cw=[W*0.18, W*0.82]
    ))
    els.append(Paragraph(f"<b>Strategies compatibles:</b> {strategies}", st['Note']))
    els.append(Paragraph(f"<b>Structure derivada:</b> {structure}", st['Note']))
    els.append(Paragraph(f"<b>Efectos favorecidos:</b> {effects}", st['Note']))
    if note:
        els.append(Paragraph(note, st['Note']))
    els.append(Spacer(1, 2*mm))
    return els


def build(st):
    e = []

    # ═══════════════════════════════════════════════════
    # PORTADA
    # ═══════════════════════════════════════════════════
    e.append(Spacer(1, 25*mm))
    e.append(Paragraph("Técnicas Compositivas", st['DocTitle']))
    e.append(Paragraph("como Motor Principal de Aleatoric Composer v0.2", st['DocSub']))
    e.append(Spacer(1, 4*mm))
    e.append(HRFlowable(width="50%", thickness=2, color=AMBER, spaceAfter=4*mm))
    e.append(Paragraph(
        "Xenakis · Feldman · Ligeti · Cage · Scelsi · Reich · Oliveros · Lachenmann · Saariaho · Nancarrow · Ferneyhough",
        st['DocSub']
    ))
    e.append(Spacer(1, 8*mm))
    e.append(Paragraph(
        "Las técnicas compositivas funcionan como <b>PRESETS inteligentes</b> que configuran todo el pipeline: "
        "distribuciones, structure, efectos, rangos. Pero el usuario tiene <b>libertad total</b> para modificar "
        "cualquier parámetro después de seleccionar la técnica. El preset es un punto de partida estético, "
        "no una cárcel. Esto es un Aleatoric Composer: la indeterminación y la libertad creativa son el objetivo.",
        st['B']
    ))
    e.append(Paragraph(
        "Cada técnica preselecciona intervalos y probabilidades. El usuario puede aceptar los defaults, "
        "modificar capas individuales, o mezclar técnicas. No hay combinaciones prohibidas.",
        st['Callout']
    ))

    # ═══════════════════════════════════════════════════
    # 1. FILOSOFÍA: PRESETS ABIERTOS
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("1. Filosofía: Presets Abiertos, No Encasillados", st['S1']))
    e.append(Spacer(1, 3*mm))

    e.append(Paragraph(
        "En v0.1 no hay concepto de técnica compositiva. La Strategy (scatter/structured/layer/canon) "
        "y los Constraints (density_curve, amplitude, pan...) son independientes. Esto da libertad pero "
        "falta guía estética. En v0.2 añadimos una capa superior — la técnica — que actúa como preset:", st['B']
    ))

    e.append(Paragraph("1.1 Qué es una técnica compositiva en esta app", st['S2']))
    e.append(Paragraph(
        "Un <b>perfil de configuración predefinido</b> que ajusta todos los parámetros del pipeline "
        "a valores estéticamente coherentes con el estilo de un compositor o escuela. "
        "Es un botón que dice 'dame algo que suene a Xenakis' o 'dame algo Feldmaniano'. "
        "Pero después de pulsar ese botón, <b>todo sigue siendo editable</b>.", st['B']
    ))

    e.append(Paragraph("1.2 Qué configura el preset", st['S2']))
    preset_rows = [
        ["Strategy recomendada", "Sugiere una strategy pero NO la fuerza. El usuario puede elegir cualquiera.",
         "Selector con estrella en la recomendada"],
        ["Structure / density_curve", "Define la forma global (plana, arco, nubes...). Override libre.",
         "Editor visual de curva + presets"],
        ["Distribuciones por parámetro", "Para timing, amplitude, pan, duración, etc. Cada parámetro tiene "
         "su distribución + params (mean, std, lambda, k...).",
         "Dropdown por parámetro + sliders"],
        ["Rangos [min, max]", "Preselecciona rangos coherentes. Ej: Feldman amp_max=0.4.",
         "RangeSlider (ya existe en v0.1)"],
        ["Moduladores (walk, Markov, sieve)", "Activa/desactiva walks, cadenas de Markov, cribas por parámetro.",
         "Toggle + configuración por parámetro"],
        ["Efectos favorecidos", "Lista de efectos y probabilidades. NO excluye ninguno — solo pondera.",
         "Pesos editables por efecto"],
        ["Distribución de params de efecto", "Cómo se generan los params de cada efecto (distribución + walk).",
         "Panel avanzado por efecto"],
    ]
    e.append(tbl(["Capa", "Qué configura el preset", "UI del override"],
                 preset_rows, st, cw=[W*0.20, W*0.48, W*0.32]))

    e.append(Paragraph("1.3 Lo que el preset NO hace", st['S2']))
    no_list = [
        "NO bloquea ningún parámetro — todo es editable después de seleccionar la técnica",
        "NO excluye efectos — solo cambia probabilidades/pesos",
        "NO obliga a una strategy — solo la recomienda (marcada con estrella)",
        "NO limita el número de tracks, la duración, ni las sources",
        "NO impide mezclar: puedes empezar con Xenakis y luego mover sliders hacia Feldman",
        "NO es destructivo: cambiar de técnica re-aplica defaults pero el usuario puede deshacer",
    ]
    for item in no_list:
        e.append(Paragraph(f"<bullet>&bull;</bullet>{item}", st['Bul']))

    e.append(Spacer(1, 4*mm))
    e.append(Paragraph(
        "Principio rector: la técnica es un PUNTO DE PARTIDA, no un DESTINO. "
        "El usuario siempre tiene la última palabra. Aleatoric Composer es una herramienta de "
        "exploración creativa, no un simulador de compositores.",
        st['Callout2']
    ))

    # ═══════════════════════════════════════════════════
    # 2. PIPELINE v0.2
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("2. Pipeline v0.2", st['S1']))
    e.append(Spacer(1, 3*mm))

    e.append(Paragraph("v0.1 — Plano:", st['S3']))
    e.append(Paragraph(
        "SOURCES → STRATEGY → CONSTRAINTS (density_curve independiente) → RNG (uniform/gaussian) → "
        "EFFECTS (params vacíos) → COMPOSITION", st['Pipe']))

    e.append(Paragraph("v0.2 — Técnica como preset abierto:", st['S3']))
    e.append(Paragraph(
        "SOURCES → TÉCNICA (preset) → STRATEGY (recomendada, override libre) → "
        "STRUCTURE (derivada, override libre) → RNG (distribución del preset, override libre) → "
        "EFFECTS (params vivos del preset, override libre) → COMPOSITION", st['Pipe']))

    e.append(Spacer(1, 3*mm))
    e.append(Paragraph("2.1 Sistema de capas con override", st['S2']))

    layers = [
        ["Capa 0: Sources", "El usuario carga archivos de audio", "Sin cambios. No depende de la técnica"],
        ["Capa 1: Técnica (preset)", "Configura defaults inteligentes para TODO", "Primera elección del usuario. Un click."],
        ["Capa 2: Strategy", "Algoritmo de colocación de eventos", "Recomendada por la técnica. Override libre."],
        ["Capa 3: Structure", "Forma global (densidad, secciones)", "Derivada de la técnica. Editor visual libre."],
        ["Capa 4: Distribuciones", "Distribución por parámetro + moduladores", "Dropdown por param. Override libre."],
        ["Capa 5: Rangos", "Min/max de cada parámetro", "RangeSliders. Override libre."],
        ["Capa 6: Efectos", "Pesos, params, evolución", "Panel de efectos. Override libre."],
        ["Capa 7: Seed", "Semilla RNG", "Sin cambios. Determinismo reproducible."],
    ]
    e.append(tbl(["Capa", "Función", "Override"], layers, st, cw=[W*0.20, W*0.40, W*0.40]))

    e.append(Paragraph(
        "Cada capa inferior puede override la superior. Si el usuario no toca nada, "
        "el preset genera un resultado coherente. Si modifica capas, personaliza el resultado. "
        "Si cambia TODOS los parámetros, la técnica original ya no se nota — y eso está bien.",
        st['Note']
    ))

    # pipeline for single param
    e.append(Paragraph("2.2 Pipeline de generación de un parámetro individual", st['S2']))
    pipe_steps = [
        ["1. Técnica → ParameterProfile", "Define distribución, rango, modulador por defecto"],
        ["2. Override del usuario", "Si el usuario modificó algo, se usa su valor"],
        ["3. RNG genera valor crudo", "Usa la distribución seleccionada (Cauchy, Gaussian, Uniform, Weibull...)"],
        ["4. Sieve filtra (opcional)", "Si hay criba activa, cuantiza al valor permitido más cercano"],
        ["5. Walk modula (opcional)", "Si hay walk, el valor anterior influye en el nuevo (step + drift)"],
        ["6. Clamp a [min, max]", "Resultado recortado al rango"],
        ["7. Resultado → AudioEvent", "Se asigna al parámetro del evento"],
    ]
    e.append(tbl(["Paso", "Descripción"], pipe_steps, st, cw=[W*0.28, W*0.72]))

    # ═══════════════════════════════════════════════════
    # 3. CATÁLOGO COMPLETO DE TÉCNICAS (11)
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("3. Catálogo Completo: 11 Técnicas Compositivas", st['S1']))
    e.append(Spacer(1, 3*mm))
    e.append(Paragraph(
        "Cada ficha define los <b>defaults del preset</b>. Todos los valores son overridables. "
        "La columna 'Preset por defecto' muestra lo que se configura automáticamente al seleccionar la técnica.",
        st['B']
    ))

    # ─── 3.1 XENAKIS ───
    e += _card(st, "IANNIS XENAKIS", C_XEN, "Música Estocástica",
        "La composición como proceso probabilístico gobernado por leyes estadísticas. "
        "Las decisiones individuales se derivan de distribuciones de probabilidad. El compositor "
        "no decide cada evento sino las <i>leyes</i> que los generan. Nubes de sonido donde la "
        "estadística global importa más que cada punto individual.",
        [
            ["timeline_start", "Exponencial(lambda=2.0) → ráfagas agrupadas con silencios variables. "
             "Sieve opcional para cuantizar a grid rítmico. Rango: 0.01-15s"],
            ["event_duration", "Weibull(k=0.8) → predominan eventos cortos con cola de largos. "
             "Sieve opcional para duraciones discretas (0.5, 1.0, 2.0...). Rango: 0.1-20s"],
            ["amplitude", "Cauchy(loc=0.5, scale=0.2) → extremos frecuentes (pp y ff). "
             "Walk(step=0.1) para evolución gradual. Rango: 0.1-1.0"],
            ["pan", "Random walk(step=0.15, frontera=reflectante) desde centro. "
             "Sieve opcional para posiciones discretas (ej: 5 puntos stereo)"],
            ["density", "Función arbitraria (nube de probabilidad). Default: arc con variación aleatoria. "
             "Secciones por Markov: sparse↔medium↔dense↔climax↔silence"],
            ["effects", "Markov para secuencia de efectos. Parámetros por Cauchy (extremos) o "
             "Exponencial (sesgados). Walk para evolución entre eventos. Todos los efectos permitidos"],
            ["source selection", "Markov: 'después de piano, 70% cello'. Matriz de transición editable"],
        ],
        "scatter (máxima libertad estocástica), structured (Markov por secciones)",
        "Nubes de probabilidad — density cloud como función dibujable + secciones Markov",
        "TODOS — la estocástica abarca todo. Favorece: distort, granular, CDP bounce/cascade/scramble"
    )

    # ─── 3.2 FELDMAN ───
    e.append(PageBreak())
    e += _card(st, "MORTON FELDMAN", C_FEL, "Clusters Estáticos y Duración Extendida",
        "Sonidos sostenidos, dinámicas extremadamente suaves, cambios casi imperceptibles. "
        "Los <i>clusters</i> son grupos de eventos con timing casi idéntico que crean una textura "
        "densa pero quieta. La forma es plana — sin clímax dramáticos. El silencio es estructural. "
        "Obras como 'For Philip Guston' o 'String Quartet II' duran horas.",
        [
            ["timeline_start", "Clusters: N eventos con gaussian muy estrecha (std=0.05-0.2s). "
             "Entre clusters: exponencial(lambda=0.15) → silencios largos (5-30s)"],
            ["event_duration", "Larga: gaussian(mean=25, std=5). Rango: 10-60s. "
             "Variación mínima dentro del cluster. Todos los eventos del cluster ≈ igual duración"],
            ["amplitude", "Muy baja: gaussian(mean=0.25, std=0.04). Rango: 0.10-0.40. "
             "Walk(step=0.02) para fluctuaciones sutiles. Nunca supera mf"],
            ["pan", "Casi estático: walk(step=0.02, frontera=reflectante). "
             "Los clusters comparten posición ± 0.05"],
            ["density", "Baja constante (0.15) con ondulaciones lentas (sin(t)*0.05). "
             "Sin climax. Picos locales suaves = clusters"],
            ["effects", "Reverb largo (room=0.8, wet=0.6), gain bajo. SIN distorsión. "
             "Parámetros casi fijos: variación &lt;5%. Walk(step=0.005)"],
            ["source selection", "Repetición deliberada: Markov con P(mismo)=0.85. Cambios lentos"],
        ],
        "layer (texturas sostenidas), structured (secciones lentas con mucho silencio)",
        "Plana con ondulaciones mínimas. Sin secciones marcadas. Silencio como material",
        "reverb largo, envel dovetail, gain bajo, modify space. CDP: envel warp (flatten, ducked)",
        "Cluster_size (eventos por cluster): default 3-5, editable. Cluster_spread (dispersión temporal): default 0.1s"
    )

    # ─── 3.3 LIGETI ───
    e += _card(st, "GYÖRGY LIGETI", C_LIG, "Micropolifonía y Texturas de Masas",
        "Masas de sonido donde las voces individuales se funden en texturas. Altísima densidad "
        "de eventos con movimiento cromático lento. Los clusters micropolifónicos son nubes "
        "densísimas de eventos superpuestos que crean una masa en movimiento. Las transformaciones "
        "entre masas son graduales (sigmoid/ease). Obras: Atmosphères, Lontano, Lux Aeterna.",
        [
            ["timeline_start", "Extremadamente denso: eventos cada 0.01-0.15s. "
             "Quasi-random (Van der Corput) para distribución uniforme anti-clustering"],
            ["event_duration", "Corta a media: gaussian(mean=2, std=1). Rango: 0.3-6s. "
             "Solapamiento masivo crea continuidad a pesar de eventos cortos"],
            ["amplitude", "Homogénea: gaussian(mean=0.45, std=0.07). Rango: 0.20-0.65. "
             "Dinámica global lenta (crescendo/decresc de la masa), no individual"],
            ["pan", "Amplia: uniform(-1, +1). Toda la imagen stereo simultáneamente. "
             "Cada evento independiente → textura espacialmente ancha"],
            ["density", "Muy alta sostenida (0.9+). Bloques texturales con transiciones sigmoid. "
             "Forma = transformación masa_1 → transición(5-15s) → masa_2"],
            ["effects", "spectral_smear, blur, chorus, phaser, granular denso. Walk lento en todos "
             "los params. Efectos difuminan voces individuales en masa"],
            ["source selection", "Uniform: todos los sources simultáneamente. La mezcla de timbres ES la textura"],
            ["num_tracks", "Alto: 6-12. Cada track = una voz de la micropolifonía"],
        ],
        "scatter (densidad máxima), layer (masas continuas)",
        "Bloques texturales densos con transiciones graduales. Sin vacíos. Sin secciones discretas",
        "spectral_smear, spectral_gate, chorus, phaser, granular. CDP: blur, hover, wrappage"
    )

    # ─── 3.4 CAGE ───
    e.append(PageBreak())
    e += _card(st, "JOHN CAGE", C_CAG, "Indeterminación y Azar Puro",
        "Cada decisión es completamente aleatoria sin sesgo estadístico ni memoria. "
        "Distribución uniforme para todo. No hay preferencias, no hay Markov, no hay walks. "
        "El resultado es impredecible y cada render es radicalmente diferente. "
        "Los silencios tienen el mismo peso que los sonidos. Obras: Music of Changes, Williams Mix.",
        [
            ["timeline_start", "Uniform puro (0, max_silence). Sin clustering, sin tendencias, sin grid. "
             "El silencio puede ser 0s o 30s con igual probabilidad"],
            ["event_duration", "Uniform(min_event, max_event). Sin sesgo gaussiano. "
             "Eventos de 0.5s y 30s son igualmente probables"],
            ["amplitude", "Uniform(0.0, 1.0). Incluye silencio (amp→0). Sin suavizado, sin walk. "
             "Cada evento es completamente independiente del anterior"],
            ["pan", "Uniform(-1, +1). Sin memoria de posición anterior"],
            ["density", "Constante=1.0. Sin curva. Sin forma. La distribución uniform de gaps "
             "genera su propia forma impredecible"],
            ["effects", "Uniform: cada efecto = misma probabilidad. Params = uniform en todo rango. "
             "Sin correlación entre eventos. Sin walk, sin Markov"],
            ["source selection", "Uniform sin pesos. Cada source = misma probabilidad. Sin historia"],
        ],
        "scatter (único que respeta indeterminación total)",
        "NINGUNA. La ausencia de estructura ES la estructura. density=constant(1.0)",
        "TODOS con igual probabilidad. Params en todo el rango. CDP: cualquiera, sin preferencia",
        "Este preset REPRODUCE el comportamiento de v0.1 (Scatter con defaults). Es el 'modo libre'."
    )

    # ─── 3.5 SCELSI ───
    e += _card(st, "GIACINTO SCELSI", C_SCE, "Profundidad de un Solo Sonido",
        "Un solo sonido explorado en profundidad extrema. Eventos muy largos basados en una sola fuente. "
        "La variación viene de cambios tímbricos microscópicos: micro-fluctuaciones de pitch, "
        "evolución lenta de efectos espectrales, exploración del interior del sonido. "
        "Pocos eventos, mucha profundidad. Obras: Quattro Pezzi, Anahit, Konx-Om-Pax.",
        [
            ["timeline_start", "Muy pocos eventos (1-5 en toda la composición). "
             "Prácticamente continuo. Crossfades largos de 3-5s entre capas"],
            ["event_duration", "Máxima: gaussian(mean=dur*0.8, std=5). Rango: 30s a total_duration. "
             "Un evento puede abarcar casi toda la composición"],
            ["amplitude", "Estable: gaussian(mean=0.5, std=0.03). Walk(step=0.01) → "
             "micro-respiración. Sin dinámica dramática"],
            ["pan", "Walk muy lento (step=0.01). El sonido 'respira' espacialmente. "
             "Movimiento casi imperceptible"],
            ["density", "Mínima: 1-2 eventos simultáneos. La textura viene de la profundidad "
             "del procesamiento, no de la cantidad"],
            ["effects", "CDP spectral como protagonistas: freeze, shift, smear. Granulación fina. "
             "time_stretch largo. Walk continuo (step=0.005). Los efectos SON la composición"],
            ["source selection", "1 source preferido: Markov P(mismo)=0.95. "
             "Si hay más sources, solo toques sutiles del secundario"],
        ],
        "layer (obligatorio — una sola textura continua que evoluciona)",
        "Arco larguísimo: attack(30%), sustain(40%), release(30%). Un solo gesto",
        "spectral_freeze, spectral_shift, spectral_smear, time_stretch, granular fino. CDP: hover, hover2"
    )

    # ─── 3.6 REICH ───
    e.append(PageBreak())
    e += _card(st, "STEVE REICH", C_REI, "Phasing y Procesos Graduales",
        "Repetición y proceso gradual. La misma fuente suena en múltiples tracks con desfase que "
        "evoluciona lentamente (phasing). Los patrones son cortos y repetidos; el interés viene de "
        "las relaciones que emergen cuando las copias se desfasan. Procesos audibles y predecibles. "
        "Obras: It's Gonna Rain, Come Out, Piano Phase, Music for 18 Musicians.",
        [
            ["timeline_start", "Repetición regular: cada evento inicia cada <i>loop_period</i> (0.5-4s). "
             "Walk(step=0.002-0.01) añade el phasing gradual entre tracks"],
            ["event_duration", "Igual al loop_period o muy cercano. gaussian(mean=loop_period, std=0.05). "
             "Todos los eventos del mismo track son casi idénticos en duración"],
            ["amplitude", "Constante por track: 0.5-0.7. Sin variación dinámica. "
             "Walk(step=0.005) para micro-variación. Rango estrecho: 0.45-0.75"],
            ["pan", "Fijo por track: distribuidos equidistantemente en el espacio stereo. "
             "Track 1=-0.7, Track 2=0.0, Track 3=+0.7 (con N tracks)"],
            ["density", "Alta y constante. Sin variación. La densidad es la del loop ×N tracks"],
            ["effects", "Mínimos: delay corto para reinforcement, slight reverb. "
             "Parámetros fijos. Sin walk. CDP: repeater, shifter"],
            ["source selection", "1 source en todos los tracks (obligatorio para phasing). "
             "source_start evoluciona con walk para crear el desfase"],
            ["phase_drift", "NUEVO param: walk(step=0.001-0.01) aplicado a timeline_start de cada track. "
             "Esto ES el phasing. Valor pequeño = proceso lento. Editable."],
        ],
        "canon (copias desfasadas — perfecto para phasing)",
        "Constante total. Sin secciones. El proceso IS the piece. Forma = evolución gradual del desfase",
        "Mínimos: delay, slight reverb. CDP: repeater para loops. Sin distorsión ni granulación"
    )

    # ─── 3.7 OLIVEROS ───
    e += _card(st, "PAULINE OLIVEROS", C_OLI, "Deep Listening y Atención Expandida",
        "Escucha profunda: atención plena al sonido y su entorno. Densidad mínima, duraciones "
        "extremas, respuesta al material sonoro. Cada sonido tiene espacio para resonar. "
        "La composición es un acto de escucha más que de escritura. "
        "Obras: Sonic Meditations, Deep Listening, The Well and the Gentle.",
        [
            ["timeline_start", "Eventos espaciados: exponencial(lambda=0.08) → gaps de 5-60s. "
             "Cada sonido tiene tiempo para 'habitar' el espacio antes del siguiente"],
            ["event_duration", "Larga a muy larga: gaussian(mean=20, std=8). Rango: 5-90s. "
             "Los sonidos se despliegan lentamente"],
            ["amplitude", "Suave: gaussian(mean=0.30, std=0.08). Rango: 0.10-0.50. "
             "Walk(step=0.015) para respiración natural"],
            ["pan", "Walk lento (step=0.03) explorando todo el espacio. "
             "A diferencia de Scelsi, aquí el movimiento espacial es parte del deep listening"],
            ["density", "Muy baja con momentos de actividad suave. Sin climax. "
             "Forma orgánica: respiración lenta in-out"],
            ["effects", "Reverb largo (sala grande), delay largo y sutil. Sin procesamiento agresivo. "
             "Walk lento. CDP: envel warp (expand, ducked), modify space"],
            ["source selection", "Múltiples sources (a diferencia de Scelsi). Markov con cambios lentos. "
             "Cada source se 'escucha' por completo antes de cambiar"],
        ],
        "layer (texturas largas), structured (con secciones muy abiertas)",
        "Respiración orgánica: ondulaciones lentas sin forma predeterminada",
        "reverb largo, delay largo, envel warp. CDP: modify space, envel dovetail. Sin distorsión"
    )

    # ─── 3.8 LACHENMANN ───
    e.append(PageBreak())
    e += _card(st, "HELMUT LACHENMANN", C_LAC, "Musique Concrète Instrumentale",
        "Focus en el ruido, la textura y los modos de producción del sonido. Los instrumentos "
        "se tocan de maneras no convencionales para extraer ruidos, chirridos, respiraciones. "
        "El resultado es una exploración del continuo sonido↔ruido. Texturas ásperas, "
        "fragmentadas, con silencios dramáticos. Obras: Pression, Air, Gran Torso.",
        [
            ["timeline_start", "Irregular: Cauchy(loc=0, scale=0.5) → clusters abruptos y silencios. "
             "Ráfagas seguidas de vacíos dramáticos"],
            ["event_duration", "Variable extremo: Weibull(k=0.5) → muchos muy cortos (0.05-0.3s) "
             "con alguno largo ocasional (5-15s). Contraste radical"],
            ["amplitude", "Cauchy(loc=0.6, scale=0.3) → extremos (ppp o fff). "
             "Sin zona media. Sin walk. Cada evento es un gesto independiente"],
            ["pan", "Abrupto: sin walk. Uniform(-1, +1) con cambios discretos. "
             "El espacio es otro parámetro de gesto, no un continuo"],
            ["density", "Muy variable: bloques densos alternados con silencios absolutos. "
             "Markov: dense(0.4)↔silence(0.4)↔sparse(0.2). Sin transiciones suaves"],
            ["effects", "Distorsión, bitcrush, granulación agresiva, filtros extremos. "
             "CDP: distort (fractal, reform), clip, quirk, scramble, constrict. "
             "Params en extremos: distribución Cauchy"],
            ["source selection", "Cambios abruptos. Markov con baja auto-transición (P=0.3). "
             "El contraste tímbrico es dramático"],
        ],
        "scatter (fragmentación), structured (bloques con silencios dramáticos)",
        "Bloques fragmentados: dense/silence alternados sin transición. Markov abrupto",
        "distort (todos), bitcrush, clip, quirk, scramble, granular agresivo, filter extreme. "
        "CDP: constrict, bounce, splinter"
    )

    # ─── 3.9 SAARIAHO ───
    e += _card(st, "KAIJA SAARIAHO", C_SAA, "Espectralismo y Transiciones Timbre-Ruido",
        "Transiciones continuas entre sonido puro y ruido, entre textura y melodía. "
        "El timbre es el parámetro principal de composición. Crossfades larguísimos entre "
        "estados sonoros. Uso intensivo de procesamiento spectral. "
        "Obras: Nymphéa, Lichtbogen, L'Amour de Loin, Graal Théâtre.",
        [
            ["timeline_start", "Fluido: gaussian(mean=1.5, std=0.8) entre eventos. "
             "Solapamiento frecuente. Crossfades de 2-5s entre capas"],
            ["event_duration", "Media a larga: gaussian(mean=12, std=5). Rango: 3-40s. "
             "Suficiente para que las transiciones timbrales se desplieguen"],
            ["amplitude", "Gradual: walk(step=0.04) con gaussian(mean=0.5, std=0.1). "
             "Crescendo/decrescendo largos. Rango: 0.15-0.85"],
            ["pan", "Walk lento (step=0.04). Movimiento espacial como parte de la transformación tímbrica"],
            ["density", "Media, fluida. Transiciones largas entre estados. "
             "Curva smooth (spline) sin discontinuidades. Forma: arco con ondulaciones"],
            ["effects", "SPECTRAL como protagonistas: freeze, smear, shift, gate. "
             "Walk continuo en todos los params → transición timbre↔ruido. "
             "CDP blur, morph (cuando disponible). Granulación suave"],
            ["source selection", "Walk entre sources: crossfade tímbrico gradual. "
             "Markov con P transición=0.3 (cambios lentos pero más frecuentes que Scelsi)"],
        ],
        "layer (transiciones continuas), structured (secciones fluidas)",
        "Spline continuo. Forma orgánica sin secciones marcadas. Arco con ondulaciones internas",
        "spectral_freeze, smear, shift, gate, granular suave, time_stretch. CDP: blur, hover. "
        "Los efectos son el medio principal de transformación tímbrica"
    )

    # ─── 3.10 NANCARROW ───
    e.append(PageBreak())
    e += _card(st, "CONLON NANCARROW", C_NAN, "Tempo Canons y Velocidades Simultáneas",
        "Música para piano mecánico: velocidades imposibles para humanos. Múltiples tempos "
        "simultáneos en diferentes tracks. La misma fuente suena a velocidades diferentes, "
        "creando relaciones rítmicas complejas (ratios irracionales como √2:1). "
        "Accelerandos y decelerandos superpuestos. Obras: Studies for Player Piano.",
        [
            ["timeline_start", "Regular por track pero a diferentes velocidades. "
             "Track N: gap = base_gap × speed_ratio[N]. Ratios editables (ej: 1:√2:e:π)"],
            ["event_duration", "Proporcional a la velocidad del track. "
             "Track rápido: eventos cortos. Track lento: eventos largos. gaussian estrecha"],
            ["amplitude", "Constante por track: 0.5-0.8. Sin variación dinámica. "
             "El interés viene del ritmo, no de la dinámica"],
            ["pan", "Fijo por track para distinguir las voces/velocidades. "
             "Distribuidos en el espacio stereo"],
            ["density", "Alta pero regular. La densidad percibida varía por las relaciones de tempo. "
             "Accelerandi: walk en el gap entre eventos"],
            ["effects", "Mínimos: pitch_shift vinculado a speed (o no). time_stretch para ajustar. "
             "CDP: modify speed (accleración), retime. Sin procesamiento tímbrico"],
            ["source selection", "1 source en todos los tracks (canon a diferentes velocidades). "
             "Posible 2nd source para contraste"],
            ["speed_ratios", "NUEVO param: lista de ratios de velocidad por track. "
             "Default: [1.0, 1.414, 1.618] (1:√2:φ). Editable. Define la pieza"],
        ],
        "canon (obligatorio — misma fuente a diferentes velocidades)",
        "Constante o con accelerando/decelerando global. Walk en gaps para aceleración",
        "Mínimos: modify speed, time_stretch. CDP: retime. Sin efectos de textura"
    )

    # ─── 3.11 FERNEYHOUGH ───
    e += _card(st, "BRIAN FERNEYHOUGH", C_FER, "Nueva Complejidad",
        "Máxima densidad + máxima independencia entre voces. Cada track tiene su propia lógica. "
        "Complejidad rítmica extrema: subdivisiones irracionales, cambios de tempo constantes, "
        "gestos superpuestos sin sincronización. El resultado es un torrente de información "
        "que desborda la percepción. Obras: Carceri d'Invenzione, Superscriptio, Time and Motion Study.",
        [
            ["timeline_start", "Denso e irregular: Cauchy(loc=0, scale=0.3) por track INDEPENDIENTE. "
             "Cada track tiene su propia distribución/seed. Sin sincronización entre tracks"],
            ["event_duration", "Extremadamente variable POR TRACK: Weibull(k=variable_por_track). "
             "Track 1: k=0.5 (muchos cortos). Track 2: k=2.0 (muchos medianos). Etc."],
            ["amplitude", "Variable independiente por track: Cauchy con parámetros diferentes. "
             "Track 1: loc=0.8, scale=0.1. Track 2: loc=0.3, scale=0.3. Sin correlación"],
            ["pan", "Independiente por track. Walk con diferentes steps. "
             "El espacio es tan complejo como el ritmo"],
            ["density", "Máxima y constante. Sin respiro. Sin silencios. "
             "La complejidad ES la densidad"],
            ["effects", "Diferentes por track: cada track tiene su propio perfil de efectos. "
             "Track 1: granulación. Track 2: distorsión. Track 3: spectral. "
             "Todos los params por Cauchy. Sin correlación"],
            ["source selection", "Diferente por track. Cada track elige sources con su propio Markov. "
             "Máxima independencia"],
            ["independence", "CLAVE: meta-técnica donde cada track puede tener una sub-técnica diferente. "
             "Track 1 = Xenakis, Track 2 = Ligeti, Track 3 = Lachenmann → superpuestos"],
        ],
        "scatter (todos los tracks independientes, máxima complejidad)",
        "Sin forma global. Cada track tiene su propia curva de densidad. Complejidad emergente",
        "TODOS con igual probabilidad PERO diferentes por track. CDP: el catálogo completo",
        "Es la meta-técnica: permite asignar sub-técnicas por track. La complejidad viene de "
        "la independencia total entre voces."
    )

    # ═══════════════════════════════════════════════════
    # 4. TABLA COMPARATIVA
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("4. Tabla Comparativa: 11 Técnicas", st['S1']))
    e.append(Spacer(1, 3*mm))

    comp_rows = [
        [ct("Xenakis", C_XEN), "Estocástica", "scatter, struct.", "Nubes prob.",
         "Exp/Cauchy/Weibull", "Markov + distrib.", "Alta/var."],
        [ct("Feldman", C_FEL), "Clusters", "layer, struct.", "Plana",
         "Gauss. estrecha", "Fijos (±5%)", "Baja"],
        [ct("Ligeti", C_LIG), "Micropolifonía", "scatter, layer", "Bloques",
         "Uniform/Quasi", "Smear, blur, walk", "Muy alta"],
        [ct("Cage", C_CAG), "Indeterminación", "scatter", "Ninguna",
         "Uniform puro", "Uniform todo rango", "Variable"],
        [ct("Scelsi", C_SCE), "Sonido profundo", "layer", "Arco largo",
         "Gauss.+walk", "Spectral+walk", "Mínima"],
        [ct("Reich", C_REI), "Phasing", "canon", "Constante",
         "Regular+walk", "Mínimos, fijos", "Alta const."],
        [ct("Oliveros", C_OLI), "Deep Listening", "layer, struct.", "Respiración",
         "Exp.(lambda baja)", "Reverb largo, walk", "Muy baja"],
        [ct("Lachenmann", C_LAC), "Concrète Instr.", "scatter, struct.", "Fragmentos",
         "Cauchy extrema", "Distorsión, filtro", "Variable"],
        [ct("Saariaho", C_SAA), "Espectralismo", "layer, struct.", "Spline",
         "Gauss.+walk", "Spectral, walk", "Media"],
        [ct("Nancarrow", C_NAN), "Tempo canons", "canon", "Constante",
         "Regular×ratio", "Mínimos", "Alta reg."],
        [ct("Ferneyhough", C_FER), "Nva. complejidad", "scatter", "Por track",
         "Cauchy indep.", "Todos, por track", "Máxima"],
    ]
    e.append(tbl(
        ["Técnica", "Concepto", "Strategies", "Structure", "Distribuciones", "Efectos", "Densidad"],
        comp_rows, st, cw=[W*0.11, W*0.11, W*0.10, W*0.10, W*0.16, W*0.16, W*0.10]
    ))

    # ═══════════════════════════════════════════════════
    # 5. MAPA PARÁMETRO → DISTRIBUCIÓN POR TÉCNICA
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("5. Mapa: Parámetro × Técnica → Distribución", st['S1']))
    e.append(Spacer(1, 3*mm))
    e.append(Paragraph(
        "Referencia rápida de qué distribución usa cada preset para cada parámetro del pipeline. "
        "Todos estos valores son <b>override libre</b>.", st['B']
    ))

    # timing
    e.append(Paragraph("5.1 Gap entre eventos (timing)", st['S2']))
    timing_rows = [
        [ct("Xenakis", C_XEN), "Exponencial(λ=2.0)", "0.01-15s", "Sieve opcional"],
        [ct("Feldman", C_FEL), "Cluster: Gauss(0.1,0.05) + Exp(λ=0.15)", "0.05-30s", "—"],
        [ct("Ligeti", C_LIG), "Uniform / Van der Corput", "0.01-0.15s", "—"],
        [ct("Cage", C_CAG), "Uniform", "0.0-max_silence", "—"],
        [ct("Scelsi", C_SCE), "Gaussian(dur×0.8, 2)", "0-5s", "—"],
        [ct("Reich", C_REI), "Constante=loop_period", "loop_period±0.01", "Walk phasing"],
        [ct("Oliveros", C_OLI), "Exponencial(λ=0.08)", "5-60s", "—"],
        [ct("Lachenmann", C_LAC), "Cauchy(0, 0.5)", "0-20s", "Markov dense↔silence"],
        [ct("Saariaho", C_SAA), "Gaussian(1.5, 0.8)", "0.2-8s", "—"],
        [ct("Nancarrow", C_NAN), "Constante × speed_ratio[track]", "ratio-dependiente", "Walk accel"],
        [ct("Ferneyhough", C_FER), "Cauchy indep. por track", "0.01-5s", "Diferente por track"],
    ]
    e.append(tbl(["Técnica", "Distribución", "Rango", "Modulador"],
                 timing_rows, st, cw=[W*0.13, W*0.37, W*0.20, W*0.30]))

    # amplitude
    e.append(Paragraph("5.2 Amplitud", st['S2']))
    amp_rows = [
        [ct("Xenakis", C_XEN), "Cauchy(0.5, 0.2)", "0.1-1.0", "Walk(0.10)"],
        [ct("Feldman", C_FEL), "Gaussian(0.25, 0.04)", "0.10-0.40", "Walk(0.02)"],
        [ct("Ligeti", C_LIG), "Gaussian(0.45, 0.07)", "0.20-0.65", "Walk(0.03)"],
        [ct("Cage", C_CAG), "Uniform", "0.0-1.0", "—"],
        [ct("Scelsi", C_SCE), "Gaussian(0.5, 0.03)", "0.30-0.70", "Walk(0.01)"],
        [ct("Reich", C_REI), "Constante=0.6", "0.45-0.75", "Walk(0.005)"],
        [ct("Oliveros", C_OLI), "Gaussian(0.30, 0.08)", "0.10-0.50", "Walk(0.015)"],
        [ct("Lachenmann", C_LAC), "Cauchy(0.6, 0.3)", "0.05-1.0", "—"],
        [ct("Saariaho", C_SAA), "Gaussian(0.5, 0.1)", "0.15-0.85", "Walk(0.04)"],
        [ct("Nancarrow", C_NAN), "Constante=0.65", "0.50-0.80", "—"],
        [ct("Ferneyhough", C_FER), "Cauchy (diferente/track)", "0.1-1.0", "Indep./track"],
    ]
    e.append(tbl(["Técnica", "Distribución", "Rango", "Modulador"],
                 amp_rows, st, cw=[W*0.13, W*0.32, W*0.20, W*0.35]))

    # effects
    e.append(Paragraph("5.3 Efectos — probabilidad y distribución de parámetros", st['S2']))
    fx_rows = [
        [ct("Xenakis", C_XEN), "0.85", "Cauchy/Weibull", "Walk(0.10)", "Markov"],
        [ct("Feldman", C_FEL), "0.90", "Gaussian estrecha", "Walk(0.005)", "Fijo (reverb)"],
        [ct("Ligeti", C_LIG), "0.95", "Gaussian + walk", "Walk(0.03)", "Weighted spectral"],
        [ct("Cage", C_CAG), "0.50", "Uniform todo rango", "—", "Uniform"],
        [ct("Scelsi", C_SCE), "1.0", "Gaussian + walk", "Walk(0.005)", "Weighted spectral"],
        [ct("Reich", C_REI), "0.30", "Fijo", "—", "Fijo (delay)"],
        [ct("Oliveros", C_OLI), "0.60", "Gaussian suave", "Walk(0.01)", "Weighted reverb"],
        [ct("Lachenmann", C_LAC), "0.90", "Cauchy extrema", "—", "Weighted distort"],
        [ct("Saariaho", C_SAA), "0.95", "Gaussian + walk", "Walk(0.03)", "Weighted spectral"],
        [ct("Nancarrow", C_NAN), "0.10", "Fijo", "—", "Fijo o ninguno"],
        [ct("Ferneyhough", C_FER), "0.95", "Cauchy indep.", "Indep./track", "Indep./track"],
    ]
    e.append(tbl(["Técnica", "P(efecto)", "Params", "Walk", "Selección"],
                 fx_rows, st, cw=[W*0.13, W*0.10, W*0.22, W*0.18, W*0.22]))

    # ═══════════════════════════════════════════════════
    # 6. MEZCLA LIBRE Y TÉCNICA CUSTOM
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("6. Mezcla Libre y Técnica Custom", st['S1']))
    e.append(Spacer(1, 3*mm))

    e.append(Paragraph(
        "Las 11 técnicas son presets. Pero el usuario SIEMPRE puede:", st['B']
    ))

    mix_items = [
        "Empezar con un preset y modificar cualquier parámetro → resultado híbrido",
        "Crear una TÉCNICA CUSTOM desde cero → perfil vacío que el usuario rellena",
        "Copiar un preset y modificarlo → 'Xenakis pero con amplitud de Feldman'",
        "En modo Ferneyhough: asignar SUB-TÉCNICAS por track → meta-composición",
        "Guardar y compartir presets custom como archivos .json",
        "Importar presets de la comunidad",
    ]
    for item in mix_items:
        e.append(Paragraph(f"<bullet>&bull;</bullet>{item}", st['Bul']))

    e.append(Spacer(1, 4*mm))
    e.append(Paragraph("6.1 Técnica 'Custom' (Blank Preset)", st['S2']))
    e.append(Paragraph(
        "Un preset especial que no configura nada. Todos los parámetros en sus rangos máximos, "
        "distribución uniform, sin moduladores. El usuario construye su propio perfil desde cero. "
        "Para usuarios avanzados que quieren control total sin punto de partida estético.",
        st['B']
    ))

    e.append(Paragraph("6.2 Mezcla por parámetro (Pick &amp; Mix)", st['S2']))
    e.append(Paragraph(
        "El UI permite copiar la configuración de un parámetro de una técnica a otra. "
        "Ej: 'quiero el timing de Xenakis con la amplitud de Feldman y los efectos de Saariaho'. "
        "Implementación: cada ParameterProfile es independiente y mezclable.",
        st['B']
    ))

    e.append(Paragraph("6.3 Ferneyhough como meta-técnica", st['S2']))
    e.append(Paragraph(
        "La técnica Ferneyhough permite asignar una sub-técnica diferente a cada track. "
        "Track 1 = Xenakis, Track 2 = Ligeti, Track 3 = Lachenmann, Track 4 = Cage. "
        "Cada track tiene su propia distribución, efectos, densidad. "
        "Esto es el nivel más alto de complejidad y libertad del sistema.",
        st['B']
    ))

    e.append(Spacer(1, 4*mm))
    e.append(Paragraph(
        "PRINCIPIO RECTOR: Las técnicas son mapas, no territorios. "
        "El usuario es el compositor. La app es la herramienta. "
        "Los presets son sugerencias educadas, no reglas. "
        "TODO es editable. TODO es mezclable. TODO es aleatorio si el usuario quiere.",
        st['Callout']
    ))

    # ═══════════════════════════════════════════════════
    # 7. IMPLEMENTACIÓN
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("7. Arquitectura de Implementación", st['S1']))
    e.append(Spacer(1, 3*mm))

    e.append(Paragraph("7.1 Clase CompositionTechnique", st['S2']))
    impl = [
        ["CompositionTechnique (ABC)", "get_profile() → ParameterProfile (dict de configs por param)\n"
         "get_compatible_strategies() → list[str]\n"
         "get_structure() → StructureConfig\n"
         "get_effect_preferences() → EffectPreferences\n"
         "get_description() → str (para UI)"],
        ["ParameterProfile", "Dict[param_name → ParamConfig]. Cada ParamConfig:\n"
         "distribution: str ('gaussian', 'cauchy', 'uniform', 'exponential', 'weibull', 'constant')\n"
         "dist_params: dict (mean, std, loc, scale, lambda, k...)\n"
         "range: (min, max)\n"
         "modulator: str ('walk', 'markov', 'sieve', None)\n"
         "mod_params: dict (step, drift, matrix, modulus/residue...)"],
        ["StructureConfig", "density_function: callable (t → density)\n"
         "section_markov: dict (transition matrix) o None\n"
         "form: str (descripción)\n"
         "max_events: int o None"],
        ["EffectPreferences", "effect_weights: dict[str, float] (peso por efecto, default=1.0)\n"
         "effect_probability: float\n"
         "param_profiles: dict[effect_name, ParameterProfile]"],
    ]
    e.append(tbl(["Componente", "Estructura interna"], impl, st, cw=[W*0.25, W*0.75]))

    e.append(Paragraph("7.2 Técnicas concretas", st['S2']))
    classes = [
        ["XenakisTechnique", "Exponencial/Cauchy/Weibull. Markov. Sieves. Walks. Nubes"],
        ["FeldmanTechnique", "Clusters gaussian estrecha. Amplitud baja. Reverb largo"],
        ["LigetiTechnique", "Densidad extrema. Quasi-random. Spectral smear. 6-12 tracks"],
        ["CageTechnique", "Uniform puro en todo. Sin moduladores. Sin memoria"],
        ["ScelsiTechnique", "1 source. Duración máxima. Walk mínimo. Spectral effects"],
        ["ReichTechnique", "Canon con phase_drift. Loop regular. 1 source. Mínimos efectos"],
        ["OliverosTechnique", "Gaps largos. Amplitud baja. Walk lento. Deep reverb"],
        ["LachenmannTechnique", "Cauchy extrema. Distorsión. Fragmentación. Markov dense↔silence"],
        ["SaariahoTechnique", "Walk continuo. Spectral effects. Crossfades largos. Spline density"],
        ["NancarrowTechnique", "Canon con speed_ratios. Regular×ratio. Mínimos efectos"],
        ["FerneyhoughTechnique", "Meta-técnica: sub-técnica por track. Máxima independencia"],
        ["CustomTechnique", "Blank: uniform en todo, rangos máximos, sin moduladores"],
    ]
    e.append(tbl(["Clase", "Característica principal"], classes, st, cw=[W*0.25, W*0.75]))

    e.append(Paragraph("7.3 Registro de técnicas", st['S2']))
    e.append(Paragraph(
        "TECHNIQUES_REGISTRY: dict[str, Type[CompositionTechnique]]. "
        "Las clases se registran con un nombre amigable. El UI las muestra en un selector. "
        "Añadir una técnica nueva = crear una clase + registrar. Sin cambiar código existente.",
        st['B']
    ))

    e.append(Paragraph("7.4 Flujo completo", st['S2']))
    flow = [
        "1. Usuario carga SOURCES",
        "2. Usuario selecciona TÉCNICA en el panel (o 'Custom' para empezar desde cero)",
        "3. App carga ParameterProfile con defaults de la técnica → UI se actualiza",
        "4. App sugiere STRATEGY (marcada con ★) → usuario puede cambiar",
        "5. App genera STRUCTURE → editor visual muestra la curva → usuario puede redibujar",
        "6. Usuario ajusta cualquier parámetro que quiera override (capas 2-6) — OPCIONAL",
        "7. COMPOSE: Arranger genera eventos usando el perfil (con overrides aplicados)",
        "8. Para cada evento, cada parámetro: distribución → sieve → walk → clamp → AudioEvent",
        "9. Render → Export",
        "10. REROLL: fork seed, regenerar con mismo perfil → variación manteniendo estética",
    ]
    for step in flow:
        e.append(Paragraph(step, st['B']))

    # ═══════════════════════════════════════════════════
    # 8. RESUMEN FINAL
    # ═══════════════════════════════════════════════════
    e.append(PageBreak())
    e.append(Paragraph("8. Resumen Final", st['S1']))
    e.append(Spacer(1, 3*mm))

    summary = [
        ["¿Cuántas técnicas?", "11 presets + 1 Custom (blank). Extensible sin límite"],
        ["¿Son obligatorias?", "NO. El usuario puede usar Custom (= v0.1 sin preset) o no elegir ninguna"],
        ["¿Encasillan?", "NO. Son puntos de partida. Todo es editable después de seleccionar"],
        ["¿Se pueden mezclar?", "SÍ. Pick &amp; Mix por parámetro. Ferneyhough = sub-técnica por track"],
        ["¿Qué define cada técnica?", "Distribuciones, rangos, moduladores, structure, efectos. Para CADA parámetro"],
        ["¿Sources cambian?", "NO. Sin cambios"],
        ["¿Strategy cambia?", "NO. Las 4 se mantienen. La técnica solo RECOMIENDA"],
        ["¿Structure cambia?", "SÍ. Se DERIVA de la técnica. Pero override libre (editor visual)"],
        ["¿RNG cambia?", "Se AMPLÍA: +Exponencial, +Cauchy, +Weibull, +Poisson, +Sieves, +Walks. La seed funciona igual"],
        ["¿Effects cambian?", "SÍ. Los params se generan estocásticamente. Ya no van vacíos"],
        ["¿Es backward compatible?", "SÍ. Técnica 'Cage' + Strategy 'scatter' ≈ comportamiento v0.1"],
        ["¿Orden del flujo?", "SOURCES → TÉCNICA → STRATEGY → STRUCTURE → RNG → EFFECTS → COMPOSITION"],
    ]
    e.append(tbl(["Pregunta", "Respuesta"], summary, st, cw=[W*0.22, W*0.78]))

    e.append(Spacer(1, 6*mm))
    e.append(Paragraph(
        "El usuario es el compositor. Las técnicas son pinceles. "
        "La app pone a disposición las herramientas de Xenakis, Feldman, Ligeti, Cage, Scelsi, "
        "Reich, Oliveros, Lachenmann, Saariaho, Nancarrow y Ferneyhough — y luego se aparta. "
        "Aleatoric Composer: libertad estocástica con guía estética opcional.",
        st['Callout']
    ))

    return e


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(SLATE)
    canvas.rect(0, A4[1]-11*mm, A4[0], 11*mm, fill=1, stroke=0)
    canvas.setFillColor(AMBER)
    canvas.rect(0, A4[1]-11.8*mm, A4[0], 0.8*mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont('Helvetica-Bold', 7.5)
    canvas.drawString(15*mm, A4[1]-7.5*mm, "Aleatoric Composer v0.2 — Técnicas Compositivas")
    canvas.setFillColor(AMBER)
    canvas.drawRightString(A4[0]-15*mm, A4[1]-7.5*mm, f"Pág. {doc.page}")
    canvas.setFillColor(TEXT_MUTED)
    canvas.setFont('Helvetica', 6.5)
    canvas.drawCentredString(A4[0]/2, 7*mm,
        "Xenakis · Feldman · Ligeti · Cage · Scelsi · Reich · Oliveros · Lachenmann · Saariaho · Nancarrow · Ferneyhough")
    canvas.restoreState()


def first_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(SLATE_120)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFillAlpha(0.05)
    canvas.setFillColor(C_XEN)
    canvas.circle(A4[0]-30*mm, A4[1]-50*mm, 100*mm, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.circle(50*mm, 70*mm, 70*mm, fill=1, stroke=0)
    canvas.setFillColor(AMBER)
    canvas.circle(A4[0]/2, A4[1]/2-20*mm, 50*mm, fill=1, stroke=0)
    canvas.setFillColor(C_LIG)
    canvas.circle(30*mm, A4[1]-100*mm, 40*mm, fill=1, stroke=0)
    canvas.setFillColor(C_SAA)
    canvas.circle(A4[0]-60*mm, 120*mm, 35*mm, fill=1, stroke=0)
    canvas.restoreState()
    header_footer(canvas, doc)


def main():
    st = styles()
    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        topMargin=17*mm, bottomMargin=14*mm,
        leftMargin=15*mm, rightMargin=15*mm,
        title="Técnicas Compositivas — Aleatoric Composer v0.2",
        author="Aleatoric Composer Team",
    )
    elements = build(st)
    doc.build(elements, onFirstPage=first_page, onLaterPages=header_footer)
    print(f"PDF: {OUT}")
    print(f"  Size: {OUT.stat().st_size / 1024:.0f} KB")


if __name__ == '__main__':
    main()
