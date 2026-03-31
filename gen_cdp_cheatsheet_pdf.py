#!/usr/bin/env python3
"""Generate CDP Effects Cheatsheet — A3 Landscape PDF
   Styled with the Aleatoric Composer design system."""

from pathlib import Path
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import textwrap

OUT = Path(__file__).parent / "CDP_Cheatsheet_A3.pdf"

# ── Design System Colors ──
AMBER = HexColor("#FBAD17")
AMBER_10 = HexColor("#FFF8E7")
AMBER_20 = HexColor("#FEEFC3")
AMBER_120 = HexColor("#D9920A")
SLATE = HexColor("#303C42")
SLATE_10 = HexColor("#EEF0F1")
SLATE_20 = HexColor("#CDD1D4")
TEAL = HexColor("#005A65")
TEAL_10 = HexColor("#E6F2F4")
TEAL_20 = HexColor("#B3D9DE")
TEAL_60 = HexColor("#007D8C")
SAND = HexColor("#A69C95")
SAND_10 = HexColor("#F6F4F2")
SAND_20 = HexColor("#E5E1DE")
SAND_40 = HexColor("#C7BFB9")
SAND_120 = HexColor("#857870")
BG = HexColor("#F8F6F3")
TEXT_COLOR = HexColor("#1A1F22")
TEXT_MUTED = HexColor("#6B7780")
SURFACE = HexColor("#FFFFFF")

# Section color themes: (header_bg, num_bg, title_color)
SEC_COLORS = {
    "reverb":     (TEAL_10, TEAL, TEAL),
    "filter":     (HexColor("#F3E5F5"), HexColor("#6A1B9A"), HexColor("#6A1B9A")),
    "distortion": (HexColor("#FFEBEE"), HexColor("#C0392B"), HexColor("#C0392B")),
    "granular":   (HexColor("#E8F5E9"), HexColor("#2E7D32"), HexColor("#2E7D32")),
    "time":       (HexColor("#FFF3E0"), HexColor("#E65100"), HexColor("#E65100")),
    "spectral":   (HexColor("#E3F2FD"), HexColor("#1565C0"), HexColor("#1565C0")),
    "modulation": (HexColor("#E0F7FA"), HexColor("#00838F"), HexColor("#00838F")),
    "envelope":   (AMBER_10, AMBER, AMBER_120),
    "synthesis":  (SLATE_10, SLATE, SLATE),
    "spatial":    (HexColor("#EDE7F6"), HexColor("#311B92"), HexColor("#311B92")),
    "other":      (SAND_10, SAND_120, SAND_120),
    "quick":      (AMBER_10, AMBER, AMBER_120),
}

# Type badge colors
TYPE_COLORS = {
    "WAV":      (AMBER_10, AMBER_120),
    "WAV/MONO": (AMBER_10, AMBER_120),
    "SPECTRAL": (TEAL_10, TEAL),
    "SYNTH":    (SAND_10, SAND_120),
}

