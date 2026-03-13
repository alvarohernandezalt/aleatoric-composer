"""Dark theme colors and QSS stylesheet."""

# Palette
BG_WINDOW = "#1e1e2e"
BG_PANEL = "#252536"
BG_CONTROL = "#2d2d44"
BG_INPUT = "#363650"
TEXT_PRIMARY = "#e0e0e0"
TEXT_SECONDARY = "#8888aa"
ACCENT = "#7c6ff0"
ACCENT2 = "#4ecdc4"
BORDER = "#3a3a55"
HOVER = "#3d3d5c"

# Track event colors (assigned per source)
TRACK_COLORS = [
    "#4ecdc4",  # turquoise
    "#ff6b6b",  # coral
    "#ffd93d",  # yellow
    "#6bcb77",  # green
    "#a78bfa",  # lavender
    "#f472b6",  # pink
    "#fb923c",  # orange
    "#38bdf8",  # sky blue
]

DARK_QSS = f"""
QMainWindow, QWidget {{
    background-color: {BG_WINDOW};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
}}

QGroupBox {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 18px;
    font-weight: bold;
    color: {TEXT_PRIMARY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {ACCENT};
}}

QPushButton {{
    background-color: {BG_CONTROL};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 6px 14px;
    min-height: 24px;
}}

QPushButton:hover {{
    background-color: {HOVER};
    border-color: {ACCENT};
}}

QPushButton:pressed {{
    background-color: {ACCENT};
    color: white;
}}

QPushButton#accent {{
    background-color: {ACCENT};
    color: white;
    font-weight: bold;
    border: none;
}}

QPushButton#accent:hover {{
    background-color: #8b7ff5;
}}

QComboBox {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 24px;
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT};
    border: 1px solid {BORDER};
}}

QSpinBox, QDoubleSpinBox {{
    background-color: {BG_INPUT};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 3px 6px;
    min-height: 22px;
}}

QSlider::groove:horizontal {{
    height: 4px;
    background: {BORDER};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: {ACCENT};
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}

QSlider::sub-page:horizontal {{
    background: {ACCENT};
    border-radius: 2px;
}}

QCheckBox {{
    color: {TEXT_PRIMARY};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER};
    border-radius: 3px;
    background: {BG_INPUT};
}}

QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}

QTabWidget::pane {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER};
    border-top: none;
}}

QTabBar::tab {{
    background-color: {BG_CONTROL};
    color: {TEXT_SECONDARY};
    padding: 8px 18px;
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border-bottom: 2px solid {ACCENT};
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background: {BG_WINDOW};
    width: 10px;
    border: none;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QLabel {{
    color: {TEXT_PRIMARY};
}}

QLabel#secondary {{
    color: {TEXT_SECONDARY};
    font-size: 11px;
}}

QProgressBar {{
    background-color: {BG_CONTROL};
    border: 1px solid {BORDER};
    border-radius: 4px;
    text-align: center;
    color: {TEXT_PRIMARY};
    min-height: 18px;
}}

QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 3px;
}}

QSplitter::handle {{
    background-color: {BORDER};
}}

QSplitter::handle:horizontal {{
    width: 3px;
}}

QSplitter::handle:vertical {{
    height: 3px;
}}

QListWidget {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 4px;
    outline: none;
}}

QListWidget::item {{
    padding: 4px;
    border-bottom: 1px solid {BORDER};
}}

QListWidget::item:selected {{
    background-color: {BG_CONTROL};
    border-left: 3px solid {ACCENT};
}}

QMenuBar {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border-bottom: 1px solid {BORDER};
}}

QMenuBar::item:selected {{
    background-color: {ACCENT};
}}

QMenu {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
}}

QMenu::item:selected {{
    background-color: {ACCENT};
}}
"""
