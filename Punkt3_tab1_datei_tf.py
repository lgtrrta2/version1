# 📊 PUNKT 3: TAB 1 - DATEI & TIMEFRAME AUSWAHL
# Erste Tab für Datei-Auswahl und Timeframe-Konfiguration

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import logging
from typing import Dict, List, Optional

from Punkt3_settings import CONFIG
from Punkt3_events import emit_file_selected, emit_timeframes_changed, emit_status_changed, on
from Punkt3_state_manager import state_manager, get_state
from Punkt3_utils import FileUtils, UIUtils, ValidationUtils, ScrollableFrame

class Tab1DateiTimeframe:
    """Tab 1: Datei- und Timeframe-Auswahl"""

    def __init__(self, parent_notebook):
        self.notebook = parent_notebook
        self.logger = logging.getLogger(__name__)

        # Variablen
        self.file_var = tk.StringVar()
        self.selected_file_var = tk.StringVar()
        self.timeframe_mode_var = tk.StringVar()
        self.multi_indicator_mode_var = tk.StringVar()

        # Verfügbare Dateien
        self.available_files = {}

        # Tab erstellen
        self.create_tab()

        # Event-Listener registrieren
        self.setup_event_listeners()

        # Initial laden
        self.load_available_files()
        self.load_state()

    def create_tab(self):
        """Erstellt Tab 1 GUI"""
        # Tab-Frame
        self.tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_frame, text="📁 1. DATEI & TIMEFRAMES")

        # Scrollbares Frame erstellen
        self.scrollable = ScrollableFrame(self.tab_frame)
        self.scrollable.get_main_frame().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Container ist jetzt das scrollbare Frame
        container = self.scrollable.get_frame()

        # Padding hinzufügen
        container.configure(padding=CONFIG.GUI_CONFIG['tab_padding'])

        # 1. DATEI-AUSWAHL SEKTION
        self.create_file_selection_section(container)

        # 2. TIMEFRAME-AUSWAHL SEKTION
        self.create_timeframe_selection_section(container)

        # Grid-Konfiguration für responsive Design
        self.tab_frame.columnconfigure(0, weight=1)
        self.tab_frame.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

    def create_file_selection_section(self, parent):
        """Erstellt Datei-Auswahl Sektion"""
        file_frame = ttk.LabelFrame(parent, text="📁 PUNKT 2 DATEI-AUSWAHL",
                                   padding=CONFIG.GUI_CONFIG['frame_padding'])
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        # Beschreibung
        desc_label = ttk.Label(file_frame,
                              text="Wählen Sie eine Punkt 2 Datei aus, die Multi-Timeframe Daten enthält:",
                              font=CONFIG.FONTS['normal'])
        desc_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Scan-Ordner Info und Änderung
        scan_info_frame = ttk.Frame(file_frame)
        scan_info_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(20, 0))

        ttk.Label(scan_info_frame, text="📁 Gescannter Ordner:",
                 font=CONFIG.FONTS['small']).grid(row=0, column=0, sticky=tk.W)
        
        self.scan_path_var = tk.StringVar(value=CONFIG.PATHS['punkt2_dir'])
        self.scan_path_label = ttk.Label(scan_info_frame, textvariable=self.scan_path_var,
                                        font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['info'])
        self.scan_path_label.grid(row=1, column=0, sticky=tk.W)
        
        ttk.Button(scan_info_frame, text="📂 Ordner ändern",
                  command=self.change_scan_directory,
                  width=15).grid(row=2, column=0, sticky=tk.W, pady=(5, 0))

        # Datei-Dropdown
        dropdown_frame = ttk.Frame(file_frame)
        dropdown_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(dropdown_frame, text="Verfügbare Dateien:",
                 font=CONFIG.FONTS['heading']).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.file_combo = ttk.Combobox(dropdown_frame, textvariable=self.file_var,
                                      width=70, font=CONFIG.FONTS['normal'], state="readonly")
        self.file_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.file_combo.bind('<<ComboboxSelected>>', self.on_file_select)

        # Datei-Status
        self.file_status_label = ttk.Label(dropdown_frame, textvariable=self.selected_file_var,
                                          font=CONFIG.FONTS['normal'], foreground=CONFIG.COLORS['success'])
        self.file_status_label.grid(row=2, column=0, sticky=tk.W)

        # Alternative Datei-Auswahl
        alt_frame = ttk.Frame(file_frame)
        alt_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(15, 0))

        ttk.Button(alt_frame, text="📁 ANDERE DATEI WÄHLEN",
                  command=self.browse_file,
                  width=CONFIG.GUI_CONFIG['button_width']).grid(row=0, column=0)

        ttk.Button(alt_frame, text="🔄 AKTUALISIEREN",
                  command=self.refresh_files,
                  width=CONFIG.GUI_CONFIG['button_width']).grid(row=0, column=1, padx=(10, 0))

        # Datei-Informationen
        self.create_file_info_section(file_frame)

        # Grid-Konfiguration
        file_frame.columnconfigure(0, weight=3)  # Hauptbereich bekommt mehr Platz
        file_frame.columnconfigure(1, weight=1)  # Info-Bereich bekommt weniger Platz
        dropdown_frame.columnconfigure(0, weight=1)

    def create_file_info_section(self, parent):
        """Erstellt Datei-Informationen Sektion"""
        info_frame = ttk.LabelFrame(parent, text="📋 DATEI-INFORMATIONEN",
                                   padding=CONFIG.GUI_CONFIG['frame_padding'])
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(15, 0))

        # Info-Text
        self.file_info_text = tk.Text(info_frame, height=6, width=80,
                                     bg=CONFIG.COLORS['background'],
                                     font=CONFIG.FONTS['small'],
                                     wrap=tk.WORD, state='disabled')

        # Scrollbar für Info-Text
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.file_info_text.yview)
        self.file_info_text.configure(yscrollcommand=info_scrollbar.set)

        self.file_info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        info_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)

    def create_timeframe_selection_section(self, parent):
        """Erstellt Timeframe-Auswahl Sektion"""
        tf_frame = ttk.LabelFrame(parent, text="⏰ TIMEFRAME-AUSWAHL",
                                 padding=CONFIG.GUI_CONFIG['frame_padding'])
        tf_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Timeframe-Modus
        mode_frame = ttk.Frame(tf_frame)
        mode_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(mode_frame, text="Modus:", font=CONFIG.FONTS['heading']).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        self.single_tf_radio = ttk.Radiobutton(mode_frame, text="📊 Single Timeframe",
                                              variable=self.timeframe_mode_var,
                                              value="single", command=self.on_timeframe_mode_change)
        self.single_tf_radio.grid(row=1, column=0, sticky=tk.W, padx=(0, 30))

        self.multi_tf_radio = ttk.Radiobutton(mode_frame, text="📈 Multi Timeframe",
                                             variable=self.timeframe_mode_var,
                                             value="multi", command=self.on_timeframe_mode_change)
        self.multi_tf_radio.grid(row=1, column=1, sticky=tk.W)

        # Timeframe-Liste
        list_frame = ttk.Frame(tf_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))

        ttk.Label(list_frame, text="Verfügbare Timeframes:",
                 font=CONFIG.FONTS['heading']).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Listbox mit Scrollbar
        listbox_container = ttk.Frame(list_frame)
        listbox_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.timeframe_listbox = tk.Listbox(listbox_container,
                                           height=CONFIG.GUI_CONFIG['listbox_height'],
                                           selectmode=tk.SINGLE,
                                           font=CONFIG.FONTS['normal'])

        tf_scrollbar = ttk.Scrollbar(listbox_container, orient="vertical",
                                    command=self.timeframe_listbox.yview)
        self.timeframe_listbox.configure(yscrollcommand=tf_scrollbar.set)

        self.timeframe_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tf_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Event-Binding für Timeframe-Auswahl
        self.timeframe_listbox.bind('<<ListboxSelect>>', self.on_timeframe_select)

        listbox_container.columnconfigure(0, weight=1)
        listbox_container.rowconfigure(0, weight=1)

        # Multi-Timeframe Optionen
        self.multi_options_frame = ttk.LabelFrame(tf_frame, text="📊 MULTI-TIMEFRAME OPTIONEN",
                                                 padding=CONFIG.GUI_CONFIG['frame_padding'])
        self.multi_options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(15, 0))

        ttk.Label(self.multi_options_frame, text="Indikator-Modus:",
                 font=CONFIG.FONTS['heading']).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        ttk.Radiobutton(self.multi_options_frame, text="Gleiche Indikatoren für alle Timeframes",
                       variable=self.multi_indicator_mode_var, value="same").grid(row=1, column=0, sticky=tk.W, pady=2)

        ttk.Radiobutton(self.multi_options_frame, text="Individuelle Indikatoren pro Timeframe",
                       variable=self.multi_indicator_mode_var, value="individual").grid(row=2, column=0, sticky=tk.W, pady=2)

        # Grid-Konfiguration
        tf_frame.columnconfigure(0, weight=1)
        tf_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)

        # Initial Multi-Optionen verstecken
        self.multi_options_frame.grid_remove()

    def setup_event_listeners(self):
        """Registriert Event-Listener"""
        # Keine externen Events für Tab 1 - er ist der Initiator
        pass

    def load_available_files(self):
        """Lädt verfügbare Punkt 2 Dateien"""
        try:
            self.available_files = FileUtils.scan_punkt2_files()
            self.update_file_dropdown()
            self.update_file_info_display()

            emit_status_changed("tab1", "files_loaded",
                               f"{len(self.available_files)} Punkt 2 Dateien gefunden", "info")

        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Dateien: {e}")
            UIUtils.show_error("Fehler", f"Fehler beim Laden der Punkt 2 Dateien:\n{e}")

    def update_file_dropdown(self):
        """Aktualisiert Datei-Dropdown"""
        if self.available_files:
            file_options = []
            for name, info in self.available_files.items():
                tf_count = len(info.get('timeframes', []))
                size_mb = info.get('file_size_mb', 0.0)
                file_type = info.get('type', 'multi_timeframe')

                if file_type == 'single_timeframe':
                    timeframe = info.get('timeframes', ['1m'])[0]
                    option = f"{name} (Single-TF: {timeframe}, {size_mb:.1f}MB)"
                else:
                    option = f"{name} ({tf_count} TFs, {size_mb:.1f}MB)"
                file_options.append(option)

            self.file_combo['values'] = file_options

            # Auto-Auswahl der neuesten Datei
            if file_options:
                latest_file = sorted(self.available_files.keys())[-1]
                for option in file_options:
                    if option.startswith(latest_file):
                        self.file_var.set(option)
                        self.on_file_select()
                        break
        else:
            self.file_combo['values'] = ["Keine Punkt 2 Dateien gefunden"]
            self.file_var.set("Keine Punkt 2 Dateien gefunden")

    def update_file_info_display(self):
        """Aktualisiert Datei-Informationen Anzeige"""
        self.file_info_text.config(state='normal')
        self.file_info_text.delete(1.0, tk.END)

        if self.available_files:
            info_text = f"✅ {len(self.available_files)} Punkt 2 Dateien gefunden:\n\n"

            for file_name, file_info in sorted(self.available_files.items()):
                file_type = file_info.get('type', 'multi_timeframe')

                if file_type == 'multi_timeframe':
                    info_text += f"📊 {file_name} (Multi-Timeframe)\n"
                    info_text += f"   ⏰ Timeframes: {', '.join(file_info.get('timeframes', []))}\n"
                    info_text += f"   📁 H5-Dateien: {len(file_info.get('h5_files', []))}\n"
                    info_text += f"   💾 Größe: {file_info.get('file_size_mb', 0.0):.1f} MB\n"
                    info_text += f"   🕐 Erstellt: {file_info.get('created_at', 'Unbekannt')[:19]}\n"
                    if 'record_count' in file_info:
                        info_text += f"   📈 Datensätze: {file_info['record_count']:,}\n"
                else:
                    # Single-Timeframe
                    info_text += f"📊 {file_name} (Single-Timeframe)\n"
                    info_text += f"   ⏰ Timeframe: {', '.join(file_info.get('timeframes', ['1m']))}\n"
                    info_text += f"   📁 Datei: {file_info.get('data_file', file_info.get('original_file', 'Unbekannt'))}\n"
                    info_text += f"   💾 Größe: {file_info.get('file_size_mb', 0.0):.1f} MB\n"
                    info_text += f"   🕐 Erstellt: {file_info.get('created_at', 'Unbekannt')[:19]}\n"
                    if 'record_count' in file_info and file_info['record_count'] > 0:
                        info_text += f"   📈 Datensätze: {file_info['record_count']:,}\n"

                info_text += "\n"
        else:
            info_text = "❌ Keine Punkt 2 Dateien gefunden!\n\n"
            info_text += "💡 Führen Sie zuerst Punkt 2 aus, um Multi-Timeframe Daten zu erstellen.\n\n"
            info_text += f"📁 Erwarteter Pfad: {CONFIG.PATHS['punkt2_dir']}\n"
            info_text += "📋 Erwartete Dateien: *_metadata.json und entsprechende *.h5 Dateien"

        self.file_info_text.insert(1.0, info_text)
        self.file_info_text.config(state='disabled')

    def on_file_select(self, event=None):
        """Wird aufgerufen wenn Datei ausgewählt wird"""
        selection = self.file_var.get()
        if not selection or "Keine Punkt 2 Dateien" in selection:
            return

        # Dateiname extrahieren
        file_name = selection.split(' (')[0]
        if file_name in self.available_files:
            file_info = self.available_files[file_name]

            # Unterscheide Multi vs Single-Timeframe
            if file_info.get('type') == 'single_timeframe':
                file_path = file_info['data_path']
            else:
                file_path = file_info['metadata_path']

            # State aktualisieren
            state_manager.set_selected_file(file_path, file_info)

            # UI aktualisieren
            self.selected_file_var.set(f"✅ Gewählt: {file_name}")
            self.update_timeframe_list(file_name)

            # Event senden
            emit_file_selected("tab1", file_path, file_info)

            self.logger.info(f"Datei ausgewählt: {file_name}")

    def update_timeframe_list(self, file_name: str):
        """Aktualisiert Timeframe-Liste mit Auto-Auswahl"""
        self.timeframe_listbox.delete(0, tk.END)

        if file_name in self.available_files:
            timeframes = self.available_files[file_name]['timeframes']

            for tf in timeframes:
                self.timeframe_listbox.insert(tk.END, tf)

            # Auto-Auswahl und Modus-Konfiguration
            if timeframes:
                if len(timeframes) == 1:
                    # Nur ein Timeframe: Auto-Auswahl, Multi deaktiviert
                    self.timeframe_listbox.selection_set(0)
                    self.timeframe_mode_var.set("single")
                    self.multi_tf_radio.config(state='disabled')
                    self.single_tf_radio.config(text=f"📊 Single Timeframe ({timeframes[0]})")

                    # State aktualisieren
                    state_manager.set_timeframe_mode("single")
                    state_manager.set_selected_timeframes([timeframes[0]])

                    self.logger.info(f"Auto-Auswahl: Nur ein Timeframe ({timeframes[0]}) verfügbar")
                else:
                    # Mehrere Timeframes: Ersten auswählen, Multi aktiviert
                    self.timeframe_listbox.selection_set(0)
                    self.timeframe_mode_var.set("single")  # Default auf Single
                    self.multi_tf_radio.config(state='normal')
                    self.single_tf_radio.config(text="📊 Single Timeframe")

                    # State aktualisieren
                    state_manager.set_timeframe_mode("single")
                    state_manager.set_selected_timeframes([timeframes[0]])

                    self.logger.info(f"{len(timeframes)} Timeframes verfügbar: {', '.join(timeframes)}")

                # UI aktualisieren
                self.on_timeframe_mode_change()

    def on_timeframe_mode_change(self):
        """Wird aufgerufen wenn Timeframe-Modus geändert wird"""
        mode = self.timeframe_mode_var.get()

        # State aktualisieren
        state_manager.set_timeframe_mode(mode)

        if mode == "multi":
            self.timeframe_listbox.config(selectmode=tk.EXTENDED)
            self.multi_options_frame.grid()

            # Bei Multi-Mode alle Timeframes auswählen
            self.timeframe_listbox.selection_set(0, tk.END)
            self.on_timeframe_select()
        else:
            self.timeframe_listbox.config(selectmode=tk.SINGLE)
            self.multi_options_frame.grid_remove()

            # Bei Single-Mode nur ersten auswählen
            if self.timeframe_listbox.size() > 0:
                self.timeframe_listbox.selection_clear(0, tk.END)
                self.timeframe_listbox.selection_set(0)
                self.on_timeframe_select()

        self.logger.info(f"Timeframe-Modus geändert: {mode}")

    def on_timeframe_select(self, event=None):
        """Wird aufgerufen wenn Timeframes ausgewählt werden"""
        selection = self.timeframe_listbox.curselection()
        selected_timeframes = [self.timeframe_listbox.get(idx) for idx in selection]

        # Validierung
        mode = self.timeframe_mode_var.get()
        valid, msg = ValidationUtils.validate_timeframe_selection(selected_timeframes, mode)

        if valid:
            # State aktualisieren
            state_manager.set_selected_timeframes(selected_timeframes)

            # Event senden
            emit_timeframes_changed("tab1", selected_timeframes, mode)

            self.logger.info(f"Timeframes ausgewählt: {selected_timeframes}")
        else:
            self.logger.warning(f"Ungültige Timeframe-Auswahl: {msg}")

    def browse_file(self):
        """Öffnet Datei-Browser für andere Datei-Auswahl"""
        filename = filedialog.askopenfilename(
            title="📊 Punkt 2 Datei auswählen",
            filetypes=[
                ("VBT Pickle Dateien", "*.pickle"),
                ("H5 Dateien", "*.h5"),
                ("Punkt 2 Metadata", "*_metadata.json"),
                ("Alle Daten-Dateien", "*.pickle;*.h5"),
                ("All files", "*.*")
            ],
            initialdir=CONFIG.PATHS['punkt2_dir'] if os.path.exists(CONFIG.PATHS['punkt2_dir']) else "."
        )

        if filename:
            # Datei validieren
            valid, msg, metadata = FileUtils.validate_punkt2_file(filename)

            if valid:
                # Datei zu verfügbaren Dateien hinzufügen
                if filename.endswith('_metadata.json'):
                    # Multi-Timeframe Datei
                    base_name = os.path.basename(filename).replace('_metadata.json', '')
                    file_info = {
                        'type': 'multi_timeframe',
                        'metadata_file': os.path.basename(filename),
                        'metadata_path': filename,
                        'metadata': metadata,
                        'timeframes': metadata.get('timeframes', []),
                        'created_at': metadata.get('created_at', 'Unbekannt'),
                        'original_file': metadata.get('original_file', 'Unbekannt'),
                        'file_size_mb': os.path.getsize(filename) / (1024 * 1024)
                    }
                else:
                    # Single-Timeframe Datei
                    base_name = os.path.basename(filename).replace('.h5', '').replace('.pickle', '')
                    file_info = metadata  # metadata enthält bereits die korrekte Struktur
                    # Stelle sicher, dass file_size_mb vorhanden ist
                    if 'file_size_mb' not in file_info:
                        file_info['file_size_mb'] = os.path.getsize(filename) / (1024 * 1024)

                self.available_files[base_name] = file_info

                # UI aktualisieren
                self.update_file_dropdown()
                file_type_label = "Multi-TF" if file_info.get('type') == 'multi_timeframe' else "Single-TF"
                self.file_var.set(f"📁 {base_name} ({file_type_label})")
                self.selected_file_var.set(f"✅ Gewählt: {base_name}")

                # State aktualisieren
                state_manager.set_selected_file(filename, file_info)

                # Timeframes aktualisieren
                self.update_timeframe_list(base_name)

                UIUtils.show_info("Datei gewählt", f"✅ Punkt 2 Datei erfolgreich gewählt!\n\n📁 Datei: {base_name}")
            else:
                UIUtils.show_error("Ungültige Datei", f"Die ausgewählte Datei ist ungültig:\n\n{msg}")

    def refresh_files(self):
        """Aktualisiert die Datei-Liste"""
        self.load_available_files()
        UIUtils.show_info("Aktualisiert", "Datei-Liste wurde aktualisiert!")
        
    def change_scan_directory(self):
        """Ändert den Ordner, der nach Punkt 2 Dateien gescannt wird"""
        current_dir = self.scan_path_var.get()
        initial_dir = current_dir if os.path.exists(current_dir) else os.path.dirname(current_dir)
        
        new_dir = filedialog.askdirectory(
            title="📁 Ordner für Punkt 2 Dateien auswählen",
            initialdir=initial_dir
        )
        
        if new_dir:
            # Pfad aktualisieren
            CONFIG.PATHS['punkt2_dir'] = new_dir
            self.scan_path_var.set(new_dir)
            
            # Konfiguration persistent speichern
            if CONFIG.save_config():
                self.logger.info(f"Konfiguration gespeichert: neuer Scan-Ordner {new_dir}")
            else:
                self.logger.warning("Konfiguration konnte nicht gespeichert werden")
            
            # Dateien neu laden
            self.load_available_files()
            
            # Info anzeigen
            UIUtils.show_info("Ordner geändert", f"Scan-Ordner wurde geändert auf:\n\n{new_dir}\n\n{len(self.available_files)} Dateien gefunden.\n\nDie Einstellung wurde dauerhaft gespeichert.")

    def load_state(self):
        """Lädt Zustand aus State Manager"""
        state = get_state()

        # Scan-Pfad aktualisieren
        self.scan_path_var.set(CONFIG.PATHS['punkt2_dir'])

        # Timeframe-Modus setzen
        if state.timeframe_mode:
            self.timeframe_mode_var.set(state.timeframe_mode)

        # Multi-Indikator-Modus setzen
        if state.multi_indicator_mode:
            self.multi_indicator_mode_var.set(state.multi_indicator_mode)

        # Ausgewählte Datei setzen
        if state.selected_file_path and os.path.exists(state.selected_file_path):
            if state.selected_file_path.endswith('_metadata.json'):
                base_name = os.path.basename(state.selected_file_path).replace('_metadata.json', '')
            else:
                base_name = os.path.basename(state.selected_file_path).replace('.h5', '').replace('.pickle', '')
            self.selected_file_var.set(f"✅ Gewählt: {base_name}")

    def get_tab_frame(self):
        """Gibt Tab-Frame zurück"""
        return self.tab_frame