# ── DATA ──
SECTIONS = [
    ("reverb", "1", "REVERB & DELAY", [
        ("reverb", "WAV", "Reverb multicanal. 1-16 ch.", "rgain mix rvbtime absorb lpfreq trtime", None),
        ("rmverb", "WAV", "Reverb con sala (S/M/L).", "rmsize rgain mix fback absorb", None),
        ("newdelay", "WAV", "Delay basado en pitch con resonancia.", "midipitch(TV) mix feedback", None),
        ("sfecho", "WAV", "Echo simple con decaimiento.", "delay(TV) atten(TV) totaldur -r -c", None),
        ("tapdelay", "WAV", "Multi-tap delay stereo con panning.", "tapgain feedback mix trailtime taps.txt", None),
        ("modify revecho", "WAV", "Reverb/echo/resonancia. 3 modos.", None, "M1:delay | M2:delay LFO | M3:stadium"),
        ("fastconv", "WAV", "Convolución rápida (IR reverb).", None, None),
        ("dvdwind", "WAV", "Contracción temporal read-skip.", "contraction >1, clipsize (ms)", None),
    ]),
    ("filter", "2", "FILTROS", [
        ("filter fixed", "WAV", "Boost/cut en freq fija. 3 modos.", "freq boost/cut bwidth(M3)", None),
        ("filter variable", "WAV", "LP/HP/BP/Notch variable.", "acuity(TV) gain frq(TV)", None),
        ("filter lohi", "WAV", "Lowpass/Highpass fijo.", "attenuation pass-band stop-band", None),
        ("filter bank", "WAV", "Banco de filtros Q variable. 6 modos.", "Q(TV) gain lof hif -s scat -d", None),
        ("filter userbank", "WAV", "Banco por usuario (pitch/amp).", "datafile Q(TV) gain", None),
        ("filter varibank", "WAV", "Banco variable en tiempo.", "data(TV) Q(TV) gain -h -r", None),
        ("filter sweeping", "WAV", "Filtro con barrido. 4 modos.", "acuity(TV) lofrq(TV) hifrq(TV) sweepfrq(TV)", None),
        ("filter iterated", "WAV", "Filtrado iterativo con delay.", "datafile Q gain delay dur -r -p -a -e", None),
        ("filter phasing", "WAV", "Phaser. 2 modos.", "gain delay(TV)", None),
        ("synfilt", "SYNTH", "Síntesis de ruido filtrado.", "data dur srate Q gain hcnt rolloff", None),
    ]),
    ("distortion", "3", "DISTORSIÓN", [
        ("distort", "WAV/MONO", "Suite distorsión wavecycles. 21 sub-modos.", None,
         "fractal·harmonic·multiply·divide·overload·reform·pitch·envel·repeat·reverse·shuffle·delete·filter·interpolate·telescope·omit·replace·average·pulsed·interact"),
        ("distcut", "WAV", "Corta elementos con decay envelope.", "cyclecnt exp -c limit", None),
        ("distmark", "WAV/MONO", "Interpolación wavesets en marcas.", "marklist unitlen(TV) -s -r", None),
        ("clip", "WAV", "Recorte de señal. 2 modos.", None, None),
        ("constrict", "WAV", "Acortar secciones de silencio.", "constriction 0-200%", None),
        ("crumble", "WAV", "Desintegración multicanal progresiva.", "stt dur1-3 size(TV) rand(TV) pscat(TV)", None),
        ("bounce", "WAV", "Rebotes con aceleración y decay.", "count startgap shorten endlevel ewarp", None),
        ("splinter", "WAV", "Astillas repetidas y encogidas.", "target wcnt shrcnt ocnt p1 p2 -f", None),
        ("shrink", "WAV", "Repite acortando. 6 modos.", "shrinkage gap contract dur", None),
        ("quirk", "WAV", "Distorsión por potencia muestras.", "powfac 0.01-100", None),
        ("scramble", "WAV", "Reordena wavesets. 10 modos.", "-c cnt -t trns(TV) -a atten(TV) seed", None),
    ]),
    ("granular", "4", "GRANULAR", [
        ("grain", "WAV", "Suite de granos. 16 sub-modos.", "-l gate(TV) -h minhole -b len -t win",
         "omit·repitch·timewarp·duplicate·rerhythm·reverse·reposition·reorder·remotif·r_extend·grev·noise_extend·align"),
        ("grainex", "WAV", "Extiende zona de granos.", "wsiz trof plus stt end", None),
        ("grnmill", "WAV", "Granulador completo.", None, None),
        ("hover", "WAV", "Lectura zigzag a freq dada.", "frq(TV) loc(TV) frqrand(TV) locrand(TV) splice dur", None),
        ("hover2", "WAV", "Zigzag desde zero-crossings.", "frq(TV) loc(TV) frqrand(TV) locrand(TV) dur", None),
        ("stutter", "WAV", "Corta en sílabas y reordena.", "datafile dur segjoins silprop seed -t -a -b", None),
        ("packet", "WAV", "Aísla/genera paquetes de onda.", "times narrowing centring", None),
        ("wrappage", "WAV", "Granulación multicanal (Wishart).", "outchans centre(TV) spread(TV) veloc(TV) dens(TV) gsize(TV) pshift(TV) amp(TV) jitter(TV)", None),
        ("modify brassage", "WAV", "Brassage granular de Wishart.", None, None),
    ]),
    ("time", "5", "TIEMPO & PITCH", [
        ("modify speed", "WAV", "Velocidad/pitch. 4 modos.", "speed(TV) semitone(TV) accel vibrate(TV)",
         "M1:multiplicador | M2:semitonos | M5:accel | M6:vibrato"),
        ("strans multi", "WAV", "Speed/pitch multicanal. 4 modos.", "speed(TV) semitone(TV) accel vibfrq(TV)", None),
        ("retime", "WAV", "Ajuste rítmico. 14 modos.", None, "pulse·timestretch·speed·beats·repeat-a-tempo..."),
        ("psow", "WAV", "Granos pitch-síncronos (FOFs). 12 modos.", None,
         "stretch·dupl·delete·strtrans·grab·sustain·chop·interp·synth·impose·space·reinforce"),
        ("tweet", "WAV", "Reemplaza FOFs por tweets/ruido. 3 modos.", "pitchdata minlevel pkcnt frq chirp", None),
    ]),
    ("spectral", "6", "SPECTRAL", [
        ("blur", "SPECTRAL", "Difuminado espectral. 10 sub-modos.", None,
         "avrg·blur·suppress·chorus·drunk·shuffle·weave·noise·scatter·spread"),
        ("morph", "SPECTRAL", "Morphing entre espectros. 2 inputs.", None, "glide·bridge·morph"),
        ("newmorph", "SPECTRAL", "Nuevos tipos de morphing. 2 inputs.", None, None),
        ("focus", "SPECTRAL", "Enfoque espectral. 7 sub-modos.", None, "accu·exag·focus·fold·freeze·hold·step"),
        ("hilite", "SPECTRAL", "Resaltado espectral. 8 sub-modos.", None, "filter·greq·band·arpeg·pluck·trace·bltr·vowels"),
        ("specfnu", "SPECTRAL", "Manipulación formantes. 23 modos.", None, "narrow·compress·invert·rotate·negative·arpeg·octshift·transpose·respace·randpitch·sine-speech..."),
        ("specfold", "SPECTRAL", "Plegar/invertir/randomizar. 3 modos.", "stt len cnt seed", None),
        ("specsphinx", "SPECTRAL", "Cross-spectral. 2 inputs.", "-a ampbal -f frqbal -b bias -g gain", None),
        ("spectstr", "SPECTRAL", "Time-stretch anti-artefactos.", "timestretch(TV) d-ratio di-rand", None),
        ("spectwin", "SPECTRAL", "Interpolación 2 espectros.", "-f frqint -e envint -d dupl -s step", None),
        ("stretch", "SPECTRAL", "Stretch de freq y temporal.", "frq_divide maxstretch exponent timestretch(TV)", "spectrum 1/2 · time 1"),
        ("glisten", "SPECTRAL", "Partición aleatoria espectro.", "grpdiv setdur -p pitchshift -d durrand", None),
    ]),
    ("modulation", "7", "MODULACIÓN & TREMOLO", [
        ("tremolo", "WAV", "Tremolo con narrowing.", "frq(TV) 0-500Hz depth(TV) gain(TV) fineness", None),
        ("tremenv", "WAV", "Tremolo post-peak del envelope.", "frq depth winsize fineness", None),
        ("flutter", "WAV", "Tremulación multicanal.", "chanseq freq(TV) depth(TV) gain", None),
        ("phasor", "WAV/MONO", "Phasing por múltiples streams.", "streams 2-8 phasfrq(TV) shift(TV) 0-12st ochans", None),
        ("rotor", "WAV", "Sets notas con rango/veloc variable.", "cnt minp maxp step prot trot phas dur", None),
    ]),
    ("envelope", "8", "ENVELOPE", [
        ("envel warp", "WAV", "Deformación envelope. 15 modos.", None,
         "normalise·reverse·exaggerate·attenuate·lift·timestretch·flatten·gate·invert·limit·corrugate·expand·trigger·ceiling·ducked"),
        ("envel impose", "WAV", "Imponer envelope. 4 fuentes.", None, "soundfile·binary·breakpoint 0-1·breakpoint dB"),
        ("envel replace", "WAV", "Reemplazar envelope (4 modos).", None, None),
        ("envel tremolo", "WAV", "Tremolo por modulación envelope.", "frq(TV) depth(TV) gain(TV)", None),
        ("envel attack", "WAV", "Enfatizar ataque.", "gain onset 5-32767ms decay", None),
        ("envel dovetail", "WAV", "Fade-in/out configurable.", "infadedur outfadedur intype outtype", None),
        ("envel pluck", "WAV/MONO", "Ataque de pluck.", "startsamp wavelen -a atkcycles -d decayrate", None),
        ("envcut", "WAV", "Cortar con envelope descendente.", "envlen attack exp", None),
        ("envspeak", "WAV", "Procesamiento sílabas. 25 modos.", None, "repeat·reverse-repeat·attenuate·shrink·divide·extract·reorder..."),
        ("gate", "WAV", "Puerta de ruido. 2 modos.", "gatelevel 0 a -96dB", None),
    ]),
    ("synthesis", "9", "SÍNTESIS", [
        ("brownian", "WAV", "Textura browniana desde source.", "chans dur att(TV) dec(TV) plo(TV) phi(TV) step(TV) tick(TV)", None),
        ("chirikov", "SYNTH", "Mapas caóticos (Standard/Circle).", "dur frq(TV) damping(TV) srate", None),
        ("crystal", "WAV", "Eventos desde cristal rotante 3D.", "vdat rota rotb twidth tstep plo phi", None),
        ("cascade", "WAV", "Echo-cascada de segmentos.", "clipsize(TV) echos(TV) -r rand(TV) -N shredno(TV)", None),
        ("cantor", "WAV", "Conjunto de Cantor (fractal).", "holesize holedig maxdur", None),
        ("fractal", "WAV", "Fractalización de sonido.", "layers -s splicelen", None),
        ("motor", "WAV", "Pulsos rápidos dentro de lentos.", "dur freq pulse fratio pratio sym -j -t", None),
        ("synspline", "SYNTH", "Síntesis por splines aleatorios.", "frq(TV) splinecnt(TV) interpval(TV) -d -v", None),
    ]),
    ("spatial", "10", "ESPACIAL & MIXING", [
        ("mchanpan", "WAV", "Pan multicanal. 10 modos.", None, "positions·switch·spread-step·spread-gradual·antifonal·pan-config·rotación·switch-rand"),
        ("mchanrev", "WAV", "Ecos/reverb multicanal (stadium).", "gain roll_off size count centre spread", None),
        ("mchiter", "WAV", "Iteración multicanal fluida.", "outchans -d delay -r rand -p pshift -a -f", None),
        ("mchshred", "WAV", "Shred multicanal.", "repeats chunklen scatter", None),
        ("mchzig", "WAV", "Zigzag con pan aleatorio.", "start end dur minzig outchans", None),
        ("panorama", "WAV", "Distribuye monos en panorama.", "lspk_cnt lspk_aw sounds_aw -r rand", None),
        ("modify space", "WAV", "Espacio stereo. 3 modos.", "pan(TV) narrowing -p prescale", "M1:pan | M2:mirror | M4:narrow"),
        ("texmchan", "WAV", "Textura multicanal armónica.", "notedata outdur packing scatter outchans -s spread", None),
    ]),
    ("other", "11", "OTROS EFECTOS", [
        ("flatten", "WAV", "Ecualizar nivel de elementos.", "elementsize 0.001-100s shoulder", None),
        ("isolate", "WAV", "Cortar segmentos manteniendo timing. 5 modos.", None, None),
        ("manysil", "WAV", "Insertar silencios en tiempos.", "silencedata splicelen", None),
        ("repeater", "WAV", "Repetir elementos con accel/bounce.", "datafile -r rand(TV) -p prand(TV) accel warp fade", None),
        ("shifter", "WAV", "Ciclos repetición con foco.", "cycles cycdur dur ochans linger transit boost", None),
        ("frame", "WAV", "Manipulación canales. 6 modos.", None, "rotate·rotate-pair·reassign·mirror·swap·envelope-ind"),
    ]),
]

