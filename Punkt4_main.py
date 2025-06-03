#!/usr/bin/env python3
# 📊 PUNKT 4: PARAMETER-KONFIGURATOR - HAUPTANWENDUNG
# VectorBT Pro Parameter-Konfigurator für Trading-Strategien

import tkinter as tk
from tkinter import ttk
import sys
import logging
from pathlib import Path

# Punkt 4 Module importieren
from Punkt4_settings import CONFIG
from Punkt4_events import emit, on, Events, setup_event_logging
from Punkt4_state_manager import state_manager
from Punkt4_tab1_datei_export import Tab1DateiExport
from Punkt4_tab2_essential import Tab2Essential

class Punkt4Main:
    """Hauptanwendung für Punkt 4 Parameter-Konfigurator"""
    
    def __init__(self):
        self.logger = self.setup_logging()
        self.logger.info("🚀 Punkt 4 Parameter-Konfigurator wird gestartet...")
        
        # Tkinter Setup
        self.root = tk.Tk()
        self.setup_window()
        
        # Tab-Instanzen
        self.tabs = {}
        
        # UI erstellen
        self.create_ui()
        self.setup_events()
        
        # Initial State
        self.update_title()
        
        self.logger.info("✅ Punkt 4 Parameter-Konfigurator bereit")
    
    def setup_logging(self):
        """Logging konfigurieren"""
        # Logs Verzeichnis erstellen
        CONFIG.PATHS['logs'].mkdir(exist_ok=True)
        
        # Logger konfigurieren
        logger = logging.getLogger('Punkt4')
        logger.setLevel(logging.INFO)
        
        # File Handler
        file_handler = logging.FileHandler(
            CONFIG.PATHS['logs'] / 'punkt4.log',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Handler hinzufügen
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def setup_window(self):
        """Hauptfenster konfigurieren"""
        self.root.title(CONFIG.APP['title'])
        self.root.geometry(CONFIG.APP['geometry'])
        self.root.minsize(*CONFIG.APP['min_size'])
        
        # Icon setzen (falls vorhanden)
        if CONFIG.APP['icon_path'] and Path(CONFIG.APP['icon_path']).exists():
            self.root.iconbitmap(CONFIG.APP['icon_path'])
        
        # Window Close Event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Style konfigurieren
        self.style = ttk.Style()
        if CONFIG.APP['theme'] != 'default':
            try:
                self.style.theme_use(CONFIG.APP['theme'])
            except tk.TclError:
                self.logger.warning(f"Theme '{CONFIG.APP['theme']}' nicht verfügbar")
    
    def create_ui(self):
        """Benutzeroberfläche erstellen"""
        # Main Container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header
        self.create_header()
        
        # Notebook (Tabs)
        self.create_notebook()
        
        # Status Bar
        self.create_status_bar()
    
    def create_header(self):
        """Header-Bereich erstellen"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="📊 PUNKT 4: PARAMETER-KONFIGURATOR",
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Version Info
        version_label = ttk.Label(header_frame,
                                 text=f"v{CONFIG.APP['version']} | VectorBT Pro Optimiert",
                                 font=('TkDefaultFont', 9),
                                 foreground='gray')
        version_label.pack(side=tk.RIGHT)
        
        # Separator
        separator = ttk.Separator(header_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(10, 0))
    
    def create_notebook(self):
        """Notebook mit Tabs erstellen"""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Datei & Export
        tab1_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab1_frame, text="📁 Datei & Export")
        self.tabs['tab1'] = Tab1DateiExport(tab1_frame)
        
        # Tab 2: Essential Parameters
        tab2_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab2_frame, text="⚙️ Essential Parameters")
        self.tabs['tab2'] = Tab2Essential(tab2_frame)
        
        # Tab 3: Advanced Parameters (Platzhalter)
        tab3_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab3_frame, text="🔧 Advanced")
        ttk.Label(tab3_frame, text="🚧 Advanced Parameter (Coming Soon)",
                 font=('TkDefaultFont', 12)).pack(expand=True)
        
        # Tab 4: Professional Parameters (Platzhalter)
        tab4_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab4_frame, text="🏆 Professional")
        ttk.Label(tab4_frame, text="🚧 Professional Features (Coming Soon)",
                 font=('TkDefaultFont', 12)).pack(expand=True)
        
        # Tab Change Event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def create_status_bar(self):
        """Status-Bar erstellen"""
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        # Status Label
        self.status_var = tk.StringVar(value="Bereit für Parameter-Konfiguration")
        self.status_label = ttk.Label(self.status_frame, 
                                     textvariable=self.status_var,
                                     relief=tk.SUNKEN, 
                                     anchor=tk.W,
                                     font=('TkDefaultFont', 9))
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # VBT Status
        self.vbt_status_label = ttk.Label(self.status_frame,
                                         text="🚀 VBT Pro",
                                         foreground='green',
                                         font=('TkDefaultFont', 9))
        self.vbt_status_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Dirty State Indicator
        self.dirty_label = ttk.Label(self.status_frame,
                                    text="",
                                    foreground='orange',
                                    font=('TkDefaultFont', 9))
        self.dirty_label.pack(side=tk.RIGHT, padx=(10, 0))
    
    def setup_events(self):
        """Event-Handler registrieren"""
        def on_status_changed(data):
            message = data.get('message', '')
            level = data.get('level', 'info')

            if level == 'error':
                self.status_var.set(f"❌ {message}")
            elif level == 'warning':
                self.status_var.set(f"⚠️ {message}")
            elif level == 'success':
                self.status_var.set(f"✅ {message}")
            else:
                self.status_var.set(f"ℹ️ {message}")

        def on_parameter_changed(data):
            self.update_dirty_state()
            self.update_title()

        def on_data_loaded(data):
            self.update_title()

        def on_export_completed(data):
            file_path = data.get('file_path', '')
            target = data.get('target', '')
            self.status_var.set(f"✅ Export erfolgreich: {Path(file_path).name}")

        def on_validation_passed(data):
            self.status_var.set("✅ Parameter-Validierung erfolgreich")

        def on_validation_failed(data):
            errors = data.get('errors', [])
            self.status_var.set(f"❌ Validierung fehlgeschlagen: {len(errors)} Fehler")

        # Event-Listener registrieren
        on(Events.STATUS_CHANGED, on_status_changed)
        on(Events.PARAMETER_CHANGED, on_parameter_changed)
        on(Events.PUNKT3_DATA_LOADED, on_data_loaded)
        on(Events.EXPORT_COMPLETED, on_export_completed)
        on(Events.VALIDATION_PASSED, on_validation_passed)
        on(Events.VALIDATION_FAILED, on_validation_failed)
    
    def on_tab_changed(self, event):
        """Tab-Wechsel behandeln"""
        try:
            current_tab = self.notebook.index(self.notebook.select())
            emit(Events.TAB_CHANGED, {'tab_index': current_tab}, 'Punkt4Main')
            
            # Tab-spezifische Aktionen
            if current_tab == 0:  # Tab 1
                self.status_var.set("📁 Datei & Export - Punkt 3 Daten auswählen")
            elif current_tab == 1:  # Tab 2
                self.status_var.set("⚙️ Essential Parameters - VBT Pro Parameter konfigurieren")
            elif current_tab == 2:  # Tab 3
                self.status_var.set("🔧 Advanced Parameters - Erweiterte Features (geplant)")
            elif current_tab == 3:  # Tab 4
                self.status_var.set("🏆 Professional Parameters - Portfolio-Optimierung (geplant)")
                
        except Exception as e:
            self.logger.error(f"Tab-Wechsel Fehler: {e}")
    
    def update_dirty_state(self):
        """Dirty State Anzeige aktualisieren"""
        if state_manager.is_dirty():
            self.dirty_label.config(text="● Ungespeichert")
        else:
            self.dirty_label.config(text="")
    
    def update_title(self):
        """Fenstertitel aktualisieren"""
        base_title = CONFIG.APP['title']
        
        # Punkt 3 Daten Info
        from Punkt4_state_manager import get_state
        data_loaded = get_state('punkt3.data_loaded')
        
        if data_loaded:
            metadata_file = get_state('punkt3.metadata_file')
            if metadata_file:
                filename = Path(metadata_file).stem
                base_title += f" - {filename}"
        
        # Dirty State
        if state_manager.is_dirty():
            base_title += " *"
        
        self.root.title(base_title)
    
    def on_closing(self):
        """Anwendung schließen"""
        try:
            # Prüfen ob ungespeicherte Änderungen vorhanden
            if state_manager.is_dirty():
                from tkinter import messagebox
                result = messagebox.askyesnocancel(
                    "Ungespeicherte Änderungen",
                    "Es gibt ungespeicherte Parameter-Änderungen.\n\n"
                    "Möchten Sie diese vor dem Schließen speichern?"
                )
                
                if result is None:  # Cancel
                    return
                elif result:  # Yes - Save
                    # TODO: Implementiere Auto-Save
                    pass
            
            self.logger.info("🔚 Punkt 4 Parameter-Konfigurator wird beendet")
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Schließen Fehler: {e}")
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Anwendung starten"""
        try:
            self.logger.info("🎯 Punkt 4 Parameter-Konfigurator gestartet")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("⌨️ Anwendung durch Benutzer unterbrochen")
        except Exception as e:
            self.logger.error(f"Anwendungs-Fehler: {e}")
            raise
        finally:
            self.logger.info("👋 Punkt 4 Parameter-Konfigurator beendet")

def main():
    """Hauptfunktion"""
    try:
        # Event-Logging aktivieren
        setup_event_logging()
        
        # Anwendung erstellen und starten
        app = Punkt4Main()
        app.run()
        
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
