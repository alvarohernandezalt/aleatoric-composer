# Fundamental — Compositor Semi-Aleatorio de Audio

## Descripción General

Fundamental es una aplicación de escritorio para composición musical semi-aleatoria. Toma archivos de audio como materia prima, les aplica procesos (granulares, espectrales, efectos clásicos y experimentales), y monta composiciones multipista usando métodos controlados por azar. El resultado se exporta como archivo de audio.

---

## Características Principales

### Carga de Audio
- **Formatos soportados**: WAV, MP3, FLAC, OGG, AIFF
- **Sin límite de archivos**: Se pueden cargar tantos archivos fuente como se desee
- **Métodos de carga**: Botón "+ Add audio files" o menú File > Add audio files (Ctrl+O)
- **Visualización**: Cada archivo muestra nombre, duración, canales, sample rate y mini waveform
- **Pesos por fuente**: Slider individual por archivo para controlar su probabilidad de aparición en la composición (0.0 a 1.0)
- **Colores automáticos**: Cada fuente recibe un color distinto para identificarla visualmente en el timeline

### Motor de Composición

#### Parámetros Configurables
| Parámetro | Rango | Default | Descripción |
|-----------|-------|---------|-------------|
| Estrategia | scatter, structured, layer, canon | scatter | Algoritmo de distribución de eventos |
| Semilla (Seed) | 0 – 2,147,483,647 | 42 | Semilla RNG para reproducibilidad |
| Duración total | 1.0 – 3,600.0 s | 120.0 s | Duración de la composición (hasta 1 hora) |
| Número de tracks | 1 – 16 | 4 | Pistas simultáneas |
| Duración de evento | 0.01 – 60.0 s | 0.5 – 30.0 s | Rango min/max de cada fragmento |
| Silencio entre eventos | 0.0 – 30.0 s | 0.0 – 5.0 s | Rango min/max de gaps |
| Permitir overlap | Sí/No | Sí | Eventos pueden superponerse en una pista |
| Amplitud | 0.0 – 1.0 | 0.3 – 1.0 | Rango de volumen por evento |
| Pan | -1.0 – 1.0 | -1.0 – 1.0 | Rango de paneo estéreo |
| Fade in | 0.001 – 2.0 s | 0.01 – 0.5 s | Rango de fundido de entrada |
| Fade out | 0.001 – 2.0 s | 0.01 – 1.0 s | Rango de fundido de salida |
| Probabilidad de efectos | 0.0 – 1.0 | 0.7 | Probabilidad de aplicar efectos a cada evento |
| Max efectos por evento | 1 – 10 | 3 | Cadena máxima de efectos |
| Curva de densidad | constant, crescendo, decrescendo, arc, wave | constant | Distribución temporal de la densidad de eventos |

#### 4 Estrategias de Composición

1. **Scatter** — Fragmentos dispersos aleatoriamente por el timeline. Resultado más caótico y puntillista. La densidad se modula según la curva seleccionada.

2. **Structured** — Timeline dividido en secciones (sparse, medium, dense, climax, silence) con transiciones por cadena de Markov. Balance entre estructura y azar.

3. **Layer** — Cada track es una transformación continua de una sola fuente (segmentos largos y solapados). Ideal para texturas y drones.

4. **Canon** — Material base generado en Track 1, copiado a los demás tracks con offset temporal progresivo y efectos acumulativos. Produce estructuras canónicas.

#### Aleatoriedad Controlada (RNG)
- Semilla maestra para reproducibilidad total (mismo seed = mismo resultado)
- Distribuciones: uniforme, gaussiana con clamp, weighted choice, Van der Corput (quasi-random), Markov
- Fork de RNG: cada track tiene su propio sub-generador (un track no afecta a otro)
- Botón "Re-roll" para generar variaciones rápidamente

### Efectos de Audio (18 efectos)

#### Efectos Clásicos (via Pedalboard)
| Efecto | Parámetros |
|--------|-----------|
| **Reverb** | room_size, damping, wet_level, dry_level, width |
| **Delay** | delay_seconds, feedback, mix |
| **Pitch Shift** | semitones (-24 a +24) |
| **Distortion** | drive_db |
| **Compressor** | threshold_db, ratio, attack_ms, release_ms |
| **Gain** | gain_db |
| **Limiter** | threshold_db, release_ms |
| **Chorus** | rate_hz, depth, mix |
| **Phaser** | rate_hz, depth, mix |
| **Highpass Filter** | cutoff_frequency_hz |
| **Lowpass Filter** | cutoff_frequency_hz |
| **Bitcrush** | bit_depth |

#### Efectos Experimentales (custom numpy/scipy/librosa)
| Efecto | Descripción | Parámetros |
|--------|-------------|-----------|
| **Granular Synthesis** | Descompone audio en micro-granos y los reensambla | grain_size_ms, grain_density, grain_scatter, position_random, pitch_random, amplitude_random, reverse_probability, window_type |
| **Spectral Freeze** | Congela el espectro en un punto → drone sostenido | freeze_position, output_duration |
| **Spectral Smear** | Difumina el espectrograma con blur gaussiano | smear_amount, time_smear |
| **Spectral Gate** | Elimina componentes espectrales débiles | threshold |
| **Spectral Shift** | Desplaza bins de frecuencia arriba/abajo | shift_bins |
| **Time Stretch** | Cambia duración sin alterar pitch (phase vocoder) | rate |

### Render y Exportación