QUICK_REF = [
    ("1", "reverb", "Reverb multicanal"),
    ("2", "rmverb", "Reverb con sala"),
    ("3", "sfecho", "Echo simple"),
    ("4", "tapdelay", "Multi-tap stereo"),
    ("5", "filter variable", "LP/HP/BP/Notch"),
    ("6", "filter sweeping", "Filtro con sweep"),
    ("7", "filter phasing", "Phaser"),
    ("8", "tremolo", "Tremolo"),
    ("9", "distort fractal", "Dist. fractal"),
    ("10", "distort reform", "Waveshape (8)"),
    ("11", "distort pitch", "Transpone wavecycles"),
    ("12", "bounce", "Rebotes acelerados"),
    ("13", "clip", "Recorte señal"),
    ("14", "gate", "Puerta de ruido"),
    ("15", "envel dovetail", "Fade in/out"),
    ("16", "envel attack", "Enfatizar ataque"),
    ("17", "envel warp", "15 deformaciones"),
    ("18", "modify speed", "Pitch/speed"),
    ("19", "modify space", "Pan stereo"),
    ("20", "hover", "Zigzag granular"),
    ("21", "stutter", "Tartamudeo"),
    ("22", "grain omit", "Omitir granos"),
    ("23", "grain timewarp", "Stretch granos"),
    ("24", "grain reverse", "Invertir granos"),
    ("25", "wrappage", "Granul. multicanal"),
    ("26", "scramble", "Reordenar wavesets"),
    ("27", "constrict", "Acortar silencios"),
    ("28", "quirk", "Dist. potencia"),
    ("29", "fractal", "Capas fractales"),
    ("30", "dvdwind", "Contracción read-skip"),
]
QUICK_REF_SPECTRAL = [
    ("31", "blur (10)", "Difuminado spectral"),
    ("32", "morph", "Morphing espectros"),
    ("33", "focus (7)", "Enfoque spectral"),
    ("34", "hilite (8)", "Resaltado spectral"),
    ("35", "specfnu (23)", "Formantes"),
    ("36", "specfold", "Plegar espectro"),
    ("37", "specsphinx", "Cross-spectral"),
    ("38", "spectstr", "Time-stretch spectral"),
    ("39", "spectwin", "Interpolación spectral"),
    ("40", "stretch", "Stretch freq/tiempo"),
    ("41", "glisten", "Partición aleatoria"),
]


