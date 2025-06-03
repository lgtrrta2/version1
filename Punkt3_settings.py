# 📊 PUNKT 3: KONFIGURATION
# Zentrale Konfigurationsdatei für alle Module

import os
import json
from datetime import datetime

class Punkt3Settings:
    """Zentrale Konfiguration für Punkt 3"""

    # Anwendungs-Info
    APP_NAME = "VectorBT Pro - Punkt 3 Konfigurator"
    APP_VERSION = "2.0.0"
    APP_TITLE = "📊 PUNKT 3: KONFIGURATOR (MODULAR)"

    # Fenster-Konfiguration
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    WINDOW_MIN_WIDTH = 1200
    WINDOW_MIN_HEIGHT = 700

    # Farben und Design
    COLORS = {
        'primary': '#2E8B57',      # Grün
        'secondary': '#4169E1',    # Blau
        'warning': '#FF8C00',      # Orange
        'error': '#DC143C',        # Rot
        'success': '#2E8B57',      # Grün
        'info': '#666666',         # Grau
        'background': '#f0f0f0',   # Heller Hintergrund
        'code_bg': '#1e1e1e',      # Dunkler Code-Hintergrund
        'code_fg': '#ffffff'       # Weiße Code-Schrift
    }

    # Schriftarten
    FONTS = {
        'title': ('Arial', 18, 'bold'),
        'heading': ('Arial', 12, 'bold'),
        'normal': ('Arial', 10),
        'small': ('Arial', 9),
        'code': ('Consolas', 9)
    }

    # Pfade
    PATHS = {
        'punkt2_dir': 'data/punkt2',
        'punkt3_dir': 'data/punkt3',
        'backup_dir': 'data/backups',
        'export_dir': 'exports'
    }

    # Datei-Patterns
    FILE_PATTERNS = {
        'metadata': '*_metadata.json',
        'h5_data': '*.h5',
        'python_code': '*.py',
        'json_export': '*.json'
    }

    # Standard-Werte
    DEFAULTS = {
        'timeframe_mode': 'single',
        'visualization_mode': 'Interaktive Charts mit Indikatoren',
        'visualization_period': '1 Woche (2016 Kerzen)',
        'save_punkt4': True,
        'save_backup': True,
        'save_charts': False,
        'show_summary': True,
        'multi_indicator_mode': 'same'
    }

    # Visualisierungs-Optionen
    VISUALIZATION_MODES = [
        "Interaktive Charts mit Indikatoren",
        "Normale Charts mit Indikatoren",
        "Nur Daten-Tabellen",
        "Charts + Tabellen",
        "Keine Visualisierung"
    ]

    # Zeitraum-Optionen
    VISUALIZATION_PERIODS = [
        "1 Tag (288 Kerzen bei 5m)",
        "2 Tage (576 Kerzen)",
        "3 Tage (864 Kerzen)",
        "1 Woche (2016 Kerzen)",
        "2 Wochen (4032 Kerzen)",
        "4 Wochen (8064 Kerzen)",
        "8 Wochen (16128 Kerzen)",
        "12 Wochen (24192 Kerzen)",
        "20 Wochen (40320 Kerzen)",
        "52 Wochen (104832 Kerzen)",
        "Alle Daten"
    ]

    # Indikator-Kategorien
    INDICATOR_CATEGORIES = [
        "Alle", "Trend", "Momentum", "Volatility", "Volume",
        "Pattern", "Statistical", "Math", "Price", "Cycle",
        "Smart Money", "Quantitative", "Technical", "Utility", "Numpy"
    ]

    # Standard-Indikator-Sets
    INDICATOR_SETS = {
        'standard': [
            {"library": "talib", "name": "SMA", "params": {"timeperiod": 20}},
            {"library": "talib", "name": "SMA", "params": {"timeperiod": 50}},
            {"library": "talib", "name": "EMA", "params": {"timeperiod": 12}},
            {"library": "talib", "name": "RSI", "params": {"timeperiod": 14}},
            {"library": "talib", "name": "MACD", "params": {"fastperiod": 12, "slowperiod": 26, "signalperiod": 9}}
        ],
        'trend': [
            {"library": "talib", "name": "SMA", "params": {"timeperiod": 10}},
            {"library": "talib", "name": "SMA", "params": {"timeperiod": 20}},
            {"library": "talib", "name": "SMA", "params": {"timeperiod": 50}},
            {"library": "talib", "name": "EMA", "params": {"timeperiod": 12}},
            {"library": "talib", "name": "EMA", "params": {"timeperiod": 26}},
            {"library": "talib", "name": "BBANDS", "params": {"timeperiod": 20, "nbdevup": 2, "nbdevdn": 2}}
        ],
        'momentum': [
            {"library": "talib", "name": "RSI", "params": {"timeperiod": 14}},
            {"library": "talib", "name": "MACD", "params": {"fastperiod": 12, "slowperiod": 26, "signalperiod": 9}},
            {"library": "talib", "name": "STOCH", "params": {"fastkperiod": 5, "slowkperiod": 3, "slowdperiod": 3}},
            {"library": "talib", "name": "ADX", "params": {"timeperiod": 14}}
        ]
    }

    # GUI-Layout Konfiguration
    GUI_CONFIG = {
        'tab_padding': 20,
        'frame_padding': 15,
        'button_width': 15,
        'entry_width': 25,
        'listbox_height': 8,
        'treeview_height': 15,
        'code_editor_height': 15,
        'code_editor_width': 80
    }

    # Event-Namen
    EVENTS = {
        'file_selected': 'file_selected',
        'timeframes_changed': 'timeframes_changed',
        'indicators_changed': 'indicators_changed',
        'visualization_changed': 'visualization_changed',
        'code_generated': 'code_generated',
        'status_changed': 'status_changed'
    }

    # Logging-Konfiguration
    LOGGING = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'punkt3.log',
        'max_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5
    }

    # Performance-Einstellungen
    PERFORMANCE = {
        'max_indicators_display': 1000,
        'lazy_loading': True,
        'cache_indicators': True,
        'debounce_search_ms': 300
    }

    @classmethod
    def get_timestamp(cls):
        """Gibt aktuellen Zeitstempel zurück"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    @classmethod
    def ensure_directories(cls):
        """Stellt sicher, dass alle benötigten Verzeichnisse existieren"""
        for path in cls.PATHS.values():
            os.makedirs(path, exist_ok=True)

    @classmethod
    def get_export_filename(cls, prefix, extension='.py'):
        """Generiert Dateinamen für Export"""
        timestamp = cls.get_timestamp()
        return f"{prefix}_{timestamp}{extension}"

    @classmethod
    def save_config(cls):
        """Speichert die aktuelle Konfiguration persistent"""
        config_file = 'punkt3_config.json'
        try:
            config_data = {
                'PATHS': cls.PATHS,
                'DEFAULTS': cls.DEFAULTS
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Fehler beim Speichern der Konfiguration: {e}")
            return False

    @classmethod
    def load_config(cls):
        """Lädt die gespeicherte Konfiguration"""
        config_file = 'punkt3_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Aktualisiere PATHS
                if 'PATHS' in config_data:
                    old_punkt2_dir = cls.PATHS.get('punkt2_dir', 'N/A')
                    cls.PATHS.update(config_data['PATHS'])
                    new_punkt2_dir = cls.PATHS.get('punkt2_dir', 'N/A')
                    print(f"Konfiguration geladen: punkt2_dir von '{old_punkt2_dir}' zu '{new_punkt2_dir}'")
                
                # Aktualisiere DEFAULTS
                if 'DEFAULTS' in config_data:
                    cls.DEFAULTS.update(config_data['DEFAULTS'])
                
                print(f"Konfiguration erfolgreich aus {config_file} geladen")
                return True
            except Exception as e:
                print(f"Fehler beim Laden der Konfiguration: {e}")
                return False
        else:
            print(f"Keine gespeicherte Konfiguration gefunden ({config_file})")
        return False

    @classmethod
    def validate_config(cls):
        """Validiert die Konfiguration"""
        errors = []

        # Prüfe Pfade
        for name, path in cls.PATHS.items():
            if not os.path.exists(path):
                try:
                    os.makedirs(path, exist_ok=True)
                except Exception as e:
                    errors.append(f"Kann Pfad {name} nicht erstellen: {e}")

        # Prüfe Standard-Werte
        required_defaults = ['timeframe_mode', 'visualization_mode', 'visualization_period']
        for key in required_defaults:
            if key not in cls.DEFAULTS:
                errors.append(f"Fehlender Standard-Wert: {key}")

        return errors

# Globale Konfiguration
CONFIG = Punkt3Settings()

# Gespeicherte Konfiguration laden
CONFIG.load_config()

# Verzeichnisse beim Import erstellen
CONFIG.ensure_directories()
