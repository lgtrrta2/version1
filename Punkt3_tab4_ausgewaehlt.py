# 📊 PUNKT 3: TAB 4 - AUSGEWÄHLTE INDIKATOREN
# Vierte Tab für Verwaltung der ausgewählten Indikatoren

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import logging
import os
from typing import Dict, List, Optional

from Punkt3_settings import CONFIG
from Punkt3_events import emit_indicators_changed, emit_status_changed, on, Events
from Punkt3_state_manager import state_manager, get_state
from Punkt3_utils import IndicatorUtils, UIUtils, FormatUtils, ScrollableFrame
from punkt3_indicators import get_all_indicators

class Tab4Ausgewaehlt:
    """Tab 4: Verwaltung ausgewählter Indikatoren"""

    def __init__(self, parent_notebook):
        self.notebook = parent_notebook
        self.logger = logging.getLogger(__name__)

        # Alle verfügbaren Indikatoren für Parameter-Validierung
        self.all_indicators = get_all_indicators()

        # Tab erstellen
        self.create_tab()

        # Event-Listener registrieren
        self.setup_event_listeners()

        # Initial laden
        self.update_display()

    def create_tab(self):
        """Erstellt Tab 4 GUI"""
        # Tab-Frame
        self.tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_frame, text="✅ 4. AUSGEWÄHLTE")

        # Scrollbares Frame erstellen
        self.scrollable = ScrollableFrame(self.tab_frame)
        self.scrollable.get_main_frame().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Container ist jetzt das scrollbare Frame
        container = self.scrollable.get_frame()

        # Padding hinzufügen
        container.configure(padding=CONFIG.GUI_CONFIG['tab_padding'])

        # 1. ÜBERSICHT SEKTION
        self.create_overview_section(container)

        # 2. INDIKATOR-LISTE
        self.create_indicator_list_section(container)

        # 3. AKTIONEN
        self.create_actions_section(container)

        # Grid-Konfiguration
        self.tab_frame.columnconfigure(0, weight=1)
        self.tab_frame.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

    def create_overview_section(self, parent):
        """Erstellt Übersicht-Sektion"""
        overview_frame = ttk.LabelFrame(parent, text="📊 ÜBERSICHT",
                                       padding=CONFIG.GUI_CONFIG['frame_padding'])
        overview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))

        # Statistiken-Container
        stats_container = ttk.Frame(overview_frame)
        stats_container.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Haupt-Statistik
        self.count_label = ttk.Label(stats_container, text="0 Indikatoren ausgewählt",
                                    font=CONFIG.FONTS['heading'], foreground=CONFIG.COLORS['primary'])
        self.count_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Detail-Statistiken
        detail_frame = ttk.Frame(stats_container)
        detail_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Bibliothek-Verteilung
        ttk.Label(detail_frame, text="Bibliotheken:",
                 font=CONFIG.FONTS['normal']).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.library_stats_label = ttk.Label(detail_frame, text="Keine",
                                            font=CONFIG.FONTS['normal'], foreground=CONFIG.COLORS['info'])
        self.library_stats_label.grid(row=0, column=1, sticky=tk.W)

        # Kategorie-Verteilung
        ttk.Label(detail_frame, text="Kategorien:",
                 font=CONFIG.FONTS['normal']).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.category_stats_label = ttk.Label(detail_frame, text="Keine",
                                             font=CONFIG.FONTS['normal'], foreground=CONFIG.COLORS['info'])
        self.category_stats_label.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))

        # Performance-Hinweis
        self.performance_label = ttk.Label(overview_frame, text="",
                                          font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['warning'])
        self.performance_label.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))

        overview_frame.columnconfigure(0, weight=1)
        stats_container.columnconfigure(0, weight=1)

    def create_indicator_list_section(self, parent):
        """Erstellt Indikator-Liste Sektion"""
        list_frame = ttk.LabelFrame(parent, text="📋 AUSGEWÄHLTE INDIKATOREN",
                                   padding=CONFIG.GUI_CONFIG['frame_padding'])
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Treeview für ausgewählte Indikatoren
        tree_container = ttk.Frame(list_frame)
        tree_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Treeview mit Spalten
        columns = ('library', 'category', 'params', 'display')
        self.selected_tree = ttk.Treeview(tree_container, columns=columns,
                                         show='tree headings',
                                         height=CONFIG.GUI_CONFIG['treeview_height'])

        # Spalten konfigurieren
        self.selected_tree.heading('#0', text='Indikator')
        self.selected_tree.heading('library', text='Bibliothek')
        self.selected_tree.heading('category', text='Kategorie')
        self.selected_tree.heading('params', text='Parameter')
        self.selected_tree.heading('display', text='Anzeige-Name')

        # Spaltenbreiten
        UIUtils.configure_treeview_columns(self.selected_tree, {
            '#0': 150,
            'library': 100,
            'category': 100,
            'params': 200,
            'display': 180
        })

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical",
                                   command=self.selected_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal",
                                   command=self.selected_tree.xview)

        self.selected_tree.configure(yscrollcommand=v_scrollbar.set,
                                    xscrollcommand=h_scrollbar.set)

        # Grid-Layout für Treeview
        self.selected_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        # Event-Bindings
        self.selected_tree.bind('<Double-1>', self.edit_selected_indicator)
        self.selected_tree.bind('<Delete>', self.remove_selected_indicator)

        # Grid-Konfiguration
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

    def create_actions_section(self, parent):
        """Erstellt Aktionen-Sektion"""
        actions_frame = ttk.LabelFrame(parent, text="🔧 AKTIONEN",
                                      padding=CONFIG.GUI_CONFIG['frame_padding'])
        actions_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(20, 0))

        # Button-Container
        button_container = ttk.Frame(actions_frame)
        button_container.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Erste Reihe: Bearbeitung
        edit_frame = ttk.Frame(button_container)
        edit_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(edit_frame, text="🔧 PARAMETER BEARBEITEN",
                  command=self.edit_selected_indicator,
                  width=20).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(edit_frame, text="📋 DUPLIZIEREN",
                  command=self.duplicate_indicator,
                  width=15).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(edit_frame, text="↕️ REIHENFOLGE",
                  command=self.change_order,
                  width=15).grid(row=0, column=2)

        # Zweite Reihe: Verwaltung
        manage_frame = ttk.Frame(button_container)
        manage_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(manage_frame, text="❌ ENTFERNEN",
                  command=self.remove_selected_indicator,
                  width=15).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(manage_frame, text="🗑️ ALLE LÖSCHEN",
                  command=self.clear_all_indicators,
                  width=15).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(manage_frame, text="🔄 ZURÜCKSETZEN",
                  command=self.reset_to_defaults,
                  width=15).grid(row=0, column=2)

        # Dritte Reihe: Import/Export
        io_frame = ttk.Frame(button_container)
        io_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

        ttk.Button(io_frame, text="📥 IMPORTIEREN",
                  command=self.import_indicators,
                  width=15).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(io_frame, text="📤 EXPORTIEREN",
                  command=self.export_indicators,
                  width=15).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(io_frame, text="💾 ALS PRESET SPEICHERN",
                  command=self.save_as_preset,
                  width=20).grid(row=0, column=2)

        # Hilfe-Text
        help_label = ttk.Label(actions_frame,
                              text="💡 Doppelklick zum Bearbeiten | Entf-Taste zum Löschen",
                              font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['info'])
        help_label.grid(row=1, column=0, sticky=tk.W, pady=(15, 0))

        actions_frame.columnconfigure(0, weight=1)
        button_container.columnconfigure(0, weight=1)

    def setup_event_listeners(self):
        """Registriert Event-Listener"""
        # Lausche auf Indikator-Änderungen
        on(Events.INDICATORS_CHANGED, self.on_indicators_changed)

    def update_display(self):
        """Aktualisiert die komplette Anzeige"""
        state = get_state()
        indicators = state.selected_indicators or []

        # Übersicht aktualisieren
        self.update_overview(indicators)

        # Liste aktualisieren
        self.update_indicator_list(indicators)

    def update_overview(self, indicators: List[Dict]):
        """Aktualisiert Übersicht-Sektion"""
        count = len(indicators)

        # Haupt-Count
        if count == 0:
            self.count_label.config(text="Keine Indikatoren ausgewählt",
                                   foreground=CONFIG.COLORS['info'])
        elif count == 1:
            self.count_label.config(text="1 Indikator ausgewählt",
                                   foreground=CONFIG.COLORS['success'])
        else:
            self.count_label.config(text=f"{count} Indikatoren ausgewählt",
                                   foreground=CONFIG.COLORS['primary'])

        if not indicators:
            self.library_stats_label.config(text="Keine")
            self.category_stats_label.config(text="Keine")
            self.performance_label.config(text="")
            return

        # Bibliothek-Statistiken
        library_counts = {}
        category_counts = {}

        for indicator in indicators:
            lib = indicator.get('library', 'Unbekannt')
            cat = indicator.get('category', 'Unbekannt')

            library_counts[lib] = library_counts.get(lib, 0) + 1
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Top 3 Bibliotheken
        top_libs = sorted(library_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        lib_text = ", ".join([f"{lib}({count})" for lib, count in top_libs])
        if len(library_counts) > 3:
            lib_text += f" +{len(library_counts)-3} weitere"
        self.library_stats_label.config(text=lib_text)

        # Top 3 Kategorien
        top_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        cat_text = ", ".join([f"{cat}({count})" for cat, count in top_cats])
        if len(category_counts) > 3:
            cat_text += f" +{len(category_counts)-3} weitere"
        self.category_stats_label.config(text=cat_text)

        # Performance-Hinweis
        if count > 20:
            self.performance_label.config(text="⚠️ Viele Indikatoren können die Performance beeinträchtigen")
        elif count > 10:
            self.performance_label.config(text="💡 Mittlere Anzahl Indikatoren - gute Balance")
        else:
            self.performance_label.config(text="✅ Optimale Anzahl für beste Performance")

    def update_indicator_list(self, indicators: List[Dict]):
        """Aktualisiert Indikator-Liste"""
        # Treeview leeren
        for item in self.selected_tree.get_children():
            self.selected_tree.delete(item)

        # Indikatoren hinzufügen
        for i, indicator in enumerate(indicators):
            name = indicator.get('name', 'Unbekannt')
            library = indicator.get('library', 'Unbekannt')
            params = indicator.get('params', {})
            display_name = indicator.get('display_name', name)

            # Kategorie aus all_indicators holen
            category = "Unbekannt"
            if library in self.all_indicators and name in self.all_indicators[library]:
                category = self.all_indicators[library][name].get('category', 'Unbekannt')

            # Parameter-String
            if params:
                param_str = ", ".join([f"{k}={v}" for k, v in params.items()])
            else:
                param_str = "Keine Parameter"

            # Item hinzufügen
            item_id = self.selected_tree.insert('', 'end', text=f"{i+1}. {name}",
                                               values=(library, category, param_str, display_name))

            # Farbe basierend auf Bibliothek
            if library == 'talib':
                self.selected_tree.set(item_id, 'library', f"📊 {library}")
            elif library == 'pandas_ta':
                self.selected_tree.set(item_id, 'library', f"🐼 {library}")
            elif library == 'vbt':
                self.selected_tree.set(item_id, 'library', f"⚡ {library}")
            else:
                self.selected_tree.set(item_id, 'library', f"📈 {library}")

    def on_indicators_changed(self, event_data):
        """Wird aufgerufen wenn Indikatoren geändert werden"""
        self.update_display()

    def edit_selected_indicator(self, event=None):
        """Bearbeitet ausgewählten Indikator"""
        selection = self.selected_tree.selection()
        if not selection:
            UIUtils.show_warning("Warnung", "Bitte wählen Sie einen Indikator zum Bearbeiten aus!")
            return

        # Index ermitteln
        item_index = self.selected_tree.index(selection[0])
        state = get_state()

        if item_index >= len(state.selected_indicators):
            UIUtils.show_error("Fehler", "Ungültiger Indikator-Index!")
            return

        indicator = state.selected_indicators[item_index]
        library = indicator['library']
        name = indicator['name']

        # Parameter-Dialog öffnen
        if library in self.all_indicators and name in self.all_indicators[library]:
            indicator_info = self.all_indicators[library][name]
            new_params = self.show_parameter_dialog(name, library, indicator_info, indicator['params'])

            if new_params is not None:
                # Display-Name aktualisieren
                new_display_name = IndicatorUtils.create_display_name(name, new_params)

                # Indikator aktualisieren
                updated_indicator = indicator.copy()
                updated_indicator['params'] = new_params
                updated_indicator['display_name'] = new_display_name

                state_manager.update_indicator(item_index, updated_indicator)

                UIUtils.show_info("Aktualisiert", f"✅ Parameter für {new_display_name} aktualisiert!")

    def show_parameter_dialog(self, name: str, library: str, indicator_info: Dict, current_params: Dict) -> Optional[Dict]:
        """Zeigt Parameter-Dialog mit aktuellen Werten"""
        param_names = indicator_info.get("params", [])
        defaults = indicator_info.get("defaults", [])

        if not param_names:
            UIUtils.show_info("Info", f"{name} hat keine konfigurierbaren Parameter.")
            return None

        # Dialog erstellen
        dialog = tk.Toplevel(self.tab_frame)
        dialog.title(f"Parameter bearbeiten: {library}.{name}")
        dialog.geometry("500x450")
        dialog.transient(self.tab_frame)
        dialog.grab_set()

        # Dialog zentrieren
        UIUtils.center_window(dialog, 500, 450)

        # Hauptframe
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Titel
        title_label = ttk.Label(main_frame, text=f"Parameter für {name}",
                               font=CONFIG.FONTS['heading'])
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Header
        ttk.Label(main_frame, text="Parameter", font=CONFIG.FONTS['normal']).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(main_frame, text="Aktuell", font=CONFIG.FONTS['normal']).grid(row=1, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Label(main_frame, text="Standard", font=CONFIG.FONTS['normal']).grid(row=1, column=2, sticky=tk.W)

        # Parameter-Eingaben
        param_vars = {}
        for i, (param, default) in enumerate(zip(param_names, defaults)):
            row = i + 2

            # Parameter-Name
            ttk.Label(main_frame, text=f"{param}:",
                     font=CONFIG.FONTS['normal']).grid(row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10))

            # Aktueller Wert
            current_value = current_params.get(param, default)
            var = tk.StringVar(value=str(current_value))
            entry = ttk.Entry(main_frame, textvariable=var, width=15)
            entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
            param_vars[param] = var

            # Standard-Wert (nur Anzeige)
            ttk.Label(main_frame, text=str(default),
                     font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['info']).grid(row=row, column=2, sticky=tk.W, pady=5)

        # Ergebnis-Variable
        result = {'params': None}

        # Button-Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(param_names)+3, column=0, columnspan=3, pady=(20, 0))

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

        def reset_clicked():
            # Auf Standard-Werte zurücksetzen
            for param, default in zip(param_names, defaults):
                if param in param_vars:
                    param_vars[param].set(str(default))

        def cancel_clicked():
            dialog.destroy()

        ttk.Button(button_frame, text="✅ OK", command=ok_clicked).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="🔄 Standard", command=reset_clicked).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Abbrechen", command=cancel_clicked).grid(row=0, column=2)

        # Grid-Konfiguration
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Warten auf Dialog-Schließung
        dialog.wait_window()

        return result['params']

    def duplicate_indicator(self):
        """Dupliziert ausgewählten Indikator"""
        selection = self.selected_tree.selection()
        if not selection:
            UIUtils.show_warning("Warnung", "Bitte wählen Sie einen Indikator zum Duplizieren aus!")
            return

        # Index ermitteln
        item_index = self.selected_tree.index(selection[0])
        state = get_state()

        if item_index >= len(state.selected_indicators):
            return

        # Indikator kopieren
        original = state.selected_indicators[item_index]
        duplicate = original.copy()
        duplicate['params'] = original['params'].copy()
        duplicate['display_name'] = f"{original['display_name']} (Kopie)"

        # Hinzufügen
        state_manager.add_indicator(duplicate)

        UIUtils.show_info("Dupliziert", f"✅ {original['display_name']} wurde dupliziert!")

    def change_order(self):
        """Ändert Reihenfolge der Indikatoren"""
        state = get_state()
        indicators = state.selected_indicators

        if len(indicators) < 2:
            UIUtils.show_info("Info", "Mindestens 2 Indikatoren erforderlich für Reihenfolge-Änderung.")
            return

        # Einfacher Dialog für Reihenfolge
        dialog = tk.Toplevel(self.tab_frame)
        dialog.title("Reihenfolge ändern")
        dialog.geometry("400x500")
        dialog.transient(self.tab_frame)
        dialog.grab_set()

        UIUtils.center_window(dialog, 400, 500)

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(main_frame, text="Reihenfolge der Indikatoren:",
                 font=CONFIG.FONTS['heading']).grid(row=0, column=0, pady=(0, 15))

        # Listbox für Reihenfolge
        listbox_frame = ttk.Frame(main_frame)
        listbox_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        order_listbox = tk.Listbox(listbox_frame, height=15)
        order_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=order_listbox.yview)
        order_listbox.configure(yscrollcommand=order_scrollbar.set)

        order_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        order_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Indikatoren in Listbox laden
        for indicator in indicators:
            order_listbox.insert(tk.END, indicator['display_name'])

        # Buttons für Reihenfolge
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(15, 0))

        def move_up():
            selection = order_listbox.curselection()
            if selection and selection[0] > 0:
                idx = selection[0]
                # In Listbox verschieben
                item = order_listbox.get(idx)
                order_listbox.delete(idx)
                order_listbox.insert(idx-1, item)
                order_listbox.selection_set(idx-1)

        def move_down():
            selection = order_listbox.curselection()
            if selection and selection[0] < order_listbox.size()-1:
                idx = selection[0]
                # In Listbox verschieben
                item = order_listbox.get(idx)
                order_listbox.delete(idx)
                order_listbox.insert(idx+1, item)
                order_listbox.selection_set(idx+1)

        def apply_order():
            # Neue Reihenfolge anwenden
            new_order = []
            for i in range(order_listbox.size()):
                display_name = order_listbox.get(i)
                # Finde entsprechenden Indikator
                for indicator in indicators:
                    if indicator['display_name'] == display_name:
                        new_order.append(indicator)
                        break

            # State aktualisieren
            state_manager.update_state(selected_indicators=new_order)
            dialog.destroy()
            UIUtils.show_info("Reihenfolge", "✅ Reihenfolge wurde aktualisiert!")

        ttk.Button(button_frame, text="↑ Nach oben", command=move_up).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="↓ Nach unten", command=move_down).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="✅ Anwenden", command=apply_order).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Abbrechen", command=dialog.destroy).grid(row=0, column=3)

        # Grid-Konfiguration
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

    def remove_selected_indicator(self, event=None):
        """Entfernt ausgewählten Indikator"""
        selection = self.selected_tree.selection()
        if not selection:
            UIUtils.show_warning("Warnung", "Bitte wählen Sie einen Indikator zum Entfernen aus!")
            return

        # Index ermitteln
        item_index = self.selected_tree.index(selection[0])
        state = get_state()

        if item_index >= len(state.selected_indicators):
            return

        indicator = state.selected_indicators[item_index]

        if UIUtils.ask_yes_no("Bestätigen", f"Möchten Sie {indicator['display_name']} wirklich entfernen?"):
            state_manager.remove_indicator(item_index)
            UIUtils.show_info("Entfernt", f"❌ {indicator['display_name']} wurde entfernt!")

    def clear_all_indicators(self):
        """Löscht alle Indikatoren"""
        state = get_state()
        if not state.selected_indicators:
            UIUtils.show_info("Info", "Keine Indikatoren zum Löschen vorhanden.")
            return

        count = len(state.selected_indicators)
        if UIUtils.ask_yes_no("Bestätigen", f"Möchten Sie wirklich alle {count} Indikatoren löschen?"):
            state_manager.clear_indicators()
            UIUtils.show_info("Gelöscht", f"🗑️ Alle {count} Indikatoren wurden gelöscht!")

    def reset_to_defaults(self):
        """Setzt alle Parameter auf Standard-Werte zurück"""
        state = get_state()
        if not state.selected_indicators:
            UIUtils.show_info("Info", "Keine Indikatoren vorhanden.")
            return

        if not UIUtils.ask_yes_no("Bestätigen", "Möchten Sie alle Parameter auf Standard-Werte zurücksetzen?"):
            return

        updated_indicators = []
        for indicator in state.selected_indicators:
            library = indicator['library']
            name = indicator['name']

            # Standard-Parameter holen
            if library in self.all_indicators and name in self.all_indicators[library]:
                indicator_info = self.all_indicators[library][name]
                param_names = indicator_info.get("params", [])
                defaults = indicator_info.get("defaults", [])

                # Standard-Parameter setzen
                standard_params = {}
                for param, default in zip(param_names, defaults):
                    standard_params[param] = default

                # Indikator aktualisieren
                updated_indicator = indicator.copy()
                updated_indicator['params'] = standard_params
                updated_indicator['display_name'] = IndicatorUtils.create_display_name(name, standard_params)
                updated_indicators.append(updated_indicator)
            else:
                updated_indicators.append(indicator)

        # State aktualisieren
        state_manager.update_state(selected_indicators=updated_indicators)
        UIUtils.show_info("Zurückgesetzt", "🔄 Alle Parameter wurden auf Standard-Werte zurückgesetzt!")

    def import_indicators(self):
        """Importiert Indikatoren aus Datei"""
        filename = filedialog.askopenfilename(
            title="Indikatoren importieren",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )

        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_indicators = json.load(f)

            if not isinstance(imported_indicators, list):
                UIUtils.show_error("Fehler", "Ungültiges Dateiformat. Erwartet wird eine Liste von Indikatoren.")
                return

            # Validierung
            valid_indicators = []
            for indicator in imported_indicators:
                if all(key in indicator for key in ['library', 'name', 'params']):
                    # Display-Name neu generieren
                    display_name = IndicatorUtils.create_display_name(indicator['name'], indicator['params'])
                    indicator['display_name'] = display_name
                    valid_indicators.append(indicator)

            if not valid_indicators:
                UIUtils.show_error("Fehler", "Keine gültigen Indikatoren in der Datei gefunden.")
                return

            # Hinzufügen oder ersetzen?
            if UIUtils.ask_yes_no("Import-Modus",
                                 f"{len(valid_indicators)} Indikatoren gefunden.\n\n"
                                 "Ja = Zu bestehenden hinzufügen\n"
                                 "Nein = Bestehende ersetzen"):
                # Hinzufügen
                for indicator in valid_indicators:
                    state_manager.add_indicator(indicator)
            else:
                # Ersetzen
                state_manager.update_state(selected_indicators=valid_indicators)

            UIUtils.show_info("Importiert", f"✅ {len(valid_indicators)} Indikatoren erfolgreich importiert!")

        except Exception as e:
            UIUtils.show_error("Import-Fehler", f"Fehler beim Importieren:\n{e}")

    def export_indicators(self):
        """Exportiert Indikatoren in Datei"""
        state = get_state()
        if not state.selected_indicators:
            UIUtils.show_warning("Warnung", "Keine Indikatoren zum Exportieren vorhanden!")
            return

        filename = filedialog.asksaveasfilename(
            title="Indikatoren exportieren",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ],
            initialfilename=f"punkt3_indikatoren_{CONFIG.get_timestamp()}.json"
        )

        if not filename:
            return

        try:
            # Export-Daten vorbereiten
            export_data = []
            for indicator in state.selected_indicators:
                export_indicator = {
                    'library': indicator['library'],
                    'name': indicator['name'],
                    'params': indicator['params'],
                    'display_name': indicator['display_name']
                }
                export_data.append(export_indicator)

            # Datei schreiben
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            UIUtils.show_info("Exportiert",
                             f"✅ {len(export_data)} Indikatoren erfolgreich exportiert!\n\n"
                             f"Datei: {filename}")

        except Exception as e:
            UIUtils.show_error("Export-Fehler", f"Fehler beim Exportieren:\n{e}")

    def save_as_preset(self):
        """Speichert aktuelle Auswahl als Preset"""
        state = get_state()
        if not state.selected_indicators:
            UIUtils.show_warning("Warnung", "Keine Indikatoren zum Speichern vorhanden!")
            return

        # Preset-Name abfragen
        preset_name = simpledialog.askstring(
            "Preset speichern",
            "Geben Sie einen Namen für das Preset ein:",
            initialvalue=f"Preset_{CONFIG.get_timestamp()}"
        )

        if not preset_name:
            return

        # Preset-Datei speichern
        preset_dir = "presets"
        os.makedirs(preset_dir, exist_ok=True)

        preset_filename = os.path.join(preset_dir, f"{preset_name}.json")

        try:
            preset_data = {
                'name': preset_name,
                'created_at': CONFIG.get_timestamp(),
                'indicator_count': len(state.selected_indicators),
                'indicators': state.selected_indicators
            }

            with open(preset_filename, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=2, ensure_ascii=False)

            UIUtils.show_info("Preset gespeichert",
                             f"✅ Preset '{preset_name}' erfolgreich gespeichert!\n\n"
                             f"Datei: {preset_filename}\n"
                             f"Indikatoren: {len(state.selected_indicators)}")

        except Exception as e:
            UIUtils.show_error("Preset-Fehler", f"Fehler beim Speichern des Presets:\n{e}")

    def get_tab_frame(self):
        """Gibt Tab-Frame zurück"""
        return self.tab_frame