def hex_to_rgb(hc):
    """Convert HexColor to (r,g,b) tuple 0-1."""
    return (hc.red, hc.green, hc.blue)


def draw_rounded_rect(c, x, y, w, h, r, fill=None, stroke=None, stroke_width=0.5):
    """Draw a rounded rectangle."""
    c.saveState()
    if fill:
        c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(stroke_width)
    p = c.beginPath()
    p.roundRect(x, y, w, h, r)
    if fill and stroke:
        c.drawPath(p, fill=1, stroke=1)
    elif fill:
        c.drawPath(p, fill=1, stroke=0)
    elif stroke:
        c.drawPath(p, fill=0, stroke=1)
    c.restoreState()


def draw_section(c, sx, sy, sw, sh, sec_data):
    """Draw a section card. sy is top-left Y (PDF coords: bottom-up)."""
    theme_key, num, title, effects = sec_data
    hdr_bg, num_bg, title_color = SEC_COLORS[theme_key]

    # Card background
    draw_rounded_rect(c, sx, sy, sw, sh, 4, fill=SURFACE, stroke=SAND_20, stroke_width=0.4)

    # Header bar
    hdr_h = 18
    draw_rounded_rect(c, sx, sy + sh - hdr_h, sw, hdr_h, 4, fill=hdr_bg)
    # Cover bottom corners of header
    c.saveState()
    c.setFillColor(hdr_bg)
    c.rect(sx, sy + sh - hdr_h, sw, 5, fill=1, stroke=0)
    c.restoreState()

    # Number badge
    badge_sz = 12
    bx = sx + 5
    by = sy + sh - hdr_h + (hdr_h - badge_sz) / 2
    draw_rounded_rect(c, bx, by, badge_sz, badge_sz, 3, fill=num_bg)
    c.saveState()
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(bx + badge_sz / 2, by + 3, num)
    c.restoreState()

    # Title
    c.saveState()
    c.setFillColor(title_color)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(bx + badge_sz + 4, by + 3, title)
    c.restoreState()

    # Count
    count = len(effects)
    c.saveState()
    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 7)
    c.drawRightString(sx + sw - 5, by + 3, f"{count} efectos")
    c.restoreState()

    # Effects list
    ey = sy + sh - hdr_h - 5
    left_margin = sx + 6
    max_w = sw - 12

    for i, (name, typ, desc, params, submodes) in enumerate(effects):
        # Name
        c.saveState()
        c.setFont("Courier-Bold", 7.5)
        c.setFillColor(SLATE)
        name_w = c.stringWidth(name, "Courier-Bold", 7.5)
        c.drawString(left_margin, ey, name)

        # Type badge
        base_type = typ.split("/")[0].split(" ")[0]
        if base_type in ("SPECTRAL",):
            badge_bg, badge_fg = TYPE_COLORS["SPECTRAL"]
        elif base_type in ("SYNTH",):
            badge_bg, badge_fg = TYPE_COLORS["SYNTH"]
        else:
            badge_bg, badge_fg = TYPE_COLORS["WAV"]

        tbx = left_margin + name_w + 4
        tbw = c.stringWidth(typ, "Helvetica", 5.5) + 6
        draw_rounded_rect(c, tbx, ey - 1, tbw, 8, 2, fill=badge_bg)
        c.setFont("Helvetica", 5.5)
        c.setFillColor(badge_fg)
        c.drawString(tbx + 3, ey + 0.5, typ)
        c.restoreState()

        ey -= 9

        # Description
        c.saveState()
        c.setFont("Helvetica", 6.5)
        c.setFillColor(TEXT_MUTED)
        c.drawString(left_margin, ey, desc)
        c.restoreState()
        ey -= 7.5

        # Params
        if params:
            c.saveState()
            c.setFont("Courier", 5.5)
            c.setFillColor(TEAL_60)
            # Truncate if too long
            txt = params
            while c.stringWidth(txt, "Courier", 5.5) > max_w and len(txt) > 10:
                txt = txt[:-4] + "..."
            c.drawString(left_margin, ey, txt)
            c.restoreState()
            ey -= 6.5

        # Submodes
        if submodes:
            c.saveState()
            c.setFont("Helvetica-Oblique", 5.5)
            c.setFillColor(SAND_120)
            txt = submodes
            while c.stringWidth(txt, "Helvetica-Oblique", 5.5) > max_w and len(txt) > 10:
                txt = txt[:-4] + "..."
            c.drawString(left_margin, ey, txt)
            c.restoreState()
            ey -= 6.5

        # Separator line
        if i < len(effects) - 1:
            c.saveState()
            c.setStrokeColor(SAND_20)
            c.setLineWidth(0.3)
            c.line(left_margin, ey + 2, sx + sw - 6, ey + 2)
            c.restoreState()
            ey -= 2.5


