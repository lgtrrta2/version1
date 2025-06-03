#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punkt3.1 Tab2 - Datenvisualisierung
Tab für die Visualisierung von VectorbtPro-Daten als Tabelle und Charts

Autor: AI Assistant
Datum: 2025-06-02
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import threading

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib nicht verfügbar. Charts sind nicht verfügbar.")

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Plotly nicht verfügbar. Interaktive Charts sind nicht verfügbar.")

class Tab2Visualisierung:
    """
    Tab 2: Datenvisualisierung
    """
    
    def __init__(self, parent, data_manager):
        self.parent = parent
        self.data_manager = data_manager
        
        self.current_data = None
        self.current_metadata = None
        self.current_file_path = None
        self.filtered_data = None
        
        self.create_widgets()
        self.setup_bindings()
        
    def create_widgets(self):
        """Erstellt die GUI-Widgets für Tab 2"""
        # Hauptframe
        self.frame = ttk.Frame(self.parent, padding="10")
        
        # Erstelle Notebook für Visualisierungs-Optionen
        self.viz_notebook = ttk.Notebook(self.frame)
        self.viz_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Sub-Tab 1: Tabellen-Ansicht
        self.create_table_tab()
        
        # Sub-Tab 2: Chart-Ansicht (falls verfügbar)
        if MATPLOTLIB_AVAILABLE or PLOTLY_AVAILABLE:
            self.create_chart_tab()
            
    def create_table_tab(self):
        """Erstellt den Tabellen-Tab"""
        table_frame = ttk.Frame(self.viz_notebook, padding="10")
        self.viz_notebook.add(table_frame, text="Tabellen-Ansicht")
        
        # Kontroll-Panel
        control_frame = ttk.LabelFrame(table_frame, text="Anzeigeoptionen", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Zeitraum-Auswahl
        timeframe_frame = ttk.Frame(control_frame)
        timeframe_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(timeframe_frame, text="Zeitraum:").pack(side=tk.LEFT)
        
        self.timeframe_var = tk.StringVar(value="Vollständig")
        timeframe_combo = ttk.Combobox(
            timeframe_frame, 
            textvariable=self.timeframe_var,
            values=["Vollständig", "1w", "2w", "3w", "4w", "8w", "12w", "Benutzerdefiniert"],
            state="readonly",
            width=15
        )
        timeframe_combo.pack(side=tk.LEFT, padx=(5, 20))
        timeframe_combo.bind('<<ComboboxSelected>>', self.on_timeframe_changed)
        
        # Benutzerdefinierte Datumsauswahl (initial versteckt)
        self.custom_date_frame = ttk.Frame(timeframe_frame)
        
        ttk.Label(self.custom_date_frame, text="Von:").pack(side=tk.LEFT, padx=(20, 5))
        self.start_date_var = tk.StringVar()
        start_date_entry = ttk.Entry(self.custom_date_frame, textvariable=self.start_date_var, width=12)
        start_date_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(self.custom_date_frame, text="Bis:").pack(side=tk.LEFT, padx=(0, 5))
        self.end_date_var = tk.StringVar()
        end_date_entry = ttk.Entry(self.custom_date_frame, textvariable=self.end_date_var, width=12)
        end_date_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(self.custom_date_frame, text="Anwenden", command=self.apply_custom_timeframe).pack(side=tk.LEFT)
        
        # Datenauswahl (für Multi-Timeframe oder Dictionary-Daten)
        data_selection_frame = ttk.Frame(control_frame)
        data_selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(data_selection_frame, text="Datenquelle:").pack(side=tk.LEFT)
        
        self.data_source_var = tk.StringVar()
        self.data_source_combo = ttk.Combobox(
            data_selection_frame,
            textvariable=self.data_source_var,
            state="readonly",
            width=20
        )
        self.data_source_combo.pack(side=tk.LEFT, padx=(5, 20))
        self.data_source_combo.bind('<<ComboboxSelected>>', self.on_data_source_changed)
        
        # Spaltenauswahl
        column_frame = ttk.Frame(control_frame)
        column_frame.pack(fill=tk.X)
        
        ttk.Label(column_frame, text="Spalten:").pack(side=tk.LEFT)
        
        self.show_all_columns_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(column_frame, text="Alle anzeigen", variable=self.show_all_columns_var, command=self.on_column_selection_changed).pack(side=tk.LEFT, padx=(5, 20))
        
        # Aktualisieren Button
        ttk.Button(control_frame, text="Tabelle aktualisieren", command=self.update_table).pack(anchor=tk.E, pady=(10, 0))
        
        # Tabellen-Frame
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Treeview für Tabellendaten
        self.table_tree = ttk.Treeview(table_container, show='headings')
        
        # Scrollbars
        v_scrollbar_table = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.table_tree.yview)
        h_scrollbar_table = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.table_tree.xview)
        self.table_tree.configure(yscrollcommand=v_scrollbar_table.set, xscrollcommand=h_scrollbar_table.set)
        
        # Grid Layout
        self.table_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar_table.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar_table.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)
        
        # Status-Label
        self.table_status_var = tk.StringVar(value="Keine Daten geladen")
        ttk.Label(table_frame, textvariable=self.table_status_var).pack(pady=(10, 0))
        
    def create_chart_tab(self):
        """Erstellt den Chart-Tab"""
        chart_frame = ttk.Frame(self.viz_notebook, padding="10")
        self.viz_notebook.add(chart_frame, text="Chart-Ansicht")
        
        # Chart-Kontroll-Panel
        chart_control_frame = ttk.LabelFrame(chart_frame, text="Chart-Optionen", padding="10")
        chart_control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Chart-Typ Auswahl
        chart_type_frame = ttk.Frame(chart_control_frame)
        chart_type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(chart_type_frame, text="Chart-Typ:").pack(side=tk.LEFT)
        
        self.chart_type_var = tk.StringVar(value="Linie")
        chart_type_combo = ttk.Combobox(
            chart_type_frame,
            textvariable=self.chart_type_var,
            values=["Linie", "Candlestick", "OHLC", "Volumen", "Scatter"],
            state="readonly",
            width=15
        )
        chart_type_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        # Y-Achse Spaltenauswahl
        ttk.Label(chart_type_frame, text="Y-Achse:").pack(side=tk.LEFT)
        
        self.y_column_var = tk.StringVar()
        self.y_column_combo = ttk.Combobox(
            chart_type_frame,
            textvariable=self.y_column_var,
            state="readonly",
            width=15
        )
        self.y_column_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        # Chart erstellen Button
        ttk.Button(chart_control_frame, text="Chart erstellen", command=self.create_chart).pack(anchor=tk.E)
        
        # Chart-Container
        self.chart_container = ttk.Frame(chart_frame)
        self.chart_container.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder für Chart
        self.chart_placeholder = ttk.Label(
            self.chart_container,
            text="Keine Chart-Daten verfügbar.\n\nLaden Sie Daten und wählen Sie Chart-Optionen.",
            font=('Arial', 12),
            foreground='gray'
        )
        self.chart_placeholder.pack(expand=True)
        
    def setup_bindings(self):
        """Setzt Event-Bindings auf"""
        pass
        
    def update_data(self, data, metadata: Dict[str, Any], file_path: str):
        """Aktualisiert die Daten für die Visualisierung"""
        self.current_data = data
        self.current_metadata = metadata
        self.current_file_path = file_path
        
        # Datenquellen aktualisieren
        self.update_data_sources()
        
        # Standardmäßig erste verfügbare Datenquelle auswählen
        if self.data_source_combo['values']:
            self.data_source_var.set(self.data_source_combo['values'][0])
            self.on_data_source_changed()
            
    def update_data_sources(self):
        """Aktualisiert die verfügbaren Datenquellen"""
        sources = []
        
        if isinstance(self.current_data, dict):
            # Dictionary mit mehreren Datenquellen
            for key, value in self.current_data.items():
                if isinstance(value, pd.DataFrame) and not value.empty:
                    sources.append(key)
        elif isinstance(self.current_data, pd.DataFrame):
            # Einzelner DataFrame
            sources.append("Hauptdaten")
        elif hasattr(self.current_data, 'close'):  # VBT Data Objekt
            sources.append("OHLCV Daten")
            if hasattr(self.current_data, 'volume'):
                sources.append("Volumen")
                
        self.data_source_combo['values'] = sources
        
    def on_data_source_changed(self, event=None):
        """Callback für Datenquellen-Änderung"""
        selected_source = self.data_source_var.get()
        if not selected_source:
            return
            
        # Aktuelle Daten basierend auf Auswahl setzen
        if isinstance(self.current_data, dict):
            if selected_source in self.current_data:
                self.filtered_data = self.current_data[selected_source]
        elif isinstance(self.current_data, pd.DataFrame):
            self.filtered_data = self.current_data
        elif hasattr(self.current_data, 'close'):  # VBT Data
            if selected_source == "OHLCV Daten":
                # OHLCV DataFrame erstellen
                ohlcv_data = pd.DataFrame({
                    'Open': self.current_data.open.iloc[:, 0] if hasattr(self.current_data, 'open') else None,
                    'High': self.current_data.high.iloc[:, 0] if hasattr(self.current_data, 'high') else None,
                    'Low': self.current_data.low.iloc[:, 0] if hasattr(self.current_data, 'low') else None,
                    'Close': self.current_data.close.iloc[:, 0],
                })
                if hasattr(self.current_data, 'volume'):
                    ohlcv_data['Volume'] = self.current_data.volume.iloc[:, 0]
                self.filtered_data = ohlcv_data
            elif selected_source == "Volumen" and hasattr(self.current_data, 'volume'):
                self.filtered_data = self.current_data.volume
                
        # Spalten für Chart-Auswahl aktualisieren
        self.update_chart_columns()
        
        # Tabelle aktualisieren
        self.update_table()
        
    def update_chart_columns(self):
        """Aktualisiert die verfügbaren Spalten für Charts"""
        if self.filtered_data is not None and isinstance(self.filtered_data, pd.DataFrame):
            numeric_columns = self.filtered_data.select_dtypes(include=[np.number]).columns.tolist()
            self.y_column_combo['values'] = numeric_columns
            if numeric_columns:
                self.y_column_var.set(numeric_columns[0])
                
    def on_timeframe_changed(self, event=None):
        """Callback für Zeitrahmen-Änderung"""
        timeframe = self.timeframe_var.get()
        
        if timeframe == "Benutzerdefiniert":
            self.custom_date_frame.pack(side=tk.LEFT, padx=(20, 0))
            # Standardwerte setzen
            if self.filtered_data is not None and isinstance(self.filtered_data, pd.DataFrame) and not self.filtered_data.empty:
                self.start_date_var.set(str(self.filtered_data.index[0].date()))
                self.end_date_var.set(str(self.filtered_data.index[-1].date()))
        else:
            self.custom_date_frame.pack_forget()
            self.apply_timeframe_filter()
            
    def apply_timeframe_filter(self):
        """Wendet Zeitrahmen-Filter an"""
        if self.filtered_data is None or not isinstance(self.filtered_data, pd.DataFrame):
            return
            
        timeframe = self.timeframe_var.get()
        
        if timeframe == "Vollständig":
            # Keine Filterung
            self.update_table()
            return
            
        # Zeitrahmen in Tage umrechnen
        timeframe_days = {
            "1w": 7,
            "2w": 14,
            "3w": 21,
            "4w": 28,
            "8w": 56,
            "12w": 84
        }
        
        if timeframe in timeframe_days:
            days = timeframe_days[timeframe]
            end_date = self.filtered_data.index[-1]
            start_date = end_date - timedelta(days=days)
            
            # Filter anwenden
            mask = (self.filtered_data.index >= start_date) & (self.filtered_data.index <= end_date)
            filtered_df = self.filtered_data.loc[mask]
            
            self.update_table(filtered_df)
            
    def apply_custom_timeframe(self):
        """Wendet benutzerdefinierten Zeitrahmen an"""
        if self.filtered_data is None:
            return
            
        try:
            start_date = pd.to_datetime(self.start_date_var.get())
            end_date = pd.to_datetime(self.end_date_var.get())
            
            if start_date >= end_date:
                messagebox.showerror("Fehler", "Startdatum muss vor Enddatum liegen.")
                return
                
            # Filter anwenden
            mask = (self.filtered_data.index >= start_date) & (self.filtered_data.index <= end_date)
            filtered_df = self.filtered_data.loc[mask]
            
            self.update_table(filtered_df)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Ungültiges Datumsformat:\n{str(e)}")
            
    def on_column_selection_changed(self):
        """Callback für Spaltenauswahl-Änderung"""
        self.update_table()
        
    def update_table(self, data_to_show=None):
        """Aktualisiert die Tabellen-Anzeige"""
        if data_to_show is None:
            data_to_show = self.filtered_data
            
        if data_to_show is None or data_to_show.empty:
            self.table_status_var.set("Keine Daten verfügbar")
            return
            
        try:
            # Treeview leeren
            for item in self.table_tree.get_children():
                self.table_tree.delete(item)
                
            # Spalten konfigurieren
            if self.show_all_columns_var.get():
                columns_to_show = data_to_show.columns.tolist()
            else:
                # Nur wichtige Spalten anzeigen (OHLCV)
                important_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                columns_to_show = [col for col in important_cols if col in data_to_show.columns]
                if not columns_to_show:
                    columns_to_show = data_to_show.columns.tolist()[:10]  # Erste 10 Spalten
                    
            # Treeview Spalten setzen
            display_columns = ['Index'] + columns_to_show
            self.table_tree['columns'] = display_columns
            self.table_tree['show'] = 'headings'
            
            # Spalten-Header setzen
            for col in display_columns:
                self.table_tree.heading(col, text=col)
                self.table_tree.column(col, width=100, anchor=tk.E if col != 'Index' else tk.W)
                
            # Daten hinzufügen (limitiert auf 1000 Zeilen für Performance)
            max_rows = min(1000, len(data_to_show))
            
            for i, (index, row) in enumerate(data_to_show.head(max_rows).iterrows()):
                values = [str(index)]
                for col in columns_to_show:
                    value = row[col]
                    if pd.isna(value):
                        values.append("")
                    elif isinstance(value, float):
                        values.append(f"{value:.4f}")
                    else:
                        values.append(str(value))
                        
                self.table_tree.insert('', tk.END, values=values)
                
            # Status aktualisieren
            total_rows = len(data_to_show)
            shown_rows = min(max_rows, total_rows)
            
            status_text = f"{shown_rows} von {total_rows} Zeilen angezeigt"
            if total_rows > max_rows:
                status_text += f" (limitiert auf {max_rows} für Performance)"
                
            self.table_status_var.set(status_text)
            
        except Exception as e:
            self.table_status_var.set(f"Fehler beim Anzeigen der Tabelle: {str(e)}")
            messagebox.showerror("Tabellen-Fehler", f"Fehler beim Anzeigen der Tabelle:\n{str(e)}")
            
    def create_chart(self):
        """Erstellt ein Chart basierend auf den ausgewählten Optionen"""
        if self.filtered_data is None or self.filtered_data.empty:
            messagebox.showwarning("Keine Daten", "Keine Daten für Chart verfügbar.")
            return
            
        chart_type = self.chart_type_var.get()
        y_column = self.y_column_var.get()
        
        if not y_column:
            messagebox.showwarning("Keine Spalte", "Bitte wählen Sie eine Spalte für die Y-Achse.")
            return
            
        try:
            # Alte Charts entfernen
            for widget in self.chart_container.winfo_children():
                widget.destroy()
                
            if MATPLOTLIB_AVAILABLE:
                self.create_matplotlib_chart(chart_type, y_column)
            else:
                # Fallback: Einfache Textanzeige
                info_text = f"Chart-Typ: {chart_type}\nY-Achse: {y_column}\nDatenpunkte: {len(self.filtered_data)}"
                ttk.Label(self.chart_container, text=info_text, font=('Arial', 12)).pack(expand=True)
                
        except Exception as e:
            messagebox.showerror("Chart-Fehler", f"Fehler beim Erstellen des Charts:\n{str(e)}")
            
    def create_matplotlib_chart(self, chart_type: str, y_column: str):
        """Erstellt ein Matplotlib-Chart"""
        # Figure erstellen
        fig = Figure(figsize=(12, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Daten für Chart vorbereiten
        data_for_chart = self.filtered_data.copy()
        
        # Zeitrahmen-Filter anwenden falls nötig
        timeframe = self.timeframe_var.get()
        if timeframe != "Vollständig":
            self.apply_timeframe_filter()
            
        # Chart basierend auf Typ erstellen
        if chart_type == "Linie":
            ax.plot(data_for_chart.index, data_for_chart[y_column], linewidth=1)
            ax.set_ylabel(y_column)
            
        elif chart_type == "Candlestick" and all(col in data_for_chart.columns for col in ['Open', 'High', 'Low', 'Close']):
            # Vereinfachter Candlestick (als OHLC Bars)
            for i, (index, row) in enumerate(data_for_chart.iterrows()):
                open_price = row['Open']
                high_price = row['High']
                low_price = row['Low']
                close_price = row['Close']
                
                color = 'green' if close_price >= open_price else 'red'
                
                # High-Low Linie
                ax.plot([i, i], [low_price, high_price], color='black', linewidth=0.5)
                
                # Open-Close Box
                height = abs(close_price - open_price)
                bottom = min(open_price, close_price)
                ax.bar(i, height, bottom=bottom, color=color, alpha=0.7, width=0.8)
                
            ax.set_ylabel('Preis')
            
        elif chart_type == "Volumen" and 'Volume' in data_for_chart.columns:
            ax.bar(range(len(data_for_chart)), data_for_chart['Volume'], alpha=0.7)
            ax.set_ylabel('Volumen')
            
        elif chart_type == "Scatter":
            ax.scatter(range(len(data_for_chart)), data_for_chart[y_column], alpha=0.6, s=1)
            ax.set_ylabel(y_column)
            
        else:
            # Fallback: Linie
            ax.plot(data_for_chart.index, data_for_chart[y_column])
            ax.set_ylabel(y_column)
            
        # Chart-Styling
        ax.set_title(f"{chart_type} - {y_column}")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        
        # Chart in Tkinter einbetten
        canvas = FigureCanvasTkAgg(fig, self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Navigation Toolbar hinzufügen
        toolbar = NavigationToolbar2Tk(canvas, self.chart_container)
        toolbar.update()
        
    def cleanup(self):
        """Cleanup-Funktion beim Schließen"""
        # Matplotlib Figures schließen
        if MATPLOTLIB_AVAILABLE:
            plt.close('all')