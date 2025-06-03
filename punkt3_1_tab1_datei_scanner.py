#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punkt3.1 Tab1 - Datei Scanner und Informationsanzeige
Tab für das Scannen, Auswählen und Anzeigen von VectorbtPro-Dateien

Autor: AI Assistant
Datum: 2025-06-02
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import threading

class Tab1DateiScanner:
    """
    Tab 1: Datei Scanner und Informationsanzeige
    """
    
    def __init__(self, parent, data_manager, data_loaded_callback: Callable):
        self.parent = parent
        self.data_manager = data_manager
        self.data_loaded_callback = data_loaded_callback
        
        self.current_directory = os.getcwd()
        self.scanned_files = []
        self.selected_file = None
        self.current_data = None
        self.current_metadata = None
        
        self.create_widgets()
        self.setup_bindings()
        
        # Automatischer Scan beim Start
        self.scan_directory()
        
    def create_widgets(self):
        """Erstellt die GUI-Widgets für Tab 1"""
        # Hauptframe
        self.frame = ttk.Frame(self.parent, padding="10")
        
        # Erstelle Notebook für Untertabs
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Sub-Tab 1: Datei-Scanner
        self.create_scanner_tab()
        
        # Sub-Tab 2: Datei-Informationen
        self.create_info_tab()
        
    def create_scanner_tab(self):
        """Erstellt den Scanner-Tab"""
        scanner_frame = ttk.Frame(self.sub_notebook, padding="10")
        self.sub_notebook.add(scanner_frame, text="Datei Scanner")
        
        # Verzeichnis-Auswahl Sektion
        dir_frame = ttk.LabelFrame(scanner_frame, text="Scan-Verzeichnis", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Aktuelles Verzeichnis
        ttk.Label(dir_frame, text="Aktuelles Verzeichnis:").pack(anchor=tk.W)
        
        dir_path_frame = ttk.Frame(dir_frame)
        dir_path_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.dir_var = tk.StringVar(value=self.current_directory)
        self.dir_entry = ttk.Entry(dir_path_frame, textvariable=self.dir_var, state="readonly")
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(dir_path_frame, text="Durchsuchen", command=self.browse_directory).pack(side=tk.RIGHT)
        
        # Scan-Optionen
        options_frame = ttk.Frame(dir_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Unterverzeichnisse einschließen", variable=self.recursive_var).pack(side=tk.LEFT)
        
        self.max_depth_var = tk.IntVar(value=3)
        ttk.Label(options_frame, text="Max. Tiefe:").pack(side=tk.LEFT, padx=(20, 5))
        depth_spin = ttk.Spinbox(options_frame, from_=1, to=10, width=5, textvariable=self.max_depth_var)
        depth_spin.pack(side=tk.LEFT)
        
        # Scan-Button
        scan_button_frame = ttk.Frame(dir_frame)
        scan_button_frame.pack(fill=tk.X)
        
        self.scan_button = ttk.Button(scan_button_frame, text="Verzeichnis scannen", command=self.scan_directory)
        self.scan_button.pack(side=tk.LEFT)
        
        self.scan_progress = ttk.Progressbar(scan_button_frame, mode='indeterminate')
        self.scan_progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Gefundene Dateien Sektion
        files_frame = ttk.LabelFrame(scanner_frame, text="Gefundene Dateien", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Filter-Optionen
        filter_frame = ttk.Frame(files_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT)
        
        self.filter_var = tk.StringVar()
        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=20)
        filter_entry.pack(side=tk.LEFT, padx=(5, 10))
        filter_entry.bind('<KeyRelease>', self.on_filter_changed)
        
        self.show_single_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(filter_frame, text="Single-TF", variable=self.show_single_var, command=self.apply_filters).pack(side=tk.LEFT, padx=(10, 5))
        
        self.show_multi_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(filter_frame, text="Multi-TF", variable=self.show_multi_var, command=self.apply_filters).pack(side=tk.LEFT, padx=(5, 10))
        
        # Dateien-Liste
        list_frame = ttk.Frame(files_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview für Dateien
        columns = ('Name', 'Typ', 'Größe', 'Geändert', 'Timeframe')
        self.files_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # Spalten konfigurieren
        self.files_tree.heading('Name', text='Dateiname')
        self.files_tree.heading('Typ', text='Typ')
        self.files_tree.heading('Größe', text='Größe')
        self.files_tree.heading('Geändert', text='Geändert')
        self.files_tree.heading('Timeframe', text='Timeframe')
        
        self.files_tree.column('Name', width=300)
        self.files_tree.column('Typ', width=120)
        self.files_tree.column('Größe', width=80)
        self.files_tree.column('Geändert', width=120)
        self.files_tree.column('Timeframe', width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.files_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.files_tree.xview)
        self.files_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid Layout
        self.files_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Datei-Auswahl Buttons
        button_frame = ttk.Frame(files_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Ausgewählte Datei laden", command=self.load_selected_file).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Eigene Datei wählen", command=self.browse_file).pack(side=tk.LEFT, padx=(10, 0))
        
        # Status
        self.status_var = tk.StringVar(value="Bereit zum Scannen")
        ttk.Label(button_frame, textvariable=self.status_var).pack(side=tk.RIGHT)
        
    def create_info_tab(self):
        """Erstellt den Informations-Tab"""
        info_frame = ttk.Frame(self.sub_notebook, padding="10")
        self.sub_notebook.add(info_frame, text="Datei Informationen")
        
        # Scrollable Frame für Informationen
        canvas = tk.Canvas(info_frame)
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Info-Widgets werden dynamisch erstellt
        self.info_widgets = {}
        self.create_empty_info_display()
        
    def create_empty_info_display(self):
        """Erstellt leere Informationsanzeige"""
        empty_label = ttk.Label(
            self.scrollable_frame, 
            text="Keine Datei geladen.\n\nBitte wählen Sie eine Datei im Scanner-Tab aus.",
            font=('Arial', 12),
            foreground='gray'
        )
        empty_label.pack(expand=True, pady=50)
        self.info_widgets['empty'] = empty_label
        
    def setup_bindings(self):
        """Setzt Event-Bindings auf"""
        self.files_tree.bind('<Double-1>', self.on_file_double_click)
        self.files_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        
    def browse_directory(self):
        """Öffnet Dialog zur Verzeichnisauswahl"""
        directory = filedialog.askdirectory(
            title="Scan-Verzeichnis auswählen",
            initialdir=self.current_directory
        )
        
        if directory:
            self.current_directory = directory
            self.dir_var.set(directory)
            self.scan_directory()
            
    def scan_directory(self):
        """Scannt das aktuelle Verzeichnis nach Dateien"""
        def scan_worker():
            try:
                self.scan_progress.start()
                self.scan_button.configure(state='disabled')
                self.status_var.set("Scannen...")
                
                # Scannen
                files = self.data_manager.scan_directory(
                    self.current_directory,
                    recursive=self.recursive_var.get(),
                    max_depth=self.max_depth_var.get()
                )
                
                # UI Update im Hauptthread
                self.frame.after(0, lambda: self.update_files_list(files))
                
            except Exception as e:
                self.frame.after(0, lambda: self.show_scan_error(str(e)))
            finally:
                self.frame.after(0, self.scan_completed)
                
        # Scan in separatem Thread
        thread = threading.Thread(target=scan_worker, daemon=True)
        thread.start()
        
    def update_files_list(self, files: List[Dict[str, Any]]):
        """Aktualisiert die Dateien-Liste"""
        self.scanned_files = files
        self.apply_filters()
        
    def apply_filters(self):
        """Wendet Filter auf die Dateien-Liste an"""
        # Treeview leeren
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
            
        filter_text = self.filter_var.get().lower()
        show_single = self.show_single_var.get()
        show_multi = self.show_multi_var.get()
        
        filtered_files = []
        
        for file_info in self.scanned_files:
            # Text-Filter
            if filter_text and filter_text not in file_info['name'].lower():
                continue
                
            # Timeframe-Filter
            if file_info['is_single_timeframe'] and not show_single:
                continue
            if file_info['is_multi_timeframe'] and not show_multi:
                continue
                
            filtered_files.append(file_info)
            
        # Dateien zur Treeview hinzufügen
        for file_info in filtered_files:
            size_str = self.format_file_size(file_info['size'])
            modified_str = file_info['modified'].strftime('%Y-%m-%d %H:%M')
            
            timeframe_type = ""
            if file_info['is_single_timeframe']:
                timeframe_type = "Single"
            elif file_info['is_multi_timeframe']:
                timeframe_type = "Multi"
                
            self.files_tree.insert('', tk.END, values=(
                file_info['name'],
                file_info['type'],
                size_str,
                modified_str,
                timeframe_type
            ), tags=(file_info['path'],))
            
        self.status_var.set(f"{len(filtered_files)} Dateien gefunden")
        
    def format_file_size(self, size_bytes: int) -> str:
        """Formatiert Dateigröße"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
            
    def on_filter_changed(self, event):
        """Callback für Filter-Änderungen"""
        self.apply_filters()
        
    def on_file_select(self, event):
        """Callback für Datei-Auswahl"""
        selection = self.files_tree.selection()
        if selection:
            item = self.files_tree.item(selection[0])
            file_path = item['tags'][0]
            self.selected_file = file_path
            
    def on_file_double_click(self, event):
        """Callback für Doppelklick auf Datei"""
        self.load_selected_file()
        
    def load_selected_file(self):
        """Lädt die ausgewählte Datei"""
        if not self.selected_file:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Datei aus.")
            return
            
        self.load_file(self.selected_file)
        
    def browse_file(self):
        """Öffnet Dialog zur Dateiauswahl"""
        filetypes = [
            ('VBT Blosc Pickle', '*.pickle.blosc'),
            ('VBT Pickle', '*.pickle'),
            ('HDF5', '*.h5;*.hdf5'),
            ('Parquet', '*.parquet'),
            ('CSV', '*.csv'),
            ('Alle unterstützten', '*.pickle.blosc;*.pickle;*.h5;*.hdf5;*.parquet;*.csv'),
            ('Alle Dateien', '*.*')
        ]
        
        file_path = filedialog.askopenfilename(
            title="Datei auswählen",
            initialdir=self.current_directory,
            filetypes=filetypes
        )
        
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, file_path: str):
        """Lädt eine Datei"""
        def load_worker():
            try:
                self.status_var.set("Lade Datei...")
                
                # Daten laden
                data, metadata = self.data_manager.load_data(file_path)
                
                # Daten analysieren
                analysis = self.data_manager.analyze_data(data, metadata)
                
                # UI Update im Hauptthread
                self.frame.after(0, lambda: self.on_file_loaded(data, metadata, analysis, file_path))
                
            except Exception as e:
                error_msg = str(e)
                self.frame.after(0, lambda: self.show_load_error(error_msg))
                
        # Laden in separatem Thread
        thread = threading.Thread(target=load_worker, daemon=True)
        thread.start()
        
    def on_file_loaded(self, data, metadata: Dict[str, Any], analysis: Dict[str, Any], file_path: str):
        """Callback wenn Datei geladen wurde"""
        self.current_data = data
        self.current_metadata = metadata
        
        # Informationen anzeigen
        self.display_file_info(data, metadata, analysis, file_path)
        
        # Callback an Hauptanwendung
        self.data_loaded_callback(data, metadata, file_path)
        
        # Zum Info-Tab wechseln
        self.sub_notebook.select(1)
        
        self.status_var.set(f"Datei geladen: {os.path.basename(file_path)}")
        
    def display_file_info(self, data, metadata: Dict[str, Any], analysis: Dict[str, Any], file_path: str):
        """Zeigt Datei-Informationen vollständig und strukturiert an"""
        # Alte Widgets entfernen
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.info_widgets.clear()
        
        # Titel
        title_label = ttk.Label(
            self.scrollable_frame,
            text=f"Datei-Informationen: {os.path.basename(file_path)}",
            font=('Arial', 14, 'bold'),
            foreground='blue'
        )
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Dateipfad
        path_frame = ttk.LabelFrame(self.scrollable_frame, text="Dateipfad", padding="10")
        path_frame.pack(fill=tk.X, pady=(0, 10))
        path_label = ttk.Label(path_frame, text=file_path, font=('Courier', 9))
        path_label.pack(anchor=tk.W)
        
        # Basis-Informationen
        self.create_detailed_info_section("📊 Basis-Informationen", analysis['basic_info'])
        
        # Zeitrahmen-Informationen
        self.create_detailed_info_section("⏰ Zeitrahmen-Informationen", analysis['timeframe_info'])
        
        # Asset-Informationen
        self.create_detailed_info_section("💰 Asset-Informationen", analysis['asset_info'])
        
        # Indikatoren (vollständig anzeigen)
        if analysis['indicators']:
            self.create_indicators_section("📈 Vorhandene Indikatoren", analysis['indicators'])
            
        # Performance Features (vollständig anzeigen)
        if analysis['performance_features']:
            self.create_features_section("🚀 Performance Features", analysis['performance_features'])
            
        # Verfügbare Features (vollständig anzeigen)
        if analysis['available_features']:
            self.create_features_section("🔧 Verfügbare VBT Features", analysis['available_features'])
            
        # Metadaten (falls vorhanden)
        if metadata:
            self.create_metadata_section("📋 Metadaten", metadata)
            
    def create_detailed_info_section(self, title: str, info_dict: Dict[str, Any]):
        """Erstellt eine detaillierte Informations-Sektion"""
        # Sektion Frame
        section_frame = ttk.LabelFrame(self.scrollable_frame, text=title, padding="15")
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Informationen anzeigen
        for key, value in info_dict.items():
            if value is None:
                continue
                
            info_frame = ttk.Frame(section_frame)
            info_frame.pack(fill=tk.X, pady=5)
            
            # Key mit besserer Formatierung
            key_text = self.format_key_name(key)
            key_label = ttk.Label(info_frame, text=f"{key_text}:", font=('Arial', 10, 'bold'), foreground='darkblue')
            key_label.pack(anchor=tk.W)
            
            # Value mit vollständiger Anzeige
            value_text = self.format_value_display(value)
            value_label = ttk.Label(info_frame, text=value_text, font=('Arial', 9), wraplength=600, justify=tk.LEFT)
            value_label.pack(anchor=tk.W, padx=(20, 0))
            
    def create_indicators_section(self, title: str, indicators: list):
        """Erstellt eine vollständige Indikatoren-Sektion"""
        section_frame = ttk.LabelFrame(self.scrollable_frame, text=title, padding="15")
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        if not indicators:
            no_indicators_label = ttk.Label(section_frame, text="Keine Indikatoren gefunden", font=('Arial', 9), foreground='gray')
            no_indicators_label.pack(anchor=tk.W)
            return
            
        # Anzahl der Indikatoren
        count_label = ttk.Label(section_frame, text=f"Anzahl Indikatoren: {len(indicators)}", font=('Arial', 10, 'bold'), foreground='darkgreen')
        count_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Alle Indikatoren auflisten
        for i, indicator in enumerate(indicators, 1):
            indicator_frame = ttk.Frame(section_frame)
            indicator_frame.pack(fill=tk.X, pady=2)
            
            indicator_label = ttk.Label(indicator_frame, text=f"{i:2d}. {indicator}", font=('Arial', 9))
            indicator_label.pack(anchor=tk.W, padx=(20, 0))
            
    def create_features_section(self, title: str, features: list):
        """Erstellt eine vollständige Features-Sektion"""
        section_frame = ttk.LabelFrame(self.scrollable_frame, text=title, padding="15")
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        if not features:
            no_features_label = ttk.Label(section_frame, text="Keine Features gefunden", font=('Arial', 9), foreground='gray')
            no_features_label.pack(anchor=tk.W)
            return
            
        # Anzahl der Features
        count_label = ttk.Label(section_frame, text=f"Anzahl Features: {len(features)}", font=('Arial', 10, 'bold'), foreground='darkgreen')
        count_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Alle Features auflisten
        for i, feature in enumerate(features, 1):
            feature_frame = ttk.Frame(section_frame)
            feature_frame.pack(fill=tk.X, pady=2)
            
            feature_label = ttk.Label(feature_frame, text=f"{i:2d}. {feature}", font=('Arial', 9))
            feature_label.pack(anchor=tk.W, padx=(20, 0))
            
    def create_metadata_section(self, title: str, metadata: Dict[str, Any]):
        """Erstellt eine Metadaten-Sektion"""
        section_frame = ttk.LabelFrame(self.scrollable_frame, text=title, padding="15")
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        for key, value in metadata.items():
            if value is None:
                continue
                
            meta_frame = ttk.Frame(section_frame)
            meta_frame.pack(fill=tk.X, pady=3)
            
            key_text = self.format_key_name(key)
            key_label = ttk.Label(meta_frame, text=f"{key_text}:", font=('Arial', 9, 'bold'), foreground='purple')
            key_label.pack(anchor=tk.W)
            
            value_text = self.format_value_display(value)
            value_label = ttk.Label(meta_frame, text=value_text, font=('Arial', 9), wraplength=600, justify=tk.LEFT)
            value_label.pack(anchor=tk.W, padx=(20, 0))
            
    def format_key_name(self, key: str) -> str:
        """Formatiert Schlüsselnamen für bessere Lesbarkeit"""
        # Deutsche Übersetzungen für häufige Begriffe
        translations = {
            'type': 'Typ',
            'shape': 'Form/Dimensionen',
            'size': 'Größe',
            'memory_usage': 'Speicherverbrauch',
            'start_date': 'Startdatum',
            'end_date': 'Enddatum',
            'total_periods': 'Gesamte Perioden',
            'frequency': 'Frequenz',
            'timeframe': 'Zeitrahmen',
            'time_unit': 'Zeiteinheit',
            'asset_count': 'Anzahl Assets',
            'asset_names': 'Asset-Namen',
            'columns': 'Spalten',
            'index_name': 'Index-Name',
            'dtypes': 'Datentypen'
        }
        
        if key in translations:
            return translations[key]
        else:
            return key.replace('_', ' ').title()
            
    def format_value_display(self, value) -> str:
        """Formatiert Werte für vollständige Anzeige"""
        if value is None:
            return "Nicht verfügbar"
        elif isinstance(value, list):
            if len(value) == 0:
                return "Keine Einträge"
            elif len(value) <= 10:
                return "\n".join([f"  • {str(v)}" for v in value])
            else:
                first_items = "\n".join([f"  • {str(v)}" for v in value[:8]])
                return f"{first_items}\n  • ... und {len(value)-8} weitere Einträge"
        elif isinstance(value, dict):
            if len(value) == 0:
                return "Keine Einträge"
            else:
                items = []
                for k, v in list(value.items())[:5]:
                    items.append(f"  • {k}: {v}")
                if len(value) > 5:
                    items.append(f"  • ... und {len(value)-5} weitere Einträge")
                return "\n".join(items)
        elif isinstance(value, (int, float)):
            if isinstance(value, float):
                return f"{value:,.2f}"
            else:
                return f"{value:,}"
        else:
            return str(value)
            
    def create_info_section(self, title: str, info_dict: Dict[str, Any]):
        """Erstellt eine einfache Informations-Sektion (Fallback)"""
        # Sektion Frame
        section_frame = ttk.LabelFrame(self.scrollable_frame, text=title, padding="10")
        section_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Informationen anzeigen
        for key, value in info_dict.items():
            if value is None:
                continue
                
            info_frame = ttk.Frame(section_frame)
            info_frame.pack(fill=tk.X, pady=2)
            
            # Key
            key_label = ttk.Label(info_frame, text=f"{key.replace('_', ' ').title()}:", font=('Arial', 9, 'bold'))
            key_label.pack(side=tk.LEFT, anchor=tk.W)
            
            # Value
            if isinstance(value, list):
                if len(value) <= 5:
                    value_text = ", ".join(str(v) for v in value)
                else:
                    value_text = f"{', '.join(str(v) for v in value[:5])}... (+{len(value)-5} weitere)"
            elif isinstance(value, dict):
                value_text = f"{len(value)} Einträge"
            else:
                value_text = str(value)
                
            value_label = ttk.Label(info_frame, text=value_text)
            value_label.pack(side=tk.LEFT, anchor=tk.W, padx=(10, 0))
            
    def scan_completed(self):
        """Callback wenn Scan abgeschlossen ist"""
        self.scan_progress.stop()
        self.scan_button.configure(state='normal')
        
    def show_scan_error(self, error_msg: str):
        """Zeigt Scan-Fehler an"""
        self.status_var.set("Scan-Fehler")
        messagebox.showerror("Scan-Fehler", f"Fehler beim Scannen:\n{error_msg}")
        
    def show_load_error(self, error_msg: str):
        """Zeigt Lade-Fehler an"""
        self.status_var.set("Lade-Fehler")
        messagebox.showerror("Lade-Fehler", f"Fehler beim Laden der Datei:\n{error_msg}")