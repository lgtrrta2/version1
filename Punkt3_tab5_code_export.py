# 📊 PUNKT 3: TAB 5 - CODE-GENERIERUNG & EXPORT
# Fünfte Tab für Code-Generierung und Export-Optionen

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import logging
from typing import Dict, List, Optional

from Punkt3_settings import CONFIG
from Punkt3_events import emit_code_generated, emit_status_changed, on, Events
from Punkt3_state_manager import state_manager, get_state
from Punkt3_utils import UIUtils, ValidationUtils, FormatUtils, ScrollableFrame
from punkt3_code_generator import generate_punkt3_code

class Tab5CodeExport:
    """Tab 5: Code-Generierung und Export"""

    def __init__(self, parent_notebook):
        self.notebook = parent_notebook
        self.logger = logging.getLogger(__name__)

        # Variablen für Speicher-Optionen
        self.save_punkt4_var = tk.BooleanVar(value=CONFIG.DEFAULTS['save_punkt4'])
        self.save_backup_var = tk.BooleanVar(value=CONFIG.DEFAULTS['save_backup'])
        self.save_charts_var = tk.BooleanVar(value=CONFIG.DEFAULTS['save_charts'])
        self.show_summary_var = tk.BooleanVar(value=CONFIG.DEFAULTS['show_summary'])

        # Tab erstellen
        self.create_tab()

        # Event-Listener registrieren
        self.setup_event_listeners()

        # Initial laden
        self.update_generation_status()

    def create_tab(self):
        """Erstellt Tab 5 GUI"""
        # Tab-Frame
        self.tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_frame, text="🚀 5. CODE & EXPORT")

        # Scrollbares Frame erstellen
        self.scrollable = ScrollableFrame(self.tab_frame)
        self.scrollable.get_main_frame().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Container ist jetzt das scrollbare Frame
        container = self.scrollable.get_frame()

        # Padding hinzufügen
        container.configure(padding=CONFIG.GUI_CONFIG['tab_padding'])

        # 1. KONFIGURATION ÜBERSICHT
        self.create_config_overview_section(container)

        # 2. SPEICHER-OPTIONEN
        self.create_save_options_section(container)

        # 3. CODE-GENERIERUNG
        self.create_code_generation_section(container)

        # 4. CODE-AUSGABE
        self.create_code_output_section(container)

        # Grid-Konfiguration
        self.tab_frame.columnconfigure(0, weight=1)
        self.tab_frame.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(3, weight=1)

    def create_config_overview_section(self, parent):
        """Erstellt Konfiguration-Übersicht"""
        overview_frame = ttk.LabelFrame(parent, text="📋 KONFIGURATION ÜBERSICHT",
                                       padding=CONFIG.GUI_CONFIG['frame_padding'])
        overview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Status-Container
        status_container = ttk.Frame(overview_frame)
        status_container.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Status-Icon und Text
        self.status_icon_label = ttk.Label(status_container, text="⏳", font=('Arial', 16))
        self.status_icon_label.grid(row=0, column=0, padx=(0, 10))

        self.status_text_label = ttk.Label(status_container, text="Konfiguration wird geladen...",
                                          font=CONFIG.FONTS['heading'], foreground=CONFIG.COLORS['info'])
        self.status_text_label.grid(row=0, column=1, sticky=tk.W)

        # Konfiguration-Details
        details_frame = ttk.Frame(overview_frame)
        details_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(15, 0))

        # Details in Grid-Layout
        self.config_labels = {}
        config_items = [
            ("📁 Datei:", "Nicht ausgewählt", 0, 0),
            ("⏰ Timeframes:", "0", 0, 2),
            ("📊 Modus:", "Single", 1, 0),
            ("📈 Indikatoren:", "0", 1, 2),
            ("🎨 Visualisierung:", "Nicht konfiguriert", 2, 0),
            ("📅 Zeitraum:", "Nicht ausgewählt", 2, 2)
        ]

        for label_text, default_value, row, col in config_items:
            # Label
            ttk.Label(details_frame, text=label_text,
                     font=CONFIG.FONTS['normal']).grid(row=row, column=col, sticky=tk.W, padx=(0, 10), pady=2)
            # Wert
            value_label = ttk.Label(details_frame, text=default_value,
                                   font=CONFIG.FONTS['normal'], foreground=CONFIG.COLORS['primary'])
            value_label.grid(row=row, column=col+1, sticky=tk.W, padx=(0, 30), pady=2)
            self.config_labels[label_text] = value_label

        overview_frame.columnconfigure(0, weight=1)
        status_container.columnconfigure(1, weight=1)

    def create_save_options_section(self, parent):
        """Erstellt Speicher-Optionen"""
        save_frame = ttk.LabelFrame(parent, text="💾 SPEICHER-OPTIONEN",
                                   padding=CONFIG.GUI_CONFIG['frame_padding'])
        save_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Optionen in zwei Spalten
        left_options = ttk.Frame(save_frame)
        left_options.grid(row=0, column=0, sticky=(tk.W, tk.N))

        right_options = ttk.Frame(save_frame)
        right_options.grid(row=0, column=1, sticky=(tk.W, tk.N), padx=(30, 0))

        # Linke Spalte
        ttk.Checkbutton(left_options, text="✅ Für Punkt 4 speichern (data/punkt3/)",
                       variable=self.save_punkt4_var,
                       command=self.on_option_change).grid(row=0, column=0, sticky=tk.W, pady=2)

        ttk.Checkbutton(left_options, text="🔄 Intelligentes Backup (data/backups/)",
                       variable=self.save_backup_var,
                       command=self.on_option_change).grid(row=1, column=0, sticky=tk.W, pady=2)

        # Rechte Spalte
        ttk.Checkbutton(right_options, text="📊 Charts als HTML speichern",
                       variable=self.save_charts_var,
                       command=self.on_option_change).grid(row=0, column=0, sticky=tk.W, pady=2)

        ttk.Checkbutton(right_options, text="📋 Zusammenfassung anzeigen",
                       variable=self.show_summary_var,
                       command=self.on_option_change).grid(row=1, column=0, sticky=tk.W, pady=2)

        # Beschreibungen
        desc_frame = ttk.Frame(save_frame)
        desc_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))

        descriptions = [
            "💡 Punkt 4: Speichert Code für direkte Verwendung in Punkt 4 (Strategie-Entwicklung)",
            "💡 Backup: Erstellt automatische Sicherungskopien mit Zeitstempel",
            "💡 Charts: Speichert interaktive HTML-Charts für spätere Analyse",
            "💡 Zusammenfassung: Zeigt detaillierte Übersicht nach Code-Generierung"
        ]

        for i, desc in enumerate(descriptions):
            ttk.Label(desc_frame, text=desc, font=CONFIG.FONTS['small'],
                     foreground=CONFIG.COLORS['info']).grid(row=i, column=0, sticky=tk.W, pady=1)

    def create_code_generation_section(self, parent):
        """Erstellt Code-Generierung Sektion"""
        gen_frame = ttk.LabelFrame(parent, text="🚀 CODE-GENERIERUNG",
                                  padding=CONFIG.GUI_CONFIG['frame_padding'])
        gen_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Status und Validierung
        validation_frame = ttk.Frame(gen_frame)
        validation_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        self.validation_label = ttk.Label(validation_frame, text="Validierung läuft...",
                                         font=CONFIG.FONTS['normal'], foreground=CONFIG.COLORS['info'])
        self.validation_label.grid(row=0, column=0, sticky=tk.W)

        # Haupt-Generierung Button
        button_frame = ttk.Frame(gen_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.generate_btn = ttk.Button(button_frame, text="🚀 PUNKT 3 CODE GENERIEREN",
                                      command=self.generate_code,
                                      style='Accent.TButton')
        self.generate_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Zusätzliche Aktionen
        action_frame = ttk.Frame(gen_frame)
        action_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

        ttk.Button(action_frame, text="🔍 KONFIGURATION PRÜFEN",
                  command=self.validate_configuration,
                  width=20).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(action_frame, text="📋 VORSCHAU GENERIEREN",
                  command=self.generate_preview,
                  width=20).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(action_frame, text="🔄 KONFIGURATION ZURÜCKSETZEN",
                  command=self.reset_configuration,
                  width=25).grid(row=0, column=2)

        # Grid-Konfiguration
        gen_frame.columnconfigure(0, weight=1)
        validation_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(0, weight=1)

    def create_code_output_section(self, parent):
        """Erstellt Code-Ausgabe Sektion"""
        output_frame = ttk.LabelFrame(parent, text="📝 GENERIERTER PYTHON-CODE",
                                     padding=CONFIG.GUI_CONFIG['frame_padding'])
        output_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Code-Editor
        editor_frame = ttk.Frame(output_frame)
        editor_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.code_text = scrolledtext.ScrolledText(editor_frame,
                                                  height=CONFIG.GUI_CONFIG['code_editor_height'],
                                                  width=CONFIG.GUI_CONFIG['code_editor_width'],
                                                  bg=CONFIG.COLORS['code_bg'],
                                                  fg=CONFIG.COLORS['code_fg'],
                                                  font=CONFIG.FONTS['code'],
                                                  wrap=tk.NONE,
                                                  insertbackground='white',
                                                  selectbackground='#404040')
        self.code_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Code-Aktionen
        code_actions_frame = ttk.Frame(output_frame)
        code_actions_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(15, 0))

        # Erste Reihe: Haupt-Aktionen
        main_actions = ttk.Frame(code_actions_frame)
        main_actions.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(main_actions, text="📋 CODE KOPIEREN",
                  command=self.copy_code, width=18).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(main_actions, text="💾 ALS DATEI SPEICHERN",
                  command=self.save_code_as_file, width=20).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(main_actions, text="🚀 DIREKT AUSFÜHREN",
                  command=self.execute_code, width=18).grid(row=0, column=2)

        # Zweite Reihe: Export-Aktionen
        export_actions = ttk.Frame(code_actions_frame)
        export_actions.grid(row=1, column=0, sticky=(tk.W, tk.E))

        ttk.Button(export_actions, text="📤 NACH PUNKT 4 EXPORTIEREN",
                  command=self.export_to_punkt4, width=25).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(export_actions, text="📊 CHARTS GENERIEREN",
                  command=self.generate_charts, width=20).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(export_actions, text="📋 ZUSAMMENFASSUNG",
                  command=self.show_summary, width=18).grid(row=0, column=2)

        # Code-Info
        info_frame = ttk.Frame(output_frame)
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        self.code_info_label = ttk.Label(info_frame,
                                        text="💡 Konfigurieren Sie die Parameter und generieren Sie den Code",
                                        font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['info'])
        self.code_info_label.grid(row=0, column=0, sticky=tk.W)

        self.code_stats_label = ttk.Label(info_frame, text="",
                                         font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['primary'])
        self.code_stats_label.grid(row=0, column=1, sticky=tk.E)

        # Grid-Konfiguration
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)

    def setup_event_listeners(self):
        """Registriert Event-Listener"""
        # Lausche auf alle relevanten Änderungen
        on(Events.FILE_SELECTED, self.on_config_changed)
        on(Events.TIMEFRAMES_CHANGED, self.on_config_changed)
        on(Events.INDICATORS_CHANGED, self.on_config_changed)
        on(Events.VISUALIZATION_CHANGED, self.on_config_changed)

    def on_config_changed(self, event_data=None):
        """Wird aufgerufen wenn Konfiguration geändert wird"""
        self.update_config_overview()
        self.update_generation_status()

    def on_option_change(self):
        """Wird aufgerufen wenn Speicher-Optionen geändert werden"""
        # State aktualisieren
        state_manager.update_state(
            save_punkt4=self.save_punkt4_var.get(),
            save_backup=self.save_backup_var.get(),
            save_charts=self.save_charts_var.get(),
            show_summary=self.show_summary_var.get()
        )

    def update_config_overview(self):
        """Aktualisiert Konfiguration-Übersicht"""
        state = get_state()

        # Datei
        if state.selected_file_path:
            file_name = os.path.basename(state.selected_file_path).replace('_metadata.json', '')
            self.config_labels["📁 Datei:"].config(text=FormatUtils.truncate_text(file_name, 30))
        else:
            self.config_labels["📁 Datei:"].config(text="Nicht ausgewählt")

        # Timeframes
        tf_count = len(state.selected_timeframes) if state.selected_timeframes else 0
        self.config_labels["⏰ Timeframes:"].config(text=str(tf_count))

        # Modus
        mode_text = "Multi" if state.timeframe_mode == "multi" else "Single"
        self.config_labels["📊 Modus:"].config(text=mode_text)

        # Indikatoren
        indicator_count = len(state.selected_indicators) if state.selected_indicators else 0
        self.config_labels["📈 Indikatoren:"].config(text=str(indicator_count))

        # Visualisierung
        if state.visualization_mode:
            viz_short = state.visualization_mode.split()[0]
            self.config_labels["🎨 Visualisierung:"].config(text=viz_short)
        else:
            self.config_labels["🎨 Visualisierung:"].config(text="Nicht konfiguriert")

        # Zeitraum
        if state.visualization_period:
            period_short = state.visualization_period.split()[0] + " " + state.visualization_period.split()[1]
            self.config_labels["📅 Zeitraum:"].config(text=period_short)
        else:
            self.config_labels["📅 Zeitraum:"].config(text="Nicht ausgewählt")

    def update_generation_status(self):
        """Aktualisiert Generierung-Status"""
        state = get_state()
        ready, message = state_manager.is_ready_for_generation()

        if ready:
            self.status_icon_label.config(text="✅")
            self.status_text_label.config(text="Bereit für Code-Generierung",
                                         foreground=CONFIG.COLORS['success'])
            self.validation_label.config(text="✅ Alle Anforderungen erfüllt",
                                        foreground=CONFIG.COLORS['success'])
            self.generate_btn.config(state='normal')
        else:
            self.status_icon_label.config(text="⚠️")
            self.status_text_label.config(text="Konfiguration unvollständig",
                                         foreground=CONFIG.COLORS['warning'])
            self.validation_label.config(text=f"⚠️ {message}",
                                        foreground=CONFIG.COLORS['warning'])
            self.generate_btn.config(state='disabled')

    def validate_configuration(self):
        """Validiert die komplette Konfiguration"""
        state = get_state()

        # Konfiguration für Validierung erstellen
        config = {
            'metadata_file': state.selected_file_path,
            'selected_timeframes': state.selected_timeframes,
            'timeframe_mode': state.timeframe_mode,
            'selected_indicators': state.selected_indicators,
            'visualization_mode': state.visualization_mode,
            'visualization_period': state.visualization_period
        }

        # Validierung durchführen
        is_valid, errors = ValidationUtils.validate_configuration(config)

        if is_valid:
            UIUtils.show_info("Validierung erfolgreich",
                             "✅ Konfiguration ist vollständig und gültig!\n\n"
                             "Sie können jetzt den Code generieren.")
        else:
            error_text = "❌ Folgende Probleme wurden gefunden:\n\n"
            for i, error in enumerate(errors, 1):
                error_text += f"{i}. {error}\n"
            error_text += "\nBitte beheben Sie diese Probleme vor der Code-Generierung."

            UIUtils.show_error("Validierung fehlgeschlagen", error_text)

    def generate_preview(self):
        """Generiert Code-Vorschau"""
        try:
            # Kurze Vorschau generieren
            state = get_state()
            preview_text = f"# PUNKT 3 CODE VORSCHAU\n"
            preview_text += f"# Generiert am: {CONFIG.get_timestamp()}\n\n"

            if state.selected_file_path:
                preview_text += f"# Datei: {os.path.basename(state.selected_file_path)}\n"

            if state.selected_timeframes:
                preview_text += f"# Timeframes: {', '.join(state.selected_timeframes)}\n"

            if state.selected_indicators:
                preview_text += f"# Indikatoren: {len(state.selected_indicators)}\n"
                for indicator in state.selected_indicators[:5]:  # Nur erste 5
                    preview_text += f"#   - {indicator['display_name']}\n"
                if len(state.selected_indicators) > 5:
                    preview_text += f"#   ... und {len(state.selected_indicators)-5} weitere\n"

            preview_text += f"\n# Vollständiger Code wird bei 'Code Generieren' erstellt...\n"

            # Vorschau anzeigen
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(1.0, preview_text)

            self.code_info_label.config(text="👁️ Vorschau generiert - für vollständigen Code 'Generieren' klicken")

        except Exception as e:
            UIUtils.show_error("Vorschau-Fehler", f"Fehler bei Vorschau-Generierung:\n{e}")

    def reset_configuration(self):
        """Setzt Konfiguration zurück"""
        if UIUtils.ask_yes_no("Konfiguration zurücksetzen",
                             "Möchten Sie wirklich die komplette Konfiguration zurücksetzen?\n\n"
                             "Dies löscht alle ausgewählten Indikatoren und Einstellungen."):

            # State zurücksetzen
            state_manager.update_state(
                selected_file_path=None,
                selected_timeframes=[],
                selected_indicators=[],
                visualization_mode=CONFIG.DEFAULTS['visualization_mode'],
                visualization_period=CONFIG.DEFAULTS['visualization_period']
            )

            # Code-Ausgabe leeren
            self.code_text.delete(1.0, tk.END)
            self.code_info_label.config(text="🔄 Konfiguration zurückgesetzt")
            self.code_stats_label.config(text="")

            UIUtils.show_info("Zurückgesetzt", "🔄 Konfiguration wurde zurückgesetzt!")

    def generate_code(self):
        """Generiert den kompletten Punkt 3 Code"""
        try:
            state = get_state()

            # Finale Validierung
            ready, message = state_manager.is_ready_for_generation()
            if not ready:
                UIUtils.show_error("Generierung nicht möglich", f"❌ {message}")
                return

            # Visualisierungs-Konfiguration aus State Manager holen
            viz_config = {
                'quality': state.quality,
                'theme': state.theme,
                'enable_segmentation': state.enable_segmentation,
                'candles_per_chart': state.candles_per_chart
            }

            # Konfiguration für Code-Generator erstellen
            config = {
                'metadata_file': state.selected_file_path.replace('\\', '/'),
                'base_name': os.path.basename(state.selected_file_path).replace('_metadata.json', ''),
                'timeframe_mode': state.timeframe_mode,
                'selected_timeframes': state.selected_timeframes,
                'selected_indicators': state.selected_indicators,
                'visualization_mode': state.visualization_mode,
                'visualization_period': state.visualization_period,
                'save_punkt4': self.save_punkt4_var.get(),
                'save_backup': self.save_backup_var.get(),
                'save_charts': self.save_charts_var.get(),
                'show_summary': self.show_summary_var.get(),
                'multi_indicator_mode': state.multi_indicator_mode,
                # Visualisierungs-Konfiguration hinzufügen
                'quality': viz_config.get('quality', 'Hoch'),
                'theme': viz_config.get('theme', 'plotly_dark'),
                'enable_segmentation': viz_config.get('enable_segmentation', False),
                'candles_per_chart': viz_config.get('candles_per_chart', '100')
            }

            # Code generieren
            self.code_info_label.config(text="⏳ Code wird generiert...")
            self.tab_frame.update()

            complete_code = generate_punkt3_code(config)

            # Code anzeigen
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(1.0, complete_code)

            # Statistiken aktualisieren
            code_lines = len(complete_code.split('\n'))
            self.code_info_label.config(text="✅ Code erfolgreich generiert und bereit zum Export")
            self.code_stats_label.config(text=f"{code_lines} Zeilen | {len(state.selected_timeframes)} TF | {len(state.selected_indicators)} Indikatoren")

            # State aktualisieren
            state_manager.set_generated_code(complete_code, config)

            # Event senden
            emit_code_generated("tab5", complete_code, config)

            # Erfolgs-Nachricht (nur in Status-Label, kein Popup)
            self.logger.info(f"Code generiert: {code_lines} Zeilen, {len(state.selected_timeframes)} TF, {len(state.selected_indicators)} Indikatoren")

            # Automatische Aktionen basierend auf Optionen
            if self.save_punkt4_var.get():
                self.export_to_punkt4(silent=True)

            if self.save_backup_var.get():
                self.create_backup(silent=True)

            if self.show_summary_var.get():
                self.show_summary()

        except Exception as e:
            self.logger.error(f"Fehler bei Code-Generierung: {e}")
            UIUtils.show_error("Generierung fehlgeschlagen", f"❌ Fehler bei Code-Generierung:\n\n{e}")
            self.code_info_label.config(text="❌ Fehler bei Code-Generierung")

    def copy_code(self):
        """Kopiert den generierten Code"""
        try:
            code = self.code_text.get(1.0, tk.END)
            if not code.strip():
                UIUtils.show_warning("Warnung", "Kein Code zum Kopieren vorhanden!")
                return

            self.tab_frame.clipboard_clear()
            self.tab_frame.clipboard_append(code)

            # Feedback (nur Status-Label, kein Popup)
            self.code_info_label.config(text="📋 Code in Zwischenablage kopiert")

        except Exception as e:
            UIUtils.show_error("Kopier-Fehler", f"❌ Fehler beim Kopieren:\n{e}")

    def save_code_as_file(self):
        """Speichert Code als Datei"""
        try:
            code = self.code_text.get(1.0, tk.END)
            if not code.strip():
                UIUtils.show_warning("Warnung", "Kein Code zum Speichern vorhanden!")
                return

            # Dateiname vorschlagen
            state = get_state()
            if state.selected_file_path:
                base_name = os.path.basename(state.selected_file_path).replace('_metadata.json', '')
                suggested_name = f"punkt3_{base_name}_{CONFIG.get_timestamp()}.py"
            else:
                suggested_name = f"punkt3_code_{CONFIG.get_timestamp()}.py"

            filename = filedialog.asksaveasfilename(
                title="Punkt 3 Code speichern",
                defaultextension=".py",
                filetypes=[
                    ("Python files", "*.py"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ],
                initialfilename=suggested_name
            )

            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)

                self.code_info_label.config(text=f"💾 Code gespeichert: {os.path.basename(filename)}")

        except Exception as e:
            UIUtils.show_error("Speicher-Fehler", f"❌ Fehler beim Speichern:\n{e}")

    def execute_code(self):
        """Führt den generierten Code direkt aus"""
        try:
            code = self.code_text.get(1.0, tk.END)
            if not code.strip():
                UIUtils.show_warning("Warnung", "Kein Code zum Ausführen vorhanden!")
                return

            if not UIUtils.ask_yes_no("Code ausführen",
                                     "Möchten Sie den generierten Code direkt ausführen?\n\n"
                                     "⚠️ Stellen Sie sicher, dass alle Abhängigkeiten installiert sind."):
                return

            # Temporäre Datei erstellen
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_filename = f.name

            # Code ausführen
            import subprocess
            result = subprocess.run(['python', temp_filename],
                                  capture_output=True, text=True, timeout=300)

            # Temporäre Datei löschen
            os.unlink(temp_filename)

            if result.returncode == 0:
                self.code_info_label.config(text="✅ Code erfolgreich ausgeführt")
            else:
                UIUtils.show_error("Ausführung fehlgeschlagen",
                                  f"❌ Fehler bei Code-Ausführung:\n\n{result.stderr}")

        except subprocess.TimeoutExpired:
            UIUtils.show_error("Timeout", "❌ Code-Ausführung dauerte zu lange (>5 Min)")
        except Exception as e:
            UIUtils.show_error("Ausführungs-Fehler", f"❌ Fehler bei Code-Ausführung:\n{e}")

    def export_to_punkt4(self, silent=False):
        """Exportiert Code nach Punkt 4"""
        try:
            code = self.code_text.get(1.0, tk.END)
            if not code.strip():
                if not silent:
                    UIUtils.show_warning("Warnung", "Kein Code zum Exportieren vorhanden!")
                return

            # Punkt 4 Verzeichnis erstellen
            punkt4_dir = CONFIG.PATHS['punkt3_dir']
            os.makedirs(punkt4_dir, exist_ok=True)

            # Dateiname für Punkt 4
            state = get_state()
            if state.selected_file_path:
                base_name = os.path.basename(state.selected_file_path).replace('_metadata.json', '')
                punkt4_filename = f"punkt3_{base_name}_{CONFIG.get_timestamp()}.py"
            else:
                punkt4_filename = f"punkt3_export_{CONFIG.get_timestamp()}.py"

            punkt4_path = os.path.join(punkt4_dir, punkt4_filename)

            # Code schreiben
            with open(punkt4_path, 'w', encoding='utf-8') as f:
                f.write(code)

            # Kein Popup, nur Status-Label Update

            self.code_info_label.config(text=f"📤 Nach Punkt 4 exportiert: {punkt4_filename}")

        except Exception as e:
            if not silent:
                UIUtils.show_error("Export-Fehler", f"❌ Fehler beim Export nach Punkt 4:\n{e}")

    def create_backup(self, silent=False):
        """Erstellt Backup des Codes"""
        try:
            code = self.code_text.get(1.0, tk.END)
            if not code.strip():
                return

            # Backup-Verzeichnis erstellen
            backup_dir = CONFIG.PATHS['backup_dir']
            os.makedirs(backup_dir, exist_ok=True)

            # Backup-Dateiname
            state = get_state()
            if state.selected_file_path:
                base_name = os.path.basename(state.selected_file_path).replace('_metadata.json', '')
                backup_filename = f"punkt3_backup_{base_name}_{CONFIG.get_timestamp()}.py"
            else:
                backup_filename = f"punkt3_backup_{CONFIG.get_timestamp()}.py"

            backup_path = os.path.join(backup_dir, backup_filename)

            # Backup schreiben
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(code)

            # Kein Popup für Backup

        except Exception as e:
            if not silent:
                UIUtils.show_error("Backup-Fehler", f"❌ Fehler beim Backup:\n{e}")

    def generate_charts(self):
        """Generiert Charts basierend auf dem Code"""
        try:
            code = self.code_text.get(1.0, tk.END)
            if not code.strip():
                UIUtils.show_warning("Warnung", "Kein Code für Chart-Generierung vorhanden!")
                return

            UIUtils.show_info("Chart-Generierung",
                             "📊 Chart-Generierung wird implementiert...\n\n"
                             "Diese Funktion wird in einer zukünftigen Version verfügbar sein.")

        except Exception as e:
            UIUtils.show_error("Chart-Fehler", f"❌ Fehler bei Chart-Generierung:\n{e}")

    def show_summary(self):
        """Zeigt detaillierte Zusammenfassung"""
        try:
            state = get_state()

            # Zusammenfassung erstellen
            summary_text = "📊 PUNKT 3 ZUSAMMENFASSUNG\n"
            summary_text += "=" * 50 + "\n\n"

            # Datei-Info
            if state.selected_file_path:
                file_name = os.path.basename(state.selected_file_path).replace('_metadata.json', '')
                summary_text += f"📁 Datei: {file_name}\n"
                summary_text += f"📂 Pfad: {state.selected_file_path}\n\n"

            # Timeframe-Info
            summary_text += f"⏰ Timeframe-Modus: {state.timeframe_mode.title()}\n"
            summary_text += f"📊 Timeframes ({len(state.selected_timeframes)}):\n"
            for tf in state.selected_timeframes:
                summary_text += f"   • {tf}\n"
            summary_text += "\n"

            # Indikator-Info
            summary_text += f"📈 Indikatoren ({len(state.selected_indicators)}):\n"

            # Gruppiere nach Bibliothek
            by_library = {}
            for indicator in state.selected_indicators:
                lib = indicator['library']
                if lib not in by_library:
                    by_library[lib] = []
                by_library[lib].append(indicator)

            for library, indicators in sorted(by_library.items()):
                summary_text += f"   📚 {library} ({len(indicators)}):\n"
                for indicator in indicators:
                    summary_text += f"      • {indicator['display_name']}\n"
                summary_text += "\n"

            # Visualisierung-Info
            summary_text += f"🎨 Visualisierung: {state.visualization_mode}\n"
            summary_text += f"📅 Zeitraum: {state.visualization_period}\n\n"

            # Export-Optionen
            summary_text += "💾 Export-Optionen:\n"
            summary_text += f"   • Punkt 4: {'✅' if self.save_punkt4_var.get() else '❌'}\n"
            summary_text += f"   • Backup: {'✅' if self.save_backup_var.get() else '❌'}\n"
            summary_text += f"   • Charts: {'✅' if self.save_charts_var.get() else '❌'}\n"
            summary_text += f"   • Zusammenfassung: {'✅' if self.show_summary_var.get() else '❌'}\n\n"

            # Code-Statistiken
            code = self.code_text.get(1.0, tk.END)
            if code.strip():
                code_lines = len(code.split('\n'))
                code_chars = len(code)
                summary_text += f"📝 Code-Statistiken:\n"
                summary_text += f"   • Zeilen: {code_lines:,}\n"
                summary_text += f"   • Zeichen: {code_chars:,}\n"
                summary_text += f"   • Größe: {FormatUtils.format_file_size(len(code.encode('utf-8')))}\n\n"

            # Zeitstempel
            summary_text += f"🕐 Generiert am: {CONFIG.get_timestamp()}\n"

            # Zusammenfassung in Dialog anzeigen
            self.show_summary_dialog(summary_text)

        except Exception as e:
            UIUtils.show_error("Zusammenfassung-Fehler", f"❌ Fehler bei Zusammenfassung:\n{e}")

    def show_summary_dialog(self, summary_text: str):
        """Zeigt Zusammenfassung in eigenem Dialog"""
        dialog = tk.Toplevel(self.tab_frame)
        dialog.title("📊 Punkt 3 Zusammenfassung")
        dialog.geometry("600x700")
        dialog.transient(self.tab_frame)
        dialog.grab_set()

        UIUtils.center_window(dialog, 600, 700)

        # Hauptframe
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Text-Widget mit Scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        summary_text_widget = scrolledtext.ScrolledText(text_frame, width=70, height=35,
                                                       font=CONFIG.FONTS['small'],
                                                       wrap=tk.WORD)
        summary_text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        summary_text_widget.insert(1.0, summary_text)
        summary_text_widget.config(state='disabled')

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=(15, 0))

        def save_summary():
            filename = filedialog.asksaveasfilename(
                title="Zusammenfassung speichern",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfilename=f"punkt3_zusammenfassung_{CONFIG.get_timestamp()}.txt"
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(summary_text)
                UIUtils.show_info("Gespeichert", f"✅ Zusammenfassung gespeichert:\n{filename}")

        ttk.Button(button_frame, text="💾 Speichern", command=save_summary).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="📋 Kopieren",
                  command=lambda: dialog.clipboard_append(summary_text)).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Schließen", command=dialog.destroy).grid(row=0, column=2)

        # Grid-Konfiguration
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

    def get_tab_frame(self):
        """Gibt Tab-Frame zurück"""
        return self.tab_frame
