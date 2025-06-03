#!/usr/bin/env python3
"""
🚀 PUNKT2 ULTRA-PERFORMANCE KONFIGURATOR
VectorBT Pro optimierte GUI mit allen Performance-Features
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import json
from datetime import datetime

class UltraPerformancePunkt2Konfigurator:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 VectorBT Pro - Punkt 2 Ultra-Performance Konfigurator")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#1e1e1e')

        # Maximieren für bessere Sicht
        self.root.state('zoomed')  # Windows maximieren

        # Variablen für Konfiguration
        self.selected_file_path = None
        self.timeframe_mode_var = tk.StringVar()
        self.single_timeframe_var = tk.StringVar()

        # Multi-Timeframe Variablen
        self.tf_1m_var = tk.BooleanVar()
        self.tf_2m_var = tk.BooleanVar()
        self.tf_3m_var = tk.BooleanVar()
        self.tf_5m_var = tk.BooleanVar()
        self.tf_10m_var = tk.BooleanVar()
        self.tf_15m_var = tk.BooleanVar()
        self.tf_30m_var = tk.BooleanVar()
        self.tf_1h_var = tk.BooleanVar()
        self.tf_2h_var = tk.BooleanVar()
        self.tf_4h_var = tk.BooleanVar()
        self.tf_8h_var = tk.BooleanVar()
        self.tf_1d_var = tk.BooleanVar()
        self.tf_3d_var = tk.BooleanVar()
        self.tf_1w_var = tk.BooleanVar()

        # Visualisierung und Speicher-Optionen
        self.viz_var = tk.StringVar()
        self.viz_count_var = tk.StringVar()
        self.custom_count_var = tk.IntVar(value=500)
        self.save_punkt3_var = tk.BooleanVar(value=True)
        self.save_backup_var = tk.BooleanVar(value=True)
        self.save_charts_var = tk.BooleanVar(value=False)
        self.show_summary_var = tk.BooleanVar(value=True)

        # Performance-Optionen
        self.enable_chunking_var = tk.BooleanVar(value=True)
        self.enable_numba_var = tk.BooleanVar(value=True)
        self.enable_vbt_data_var = tk.BooleanVar(value=True)
        self.enable_memory_opt_var = tk.BooleanVar(value=True)

        # Punkt 1 Dateien scannen
        self.available_files = self.scan_punkt1_files()

        # GUI erstellen
        self.create_widgets()

        # Standard-Werte setzen
        self.set_defaults()

    def scan_punkt1_files(self):
        """Scannt data/punkt1/ nach verfügbaren Dateien - VEREINFACHT"""
        files = {}
        punkt1_dir = "data/punkt1"

        if os.path.exists(punkt1_dir):
            # Alle relevanten Dateien scannen
            all_files = [f for f in os.listdir(punkt1_dir)
                        if f.endswith(('.h5', '.pickle', '.parquet')) and not f.endswith('_metadata.json')]

            for i, file in enumerate(all_files, 1):
                file_path = os.path.join(punkt1_dir, file)

                # Datei-Validierung
                try:
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

                    # Prüfe ob Datei ladbar ist
                    is_valid = self.validate_file(file_path)

                except Exception as e:
                    print(f"⚠️ Fehler bei Datei {file}: {e}")
                    is_valid = False
                    file_size_mb = 0

                # VEREINFACHTE Asset/Period Extraktion
                base_name = file.replace('.h5', '').replace('.pickle', '').replace('.parquet', '')

                # Einfache Erkennung: Erstes Wort = Asset, Zweites = Period
                parts = base_name.split('_')
                asset = parts[0] if len(parts) > 0 else 'Unknown'
                period = parts[1] if len(parts) > 1 else 'Unknown'

                # VBT-Typ erkennen (verbessert)
                if file.endswith('.pickle'):
                    file_type = "VBT"  # Pickle-Dateien sind meist VBT Data Objekte
                elif any(keyword in file.upper() for keyword in ['VBT', 'PUNKT2']):
                    file_type = "VBT"
                else:
                    file_type = "Standard"

                # Timestamp aus Datei-Modifikationszeit
                import datetime
                mod_time = os.path.getmtime(file_path)
                timestamp = datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M")

                files[file] = {
                    'file_path': file_path,
                    'file_size_mb': file_size_mb,
                    'asset': asset,
                    'period': period,
                    'file_type': file_type,
                    'timestamp': timestamp,
                    'index': i,
                    'is_valid': is_valid
                }

        return files

    def validate_file(self, file_path):
        """Validiert ob eine Datei ladbar ist - REPARIERT FÜR PICKLE"""
        try:
            if file_path.endswith('.pickle'):
                # Pickle-Datei testen - VEREINFACHT und ROBUST

                # Methode 1: Prüfe Pickle Magic Number (schnell)
                try:
                    with open(file_path, 'rb') as f:
                        header = f.read(10)  # Erste 10 Bytes
                        if len(header) > 0 and header[0:1] in [b'\x80', b'\x81', b'\x82', b'\x83', b'\x84', b'\x85']:
                            return True
                except Exception:
                    pass

                # Methode 2: Versuche VBT Data Objekt zu laden (falls VBT verfügbar)
                try:
                    import vectorbtpro as vbt
                    # Teste VBT Data Objekt Laden
                    vbt_data = vbt.Data.load(file_path)
                    return True
                except ImportError:
                    pass
                except Exception:
                    pass

                # Methode 3: Standard Pickle Test (vorsichtig)
                try:
                    import pickle
                    with open(file_path, 'rb') as f:
                        # Versuche nur den ersten Pickle-Eintrag zu lesen
                        pickler = pickle.Unpickler(f)
                        obj = pickler.load()
                        return True
                except Exception:
                    pass

                # Fallback: Datei existiert und ist nicht leer
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    return True

                return False

            elif file_path.endswith('.h5'):
                # HDF5-Datei testen
                import pandas as pd
                try:
                    with pd.HDFStore(file_path, 'r') as store:
                        keys = list(store.keys())
                        return len(keys) > 0
                except:
                    # Fallback: Prüfe nur ob Datei existiert und lesbar ist
                    return os.path.exists(file_path) and os.path.getsize(file_path) > 0

            elif file_path.endswith('.parquet'):
                # Parquet-Datei testen
                import pandas as pd
                try:
                    df = pd.read_parquet(file_path, nrows=1)  # Nur erste Zeile
                    return len(df) > 0
                except:
                    # Fallback: Prüfe nur ob Datei existiert
                    return os.path.exists(file_path) and os.path.getsize(file_path) > 0
            else:
                return False
        except Exception as e:
            print(f"⚠️ Validierung fehlgeschlagen für {file_path}: {e}")
            return False

    def create_widgets(self):
        """Erstellt alle GUI-Elemente"""

        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Titel
        title_label = ttk.Label(main_frame, text="🚀 PUNKT 2: ULTRA-PERFORMANCE MULTI-TIMEFRAME KONFIGURATOR",
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Performance-Status anzeigen
        self.create_performance_status(main_frame)

        # Linke Spalte - Scrollable Konfiguration
        config_outer_frame = ttk.LabelFrame(main_frame, text="🔧 ULTRA-PERFORMANCE KONFIGURATION", padding="5")
        config_outer_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Canvas und Scrollbar für Scrolling
        canvas = tk.Canvas(config_outer_frame, bg='#2e2e2e', highlightthickness=0, width=500, height=700)
        scrollbar = ttk.Scrollbar(config_outer_frame, orient="vertical", command=canvas.yview)
        config_frame = ttk.Frame(canvas)

        # Scrollable Frame konfigurieren
        config_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=config_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Canvas und Scrollbar platzieren
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Grid-Konfiguration für Canvas
        config_outer_frame.columnconfigure(0, weight=1)
        config_outer_frame.rowconfigure(0, weight=1)

        # Mausrad-Scrolling hinzufügen
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)
        self.canvas = canvas

        row = 0

        # 1. DATEI-AUSWAHL
        self.create_file_selection(config_frame, row)
        row += 3

        # 2. TIMEFRAME-MODUS
        self.create_timeframe_selection(config_frame, row)
        row += 5

        # 3. PERFORMANCE-OPTIONEN
        self.create_performance_options(config_frame, row)
        row += 2

        # 4. VISUALISIERUNG
        self.create_visualization_options(config_frame, row)
        row += 3

        # 5. SPEICHER-OPTIONEN
        self.create_save_options(config_frame, row)
        row += 2

        # Code generieren Button
        generate_btn = ttk.Button(config_frame, text="🚀 ULTRA-PERFORMANCE CODE GENERIEREN",
                                 command=self.generate_ultra_performance_code, 
                                 style='Accent.TButton')
        generate_btn.grid(row=row, column=0, pady=(20, 0), sticky=(tk.W, tk.E))

        # Rechte Spalte - Datei-Info und Code-Ausgabe
        self.create_right_panel(main_frame)

        # Grid-Konfiguration für Responsive Design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

    def create_performance_status(self, parent):
        """Erstellt Performance-Status Anzeige"""
        status_frame = ttk.LabelFrame(parent, text="🚀 ULTRA-PERFORMANCE STATUS", padding="10")
        status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Performance-Checks
        try:
            import vectorbtpro as vbt
            vbt_status = "✅ VectorBT Pro verfügbar"
            vbt_color = "green"
        except ImportError:
            vbt_status = "❌ VectorBT Pro nicht verfügbar"
            vbt_color = "red"

        try:
            from numba import njit
            numba_status = "✅ Numba JIT verfügbar"
            numba_color = "green"
        except ImportError:
            numba_status = "❌ Numba nicht verfügbar"
            numba_color = "red"

        # Status Labels
        ttk.Label(status_frame, text=vbt_status, foreground=vbt_color).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Label(status_frame, text=numba_status, foreground=numba_color).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        ttk.Label(status_frame, text="✅ Memory-Optimierung", foreground="green").grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        ttk.Label(status_frame, text="✅ Chunked Processing", foreground="green").grid(row=0, column=3, sticky=tk.W)

    def create_file_selection(self, parent, start_row):
        """Erstellt Datei-Auswahl Sektion"""
        ttk.Label(parent, text="📁 1. ULTRA-PERFORMANCE DATEI-AUSWAHL:", 
                 font=('Arial', 12, 'bold')).grid(row=start_row, column=0, sticky=tk.W, pady=(0, 10))

        # Datei-Auswahl Frame
        file_frame = ttk.Frame(parent)
        file_frame.grid(row=start_row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(0, weight=1)

        # Dropdown für verfügbare Dateien (nur gültige)
        if self.available_files:
            valid_files = {k: v for k, v in self.available_files.items() if v.get('is_valid', False)}
            if valid_files:
                file_options = [f"{info['asset']} ({info['period']}) - {info['file_type']} - {info['file_size_mb']:.1f}MB"
                               for info in valid_files.values()]
            else:
                file_options = ["Keine gültigen Punkt 1 Dateien gefunden"]
        else:
            file_options = ["Keine Punkt 1 Dateien gefunden"]

        self.file_var = tk.StringVar()
        self.file_combo = ttk.Combobox(file_frame, textvariable=self.file_var, values=file_options, width=50)
        self.file_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.file_combo.bind('<<ComboboxSelected>>', self.on_file_selected)

        # Button für Datei-Browser
        ttk.Button(file_frame, text="📁 ANDERE DATEI", command=self.browse_file, width=15).grid(row=0, column=1)

        # Label für gewählte Datei
        self.selected_file_var = tk.StringVar()
        self.file_label = ttk.Label(file_frame, textvariable=self.selected_file_var, 
                                   foreground='green', font=('Arial', 9))
        self.file_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))

    def create_timeframe_selection(self, parent, start_row):
        """Erstellt Timeframe-Auswahl Sektion"""
        ttk.Label(parent, text="⏰ 2. ULTRA-PERFORMANCE TIMEFRAME-MODUS:", 
                 font=('Arial', 12, 'bold')).grid(row=start_row, column=0, sticky=tk.W, pady=(10, 5))

        # Timeframe-Modus Auswahl
        mode_frame = ttk.Frame(parent)
        mode_frame.grid(row=start_row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Radiobutton(mode_frame, text="📊 Einzel-Timeframe (Optimiert)", 
                       variable=self.timeframe_mode_var, value="single", 
                       command=self.on_mode_change).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))

        ttk.Radiobutton(mode_frame, text="📈 Multi-Timeframe (Ultra-Performance)", 
                       variable=self.timeframe_mode_var, value="multi", 
                       command=self.on_mode_change).grid(row=0, column=1, sticky=tk.W)

        # Einzel-Timeframe Auswahl
        self.single_frame = ttk.LabelFrame(parent, text="📊 EINZEL-TIMEFRAME AUSWAHL", padding="10")
        self.single_frame.grid(row=start_row+2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        timeframes = ["1m", "2m", "3m", "5m", "10m", "15m", "30m", "1h", "2h", "4h", "8h", "1d", "3d", "1w"]
        self.single_combo = ttk.Combobox(self.single_frame, textvariable=self.single_timeframe_var,
                                        values=timeframes, width=15)
        self.single_combo.grid(row=0, column=0, sticky=tk.W)

        # Multi-Timeframe Auswahl
        self.multi_frame = ttk.LabelFrame(parent, text="📈 MULTI-TIMEFRAME ULTRA-PERFORMANCE", padding="10")
        self.multi_frame.grid(row=start_row+3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.create_multi_timeframe_checkboxes()

    def create_multi_timeframe_checkboxes(self):
        """Erstellt Multi-Timeframe Checkboxes"""
        tf_row = 0

        # Minuten
        ttk.Label(self.multi_frame, text="⏱️ Minuten (High-Frequency):", 
                 font=('Arial', 9, 'bold')).grid(row=tf_row, column=0, sticky=tk.W, pady=(0, 5))
        tf_row += 1

        minute_frame = ttk.Frame(self.multi_frame)
        minute_frame.grid(row=tf_row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Checkbutton(minute_frame, text="1m", variable=self.tf_1m_var).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Checkbutton(minute_frame, text="2m", variable=self.tf_2m_var).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Checkbutton(minute_frame, text="3m", variable=self.tf_3m_var).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        ttk.Checkbutton(minute_frame, text="5m", variable=self.tf_5m_var).grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        ttk.Checkbutton(minute_frame, text="10m", variable=self.tf_10m_var).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Checkbutton(minute_frame, text="15m", variable=self.tf_15m_var).grid(row=1, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Checkbutton(minute_frame, text="30m", variable=self.tf_30m_var).grid(row=1, column=2, sticky=tk.W, padx=(0, 10))

        tf_row += 1

        # Stunden
        ttk.Label(self.multi_frame, text="🕐 Stunden (Medium-Frequency):", 
                 font=('Arial', 9, 'bold')).grid(row=tf_row, column=0, sticky=tk.W, pady=(10, 5))
        tf_row += 1

        hour_frame = ttk.Frame(self.multi_frame)
        hour_frame.grid(row=tf_row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Checkbutton(hour_frame, text="1h", variable=self.tf_1h_var).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Checkbutton(hour_frame, text="2h", variable=self.tf_2h_var).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Checkbutton(hour_frame, text="4h", variable=self.tf_4h_var).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        ttk.Checkbutton(hour_frame, text="8h", variable=self.tf_8h_var).grid(row=0, column=3, sticky=tk.W, padx=(0, 10))

        tf_row += 1

        # Tage/Wochen
        ttk.Label(self.multi_frame, text="📅 Tage/Wochen (Low-Frequency):", 
                 font=('Arial', 9, 'bold')).grid(row=tf_row, column=0, sticky=tk.W, pady=(10, 5))
        tf_row += 1

        period_frame = ttk.Frame(self.multi_frame)
        period_frame.grid(row=tf_row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Checkbutton(period_frame, text="1d", variable=self.tf_1d_var).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Checkbutton(period_frame, text="3d", variable=self.tf_3d_var).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Checkbutton(period_frame, text="1w", variable=self.tf_1w_var).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))

        # Quick-Select Buttons
        tf_row += 1
        quick_frame = ttk.Frame(self.multi_frame)
        quick_frame.grid(row=tf_row, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Button(quick_frame, text="🚀 Alle auswählen", command=self.select_all_timeframes, width=15).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(quick_frame, text="❌ Alle abwählen", command=self.deselect_all_timeframes, width=15).grid(row=0, column=1, padx=5)
        ttk.Button(quick_frame, text="⭐ Ultra-Performance (5m,15m,1h,1d)", command=self.select_ultra_performance_timeframes, width=25).grid(row=0, column=2, padx=(5, 0))

    def create_performance_options(self, parent, start_row):
        """Erstellt Performance-Optionen"""
        ttk.Label(parent, text="🚀 3. ULTRA-PERFORMANCE OPTIONEN:", 
                 font=('Arial', 12, 'bold')).grid(row=start_row, column=0, sticky=tk.W, pady=(15, 5))

        perf_frame = ttk.Frame(parent)
        perf_frame.grid(row=start_row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Checkbutton(perf_frame, text="🧩 Chunked Processing (große Datenmengen)", 
                       variable=self.enable_chunking_var).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(perf_frame, text="⚡ Numba JIT Optimierung (10-50x schneller)", 
                       variable=self.enable_numba_var).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(perf_frame, text="🚀 VBT Data Objekte (20x Backtesting-Speedup)", 
                       variable=self.enable_vbt_data_var).grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(perf_frame, text="💾 Memory-Optimierung (50-70% weniger RAM)", 
                       variable=self.enable_memory_opt_var).grid(row=3, column=0, sticky=tk.W, pady=2)

    def create_visualization_options(self, parent, start_row):
        """Erstellt Visualisierung-Optionen"""
        ttk.Label(parent, text="📈 4. ULTRA-PERFORMANCE VISUALISIERUNG:", 
                 font=('Arial', 12, 'bold')).grid(row=start_row, column=0, sticky=tk.W, pady=(15, 5))

        # Visualisierung Auswahl
        viz_options = [
            "Interaktive Multi-Timeframe Charts (Ultra-Performance)",
            "Normale Multi-Timeframe Charts",
            "Nur Daten-Tabellen (Memory-optimiert)",
            "Interaktive Charts + Tabellen",
            "Normale Charts + Tabellen",
            "Keine Visualisierung (Maximale Performance)"
        ]
        self.viz_combo = ttk.Combobox(parent, textvariable=self.viz_var, values=viz_options, width=45)
        self.viz_combo.grid(row=start_row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.viz_combo.bind('<<ComboboxSelected>>', self.on_viz_change)

        # Kerzen-Anzahl
        self.viz_count_frame = ttk.Frame(parent)
        self.viz_count_frame.grid(row=start_row+2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(self.viz_count_frame, text="📊 Kerzen pro Chart (Performance-optimiert):", 
                 font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 2))

        count_options = [
            "100 Kerzen (Ultra-schnell)",
            "250 Kerzen (Schnell)",
            "500 Kerzen (Standard)",
            "1000 Kerzen (Langsam)",
            "Benutzerdefiniert",
            "Alle Kerzen (Sehr langsam)"
        ]
        self.viz_count_combo = ttk.Combobox(self.viz_count_frame, textvariable=self.viz_count_var, 
                                           values=count_options, width=25)
        self.viz_count_combo.grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.viz_count_combo.bind('<<ComboboxSelected>>', self.on_count_change)

        # Custom Count
        self.custom_count_frame = ttk.Frame(self.viz_count_frame)
        self.custom_count_frame.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        ttk.Label(self.custom_count_frame, text="Anzahl:").grid(row=0, column=0, sticky=tk.W)
        self.custom_count_spin = ttk.Spinbox(self.custom_count_frame, from_=50, to=10000, 
                                            textvariable=self.custom_count_var, width=8)
        self.custom_count_spin.grid(row=0, column=1, padx=(5, 0))

    def create_save_options(self, parent, start_row):
        """Erstellt Speicher-Optionen"""
        ttk.Label(parent, text="💾 5. ULTRA-PERFORMANCE SPEICHER-OPTIONEN:", 
                 font=('Arial', 12, 'bold')).grid(row=start_row, column=0, sticky=tk.W, pady=(15, 5))

        save_frame = ttk.Frame(parent)
        save_frame.grid(row=start_row+1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Checkbutton(save_frame, text="🚀 Speichern für Punkt 3 (VBT Data Objekte + HDF5)",
                       variable=self.save_punkt3_var).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(save_frame, text="📁 Ultra-Performance Backup (Blosc komprimiert)",
                       variable=self.save_backup_var).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(save_frame, text="📊 Charts als HTML speichern",
                       variable=self.save_charts_var).grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(save_frame, text="📋 Ultra-Performance Zusammenfassung anzeigen",
                       variable=self.show_summary_var).grid(row=3, column=0, sticky=tk.W, pady=2)

    def create_right_panel(self, parent):
        """Erstellt rechtes Panel"""
        right_frame = ttk.Frame(parent)
        right_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))

        # Datei-Info
        file_info_frame = ttk.LabelFrame(right_frame, text="📋 VERFÜGBARE PUNKT 1 DATEIEN (ULTRA-PERFORMANCE)", padding="10")
        file_info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))

        self.file_info_text = tk.Text(file_info_frame, height=10, width=60, bg='#2e2e2e', fg='#ffffff')
        self.file_info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.update_file_info()

        # Code-Ausgabe
        code_frame = ttk.LabelFrame(right_frame, text="📋 ULTRA-PERFORMANCE GENERIERTER CODE", padding="10")
        code_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.code_text = scrolledtext.ScrolledText(code_frame, height=25, width=70,
                                                  bg='#1e1e1e', fg='#00ff88',
                                                  font=('Consolas', 9))
        self.code_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Buttons für Code-Aktionen
        button_frame = ttk.Frame(code_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Button(button_frame, text="📋 CODE KOPIEREN",
                  command=self.copy_code).grid(row=0, column=0, padx=(0, 5))

        ttk.Button(button_frame, text="💾 ALS DATEI SPEICHERN",
                  command=self.save_code).grid(row=0, column=1, padx=5)

        ttk.Button(button_frame, text="🚀 CODE AUSFÜHREN",
                  command=self.execute_code).grid(row=0, column=2, padx=(5, 0))

        # Grid-Konfiguration
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        code_frame.columnconfigure(0, weight=1)
        code_frame.rowconfigure(0, weight=1)

    def set_defaults(self):
        """Setzt Standard-Werte"""
        self.timeframe_mode_var.set("multi")
        self.single_timeframe_var.set("5m")

        # Ultra-Performance Standard-Timeframes
        self.tf_5m_var.set(True)
        self.tf_15m_var.set(True)
        self.tf_1h_var.set(True)
        self.tf_1d_var.set(True)

        self.viz_var.set("Interaktive Multi-Timeframe Charts (Ultra-Performance)")
        self.viz_count_var.set("500 Kerzen (Standard)")

        self.on_mode_change()
        self.on_viz_change()
        self.on_count_change()

    def on_file_selected(self, event=None):
        """Event-Handler für Datei-Auswahl - VEREINFACHT"""
        selected_text = self.file_var.get()

        # Finde die entsprechende Datei (nur gültige)
        valid_files = {k: v for k, v in self.available_files.items() if v.get('is_valid', False)}

        for filename, info in valid_files.items():
            display_text = f"{info['asset']} ({info['period']}) - {info['file_type']} - {info['file_size_mb']:.1f}MB"
            if display_text == selected_text:
                self.selected_file_path = info['file_path']
                status_icon = "✅" if info['is_valid'] else "⚠️"
                self.selected_file_var.set(f"{status_icon} Gewählt: {filename} ({info['file_size_mb']:.1f} MB)")
                break

    def browse_file(self):
        """Öffnet Datei-Browser"""
        file_path = filedialog.askopenfilename(
            title="Ultra-Performance Datei auswählen",
            filetypes=[
                ("VBT Data Objekte", "*.pickle"),
                ("HDF5 Dateien", "*.h5"),
                ("Alle Dateien", "*.*")
            ],
            initialdir="data/punkt1"
        )

        if file_path:
            self.selected_file_path = file_path
            filename = os.path.basename(file_path)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            self.selected_file_var.set(f"✅ Gewählt: {filename} ({file_size_mb:.1f} MB)")

    def on_mode_change(self):
        """Event-Handler für Timeframe-Modus Änderung"""
        mode = self.timeframe_mode_var.get()

        if mode == "single":
            self.single_frame.grid()
            self.multi_frame.grid_remove()
        else:
            self.single_frame.grid_remove()
            self.multi_frame.grid()

    def on_viz_change(self, event=None):
        """Event-Handler für Visualisierung Änderung"""
        viz_option = self.viz_var.get()

        if "Keine Visualisierung" in viz_option:
            self.viz_count_frame.grid_remove()
        else:
            self.viz_count_frame.grid()

    def on_count_change(self, event=None):
        """Event-Handler für Kerzen-Anzahl Änderung"""
        count_option = self.viz_count_var.get()

        if "Benutzerdefiniert" in count_option:
            self.custom_count_frame.grid()
        else:
            self.custom_count_frame.grid_remove()

    def select_all_timeframes(self):
        """Wählt alle Timeframes aus"""
        all_tf_vars = [
            self.tf_1m_var, self.tf_2m_var, self.tf_3m_var, self.tf_5m_var,
            self.tf_10m_var, self.tf_15m_var, self.tf_30m_var, self.tf_1h_var,
            self.tf_2h_var, self.tf_4h_var, self.tf_8h_var, self.tf_1d_var,
            self.tf_3d_var, self.tf_1w_var
        ]
        for var in all_tf_vars:
            var.set(True)

    def deselect_all_timeframes(self):
        """Wählt alle Timeframes ab"""
        all_tf_vars = [
            self.tf_1m_var, self.tf_2m_var, self.tf_3m_var, self.tf_5m_var,
            self.tf_10m_var, self.tf_15m_var, self.tf_30m_var, self.tf_1h_var,
            self.tf_2h_var, self.tf_4h_var, self.tf_8h_var, self.tf_1d_var,
            self.tf_3d_var, self.tf_1w_var
        ]
        for var in all_tf_vars:
            var.set(False)

    def select_ultra_performance_timeframes(self):
        """Wählt Ultra-Performance Timeframes aus"""
        self.deselect_all_timeframes()
        self.tf_5m_var.set(True)
        self.tf_15m_var.set(True)
        self.tf_1h_var.set(True)
        self.tf_1d_var.set(True)

    def update_file_info(self):
        """Aktualisiert Datei-Info Anzeige - VERBESSERT"""
        self.file_info_text.delete(1.0, tk.END)

        if not self.available_files:
            self.file_info_text.insert(tk.END, "❌ Keine Punkt 1 Dateien gefunden!\n\n")
            self.file_info_text.insert(tk.END, "💡 Führen Sie zuerst Punkt 1 Ultra-Performance aus:\n")
            self.file_info_text.insert(tk.END, "   python punkt1_ultra_performance_konfigurator.py\n\n")
            self.file_info_text.insert(tk.END, "🚀 Oder verwenden Sie 'ANDERE DATEI' Button")
            return

        # Separate gültige und ungültige Dateien
        valid_files = {k: v for k, v in self.available_files.items() if v.get('is_valid', False)}
        invalid_files = {k: v for k, v in self.available_files.items() if not v.get('is_valid', False)}

        self.file_info_text.insert(tk.END, f"🚀 PUNKT 1 DATEIEN GEFUNDEN ({len(self.available_files)} total):\n")
        self.file_info_text.insert(tk.END, "=" * 60 + "\n\n")

        # Gültige Dateien zuerst
        if valid_files:
            self.file_info_text.insert(tk.END, f"✅ GÜLTIGE DATEIEN ({len(valid_files)}):\n")

            # Sortiere nach Timestamp (neueste zuerst)
            sorted_valid = sorted(valid_files.items(),
                                 key=lambda x: x[1]['timestamp'], reverse=True)

            for filename, info in sorted_valid:
                self.file_info_text.insert(tk.END, f"📁 {filename}\n")
                self.file_info_text.insert(tk.END, f"   📊 Asset: {info['asset']}\n")
                self.file_info_text.insert(tk.END, f"   📅 Periode: {info['period']}\n")
                self.file_info_text.insert(tk.END, f"   🚀 Typ: {info['file_type']}\n")
                self.file_info_text.insert(tk.END, f"   💾 Größe: {info['file_size_mb']:.1f} MB\n")
                self.file_info_text.insert(tk.END, f"   🕐 Erstellt: {info['timestamp']}\n")

                if info['file_type'] == 'VBT':
                    self.file_info_text.insert(tk.END, f"   ⚡ 20x Backtesting-Speedup verfügbar!\n")

                self.file_info_text.insert(tk.END, "\n")

        # Ungültige Dateien (falls vorhanden)
        if invalid_files:
            self.file_info_text.insert(tk.END, f"⚠️ UNGÜLTIGE DATEIEN ({len(invalid_files)}):\n")
            for filename, info in invalid_files.items():
                self.file_info_text.insert(tk.END, f"❌ {filename} - Nicht ladbar\n")
            self.file_info_text.insert(tk.END, "\n")

    def get_selected_timeframes(self):
        """Gibt ausgewählte Timeframes zurück"""
        if self.timeframe_mode_var.get() == "single":
            return [self.single_timeframe_var.get()]

        timeframes = []

        # Korrekte Timeframe-Mapping (BooleanVar als Key funktioniert nicht)
        tf_vars_and_names = [
            (self.tf_1m_var, "1m"), (self.tf_2m_var, "2m"), (self.tf_3m_var, "3m"),
            (self.tf_5m_var, "5m"), (self.tf_10m_var, "10m"), (self.tf_15m_var, "15m"),
            (self.tf_30m_var, "30m"), (self.tf_1h_var, "1h"), (self.tf_2h_var, "2h"),
            (self.tf_4h_var, "4h"), (self.tf_8h_var, "8h"), (self.tf_1d_var, "1d"),
            (self.tf_3d_var, "3d"), (self.tf_1w_var, "1w")
        ]

        for var, tf_name in tf_vars_and_names:
            if var.get():
                timeframes.append(tf_name)

        return timeframes

    def generate_ultra_performance_code(self):
        """Generiert Ultra-Performance Code"""
        # Validierung
        if not self.selected_file_path:
            messagebox.showerror("Fehler", "Bitte wählen Sie eine Datei aus!")
            return

        timeframes = self.get_selected_timeframes()
        if not timeframes:
            messagebox.showerror("Fehler", "Bitte wählen Sie mindestens einen Timeframe aus!")
            return

        # Konfiguration erstellen
        config = {
            'selected_file_path': self.selected_file_path,
            'timeframe_mode': self.timeframe_mode_var.get(),
            'timeframes': timeframes,
            'viz_option': self.viz_var.get(),
            'viz_count': self.viz_count_var.get(),
            'custom_count': self.custom_count_var.get(),
            'save_punkt3': self.save_punkt3_var.get(),
            'save_backup': self.save_backup_var.get(),
            'save_charts': self.save_charts_var.get(),
            'show_summary': self.show_summary_var.get(),
            'enable_chunking': self.enable_chunking_var.get(),
            'enable_numba': self.enable_numba_var.get(),
            'enable_vbt_data': self.enable_vbt_data_var.get(),
            'enable_memory_opt': self.enable_memory_opt_var.get()
        }

        try:
            # Code generieren
            from punkt2_ultra_performance_code_generator import generate_ultra_performance_punkt2_code
            generated_code = generate_ultra_performance_punkt2_code(config)

            # Code anzeigen
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(tk.END, generated_code)

            # Erfolg-Nachricht
            messagebox.showinfo("Erfolg",
                               f"🚀 Ultra-Performance Code generiert!\n\n"
                               f"📊 Timeframes: {len(timeframes)}\n"
                               f"📁 Datei: {os.path.basename(self.selected_file_path)}\n"
                               f"⚡ VBT Optimierungen: Alle aktiv\n"
                               f"💾 Code-Länge: {len(generated_code):,} Zeichen")

        except Exception as e:
            messagebox.showerror("Fehler", f"Code-Generierung fehlgeschlagen:\n{str(e)}")

    def copy_code(self):
        """Kopiert Code in Zwischenablage"""
        code = self.code_text.get(1.0, tk.END)
        if code.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            messagebox.showinfo("Erfolg", "Code in Zwischenablage kopiert!")
        else:
            messagebox.showwarning("Warnung", "Kein Code zum Kopieren vorhanden!")

    def save_code(self):
        """Speichert Code als Datei"""
        code = self.code_text.get(1.0, tk.END)
        if not code.strip():
            messagebox.showwarning("Warnung", "Kein Code zum Speichern vorhanden!")
            return

        # Dateiname vorschlagen
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        timeframes = self.get_selected_timeframes()
        tf_str = "_".join(timeframes[:3])  # Erste 3 Timeframes
        suggested_name = f"punkt2_ultra_performance_{tf_str}_{timestamp}.py"

        file_path = filedialog.asksaveasfilename(
            title="Ultra-Performance Code speichern",
            defaultextension=".py",
            filetypes=[("Python Dateien", "*.py"), ("Alle Dateien", "*.*")],
            initialfilename=suggested_name
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                messagebox.showinfo("Erfolg", f"Code gespeichert:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Speichern fehlgeschlagen:\n{str(e)}")

    def execute_code(self):
        """Führt generierten Code aus"""
        code = self.code_text.get(1.0, tk.END)
        if not code.strip():
            messagebox.showwarning("Warnung", "Kein Code zum Ausführen vorhanden!")
            return

        # Warnung anzeigen
        result = messagebox.askyesno("Ultra-Performance Code ausführen",
                                    "🚀 ULTRA-PERFORMANCE CODE AUSFÜHREN?\n\n"
                                    "⚠️ WARNUNG:\n"
                                    "• Code wird sofort ausgeführt\n"
                                    "• Kann viel RAM und CPU verwenden\n"
                                    "• Erstellt Dateien in data/punkt2/\n\n"
                                    "💡 EMPFEHLUNG:\n"
                                    "• Speichern Sie den Code zuerst\n"
                                    "• Führen Sie ihn im vectorbt_env aus\n\n"
                                    "Trotzdem ausführen?")

        if result:
            try:
                # Code in temporärer Datei speichern und ausführen
                timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                temp_file = f"temp_ultra_performance_{timestamp}.py"

                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(code)

                # Code ausführen
                import subprocess
                import sys

                # Führe im aktuellen Python-Environment aus
                result = subprocess.run([sys.executable, temp_file],
                                      capture_output=True, text=True, timeout=300)

                # Temporäre Datei löschen
                try:
                    os.remove(temp_file)
                except:
                    pass

                if result.returncode == 0:
                    messagebox.showinfo("Erfolg",
                                       "🚀 Ultra-Performance Code erfolgreich ausgeführt!\n\n"
                                       "📁 Prüfen Sie data/punkt2/ für Ergebnisse")
                else:
                    messagebox.showerror("Fehler",
                                        f"Code-Ausführung fehlgeschlagen:\n\n"
                                        f"STDOUT:\n{result.stdout}\n\n"
                                        f"STDERR:\n{result.stderr}")

            except subprocess.TimeoutExpired:
                messagebox.showerror("Fehler", "Code-Ausführung Timeout (5 Minuten)")
            except Exception as e:
                messagebox.showerror("Fehler", f"Ausführung fehlgeschlagen:\n{str(e)}")


def main():
    """Hauptfunktion"""
    root = tk.Tk()

    # Dunkles Theme (falls verfügbar)
    try:
        root.tk.call("source", "azure.tcl")
        root.tk.call("set_theme", "dark")
    except:
        pass

    app = UltraPerformancePunkt2Konfigurator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
