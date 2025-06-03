# 📊 PUNKT 3: HILFSFUNKTIONEN
# Gemeinsame Utility-Funktionen für alle Module

import os
import json
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from Punkt3_settings import CONFIG

class FileUtils:
    """Datei-bezogene Hilfsfunktionen"""

    @staticmethod
    def scan_punkt2_files() -> Dict[str, Any]:
        """Scannt data/punkt2/ nach verfügbaren Multi-Timeframe UND Single-Timeframe Dateien"""
        files = {}
        punkt2_dir = CONFIG.PATHS['punkt2_dir']

        if not os.path.exists(punkt2_dir):
            logging.warning(f"Punkt 2 Verzeichnis nicht gefunden: {punkt2_dir}")
            return files

        try:
            # 1. MULTI-TIMEFRAME DATEIEN (mit Metadata)
            metadata_files = [f for f in os.listdir(punkt2_dir) if f.endswith('_metadata.json') or f.endswith('_ULTRA_PERFORMANCE_metadata.json')]

            for metadata_file in metadata_files:
                try:
                    metadata_path = os.path.join(punkt2_dir, metadata_file)
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

                    # Extrahiere Base-Name (verschiedene Metadata-Suffixe)
                    if metadata_file.endswith('_ULTRA_PERFORMANCE_metadata.json'):
                        base_name = metadata_file.replace('_ULTRA_PERFORMANCE_metadata.json', '')
                    else:
                        base_name = metadata_file.replace('_metadata.json', '')

                    # Prüfe Daten-Dateien (H5 und VBT Pickle)
                    data_files = []
                    total_size = 0
                    for tf in metadata.get('timeframes', []):
                        # Prüfe verschiedene Datei-Formate
                        possible_files = [
                            f"{base_name}_{tf}_VBT.pickle",  # VBT Pickle (bevorzugt)
                            f"{base_name}_{tf}_VBT.h5",      # VBT H5
                            f"{base_name}_{tf}.h5",          # Standard H5
                            f"{base_name}_{tf}.pickle"       # Standard Pickle
                        ]

                        for data_file in possible_files:
                            data_path = os.path.join(punkt2_dir, data_file)
                            if os.path.exists(data_path):
                                data_files.append(data_file)
                                total_size += os.path.getsize(data_path)
                                break  # Nur erste gefundene Datei pro Timeframe

                    if data_files:
                        files[base_name] = {
                            'type': 'multi_timeframe',
                            'metadata_file': metadata_file,
                            'metadata_path': metadata_path,
                            'metadata': metadata,
                            'data_files': data_files,  # Kann H5 oder Pickle sein
                            'h5_files': [f for f in data_files if f.endswith('.h5')],  # Für Kompatibilität
                            'timeframes': metadata.get('timeframes', []),
                            'created_at': metadata.get('created_at', 'Unbekannt'),
                            'original_file': metadata.get('original_file', 'Unbekannt'),
                            'file_size_mb': total_size / (1024 * 1024),
                            'record_count': metadata.get('total_records', 0)
                        }

                except Exception as e:
                    logging.error(f"Fehler beim Lesen von {metadata_file}: {e}")

            # 2. SINGLE-TIMEFRAME DATEIEN (H5 und Pickle ohne Metadata)
            all_files = os.listdir(punkt2_dir)
            data_files = [f for f in all_files if f.endswith(('.h5', '.pickle')) and not any(f.startswith(base) for base in files.keys())]

            for data_file in data_files:
                try:
                    data_path = os.path.join(punkt2_dir, data_file)
                    file_size = os.path.getsize(data_path)

                    # Extrahiere Timeframe aus Dateiname (falls vorhanden)
                    base_name = data_file.replace('.h5', '').replace('.pickle', '')

                    # Versuche Timeframe zu erkennen
                    timeframe = FileUtils._extract_timeframe_from_filename(base_name)
                    if not timeframe:
                        timeframe = "1m"  # Default Timeframe

                    # Erstelle Pseudo-Metadata
                    files[base_name] = {
                        'type': 'single_timeframe',
                        'data_file': data_file,
                        'data_path': data_path,
                        'timeframes': [timeframe],
                        'created_at': datetime.fromtimestamp(os.path.getctime(data_path)).isoformat(),
                        'original_file': data_file,
                        'file_size_mb': file_size / (1024 * 1024),
                        'record_count': 0  # Wird beim Laden ermittelt
                    }

                except Exception as e:
                    logging.error(f"Fehler beim Verarbeiten von {data_file}: {e}")

        except Exception as e:
            logging.error(f"Fehler beim Scannen von {punkt2_dir}: {e}")

        logging.info(f"Gefunden: {len(files)} Punkt 2 Dateien (Multi + Single Timeframe)")
        return files

    @staticmethod
    def _extract_timeframe_from_filename(filename: str) -> Optional[str]:
        """Extrahiert Timeframe aus Dateiname"""
        import re

        # Bekannte Timeframe-Patterns
        patterns = [
            r'_(\d+m)(?:_|$)',      # _5m_, _1m_
            r'_(\d+h)(?:_|$)',      # _1h_, _4h_
            r'_(\d+d)(?:_|$)',      # _1d_, _3d_
            r'_(\d+w)(?:_|$)',      # _1w_
            r'(\d+min)',            # 5min, 15min
            r'(\d+hour)',           # 1hour, 4hour
            r'(\d+day)',            # 1day
        ]

        for pattern in patterns:
            match = re.search(pattern, filename.lower())
            if match:
                tf = match.group(1)
                # Normalisiere Timeframe-Format
                if 'min' in tf:
                    tf = tf.replace('min', 'm')
                elif 'hour' in tf:
                    tf = tf.replace('hour', 'h')
                elif 'day' in tf:
                    tf = tf.replace('day', 'd')
                return tf

        return None

    @staticmethod
    def validate_punkt2_file(file_path: str) -> Tuple[bool, str, Dict]:
        """Validiert eine Punkt 2 Datei (Metadata oder direkte Daten-Datei)"""
        try:
            if not os.path.exists(file_path):
                return False, "Datei existiert nicht", {}

            # 1. METADATA-DATEI (Multi-Timeframe)
            if file_path.endswith('_metadata.json') or file_path.endswith('_ULTRA_PERFORMANCE_metadata.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                # Prüfe erforderliche Felder
                required_fields = ['timeframes', 'created_at']
                for field in required_fields:
                    if field not in metadata:
                        return False, f"Fehlendes Feld: {field}", {}

                # Prüfe Timeframes
                timeframes = metadata['timeframes']
                if not timeframes or not isinstance(timeframes, list):
                    return False, "Keine gültigen Timeframes", {}

                # Prüfe Daten-Dateien
                if file_path.endswith('_ULTRA_PERFORMANCE_metadata.json'):
                    base_name = os.path.basename(file_path).replace('_ULTRA_PERFORMANCE_metadata.json', '')
                else:
                    base_name = os.path.basename(file_path).replace('_metadata.json', '')
                punkt2_dir = os.path.dirname(file_path)

                missing_files = []
                for tf in timeframes:
                    # Prüfe verschiedene Datei-Formate
                    possible_files = [
                        f"{base_name}_{tf}_VBT.pickle",  # VBT Pickle (bevorzugt)
                        f"{base_name}_{tf}_VBT.h5",      # VBT H5
                        f"{base_name}_{tf}.h5",          # Standard H5
                        f"{base_name}_{tf}.pickle"       # Standard Pickle
                    ]

                    found = False
                    for data_file in possible_files:
                        data_path = os.path.join(punkt2_dir, data_file)
                        if os.path.exists(data_path):
                            found = True
                            break

                    if not found:
                        missing_files.append(f"{base_name}_{tf}.*")

                if missing_files:
                    return False, f"Fehlende Daten-Dateien: {', '.join(missing_files)}", metadata

                return True, "Multi-Timeframe Datei ist gültig", metadata

            # 2. DIREKTE DATEN-DATEI (Single-Timeframe)
            elif file_path.endswith(('.h5', '.pickle')):
                # Versuche Datei zu laden um Gültigkeit zu prüfen
                try:
                    if file_path.endswith('.h5'):
                        import pandas as pd
                        data = pd.read_hdf(file_path, key='data')
                    elif file_path.endswith('.pickle'):
                        try:
                            import vectorbtpro as vbt
                            vbt_data = vbt.Data.load(file_path)
                            data = vbt_data.get()
                        except:
                            import pickle
                            with open(file_path, 'rb') as f:
                                data = pickle.load(f)

                    # Prüfe OHLCV Spalten
                    required_cols = ['open', 'high', 'low', 'close']
                    missing_cols = [col for col in required_cols if col not in data.columns]
                    if missing_cols:
                        return False, f"Fehlende OHLCV Spalten: {', '.join(missing_cols)}", {}

                    # Erstelle Pseudo-Metadata
                    base_name = os.path.basename(file_path).replace('.h5', '').replace('.pickle', '')
                    timeframe = FileUtils._extract_timeframe_from_filename(base_name) or "1m"

                    pseudo_metadata = {
                        'type': 'single_timeframe',
                        'timeframes': [timeframe],
                        'created_at': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                        'original_file': os.path.basename(file_path),
                        'record_count': len(data),
                        'columns': list(data.columns)
                    }

                    return True, "Single-Timeframe Datei ist gültig", pseudo_metadata

                except Exception as e:
                    return False, f"Datei kann nicht geladen werden: {e}", {}

            else:
                return False, "Unbekanntes Dateiformat (erwartet: .json, .h5, .pickle)", {}

        except json.JSONDecodeError:
            return False, "Ungültiges JSON-Format", {}
        except Exception as e:
            return False, f"Fehler beim Validieren: {e}", {}

    @staticmethod
    def get_file_info(file_path: str) -> str:
        """Gibt formatierte Datei-Informationen zurück"""
        try:
            size = os.path.getsize(file_path)
            size_mb = size / (1024 * 1024)
            modified = datetime.fromtimestamp(os.path.getmtime(file_path))

            return f"Größe: {size_mb:.1f} MB | Geändert: {modified.strftime('%d.%m.%Y %H:%M')}"
        except Exception:
            return "Datei-Info nicht verfügbar"

class IndicatorUtils:
    """Indikator-bezogene Hilfsfunktionen"""

    @staticmethod
    def create_display_name(name: str, params: Dict) -> str:
        """Erstellt Anzeige-Namen für Indikator"""
        if not params:
            return name

        param_values = list(params.values())
        if param_values:
            return f"{name}({','.join(map(str, param_values))})"
        return name

    @staticmethod
    def validate_indicator_params(params: Dict, param_names: List[str]) -> Tuple[bool, str]:
        """Validiert Indikator-Parameter"""
        try:
            for param_name in param_names:
                if param_name not in params:
                    return False, f"Fehlender Parameter: {param_name}"

                value = params[param_name]

                # Versuche numerische Konvertierung
                if isinstance(value, str):
                    try:
                        if '.' in value:
                            float(value)
                        else:
                            int(value)
                    except ValueError:
                        # String-Parameter sind auch OK
                        pass

            return True, "Parameter sind gültig"

        except Exception as e:
            return False, f"Fehler bei Parameter-Validierung: {e}"

    @staticmethod
    def get_indicator_categories() -> List[str]:
        """Gibt alle verfügbaren Indikator-Kategorien zurück"""
        return CONFIG.INDICATOR_CATEGORIES

    @staticmethod
    def filter_indicators(indicators: Dict, search_term: str = "",
                         library_filter: str = "Alle",
                         category_filter: str = "Alle") -> Dict:
        """Filtert Indikatoren basierend auf Kriterien"""
        filtered = {}

        for library, lib_indicators in indicators.items():
            # Bibliothek-Filter
            if library_filter != "Alle" and library != library_filter:
                continue

            filtered_lib = {}
            for name, info in lib_indicators.items():
                # Such-Filter
                if search_term and search_term.lower() not in name.lower():
                    continue

                # Kategorie-Filter
                if category_filter != "Alle" and info.get("category", "") != category_filter:
                    continue

                filtered_lib[name] = info

            if filtered_lib:
                filtered[library] = filtered_lib

        return filtered

class ScrollableFrame:
    """Scrollbares Frame für große Inhalte"""

    def __init__(self, parent):
        # Hauptframe
        self.main_frame = tk.Frame(parent)

        # Canvas für Scrolling
        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0)

        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.canvas.xview)

        # Scrollbares Frame
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Canvas konfigurieren
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Grid-Layout
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Grid-Konfiguration
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Scrollbares Frame in Canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Event-Bindings
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Keyboard-Scrolling
        self.canvas.bind("<Key>", self.on_key_press)
        self.canvas.focus_set()

    def on_frame_configure(self, event=None):
        """Wird aufgerufen wenn Frame-Größe sich ändert"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event=None):
        """Wird aufgerufen wenn Canvas-Größe sich ändert"""
        # Frame-Breite an Canvas anpassen
        canvas_width = self.canvas.winfo_width()
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)

    def on_mousewheel(self, event):
        """Mausrad-Scrolling"""
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_key_press(self, event):
        """Keyboard-Scrolling"""
        if event.keysym == "Up":
            self.canvas.yview_scroll(-1, "units")
        elif event.keysym == "Down":
            self.canvas.yview_scroll(1, "units")
        elif event.keysym == "Page_Up":
            self.canvas.yview_scroll(-1, "pages")
        elif event.keysym == "Page_Down":
            self.canvas.yview_scroll(1, "pages")
        elif event.keysym == "Home":
            self.canvas.yview_moveto(0)
        elif event.keysym == "End":
            self.canvas.yview_moveto(1)

    def get_frame(self):
        """Gibt das scrollbare Frame zurück"""
        return self.scrollable_frame

    def get_main_frame(self):
        """Gibt das Haupt-Frame zurück"""
        return self.main_frame

    def scroll_to_top(self):
        """Scrollt nach oben"""
        self.canvas.yview_moveto(0)

    def scroll_to_bottom(self):
        """Scrollt nach unten"""
        self.canvas.yview_moveto(1)

class UIUtils:
    """UI-bezogene Hilfsfunktionen"""

    @staticmethod
    def center_window(window, width: int, height: int):
        """Zentriert Fenster auf dem Bildschirm"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")

    @staticmethod
    def show_error(title: str, message: str):
        """Zeigt Fehler-Dialog - DEAKTIVIERT"""
        print(f"❌ {title}: {message}")

    @staticmethod
    def show_warning(title: str, message: str):
        """Zeigt Warnung-Dialog - DEAKTIVIERT"""
        print(f"⚠️ {title}: {message}")

    @staticmethod
    def show_info(title: str, message: str):
        """Zeigt Info-Dialog - DEAKTIVIERT"""
        print(f"ℹ️ {title}: {message}")

    @staticmethod
    def ask_yes_no(title: str, message: str) -> bool:
        """Zeigt Ja/Nein-Dialog - DEAKTIVIERT, gibt immer True zurück"""
        print(f"❓ {title}: {message} -> Auto-Ja")
        return True

    @staticmethod
    def create_tooltip(widget, text: str):
        """Erstellt Tooltip für Widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(tooltip, text=text, background="lightyellow",
                           relief="solid", borderwidth=1, font=CONFIG.FONTS['small'])
            label.pack()

            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    @staticmethod
    def configure_treeview_columns(treeview, columns: Dict[str, int]):
        """Konfiguriert Treeview-Spalten"""
        for col_name, width in columns.items():
            if col_name == '#0':
                treeview.column('#0', width=width)
            else:
                treeview.column(col_name, width=width)

class ValidationUtils:
    """Validierungs-Hilfsfunktionen"""

    @staticmethod
    def validate_timeframe_selection(timeframes: List[str], mode: str) -> Tuple[bool, str]:
        """Validiert Timeframe-Auswahl"""
        if not timeframes:
            return False, "Keine Timeframes ausgewählt"

        if mode == "single" and len(timeframes) > 1:
            return False, "Im Single-Modus nur ein Timeframe erlaubt"

        return True, "Timeframe-Auswahl ist gültig"

    @staticmethod
    def validate_indicator_selection(indicators: List[Dict]) -> Tuple[bool, str]:
        """Validiert Indikator-Auswahl"""
        if not indicators:
            return False, "Keine Indikatoren ausgewählt"

        # Prüfe auf Duplikate
        seen = set()
        for indicator in indicators:
            key = f"{indicator.get('library', '')}.{indicator.get('name', '')}.{indicator.get('display_name', '')}"
            if key in seen:
                return False, f"Duplikat gefunden: {indicator.get('display_name', 'Unbekannt')}"
            seen.add(key)

        return True, "Indikator-Auswahl ist gültig"

    @staticmethod
    def validate_configuration(config: Dict) -> Tuple[bool, List[str]]:
        """Validiert komplette Konfiguration"""
        errors = []

        # Datei-Validierung
        if not config.get('metadata_file'):
            errors.append("Keine Metadaten-Datei ausgewählt")

        # Timeframe-Validierung
        timeframes = config.get('selected_timeframes', [])
        mode = config.get('timeframe_mode', 'single')
        valid, msg = ValidationUtils.validate_timeframe_selection(timeframes, mode)
        if not valid:
            errors.append(f"Timeframes: {msg}")

        # Indikator-Validierung
        indicators = config.get('selected_indicators', [])
        valid, msg = ValidationUtils.validate_indicator_selection(indicators)
        if not valid:
            errors.append(f"Indikatoren: {msg}")

        # Visualisierung-Validierung
        if not config.get('visualization_mode'):
            errors.append("Keine Visualisierung ausgewählt")

        if not config.get('visualization_period'):
            errors.append("Kein Visualisierungs-Zeitraum ausgewählt")

        return len(errors) == 0, errors

class IndicatorUtils:
    """Indikator-bezogene Hilfsfunktionen"""

    @staticmethod
    def create_display_name(name: str, params: Dict) -> str:
        """Erstellt Anzeige-Namen für Indikator"""
        if not params:
            return name

        # Kurze Parameter-Liste für Display-Name
        param_str = ", ".join([f"{k}={v}" for k, v in params.items()])
        return f"{name}({param_str})"

    @staticmethod
    def validate_parameters(params: Dict, param_names: List[str], defaults: List) -> Tuple[bool, str]:
        """Validiert Indikator-Parameter"""
        if not param_names:
            return True, "Keine Parameter erforderlich"

        for param_name in param_names:
            if param_name not in params:
                return False, f"Parameter '{param_name}' fehlt"

        return True, "Parameter sind gültig"

    @staticmethod
    def get_parameter_info(indicator_info: Dict) -> Tuple[List[str], List]:
        """Extrahiert Parameter-Informationen"""
        param_names = indicator_info.get("params", [])
        defaults = indicator_info.get("defaults", [])

        # Sicherstellen dass Listen gleich lang sind
        while len(defaults) < len(param_names):
            defaults.append(None)

        return param_names, defaults

    @staticmethod
    def filter_indicators(all_indicators: Dict, search_term: str = "", library_filter: str = "Alle", category_filter: str = "Alle") -> Dict:
        """Filtert Indikatoren basierend auf Suchterm, Bibliothek und Kategorie"""
        filtered = {}

        for library, indicators in all_indicators.items():
            # Bibliotheks-Filter
            if library_filter != "Alle" and library != library_filter:
                continue

            filtered_lib_indicators = {}

            for name, info in indicators.items():
                # Such-Filter
                if search_term and search_term.lower() not in name.lower():
                    continue

                # Kategorie-Filter
                if category_filter != "Alle" and info.get("category", "") != category_filter:
                    continue

                filtered_lib_indicators[name] = info

            if filtered_lib_indicators:
                filtered[library] = filtered_lib_indicators

        return filtered

class FormatUtils:
    """Formatierungs-Hilfsfunktionen"""

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Formatiert Dateigröße"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    @staticmethod
    def format_timestamp(timestamp: str) -> str:
        """Formatiert Zeitstempel"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%d.%m.%Y %H:%M")
        except Exception:
            return timestamp[:19] if len(timestamp) >= 19 else timestamp

    @staticmethod
    def format_number(number: float, decimals: int = 2) -> str:
        """Formatiert Zahlen"""
        return f"{number:.{decimals}f}"

    @staticmethod
    def truncate_text(text: str, max_length: int = 50) -> str:
        """Kürzt Text mit Ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

# Logging konfigurieren
logging.basicConfig(
    level=getattr(logging, CONFIG.LOGGING['level']),
    format=CONFIG.LOGGING['format']
)
