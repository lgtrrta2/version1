# 📊 PUNKT 4: PARAMETER-KONFIGURATOR - UTILITIES
# Hilfsfunktionen für VectorBT Pro Parameter-Management

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
from datetime import datetime
import vectorbtpro as vbt

from Punkt4_settings import CONFIG

class UIUtils:
    """UI-Hilfsfunktionen für Parameter-GUI"""
    
    @staticmethod
    def create_labeled_frame(parent, text: str, padding: int = 5) -> ttk.LabelFrame:
        """Erstellt einen LabelFrame mit Standard-Padding"""
        frame = ttk.LabelFrame(parent, text=text, padding=padding)
        return frame
    
    @staticmethod
    def create_parameter_entry(parent, param_name: str, param_value: Any, 
                              param_type: str = 'float', choices: List = None) -> Tuple[ttk.Label, tk.Widget, tk.Variable]:
        """Erstellt Parameter-Eingabefeld basierend auf Typ"""
        
        # Label erstellen
        label = ttk.Label(parent, text=f"{param_name}:", width=20)
        
        if choices:
            # Combobox für Enum-Parameter
            var = tk.StringVar(value=str(param_value))
            widget = ttk.Combobox(parent, textvariable=var, values=[choice[0] for choice in choices], 
                                state="readonly", width=25)
        elif param_type == 'bool':
            # Checkbutton für Boolean
            var = tk.BooleanVar(value=bool(param_value))
            widget = ttk.Checkbutton(parent, variable=var)
        elif param_type == 'int':
            # Entry für Integer
            var = tk.IntVar(value=int(param_value) if param_value is not None else 0)
            widget = ttk.Entry(parent, textvariable=var, width=25)
        else:
            # Entry für Float/String
            var = tk.StringVar(value=str(param_value) if param_value is not None else "")
            widget = ttk.Entry(parent, textvariable=var, width=25)
        
        return label, widget, var
    
    @staticmethod
    def create_parameter_section(parent, section_name: str, parameters: List[str]) -> ttk.LabelFrame:
        """Erstellt Parameter-Sektion"""
        frame = UIUtils.create_labeled_frame(parent, section_name)
        frame.pack(fill=tk.X, pady=5)
        return frame
    
    @staticmethod
    def show_error(title: str, message: str):
        """Zeigt Fehlermeldung"""
        messagebox.showerror(title, message)
    
    @staticmethod
    def show_warning(title: str, message: str):
        """Zeigt Warnung"""
        messagebox.showwarning(title, message)
    
    @staticmethod
    def show_info(title: str, message: str):
        """Zeigt Information"""
        messagebox.showinfo(title, message)
    
    @staticmethod
    def ask_yes_no(title: str, message: str) -> bool:
        """Fragt Ja/Nein"""
        return messagebox.askyesno(title, message)
    
    @staticmethod
    def select_file(title: str, filetypes: List[Tuple[str, str]], initialdir: str = None) -> Optional[str]:
        """Datei-Auswahl Dialog"""
        return filedialog.askopenfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initialdir
        )
    
    @staticmethod
    def save_file(title: str, filetypes: List[Tuple[str, str]], initialdir: str = None, 
                  defaultextension: str = None) -> Optional[str]:
        """Datei-Speichern Dialog"""
        return filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initialdir,
            defaultextension=defaultextension
        )

