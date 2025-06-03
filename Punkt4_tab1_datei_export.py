# 📊 PUNKT 4: PARAMETER-KONFIGURATOR - TAB 1: DATEI & EXPORT
# Punkt 3 Datei-Auswahl und Code-Export für Jupyter

import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from Punkt4_settings import CONFIG
from Punkt4_events import emit, on, Events
from Punkt4_state_manager import get_state, set_state, update_state
from Punkt4_utils import UIUtils, DataUtils, CodeGenerator

class Tab1DateiExport:
    """Tab 1: Punkt 3 Datei-Auswahl und Code-Export"""
    
    def __init__(self, parent):
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        
        # Tkinter Variables
        self.metadata_file_var = tk.StringVar()
        self.indicators_file_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Keine Punkt 3 Datei ausgewählt")
        self.export_target_var = tk.StringVar(value="punkt5")
        
        # UI Setup
        self.setup_ui()
        self.setup_events()
        
        # Initial State
        self.update_from_state()
    
    def setup_ui(self):
        """UI-Komponenten erstellen"""
        # Main Container
        self.main_frame = ttk.Frame(self.parent, padding=CONFIG.GUI['tab_padding'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === PUNKT 3 DATEI-AUSWAHL ===
        self.create_file_selection_section()
        
        # === DATEN-ÜBERSICHT ===
        self.create_data_overview_section()
        
        # === CODE-EXPORT ===
        self.create_export_section()
        
        # === STATUS ===
        self.create_status_section()
    
    def create_file_selection_section(self):
        """Punkt 3 Datei-Auswahl Sektion"""
        file_frame = UIUtils.create_labeled_frame(self.main_frame, "📁 PUNKT 3 DATEN AUSWAHL")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Info Text
        info_label = ttk.Label(file_frame,
                              text="Punkt 3 Daten werden automatisch geladen:",
                              font=('TkDefaultFont', 9))
        info_label.pack(anchor=tk.W, pady=(0, 10))

        # Vereinfachte Datei-Anzeige
        file_display_frame = ttk.Frame(file_frame)
        file_display_frame.pack(fill=tk.X, pady=5)

        ttk.Label(file_display_frame, text="Punkt 3 Export:", width=20).pack(side=tk.LEFT)
        self.file_display_var = tk.StringVar(value="Keine Dateien gefunden")
        ttk.Entry(file_display_frame, textvariable=self.file_display_var, state="readonly", width=60).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(file_display_frame, text="📂 Manuell wählen", command=self.select_punkt3_export, width=15).pack(side=tk.RIGHT, padx=5)

        # Aktions-Buttons
        action_frame = ttk.Frame(file_frame)
        action_frame.pack(fill=tk.X, pady=10)

        ttk.Button(action_frame, text="🔍 Auto-Laden", command=self.auto_load_punkt3, width=15).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="🔄 Neu laden", command=self.reload_data, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(action_frame, text="🧪 Test Indikatoren", command=self.test_load_indicators, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(action_frame, text="🚀 VBT Daten", command=self.load_vbt_data_directly, width=15).pack(side=tk.LEFT, padx=5)

        ttk.Button(action_frame, text="❌ Zurücksetzen", command=self.reset_files, width=15).pack(side=tk.LEFT, padx=10)

        # Auto-Load beim Start
        self.parent.after(2000, self.auto_load_punkt3)  # Nach 2 Sekunden auto-laden
        print("DEBUG: Auto-Load Timer gestartet (2 Sekunden)")
    
    def create_data_overview_section(self):
        """Erweiterte Daten-Analyse Sektion"""
        overview_frame = UIUtils.create_labeled_frame(self.main_frame, "📊 DETAILLIERTE DATEN-ANALYSE")
        overview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Notebook für verschiedene Analyse-Bereiche
        self.analysis_notebook = ttk.Notebook(overview_frame)
        self.analysis_notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Tab 1: Asset & Zeitraum Info
        self.create_asset_info_tab()

        # Tab 2: Indikator-Übersicht
        self.create_indicators_tab()

        # Tab 3: VBT Pro Optimierungen
        self.create_vbt_optimization_tab()

        # Tab 4: Datei-Informationen
        self.create_file_info_tab()

    def create_asset_info_tab(self):
        """Asset & Zeitraum Informationen Tab"""
        asset_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(asset_frame, text="📊 Assets & Zeitraum")

        # Asset Informationen
        asset_info_frame = UIUtils.create_labeled_frame(asset_frame, "📈 ASSET-INFORMATIONEN")
        asset_info_frame.pack(fill=tk.X, pady=5)

        self.assets_label = ttk.Label(asset_info_frame, text="Assets: -", font=('TkDefaultFont', 9))
        self.assets_label.pack(anchor=tk.W, pady=2)

        self.asset_count_label = ttk.Label(asset_info_frame, text="Anzahl Assets: -", font=('TkDefaultFont', 9))
        self.asset_count_label.pack(anchor=tk.W, pady=2)

        self.asset_types_label = ttk.Label(asset_info_frame, text="Asset-Typen: -", font=('TkDefaultFont', 9))
        self.asset_types_label.pack(anchor=tk.W, pady=2)

        # Zeitraum Informationen
        time_info_frame = UIUtils.create_labeled_frame(asset_frame, "⏰ ZEITRAUM-INFORMATIONEN")
        time_info_frame.pack(fill=tk.X, pady=5)

        self.date_range_label = ttk.Label(time_info_frame, text="Zeitraum: -", font=('TkDefaultFont', 9))
        self.date_range_label.pack(anchor=tk.W, pady=2)

        self.timeframe_label = ttk.Label(time_info_frame, text="Timeframe: -", font=('TkDefaultFont', 9))
        self.timeframe_label.pack(anchor=tk.W, pady=2)

        self.data_points_label = ttk.Label(time_info_frame, text="Datenpunkte: -", font=('TkDefaultFont', 9))
        self.data_points_label.pack(anchor=tk.W, pady=2)

        self.duration_label = ttk.Label(time_info_frame, text="Zeitraum-Länge: -", font=('TkDefaultFont', 9))
        self.duration_label.pack(anchor=tk.W, pady=2)

        # Daten-Shape
        shape_info_frame = UIUtils.create_labeled_frame(asset_frame, "📐 DATEN-STRUKTUR")
        shape_info_frame.pack(fill=tk.X, pady=5)

        self.data_shape_label = ttk.Label(shape_info_frame, text="Shape: -", font=('TkDefaultFont', 9))
        self.data_shape_label.pack(anchor=tk.W, pady=2)

        self.columns_count_label = ttk.Label(shape_info_frame, text="Spalten: -", font=('TkDefaultFont', 9))
        self.columns_count_label.pack(anchor=tk.W, pady=2)

        self.memory_usage_label = ttk.Label(shape_info_frame, text="Memory Usage: -", font=('TkDefaultFont', 9))
        self.memory_usage_label.pack(anchor=tk.W, pady=2)

    def create_indicators_tab(self):
        """Indikator-Übersicht Tab"""
        indicators_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(indicators_frame, text="📈 Indikatoren")

        # Indikator-Statistiken
        stats_frame = UIUtils.create_labeled_frame(indicators_frame, "📊 INDIKATOR-STATISTIKEN")
        stats_frame.pack(fill=tk.X, pady=5)

        self.indicators_count_label = ttk.Label(stats_frame, text="Anzahl Indikatoren: -", font=('TkDefaultFont', 9))
        self.indicators_count_label.pack(anchor=tk.W, pady=2)

        self.libraries_label = ttk.Label(stats_frame, text="Bibliotheken: -", font=('TkDefaultFont', 9))
        self.libraries_label.pack(anchor=tk.W, pady=2)

        self.ohlcv_label = ttk.Label(stats_frame, text="OHLCV Spalten: -", font=('TkDefaultFont', 9))
        self.ohlcv_label.pack(anchor=tk.W, pady=2)

        # Indikator-Liste
        list_frame = UIUtils.create_labeled_frame(indicators_frame, "📋 INDIKATOR-LISTE")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Treeview für detaillierte Indikator-Anzeige
        columns = ('Indikator', 'Bibliothek', 'Parameter', 'Spalten')
        self.indicators_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)

        # Spalten konfigurieren
        self.indicators_tree.heading('Indikator', text='Indikator')
        self.indicators_tree.heading('Bibliothek', text='Bibliothek')
        self.indicators_tree.heading('Parameter', text='Parameter')
        self.indicators_tree.heading('Spalten', text='Spalten')

        self.indicators_tree.column('Indikator', width=150)
        self.indicators_tree.column('Bibliothek', width=100)
        self.indicators_tree.column('Parameter', width=200)
        self.indicators_tree.column('Spalten', width=100)

        # Scrollbar
        tree_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.indicators_tree.yview)
        self.indicators_tree.configure(yscrollcommand=tree_scrollbar.set)

        self.indicators_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_vbt_optimization_tab(self):
        """VectorBT Pro Optimierungen Tab"""
        vbt_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(vbt_frame, text="🚀 VBT Pro")

        # VBT Data Objekt Status
        vbt_data_frame = UIUtils.create_labeled_frame(vbt_frame, "📊 VBT DATA OBJEKT")
        vbt_data_frame.pack(fill=tk.X, pady=5)

        self.vbt_data_status_label = ttk.Label(vbt_data_frame, text="VBT Data Objekt: -", font=('TkDefaultFont', 9))
        self.vbt_data_status_label.pack(anchor=tk.W, pady=2)

        self.vbt_wrapper_label = ttk.Label(vbt_data_frame, text="Wrapper Info: -", font=('TkDefaultFont', 9))
        self.vbt_wrapper_label.pack(anchor=tk.W, pady=2)

        self.vbt_symbols_label = ttk.Label(vbt_data_frame, text="VBT Symbols: -", font=('TkDefaultFont', 9))
        self.vbt_symbols_label.pack(anchor=tk.W, pady=2)

        # Numba Optimierungen
        numba_frame = UIUtils.create_labeled_frame(vbt_frame, "⚡ NUMBA OPTIMIERUNGEN")
        numba_frame.pack(fill=tk.X, pady=5)

        self.numba_status_label = ttk.Label(numba_frame, text="Numba Status: -", font=('TkDefaultFont', 9))
        self.numba_status_label.pack(anchor=tk.W, pady=2)

        self.numba_parallel_label = ttk.Label(numba_frame, text="Parallel Processing: -", font=('TkDefaultFont', 9))
        self.numba_parallel_label.pack(anchor=tk.W, pady=2)

        self.numba_cache_label = ttk.Label(numba_frame, text="Numba Cache: -", font=('TkDefaultFont', 9))
        self.numba_cache_label.pack(anchor=tk.W, pady=2)

        # Performance Optimierungen
        perf_frame = UIUtils.create_labeled_frame(vbt_frame, "🔧 PERFORMANCE OPTIMIERUNGEN")
        perf_frame.pack(fill=tk.X, pady=5)

        self.compression_label = ttk.Label(perf_frame, text="Kompression: -", font=('TkDefaultFont', 9))
        self.compression_label.pack(anchor=tk.W, pady=2)

        self.chunking_label = ttk.Label(perf_frame, text="Chunking: -", font=('TkDefaultFont', 9))
        self.chunking_label.pack(anchor=tk.W, pady=2)

        self.dtype_optimization_label = ttk.Label(perf_frame, text="Datentyp-Optimierung: -", font=('TkDefaultFont', 9))
        self.dtype_optimization_label.pack(anchor=tk.W, pady=2)

        # Performance Benefits
        benefits_frame = UIUtils.create_labeled_frame(vbt_frame, "📈 PERFORMANCE-VORTEILE")
        benefits_frame.pack(fill=tk.X, pady=5)

        self.speed_improvement_label = ttk.Label(benefits_frame, text="Geschwindigkeits-Verbesserung: -", font=('TkDefaultFont', 9))
        self.speed_improvement_label.pack(anchor=tk.W, pady=2)

        self.memory_efficiency_label = ttk.Label(benefits_frame, text="Memory-Effizienz: -", font=('TkDefaultFont', 9))
        self.memory_efficiency_label.pack(anchor=tk.W, pady=2)

        self.scalability_label = ttk.Label(benefits_frame, text="Skalierbarkeit: -", font=('TkDefaultFont', 9))
        self.scalability_label.pack(anchor=tk.W, pady=2)

    def create_file_info_tab(self):
        """Datei-Informationen Tab"""
        file_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(file_frame, text="💾 Datei-Info")

        # Datei-Details
        file_details_frame = UIUtils.create_labeled_frame(file_frame, "📁 DATEI-DETAILS")
        file_details_frame.pack(fill=tk.X, pady=5)

        self.file_path_label = ttk.Label(file_details_frame, text="Dateipfad: -", font=('TkDefaultFont', 9))
        self.file_path_label.pack(anchor=tk.W, pady=2)

        self.file_size_label = ttk.Label(file_details_frame, text="Dateigröße: -", font=('TkDefaultFont', 9))
        self.file_size_label.pack(anchor=tk.W, pady=2)

        self.file_type_label = ttk.Label(file_details_frame, text="Dateityp: -", font=('TkDefaultFont', 9))
        self.file_type_label.pack(anchor=tk.W, pady=2)

        self.creation_date_label = ttk.Label(file_details_frame, text="Erstellt: -", font=('TkDefaultFont', 9))
        self.creation_date_label.pack(anchor=tk.W, pady=2)

        # Datentyp-Informationen
        dtype_frame = UIUtils.create_labeled_frame(file_frame, "🔢 DATENTYP-INFORMATIONEN")
        dtype_frame.pack(fill=tk.X, pady=5)

        self.dtypes_label = ttk.Label(dtype_frame, text="Datentypen: -", font=('TkDefaultFont', 9))
        self.dtypes_label.pack(anchor=tk.W, pady=2)

        self.float64_columns_label = ttk.Label(dtype_frame, text="Float64 Spalten: -", font=('TkDefaultFont', 9))
        self.float64_columns_label.pack(anchor=tk.W, pady=2)

        self.nan_percentage_label = ttk.Label(dtype_frame, text="NaN Anteil: -", font=('TkDefaultFont', 9))
        self.nan_percentage_label.pack(anchor=tk.W, pady=2)

        # Kompression & Effizienz
        compression_frame = UIUtils.create_labeled_frame(file_frame, "📦 KOMPRESSION & EFFIZIENZ")
        compression_frame.pack(fill=tk.X, pady=5)

        self.compression_ratio_label = ttk.Label(compression_frame, text="Kompression-Ratio: -", font=('TkDefaultFont', 9))
        self.compression_ratio_label.pack(anchor=tk.W, pady=2)

        self.load_time_label = ttk.Label(compression_frame, text="Ladezeit: -", font=('TkDefaultFont', 9))
        self.load_time_label.pack(anchor=tk.W, pady=2)

        self.punkt4_compatibility_label = ttk.Label(compression_frame, text="Punkt 4 Kompatibilität: -", font=('TkDefaultFont', 9))
        self.punkt4_compatibility_label.pack(anchor=tk.W, pady=2)
    
    def create_export_section(self):
        """Code-Export Sektion"""
        export_frame = UIUtils.create_labeled_frame(self.main_frame, "💾 JUPYTER CODE-EXPORT")
        export_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Export-Ziel Auswahl
        target_frame = ttk.Frame(export_frame)
        target_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(target_frame, text="Export-Ziel:", width=15).pack(side=tk.LEFT)
        target_combo = ttk.Combobox(target_frame, textvariable=self.export_target_var,
                                   values=["punkt5", "punkt6"], state="readonly", width=15)
        target_combo.pack(side=tk.LEFT, padx=5)
        
        # Info Label
        self.export_info_label = ttk.Label(target_frame, text="Punkt 5: Strategie-Entwicklung", 
                                          font=('TkDefaultFont', 9), foreground='blue')
        self.export_info_label.pack(side=tk.LEFT, padx=20)
        
        # Export-Buttons
        button_frame = ttk.Frame(export_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="🚀 Code generieren", command=self.generate_code, width=20).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="💾 Code speichern", command=self.save_code, width=20).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="📋 Code kopieren", command=self.copy_code, width=20).pack(side=tk.LEFT, padx=10)
        
        # Code-Vorschau
        preview_label = ttk.Label(export_frame, text="📝 Code-Vorschau:")
        preview_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.code_text = scrolledtext.ScrolledText(export_frame, height=15, width=80, 
                                                  font=('Consolas', 9), wrap=tk.NONE)
        self.code_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Export-Target Change Event
        target_combo.bind('<<ComboboxSelected>>', self.on_export_target_changed)
    
    def create_status_section(self):
        """Status Sektion"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status Label
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                     relief=tk.SUNKEN, anchor=tk.W, font=('TkDefaultFont', 9))
        self.status_label.pack(fill=tk.X, pady=5)
    
    def setup_events(self):
        """Event-Handler registrieren"""
        def on_data_loaded(data):
            self.update_data_overview()
            self.status_var.set("✅ Punkt 3 Daten erfolgreich geladen")

        def on_data_error(data):
            error = data.get('error', 'Unbekannter Fehler')
            self.status_var.set(f"❌ Fehler: {error}")
            UIUtils.show_error("Daten-Fehler", error)

        def on_status_changed(data):
            message = data.get('message', '')
            level = data.get('level', 'info')
            if level == 'error':
                self.status_var.set(f"❌ {message}")
            elif level == 'warning':
                self.status_var.set(f"⚠️ {message}")
            else:
                self.status_var.set(f"ℹ️ {message}")

        def on_code_generated(data):
            code = data.get('code', '')
            lines = data.get('lines', 0)
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(1.0, code)
            self.status_var.set(f"✅ Code generiert: {lines} Zeilen")

        # Event-Listener registrieren
        on(Events.PUNKT3_DATA_LOADED, on_data_loaded)
        on(Events.PUNKT3_DATA_ERROR, on_data_error)
        on(Events.STATUS_CHANGED, on_status_changed)
        on(Events.CODE_GENERATED, on_code_generated)
    
    def select_metadata_file(self):
        """Metadaten-Datei auswählen"""
        file_path = UIUtils.select_file(
            "Punkt 3 Metadaten-Datei auswählen",
            CONFIG.FILE_FILTERS['punkt3_metadata'],
            str(CONFIG.PATHS['punkt3_data'])
        )
        
        if file_path:
            self.metadata_file_var.set(file_path)
            set_state('punkt3.metadata_file', file_path)
            self.status_var.set(f"📁 Metadaten-Datei ausgewählt: {Path(file_path).name}")
    
    def select_indicators_file(self):
        """Indikatoren-Datei auswählen"""
        file_path = UIUtils.select_file(
            "Punkt 3 Indikatoren-Datei auswählen",
            CONFIG.FILE_FILTERS['punkt3_indicators'],
            str(CONFIG.PATHS['punkt3_data'])
        )
        
        if file_path:
            self.indicators_file_var.set(file_path)
            set_state('punkt3.indicators_file', file_path)
            self.status_var.set(f"📁 Indikatoren-Datei ausgewählt: {Path(file_path).name}")
    
    def auto_load_punkt3(self):
        """Automatisches Laden der neuesten Punkt 3 Dateien"""
        try:
            print("DEBUG: auto_load_punkt3 aufgerufen")
            punkt3_dir = CONFIG.PATHS['punkt3_data']
            print(f"DEBUG: Punkt 3 Verzeichnis: {punkt3_dir}")

            if not punkt3_dir.exists():
                print("DEBUG: Punkt 3 Verzeichnis existiert nicht")
                self.status_var.set("❌ Punkt 3 Verzeichnis nicht gefunden")
                self.file_display_var.set("Punkt 3 Verzeichnis nicht gefunden")
                return

            # Suche nach neuester Metadaten-Datei
            metadata_files = list(punkt3_dir.glob("*_metadata.json"))
            if not metadata_files:
                self.status_var.set("❌ Keine Punkt 3 Exports gefunden")
                self.file_display_var.set("Keine Punkt 3 Exports gefunden")
                return

            # Neueste Metadaten-Datei
            latest_metadata = max(metadata_files, key=os.path.getctime)
            base_name = latest_metadata.stem.replace('_metadata', '')

            # Suche nach passender VBT Datei
            vbt_files = list(punkt3_dir.glob(f"{base_name}*_VBT.pickle*"))
            if vbt_files:
                latest_vbt = max(vbt_files, key=os.path.getctime)

                # Dateien setzen
                self.metadata_file_var.set(str(latest_metadata))
                self.indicators_file_var.set(str(latest_vbt))

                # Display aktualisieren
                export_name = latest_metadata.stem.replace('_indicators_metadata', '')
                self.file_display_var.set(f"✅ {export_name} (VBT optimiert)")

                # Automatisch laden
                self.load_data()

            else:
                # Fallback: CSV
                csv_files = list(punkt3_dir.glob(f"{base_name}*_backup.csv"))
                if csv_files:
                    latest_csv = max(csv_files, key=os.path.getctime)

                    self.metadata_file_var.set(str(latest_metadata))
                    self.indicators_file_var.set(str(latest_csv))

                    export_name = latest_metadata.stem.replace('_indicators_metadata', '')
                    self.file_display_var.set(f"⚠️ {export_name} (CSV Fallback)")

                    self.load_data()
                else:
                    self.status_var.set("❌ Keine passenden Indikatoren-Dateien gefunden")
                    self.file_display_var.set("Keine Indikatoren-Dateien gefunden")

        except Exception as e:
            self.logger.error(f"Auto-Load Fehler: {e}")
            self.status_var.set(f"❌ Auto-Load Fehler: {e}")
            self.file_display_var.set(f"Fehler: {e}")

    def select_punkt3_export(self):
        """Manuell Punkt 3 Daten-Datei auswählen"""
        # Erweiterte Datei-Filter für alle unterstützten Formate
        file_filters = [
            ('VBT Pickle Blosc', '*.pickle.blosc'),
            ('VBT Pickle', '*.pickle'),
            ('HDF5 Dateien', '*.h5'),
            ('HDF5 Dateien', '*.hdf5'),
            ('CSV Dateien', '*.csv'),
            ('JSON Metadaten', '*.json'),
            ('Alle Dateien', '*.*')
        ]

        file_path = UIUtils.select_file(
            "Punkt 3 Daten-Datei auswählen (Pickle/HDF5/CSV)",
            file_filters,
            str(CONFIG.PATHS['punkt3_data'])
        )

        if file_path:
            self.process_selected_file(file_path)

    def process_selected_file(self, file_path):
        """Verarbeitet die ausgewählte Datei und sucht passende Metadaten"""
        try:
            file_path = Path(file_path)
            self.status_var.set(f"🔄 Verarbeite {file_path.name}...")

            # Datei-Typ bestimmen
            file_type = self.detect_file_type(file_path)

            if file_type == 'metadata':
                # JSON Metadaten-Datei ausgewählt
                self.process_metadata_file(file_path)
            else:
                # Daten-Datei ausgewählt
                self.process_data_file(file_path, file_type)

        except Exception as e:
            self.logger.error(f"Datei-Verarbeitung Fehler: {e}")
            self.status_var.set(f"❌ Fehler beim Verarbeiten: {e}")

    def detect_file_type(self, file_path):
        """Erkennt den Dateityp"""
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()

        if 'metadata' in name and suffix == '.json':
            return 'metadata'
        elif suffix == '.blosc' or file_path.name.endswith('.pickle.blosc'):
            return 'pickle_blosc'
        elif suffix == '.pickle':
            return 'pickle'
        elif suffix in ['.h5', '.hdf5']:
            return 'hdf5'
        elif suffix == '.csv':
            return 'csv'
        elif suffix == '.json':
            return 'json_data'
        else:
            return 'unknown'

    def process_metadata_file(self, metadata_path):
        """Verarbeitet Metadaten-Datei und sucht passende Daten-Datei"""
        try:
            # Metadaten-Datei setzen
            self.metadata_file_var.set(str(metadata_path))

            # Base-Name für Suche
            base_name = metadata_path.stem.replace('_metadata', '').replace('_indicators_metadata', '')
            punkt3_dir = metadata_path.parent

            # Suche nach passender Daten-Datei (Priorität: Blosc > Pickle > HDF5 > CSV)
            data_file = self.find_matching_data_file(punkt3_dir, base_name)

            if data_file:
                self.indicators_file_var.set(str(data_file))
                file_type = self.detect_file_type(data_file)
                self.update_file_display(base_name, file_type)
                self.load_data()
            else:
                self.status_var.set("❌ Keine passende Daten-Datei gefunden")

        except Exception as e:
            self.logger.error(f"Metadaten-Verarbeitung Fehler: {e}")
            self.status_var.set(f"❌ Metadaten-Fehler: {e}")

    def process_data_file(self, data_path, file_type):
        """Verarbeitet Daten-Datei und sucht passende Metadaten"""
        try:
            # Daten-Datei setzen
            self.indicators_file_var.set(str(data_path))

            # Base-Name für Metadaten-Suche
            base_name = data_path.stem
            # Entferne bekannte Suffixe
            for suffix in ['_VBT', '_backup', '_indicators', '_data']:
                base_name = base_name.replace(suffix, '')

            punkt3_dir = data_path.parent

            # Suche nach passender Metadaten-Datei
            metadata_file = self.find_matching_metadata_file(punkt3_dir, base_name)

            if metadata_file:
                self.metadata_file_var.set(str(metadata_file))
                self.update_file_display(base_name, file_type)
                self.load_data()
            else:
                # Versuche ohne Metadaten zu laden
                self.metadata_file_var.set("")
                self.update_file_display(base_name, file_type)
                self.load_data_without_metadata(data_path, file_type)

        except Exception as e:
            self.logger.error(f"Daten-Verarbeitung Fehler: {e}")
            self.status_var.set(f"❌ Daten-Fehler: {e}")

    def find_matching_data_file(self, directory, base_name):
        """Findet passende Daten-Datei (Priorität: Blosc > Pickle > HDF5 > CSV)"""
        search_patterns = [
            f"{base_name}*_VBT.pickle.blosc",
            f"{base_name}*indicators_VBT.pickle.blosc",
            f"{base_name}*.pickle.blosc",
            f"{base_name}*_VBT.pickle",
            f"{base_name}*indicators_VBT.pickle",
            f"{base_name}*.pickle",
            f"{base_name}*.h5",
            f"{base_name}*.hdf5",
            f"{base_name}*_backup.csv",
            f"{base_name}*indicators_backup.csv",
            f"{base_name}*.csv"
        ]

        print(f"DEBUG: Suche Daten-Datei für Base-Name: {base_name}")
        for pattern in search_patterns:
            files = list(directory.glob(pattern))
            print(f"DEBUG: Pattern '{pattern}' gefunden: {[f.name for f in files]}")
            if files:
                found_file = max(files, key=os.path.getctime)  # Neueste Datei
                print(f"DEBUG: Verwende Daten-Datei: {found_file.name}")
                return found_file

        print(f"DEBUG: Keine passende Daten-Datei für '{base_name}' gefunden")
        return None

    def find_matching_metadata_file(self, directory, base_name):
        """Findet passende Metadaten-Datei"""
        search_patterns = [
            f"{base_name}*_indicators_metadata.json",
            f"{base_name}*_metadata.json",
            f"{base_name}*metadata.json"
        ]

        print(f"DEBUG: Suche Metadaten-Datei für Base-Name: {base_name}")
        for pattern in search_patterns:
            files = list(directory.glob(pattern))
            print(f"DEBUG: Pattern '{pattern}' gefunden: {[f.name for f in files]}")
            if files:
                # Filtere nur echte Metadaten-Dateien
                for file in files:
                    if 'metadata' in file.name.lower():
                        print(f"DEBUG: Verwende Metadaten-Datei: {file.name}")
                        return file

        print(f"DEBUG: Keine passende Metadaten-Datei für '{base_name}' gefunden")
        return None

    def update_file_display(self, base_name, file_type):
        """Aktualisiert die Datei-Anzeige"""
        type_info = {
            'pickle_blosc': '✅ VBT Blosc (20x Performance)',
            'pickle': '⚡ VBT Pickle (5x Performance)',
            'hdf5': '📊 HDF5 (Optimiert)',
            'csv': '⚠️ CSV (Standard)',
            'unknown': '❓ Unbekanntes Format'
        }

        display_text = f"{base_name} - {type_info.get(file_type, '❓ Unbekannt')}"
        self.file_display_var.set(display_text)

    def load_data_without_metadata(self, data_path, file_type):
        """Lädt Daten ohne Metadaten"""
        try:
            self.status_var.set("🔄 Lade Daten ohne Metadaten...")

            # Versuche Daten zu laden
            indicators_info = DataUtils.load_punkt3_indicators(data_path)
            if indicators_info:
                # Minimale Metadaten erstellen
                minimal_metadata = {
                    'indicators': [],
                    'timeframes': ['unknown'],
                    'punkt4_ready': False,
                    'vbt_optimized': file_type in ['pickle_blosc', 'pickle', 'hdf5']
                }

                # State aktualisieren
                update_state({
                    'punkt3.metadata': minimal_metadata,
                    'punkt3.indicators_info': indicators_info,
                    'punkt3.timeframes': ['unknown'],
                    'punkt3.indicators_list': [],
                    'punkt3.data_loaded': True
                })

                emit(Events.PUNKT3_DATA_LOADED, {
                    'metadata': minimal_metadata,
                    'indicators_info': indicators_info
                })

                self.status_var.set("✅ Daten geladen (ohne Metadaten)")
            else:
                raise ValueError("Daten konnten nicht geladen werden")

        except Exception as e:
            self.logger.error(f"Laden ohne Metadaten Fehler: {e}")
            self.status_var.set(f"❌ Laden-Fehler: {e}")

    def reload_data(self):
        """Daten neu laden"""
        if self.metadata_file_var.get() and self.indicators_file_var.get():
            self.load_data()
        else:
            self.auto_load_punkt3()

    def test_load_indicators(self):
        """Test-Funktion: Lädt Indikatoren direkt"""
        print("DEBUG: test_load_indicators aufgerufen")

        # Erstelle Test-Daten
        test_metadata = {
            'indicators': [
                {
                    'name': 'MACD',
                    'display_name': 'MACD(12,26,9)',
                    'library': 'vectorbtpro',
                    'params': {'fast_window': 12, 'slow_window': 26, 'signal_window': 9}
                },
                {
                    'name': 'RSI',
                    'display_name': 'RSI(14)',
                    'library': 'vectorbtpro',
                    'params': {'window': 14}
                },
                {
                    'name': 'MA',
                    'display_name': 'MA(20)',
                    'library': 'vectorbtpro',
                    'params': {'window': 20}
                },
                {
                    'name': 'ATR',
                    'display_name': 'ATR(14)',
                    'library': 'vectorbtpro',
                    'params': {'window': 14}
                },
                {
                    'name': 'OBV',
                    'display_name': 'OBV',
                    'library': 'vectorbtpro',
                    'params': {}
                }
            ],
            'timeframes': ['5m'],
            'punkt4_ready': True
        }

        test_indicators_info = {
            'data': None,
            'vbt_data': None,
            'symbols': ['BTCUSDT'],
            'shape': (10000, 25),
            'columns': ['MACD', 'MACD_signal', 'RSI', 'MA_20', 'ATR_14', 'OBV'],
            'file_type': 'test',
            'vbt_optimized': True
        }

        print("DEBUG: Setze Test-Daten in State...")

        # State aktualisieren
        update_state({
            'punkt3.metadata': test_metadata,
            'punkt3.indicators_info': test_indicators_info,
            'punkt3.data_loaded': True
        })

        print("DEBUG: Rufe update_data_overview auf...")

        # UI aktualisieren
        self.update_data_overview()

        self.status_var.set("🧪 Test-Indikatoren geladen")
        self.file_display_var.set("✅ Test-Daten (5 Indikatoren)")

        print("DEBUG: Test-Indikatoren-Laden abgeschlossen")

    def load_vbt_data_directly(self):
        """Lädt die echten VBT Daten direkt"""
        print("DEBUG: load_vbt_data_directly aufgerufen")

        try:
            import json

            # Direkte Pfade zu den echten Dateien
            punkt3_dir = Path("data/punkt3")

            # Finde neueste Metadaten-Datei
            metadata_files = list(punkt3_dir.glob("*_indicators_metadata.json"))
            if not metadata_files:
                print("DEBUG: Keine Metadaten-Dateien gefunden!")
                self.status_var.set("❌ Keine Metadaten-Dateien gefunden")
                return

            metadata_file = max(metadata_files, key=os.path.getctime)
            print(f"DEBUG: Verwende Metadaten-Datei: {metadata_file.name}")

            # Finde passende VBT Daten-Datei
            vbt_files = list(punkt3_dir.glob("*_VBT.pickle.blosc"))
            if not vbt_files:
                print("DEBUG: Keine VBT Daten-Dateien gefunden!")
                self.status_var.set("❌ Keine VBT Daten-Dateien gefunden")
                return

            vbt_file = max(vbt_files, key=os.path.getctime)
            print(f"DEBUG: Verwende VBT Daten-Datei: {vbt_file.name}")

            # Metadaten laden
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            indicators = metadata.get('indicators', [])
            print(f"DEBUG: {len(indicators)} Indikatoren in Metadaten gefunden")

            # VBT Daten laden
            print("DEBUG: Lade VBT Daten...")
            indicators_info = DataUtils.load_punkt3_indicators(vbt_file)

            if indicators_info:
                vbt_data = indicators_info.get('vbt_data')
                print(f"DEBUG: VBT Data Objekt verfügbar: {vbt_data is not None}")

                if vbt_data:
                    print(f"DEBUG: VBT Data Shape: {vbt_data.wrapper.shape if hasattr(vbt_data, 'wrapper') else 'Unknown'}")
                    print(f"DEBUG: VBT Symbols: {list(vbt_data.symbols) if hasattr(vbt_data, 'symbols') else 'Unknown'}")

                # State aktualisieren (ohne DataFrame um Ambiguity zu vermeiden)
                safe_indicators_info = {
                    'vbt_data': indicators_info.get('vbt_data'),
                    'file_type': indicators_info.get('file_type', 'vbt_pickle'),
                    'shape': indicators_info.get('shape'),
                    'columns': indicators_info.get('columns'),
                    'vbt_optimized': indicators_info.get('vbt_optimized', True)
                }

                update_state({
                    'punkt3.metadata': metadata,
                    'punkt3.indicators_info': safe_indicators_info,
                    'punkt3.data_loaded': True
                })

                # UI aktualisieren
                self.update_data_overview()

                self.status_var.set(f"🚀 VBT Daten geladen ({len(indicators)} Indikatoren)")
                self.file_display_var.set(f"✅ VBT Daten ({vbt_file.name})")

                print("DEBUG: VBT Daten-Laden abgeschlossen")

            else:
                print("DEBUG: VBT Daten konnten nicht geladen werden")
                self.status_var.set("❌ VBT Daten konnten nicht geladen werden")

        except Exception as e:
            print(f"DEBUG: Fehler beim Laden der VBT Daten: {e}")
            self.status_var.set(f"❌ VBT Fehler: {e}")




    
    def load_data(self):
        """Punkt 3 Daten laden"""
        metadata_file = self.metadata_file_var.get()
        indicators_file = self.indicators_file_var.get()
        
        if not metadata_file or not indicators_file:
            UIUtils.show_error("Fehler", "Bitte wählen Sie beide Dateien aus")
            return
        
        try:
            self.status_var.set("🔄 Lade Metadaten...")
            
            # Metadaten laden
            metadata = DataUtils.load_punkt3_metadata(Path(metadata_file))
            if not metadata:
                raise ValueError("Metadaten konnten nicht geladen werden")
            
            self.status_var.set("🔄 Lade Indikatoren...")
            
            # Indikatoren laden
            indicators_info = DataUtils.load_punkt3_indicators(Path(indicators_file))
            if not indicators_info:
                raise ValueError("Indikatoren konnten nicht geladen werden")
            
            self.status_var.set("🔄 Validiere Daten...")
            
            # State aktualisieren
            update_state({
                'punkt3.metadata': metadata,
                'punkt3.indicators_info': indicators_info,
                'punkt3.timeframes': metadata.get('timeframes', []),
                'punkt3.indicators_list': metadata.get('indicators', []),
                'punkt3.data_loaded': True
            })
            
            emit(Events.PUNKT3_DATA_LOADED, {
                'metadata': metadata, 
                'indicators_info': indicators_info
            })
            
        except Exception as e:
            self.logger.error(f"Daten-Laden Fehler: {e}")
            emit(Events.PUNKT3_DATA_ERROR, {'error': str(e)})
    
    def reset_files(self):
        """Dateien zurücksetzen"""
        self.metadata_file_var.set("")
        self.indicators_file_var.set("")
        
        update_state({
            'punkt3.metadata_file': None,
            'punkt3.indicators_file': None,
            'punkt3.metadata': None,
            'punkt3.indicators_info': None,
            'punkt3.data_loaded': False
        })
        
        self.update_data_overview()
        self.code_text.delete(1.0, tk.END)
        self.status_var.set("🔄 Dateien zurückgesetzt")
    
    def update_from_state(self):
        """UI von State aktualisieren"""
        metadata_file = get_state('punkt3.metadata_file')
        indicators_file = get_state('punkt3.indicators_file')
        
        if metadata_file:
            self.metadata_file_var.set(metadata_file)
        if indicators_file:
            self.indicators_file_var.set(indicators_file)
        
        self.update_data_overview()
    
    def update_data_overview(self):
        """Erweiterte Daten-Analyse aktualisieren"""
        metadata = get_state('punkt3.metadata')
        indicators_info = get_state('punkt3.indicators_info')

        print(f"DEBUG: update_data_overview aufgerufen")
        print(f"DEBUG: metadata vorhanden: {metadata is not None}")
        print(f"DEBUG: indicators_info vorhanden: {indicators_info is not None}")

        if metadata:
            indicators = metadata.get('indicators', [])
            print(f"DEBUG: {len(indicators)} Indikatoren in Metadaten gefunden")
            print(f"DEBUG: Metadaten Keys: {list(metadata.keys())}")
            if indicators:
                print(f"DEBUG: Erster Indikator: {indicators[0]}")
            else:
                print("DEBUG: Indicators-Liste ist leer!")

        if metadata and indicators_info:
            self.update_asset_info(metadata, indicators_info)
            self.update_indicators_info(metadata, indicators_info)
            self.update_vbt_optimization_info(metadata, indicators_info)
            self.update_file_info(metadata, indicators_info)
        else:
            print("DEBUG: Keine Daten verfügbar - Labels werden zurückgesetzt")
            self.reset_all_labels()

    def update_asset_info(self, metadata, indicators_info):
        """Asset & Zeitraum Informationen aktualisieren"""
        try:
            # Asset Informationen aus DataFrame extrahieren
            data = indicators_info.get('data')
            symbols = indicators_info.get('symbols', [])

            # Wenn keine Symbols, versuche aus DataFrame zu extrahieren
            if not symbols or symbols == ['data']:
                if data is not None and hasattr(data, 'columns'):
                    # Versuche Asset-Namen aus Spalten zu extrahieren
                    potential_assets = set()
                    for col in data.columns:
                        # Extrahiere Asset-Namen (vor dem ersten Unterstrich)
                        if '_' in col:
                            asset = col.split('_')[0]
                            potential_assets.add(asset)

                    if potential_assets:
                        symbols = list(potential_assets)
                    else:
                        symbols = ['UNKNOWN_ASSET']

            # Asset-Anzeige
            if len(symbols) <= 5:
                assets_text = ', '.join(symbols)
            else:
                assets_text = ', '.join(symbols[:5]) + f' ... (+{len(symbols)-5} weitere)'

            self.assets_label.config(text=f"Assets: {assets_text}")
            self.asset_count_label.config(text=f"Anzahl Assets: {len(symbols)}")

            # Asset-Typen bestimmen
            asset_types = []
            for symbol in symbols[:3]:
                symbol_upper = symbol.upper()
                if any(x in symbol_upper for x in ['BTC', 'ETH', 'USD', 'EUR']):
                    asset_types.append('Crypto/Forex')
                elif any(x in symbol_upper for x in ['AAPL', 'MSFT', 'GOOGL', 'TSLA']):
                    asset_types.append('Stocks')
                else:
                    asset_types.append('Unknown')

            unique_types = list(set(asset_types)) if asset_types else ['Unknown']
            self.asset_types_label.config(text=f"Asset-Typen: {', '.join(unique_types)}")

            # Zeitraum Informationen
            start_date = indicators_info.get('index_start')
            end_date = indicators_info.get('index_end')

            if start_date and end_date:
                date_range = f"{start_date.strftime('%Y-%m-%d')} bis {end_date.strftime('%Y-%m-%d')}"
                self.date_range_label.config(text=f"Zeitraum: {date_range}")

                # Zeitraum-Länge berechnen
                duration = end_date - start_date
                self.duration_label.config(text=f"Zeitraum-Länge: {duration.days} Tage")
            else:
                self.date_range_label.config(text="Zeitraum: Nicht verfügbar")
                self.duration_label.config(text="Zeitraum-Länge: Unbekannt")

            # Timeframe
            freq = indicators_info.get('freq')
            if freq:
                self.timeframe_label.config(text=f"Timeframe: {freq}")
            else:
                timeframes = metadata.get('timeframes', [])
                if timeframes:
                    self.timeframe_label.config(text=f"Timeframe: {', '.join(timeframes)}")
                else:
                    self.timeframe_label.config(text="Timeframe: Unbekannt")

            # Daten-Struktur
            shape = indicators_info.get('shape', (0, 0))
            if shape[0] > 0 and shape[1] > 0:
                self.data_shape_label.config(text=f"Shape: {shape[0]:,} × {shape[1]:,}")
                self.data_points_label.config(text=f"Datenpunkte: {shape[0]:,}")
                self.columns_count_label.config(text=f"Spalten: {shape[1]:,}")

                # Memory Usage schätzen
                estimated_mb = (shape[0] * shape[1] * 8) / (1024 * 1024)  # 8 bytes für float64
                self.memory_usage_label.config(text=f"Memory Usage: ~{estimated_mb:.1f} MB")
            else:
                self.data_shape_label.config(text="Shape: Keine Daten")
                self.data_points_label.config(text="Datenpunkte: 0")
                self.columns_count_label.config(text="Spalten: 0")
                self.memory_usage_label.config(text="Memory Usage: 0 MB")

        except Exception as e:
            self.logger.error(f"Asset Info Update Fehler: {e}")
            # Fallback-Werte setzen
            self.assets_label.config(text="Assets: Fehler beim Laden")
            self.asset_count_label.config(text="Anzahl Assets: Unbekannt")
            self.asset_types_label.config(text="Asset-Typen: Unbekannt")

    def update_indicators_info(self, metadata, indicators_info):
        """Indikator-Informationen aktualisieren"""
        try:
            indicators = metadata.get('indicators', [])

            # Debug: Prüfe ob Indikatoren vorhanden
            print(f"DEBUG: update_indicators_info aufgerufen mit {len(indicators)} Indikatoren")
            self.logger.info(f"Lade {len(indicators)} Indikatoren aus Metadaten")

            # Statistiken
            self.indicators_count_label.config(text=f"Anzahl Indikatoren: {len(indicators)}")
            print(f"DEBUG: indicators_count_label aktualisiert: {len(indicators)}")

            # Bibliotheken sammeln
            libraries = list(set([ind.get('library', 'unknown') for ind in indicators]))
            self.libraries_label.config(text=f"Bibliotheken: {', '.join(libraries)}")
            print(f"DEBUG: libraries_label aktualisiert: {libraries}")

            # OHLCV Spalten aus DataFrame extrahieren
            data = indicators_info.get('data')
            if data is not None:
                ohlcv_cols = []
                for col_type in ['open', 'high', 'low', 'close', 'volume']:
                    for col in data.columns:
                        if col_type in col.lower():
                            ohlcv_cols.append(col_type.upper())
                            break
                self.ohlcv_label.config(text=f"OHLCV Spalten: {', '.join(ohlcv_cols)}")
                print(f"DEBUG: OHLCV Spalten gefunden: {ohlcv_cols}")
            else:
                self.ohlcv_label.config(text="OHLCV Spalten: Keine Daten")
                print("DEBUG: Keine DataFrame-Daten verfügbar")

            # Indikator-Tree leeren
            print("DEBUG: Leere TreeView...")
            self.indicators_tree.delete(*self.indicators_tree.get_children())

            # Indikatoren zur Tree hinzufügen
            print(f"DEBUG: Füge {len(indicators)} Indikatoren zur TreeView hinzu...")
            for i, indicator in enumerate(indicators):
                try:
                    # Indikator-Informationen extrahieren
                    name = indicator.get('name', f'Indicator_{i+1}')
                    display_name = indicator.get('display_name', name)
                    library = indicator.get('library', 'unknown')
                    params = indicator.get('params', {})

                    print(f"DEBUG: Verarbeite Indikator {i+1}: {display_name} ({library})")

                    # Parameter als String formatieren
                    if params:
                        param_items = []
                        for k, v in params.items():
                            param_items.append(f"{k}={v}")
                        param_str = ', '.join(param_items)
                        if len(param_str) > 40:
                            param_str = param_str[:37] + '...'
                    else:
                        param_str = 'Default'

                    # Spalten zählen (aus DataFrame)
                    col_count = 1  # Default
                    if data is not None:
                        # Suche nach Spalten die zu diesem Indikator gehören
                        matching_cols = []
                        for col in data.columns:
                            # Verschiedene Matching-Strategien
                            if (name.lower() in col.lower() or
                                display_name.lower() in col.lower() or
                                any(name.lower() in part.lower() for part in col.split('_'))):
                                matching_cols.append(col)

                        if matching_cols:
                            col_count = len(matching_cols)

                    # Zur TreeView hinzufügen
                    item_id = self.indicators_tree.insert('', 'end', values=(
                        display_name,
                        library.upper(),
                        param_str,
                        col_count
                    ))

                    print(f"DEBUG: Indikator {display_name} zur TreeView hinzugefügt (ID: {item_id})")
                    self.logger.debug(f"Indikator hinzugefügt: {display_name} ({library}) - {col_count} Spalten")

                except Exception as e:
                    print(f"DEBUG: Fehler bei Indikator {i}: {e}")
                    self.logger.error(f"Fehler beim Hinzufügen von Indikator {i}: {e}")
                    # Fallback: Minimale Informationen
                    self.indicators_tree.insert('', 'end', values=(
                        f"Indicator_{i+1}",
                        "unknown",
                        "Error",
                        1
                    ))

            # Prüfe TreeView Inhalt
            tree_items = self.indicators_tree.get_children()
            print(f"DEBUG: TreeView hat jetzt {len(tree_items)} Items")

            self.logger.info(f"✅ {len(indicators)} Indikatoren zur Liste hinzugefügt")

        except Exception as e:
            print(f"DEBUG: Fehler in update_indicators_info: {e}")
            self.logger.error(f"Indicators Info Update Fehler: {e}")
            # Fallback-Werte setzen
            self.indicators_count_label.config(text="Anzahl Indikatoren: Fehler")
            self.libraries_label.config(text="Bibliotheken: Fehler")
            self.ohlcv_label.config(text="OHLCV Spalten: Fehler")

    def update_vbt_optimization_info(self, metadata, indicators_info):
        """VBT Pro Optimierungen aktualisieren"""
        try:
            import vectorbtpro as vbt

            # VBT Data Objekt Status
            vbt_data = indicators_info.get('vbt_data')
            if vbt_data:
                self.vbt_data_status_label.config(text="VBT Data Objekt: ✅ Verfügbar", foreground='green')

                # Wrapper Info
                try:
                    if hasattr(vbt_data, 'wrapper'):
                        wrapper = vbt_data.wrapper
                        freq_info = getattr(wrapper, 'freq', 'Unknown')
                        shape_info = getattr(wrapper, 'shape', 'Unknown')
                        self.vbt_wrapper_label.config(text=f"Wrapper Info: Freq={freq_info}, Shape={shape_info}")
                    else:
                        self.vbt_wrapper_label.config(text="Wrapper Info: Nicht verfügbar")
                except Exception as e:
                    self.vbt_wrapper_label.config(text=f"Wrapper Info: Fehler - {e}")

                # VBT Symbols
                try:
                    if hasattr(vbt_data, 'symbols'):
                        symbols = list(vbt_data.symbols)
                        if len(symbols) <= 3:
                            symbol_text = ', '.join(symbols)
                        else:
                            symbol_text = ', '.join(symbols[:3]) + f' ... (+{len(symbols)-3})'
                        self.vbt_symbols_label.config(text=f"VBT Symbols: {symbol_text}")
                    else:
                        self.vbt_symbols_label.config(text="VBT Symbols: Nicht verfügbar")
                except Exception as e:
                    self.vbt_symbols_label.config(text=f"VBT Symbols: Fehler - {e}")
            else:
                self.vbt_data_status_label.config(text="VBT Data Objekt: ❌ Nicht verfügbar", foreground='red')
                self.vbt_wrapper_label.config(text="Wrapper Info: -")
                self.vbt_symbols_label.config(text="VBT Symbols: -")

            # Numba Status prüfen
            try:
                import numba
                numba_version = numba.__version__
                self.numba_status_label.config(text=f"Numba Status: ✅ v{numba_version}", foreground='green')

                # Numba Parallel prüfen
                try:
                    parallel_enabled = vbt.settings.numba.get('parallel', False)
                    self.numba_parallel_label.config(text=f"Parallel Processing: {'✅ Aktiviert' if parallel_enabled else '❌ Deaktiviert'}")
                except:
                    self.numba_parallel_label.config(text="Parallel Processing: ❓ Unbekannt")

                # Numba Cache prüfen
                try:
                    cache_enabled = vbt.settings.numba.get('cache', False)
                    self.numba_cache_label.config(text=f"Numba Cache: {'✅ Aktiviert' if cache_enabled else '❌ Deaktiviert'}")
                except:
                    self.numba_cache_label.config(text="Numba Cache: ❓ Unbekannt")

            except ImportError:
                self.numba_status_label.config(text="Numba Status: ❌ Nicht installiert", foreground='red')
                self.numba_parallel_label.config(text="Parallel Processing: ❌ Numba fehlt")
                self.numba_cache_label.config(text="Numba Cache: ❌ Numba fehlt")

            # Chunking Status
            try:
                chunking_enabled = vbt.settings.chunking.get('enabled', False)
                chunk_size = vbt.settings.chunking.get('chunk_size', 'Unknown')
                self.chunking_label.config(text=f"Chunking: {'✅' if chunking_enabled else '❌'} (Size: {chunk_size})")
            except:
                self.chunking_label.config(text="Chunking: ❓ Unbekannt")

            # Kompression und Performance
            file_type = indicators_info.get('file_type', '')
            if 'blosc' in file_type:
                self.compression_label.config(text="Kompression: ✅ Blosc (optimal)", foreground='green')
                self.speed_improvement_label.config(text="Geschwindigkeits-Verbesserung: 🚀 20x+ (VBT+Blosc+Numba)", foreground='green')
                self.memory_efficiency_label.config(text="Memory-Effizienz: ✅ Excellent (Blosc)", foreground='green')
                self.scalability_label.config(text="Skalierbarkeit: ✅ Excellent (Chunking+Parallel)", foreground='green')
            elif 'pickle' in file_type:
                self.compression_label.config(text="Kompression: ⚠️ Standard Pickle", foreground='orange')
                self.speed_improvement_label.config(text="Geschwindigkeits-Verbesserung: ⚡ 5-10x (VBT+Numba)", foreground='orange')
                self.memory_efficiency_label.config(text="Memory-Effizienz: ⚠️ Standard", foreground='orange')
                self.scalability_label.config(text="Skalierbarkeit: ⚠️ Begrenzt", foreground='orange')
            elif file_type == 'hdf5':
                self.compression_label.config(text="Kompression: 📊 HDF5 (gut)", foreground='blue')
                self.speed_improvement_label.config(text="Geschwindigkeits-Verbesserung: ⚡ 3-5x (HDF5)", foreground='blue')
                self.memory_efficiency_label.config(text="Memory-Effizienz: ✅ Gut (HDF5)", foreground='blue')
                self.scalability_label.config(text="Skalierbarkeit: ✅ Gut", foreground='blue')
            else:
                self.compression_label.config(text="Kompression: ❌ Keine", foreground='red')
                self.speed_improvement_label.config(text="Geschwindigkeits-Verbesserung: ❌ Standard Pandas", foreground='red')
                self.memory_efficiency_label.config(text="Memory-Effizienz: ❌ Nicht optimiert", foreground='red')
                self.scalability_label.config(text="Skalierbarkeit: ❌ Begrenzt", foreground='red')

            # Datentyp-Optimierung
            data = indicators_info.get('data')
            if data is not None:
                try:
                    float64_cols = sum(1 for dtype in data.dtypes if str(dtype) == 'float64')
                    total_cols = len(data.dtypes)
                    percentage = (float64_cols / total_cols * 100) if total_cols > 0 else 0

                    if percentage >= 90:
                        self.dtype_optimization_label.config(text=f"Datentyp-Optimierung: ✅ {float64_cols}/{total_cols} Float64 ({percentage:.0f}%)", foreground='green')
                    elif percentage >= 70:
                        self.dtype_optimization_label.config(text=f"Datentyp-Optimierung: ⚠️ {float64_cols}/{total_cols} Float64 ({percentage:.0f}%)", foreground='orange')
                    else:
                        self.dtype_optimization_label.config(text=f"Datentyp-Optimierung: ❌ {float64_cols}/{total_cols} Float64 ({percentage:.0f}%)", foreground='red')
                except Exception as e:
                    self.dtype_optimization_label.config(text=f"Datentyp-Optimierung: Fehler - {e}")
            else:
                self.dtype_optimization_label.config(text="Datentyp-Optimierung: Keine Daten")

        except Exception as e:
            self.logger.error(f"VBT Optimization Update Fehler: {e}")
            # Fallback-Werte
            self.vbt_data_status_label.config(text=f"VBT Data Objekt: Fehler - {e}", foreground='red')
            self.numba_status_label.config(text="Numba Status: Fehler", foreground='red')

    def update_file_info(self, metadata, indicators_info):
        """Datei-Informationen aktualisieren"""
        try:
            # Dateipfad
            file_path = get_state('punkt3.indicators_file')
            if file_path:
                self.file_path_label.config(text=f"Dateipfad: {Path(file_path).name}")

                # Dateigröße
                try:
                    import os
                    file_size = os.path.getsize(file_path)
                    size_mb = file_size / (1024 * 1024)
                    self.file_size_label.config(text=f"Dateigröße: {size_mb:.1f} MB")
                except:
                    self.file_size_label.config(text="Dateigröße: Unbekannt")

                # Dateityp
                file_type = indicators_info.get('file_type', 'unknown')
                self.file_type_label.config(text=f"Dateityp: {file_type}")

            # Punkt 4 Kompatibilität
            vbt_optimized = indicators_info.get('vbt_optimized', False)
            punkt4_ready = metadata.get('punkt4_ready', False)

            if vbt_optimized and punkt4_ready:
                self.punkt4_compatibility_label.config(text="Punkt 4 Kompatibilität: ✅ Vollständig kompatibel", foreground='green')
            elif vbt_optimized:
                self.punkt4_compatibility_label.config(text="Punkt 4 Kompatibilität: ⚠️ VBT optimiert", foreground='orange')
            else:
                self.punkt4_compatibility_label.config(text="Punkt 4 Kompatibilität: ❌ Nicht optimiert", foreground='red')

        except Exception as e:
            self.logger.error(f"File Info Update Fehler: {e}")

    def reset_all_labels(self):
        """Alle Labels zurücksetzen"""
        try:
            # Asset Info
            self.assets_label.config(text="Assets: -")
            self.asset_count_label.config(text="Anzahl Assets: -")
            self.date_range_label.config(text="Zeitraum: -")
            self.timeframe_label.config(text="Timeframe: -")
            self.data_points_label.config(text="Datenpunkte: -")
            self.duration_label.config(text="Zeitraum-Länge: -")
            self.data_shape_label.config(text="Shape: -")
            self.columns_count_label.config(text="Spalten: -")

            # Indicators
            self.indicators_count_label.config(text="Anzahl Indikatoren: -")
            self.libraries_label.config(text="Bibliotheken: -")
            self.indicators_tree.delete(*self.indicators_tree.get_children())

            # VBT Optimization
            self.vbt_data_status_label.config(text="VBT Data Objekt: -", foreground='black')
            self.compression_label.config(text="Kompression: -", foreground='black')
            self.speed_improvement_label.config(text="Geschwindigkeits-Verbesserung: -", foreground='black')

            # File Info
            self.file_path_label.config(text="Dateipfad: -")
            self.file_size_label.config(text="Dateigröße: -")
            self.file_type_label.config(text="Dateityp: -")
            self.punkt4_compatibility_label.config(text="Punkt 4 Kompatibilität: -", foreground='black')

        except Exception as e:
            self.logger.error(f"Reset Labels Fehler: {e}")
    
    def on_export_target_changed(self, event=None):
        """Export-Ziel geändert"""
        target = self.export_target_var.get()
        if target == "punkt5":
            self.export_info_label.config(text="Punkt 5: Strategie-Entwicklung")
        elif target == "punkt6":
            self.export_info_label.config(text="Punkt 6: Backtesting mit Performance-Analyse")
    
    def generate_code(self):
        """Code generieren"""
        if not get_state('punkt3.data_loaded'):
            UIUtils.show_error("Fehler", "Bitte laden Sie zuerst Punkt 3 Daten")
            return

        try:
            vbt_parameters = get_state('vbt_parameters')

            # Punkt 3 Info sammeln
            metadata = get_state('punkt3.metadata')
            indicators_info = get_state('punkt3.indicators_info')

            # Datei-Pfade aus aktuellen Daten extrahieren
            metadata_file = None
            indicators_file = None

            if metadata and indicators_info:
                # Versuche Pfade aus State zu holen oder aus aktuellen Daten zu rekonstruieren
                punkt3_dir = Path("data/punkt3")

                # Finde neueste Metadaten-Datei
                metadata_files = list(punkt3_dir.glob("*_metadata.json"))
                if metadata_files:
                    metadata_file = str(max(metadata_files, key=os.path.getctime))

                # Finde passende VBT Daten-Datei
                vbt_files = list(punkt3_dir.glob("*_VBT.pickle.blosc"))
                if vbt_files:
                    indicators_file = str(max(vbt_files, key=os.path.getctime))
                elif list(punkt3_dir.glob("*_VBT.pickle")):
                    indicators_file = str(max(punkt3_dir.glob("*_VBT.pickle"), key=os.path.getctime))
                elif list(punkt3_dir.glob("*.csv")):
                    indicators_file = str(max(punkt3_dir.glob("*.csv"), key=os.path.getctime))

            punkt3_info = {
                'metadata_file': metadata_file,
                'indicators_file': indicators_file,
                'metadata': metadata,
                'indicators_info': indicators_info
            }

            print(f"DEBUG: Punkt3 Info - Metadata: {metadata_file}")
            print(f"DEBUG: Punkt3 Info - Indicators: {indicators_file}")

            target = self.export_target_var.get()

            if target == "punkt5":
                code = CodeGenerator.generate_punkt5_code(vbt_parameters, punkt3_info)
            elif target == "punkt6":
                code = CodeGenerator.generate_punkt6_code(vbt_parameters, punkt3_info)
            else:
                raise ValueError(f"Unbekanntes Export-Ziel: {target}")

            # Code und Parameter in State speichern
            update_state({
                f'export.{target}_code': code,
                f'export.{target}_vbt_parameters': vbt_parameters
            })

            emit(Events.CODE_GENERATED, {
                'code': code,
                'target': target
            })

            # GUI GENERIERT NUR CODE
            # VBT Pro Export erfolgt im Notebook

            print(f"DEBUG: Code generiert für {target}")

        except Exception as e:
            self.logger.error(f"Code-Generation Fehler: {e}")
            UIUtils.show_error("Code-Generation Fehler", str(e))

    # Alte Speicher-Funktion entfernt - VBT Pro Export erfolgt im Notebook

    def save_code(self):
        """Code in Datei speichern"""
        code = self.code_text.get(1.0, tk.END).strip()
        if not code:
            UIUtils.show_warning("Warnung", "Kein Code zum Speichern vorhanden")
            return
        
        target = self.export_target_var.get()
        default_filename = f"punkt4_{target}_code.py"
        
        file_path = UIUtils.save_file(
            f"Punkt 4 Code für {target.upper()} speichern",
            [('Python Dateien', '*.py'), ('Alle Dateien', '*.*')],
            str(CONFIG.PATHS['punkt4_exports']),
            '.py'
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                self.status_var.set(f"✅ Code gespeichert: {Path(file_path).name}")
                emit(Events.EXPORT_COMPLETED, {'file_path': file_path, 'target': target})
                
            except Exception as e:
                self.logger.error(f"Code-Speichern Fehler: {e}")
                UIUtils.show_error("Speichern Fehler", str(e))
    
    def copy_code(self):
        """Code in Zwischenablage kopieren"""
        code = self.code_text.get(1.0, tk.END).strip()
        if not code:
            UIUtils.show_warning("Warnung", "Kein Code zum Kopieren vorhanden")
            return
        
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(code)
            self.status_var.set("✅ Code in Zwischenablage kopiert")
        except Exception as e:
            self.logger.error(f"Code-Kopieren Fehler: {e}")
            UIUtils.show_error("Kopieren Fehler", str(e))
