# 📊 PUNKT 3: TAB 2 - VISUALISIERUNG
# Zweite Tab für Chart-Typ und Visualisierungs-Konfiguration

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Optional

from Punkt3_settings import CONFIG
from Punkt3_events import emit_visualization_changed, emit_status_changed, on, Events
from Punkt3_state_manager import state_manager, get_state
from Punkt3_utils import UIUtils, ScrollableFrame

class Tab2Visualisierung:
    """Tab 2: Visualisierungs-Konfiguration"""

    def __init__(self, parent_notebook):
        self.notebook = parent_notebook
        self.logger = logging.getLogger(__name__)

        # Variablen
        self.viz_mode_var = tk.StringVar()
        self.viz_period_var = tk.StringVar()

        # Chart-Segmentierung Variablen
        self.enable_segmentation_var = tk.BooleanVar(value=False)
        self.candles_per_chart_var = tk.StringVar(value="30")
        self.chart_count_var = tk.StringVar(value="1")

        # Tab erstellen
        self.create_tab()

        # Event-Listener registrieren
        self.setup_event_listeners()

        # Initial laden
        self.load_state()

    def create_tab(self):
        """Erstellt Tab 2 GUI"""
        # Tab-Frame
        self.tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_frame, text="🎨 2. VISUALISIERUNG")

        # Scrollbares Frame erstellen
        self.scrollable = ScrollableFrame(self.tab_frame)
        self.scrollable.get_main_frame().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Container ist jetzt das scrollbare Frame
        container = self.scrollable.get_frame()

        # Padding hinzufügen
        container.configure(padding=CONFIG.GUI_CONFIG['tab_padding'])

        # 1. CHART-TYP SEKTION
        self.create_chart_type_section(container)

        # 2. ZEITRAUM SEKTION
        self.create_period_section(container)

        # 3. CHART-SEGMENTIERUNG
        self.create_segmentation_section(container)

        # 4. ERWEITERTE OPTIONEN
        self.create_advanced_options_section(container)

        # 5. VORSCHAU/INFO
        self.create_preview_section(container)

        # Grid-Konfiguration
        self.tab_frame.columnconfigure(0, weight=1)
        self.tab_frame.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(4, weight=1)  # Vorschau-Sektion soll expandieren

    def create_chart_type_section(self, parent):
        """Erstellt Chart-Typ Auswahl"""
        chart_frame = ttk.LabelFrame(parent, text="🎨 CHART-TYP AUSWAHL",
                                    padding=CONFIG.GUI_CONFIG['frame_padding'])
        chart_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        # Beschreibung
        desc_label = ttk.Label(chart_frame,
                              text="Wählen Sie den gewünschten Visualisierungs-Typ für Ihre Analyse:",
                              font=CONFIG.FONTS['normal'])
        desc_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        # Chart-Optionen
        chart_options_frame = ttk.Frame(chart_frame)
        chart_options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Erstelle Radio-Buttons für jede Option
        for i, option in enumerate(CONFIG.VISUALIZATION_MODES):
            # Icon und Beschreibung basierend auf Option
            icon, description = self.get_option_details(option)

            radio_frame = ttk.Frame(chart_options_frame)
            radio_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=3)

            radio_btn = ttk.Radiobutton(radio_frame, text=f"{icon} {option}",
                                       variable=self.viz_mode_var, value=option,
                                       command=self.on_visualization_change)
            radio_btn.grid(row=0, column=0, sticky=tk.W)

            # Beschreibung
            desc_label = ttk.Label(radio_frame, text=description,
                                  font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['info'])
            desc_label.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))

        chart_frame.columnconfigure(0, weight=1)
        chart_options_frame.columnconfigure(0, weight=1)

    def create_period_section(self, parent):
        """Erstellt Zeitraum-Auswahl"""
        period_frame = ttk.LabelFrame(parent, text="📅 VISUALISIERUNGS-ZEITRAUM",
                                     padding=CONFIG.GUI_CONFIG['frame_padding'])
        period_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        # Beschreibung
        desc_label = ttk.Label(period_frame,
                              text="Bestimmen Sie den Zeitraum für die Visualisierung (weniger Daten = bessere Performance):",
                              font=CONFIG.FONTS['normal'])
        desc_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        # Zeitraum-Dropdown
        period_dropdown_frame = ttk.Frame(period_frame)
        period_dropdown_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        ttk.Label(period_dropdown_frame, text="Zeitraum:",
                 font=CONFIG.FONTS['heading']).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.period_combo = ttk.Combobox(period_dropdown_frame, textvariable=self.viz_period_var,
                                        values=CONFIG.VISUALIZATION_PERIODS, width=50,
                                        state="readonly", font=CONFIG.FONTS['normal'])
        self.period_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.period_combo.bind('<<ComboboxSelected>>', self.on_period_change)

        # Performance-Hinweise
        self.create_performance_hints(period_frame)

        period_frame.columnconfigure(0, weight=1)
        period_dropdown_frame.columnconfigure(0, weight=1)

    def create_segmentation_section(self, parent):
        """Erstellt Chart-Segmentierung Sektion"""
        segmentation_frame = ttk.LabelFrame(parent, text="📊 CHART-SEGMENTIERUNG",
                                           padding=CONFIG.GUI_CONFIG['frame_padding'])
        segmentation_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        # Aktivierung
        enable_frame = ttk.Frame(segmentation_frame)
        enable_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        self.segmentation_checkbox = ttk.Checkbutton(enable_frame,
                                                    text="📊 Chart-Segmentierung aktivieren",
                                                    variable=self.enable_segmentation_var,
                                                    command=self.on_segmentation_toggle)
        self.segmentation_checkbox.grid(row=0, column=0, sticky=tk.W)

        # Beschreibung
        desc_label = ttk.Label(enable_frame,
                              text="Teilt große Zeiträume in kleinere Charts auf für bessere Übersicht",
                              font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['info'])
        desc_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # Konfiguration (initial versteckt)
        self.segmentation_config_frame = ttk.Frame(segmentation_frame)
        self.segmentation_config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Kerzen pro Chart
        candles_frame = ttk.Frame(self.segmentation_config_frame)
        candles_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(candles_frame, text="📈 Kerzen pro Chart:",
                 font=CONFIG.FONTS['heading']).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Dropdown für Kerzen-Anzahl
        candles_options = ["10", "20", "30", "50", "100", "200", "500", "1000"]
        self.candles_combo = ttk.Combobox(candles_frame, textvariable=self.candles_per_chart_var,
                                         values=candles_options, width=15, state="readonly")
        self.candles_combo.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.candles_combo.bind('<<ComboboxSelected>>', self.on_segmentation_change)

        # Info-Label für Kerzen
        self.candles_info_label = ttk.Label(candles_frame, text="Empfohlen: 30-100 für beste Sichtbarkeit",
                                           font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['info'])
        self.candles_info_label.grid(row=2, column=0, sticky=tk.W)

        # Ergebnis-Anzeige
        result_frame = ttk.Frame(self.segmentation_config_frame)
        result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(result_frame, text="📊 Ergebnis:",
                 font=CONFIG.FONTS['heading']).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Chart-Anzahl Anzeige
        self.chart_count_label = ttk.Label(result_frame, text="1 Chart wird generiert",
                                          font=CONFIG.FONTS['normal'], foreground=CONFIG.COLORS['primary'])
        self.chart_count_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        # Performance-Hinweis
        self.performance_hint_label = ttk.Label(result_frame, text="",
                                               font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['warning'])
        self.performance_hint_label.grid(row=2, column=0, sticky=tk.W)

        # Beispiel-Anzeige
        example_frame = ttk.LabelFrame(self.segmentation_config_frame, text="💡 BEISPIEL",
                                      padding=CONFIG.GUI_CONFIG['frame_padding'])
        example_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        self.example_label = ttk.Label(example_frame, text="Wählen Sie einen Zeitraum und Kerzen-Anzahl",
                                      font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['info'])
        self.example_label.grid(row=0, column=0, sticky=tk.W)

        # Grid-Konfiguration
        segmentation_frame.columnconfigure(0, weight=1)
        enable_frame.columnconfigure(0, weight=1)
        self.segmentation_config_frame.columnconfigure(0, weight=1)
        candles_frame.columnconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        example_frame.columnconfigure(0, weight=1)

        # Initial verstecken
        self.segmentation_config_frame.grid_remove()

    def create_performance_hints(self, parent):
        """Erstellt Performance-Hinweise"""
        hints_frame = ttk.LabelFrame(parent, text="💡 PERFORMANCE-TIPPS",
                                    padding=CONFIG.GUI_CONFIG['frame_padding'])
        hints_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(15, 0))

        hints = [
            "🚀 Interaktive Charts: 1-4 Wochen für beste Performance",
            "📊 Normale Charts: Bis zu 12 Wochen ohne Probleme",
            "📋 Tabellen: Alle Daten möglich, sehr schnell",
            "⚡ Weniger Indikatoren = Bessere Performance",
            "💾 Große Zeiträume benötigen mehr RAM"
        ]

        for i, hint in enumerate(hints):
            hint_label = ttk.Label(hints_frame, text=hint, font=CONFIG.FONTS['small'],
                                  foreground=CONFIG.COLORS['info'])
            hint_label.grid(row=i, column=0, sticky=tk.W, pady=2)

    def create_advanced_options_section(self, parent):
        """Erstellt erweiterte Optionen"""
        advanced_frame = ttk.LabelFrame(parent, text="⚙️ ERWEITERTE OPTIONEN",
                                       padding=CONFIG.GUI_CONFIG['frame_padding'])
        advanced_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        # Chart-Qualität
        quality_frame = ttk.Frame(advanced_frame)
        quality_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(quality_frame, text="Chart-Qualität:",
                 font=CONFIG.FONTS['heading']).grid(row=0, column=0, sticky=tk.W)

        self.quality_var = tk.StringVar(value="Hoch")
        quality_options = ["Niedrig (Schnell)", "Mittel", "Hoch (Standard)", "Sehr Hoch"]

        for i, option in enumerate(quality_options):
            ttk.Radiobutton(quality_frame, text=option, variable=self.quality_var,
                           value=option.split()[0], command=self.on_quality_change).grid(row=1, column=i, sticky=tk.W, padx=(0, 15))

        # Theme ist hardcoded auf plotly_dark (schwarz)
        self.theme_var = tk.StringVar(value="plotly_dark")  # Hardcoded schwarz

        advanced_frame.columnconfigure(0, weight=1)

    def create_preview_section(self, parent):
        """Erstellt Vorschau-Sektion"""
        preview_frame = ttk.LabelFrame(parent, text="👁️ KONFIGURATION VORSCHAU",
                                      padding=CONFIG.GUI_CONFIG['frame_padding'])
        preview_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Vorschau-Text
        self.preview_text = tk.Text(preview_frame, height=8, width=80,
                                   bg=CONFIG.COLORS['background'],
                                   font=CONFIG.FONTS['small'],
                                   wrap=tk.WORD, state='disabled')

        preview_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical",
                                         command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)

        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Kein Update-Button mehr - Vorschau wird automatisch aktualisiert

        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

    def setup_event_listeners(self):
        """Registriert Event-Listener"""
        # Lausche auf Datei-Änderungen für Kontext-Updates
        on(Events.FILE_SELECTED, self.on_file_changed)
        on(Events.TIMEFRAMES_CHANGED, self.on_timeframes_changed)
        on(Events.INDICATORS_CHANGED, self.on_indicators_changed)

    def get_option_details(self, option: str) -> tuple[str, str]:
        """Gibt Icon und Beschreibung für Visualisierungs-Option zurück"""
        details = {
            "Interaktive Charts mit Indikatoren": ("🔄", "Plotly-basierte interaktive Charts mit Zoom/Pan"),
            "Normale Charts mit Indikatoren": ("📊", "Statische Charts, schneller zu generieren"),
            "Nur Daten-Tabellen": ("📋", "Nur tabellarische Ausgabe, sehr schnell"),
            "Charts + Tabellen": ("📊📋", "Kombination aus Charts und Tabellen"),
            "Keine Visualisierung": ("❌", "Nur Code-Generierung ohne Visualisierung")
        }
        return details.get(option, ("📊", "Standard-Visualisierung"))

    def on_visualization_change(self):
        """Wird aufgerufen wenn Visualisierungs-Modus geändert wird"""
        mode = self.viz_mode_var.get()
        period = self.viz_period_var.get()

        # State aktualisieren
        state_manager.set_visualization(mode, period)

        # Event senden
        emit_visualization_changed("tab2", mode, period)

        # Vorschau aktualisieren
        self.update_preview()

        self.logger.info(f"Visualisierungs-Modus geändert: {mode}")

    def on_period_change(self, event=None):
        """Wird aufgerufen wenn Zeitraum geändert wird"""
        mode = self.viz_mode_var.get()
        period = self.viz_period_var.get()

        # State aktualisieren
        state_manager.set_visualization(mode, period)

        # Event senden
        emit_visualization_changed("tab2", mode, period)

        # Vorschau aktualisieren
        self.update_preview()

        self.logger.info(f"Visualisierungs-Zeitraum geändert: {period}")

    def on_segmentation_toggle(self):
        """Wird aufgerufen wenn Segmentierung aktiviert/deaktiviert wird"""
        enabled = self.enable_segmentation_var.get()

        if enabled:
            self.segmentation_config_frame.grid()
            self.calculate_segmentation()
        else:
            self.segmentation_config_frame.grid_remove()

        # State Manager aktualisieren
        state_manager.set_segmentation(enabled, self.candles_per_chart_var.get())

        # Vorschau aktualisieren
        self.update_preview()

        self.logger.info(f"Chart-Segmentierung {'aktiviert' if enabled else 'deaktiviert'}")

    def on_segmentation_change(self, event=None):
        """Wird aufgerufen wenn Segmentierung-Parameter geändert werden"""
        self.calculate_segmentation()

        # State Manager aktualisieren
        if self.enable_segmentation_var.get():
            state_manager.set_segmentation(True, self.candles_per_chart_var.get())

        self.update_preview()

    def on_quality_change(self):
        """Wird aufgerufen wenn Chart-Qualität geändert wird"""
        quality = self.quality_var.get()
        state_manager.set_chart_options(quality=quality, theme='plotly_dark')  # Theme hardcoded
        self.update_preview()

    # Theme ist hardcoded - keine on_theme_change Funktion nötig

    def calculate_segmentation(self):
        """Berechnet Chart-Segmentierung basierend auf Zeitraum und Kerzen pro Chart"""
        try:
            period = self.viz_period_var.get()
            candles_per_chart = int(self.candles_per_chart_var.get())

            # Extrahiere Kerzen-Anzahl aus Zeitraum
            total_candles = self.extract_candles_from_period(period)

            if total_candles > 0:
                # Berechne Anzahl Charts
                chart_count = max(1, (total_candles + candles_per_chart - 1) // candles_per_chart)

                # Aktualisiere Anzeige
                self.chart_count_label.config(text=f"{chart_count} Charts werden generiert")

                # Performance-Hinweis
                if chart_count > 50:
                    self.performance_hint_label.config(text="⚠️ Sehr viele Charts - kann langsam werden")
                elif chart_count > 20:
                    self.performance_hint_label.config(text="💡 Viele Charts - mittlere Performance")
                elif chart_count > 10:
                    self.performance_hint_label.config(text="✅ Gute Anzahl Charts")
                else:
                    self.performance_hint_label.config(text="⚡ Wenige Charts - sehr schnell")

                # Beispiel aktualisieren
                self.update_segmentation_example(period, total_candles, candles_per_chart, chart_count)

            else:
                self.chart_count_label.config(text="Zeitraum auswählen für Berechnung")
                self.performance_hint_label.config(text="")
                self.example_label.config(text="Wählen Sie einen Zeitraum für Beispiel-Berechnung")

        except ValueError:
            self.chart_count_label.config(text="Ungültige Kerzen-Anzahl")
            self.performance_hint_label.config(text="")

    def extract_candles_from_period(self, period: str) -> int:
        """Extrahiert Kerzen-Anzahl aus Zeitraum-String"""
        if not period:
            return 0

        # Mapping für verschiedene Zeiträume (basierend auf 5m Kerzen)
        period_mappings = {
            "1 Tag": 288,
            "2 Tage": 576,
            "3 Tage": 864,
            "1 Woche": 2016,
            "2 Wochen": 4032,
            "4 Wochen": 8064,
            "8 Wochen": 16128,
            "12 Wochen": 24192,
            "20 Wochen": 40320,
            "52 Wochen": 104832
        }

        # Suche nach bekannten Zeiträumen
        for key, candles in period_mappings.items():
            if key in period:
                return candles

        # Versuche Kerzen-Anzahl direkt zu extrahieren
        import re
        match = re.search(r'(\d+)\s*Kerzen', period)
        if match:
            return int(match.group(1))

        # Fallback für "Alle Daten"
        if "Alle Daten" in period:
            return 50000  # Schätzung

        return 0

    def update_segmentation_example(self, period: str, total_candles: int, candles_per_chart: int, chart_count: int):
        """Aktualisiert Segmentierung-Beispiel"""
        example_text = f"📊 {period} = {total_candles:,} Kerzen\n"
        example_text += f"📈 {candles_per_chart} Kerzen pro Chart\n"
        example_text += f"🔢 Ergebnis: {chart_count} Charts\n"

        if chart_count > 1:
            last_chart_candles = total_candles % candles_per_chart
            if last_chart_candles == 0:
                last_chart_candles = candles_per_chart

            example_text += f"💡 Charts 1-{chart_count-1}: je {candles_per_chart} Kerzen\n"
            example_text += f"💡 Chart {chart_count}: {last_chart_candles} Kerzen"

        self.example_label.config(text=example_text)

    def update_preview(self):
        """Aktualisiert die Konfiguration-Vorschau"""
        state = get_state()

        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)

        preview_text = "📊 AKTUELLE VISUALISIERUNGS-KONFIGURATION:\n\n"

        # Chart-Typ
        mode = self.viz_mode_var.get()
        if mode:
            icon, desc = self.get_option_details(mode)
            preview_text += f"🎨 Chart-Typ: {icon} {mode}\n"
            preview_text += f"   └─ {desc}\n\n"
        else:
            preview_text += "🎨 Chart-Typ: Nicht ausgewählt\n\n"

        # Zeitraum
        period = self.viz_period_var.get()
        if period:
            preview_text += f"📅 Zeitraum: {period}\n"

            # Performance-Schätzung
            if "1 Tag" in period or "2 Tage" in period:
                preview_text += "   └─ ⚡ Sehr schnell\n\n"
            elif "1 Woche" in period or "2 Wochen" in period:
                preview_text += "   └─ 🚀 Schnell\n\n"
            elif "4 Wochen" in period or "8 Wochen" in period:
                preview_text += "   └─ 📊 Mittel\n\n"
            elif "Alle Daten" in period:
                preview_text += "   └─ ⏳ Langsam (abhängig von Datenmenge)\n\n"
            else:
                preview_text += "   └─ 📈 Performance abhängig von Datenmenge\n\n"
        else:
            preview_text += "📅 Zeitraum: Nicht ausgewählt\n\n"

        # Chart-Segmentierung
        if self.enable_segmentation_var.get():
            candles_per_chart = self.candles_per_chart_var.get()
            total_candles = self.extract_candles_from_period(period)
            if total_candles > 0:
                chart_count = max(1, (total_candles + int(candles_per_chart) - 1) // int(candles_per_chart))
                preview_text += f"📊 Segmentierung: AKTIVIERT\n"
                preview_text += f"   └─ {candles_per_chart} Kerzen pro Chart\n"
                preview_text += f"   └─ {chart_count} Charts werden generiert\n\n"
            else:
                preview_text += f"📊 Segmentierung: AKTIVIERT (Berechnung ausstehend)\n\n"
        else:
            preview_text += f"📊 Segmentierung: Deaktiviert (1 großer Chart)\n\n"

        # Erweiterte Optionen
        quality = self.quality_var.get()
        preview_text += f"⚙️ Qualität: {quality}\n"
        preview_text += f"🎨 Theme: Schwarz (hardcoded)\n\n"

        # Kontext-Informationen
        preview_text += "📋 KONTEXT-INFORMATIONEN:\n\n"

        if state.selected_file_path:
            file_name = state.selected_file_path.split('/')[-1].replace('_metadata.json', '')
            preview_text += f"📁 Datei: {file_name}\n"
        else:
            preview_text += "📁 Datei: Nicht ausgewählt\n"

        tf_count = len(state.selected_timeframes) if state.selected_timeframes else 0
        preview_text += f"⏰ Timeframes: {tf_count}\n"

        indicator_count = len(state.selected_indicators) if state.selected_indicators else 0
        preview_text += f"📈 Indikatoren: {indicator_count}\n\n"

        # Empfehlungen
        preview_text += "💡 EMPFEHLUNGEN:\n\n"

        if mode == "Interaktive Charts mit Indikatoren":
            if indicator_count > 10:
                preview_text += "⚠️ Viele Indikatoren können interaktive Charts verlangsamen\n"
            if "Alle Daten" in period:
                preview_text += "⚠️ 'Alle Daten' kann bei interaktiven Charts langsam sein\n"
            preview_text += "✅ Ideal für explorative Datenanalyse\n"

        elif mode == "Normale Charts mit Indikatoren":
            preview_text += "✅ Gute Balance zwischen Qualität und Performance\n"
            if indicator_count > 20:
                preview_text += "⚠️ Sehr viele Indikatoren können Charts überladen\n"

        elif mode == "Nur Daten-Tabellen":
            preview_text += "✅ Sehr schnell, ideal für Datenexport\n"
            preview_text += "💡 Perfekt für weitere Verarbeitung in Excel/Python\n"

        # Segmentierung-spezifische Empfehlungen
        if self.enable_segmentation_var.get():
            candles_per_chart = int(self.candles_per_chart_var.get())
            total_candles = self.extract_candles_from_period(period)

            if total_candles > 0:
                chart_count = max(1, (total_candles + candles_per_chart - 1) // candles_per_chart)

                preview_text += f"\n📊 SEGMENTIERUNG-EMPFEHLUNGEN:\n"

                if candles_per_chart < 20:
                    preview_text += "⚠️ Sehr wenige Kerzen pro Chart - Details schwer erkennbar\n"
                elif candles_per_chart > 500:
                    preview_text += "⚠️ Sehr viele Kerzen pro Chart - Übersicht geht verloren\n"
                else:
                    preview_text += "✅ Gute Kerzen-Anzahl pro Chart\n"

                if chart_count > 30:
                    preview_text += "💡 Viele Charts - Navigation könnte aufwendig werden\n"
                elif chart_count > 10:
                    preview_text += "✅ Moderate Anzahl Charts - gute Balance\n"
                else:
                    preview_text += "⚡ Wenige Charts - schnelle Navigation\n"

                # Spezielle Empfehlungen basierend auf Modus
                if mode == "Interaktive Charts mit Indikatoren" and chart_count > 20:
                    preview_text += "💡 Bei vielen interaktiven Charts: Normale Charts erwägen\n"

        self.preview_text.insert(1.0, preview_text)
        self.preview_text.config(state='disabled')

    def on_file_changed(self, event_data):
        """Wird aufgerufen wenn Datei geändert wird"""
        self.update_preview()

    def on_timeframes_changed(self, event_data):
        """Wird aufgerufen wenn Timeframes geändert werden"""
        self.update_preview()

    def on_indicators_changed(self, event_data):
        """Wird aufgerufen wenn Indikatoren geändert werden"""
        self.update_preview()

    def load_state(self):
        """Lädt Zustand aus State Manager"""
        state = get_state()

        # Visualisierungs-Modus setzen
        if state.visualization_mode:
            self.viz_mode_var.set(state.visualization_mode)
        else:
            self.viz_mode_var.set(CONFIG.DEFAULTS['visualization_mode'])

        # Visualisierungs-Zeitraum setzen
        if state.visualization_period:
            self.viz_period_var.set(state.visualization_period)
        else:
            self.viz_period_var.set(CONFIG.DEFAULTS['visualization_period'])

        # Segmentierung laden (falls gespeichert)
        # Standardmäßig deaktiviert
        self.enable_segmentation_var.set(False)
        self.candles_per_chart_var.set("30")

        # Vorschau aktualisieren
        self.update_preview()

    def get_configuration(self) -> Dict:
        """Gibt aktuelle Konfiguration zurück"""
        config = {
            'visualization_mode': self.viz_mode_var.get(),
            'visualization_period': self.viz_period_var.get(),
            'quality': self.quality_var.get(),
            'theme': 'plotly_dark',  # Hardcoded schwarz
            'enable_segmentation': self.enable_segmentation_var.get(),
            'candles_per_chart': self.candles_per_chart_var.get()
        }

        # Segmentierung-Details hinzufügen
        if config['enable_segmentation']:
            period = config['visualization_period']
            total_candles = self.extract_candles_from_period(period)
            candles_per_chart = int(config['candles_per_chart'])

            if total_candles > 0:
                chart_count = max(1, (total_candles + candles_per_chart - 1) // candles_per_chart)
                config['segmentation_details'] = {
                    'total_candles': total_candles,
                    'chart_count': chart_count,
                    'candles_per_chart': candles_per_chart
                }

        return config

    def get_tab_frame(self):
        """Gibt Tab-Frame zurück"""
        return self.tab_frame