def calc_section_height(effects):
    """Calculate needed height for a section."""
    hdr_h = 18
    h = hdr_h + 5  # header + top padding
    for name, typ, desc, params, submodes in effects:
        h += 9    # name line
        h += 7.5  # desc line
        if params:
            h += 6.5
        if submodes:
            h += 6.5
        h += 2.5  # separator
    return h


def draw_quick_ref(c, sx, sy, sw, sh):
    """Draw the quick reference section."""
    hdr_bg, num_bg, title_color = SEC_COLORS["quick"]

    draw_rounded_rect(c, sx, sy, sw, sh, 4, fill=SURFACE, stroke=SAND_20, stroke_width=0.4)

    hdr_h = 18
    draw_rounded_rect(c, sx, sy + sh - hdr_h, sw, hdr_h, 4, fill=hdr_bg)
    c.saveState()
    c.setFillColor(hdr_bg)
    c.rect(sx, sy + sh - hdr_h, sw, 5, fill=1, stroke=0)
    c.restoreState()

    # Star badge
    badge_sz = 12
    bx = sx + 5
    by = sy + sh - hdr_h + (hdr_h - badge_sz) / 2
    draw_rounded_rect(c, bx, by, badge_sz, badge_sz, 3, fill=AMBER)
    c.saveState()
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(bx + badge_sz / 2, by + 2.5, "\u2605")
    c.restoreState()

    c.saveState()
    c.setFillColor(AMBER_120)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(bx + badge_sz + 4, by + 3, "TOP 30 WAV + 11 SPECTRAL")
    c.restoreState()

    # Grid: 3 columns
    col_w = (sw - 16) / 3
    ey = sy + sh - hdr_h - 7
    items_per_col = 14

    # WAV items
    for i, (num, name, desc) in enumerate(QUICK_REF):
        col = i // items_per_col
        row = i % items_per_col
        ix = sx + 8 + col * col_w
        iy = ey - row * 8.5

        c.saveState()
        c.setFont("Courier", 5.5)
        c.setFillColor(TEXT_MUTED)
        c.drawRightString(ix + 10, iy, num)
        c.setFont("Courier-Bold", 6)
        c.setFillColor(SLATE)
        c.drawString(ix + 13, iy, name)
        c.setFont("Helvetica", 5.5)
        c.setFillColor(TEXT_MUTED)
        c.drawString(ix + 13 + c.stringWidth(name, "Courier-Bold", 6) + 3, iy, desc)
        c.restoreState()

    # Spectral items
    spec_start = len(QUICK_REF)
    for i, (num, name, desc) in enumerate(QUICK_REF_SPECTRAL):
        idx = spec_start + i
        col = idx // items_per_col
        row = idx % items_per_col
        ix = sx + 8 + col * col_w
        iy = ey - row * 8.5

        c.saveState()
        c.setFont("Courier", 5.5)
        c.setFillColor(TEAL)
        c.drawRightString(ix + 10, iy, num)
        c.setFont("Courier-Bold", 6)
        c.setFillColor(TEAL)
        c.drawString(ix + 13, iy, name)
        c.setFont("Helvetica", 5.5)
        c.setFillColor(TEXT_MUTED)
        c.drawString(ix + 13 + c.stringWidth(name, "Courier-Bold", 6) + 3, iy, desc)
        c.restoreState()