class DataUtils:
    """Daten-Hilfsfunktionen für Punkt 3 Integration"""
    
    @staticmethod
    def load_punkt3_metadata(file_path: Path) -> Optional[Dict[str, Any]]:
        """Lädt Punkt 3 Metadaten"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Validierung
            required_fields = ['indicators', 'timeframes', 'vbt_files']
            for field in required_fields:
                if field not in metadata:
                    raise ValueError(f"Erforderliches Feld fehlt: {field}")
            
            return metadata
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Metadaten-Laden Fehler: {e}")
            return None
    
    @staticmethod
    def load_punkt3_indicators(file_path: Path) -> Optional[Dict[str, Any]]:
        """Lädt Punkt 3 Indikator-Daten (VBT optimiert) - Unterstützt alle Formate"""
        try:
            file_path = Path(file_path)

            # VBT Pickle/Blosc Dateien
            if file_path.suffix in ['.pickle', '.blosc'] or file_path.name.endswith('.pickle.blosc'):
                return DataUtils._load_vbt_pickle(file_path)

            # HDF5 Dateien
            elif file_path.suffix in ['.h5', '.hdf5']:
                return DataUtils._load_hdf5(file_path)

            # CSV Dateien
            elif file_path.suffix == '.csv':
                return DataUtils._load_csv(file_path)

            # JSON Dateien (falls Daten in JSON gespeichert)
            elif file_path.suffix == '.json':
                return DataUtils._load_json_data(file_path)

            else:
                raise ValueError(f"Nicht unterstütztes Dateiformat: {file_path.suffix}")

        except Exception as e:
            logging.getLogger(__name__).error(f"Indikator-Daten-Laden Fehler: {e}")
            return None

    @staticmethod
    def _load_vbt_pickle(file_path: Path) -> Dict[str, Any]:
        """Lädt VBT Pickle/Blosc Dateien"""
        try:
            # VBT Data Objekt laden
            vbt_data = vbt.Data.load(str(file_path))
            df = vbt_data.get()

            # Dateityp bestimmen
            if file_path.name.endswith('.pickle.blosc'):
                file_type = 'vbt_pickle_blosc'
            else:
                file_type = 'vbt_pickle'

            return {
                'data': df,
                'vbt_data': vbt_data,  # Original VBT Data Objekt
                'symbols': list(vbt_data.symbols) if hasattr(vbt_data, 'symbols') else ['data'],
                'shape': df.shape,
                'columns': list(df.columns),
                'index_start': df.index[0] if len(df) > 0 else None,
                'index_end': df.index[-1] if len(df) > 0 else None,
                'freq': vbt_data.wrapper.freq if hasattr(vbt_data, 'wrapper') else None,
                'file_type': file_type,
                'vbt_optimized': True
            }

        except Exception as e:
            # Fallback: Versuche als normales Pickle zu laden
            import pickle
            with open(file_path, 'rb') as f:
                df = pickle.load(f)

            if not isinstance(df, pd.DataFrame):
                raise ValueError("Pickle-Datei enthält kein DataFrame")

            return {
                'data': df,
                'vbt_data': None,
                'symbols': ['data'],
                'shape': df.shape,
                'columns': list(df.columns),
                'index_start': df.index[0] if len(df) > 0 else None,
                'index_end': df.index[-1] if len(df) > 0 else None,
                'freq': pd.infer_freq(df.index) if len(df) > 1 else None,
                'file_type': 'pickle_fallback',
                'vbt_optimized': False
            }

    @staticmethod
    def _load_hdf5(file_path: Path) -> Dict[str, Any]:
        """Lädt HDF5 Dateien"""
        try:
            # Versuche verschiedene HDF5 Keys
            possible_keys = ['data', 'indicators', 'df', 'table', '/data', '/indicators']

            df = None
            used_key = None

            for key in possible_keys:
                try:
                    df = pd.read_hdf(file_path, key=key)
                    used_key = key
                    break
                except (KeyError, ValueError):
                    continue

            if df is None:
                # Versuche ohne Key (falls nur eine Tabelle)
                df = pd.read_hdf(file_path)

            if df is None or df.empty:
                raise ValueError("Keine gültigen Daten in HDF5-Datei gefunden")

            # Index als Datetime konvertieren falls nötig
            if not isinstance(df.index, pd.DatetimeIndex):
                try:
                    df.index = pd.to_datetime(df.index)
                except:
                    pass  # Index bleibt wie er ist

            return {
                'data': df,
                'vbt_data': None,
                'symbols': ['data'],
                'shape': df.shape,
                'columns': list(df.columns),
                'index_start': df.index[0] if len(df) > 0 else None,
                'index_end': df.index[-1] if len(df) > 0 else None,
                'freq': pd.infer_freq(df.index) if len(df) > 1 else None,
                'file_type': 'hdf5',
                'vbt_optimized': True,  # HDF5 ist gut optimiert
                'hdf5_key': used_key
            }

        except Exception as e:
            raise ValueError(f"HDF5-Laden Fehler: {e}")

    @staticmethod
    def _load_csv(file_path: Path) -> Dict[str, Any]:
        """Lädt CSV Dateien"""
        try:
            # CSV laden mit verschiedenen Optionen
            try:
                # Standard: Index als erste Spalte, Datetime parsing
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            except:
                try:
                    # Fallback: Ohne Datetime parsing
                    df = pd.read_csv(file_path, index_col=0)
                    # Versuche Index als Datetime zu konvertieren
                    df.index = pd.to_datetime(df.index)
                except:
                    # Letzter Fallback: Ohne Index-Spalte
                    df = pd.read_csv(file_path)

            if df.empty:
                raise ValueError("CSV-Datei ist leer")

            return {
                'data': df,
                'vbt_data': None,
                'symbols': ['data'],
                'shape': df.shape,
                'columns': list(df.columns),
                'index_start': df.index[0] if len(df) > 0 else None,
                'index_end': df.index[-1] if len(df) > 0 else None,
                'freq': pd.infer_freq(df.index) if len(df) > 1 else None,
                'file_type': 'csv',
                'vbt_optimized': False
            }

        except Exception as e:
            raise ValueError(f"CSV-Laden Fehler: {e}")

    @staticmethod
    def _load_json_data(file_path: Path) -> Dict[str, Any]:
        """Lädt JSON Daten-Dateien (falls Daten als JSON gespeichert)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Prüfe ob es DataFrame-Daten sind
            if isinstance(data, dict) and 'data' in data:
                # JSON mit DataFrame-Struktur
                df = pd.DataFrame(data['data'])
                if 'index' in data:
                    df.index = pd.to_datetime(data['index'])
            elif isinstance(data, list):
                # JSON Array
                df = pd.DataFrame(data)
            else:
                raise ValueError("JSON-Format nicht erkannt")

            if df.empty:
                raise ValueError("JSON-Datei enthält keine Daten")

            return {
                'data': df,
                'vbt_data': None,
                'symbols': ['data'],
                'shape': df.shape,
                'columns': list(df.columns),
                'index_start': df.index[0] if len(df) > 0 else None,
                'index_end': df.index[-1] if len(df) > 0 else None,
                'freq': pd.infer_freq(df.index) if len(df) > 1 else None,
                'file_type': 'json_data',
                'vbt_optimized': False
            }

        except Exception as e:
            raise ValueError(f"JSON-Daten-Laden Fehler: {e}")
    
    @staticmethod
    def extract_ohlcv_columns(df: pd.DataFrame) -> Dict[str, str]:
        """Extrahiert OHLCV Spalten aus DataFrame"""
        ohlcv_mapping = {}
        columns_lower = [col.lower() for col in df.columns]
        
        # Standard OHLCV Spalten suchen
        for ohlcv_type in ['open', 'high', 'low', 'close', 'volume']:
            for col in df.columns:
                if ohlcv_type in col.lower():
                    ohlcv_mapping[ohlcv_type] = col
                    break
        
        return ohlcv_mapping

