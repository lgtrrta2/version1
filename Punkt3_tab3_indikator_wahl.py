# 📊 PUNKT 3: TAB 3 - INDIKATOR-AUSWAHL
# Dritte Tab für Indikator-Browser und Auswahl

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logging
from typing import Dict, List, Optional, Any

from Punkt3_settings import CONFIG
from Punkt3_events import emit_indicators_changed, emit_status_changed, on, Events
from Punkt3_state_manager import state_manager, get_state
from Punkt3_utils import IndicatorUtils, UIUtils, ScrollableFrame
from punkt3_indicators import get_all_indicators

class Tab3IndikatorWahl:
    """Tab 3: Indikator-Auswahl und Browser"""

    def __init__(self, parent_notebook):
        self.notebook = parent_notebook
        self.logger = logging.getLogger(__name__)

        # Variablen
        self.search_var = tk.StringVar()
        self.library_filter_var = tk.StringVar(value="Alle")
        self.category_filter_var = tk.StringVar(value="Alle")

        # Alle verfügbaren Indikatoren laden
        self.all_indicators = get_all_indicators()
        self.filtered_indicators = self.all_indicators.copy()

        # Tab erstellen
        self.create_tab()

        # Event-Listener registrieren
        self.setup_event_listeners()

        # Initial laden
        self.populate_indicator_tree()
        self.update_statistics()

    def create_tab(self):
        """Erstellt Tab 3 GUI"""
        # Tab-Frame
        self.tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_frame, text="📊 3. INDIKATOR-AUSWAHL")

        # Scrollbares Frame erstellen
        self.scrollable = ScrollableFrame(self.tab_frame)
        self.scrollable.get_main_frame().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Container ist jetzt das scrollbare Frame
        container = self.scrollable.get_frame()

        # Padding hinzufügen
        container.configure(padding=CONFIG.GUI_CONFIG['tab_padding'])

        # 1. QUICK-ADD SEKTION
        self.create_quick_add_section(container)

        # 2. FILTER UND BROWSER
        self.create_main_browser_section(container)

        # Grid-Konfiguration
        self.tab_frame.columnconfigure(0, weight=1)
        self.tab_frame.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

    def create_quick_add_section(self, parent):
        """Erstellt Quick-Add Buttons Sektion"""
        quick_frame = ttk.LabelFrame(parent, text="⭐ SCHNELL-AUSWAHL",
                                    padding=CONFIG.GUI_CONFIG['frame_padding'])
        quick_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        # Beschreibung
        desc_label = ttk.Label(quick_frame,
                              text="Vordefinierte Indikator-Sets für schnellen Start:",
                              font=CONFIG.FONTS['normal'])
        desc_label.grid(row=0, column=0, columnspan=5, sticky=tk.W, pady=(0, 10))

        # Quick-Add Buttons
        button_frame = ttk.Frame(quick_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        buttons = [
            ("⭐ Standard Set", self.add_standard_indicators, "5 wichtigste Indikatoren"),
            ("📈 Trend Set", self.add_trend_indicators, "6 Trend-Indikatoren"),
            ("⚡ Momentum Set", self.add_momentum_indicators, "4 Momentum-Indikatoren"),
            ("🗑️ Alle löschen", self.clear_all_indicators, "Alle ausgewählten Indikatoren entfernen")
        ]

        for i, (text, command, tooltip) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command,
                            width=CONFIG.GUI_CONFIG['button_width'])
            btn.grid(row=0, column=i, padx=(0, 10) if i < len(buttons)-1 else 0)
            UIUtils.create_tooltip(btn, tooltip)

        quick_frame.columnconfigure(0, weight=1)

    def create_main_browser_section(self, parent):
        """Erstellt Haupt-Browser Sektion"""
        browser_frame = ttk.Frame(parent)
        browser_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Linke Spalte: Filter
        self.create_filter_section(browser_frame)

        # Rechte Spalte: Indikator-Browser
        self.create_indicator_browser_section(browser_frame)

        # Grid-Konfiguration
        browser_frame.columnconfigure(1, weight=1)
        browser_frame.rowconfigure(0, weight=1)

    def create_filter_section(self, parent):
        """Erstellt Filter-Sektion"""
        filter_frame = ttk.LabelFrame(parent, text="🔍 FILTER & SUCHE",
                                     padding=CONFIG.GUI_CONFIG['frame_padding'])
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))

        # Suchfeld
        search_frame = ttk.Frame(filter_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(search_frame, text="Suche:", font=CONFIG.FONTS['heading']).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var,
                                     width=CONFIG.GUI_CONFIG['entry_width'])
        self.search_entry.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.search_entry.bind('<KeyRelease>', self.on_search_change)

        # Suchfeld-Tooltip
        UIUtils.create_tooltip(self.search_entry, "Suche nach Indikator-Namen (z.B. 'SMA', 'RSI')")

        # Bibliothek-Filter
        lib_frame = ttk.Frame(filter_frame)
        lib_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(lib_frame, text="Bibliothek:", font=CONFIG.FONTS['heading']).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        libraries = ["Alle"] + sorted(list(self.all_indicators.keys()))
        self.library_combo = ttk.Combobox(lib_frame, textvariable=self.library_filter_var,
                                         values=libraries, width=22, state="readonly")
        self.library_combo.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.library_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        # Kategorie-Filter
        cat_frame = ttk.Frame(filter_frame)
        cat_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(cat_frame, text="Kategorie:", font=CONFIG.FONTS['heading']).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.category_combo = ttk.Combobox(cat_frame, textvariable=self.category_filter_var,
                                          values=CONFIG.INDICATOR_CATEGORIES, width=22, state="readonly")
        self.category_combo.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.category_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        # Statistiken
        stats_frame = ttk.LabelFrame(filter_frame, text="📊 STATISTIKEN",
                                    padding=CONFIG.GUI_CONFIG['frame_padding'])
        stats_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(15, 0))

        self.stats_label = ttk.Label(stats_frame, text="Lade Statistiken...",
                                     font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['info'])
        self.stats_label.grid(row=0, column=0, sticky=tk.W)

        # Bibliothek-Übersicht
        self.library_stats_text = tk.Text(stats_frame, height=8, width=25,
                                          bg=CONFIG.COLORS['background'],
                                          font=CONFIG.FONTS['small'],
                                          wrap=tk.WORD, state='disabled')
        self.library_stats_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # Grid-Konfiguration
        filter_frame.columnconfigure(0, weight=1)
        search_frame.columnconfigure(0, weight=1)
        lib_frame.columnconfigure(0, weight=1)
        cat_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(0, weight=1)

    def create_indicator_browser_section(self, parent):
        """Erstellt Indikator-Browser Sektion"""
        browser_frame = ttk.LabelFrame(parent, text="📋 VERFÜGBARE INDIKATOREN",
                                      padding=CONFIG.GUI_CONFIG['frame_padding'])
        browser_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Treeview für Indikatoren
        tree_container = ttk.Frame(browser_frame)
        tree_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Treeview mit Spalten
        columns = ('library', 'category', 'params')
        self.indicator_tree = ttk.Treeview(tree_container, columns=columns,
                                          show='tree headings',
                                          height=CONFIG.GUI_CONFIG['treeview_height'])

        # Spalten konfigurieren
        self.indicator_tree.heading('#0', text='Indikator')
        self.indicator_tree.heading('library', text='Bibliothek')
        self.indicator_tree.heading('category', text='Kategorie')
        self.indicator_tree.heading('params', text='Standard-Parameter')

        # Spaltenbreiten
        UIUtils.configure_treeview_columns(self.indicator_tree, {
            '#0': 180,
            'library': 100,
            'category': 120,
            'params': 250
        })

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical",
                                   command=self.indicator_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal",
                                   command=self.indicator_tree.xview)

        self.indicator_tree.configure(yscrollcommand=v_scrollbar.set,
                                     xscrollcommand=h_scrollbar.set)

        # Grid-Layout für Treeview
        self.indicator_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        # Event-Bindings
        self.indicator_tree.bind('<Double-1>', self.on_indicator_double_click)
        self.indicator_tree.bind('<Return>', self.on_indicator_double_click)

        # Action-Buttons
        action_frame = ttk.Frame(browser_frame)
        action_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(15, 0))

        # Erste Reihe: Standard-Buttons
        ttk.Button(action_frame, text="➕ HINZUFÜGEN",
                  command=self.add_selected_indicator,
                  width=CONFIG.GUI_CONFIG['button_width']).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(action_frame, text="🔧 MIT PARAMETERN",
                  command=self.add_indicator_with_params,
                  width=CONFIG.GUI_CONFIG['button_width']).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(action_frame, text="ℹ️ INFO",
                  command=self.show_indicator_info,
                  width=CONFIG.GUI_CONFIG['button_width']).grid(row=0, column=2)

        # Zweite Reihe: Test-Button
        ttk.Button(action_frame, text="🧪 ALLE HINZUFÜGEN (TEST)",
                  command=self.add_all_indicators_test,
                  width=25,
                  style="Accent.TButton").grid(row=1, column=0, columnspan=3, pady=(10, 0))

        # Hilfe-Text
        help_label = ttk.Label(action_frame,
                              text="💡 Doppelklick auf Indikator zum schnellen Hinzufügen | 🧪 Test-Button fügt ALLE Indikatoren hinzu",
                              font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['info'])
        help_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))

        # Grid-Konfiguration
        browser_frame.columnconfigure(0, weight=1)
        browser_frame.rowconfigure(0, weight=1)

    def setup_event_listeners(self):
        """Registriert Event-Listener"""
        # Lausche auf Datei-Änderungen für Kontext-Updates
        on(Events.FILE_SELECTED, self.on_file_changed)
        on(Events.TIMEFRAMES_CHANGED, self.on_timeframes_changed)

    def populate_indicator_tree(self):
        """Füllt Indikator-Treeview mit gefilterten Indikatoren"""
        # Treeview leeren
        for item in self.indicator_tree.get_children():
            self.indicator_tree.delete(item)

        count = 0
        for library, indicators in self.filtered_indicators.items():
            for name, info in indicators.items():
                # Parameter-String erstellen
                params = info.get("params", [])
                defaults = info.get("defaults", [])

                if params and defaults:
                    param_pairs = [f"{p}={d}" for p, d in zip(params, defaults)]
                    param_str = ", ".join(param_pairs)
                else:
                    param_str = "Keine Parameter"

                # Indikator hinzufügen
                self.indicator_tree.insert('', 'end', text=name,
                                         values=(library, info.get("category", "Unbekannt"), param_str))
                count += 1

        # Statistiken aktualisieren
        self.update_statistics(count)

    def on_search_change(self, event=None):
        """Wird aufgerufen bei Suche-Änderung"""
        # Debouncing für bessere Performance
        if hasattr(self, '_search_timer'):
            self.tab_frame.after_cancel(self._search_timer)

        self._search_timer = self.tab_frame.after(CONFIG.PERFORMANCE['debounce_search_ms'],
                                                 self.apply_filters)

    def on_filter_change(self, event=None):
        """Wird aufgerufen bei Filter-Änderung"""
        self.apply_filters()

    def apply_filters(self):
        """Wendet alle Filter an"""
        search_term = self.search_var.get().lower()
        library_filter = self.library_filter_var.get()
        category_filter = self.category_filter_var.get()

        # Filter anwenden
        self.filtered_indicators = IndicatorUtils.filter_indicators(
            self.all_indicators, search_term, library_filter, category_filter
        )

        # Treeview aktualisieren
        self.populate_indicator_tree()

        self.logger.debug(f"Filter angewendet: Suche='{search_term}', Lib='{library_filter}', Cat='{category_filter}'")

    def update_statistics(self, filtered_count=None):
        """Aktualisiert Statistiken"""
        if filtered_count is None:
            filtered_count = sum(len(indicators) for indicators in self.filtered_indicators.values())

        total_count = sum(len(indicators) for indicators in self.all_indicators.values())

        # Haupt-Statistik
        self.stats_label.config(text=f"Angezeigt: {filtered_count} von {total_count} Indikatoren")

        # Bibliothek-Statistiken
        self.library_stats_text.config(state='normal')
        self.library_stats_text.delete(1.0, tk.END)

        stats_text = "📚 BIBLIOTHEKEN:\n\n"
        for library, indicators in sorted(self.all_indicators.items(),
                                         key=lambda x: len(x[1]), reverse=True):
            count = len(indicators)
            filtered_count_lib = len(self.filtered_indicators.get(library, {}))

            if filtered_count_lib > 0:
                stats_text += f"✅ {library}: {filtered_count_lib}/{count}\n"
            else:
                stats_text += f"⚪ {library}: 0/{count}\n"

        self.library_stats_text.insert(1.0, stats_text)
        self.library_stats_text.config(state='disabled')

    def on_indicator_double_click(self, event=None):
        """Wird aufgerufen bei Doppelklick auf Indikator"""
        self.add_selected_indicator()

    def add_selected_indicator(self):
        """Fügt ausgewählten Indikator mit Standard-Parametern hinzu"""
        selection = self.indicator_tree.selection()
        if not selection:
            UIUtils.show_warning("Warnung", "Bitte wählen Sie einen Indikator aus!")
            return

        item = selection[0]
        name = self.indicator_tree.item(item, 'text')
        values = self.indicator_tree.item(item, 'values')
        library = values[0]

        # Indikator-Info holen
        if library in self.all_indicators and name in self.all_indicators[library]:
            indicator_info = self.all_indicators[library][name]

            # Standard-Parameter verwenden
            params = {}
            param_names = indicator_info.get("params", [])
            defaults = indicator_info.get("defaults", [])

            for param, default in zip(param_names, defaults):
                params[param] = default

            # Indikator hinzufügen
            self.add_indicator_to_state(library, name, params)

            self.logger.info(f"Indikator hinzugefügt: {library}.{name} mit Standard-Parametern")

    def add_indicator_with_params(self):
        """Fügt Indikator mit benutzerdefinierten Parametern hinzu"""
        selection = self.indicator_tree.selection()
        if not selection:
            UIUtils.show_warning("Warnung", "Bitte wählen Sie einen Indikator aus!")
            return

        item = selection[0]
        name = self.indicator_tree.item(item, 'text')
        values = self.indicator_tree.item(item, 'values')
        library = values[0]

        # Indikator-Info holen
        if library in self.all_indicators and name in self.all_indicators[library]:
            indicator_info = self.all_indicators[library][name]

            # Parameter-Dialog öffnen
            params = self.show_parameter_dialog(name, library, indicator_info)

            if params is not None:
                self.add_indicator_to_state(library, name, params)
                self.logger.info(f"Indikator hinzugefügt: {library}.{name} mit benutzerdefinierten Parametern")

    def show_parameter_dialog(self, name: str, library: str, indicator_info: Dict) -> Optional[Dict]:
        """Zeigt Parameter-Dialog für Indikator"""
        param_names = indicator_info.get("params", [])
        defaults = indicator_info.get("defaults", [])

        if not param_names:
            return {}

        # Dialog erstellen
        dialog = tk.Toplevel(self.tab_frame)
        dialog.title(f"Parameter für {library}.{name}")
        dialog.geometry("450x400")
        dialog.transient(self.tab_frame)
        dialog.grab_set()

        # Dialog zentrieren
        UIUtils.center_window(dialog, 450, 400)

        # Hauptframe
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Titel
        title_label = ttk.Label(main_frame, text=f"Parameter für {name}",
                               font=CONFIG.FONTS['heading'])
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Parameter-Eingaben
        param_vars = {}
        for i, (param, default) in enumerate(zip(param_names, defaults)):
            # Label
            ttk.Label(main_frame, text=f"{param}:",
                     font=CONFIG.FONTS['normal']).grid(row=i+1, column=0, sticky=tk.W, pady=5, padx=(0, 10))

            # Entry
            var = tk.StringVar(value=str(default))
            entry = ttk.Entry(main_frame, textvariable=var, width=20)
            entry.grid(row=i+1, column=1, sticky=(tk.W, tk.E), pady=5)
            param_vars[param] = var

        # Ergebnis-Variable
        result = {'params': None}

        # Button-Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(param_names)+2, column=0, columnspan=2, pady=(20, 0))

        def ok_clicked():
            try:
                params = {}
                for param, var in param_vars.items():
                    value = var.get().strip()

                    # Versuche numerische Konvertierung
                    try:
                        if '.' in value:
                            params[param] = float(value)
                        else:
                            params[param] = int(value)
                    except ValueError:
                        # String-Parameter
                        params[param] = value

                result['params'] = params
                dialog.destroy()
            except Exception as e:
                UIUtils.show_error("Fehler", f"Ungültige Parameter:\n{e}")

        def cancel_clicked():
            dialog.destroy()

        ttk.Button(button_frame, text="✅ OK", command=ok_clicked).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Abbrechen", command=cancel_clicked).grid(row=0, column=1)

        # Grid-Konfiguration
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Warten auf Dialog-Schließung
        dialog.wait_window()

        return result['params']

    def add_indicator_to_state(self, library: str, name: str, params: Dict):
        """Fügt Indikator zum State hinzu"""
        # Display-Name erstellen
        display_name = IndicatorUtils.create_display_name(name, params)

        # Indikator-Objekt erstellen
        indicator = {
            "library": library,
            "name": name,
            "params": params,
            "display_name": display_name
        }

        # Zum State hinzufügen (State Manager sendet bereits das Event!)
        state_manager.add_indicator(indicator)

        # ENTFERNT: Doppeltes Event vermeiden
        # emit_indicators_changed("tab3", [indicator], "added")  # State Manager macht das bereits!

        # Erfolgs-Nachricht
        emit_status_changed("tab3", "indicator_added",
                           f"Indikator hinzugefügt: {display_name}", "success")

    def show_indicator_info(self):
        """Zeigt detaillierte Indikator-Informationen"""
        selection = self.indicator_tree.selection()
        if not selection:
            UIUtils.show_warning("Warnung", "Bitte wählen Sie einen Indikator aus!")
            return

        item = selection[0]
        name = self.indicator_tree.item(item, 'text')
        values = self.indicator_tree.item(item, 'values')
        library = values[0]
        category = values[1]

        # Info-Dialog
        info_text = f"📊 INDIKATOR-INFORMATIONEN\n\n"
        info_text += f"Name: {name}\n"
        info_text += f"Bibliothek: {library}\n"
        info_text += f"Kategorie: {category}\n\n"

        if library in self.all_indicators and name in self.all_indicators[library]:
            indicator_info = self.all_indicators[library][name]

            params = indicator_info.get("params", [])
            defaults = indicator_info.get("defaults", [])

            if params:
                info_text += "Parameter:\n"
                for param, default in zip(params, defaults):
                    info_text += f"  • {param}: {default} (Standard)\n"
            else:
                info_text += "Keine Parameter erforderlich\n"

        UIUtils.show_info("Indikator-Info", info_text)

    # Quick-Add Methoden
    def add_standard_indicators(self):
        """Fügt Standard-Indikator-Set hinzu"""
        indicators = CONFIG.INDICATOR_SETS['standard']

        for indicator_config in indicators:
            self.add_indicator_to_state(
                indicator_config["library"],
                indicator_config["name"],
                indicator_config["params"]
            )

        UIUtils.show_info("Standard-Set",
                         f"⭐ {len(indicators)} Standard-Indikatoren hinzugefügt!\n\n"
                         "• SMA(20), SMA(50)\n• EMA(12)\n• RSI(14)\n• MACD(12,26,9)")

    def add_trend_indicators(self):
        """Fügt Trend-Indikator-Set hinzu"""
        indicators = CONFIG.INDICATOR_SETS['trend']

        for indicator_config in indicators:
            self.add_indicator_to_state(
                indicator_config["library"],
                indicator_config["name"],
                indicator_config["params"]
            )

        UIUtils.show_info("Trend-Set",
                         f"📈 {len(indicators)} Trend-Indikatoren hinzugefügt!\n\n"
                         "• SMA(10,20,50)\n• EMA(12,26)\n• Bollinger Bands")

    def add_momentum_indicators(self):
        """Fügt Momentum-Indikator-Set hinzu"""
        indicators = CONFIG.INDICATOR_SETS['momentum']

        for indicator_config in indicators:
            self.add_indicator_to_state(
                indicator_config["library"],
                indicator_config["name"],
                indicator_config["params"]
            )

        UIUtils.show_info("Momentum-Set",
                         f"⚡ {len(indicators)} Momentum-Indikatoren hinzugefügt!\n\n"
                         "• RSI(14)\n• MACD(12,26,9)\n• Stochastic\n• ADX(14)")

    def add_all_indicators_test(self):
        """Fügt ALLE verfügbaren Indikatoren hinzu (OHNE Test-Modus Popup)"""
        # DIREKT HINZUFÜGEN OHNE POPUP
        total_indicators = sum(len(indicators) for indicators in self.all_indicators.values())
        print(f"📊 Füge {total_indicators} Indikatoren hinzu...")

        # Alle Indikatoren hinzufügen
        added_count = 0
        errors = []

        try:
            for library, indicators in self.all_indicators.items():
                for name, info in indicators.items():
                    try:
                        # Standard-Parameter verwenden
                        params = {}
                        param_names = info.get("params", [])
                        defaults = info.get("defaults", [])

                        for param, default in zip(param_names, defaults):
                            params[param] = default

                        # Indikator hinzufügen
                        self.add_indicator_to_state(library, name, params)
                        added_count += 1

                        # Progress-Update alle 50 Indikatoren
                        if added_count % 50 == 0:
                            self.logger.info(f"Test-Modus: {added_count}/{total_indicators} Indikatoren hinzugefügt...")

                    except Exception as e:
                        error_msg = f"{library}.{name}: {str(e)}"
                        errors.append(error_msg)
                        self.logger.error(f"Fehler beim Hinzufügen von {library}.{name}: {e}")

            # NUR CONSOLE-OUTPUT (KEIN POPUP)
            print(f"✅ {added_count}/{total_indicators} Indikatoren hinzugefügt!")

            if errors:
                print(f"❌ {len(errors)} Fehler aufgetreten:")
                for error in errors[:5]:  # Nur erste 5 Fehler anzeigen
                    print(f"  • {error}")
                if len(errors) > 5:
                    print(f"  ... und {len(errors) - 5} weitere Fehler")
            else:
                print(f"🎉 Alle Indikatoren erfolgreich hinzugefügt!")

            self.logger.info(f"Alle Indikatoren hinzugefügt: {added_count} erfolgreich, {len(errors)} Fehler")

        except Exception as e:
            print(f"❌ Test-Modus Fehler: Unerwarteter Fehler beim Hinzufügen aller Indikatoren: {e}")
            self.logger.error(f"Test-Modus Fehler: {e}")

    def clear_all_indicators(self):
        """Löscht alle ausgewählten Indikatoren"""
        state = get_state()
        if not state.selected_indicators:
            print("ℹ️ Info: Keine Indikatoren zum Löschen vorhanden.")
            return

        # Direkt löschen ohne Popup
        state_manager.clear_indicators()
        print("🗑️ Alle Indikatoren wurden gelöscht!")

    def on_file_changed(self, event_data):
        """Wird aufgerufen wenn Datei geändert wird"""
        # Kontext-abhängige Updates könnten hier implementiert werden
        pass

    def on_timeframes_changed(self, event_data):
        """Wird aufgerufen wenn Timeframes geändert werden"""
        # Kontext-abhängige Updates könnten hier implementiert werden
        pass

    def get_tab_frame(self):
        """Gibt Tab-Frame zurück"""
        return self.tab_frame