def main():
    pw, ph = landscape(A3)  # 1190.55 x 841.89 points
    c = canvas.Canvas(str(OUT), pagesize=landscape(A3))

    # ═══ HEADER ═══
    header_h = 40
    c.saveState()
    c.setFillColor(SLATE)
    c.rect(0, ph - header_h, pw, header_h, fill=1, stroke=0)

    # Decorative circle
    c.saveState()
    from reportlab.lib.colors import Color
    c.setFillColor(Color(AMBER.red, AMBER.green, AMBER.blue, 0.1))
    c.circle(pw - 30, ph - 5, 50, fill=1, stroke=0)
    c.restoreState()

    # Label
    c.setFillColor(AMBER)
    c.setFont("Courier", 7)
    c.drawString(24, ph - 14, "ALEATORIC COMPOSER V0.2")

    # Title
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(24, ph - 32, "CDP Effects")
    c.setFillColor(AMBER)
    c.setFont("Helvetica-BoldOblique", 18)
    c.drawString(24 + c.stringWidth("CDP Effects ", "Helvetica-Bold", 18), ph - 32, "Cheatsheet")

    # Badges
    badges = [
        ("WAV DIRECTO", AMBER, SLATE),
        ("SPECTRAL (specanal\u2192pvoc)", TEAL, white),
        ("SYNTH", SAND_120, white),
        ("TV = TIME-VARIABLE", None, AMBER),
    ]
    bx = pw - 24
    for label, bg, fg in reversed(badges):
        c.setFont("Courier", 6.5)
        bw = c.stringWidth(label, "Courier", 6.5) + 12
        bx -= bw + 5
        if bg:
            draw_rounded_rect(c, bx, ph - 30, bw, 13, 4, fill=bg)
        else:
            draw_rounded_rect(c, bx, ph - 30, bw, 13, 4, stroke=SAND_40)
        c.setFillColor(fg)
        c.setFont("Courier", 6.5)
        c.drawString(bx + 6, ph - 26.5, label)

    c.restoreState()

    # ═══ LAYOUT: 6 columns × 2 rows of sections + quick ref ═══
    margin_x = 10
    margin_top = 6
    margin_bot = 18
    gap = 6

    content_top = ph - header_h - margin_top
    content_bot = margin_bot
    content_h = content_top - content_bot
    content_w = pw - 2 * margin_x

    # We have 12 sections. Layout: 6 columns.
    # Row 1: reverb, filter, distortion, granular, time, spectral (heavy sections)
    # Row 2: modulation, envelope, synthesis, spatial, other, quick_ref
    n_cols = 6
    col_w = (content_w - (n_cols - 1) * gap) / n_cols

    # Calculate heights for each section
    heights = {}
    for sec in SECTIONS:
        theme, num, title, effects = sec
        heights[theme] = calc_section_height(effects)

    row1_sections = SECTIONS[0:6]   # reverb through spectral
    row2_sections = SECTIONS[6:11]  # modulation through other

    # Split available height: proportional to content
    row1_max = max(heights[s[0]] for s in row1_sections)
    row2_max = max(heights[s[0]] for s in row2_sections)
    quick_ref_h = 5.8 * 14 + 20  # roughly

    # Use all available height
    total_needed = row1_max + row2_max + gap
    scale = content_h / total_needed if total_needed > content_h else 1.0

    row1_h = (content_h - gap) * (row1_max / (row1_max + row2_max))
    row2_h = content_h - gap - row1_h

    row1_y = content_bot + row2_h + gap  # top row is higher
    row2_y = content_bot

    # Draw Row 1
    for i, sec in enumerate(row1_sections):
        sx = margin_x + i * (col_w + gap)
        draw_section(c, sx, row1_y, col_w, row1_h, sec)

    # Draw Row 2 (5 sections + quick ref taking last column)
    for i, sec in enumerate(row2_sections):
        sx = margin_x + i * (col_w + gap)
        draw_section(c, sx, row2_y, col_w, row2_h, sec)

    # Quick Ref in last column of row 2
    qr_x = margin_x + 5 * (col_w + gap)
    draw_quick_ref(c, qr_x, row2_y, col_w, row2_h)

    # ═══ FOOTER ═══
    footer_h = 14
    c.saveState()
    c.setFillColor(SLATE)
    c.rect(0, 0, pw, footer_h, fill=1, stroke=0)
    c.setFillColor(SAND_40)
    c.setFont("Courier", 6)
    c.drawString(24, 4, "CDP RELEASE 8 \u2014 COMPOSER'S DESKTOP PROJECT (TREVOR WISHART ET AL.)")
    c.drawCentredString(pw / 2, 4, "ALEATORIC COMPOSER v0.2 \u2014 82 EFECTOS \u00b7 11 CATEGOR\u00cdAS \u00b7 ~200 SUB-MODOS")
    c.drawRightString(pw - 24, 4, "A3 LANDSCAPE \u2014 420\u00d7297mm")
    c.restoreState()

    c.save()
    print(f"PDF: {OUT}")
    print(f"  Size: {OUT.stat().st_size / 1024:.0f} KB")
    n_fx = sum(len(s[3]) for s in SECTIONS)
    print(f"  {len(SECTIONS)} secciones, {n_fx} efectos documentados")


if __name__ == "__main__":
    main()
