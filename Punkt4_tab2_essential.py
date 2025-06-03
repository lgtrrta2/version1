# 📊 PUNKT 4: PARAMETER-KONFIGURATOR - TAB 2: ESSENTIAL PARAMETERS
# VectorBT Pro Essential Parameter für Portfolio-Backtesting

import tkinter as tk
from tkinter import ttk
import numpy as np
from typing import Dict, Any, List
import logging

from Punkt4_settings import CONFIG
from Punkt4_events import emit, on, Events
from Punkt4_state_manager import get_vbt_parameter, set_vbt_parameter, get_all_vbt_parameters
from Punkt4_utils import UIUtils, VBTUtils

class Tab2Essential:
    """Tab 2: Essential VectorBT Pro Parameter"""
    
    def __init__(self, parent):
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        
        # Parameter Widgets Storage
        self.parameter_widgets = {}
        self.parameter_vars = {}
        
        # UI Setup
        self.setup_ui()
        self.setup_events()
        
        # Initial Load
        self.load_parameters_from_state()
    
    def setup_ui(self):
        """UI-Komponenten erstellen"""
        # Main Container mit Scrollbar
        self.canvas = tk.Canvas(self.parent)
        self.scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack Canvas und Scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Main Frame
        self.main_frame = ttk.Frame(self.scrollable_frame, padding=CONFIG.GUI['tab_padding'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        title_label = ttk.Label(header_frame, text="📊 ESSENTIAL PARAMETER",
                               font=('TkDefaultFont', 14, 'bold'))
        title_label.pack(anchor=tk.W)

        subtitle_label = ttk.Label(header_frame,
                                  text="Grundlegende Trading-Parameter für Futures-Backtesting (NQ Standard)",
                                  font=('TkDefaultFont', 9))
        subtitle_label.pack(anchor=tk.W, pady=(0, 10))

        # 2-Spalten Layout
        columns_frame = ttk.Frame(self.main_frame)
        columns_frame.pack(fill=tk.BOTH, expand=True)

        # Linke Spalte
        self.left_column = ttk.Frame(columns_frame)
        self.left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Rechte Spalte
        self.right_column = ttk.Frame(columns_frame)
        self.right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Parameter Sektionen verteilen
        self.create_left_column_sections()
        self.create_right_column_sections()

        # === AKTIONS-BUTTONS ===
        self.create_action_buttons()
        
        # Mouse Wheel Binding für Scrolling
        self.bind_mousewheel()

    def on_session_enabled_changed(self):
        """Session Trading aktiviert/deaktiviert"""
        enabled = self.session_enabled_var.get()
        if enabled:
            self.update_final_time_display()
        else:
            self.session_info_var.set("Alle Zeiten (24/7 Trading)")
            self.final_time_var.set("24/7 Trading (Alle Zeiten)")
            self.time_details_var.set("Kontinuierliches Trading ohne Zeitbeschränkung")

    def on_session_checkbox_changed(self, *args):
        """Session Checkbox geändert"""
        if self.session_enabled_var.get():
            self.update_final_time_display()

    def update_final_time_display(self):
        """Aktualisiert die finale Zeit-Anzeige basierend auf Checkbox-Auswahl"""
        if not self.session_enabled_var.get():
            return

        # Ausgewählte Sessions aus Checkboxen sammeln
        selected_sessions = []
        time_ranges = []

        # Standard Sessions prüfen
        session_mapping = {
            'asia_full': ("22:00", "08:00", "Asia Full"),
            'asia_part1': ("22:00", "03:00", "Asia Teil 1"),
            'asia_part2': ("03:00", "08:00", "Asia Teil 2"),
            'london_full': ("08:00", "16:00", "London Full"),
            'london_part1': ("08:00", "12:00", "London Teil 1"),
            'london_part2': ("12:00", "16:00", "London Teil 2"),
            'ny_full': ("13:00", "21:00", "New York Full"),
            'ny_part1': ("13:00", "17:00", "New York Teil 1"),
            'ny_part2': ("17:00", "21:00", "New York Teil 2"),
        }

        for session_key, (start, end, name) in session_mapping.items():
            if session_key in self.session_vars and self.session_vars[session_key].get():
                selected_sessions.append(name)
                time_ranges.append((start, end))

        # Custom Sessions prüfen
        for i in range(1, 4):  # Custom 1, 2, 3
            enabled_key = f'custom{i}_enabled'
            time_key = f'custom{i}_time'

            if (enabled_key in self.session_vars and
                self.session_vars[enabled_key].get() and
                time_key in self.session_vars):

                time_str = self.session_vars[time_key].get()
                if '-' in time_str:
                    try:
                        start, end = time_str.split('-')
                        start = start.strip()
                        end = end.strip()
                        selected_sessions.append(f"Custom {i} ({start}-{end})")
                        time_ranges.append((start, end))
                    except:
                        pass  # Ignoriere ungültige Formate

        if not time_ranges:
            self.final_time_var.set("Keine Session ausgewählt")
            self.time_details_var.set("Bitte wähle mindestens eine Session")
            return

        # WICHTIG: Bereiche NICHT kombinieren für getrennte Sessions
        # Jeder Bereich bleibt separat für präzise Session-Kontrolle
        separate_ranges = self.validate_and_sort_ranges(time_ranges)

        # Anzeige aktualisieren
        if len(separate_ranges) == 1:
            start, end = separate_ranges[0]
            self.final_time_var.set(f"{start}-{end} UTC")

            # Stunden berechnen
            hours = self.calculate_hours(start, end)
            session_names = " + ".join(selected_sessions)
            self.time_details_var.set(f"{session_names}: {hours:.1f} Stunden Trading")
        else:
            # Mehrere getrennte Bereiche (KEIN Trading dazwischen!)
            range_strs = [f"{start}-{end}" for start, end in separate_ranges]
            self.final_time_var.set(" + ".join(range_strs) + " UTC")

            total_hours = sum(self.calculate_hours(start, end) for start, end in separate_ranges)
            session_names = " + ".join(selected_sessions)
            self.time_details_var.set(f"{session_names}: {total_hours:.1f} Stunden Trading (getrennte Bereiche)")

        # Session Info auch aktualisieren
        if len(selected_sessions) == 1:
            self.session_info_var.set(f"Session Trading: {selected_sessions[0]}")
        else:
            self.session_info_var.set(f"Multi-Session Trading: {len(selected_sessions)} Sessions")

    def validate_and_sort_ranges(self, time_ranges):
        """Validiert und sortiert Zeit-Bereiche (OHNE Kombination)"""
        valid_ranges = []

        for start, end in time_ranges:
            try:
                # Validiere Zeit-Format
                start_parts = start.split(':')
                end_parts = end.split(':')

                if len(start_parts) == 2 and len(end_parts) == 2:
                    start_hour, start_min = map(int, start_parts)
                    end_hour, end_min = map(int, end_parts)

                    if (0 <= start_hour <= 23 and 0 <= start_min <= 59 and
                        0 <= end_hour <= 23 and 0 <= end_min <= 59):
                        valid_ranges.append((start, end))
            except:
                pass  # Ignoriere ungültige Zeiten

        # Sortiere nach Start-Zeit (für bessere Anzeige)
        def time_to_minutes(time_str):
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes

        valid_ranges.sort(key=lambda x: time_to_minutes(x[0]))
        return valid_ranges

    def combine_time_ranges(self, time_ranges):
        """Kombiniert überlappende Zeit-Bereiche"""
        if not time_ranges:
            return []

        # Konvertiere zu Minuten für einfachere Berechnung
        def time_to_minutes(time_str):
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes

        def minutes_to_time(minutes):
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours:02d}:{mins:02d}"

        # Konvertiere alle Bereiche
        ranges_minutes = []
        for start, end in time_ranges:
            start_min = time_to_minutes(start)
            end_min = time_to_minutes(end)

            # Handle overnight sessions (z.B. Asia 22:00-08:00)
            if end_min < start_min:
                # Split in zwei Bereiche: start-24:00 und 00:00-end
                ranges_minutes.append((start_min, 24*60))  # bis Mitternacht
                ranges_minutes.append((0, end_min))        # ab Mitternacht
            else:
                ranges_minutes.append((start_min, end_min))

        # Sortiere und kombiniere überlappende Bereiche
        ranges_minutes.sort()
        combined = []

        for start, end in ranges_minutes:
            if not combined or start > combined[-1][1]:
                # Kein Overlap
                combined.append((start, end))
            else:
                # Overlap - erweitere letzten Bereich
                combined[-1] = (combined[-1][0], max(combined[-1][1], end))

        # Zurück zu Zeit-Strings
        result = []
        for start_min, end_min in combined:
            start_str = minutes_to_time(start_min)
            end_str = minutes_to_time(end_min)
            result.append((start_str, end_str))

        return result

    def calculate_hours(self, start_time, end_time):
        """Berechnet Stunden zwischen zwei Zeiten"""
        def time_to_minutes(time_str):
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes

        start_min = time_to_minutes(start_time)
        end_min = time_to_minutes(end_time)

        if end_min < start_min:
            # Overnight session
            return (24*60 - start_min + end_min) / 60
        else:
            return (end_min - start_min) / 60

    def on_session_type_changed(self, event=None):
        """Session Type geändert"""
        self.update_session_details()
        self.update_session_part_info()
        self.update_session_info()

        # Custom Frame anzeigen/verstecken
        if self.session_type_var.get() == "CUSTOM":
            self.custom_frame.pack(fill=tk.X, pady=5)
        else:
            self.custom_frame.pack_forget()

    def on_session_part_changed(self, event=None):
        """Session Part geändert"""
        self.update_session_part_info()
        self.update_session_info()

    def on_custom_time_changed(self, *args):
        """Custom Time geändert"""
        if self.session_type_var.get() == "CUSTOM":
            self.update_session_info()

    def update_session_details(self):
        """Aktualisiert Session Details"""
        session_type = self.session_type_var.get()

        session_specs = {
            "ASIA": {
                "name": "🇦🇺 Asia Session",
                "time": "22:00-08:00 UTC",
                "description": "Sydney + Tokyo"
            },
            "LONDON": {
                "name": "🇬🇧 London Session",
                "time": "08:00-16:00 UTC",
                "description": "European Markets"
            },
            "NEW_YORK": {
                "name": "🇺🇸 New York Session",
                "time": "13:00-21:00 UTC",
                "description": "US Markets"
            },
            "CUSTOM": {
                "name": "🔧 Custom Session",
                "time": "User Defined",
                "description": "Eigene Zeiten"
            }
        }

        if session_type in session_specs:
            spec = session_specs[session_type]
            self.session_details_var.set(f"{spec['name']} - {spec['time']}")

    def update_session_part_info(self):
        """Aktualisiert Session Part Info"""
        session_type = self.session_type_var.get()
        session_part = self.session_part_var.get()

        if session_type == "CUSTOM":
            self.session_part_info_var.set("Custom Zeiten verwenden")
            return

        # Session Zeiten definieren
        session_times = {
            "ASIA": ("22:00", "08:00"),      # 10 Stunden
            "LONDON": ("08:00", "16:00"),    # 8 Stunden
            "NEW_YORK": ("13:00", "21:00")   # 8 Stunden
        }

        if session_type in session_times:
            start, end = session_times[session_type]

            if session_part == "FULL":
                self.session_part_info_var.set(f"Komplette Session: {start}-{end}")
            elif session_part == "PART_1":
                # Erste Hälfte berechnen
                if session_type == "ASIA":
                    self.session_part_info_var.set("Teil 1: 22:00-03:00 (5h)")
                elif session_type == "LONDON":
                    self.session_part_info_var.set("Teil 1: 08:00-12:00 (4h)")
                elif session_type == "NEW_YORK":
                    self.session_part_info_var.set("Teil 1: 13:00-17:00 (4h)")
            elif session_part == "PART_2":
                # Zweite Hälfte berechnen
                if session_type == "ASIA":
                    self.session_part_info_var.set("Teil 2: 03:00-08:00 (5h)")
                elif session_type == "LONDON":
                    self.session_part_info_var.set("Teil 2: 12:00-16:00 (4h)")
                elif session_type == "NEW_YORK":
                    self.session_part_info_var.set("Teil 2: 17:00-21:00 (4h)")

    def update_session_info(self):
        """Aktualisiert Session Info"""
        if not self.session_enabled_var.get():
            return

        session_type = self.session_type_var.get()
        session_part = self.session_part_var.get()

        if session_type == "CUSTOM":
            start = self.custom_start_var.get()
            end = self.custom_end_var.get()
            self.session_info_var.set(f"Custom Trading: {start}-{end} UTC")
        else:
            # Berechne aktuelle Session-Zeiten
            session_times = {
                "ASIA": {
                    "FULL": "22:00-08:00",
                    "PART_1": "22:00-03:00",
                    "PART_2": "03:00-08:00"
                },
                "LONDON": {
                    "FULL": "08:00-16:00",
                    "PART_1": "08:00-12:00",
                    "PART_2": "12:00-16:00"
                },
                "NEW_YORK": {
                    "FULL": "13:00-21:00",
                    "PART_1": "13:00-17:00",
                    "PART_2": "17:00-21:00"
                }
            }

            if session_type in session_times and session_part in session_times[session_type]:
                time_range = session_times[session_type][session_part]
                self.session_info_var.set(f"{session_type} {session_part}: {time_range} UTC")

    def create_futures_instrument_widget(self, parent):
        """Erstellt Futures Instrument Auswahl mit automatischen Standards"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        # Label
        label = ttk.Label(frame, text="Futures Instrument:", font=('TkDefaultFont', 9, 'bold'))
        label.pack(anchor=tk.W)

        # Combobox mit Futures Standards
        self.futures_var = tk.StringVar(value="NQ")
        futures_combo = ttk.Combobox(frame, textvariable=self.futures_var,
                                   values=["NQ", "ES", "GC", "CL"],
                                   state="readonly", width=10)
        futures_combo.pack(anchor=tk.W, pady=2)

        # Info Label
        self.futures_info_var = tk.StringVar()
        info_label = ttk.Label(frame, textvariable=self.futures_info_var,
                              font=('TkDefaultFont', 8), foreground='blue')
        info_label.pack(anchor=tk.W)

        # Event Handler
        futures_combo.bind('<<ComboboxSelected>>', self.on_futures_changed)

        # Initial Update
        self.update_futures_standards()

    def on_futures_changed(self, event=None):
        """Handler für Futures Instrument Änderung"""
        self.update_futures_standards()

    def update_futures_standards(self):
        """Aktualisiert Standards basierend auf gewähltem Futures Instrument"""
        instrument = self.futures_var.get()

        # Futures Standards
        futures_specs = {
            "NQ": {
                "name": "Nasdaq 100 E-mini",
                "tick_size": 0.25,
                "tick_value": 5.0,  # $5 per point (4 ticks = 1 point)
                "fees": 4.20,
                "sl_ticks": 25,     # 25 ticks = 6.25 points = $31.25
                "tp_ticks": 50      # 50 ticks = 12.5 points = $62.50
            },
            "ES": {
                "name": "S&P 500 E-mini",
                "tick_size": 0.25,
                "tick_value": 12.50,
                "fees": 4.20,
                "sl_ticks": 20,
                "tp_ticks": 40
            },
            "GC": {
                "name": "Gold",
                "tick_size": 0.10,
                "tick_value": 10.0,
                "fees": 5.50,
                "sl_ticks": 30,
                "tp_ticks": 60
            },
            "CL": {
                "name": "Crude Oil",
                "tick_size": 0.01,
                "tick_value": 10.0,
                "fees": 4.80,
                "sl_ticks": 25,
                "tp_ticks": 50
            }
        }

        if instrument in futures_specs:
            spec = futures_specs[instrument]

            # Info Text aktualisieren
            self.futures_info_var.set(
                f"{spec['name']} - Tick: ${spec['tick_value']:.2f} - Fees: ${spec['fees']:.2f}"
            )

            # Parameter automatisch setzen
            if hasattr(self, 'parameter_widgets'):
                if 'tick_size' in self.parameter_widgets:
                    self.parameter_widgets['tick_size']['var'].set(spec['tick_size'])
                if 'fixed_fees' in self.parameter_widgets:
                    self.parameter_widgets['fixed_fees']['var'].set(spec['fees'])
                if 'sl_stop' in self.parameter_widgets:
                    self.parameter_widgets['sl_stop']['var'].set(spec['sl_ticks'])
                if 'tp_stop' in self.parameter_widgets:
                    self.parameter_widgets['tp_stop']['var'].set(spec['tp_ticks'])

            print(f"DEBUG: Futures Standards gesetzt für {instrument}: {spec}")

    def create_left_column_sections(self):
        """Erstellt Sektionen für die linke Spalte"""
        # === PORTFOLIO GRUNDLAGEN ===
        self.create_portfolio_basics_section_left()

        # === POSITION MANAGEMENT ===
        self.create_position_management_section_left()

        # === STOP LOSS & TAKE PROFIT ===
        self.create_stop_profit_section_left()

        # === PERFORMANCE & LOGGING ===
        self.create_performance_section_left()

    def create_right_column_sections(self):
        """Erstellt Sektionen für die rechte Spalte"""
        # === FEES & SLIPPAGE ===
        self.create_fees_section_right()

        # === SESSION TRADING ===
        self.create_session_trading_section_right()

    def create_portfolio_basics_section_left(self):
        """Portfolio Grundlagen Sektion (Linke Spalte)"""
        section = UIUtils.create_parameter_section(self.left_column,
                                                  "💰 PORTFOLIO GRUNDLAGEN",
                                                  ['init_cash', 'cash_sharing', 'log', 'use_numba'])

        # Initial Cash
        self.create_parameter_widget(section, 'init_cash', 'Initial Cash ($)', 'float',
                                    description="Startkapital für das Portfolio")

        # Cash Sharing
        self.create_parameter_widget(section, 'cash_sharing', 'Cash Sharing', 'bool',
                                    description="Cash-Sharing zwischen Assets aktivieren")

        # Logging
        self.create_parameter_widget(section, 'log', 'Portfolio Logging', 'bool',
                                    description="Detailliertes Portfolio-Logging aktivieren")

        # Numba Optimierung
        self.create_parameter_widget(section, 'use_numba', 'Numba Optimierung', 'bool',
                                    description="Numba JIT-Kompilierung für Performance aktivieren")

    def create_position_management_section_left(self):
        """Position Management Sektion (Linke Spalte)"""
        section = UIUtils.create_parameter_section(self.left_column,
                                                  "📈 POSITION MANAGEMENT",
                                                  ['size', 'size_type', 'direction'])

        # Position Size
        self.create_parameter_widget(section, 'size', 'Position Size', 'float',
                                    description="Anzahl Kontrakte pro Trade (NQ Standard: 1)")

        # Size Type
        self.create_parameter_widget(section, 'size_type', 'Size Type', 'enum',
                                    choices=CONFIG.ENUM_CHOICES['size_type'],
                                    description="Art der Positionsgrößenangabe")

        # Direction
        self.create_parameter_widget(section, 'direction', 'Trading Direction', 'enum',
                                    choices=CONFIG.ENUM_CHOICES['direction'],
                                    description="Erlaubte Trading-Richtungen")

    def create_stop_profit_section_left(self):
        """Stop Loss & Take Profit Sektion (Linke Spalte)"""
        section = UIUtils.create_parameter_section(self.left_column,
                                                  "🛡️ STOP LOSS & TAKE PROFIT",
                                                  ['sl_stop', 'tp_stop', 'tick_size'])

        # Futures Instrument Auswahl
        self.create_futures_instrument_widget(section)

        # Stop Loss
        self.create_parameter_widget(section, 'sl_stop', 'Stop Loss (Ticks)', 'float',
                                    description="Stop Loss in Ticks (NQ: 25 Ticks = 6.25 Punkte = $31.25)")

        # Take Profit
        self.create_parameter_widget(section, 'tp_stop', 'Take Profit (Ticks)', 'float',
                                    description="Take Profit in Ticks (NQ: 50 Ticks = 12.5 Punkte = $62.50)")

        # Tick Size (wird automatisch gesetzt)
        self.create_parameter_widget(section, 'tick_size', 'Tick Size', 'float',
                                    description="Tick-Größe des Instruments (automatisch gesetzt)")

    def create_performance_section_left(self):
        """Performance & Logging Sektion (Linke Spalte)"""
        section = UIUtils.create_parameter_section(self.left_column,
                                                  "⚡ PERFORMANCE & LOGGING",
                                                  ['log', 'use_numba', 'jitted', 'seed'])

        # Logging
        self.create_parameter_widget(section, 'log', 'Portfolio Logging', 'bool',
                                    description="Detailliertes Logging (Debug vs Performance)")

        # Numba
        self.create_parameter_widget(section, 'use_numba', 'Numba JIT', 'bool',
                                    description="Numba JIT-Kompilierung (10x+ Performance)")

        # Jitted Override
        self.create_jitted_widget(section)

        # Random Seed
        self.create_parameter_widget(section, 'seed', 'Random Seed', 'string',
                                    description="Seed für Reproduzierbarkeit (leer = zufällig)")

    def create_fees_section_right(self):
        """Fees & Slippage Sektion (Rechte Spalte)"""
        section = UIUtils.create_parameter_section(self.right_column,
                                                  "💸 FEES & SLIPPAGE",
                                                  ['fixed_fees', 'slippage'])

        # Fixed Fees (Futures-Standard)
        self.create_parameter_widget(section, 'fixed_fees', 'Fixed Fees ($)', 'float',
                                    description="Feste Gebühren pro Trade (NQ Standard: $4.20 Round-Turn)")

        # Slippage
        self.create_parameter_widget(section, 'slippage', 'Slippage (Ticks)', 'float',
                                    description="Slippage in Ticks (NQ Standard: 1-2 Ticks)")

    def create_session_trading_section_right(self):
        """Session Trading Sektion (Rechte Spalte)"""
        section = UIUtils.create_parameter_section(self.right_column,
                                                  "🌍 SESSION TRADING",
                                                  ['session_enabled', 'session_combinations'])

        # Session Trading aktivieren
        self.create_session_enabled_widget(section)

        # Multi-Session Kombination
        self.create_multi_session_widget(section)

        # Finale Zeit-Anzeige
        self.create_final_time_display(section)

        # Custom Time Widget
        self.create_custom_time_widget(section)

    def create_session_enabled_widget(self, parent):
        """Session Trading Ein/Aus"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        # Checkbox
        self.session_enabled_var = tk.BooleanVar(value=False)
        checkbox = ttk.Checkbutton(frame, text="Session Trading aktivieren",
                                  variable=self.session_enabled_var,
                                  command=self.on_session_enabled_changed)
        checkbox.pack(anchor=tk.W)

        # Info Label
        self.session_info_var = tk.StringVar(value="Alle Zeiten (24/7 Trading)")
        info_label = ttk.Label(frame, textvariable=self.session_info_var,
                              font=('TkDefaultFont', 8), foreground='blue')
        info_label.pack(anchor=tk.W, pady=(2, 0))

    def create_multi_session_widget(self, parent):
        """Multi-Session Kombination Widget mit Checkboxen"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=10)

        # Label
        label = ttk.Label(frame, text="Session Kombinationen:", font=('TkDefaultFont', 9, 'bold'))
        label.pack(anchor=tk.W)

        # Info
        info_label = ttk.Label(frame, text="Wähle Sessions (mehrere möglich):",
                              font=('TkDefaultFont', 8), foreground='gray')
        info_label.pack(anchor=tk.W, pady=(0, 5))

        # 2-Spalten Layout für Sessions
        sessions_columns_frame = ttk.Frame(frame)
        sessions_columns_frame.pack(fill=tk.X, pady=5)

        # Linke Spalte (Asia + New York)
        left_sessions_frame = ttk.Frame(sessions_columns_frame)
        left_sessions_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Rechte Spalte (London + Custom)
        right_sessions_frame = ttk.Frame(sessions_columns_frame)
        right_sessions_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Session Checkboxen erstellen
        self.session_vars = {}

        # === LINKE SPALTE ===

        # Asia Sessions (Links)
        asia_frame = ttk.LabelFrame(left_sessions_frame, text="🇦🇺 Asia Sessions", padding=5)
        asia_frame.pack(fill=tk.X, pady=(0, 5))

        self.session_vars['asia_full'] = tk.BooleanVar()
        ttk.Checkbutton(asia_frame, text="Asia Full (22:00-08:00)",
                       variable=self.session_vars['asia_full'],
                       command=self.on_session_checkbox_changed).pack(anchor=tk.W)

        self.session_vars['asia_part1'] = tk.BooleanVar()
        ttk.Checkbutton(asia_frame, text="Asia Teil 1 (22:00-03:00)",
                       variable=self.session_vars['asia_part1'],
                       command=self.on_session_checkbox_changed).pack(anchor=tk.W)

        self.session_vars['asia_part2'] = tk.BooleanVar()
        ttk.Checkbutton(asia_frame, text="Asia Teil 2 (03:00-08:00)",
                       variable=self.session_vars['asia_part2'],
                       command=self.on_session_checkbox_changed).pack(anchor=tk.W)

        # New York Sessions (Links, unter Asia)
        ny_frame = ttk.LabelFrame(left_sessions_frame, text="🇺🇸 New York Sessions", padding=5)
        ny_frame.pack(fill=tk.X, pady=(5, 0))

        self.session_vars['ny_full'] = tk.BooleanVar(value=True)  # Standard aktiviert
        ttk.Checkbutton(ny_frame, text="New York Full (13:00-21:00)",
                       variable=self.session_vars['ny_full'],
                       command=self.on_session_checkbox_changed).pack(anchor=tk.W)

        self.session_vars['ny_part1'] = tk.BooleanVar()
        ttk.Checkbutton(ny_frame, text="New York Teil 1 (13:00-17:00)",
                       variable=self.session_vars['ny_part1'],
                       command=self.on_session_checkbox_changed).pack(anchor=tk.W)

        self.session_vars['ny_part2'] = tk.BooleanVar()
        ttk.Checkbutton(ny_frame, text="New York Teil 2 (17:00-21:00)",
                       variable=self.session_vars['ny_part2'],
                       command=self.on_session_checkbox_changed).pack(anchor=tk.W)

        # === RECHTE SPALTE ===

        # London Sessions (Rechts)
        london_frame = ttk.LabelFrame(right_sessions_frame, text="🇬🇧 London Sessions", padding=5)
        london_frame.pack(fill=tk.X, pady=(0, 5))

        self.session_vars['london_full'] = tk.BooleanVar()
        ttk.Checkbutton(london_frame, text="London Full (08:00-16:00)",
                       variable=self.session_vars['london_full'],
                       command=self.on_session_checkbox_changed).pack(anchor=tk.W)

        self.session_vars['london_part1'] = tk.BooleanVar()
        ttk.Checkbutton(london_frame, text="London Teil 1 (08:00-12:00)",
                       variable=self.session_vars['london_part1'],
                       command=self.on_session_checkbox_changed).pack(anchor=tk.W)

        self.session_vars['london_part2'] = tk.BooleanVar()
        ttk.Checkbutton(london_frame, text="London Teil 2 (12:00-16:00)",
                       variable=self.session_vars['london_part2'],
                       command=self.on_session_checkbox_changed).pack(anchor=tk.W)

        # Custom Sessions (Rechts, unter London)
        self.create_custom_sessions_widget(right_sessions_frame)

    def create_custom_sessions_widget(self, parent):
        """Custom Sessions Widget (Rechte Spalte, unter London)"""
        custom_frame = ttk.LabelFrame(parent, text="🔧 Custom Sessions", padding=5)
        custom_frame.pack(fill=tk.X, pady=(5, 0))

        # Info
        info_label = ttk.Label(custom_frame, text="Eigene Sessions (HH:MM-HH:MM):",
                              font=('TkDefaultFont', 8), foreground='gray')
        info_label.pack(anchor=tk.W, pady=(0, 5))

        # Custom Session 1
        self.create_custom_session_entry(custom_frame, "Custom 1", "custom1")

        # Custom Session 2
        self.create_custom_session_entry(custom_frame, "Custom 2", "custom2")

        # Custom Session 3
        self.create_custom_session_entry(custom_frame, "Custom 3", "custom3")

    def create_custom_session_entry(self, parent, label_text, var_name):
        """Erstellt eine Custom Session Entry"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)

        # Checkbox
        checkbox_var = tk.BooleanVar()
        self.session_vars[f'{var_name}_enabled'] = checkbox_var

        checkbox = ttk.Checkbutton(frame, text=f"☐ {label_text}:",
                                  variable=checkbox_var,
                                  command=self.on_session_checkbox_changed)
        checkbox.pack(side=tk.LEFT)

        # Entry für Zeit
        time_var = tk.StringVar(value="09:30-16:00")
        self.session_vars[f'{var_name}_time'] = time_var

        entry = ttk.Entry(frame, textvariable=time_var, width=15)
        entry.pack(side=tk.LEFT, padx=(10, 0))

        # Event Binding
        time_var.trace('w', self.on_session_checkbox_changed)

    def create_final_time_display(self, parent):
        """Finale Zeit-Anzeige Widget"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=10)

        # Label
        label = ttk.Label(frame, text="📊 Finale Trading-Zeiten:", font=('TkDefaultFont', 9, 'bold'))
        label.pack(anchor=tk.W)

        # Zeit-Anzeige Frame
        time_frame = ttk.LabelFrame(frame, text="Kombinierte Sessions", padding=10)
        time_frame.pack(fill=tk.X, pady=5)

        # Finale Zeit
        self.final_time_var = tk.StringVar(value="13:00-21:00 UTC (New York Full)")
        final_label = ttk.Label(time_frame, textvariable=self.final_time_var,
                               font=('TkDefaultFont', 10, 'bold'), foreground='darkgreen')
        final_label.pack(anchor=tk.W)

        # Details
        self.time_details_var = tk.StringVar(value="Einzelne Session: 8 Stunden Trading")
        details_label = ttk.Label(time_frame, textvariable=self.time_details_var,
                                 font=('TkDefaultFont', 8), foreground='blue')
        details_label.pack(anchor=tk.W, pady=(5, 0))

        # Initial Update
        self.update_final_time_display()

    def create_session_type_widget(self, parent):
        """Session Type Auswahl"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        # Label
        label = ttk.Label(frame, text="Trading Session:", font=('TkDefaultFont', 9, 'bold'))
        label.pack(anchor=tk.W)

        # Combobox
        self.session_type_var = tk.StringVar(value="NEW_YORK")
        session_combo = ttk.Combobox(frame, textvariable=self.session_type_var,
                                   values=["ASIA", "LONDON", "NEW_YORK", "CUSTOM"],
                                   state="readonly", width=15)
        session_combo.pack(anchor=tk.W, pady=2)
        session_combo.bind('<<ComboboxSelected>>', self.on_session_type_changed)

        # Session Info
        self.session_details_var = tk.StringVar()
        details_label = ttk.Label(frame, textvariable=self.session_details_var,
                                 font=('TkDefaultFont', 8), foreground='darkgreen')
        details_label.pack(anchor=tk.W)

        # Initial Update
        self.update_session_details()

    def create_session_part_widget(self, parent):
        """Session Part Auswahl"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        # Label
        label = ttk.Label(frame, text="Session Teil:", font=('TkDefaultFont', 9, 'bold'))
        label.pack(anchor=tk.W)

        # Combobox
        self.session_part_var = tk.StringVar(value="FULL")
        part_combo = ttk.Combobox(frame, textvariable=self.session_part_var,
                                values=["FULL", "PART_1", "PART_2"],
                                state="readonly", width=15)
        part_combo.pack(anchor=tk.W, pady=2)
        part_combo.bind('<<ComboboxSelected>>', self.on_session_part_changed)

        # Part Info
        self.session_part_info_var = tk.StringVar()
        part_info_label = ttk.Label(frame, textvariable=self.session_part_info_var,
                                   font=('TkDefaultFont', 8), foreground='purple')
        part_info_label.pack(anchor=tk.W)

        # Initial Update
        self.update_session_part_info()

    def create_custom_time_widget(self, parent):
        """Custom Time Widget"""
        self.custom_frame = ttk.Frame(parent)
        self.custom_frame.pack(fill=tk.X, pady=5)

        # Label
        label = ttk.Label(self.custom_frame, text="Custom Zeiten (UTC):", font=('TkDefaultFont', 9, 'bold'))
        label.pack(anchor=tk.W)

        # Time Frame
        time_frame = ttk.Frame(self.custom_frame)
        time_frame.pack(fill=tk.X, pady=2)

        # Start Time
        ttk.Label(time_frame, text="Start:").pack(side=tk.LEFT)
        self.custom_start_var = tk.StringVar(value="09:30")
        start_entry = ttk.Entry(time_frame, textvariable=self.custom_start_var, width=8)
        start_entry.pack(side=tk.LEFT, padx=(5, 10))

        # End Time
        ttk.Label(time_frame, text="End:").pack(side=tk.LEFT)
        self.custom_end_var = tk.StringVar(value="16:00")
        end_entry = ttk.Entry(time_frame, textvariable=self.custom_end_var, width=8)
        end_entry.pack(side=tk.LEFT, padx=5)

        # Bind Events
        self.custom_start_var.trace('w', self.on_custom_time_changed)
        self.custom_end_var.trace('w', self.on_custom_time_changed)

        # Initially hidden
        self.custom_frame.pack_forget()

    def create_performance_section_right(self):
        """Performance & Logging Sektion (Rechte Spalte)"""
        section = UIUtils.create_parameter_section(self.right_column,
                                                  "⚡ PERFORMANCE & LOGGING",
                                                  ['log', 'use_numba', 'jitted', 'seed'])

        # Logging
        self.create_parameter_widget(section, 'log', 'Portfolio Logging', 'bool',
                                    description="Detailliertes Logging (Debug vs Performance)")

        # Numba
        self.create_parameter_widget(section, 'use_numba', 'Numba JIT', 'bool',
                                    description="Numba JIT-Kompilierung (10x+ Performance)")

        # Jitted Override
        self.create_jitted_widget(section)

        # Random Seed
        self.create_parameter_widget(section, 'seed', 'Random Seed', 'int',
                                    description="Seed für Reproduzierbarkeit (None = random)")

    def create_jitted_widget(self, parent):
        """Jitted Override Widget"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        # Label
        label = ttk.Label(frame, text="Jitted Override:", font=('TkDefaultFont', 9, 'bold'))
        label.pack(anchor=tk.W)

        # Combobox
        self.jitted_var = tk.StringVar(value="None")
        jitted_combo = ttk.Combobox(frame, textvariable=self.jitted_var,
                                  values=["None", "True", "False"],
                                  state="readonly", width=10)
        jitted_combo.pack(anchor=tk.W, pady=2)

        # Info
        info_label = ttk.Label(frame, text="None=Auto, True=Force, False=Disable",
                              font=('TkDefaultFont', 8), foreground='gray')
        info_label.pack(anchor=tk.W)

    def create_seed_widget(self, parent):
        """Random Seed Widget mit besserer Validierung"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        # Label
        label = ttk.Label(frame, text="Random Seed:", font=('TkDefaultFont', 9, 'bold'))
        label.pack(anchor=tk.W)

        # Entry mit Placeholder
        self.seed_var = tk.StringVar(value="")
        seed_entry = ttk.Entry(frame, textvariable=self.seed_var, width=15)
        seed_entry.pack(anchor=tk.W, pady=2)

        # Placeholder Text
        def on_focus_in(event):
            if self.seed_var.get() == "":
                seed_entry.config(foreground='black')

        def on_focus_out(event):
            if self.seed_var.get() == "":
                seed_entry.config(foreground='gray')

        seed_entry.bind("<FocusIn>", on_focus_in)
        seed_entry.bind("<FocusOut>", on_focus_out)

        # Info
        info_label = ttk.Label(frame, text="Leer = zufällig, Zahl = reproduzierbar (z.B. 42)",
                              font=('TkDefaultFont', 8), foreground='gray')
        info_label.pack(anchor=tk.W)

        # Parameter Widget registrieren
        if not hasattr(self, 'parameter_widgets'):
            self.parameter_widgets = {}

        self.parameter_widgets['seed'] = {
            'var': self.seed_var,
            'widget': seed_entry,
            'type': 'seed'
        }

    def create_portfolio_basics_section(self):
        """Portfolio Grundlagen Sektion"""
        section = UIUtils.create_parameter_section(self.main_frame, 
                                                  "💰 PORTFOLIO GRUNDLAGEN", 
                                                  ['init_cash', 'cash_sharing'])
        
        # Initial Cash
        self.create_parameter_widget(section, 'init_cash', 'Initial Cash ($)', 'float',
                                    description="Startkapital für das Portfolio")
        
        # Cash Sharing
        self.create_parameter_widget(section, 'cash_sharing', 'Cash Sharing', 'bool',
                                    description="Cash-Sharing zwischen Assets aktivieren")

        # Logging
        self.create_parameter_widget(section, 'log', 'Portfolio Logging', 'bool',
                                    description="Detailliertes Portfolio-Logging aktivieren")

        # Numba Optimierung
        self.create_parameter_widget(section, 'use_numba', 'Numba Optimierung', 'bool',
                                    description="Numba JIT-Kompilierung für Performance aktivieren")
    
    def create_position_management_section(self):
        """Position Management Sektion - Futures optimiert"""
        section = UIUtils.create_parameter_section(self.main_frame,
                                                  "📊 POSITION MANAGEMENT",
                                                  ['size', 'size_type', 'direction', 'accumulate'])

        # === POSITION SIZE KONFIGURATION ===
        size_frame = UIUtils.create_labeled_frame(section, "📈 POSITION SIZE")
        size_frame.pack(fill=tk.X, pady=5)

        # Position Size Modus
        size_mode_frame = ttk.Frame(size_frame)
        size_mode_frame.pack(fill=tk.X, pady=2)

        ttk.Label(size_mode_frame, text="Position Size Modus:", width=20).pack(side=tk.LEFT)
        self.size_mode_var = tk.StringVar(value="contracts")
        size_mode_combo = ttk.Combobox(size_mode_frame, textvariable=self.size_mode_var,
                                      values=["contracts", "money"],
                                      state="readonly", width=15)
        size_mode_combo.pack(side=tk.LEFT, padx=5)
        size_mode_combo.bind('<<ComboboxSelected>>', self.on_size_mode_changed)

        # Position Size Wert
        size_value_frame = ttk.Frame(size_frame)
        size_value_frame.pack(fill=tk.X, pady=2)

        self.size_label = ttk.Label(size_value_frame, text="Position Size:", width=20)
        self.size_label.pack(side=tk.LEFT)
        self.size_value_var = tk.StringVar(value="1")
        self.size_entry = ttk.Entry(size_value_frame, textvariable=self.size_value_var, width=15)
        self.size_entry.pack(side=tk.LEFT, padx=5)
        self.size_entry.bind('<FocusOut>', self.on_size_value_changed)

        self.size_desc_label = ttk.Label(size_value_frame, text="(1 Kontrakt)",
                                        font=('TkDefaultFont', 8), foreground='gray')
        self.size_desc_label.pack(side=tk.LEFT, padx=10)

        # === TRADING DIRECTION ===
        direction_frame = UIUtils.create_labeled_frame(section, "🔄 TRADING DIRECTION")
        direction_frame.pack(fill=tk.X, pady=5)

        # Direction
        self.create_parameter_widget(direction_frame, 'direction', 'Trading Direction', 'enum',
                                    choices=CONFIG.ENUM_CHOICES['direction'],
                                    description="Handelsrichtung (Long/Short/Both)")

        # Accumulate
        self.create_parameter_widget(direction_frame, 'accumulate', 'Accumulation', 'enum',
                                    choices=CONFIG.ENUM_CHOICES['accumulate'],
                                    description="Akkumulation von Positionen erlauben")
    
    def create_stop_profit_section(self):
        """Stop Loss & Take Profit Sektion mit Tick/Punkt Support"""
        section = UIUtils.create_parameter_section(self.main_frame,
                                                  "🛑 STOP LOSS & TAKE PROFIT",
                                                  ['sl_stop', 'tp_stop', 'sl_trail', 'stop_entry_price'])

        # === STOP LOSS KONFIGURATION ===
        sl_frame = UIUtils.create_labeled_frame(section, "🔻 STOP LOSS KONFIGURATION")
        sl_frame.pack(fill=tk.X, pady=5)

        # Stop Loss Modus
        sl_mode_frame = ttk.Frame(sl_frame)
        sl_mode_frame.pack(fill=tk.X, pady=2)

        ttk.Label(sl_mode_frame, text="Stop Loss Modus:", width=20).pack(side=tk.LEFT)
        self.sl_mode_var = tk.StringVar(value="ticks")
        sl_mode_combo = ttk.Combobox(sl_mode_frame, textvariable=self.sl_mode_var,
                                    values=["ticks", "money"],
                                    state="readonly", width=15)
        sl_mode_combo.pack(side=tk.LEFT, padx=5)
        sl_mode_combo.bind('<<ComboboxSelected>>', self.on_sl_mode_changed)

        # Stop Loss Wert
        sl_value_frame = ttk.Frame(sl_frame)
        sl_value_frame.pack(fill=tk.X, pady=2)

        self.sl_label = ttk.Label(sl_value_frame, text="Stop Loss:", width=20)
        self.sl_label.pack(side=tk.LEFT)
        self.sl_value_var = tk.StringVar(value="25")
        self.sl_entry = ttk.Entry(sl_value_frame, textvariable=self.sl_value_var, width=15)
        self.sl_entry.pack(side=tk.LEFT, padx=5)
        self.sl_entry.bind('<FocusOut>', self.on_sl_value_changed)

        self.sl_desc_label = ttk.Label(sl_value_frame, text="(25 Ticks)",
                                      font=('TkDefaultFont', 8), foreground='gray')
        self.sl_desc_label.pack(side=tk.LEFT, padx=10)

        # === TAKE PROFIT KONFIGURATION ===
        tp_frame = UIUtils.create_labeled_frame(section, "🔺 TAKE PROFIT KONFIGURATION")
        tp_frame.pack(fill=tk.X, pady=5)

        # Take Profit Modus
        tp_mode_frame = ttk.Frame(tp_frame)
        tp_mode_frame.pack(fill=tk.X, pady=2)

        ttk.Label(tp_mode_frame, text="Take Profit Modus:", width=20).pack(side=tk.LEFT)
        self.tp_mode_var = tk.StringVar(value="ticks")
        tp_mode_combo = ttk.Combobox(tp_mode_frame, textvariable=self.tp_mode_var,
                                    values=["ticks", "money"],
                                    state="readonly", width=15)
        tp_mode_combo.pack(side=tk.LEFT, padx=5)
        tp_mode_combo.bind('<<ComboboxSelected>>', self.on_tp_mode_changed)

        # Take Profit Wert
        tp_value_frame = ttk.Frame(tp_frame)
        tp_value_frame.pack(fill=tk.X, pady=2)

        self.tp_label = ttk.Label(tp_value_frame, text="Take Profit:", width=20)
        self.tp_label.pack(side=tk.LEFT)
        self.tp_value_var = tk.StringVar(value="50")
        self.tp_entry = ttk.Entry(tp_value_frame, textvariable=self.tp_value_var, width=15)
        self.tp_entry.pack(side=tk.LEFT, padx=5)
        self.tp_entry.bind('<FocusOut>', self.on_tp_value_changed)

        self.tp_desc_label = ttk.Label(tp_value_frame, text="(50 Ticks)",
                                      font=('TkDefaultFont', 8), foreground='gray')
        self.tp_desc_label.pack(side=tk.LEFT, padx=10)

        # === TICK-GRÖSSE KONFIGURATION ===
        tick_frame = UIUtils.create_labeled_frame(section, "📏 TICK-GRÖSSE KONFIGURATION")
        tick_frame.pack(fill=tk.X, pady=5)

        # Asset Tick Size
        tick_size_frame = ttk.Frame(tick_frame)
        tick_size_frame.pack(fill=tk.X, pady=2)

        ttk.Label(tick_size_frame, text="Asset Tick-Größe:", width=20).pack(side=tk.LEFT)
        self.tick_size_var = tk.StringVar(value="0.01")
        tick_size_entry = ttk.Entry(tick_size_frame, textvariable=self.tick_size_var, width=15)
        tick_size_entry.pack(side=tk.LEFT, padx=5)
        tick_size_entry.bind('<FocusOut>', self.on_tick_size_changed)

        # Preset Buttons
        preset_frame = ttk.Frame(tick_frame)
        preset_frame.pack(fill=tk.X, pady=2)

        ttk.Label(preset_frame, text="Presets:", width=20).pack(side=tk.LEFT)
        ttk.Button(preset_frame, text="Crypto (0.01)", command=lambda: self.set_tick_preset(0.01), width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="ES (0.25)", command=lambda: self.set_tick_preset(0.25), width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="NQ (0.25)", command=lambda: self.set_tick_preset(0.25), width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Forex (0.0001)", command=lambda: self.set_tick_preset(0.0001), width=12).pack(side=tk.LEFT, padx=2)

        # === ERWEITERTE OPTIONEN ===
        advanced_frame = UIUtils.create_labeled_frame(section, "⚙️ ERWEITERTE STOP-OPTIONEN")
        advanced_frame.pack(fill=tk.X, pady=5)

        # Trailing Stop
        self.create_parameter_widget(advanced_frame, 'sl_trail', 'Trailing Stop', 'bool',
                                    description="Trailing Stop Loss aktivieren")

        # Stop Entry Price
        self.create_parameter_widget(advanced_frame, 'stop_entry_price', 'Stop Entry Price', 'enum',
                                    choices=CONFIG.ENUM_CHOICES['stop_entry_price'],
                                    description="Referenzpreis für Stop-Berechnung")

        # Risk-Reward Anzeige
        rr_frame = ttk.Frame(advanced_frame)
        rr_frame.pack(fill=tk.X, pady=5)

        self.risk_reward_label = ttk.Label(rr_frame, text="Risk-Reward Ratio: 2.0:1",
                                          font=('TkDefaultFont', 10, 'bold'), foreground='green')
        self.risk_reward_label.pack(anchor=tk.W)

        # Initial Risk-Reward berechnen
        self.update_risk_reward_display()
    
    def create_fees_section(self):
        """Fees & Slippage Sektion"""
        section = UIUtils.create_parameter_section(self.main_frame,
                                                  "💸 FEES & SLIPPAGE",
                                                  ['fees', 'fixed_fees', 'slippage'])
        
        # Trading Fees
        self.create_parameter_widget(section, 'fees', 'Trading Fees (%)', 'float',
                                    description="Trading-Gebühren als Dezimalzahl (0.001 = 0.1%)")
        
        # Fixed Fees
        self.create_parameter_widget(section, 'fixed_fees', 'Fixed Fees ($)', 'float',
                                    description="Fixe Gebühren pro Trade in Dollar")
        
        # Slippage
        self.create_parameter_widget(section, 'slippage', 'Slippage (%)', 'float',
                                    description="Slippage als Dezimalzahl (0.001 = 0.1%)")
    
    def create_parameter_widget(self, parent, param_name: str, display_name: str, param_type: str,
                               choices: List = None, description: str = ""):
        """Erstellt Parameter-Widget"""
        
        # Container Frame
        param_frame = ttk.Frame(parent)
        param_frame.pack(fill=tk.X, pady=5)
        
        # Parameter-Wert aus State holen
        current_value = get_vbt_parameter(param_name)
        
        # Widget erstellen
        label, widget, var = UIUtils.create_parameter_entry(
            param_frame, display_name, current_value, param_type, choices
        )
        
        # Layout
        label.pack(side=tk.LEFT, padx=(0, 10))
        widget.pack(side=tk.LEFT, padx=(0, 10))
        
        # Description Label
        if description:
            desc_label = ttk.Label(param_frame, text=f"({description})", 
                                  font=('TkDefaultFont', 8), foreground='gray')
            desc_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Validation Label
        validation_label = ttk.Label(param_frame, text="", foreground='red', 
                                    font=('TkDefaultFont', 8))
        validation_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Event Binding für Änderungen
        if param_type == 'bool':
            var.trace_add('write', lambda *args, p=param_name, v=var, vl=validation_label: 
                         self.on_parameter_changed(p, v, vl))
        else:
            widget.bind('<FocusOut>', lambda event, p=param_name, v=var, vl=validation_label: 
                       self.on_parameter_changed(p, v, vl))
            widget.bind('<Return>', lambda event, p=param_name, v=var, vl=validation_label: 
                       self.on_parameter_changed(p, v, vl))
        
        # Widgets speichern
        self.parameter_widgets[param_name] = {
            'widget': widget,
            'var': var,
            'validation_label': validation_label,
            'type': param_type
        }
        self.parameter_vars[param_name] = var
    
    def create_action_buttons(self):
        """Aktions-Buttons erstellen"""
        action_frame = ttk.Frame(self.main_frame)
        action_frame.pack(fill=tk.X, pady=20)
        
        # Separator
        separator = ttk.Separator(action_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 10))
        
        # Button Frame
        button_frame = ttk.Frame(action_frame)
        button_frame.pack()
        
        # Buttons
        ttk.Button(button_frame, text="🔄 Parameter validieren", 
                  command=self.validate_all_parameters, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="↩️ Defaults laden", 
                  command=self.load_defaults, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="💾 Parameter speichern", 
                  command=self.save_parameters, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📂 Parameter laden", 
                  command=self.load_parameters, width=20).pack(side=tk.LEFT, padx=5)
    
    def bind_mousewheel(self):
        """Mouse Wheel Binding für Scrolling"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def setup_events(self):
        """Event-Handler registrieren"""
        def on_parameter_changed(data):
            param_name = data.get('parameter', '')
            if param_name in self.parameter_widgets:
                # UI könnte hier aktualisiert werden
                pass

        def on_parameter_reset(data):
            self.load_parameters_from_state()

        # Event-Listener registrieren
        on(Events.PARAMETER_CHANGED, on_parameter_changed)
        on(Events.PARAMETER_RESET, on_parameter_reset)
    
    def on_parameter_changed(self, param_name: str, var: tk.Variable, validation_label: ttk.Label):
        """Parameter-Änderung behandeln"""
        try:
            # Wert aus Variable holen
            raw_value = var.get()
            
            # Wert konvertieren
            converted_value = VBTUtils.convert_parameter_value(param_name, raw_value)
            
            # Validierung
            is_valid, error_msg = VBTUtils.validate_vbt_parameter(param_name, converted_value)
            
            if is_valid:
                # Parameter in State speichern
                set_vbt_parameter(param_name, converted_value)
                validation_label.config(text="✅", foreground='green')
                
                # Event auslösen
                emit(Events.PARAMETER_CHANGED, {
                    'parameter': param_name,
                    'value': converted_value
                }, 'Tab2Essential')
                
            else:
                validation_label.config(text=f"❌ {error_msg}", foreground='red')
                
        except Exception as e:
            self.logger.error(f"Parameter-Änderung Fehler ({param_name}): {e}")
            validation_label.config(text=f"❌ Fehler: {str(e)}", foreground='red')
    
    def validate_all_parameters(self):
        """Alle Parameter validieren"""
        errors = []
        warnings = []
        
        for param_name, widget_info in self.parameter_widgets.items():
            var = widget_info['var']
            validation_label = widget_info['validation_label']
            
            try:
                raw_value = var.get()
                converted_value = VBTUtils.convert_parameter_value(param_name, raw_value)
                is_valid, error_msg = VBTUtils.validate_vbt_parameter(param_name, converted_value)
                
                if is_valid:
                    validation_label.config(text="✅", foreground='green')
                else:
                    validation_label.config(text=f"❌ {error_msg}", foreground='red')
                    errors.append(f"{param_name}: {error_msg}")
                    
            except Exception as e:
                error_msg = f"Validierungsfehler: {str(e)}"
                validation_label.config(text=f"❌ {error_msg}", foreground='red')
                errors.append(f"{param_name}: {error_msg}")
        
        # Spezielle Validierungen
        sl_stop = get_vbt_parameter('sl_stop')
        tp_stop = get_vbt_parameter('tp_stop')
        
        if sl_stop and tp_stop:
            if tp_stop <= sl_stop:
                warnings.append("Take Profit sollte größer als Stop Loss sein")
            
            risk_reward = tp_stop / sl_stop if sl_stop > 0 else 0
            if risk_reward < 1.5:
                warnings.append(f"Risk-Reward Ratio ist niedrig: {risk_reward:.2f}:1")
        
        # Ergebnis anzeigen
        if errors:
            error_msg = "Validierungsfehler gefunden:\n\n" + "\n".join(errors)
            if warnings:
                error_msg += "\n\nWarnungen:\n" + "\n".join(warnings)
            UIUtils.show_error("Validierungsfehler", error_msg)
            emit(Events.VALIDATION_FAILED, {'errors': errors, 'warnings': warnings})
        else:
            success_msg = "✅ Alle Parameter sind gültig!"
            if warnings:
                success_msg += "\n\nWarnungen:\n" + "\n".join(warnings)
            UIUtils.show_info("Validierung erfolgreich", success_msg)
            emit(Events.VALIDATION_PASSED, {'warnings': warnings})
    
    def load_defaults(self):
        """Default-Parameter laden"""
        if UIUtils.ask_yes_no("Defaults laden", 
                             "Möchten Sie alle Parameter auf die Standardwerte zurücksetzen?"):
            
            # Defaults in State laden
            for param_name, default_value in CONFIG.VBT_DEFAULTS.items():
                set_vbt_parameter(param_name, default_value)
            
            # UI aktualisieren
            self.load_parameters_from_state()
            
            emit(Events.PARAMETER_RESET, None, 'Tab2Essential')
            UIUtils.show_info("Defaults geladen", "Parameter wurden auf Standardwerte zurückgesetzt")
    
    def save_parameters(self):
        """Parameter in Datei speichern"""
        file_path = UIUtils.save_file(
            "VBT Parameter speichern",
            [('JSON Dateien', '*.json'), ('Alle Dateien', '*.*')],
            str(CONFIG.PATHS['punkt4_configs']),
            '.json'
        )
        
        if file_path:
            try:
                import json
                parameters = get_all_vbt_parameters()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(parameters, f, indent=2, ensure_ascii=False, default=str)
                
                UIUtils.show_info("Parameter gespeichert", f"Parameter wurden gespeichert:\n{file_path}")
                
            except Exception as e:
                self.logger.error(f"Parameter-Speichern Fehler: {e}")
                UIUtils.show_error("Speichern Fehler", str(e))
    
    def load_parameters(self):
        """Parameter aus Datei laden"""
        file_path = UIUtils.select_file(
            "VBT Parameter laden",
            [('JSON Dateien', '*.json'), ('Alle Dateien', '*.*')],
            str(CONFIG.PATHS['punkt4_configs'])
        )
        
        if file_path:
            try:
                import json
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    parameters = json.load(f)
                
                # Parameter in State laden
                for param_name, value in parameters.items():
                    if param_name in CONFIG.VBT_DEFAULTS:
                        set_vbt_parameter(param_name, value)
                
                # UI aktualisieren
                self.load_parameters_from_state()
                
                UIUtils.show_info("Parameter geladen", f"Parameter wurden geladen:\n{file_path}")
                
            except Exception as e:
                self.logger.error(f"Parameter-Laden Fehler: {e}")
                UIUtils.show_error("Laden Fehler", str(e))
    
    def load_parameters_from_state(self):
        """Parameter aus State in UI laden"""
        for param_name, widget_info in self.parameter_widgets.items():
            try:
                current_value = get_vbt_parameter(param_name)
                var = widget_info['var']
                param_type = widget_info['type']
                
                # Wert in Variable setzen
                if param_type == 'bool':
                    var.set(bool(current_value) if current_value is not None else False)
                elif param_type == 'enum':
                    var.set(str(current_value) if current_value is not None else "")
                else:
                    if current_value == np.inf:
                        var.set("inf")
                    else:
                        var.set(str(current_value) if current_value is not None else "")
                
                # Validation zurücksetzen
                widget_info['validation_label'].config(text="", foreground='black')
                
            except Exception as e:
                self.logger.error(f"Parameter-Laden Fehler ({param_name}): {e}")

    # === FUTURES-OPTIMIERTE EVENT HANDLER ===

    def on_size_mode_changed(self, event=None):
        """Position Size Modus geändert"""
        mode = self.size_mode_var.get()
        value = self.size_value_var.get()

        if mode == "contracts":
            self.size_label.config(text="Position Size:")
            self.size_desc_label.config(text=f"({value} Kontrakt{'e' if value != '1' else ''})")
            # VBT Parameter: amount
            set_vbt_parameter('size_type', 'amount')
        elif mode == "money":
            self.size_label.config(text="Position Size:")
            self.size_desc_label.config(text=f"(${value})")
            # VBT Parameter: value
            set_vbt_parameter('size_type', 'value')

        # Size-Wert aktualisieren
        self.on_size_value_changed()

    def on_size_value_changed(self, event=None):
        """Position Size Wert geändert"""
        try:
            mode = self.size_mode_var.get()
            value = self.size_value_var.get()

            if mode == "contracts":
                self.size_desc_label.config(text=f"({value} Kontrakt{'e' if value != '1' else ''})")
                # VBT: Anzahl Kontrakte
                set_vbt_parameter('size', float(value))
            elif mode == "money":
                self.size_desc_label.config(text=f"(${value})")
                # VBT: Geldwert
                set_vbt_parameter('size', float(value))

            self.update_risk_reward_display()

        except ValueError:
            self.size_desc_label.config(text="(Ungültiger Wert)")

    def on_sl_mode_changed(self, event=None):
        """Stop Loss Modus geändert"""
        mode = self.sl_mode_var.get()
        value = self.sl_value_var.get()

        if mode == "ticks":
            self.sl_label.config(text="Stop Loss:")
            self.sl_desc_label.config(text=f"({value} Ticks)")
        elif mode == "money":
            self.sl_label.config(text="Stop Loss:")
            self.sl_desc_label.config(text=f"(${value})")

        self.on_sl_value_changed()

    def on_sl_value_changed(self, event=None):
        """Stop Loss Wert geändert"""
        try:
            mode = self.sl_mode_var.get()
            value = self.sl_value_var.get()

            if mode == "ticks":
                self.sl_desc_label.config(text=f"({value} Ticks)")
                # Ticks als absolute Zahl speichern (VBT kann das verarbeiten)
                set_vbt_parameter('sl_stop', float(value))
            elif mode == "money":
                self.sl_desc_label.config(text=f"(${value})")
                # VBT: Absoluter Geldwert
                set_vbt_parameter('sl_stop', float(value))

            self.update_risk_reward_display()

        except ValueError:
            self.sl_desc_label.config(text="(Ungültiger Wert)")

    def on_tp_mode_changed(self, event=None):
        """Take Profit Modus geändert"""
        mode = self.tp_mode_var.get()
        value = self.tp_value_var.get()

        if mode == "ticks":
            self.tp_label.config(text="Take Profit:")
            self.tp_desc_label.config(text=f"({value} Ticks)")
        elif mode == "money":
            self.tp_label.config(text="Take Profit:")
            self.tp_desc_label.config(text=f"(${value})")

        self.on_tp_value_changed()

    def on_tp_value_changed(self, event=None):
        """Take Profit Wert geändert"""
        try:
            mode = self.tp_mode_var.get()
            value = self.tp_value_var.get()

            if mode == "ticks":
                self.tp_desc_label.config(text=f"({value} Ticks)")
                # Ticks als absolute Zahl speichern (VBT kann das verarbeiten)
                set_vbt_parameter('tp_stop', float(value))
            elif mode == "money":
                self.tp_desc_label.config(text=f"(${value})")
                # VBT: Absoluter Geldwert
                set_vbt_parameter('tp_stop', float(value))

            self.update_risk_reward_display()

        except ValueError:
            self.tp_desc_label.config(text="(Ungültiger Wert)")

    def update_risk_reward_display(self):
        """Risk-Reward Ratio aktualisieren"""
        try:
            sl_value = float(self.sl_value_var.get())
            tp_value = float(self.tp_value_var.get())

            if sl_value > 0:
                ratio = tp_value / sl_value
                self.risk_reward_label.config(text=f"Risk-Reward Ratio: {ratio:.1f}:1")

                # Farbe basierend auf Ratio
                if ratio >= 2.0:
                    self.risk_reward_label.config(foreground='green')
                elif ratio >= 1.5:
                    self.risk_reward_label.config(foreground='orange')
                else:
                    self.risk_reward_label.config(foreground='red')
            else:
                self.risk_reward_label.config(text="Risk-Reward Ratio: -", foreground='black')

        except (ValueError, ZeroDivisionError):
            self.risk_reward_label.config(text="Risk-Reward Ratio: Ungültig", foreground='red')

    def on_tick_size_changed(self, event=None):
        """Tick-Größe geändert"""
        try:
            tick_size = float(self.tick_size_var.get())
            # Tick-Größe für Berechnungen speichern
            # TODO: Implementiere Tick-zu-Preis Konvertierung
            pass
        except ValueError:
            pass

    def set_tick_preset(self, tick_size):
        """Tick-Größe Preset setzen"""
        self.tick_size_var.set(str(tick_size))