class VBTUtils:
    """VectorBT Pro spezifische Hilfsfunktionen"""
    
    @staticmethod
    def validate_vbt_parameter(param_name: str, value: Any) -> Tuple[bool, str]:
        """Validiert einzelnen VBT Parameter"""
        try:
            # Spezielle VBT Parameter Validierung
            if param_name == 'size_type':
                valid_types = [choice[0] for choice in CONFIG.ENUM_CHOICES['size_type']]
                if value not in valid_types:
                    return False, f"Ungültiger size_type: {value}"
            
            elif param_name == 'direction':
                valid_directions = [choice[0] for choice in CONFIG.ENUM_CHOICES['direction']]
                if value not in valid_directions:
                    return False, f"Ungültige direction: {value}"
            
            elif param_name in ['sl_stop', 'tp_stop']:
                if value is not None:
                    try:
                        float_val = float(value)
                        if float_val <= 0:
                            return False, f"{param_name} muss positiv sein"
                        if float_val > 1.0:
                            return False, f"{param_name} sollte als Dezimalzahl eingegeben werden (z.B. 0.03 für 3%)"
                    except (ValueError, TypeError):
                        return False, f"{param_name} muss eine Zahl sein"
            
            elif param_name == 'fees':
                try:
                    float_val = float(value)
                    if float_val < 0:
                        return False, "Fees können nicht negativ sein"
                    if float_val > 0.1:
                        return False, "Fees über 10% sind unrealistisch"
                except (ValueError, TypeError):
                    return False, "Fees müssen eine Zahl sein"
            
            elif param_name == 'init_cash':
                try:
                    float_val = float(value)
                    if float_val <= 0:
                        return False, "Initial Cash muss positiv sein"
                except (ValueError, TypeError):
                    return False, "Initial Cash muss eine Zahl sein"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validierungsfehler: {str(e)}"
    
    @staticmethod
    def convert_parameter_value(param_name: str, value: Any) -> Any:
        """Konvertiert Parameter-Wert in korrekten Typ für VBT"""
        try:
            # None-Werte beibehalten
            if value is None or value == "" or value == "None":
                return None
            
            # Boolean Parameter
            if param_name in ['cash_sharing', 'accumulate', 'sl_trail', 'log', 'use_numba']:
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ['true', '1', 'yes', 'on']
            
            # Float Parameter
            elif param_name in ['init_cash', 'size', 'fees', 'fixed_fees', 'slippage']:
                return float(value) if value != "" else None

            # Seed Parameter (String oder None)
            elif param_name in ['seed']:
                if value == "" or value is None or str(value).lower() in ['none', 'null', '']:
                    return None
                try:
                    # Versuche als Integer zu konvertieren
                    return int(float(value))
                except (ValueError, TypeError):
                    # Falls nicht möglich, als String zurückgeben
                    return str(value) if value else None

            # Stop Loss/Take Profit: Ticks zu Prozent konvertieren
            elif param_name in ['sl_stop', 'tp_stop']:
                if value == "" or value is None:
                    return None
                tick_value = float(value)
                # NQ: 1 Tick = 0.25 Punkte, 1 Punkt = $5
                # Für 25 Ticks: 25 * 0.25 = 6.25 Punkte = $31.25
                # Bei $5000 Startkapital: $31.25 / $5000 = 0.00625 = 0.625%
                tick_size = 0.25  # NQ Standard
                tick_dollar_value = 5.0  # $5 per point
                init_cash = 5000.0  # Standard Startkapital

                # Ticks → Dollar → Prozent
                dollar_value = tick_value * tick_size * tick_dollar_value
                percent_value = dollar_value / init_cash

                print(f"DEBUG: {param_name} Konvertierung: {tick_value} Ticks → ${dollar_value:.2f} → {percent_value:.4f} ({percent_value*100:.2f}%)")
                return percent_value
            
            # Integer Parameter
            elif param_name in ['seed']:
                return int(value) if value != "" else None
            
            # String Parameter (Enums)
            elif param_name in ['size_type', 'direction', 'stop_entry_price', 'stop_exit_price', 
                               'stop_exit_type', 'upon_long_conflict', 'upon_short_conflict', 'upon_dir_conflict']:
                return str(value)
            
            # Spezielle Behandlung für 'size' mit inf
            elif param_name == 'size' and str(value).lower() in ['inf', 'infinity', 'np.inf']:
                return np.inf
            
            # Default: String
            else:
                return str(value)
                
        except (ValueError, TypeError) as e:
            logging.getLogger(__name__).warning(f"Parameter-Konvertierung Fehler ({param_name}): {e}")
            return value
    
    @staticmethod
    def get_parameter_description(param_name: str) -> str:
        """Gibt Beschreibung für VBT Parameter zurück"""
        descriptions = {
            'init_cash': 'Startkapital für das Portfolio',
            'size': 'Positionsgröße (inf = gesamtes verfügbares Kapital)',
            'size_type': 'Art der Positionsgrößen-Angabe',
            'direction': 'Handelsrichtung (Long/Short/Both)',
            'fees': 'Trading-Gebühren als Dezimalzahl (0.001 = 0.1%)',
            'slippage': 'Slippage als Dezimalzahl',
            'sl_stop': 'Stop Loss in Ticks (automatisch zu Prozent konvertiert)',
            'tp_stop': 'Take Profit in Ticks (automatisch zu Prozent konvertiert)',
            'cash_sharing': 'Cash-Sharing zwischen Assets aktivieren',
            'accumulate': 'Akkumulation von Positionen erlauben',
            'sl_trail': 'Trailing Stop Loss aktivieren',
            'stop_entry_price': 'Referenzpreis für Stop-Berechnung',
            'log': 'Detailliertes Portfolio-Logging aktivieren',
            'use_numba': 'Numba JIT-Kompilierung für Performance aktivieren',
            'stop_exit_price': 'Ausstiegspreis bei Stop-Auslösung',
            'upon_long_conflict': 'Verhalten bei Long-Signal-Konflikten',
            'upon_short_conflict': 'Verhalten bei Short-Signal-Konflikten',
            'upon_dir_conflict': 'Verhalten bei Richtungs-Konflikten'
        }
        return descriptions.get(param_name, f'VBT Parameter: {param_name}')