- **Render en background**: No congela la interfaz (QThreadPool)
- **Barra de progreso**: Muestra avance del render en tiempo real (0-100%)
- **Sample rate**: 44,100 Hz
- **Mezcla estéreo**: Paneo por evento con constant-power panning
- **Soft-clip**: Limitador final via tanh para evitar distorsión digital
- **Formatos de exportación**:
  - WAV (vía soundfile)
  - MP3 (vía pydub + FFmpeg)
  - FLAC (vía soundfile)

### Interfaz Gráfica

#### Layout
- **3 zonas redimensionables** con QSplitter:
  - Izquierda: Panel de fuentes (~300px)
  - Derecha: Tabs (Composición / Effects Palette)
  - Inferior: Timeline + Mixer

#### Tema Oscuro
- Fondo principal: #1e1e2e (gris oscuro azulado)
- Acento primario: #7c6ff0 (púrpura/lavanda)
- Acento secundario: #4ecdc4 (turquesa)
- 8 colores para tracks/fuentes

#### Panel de Fuentes
- Lista de archivos con waveform mini (QPainter)
- Sliders de peso por fuente
- Botones de añadir/quitar archivos
- Info: duración, canales, sample rate

#### Panel de Composición
- Controles organizados en secciones: General, Timing, Dinámica, Efectos, Estructura
- Range sliders dobles para parámetros min/max
- Visualización de curva de densidad
- Botones Compose y Re-roll

#### Effects Palette
- Selector de efecto (ComboBox con 18 efectos)
- Controles dinámicos por efecto (sliders con rango apropiado)
- Parámetros con nombres legibles y valores decimales ajustables

#### Timeline
- **Canvas** pintado con QPainter: regla temporal, carriles por track, eventos como rectángulos coloreados
- **Mixer strips**: por track con nombre, Mute (M), Solo (S), volumen vertical, pan horizontal
- **Zoom**: Ctrl+Scroll para zoom temporal
- **Scroll**: Scroll horizontal para navegar el timeline
- **Auto-zoom**: Se ajusta automáticamente al generar composición
- **Stats bar**: Número de eventos, duración, tracks, seed

#### Barra de Transporte
- Botón Render (con estado: "Rendering…" durante proceso)
- Barra de progreso
- Botones Export WAV y Export MP3

### Atajos de Teclado
| Atajo | Acción |
|-------|--------|
| Ctrl+O | Añadir archivos de audio |
| Ctrl+E | Exportar render |
| Ctrl+G | Componer |
| Ctrl+R | Re-roll |
| Ctrl+Q | Salir |

---

## Arquitectura Técnica

### Stack
- **Python 3.10+**
- **PySide6** — GUI de escritorio (Qt 6)
- **pedalboard** (Spotify) — Efectos de audio de calidad estudio
- **librosa** — Análisis espectral, STFT, phase vocoder
- **numpy / scipy** — DSP custom, síntesis granular
- **soundfile** — I/O WAV/FLAC
- **pydub** — Exportación MP3 (requiere FFmpeg)

### Estructura del Proyecto
```
src/
├── main.py                         # Entry point
├── core/                           # Motor (independiente de GUI)
│   ├── audio_buffer.py             # AudioBuffer inmutable
│   ├── audio_io.py                 # Carga/guardado de archivos
│   ├── effects/
│   │   ├── base.py                 # ABC Effect
│   │   ├── pedalboard_effects.py   # 12 efectos + registry
│   │   ├── granular.py             # Síntesis granular
│   │   ├── spectral.py             # 4 efectos espectrales
│   │   ├── time_stretch.py         # Phase vocoder
│   │   └── chain.py                # Cadena de efectos
│   ├── composition/
│   │   ├── rng.py                  # RNG controlable con semilla
│   │   ├── constraints.py          # Parámetros de composición
│   │   ├── timeline.py             # AudioEvent, Track, Composition
│   │   ├── strategies.py           # 4 estrategias
│   │   └── arranger.py             # Orquestador
│   └── render/
│       ├── mixer.py                # Mezcla multipista
│       ├── renderer.py             # Pipeline de render
│       └── exporter.py             # Export WAV/MP3/FLAC
├── gui/
│   ├── main_window.py              # Ventana principal
│   ├── widgets/
│   │   ├── source_panel.py         # Panel de fuentes
│   │   ├── composition_panel.py    # Controles de composición
│   │   ├── effects_panel.py        # Paleta de efectos
│   │   ├── timeline_view.py        # Timeline + mixer
│   │   ├── waveform_view.py        # Visualización waveform
│   │   └── parameter_controls.py   # Sliders/controles reutilizables
│   └── styles/
│       └── theme.py                # Tema oscuro
└── tests/
    ├── test_end_to_end.py
    └── test_advanced_effects.py
```

### Patrones de Diseño
- **AudioBuffer inmutable**: Los efectos retornan nuevos buffers via `with_samples()`, previniendo mutaciones
- **Effect ABC**: Interfaz común con `process()`, `get_parameters()`, `set_parameters()`, `serialize()`
- **EFFECTS_REGISTRY**: Diccionario central que mapea nombres a factory functions
- **Strategy Pattern**: 4 estrategias intercambiables que implementan `CompositionStrategy`
- **Background rendering**: QRunnable/QThreadPool para no bloquear la GUI
- **Signal/Slot**: Comunicación desacoplada entre widgets Qt

---

## Requisitos del Sistema
- Python 3.10 o superior
- FFmpeg instalado y en PATH (para exportar MP3)
- Sistema operativo: Windows, macOS o Linux

## Instalación
```bash
cd 2026fundamental
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
```

## Ejecución
```bash
python -m src.main
```