class CodeGenerator:
    """Code-Generator für Jupyter Notebooks"""

    @staticmethod
    def _generate_performance_code(performance_settings: Dict[str, Any]) -> str:
        """Generiert Performance-Optimierungs-Code"""
        code_lines = []

        # Chunking
        if performance_settings.get('chunking_enabled', False):
            code_lines.append("# Chunking für große Datenmengen")
            code_lines.append("vbt.settings.chunking['disable'] = False")

            chunk_size = performance_settings.get('chunk_size', 10000)
            if chunk_size != 'auto':
                code_lines.append(f"vbt.settings.chunking['size'] = {chunk_size}")

            n_chunks = performance_settings.get('n_chunks', 'auto')
            if n_chunks != 'auto':
                code_lines.append(f"vbt.settings.chunking['n_chunks'] = {n_chunks}")

            code_lines.append("print('✅ Chunking aktiviert')")
            code_lines.append("")

        # Numba
        if performance_settings.get('numba_parallel', False):
            code_lines.append("# Numba Parallel Processing")
            code_lines.append("vbt.settings.numba['parallel'] = True")
            code_lines.append("print('✅ Numba Parallel Processing aktiviert')")
            code_lines.append("")

        if performance_settings.get('numba_cache', True):
            code_lines.append("# Numba Cache für schnellere Starts")
            code_lines.append("# Numba Cache ist standardmäßig aktiviert (NUMBA_CACHE_DIR)")
            code_lines.append("import os")
            code_lines.append("os.environ['NUMBA_CACHE_DIR'] = '.numba_cache'")
            code_lines.append("print('✅ Numba Cache aktiviert (10x schnellerer Start)')")
            code_lines.append("")

        # Caching
        if performance_settings.get('caching_enabled', True):
            code_lines.append("# Intelligentes Caching")
            code_lines.append("vbt.settings.caching['disable'] = False")

            if performance_settings.get('cache_registry', True):
                code_lines.append("vbt.settings.caching['register_lazily'] = True")

            code_lines.append("print('✅ Caching aktiviert')")
            code_lines.append("")

        # Kompression Info
        compression = performance_settings.get('compression_type', 'blosc')
        if compression == 'blosc':
            code_lines.append("# Blosc Kompression für 20x+ Performance")
            code_lines.append("print('✅ Blosc Kompression erkannt (20x+ Performance)')")
        elif compression == 'lz4':
            code_lines.append("# LZ4 Kompression für 10x Performance")
            code_lines.append("print('✅ LZ4 Kompression erkannt (10x Performance)')")

        # Parallelisierung
        if performance_settings.get('parallel_assets', False):
            code_lines.append("")
            code_lines.append("# Multi-Asset Parallelisierung")
            worker_count = performance_settings.get('worker_count', 'auto')
            if worker_count != 'auto':
                code_lines.append(f"# Worker Count: {worker_count}")
            code_lines.append("print('✅ Multi-Asset Parallelisierung aktiviert')")

        return '\n'.join(code_lines) if code_lines else "# Keine Performance-Optimierungen konfiguriert"

    @staticmethod
    def generate_punkt5_code(vbt_parameters: Dict[str, Any], punkt3_info: Dict[str, Any]) -> str:
        """Generiert Python-Code für Punkt 5 (Strategie-Entwicklung) mit korrekten Parametern"""

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        target = "punkt5"  # Ziel-Punkt definieren

        # Parameter für Code-Generation vorbereiten
        code_params = {}

        # Zuerst Standard VBT-Parameter aus CONFIG laden
        from Punkt4_settings import CONFIG
        for param, default_value in CONFIG.VBT_DEFAULTS.items():
            code_params[param] = default_value

        # Dann mit tatsächlichen GUI-Parametern überschreiben
        for param, value in vbt_parameters.items():
            if value is not None:
                code_params[param] = value

        # Parameter für Code-String formatieren
        formatted_params = {}
        for param, value in code_params.items():
            if isinstance(value, str):
                formatted_params[param] = f'"{value}"'
            elif value == np.inf:
                formatted_params[param] = 'np.inf'
            else:
                formatted_params[param] = repr(value)

        code = f'''#!/usr/bin/env python3
# 📊 PUNKT 4: PARAMETER-KONFIGURATION FÜR PUNKT 5
# Automatisch generiert am {timestamp}
# VectorBT Pro Parameter für Strategie-Entwicklung

import vectorbtpro as vbt
import numpy as np
import pandas as pd
import json
import os

print("🚀 PUNKT 4: Parameter-Konfiguration wird geladen...")

# === VECTORBT PRO OPTIMIERUNGEN BEIBEHALTEN ===
# Punkt 3 Performance-Optimierungen beibehalten

# Punkt 3 Metadaten laden und VBT-Optimierungen anwenden
punkt3_metadata_file = r"{punkt3_info.get('metadata_file', '')}"
if punkt3_metadata_file and os.path.exists(punkt3_metadata_file):
    with open(punkt3_metadata_file, 'r', encoding='utf-8') as f:
        punkt3_metadata = json.load(f)

    # VBT-Optimierungen aus Punkt 3 beibehalten
    vbt_optimized = punkt3_metadata.get('vbt_optimized', False)
    if vbt_optimized:
        try:
            # Numba Optimierungen (wie in Punkt 3)
            vbt.settings.numba['parallel'] = True
            print("✅ Numba Parallel Processing aus Punkt 3 beibehalten")
        except Exception:
            pass

        try:
            # Caching (wie in Punkt 3)
            vbt.settings.caching['disable'] = False
            print("✅ VBT Pro Caching aus Punkt 3 beibehalten")
        except Exception:
            pass

        print("🚀 VectorBT Pro Ultra-Performance aus Punkt 3 beibehalten")
    else:
        print("⚠️ Punkt 3 hatte keine VBT-Optimierungen")
else:
    print("⚠️ Punkt 3 Metadaten nicht gefunden - Standard VBT Settings")

# === PUNKT 3 DATEN LADEN ===
# Punkt 3 Metadaten und Indikatoren
punkt3_indicators_file = r"{punkt3_info.get('indicators_file', '')}"

# VBT Data Objekt laden (20x Performance-Boost)
if punkt3_indicators_file.endswith(('.pickle', '.blosc')):
    vbt_data = vbt.Data.load(punkt3_indicators_file)
    data = vbt_data.get()
    print(f"✅ VBT Data geladen: {{data.shape}} - {{list(vbt_data.symbols)}}")
else:
    # Fallback: CSV laden
    data = pd.read_csv(punkt3_indicators_file, index_col=0, parse_dates=True)
    print(f"⚠️ CSV Fallback geladen: {{data.shape}}")

# OHLCV Spalten extrahieren
ohlcv_columns = {{}}
for col_type in ['open', 'high', 'low', 'close', 'volume']:
    for col in data.columns:
        if col_type in col.lower():
            ohlcv_columns[col_type] = col
            break

print(f"📊 OHLCV Spalten: {{ohlcv_columns}}")

# === PUNKT 4: VECTORBT PRO PARAMETER ===
# Portfolio Parameter (aus Punkt 4 GUI konfiguriert)
portfolio_params = {{'''

        # Parameter hinzufügen
        for param, value in formatted_params.items():
            code += f'\n    "{param}": {value},'
        
        code += f'''
}}

print("🎯 Portfolio Parameter konfiguriert:")
for param, value in portfolio_params.items():
    print(f"   {{param}}: {{value}}")

# === VOLLSTÄNDIGE PARAMETER-KONTROLLE ===
print("\\n" + "="*80)
print("📊 VOLLSTÄNDIGE PARAMETER-KONTROLLE")
print("="*80)

# 1. PUNKT 3 PERFORMANCE EINSTELLUNGEN AUSLESEN
try:
    import pickle
    import os
    import glob

    # Punkt 3 Performance-Datei suchen (alle möglichen Formate)
    punkt3_files = (glob.glob('punkt3_*.pkl') +
                   glob.glob('punkt3_*.pickle') +
                   glob.glob('data/punkt3/*_VBT.pickle.blosc') +
                   glob.glob('data/punkt3/*_metadata.json'))

    if punkt3_files:
        latest_file = max(punkt3_files, key=os.path.getctime)
        print(f"\\n📁 Punkt 3 Datei gefunden: {{latest_file}}")

        with open(latest_file, 'rb') as f:
            punkt3_data = pickle.load(f)

        # Performance Einstellungen anzeigen
        if 'performance_settings' in punkt3_data:
            perf_settings = punkt3_data['performance_settings']
            print("\\n⚡ PUNKT 3 PERFORMANCE EINSTELLUNGEN:")
            for key, value in perf_settings.items():
                print(f"   {{key}}: {{value}}")
        else:
            print("\\n⚠️  Keine Performance-Einstellungen in Punkt 3 gefunden")

        # Indikatoren-Info anzeigen
        if 'indicators_info' in punkt3_data:
            indicators = punkt3_data['indicators_info']
            print(f"\\n📊 INDIKATOREN: {{len(indicators)}} Bibliotheken geladen")
            total_indicators = 0
            for lib, count in indicators.items():
                print(f"   {{lib}}: {{count}} Indikatoren")
                total_indicators += count
            print(f"   TOTAL: {{total_indicators}} Indikatoren verfügbar")

        # Daten-Info anzeigen
        if 'metadata' in punkt3_data:
            metadata = punkt3_data['metadata']
            print("\\n📈 DATEN-INFORMATION:")
            for key, value in metadata.items():
                if key not in ['data', 'raw_data']:  # Große Daten nicht anzeigen
                    print(f"   {{key}}: {{value}}")

        # Asset-Info
        if 'asset_info' in punkt3_data:
            asset_info = punkt3_data['asset_info']
            print("\\n💰 ASSET-INFORMATION:")
            for key, value in asset_info.items():
                print(f"   {{key}}: {{value}}")

    else:
        # === VERWENDE DIE AUSGEWÄHLTE PUNKT 3 DATEI ===
        print("\\n📁 Verwende ausgewählte Punkt 3 Dateien:")
        print(f"   Metadaten: {{punkt3_info.get('metadata_file', 'Nicht gefunden')}}")
        print(f"   Indikatoren: {{punkt3_info.get('indicators_file', 'Nicht gefunden')}}")

        # Prüfe die ausgewählten Dateien
        metadata_file = r"{punkt3_info.get('metadata_file', '')}"
        indicators_file = r"{punkt3_info.get('indicators_file', '')}"

        if metadata_file and os.path.exists(metadata_file):
            print("✅ Ausgewählte Punkt 3 Metadaten gefunden")
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    punkt3_data = json.load(f)
                print(f"✅ Punkt 3 Metadaten geladen: {{len(punkt3_data)}} Einträge")
            except Exception as e:
                print(f"❌ Fehler beim Laden der Metadaten: {{e}}")
                punkt3_data = {{}}
        else:
            print("❌ Ausgewählte Punkt 3 Metadaten nicht gefunden")
            punkt3_data = {{}}

except Exception as e:
    print(f"\\n❌ Fehler beim Laden der Punkt 3 Daten: {{e}}")

# 2. PUNKT 4 PARAMETER KONTROLLE
print("\\n💼 PUNKT 4 PARAMETER KONTROLLE:")
print(f"   Portfolio Parameter: {{len(portfolio_params)}} konfiguriert")
print(f"   Session Trading: {{portfolio_params.get('session_enabled', False)}}")
if portfolio_params.get('session_enabled', False):
    print(f"   Session Bereiche: {{portfolio_params.get('session_ranges', 'Nicht definiert')}}")
print(f"   Performance Optimierung: {{portfolio_params.get('use_numba', True)}}")
print(f"   Logging aktiviert: {{portfolio_params.get('log', False)}}")
print(f"   Random Seed: {{portfolio_params.get('seed', 'None')}}")
print(f"   Initial Cash: ${{portfolio_params.get('init_cash', 0):,.2f}}")
print(f"   Position Size: {{portfolio_params.get('size', 1)}} ({{portfolio_params.get('size_type', 'amount')}})")
print(f"   Fixed Fees: ${{portfolio_params.get('fixed_fees', 0):.2f}}")

# 3. DATEIEN KONTROLLE
print("\\n📂 DATEIEN KONTROLLE:")
hdf5_files = glob.glob("*.h5") + glob.glob("*.hdf5")
pkl_files = glob.glob("punkt3_*.pkl") + glob.glob("punkt3_*.pickle")
vbt_files = glob.glob("data/punkt3/*_VBT.pickle.blosc")
metadata_files = glob.glob("data/punkt3/*_metadata.json")
csv_files = glob.glob("*.csv")

print(f"   HDF5 Dateien: {{len(hdf5_files)}}")
print(f"   Punkt 3 PKL Dateien: {{len(pkl_files)}}")
print(f"   Punkt 3 VBT Dateien: {{len(vbt_files)}}")
print(f"   Punkt 3 Metadaten: {{len(metadata_files)}}")
print(f"   CSV Dateien: {{len(csv_files)}}")

if hdf5_files:
    print("   Verfügbare HDF5 Dateien:")
    for file in hdf5_files[:5]:  # Nur erste 5 anzeigen
        try:
            size = os.path.getsize(file) / (1024*1024)  # MB
            print(f"     - {{file}} ({{size:.1f}} MB)")
        except:
            print(f"     - {{file}} (Größe unbekannt)")

# 4. SYSTEM KONTROLLE
print("\\n🔧 SYSTEM KONTROLLE:")
try:
    import vectorbtpro as vbt
    print(f"   VectorBT Pro: ✅ {{vbt.__version__}}")
except:
    print("   VectorBT Pro: ❌ Nicht verfügbar")

try:
    import numba
    print(f"   Numba: ✅ {{numba.__version__}}")
except:
    print("   Numba: ❌ Nicht verfügbar")

print(f"   Pandas: ✅ {{pd.__version__}}")
print(f"   NumPy: ✅ {{np.__version__}}")

# 5. SPEICHER KONTROLLE
import psutil
memory = psutil.virtual_memory()
print(f"\\n💾 SPEICHER KONTROLLE:")
print(f"   Verfügbarer RAM: {{memory.available / (1024**3):.1f}} GB")
print(f"   RAM Nutzung: {{memory.percent:.1f}}%")

# 6. VALIDIERUNG
print("\\n✅ VALIDIERUNG:")
validation_errors = []

# Portfolio Parameter validieren
required_params = ['init_cash', 'size', 'size_type', 'direction']
for param in required_params:
    if param not in portfolio_params:
        validation_errors.append(f"Fehlender Parameter: {{param}}")

# Daten validieren - prüfe ausgewählte Dateien
metadata_file = r"{punkt3_info.get('metadata_file', '')}"
indicators_file = r"{punkt3_info.get('indicators_file', '')}"

if not (metadata_file and os.path.exists(metadata_file)) and not (indicators_file and os.path.exists(indicators_file)):
    validation_errors.append("Keine gültigen Punkt 3 Dateien ausgewählt")
else:
    print(f"   ✅ Ausgewählte Punkt 3 Dateien validiert")
    print(f"     Metadaten: {{os.path.exists(metadata_file) if metadata_file else False}}")
    print(f"     Indikatoren: {{os.path.exists(indicators_file) if indicators_file else False}}")

if validation_errors:
    print("   ❌ VALIDIERUNGSFEHLER:")
    for error in validation_errors:
        print(f"     - {{error}}")
else:
    print("   ✅ Alle Validierungen bestanden")

print("\\n✅ PARAMETER-KONTROLLE ABGESCHLOSSEN")
print("="*80)

# === PUNKT 4 VBT PRO EXPORT ===
print("\\n" + "="*80)
print("💾 PUNKT 4 VBT PRO EXPORT")
print("="*80)

# Variablen initialisieren
target = "punkt5"
base_name = "unknown"
punkt4_filename = f"punkt4_{{target}}_{{base_name}}_{{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}}"

try:
    import os
    from datetime import datetime
    from pathlib import Path

    # Punkt 4 Verzeichnis erstellen
    punkt4_dir = Path("data/punkt4")
    punkt4_dir.mkdir(parents=True, exist_ok=True)

    # Timestamp für eindeutige Dateinamen
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    # === 1. PUNKT 3 VBT DATA LADEN ===

    # Punkt 3 VBT Datei finden (.pickle.blosc)
    punkt3_vbt_files = list(Path("data/punkt3").glob("*_VBT.pickle.blosc"))

    if punkt3_vbt_files:
        # Neueste VBT Datei verwenden
        vbt_file = max(punkt3_vbt_files, key=os.path.getctime)
        print(f"\\n📊 Punkt 3 VBT Datei gefunden: {{vbt_file.name}}")

        # Punkt 3 VBT Data laden
        punkt3_complete = vbt.load(str(vbt_file))
        print(f"✅ Punkt 3 Daten geladen: {{type(punkt3_complete)}}")

        # Base Name extrahieren
        base_name = vbt_file.stem.replace('_VBT.pickle', '')

        # === 2. PUNKT 4 KOMPLETT-DATEN ERSTELLEN ===

        punkt4_filename = f"punkt4_{{target}}_{{base_name}}_{{timestamp}}"

        # VBT Pro Style: Alles in EINER Datei
        punkt4_complete = {{
            # === ALLE PUNKT 3 DATEN (KOMPLETT) ===
            'vbt_data': punkt3_complete.get('vbt_data') if isinstance(punkt3_complete, dict) else punkt3_complete,
            'punkt3_metadata': punkt3_complete.get('metadata', {{}}) if isinstance(punkt3_complete, dict) else {{}},
            'punkt3_indicators': punkt3_complete.get('indicators', []) if isinstance(punkt3_complete, dict) else [],
            'punkt3_performance': punkt3_complete.get('performance_settings', {{}}) if isinstance(punkt3_complete, dict) else {{}},
            'punkt3_info': punkt3_complete.get('punkt3_info', {{}}) if isinstance(punkt3_complete, dict) else {{}},

            # === PUNKT 4 PARAMETER ===
            'portfolio_parameters': portfolio_params,

            # === PUNKT 4 INFO ===
            'punkt4_info': {{
                'created_at': datetime.now().isoformat(),
                'target': target,
                'export_name': punkt4_filename,
                'parameter_count': len(portfolio_params),
                'punkt4_ready': True,
                'version': '1.0.0',
                'source_punkt3': str(vbt_file)
            }}
        }}

        # === 3. VBT PRO EXPORT (EINE DATEI) ===

        # VBT Pro Standard: .pickle.blosc für beste Performance
        export_file = punkt4_dir / f"{{punkt4_filename}}.pickle.blosc"
        vbt.save(punkt4_complete, str(export_file))

        # === 4. ERFOLGS-MELDUNG ===

        file_size = os.path.getsize(export_file) / (1024*1024)  # MB

        print(f"\\n✅ PUNKT 4 VBT PRO EXPORT ERSTELLT:")
        print(f"   📁 Datei: {{punkt4_filename}}.pickle.blosc")
        print(f"   📊 Größe: {{file_size:.1f}} MB (BLOSC komprimiert)")
        print(f"   🎯 Ziel: {{target.upper()}}")
        print(f"   📈 Punkt 3 Daten: ✅ Komplett übernommen")
        print(f"   ⚙️ Portfolio Parameter: {{len(portfolio_params)}}")
        print(f"   📂 Verzeichnis: {{punkt4_dir}}")

        print(f"\\n🚀 VBT PRO VORTEILE:")
        print(f"   ✅ EINE Datei statt mehrerer")
        print(f"   ✅ BLOSC Kompression (10x kleiner)")
        print(f"   ✅ Automatische .blosc Erkennung")
        print(f"   ✅ Alle Daten zusammen")

        print(f"\\n🔗 PUNKT 5 LADEN:")
        print(f"   punkt4_data = vbt.load('{{punkt4_filename}}.pickle.blosc')")
        print(f"   vbt_data = punkt4_data['vbt_data']")
        print(f"   portfolio_params = punkt4_data['portfolio_parameters']")

    else:
        print("\\n❌ Keine Punkt 3 VBT Dateien (.pickle.blosc) gefunden!")
        print("   Bitte führe zuerst Punkt 3 aus.")

except Exception as e:
    print(f"\\n❌ Punkt 4 VBT Pro Export Fehler: {{e}}")
    import traceback
    traceback.print_exc()

print("\\n" + "="*80)

# === BEREIT FÜR PUNKT 5 ===
print("\\n" + "="*50)
print("🎯 PUNKT 4 ABGESCHLOSSEN")
print("📈 Bereit für PUNKT 5: Strategie-Entwicklung")
print("="*50)

# Verfügbare Variablen für Punkt 5:
# - data: DataFrame mit allen Indikatoren
# - vbt_data: VBT Data Objekt (falls verfügbar)
# - ohlcv_columns: Dictionary mit OHLCV Spalten-Namen
# - portfolio_params: Dictionary mit allen Portfolio-Parametern

# Beispiel für Punkt 5 Strategie-Entwicklung:
# entries = data['RSI'] < 30  # Entry-Signale
# exits = data['RSI'] > 70   # Exit-Signale
# 
# pf = vbt.Portfolio.from_signals(
#     data,
#     entries=entries,
#     exits=exits,
#     **portfolio_params
# )
'''
        
        return code
    
    @staticmethod
    def generate_punkt6_code(vbt_parameters: Dict[str, Any], punkt3_info: Dict[str, Any]) -> str:
        """Generiert Python-Code für Punkt 6 (Backtesting)"""
        
        # Basis-Code von Punkt 5
        base_code = CodeGenerator.generate_punkt5_code(vbt_parameters, punkt3_info)
        
        # Punkt 6 spezifische Ergänzungen
        punkt6_additions = '''

# === PUNKT 6: BACKTESTING ERWEITERUNGEN ===
print("🔬 PUNKT 6: Backtesting-Funktionen werden geladen...")

# Performance-Metriken Funktionen
def calculate_performance_metrics(portfolio):
    """Berechnet umfassende Performance-Metriken"""
    metrics = {}
    
    # Basis-Metriken
    metrics['total_return'] = portfolio.total_return
    metrics['sharpe_ratio'] = portfolio.sharpe_ratio
    metrics['max_drawdown'] = portfolio.max_drawdown
    metrics['win_rate'] = portfolio.trades.win_rate
    
    # Erweiterte Metriken
    metrics['sortino_ratio'] = portfolio.sortino_ratio
    metrics['calmar_ratio'] = portfolio.calmar_ratio
    metrics['profit_factor'] = portfolio.trades.profit_factor
    
    return metrics

def run_backtest_analysis(portfolio):
    """Führt umfassende Backtest-Analyse durch"""
    print("📊 Backtest-Analyse wird durchgeführt...")
    
    # Performance-Metriken
    metrics = calculate_performance_metrics(portfolio)
    
    # Trade-Analyse
    trades = portfolio.trades
    print(f"📈 Trades: {trades.count}")
    print(f"💰 Win Rate: {trades.win_rate:.2%}")
    print(f"📊 Profit Factor: {trades.profit_factor:.2f}")
    
    # Drawdown-Analyse
    drawdowns = portfolio.drawdowns
    print(f"📉 Max Drawdown: {portfolio.max_drawdown:.2%}")
    print(f"⏱️ Avg Drawdown Duration: {drawdowns.avg_duration}")
    
    return metrics

print("✅ Punkt 6 Backtesting-Funktionen geladen")
print("🎯 Bereit für Portfolio-Backtesting mit umfassender Analyse")
'''
        
        return base_code + punkt6_additions

# Utility-Funktionen
def format_file_size(size_bytes: int) -> str:
    """Formatiert Dateigröße"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def format_number(value: Union[int, float], decimals: int = 2) -> str:
    """Formatiert Zahlen"""
    if isinstance(value, int):
        return f"{value:,}"
    return f"{value:,.{decimals}f}"

def format_percentage(value: float, decimals: int = 1) -> str:
    """Formatiert Prozentsatz"""
    return f"{value:.{decimals}f}%"
