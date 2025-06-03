# 📊 PUNKT 3: HAUPT-ANWENDUNG
# Modulare Tab-basierte GUI für VectorBT Pro Punkt 3 Konfigurator

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import logging
from typing import Dict, List, Optional

# Eigene Module importieren
from Punkt3_settings import CONFIG
from Punkt3_events import event_manager, emit_status_changed, on, Events
from Punkt3_state_manager import state_manager, get_state
from Punkt3_utils import UIUtils

# Tab-Module importieren
from Punkt3_tab1_datei_tf import Tab1DateiTimeframe
from Punkt3_tab2_visualisierung import Tab2Visualisierung
from Punkt3_tab3_indikator_wahl import Tab3IndikatorWahl
from Punkt3_tab4_ausgewaehlt import Tab4Ausgewaehlt
from Punkt3_tab5_code_export import Tab5CodeExport

class VectorBTPunkt3Main:
    """Haupt-Anwendung für VectorBT Pro Punkt 3 Konfigurator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Tkinter Root erstellen
        self.root = tk.Tk()
        self.setup_root_window()
        
        # Tab-Instanzen
        self.tabs = {}
        
        # GUI erstellen
        self.create_main_gui()
        
        # Event-Listener registrieren
        self.setup_event_listeners()
        
        # Initialisierung abschließen
        self.finalize_initialization()
    
    def setup_root_window(self):
        """Konfiguriert das Haupt-Fenster"""
        # Titel und Icon
        self.root.title(CONFIG.APP_TITLE)
        
        # Fenster-Größe und Position
        self.root.geometry(f"{CONFIG.WINDOW_WIDTH}x{CONFIG.WINDOW_HEIGHT}")
        self.root.minsize(CONFIG.WINDOW_MIN_WIDTH, CONFIG.WINDOW_MIN_HEIGHT)
        
        # Fenster zentrieren
        UIUtils.center_window(self.root, CONFIG.WINDOW_WIDTH, CONFIG.WINDOW_HEIGHT)
        
        # Maximieren für bessere Übersicht
        self.root.state('zoomed')
        
        # Hintergrundfarbe
        self.root.configure(bg=CONFIG.COLORS['background'])
        
        # Schließen-Event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Style konfigurieren
        self.setup_styles()
    
    def setup_styles(self):
        """Konfiguriert TTK-Styles"""
        style = ttk.Style()
        
        # Theme setzen
        try:
            style.theme_use('clam')  # Modernes Theme
        except:
            style.theme_use('default')
        
        # Custom Styles
        style.configure('Accent.TButton', 
                       font=CONFIG.FONTS['heading'],
                       foreground=CONFIG.COLORS['primary'])
        
        style.configure('Title.TLabel',
                       font=CONFIG.FONTS['title'],
                       foreground=CONFIG.COLORS['primary'])
        
        style.configure('Heading.TLabel',
                       font=CONFIG.FONTS['heading'],
                       foreground=CONFIG.COLORS['secondary'])
    
    def create_main_gui(self):
        """Erstellt die Haupt-GUI"""
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header erstellen
        self.create_header(main_frame)
        
        # Tab-Notebook erstellen
        self.create_tab_notebook(main_frame)
        
        # Status-Bar erstellen
        self.create_status_bar(main_frame)
        
        # Grid-Konfiguration für responsive Design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def create_header(self, parent):
        """Erstellt Header-Bereich"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Titel
        title_label = ttk.Label(header_frame, text=CONFIG.APP_TITLE, style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Version und Info
        info_frame = ttk.Frame(header_frame)
        info_frame.grid(row=0, column=1, sticky=tk.E)
        
        version_label = ttk.Label(info_frame, text=f"Version {CONFIG.APP_VERSION}", 
                                 font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['info'])
        version_label.grid(row=0, column=0, padx=(0, 20))
        
        # Hilfe-Button
        ttk.Button(info_frame, text="❓ Hilfe", command=self.show_help, width=8).grid(row=0, column=1, padx=(0, 10))
        
        # Über-Button
        ttk.Button(info_frame, text="ℹ️ Über", command=self.show_about, width=8).grid(row=0, column=2)
        
        header_frame.columnconfigure(1, weight=1)
    
    def create_tab_notebook(self, parent):
        """Erstellt Tab-Notebook mit allen Tabs"""
        # Notebook erstellen
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tabs erstellen und hinzufügen
        self.create_all_tabs()
        
        # Tab-Change Event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def create_all_tabs(self):
        """Erstellt alle Tab-Instanzen"""
        try:
            # Tab 1: Datei & Timeframes
            self.logger.info("Erstelle Tab 1: Datei & Timeframes")
            self.tabs['tab1'] = Tab1DateiTimeframe(self.notebook)
            
            # Tab 2: Visualisierung
            self.logger.info("Erstelle Tab 2: Visualisierung")
            self.tabs['tab2'] = Tab2Visualisierung(self.notebook)
            
            # Tab 3: Indikator-Auswahl
            self.logger.info("Erstelle Tab 3: Indikator-Auswahl")
            self.tabs['tab3'] = Tab3IndikatorWahl(self.notebook)
            
            # Tab 4: Ausgewählte Indikatoren
            self.logger.info("Erstelle Tab 4: Ausgewählte Indikatoren")
            self.tabs['tab4'] = Tab4Ausgewaehlt(self.notebook)
            
            # Tab 5: Code & Export
            self.logger.info("Erstelle Tab 5: Code & Export")
            self.tabs['tab5'] = Tab5CodeExport(self.notebook)
            
            self.logger.info("Alle Tabs erfolgreich erstellt")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Tabs: {e}")
            messagebox.showerror("Initialisierung fehlgeschlagen", 
                               f"Fehler beim Erstellen der Tabs:\n\n{e}")
            sys.exit(1)
    
    def create_status_bar(self, parent):
        """Erstellt Status-Bar am unteren Rand"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Separator
        separator = ttk.Separator(status_frame, orient='horizontal')
        separator.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status-Container
        status_container = ttk.Frame(status_frame)
        status_container.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Status-Label (links)
        self.status_label = ttk.Label(status_container, text="⏳ Anwendung gestartet", 
                                     font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['success'])
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Fortschritt-Anzeige (mitte)
        self.progress_frame = ttk.Frame(status_container)
        self.progress_frame.grid(row=0, column=1, padx=(20, 20))
        
        # Workflow-Indikatoren
        workflow_steps = [
            ("1️⃣", "Datei"),
            ("2️⃣", "Visualisierung"), 
            ("3️⃣", "Indikatoren"),
            ("4️⃣", "Verwaltung"),
            ("5️⃣", "Export")
        ]
        
        self.workflow_labels = {}
        for i, (icon, name) in enumerate(workflow_steps):
            label = ttk.Label(self.progress_frame, text=f"{icon} {name}", 
                             font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['info'])
            label.grid(row=0, column=i, padx=(0, 15))
            self.workflow_labels[f"step{i+1}"] = label
        
        # Info-Label (rechts)
        self.info_label = ttk.Label(status_container, text="📊 Bereit für Konfiguration", 
                                   font=CONFIG.FONTS['small'], foreground=CONFIG.COLORS['info'])
        self.info_label.grid(row=0, column=2, sticky=tk.E)
        
        # Grid-Konfiguration
        status_frame.columnconfigure(0, weight=1)
        status_container.columnconfigure(1, weight=1)
    
    def setup_event_listeners(self):
        """Registriert globale Event-Listener"""
        # Status-Änderungen
        on(Events.STATUS_CHANGED, self.on_status_changed)
        
        # Workflow-Updates
        on(Events.FILE_SELECTED, self.on_workflow_update)
        on(Events.TIMEFRAMES_CHANGED, self.on_workflow_update)
        on(Events.INDICATORS_CHANGED, self.on_workflow_update)
        on(Events.VISUALIZATION_CHANGED, self.on_workflow_update)
        on(Events.CODE_GENERATED, self.on_workflow_update)
    
    def finalize_initialization(self):
        """Schließt Initialisierung ab"""
        try:
            # Konfiguration validieren
            errors = CONFIG.validate_config()
            if errors:
                self.logger.warning(f"Konfigurationsprobleme: {errors}")
            
            # Standard-Tab aktivieren
            self.notebook.select(0)
            
            # Status aktualisieren
            emit_status_changed("main", "initialized", "Anwendung erfolgreich gestartet", "success")
            
            self.logger.info("Punkt 3 Konfigurator erfolgreich initialisiert")
            
        except Exception as e:
            self.logger.error(f"Fehler bei Finalisierung: {e}")
            messagebox.showerror("Initialisierung", f"Warnung bei Initialisierung:\n{e}")
    
    def on_tab_changed(self, event=None):
        """Wird aufgerufen wenn Tab gewechselt wird"""
        try:
            current_tab = self.notebook.index(self.notebook.select())
            tab_names = ["Datei & Timeframes", "Visualisierung", "Indikator-Auswahl", 
                        "Ausgewählte Indikatoren", "Code & Export"]
            
            if 0 <= current_tab < len(tab_names):
                tab_name = tab_names[current_tab]
                self.info_label.config(text=f"📋 Aktuell: {tab_name}")
                
                # Workflow-Schritt hervorheben
                self.update_workflow_highlight(current_tab + 1)
                
                self.logger.debug(f"Tab gewechselt zu: {tab_name}")
        
        except Exception as e:
            self.logger.error(f"Fehler bei Tab-Wechsel: {e}")
    
    def update_workflow_highlight(self, step: int):
        """Aktualisiert Workflow-Hervorhebung"""
        for i in range(1, 6):
            label = self.workflow_labels[f"step{i}"]
            if i == step:
                label.config(foreground=CONFIG.COLORS['primary'])
            elif i < step:
                label.config(foreground=CONFIG.COLORS['success'])
            else:
                label.config(foreground=CONFIG.COLORS['info'])
    
    def on_status_changed(self, event_data):
        """Wird aufgerufen bei Status-Änderungen"""
        try:
            if hasattr(event_data, 'message'):
                message = event_data.message
                level = getattr(event_data, 'level', 'info')
                
                # Farbe basierend auf Level
                color_map = {
                    'info': CONFIG.COLORS['info'],
                    'success': CONFIG.COLORS['success'],
                    'warning': CONFIG.COLORS['warning'],
                    'error': CONFIG.COLORS['error']
                }
                
                color = color_map.get(level, CONFIG.COLORS['info'])
                self.status_label.config(text=f"📊 {message}", foreground=color)
        
        except Exception as e:
            self.logger.error(f"Fehler bei Status-Update: {e}")
    
    def on_workflow_update(self, event_data=None):
        """Wird aufgerufen bei Workflow-Updates"""
        try:
            state = get_state()
            
            # Workflow-Fortschritt berechnen
            progress = 0
            
            if state.selected_file_path:
                progress += 1
                self.workflow_labels["step1"].config(foreground=CONFIG.COLORS['success'])
            
            if state.visualization_mode:
                progress += 1
                self.workflow_labels["step2"].config(foreground=CONFIG.COLORS['success'])
            
            if state.selected_indicators:
                progress += 1
                self.workflow_labels["step3"].config(foreground=CONFIG.COLORS['success'])
                self.workflow_labels["step4"].config(foreground=CONFIG.COLORS['success'])
            
            if state.generated_code:
                progress += 1
                self.workflow_labels["step5"].config(foreground=CONFIG.COLORS['success'])
            
            # Info-Label aktualisieren
            ready, message = state_manager.is_ready_for_generation()
            if ready:
                self.info_label.config(text="✅ Bereit für Code-Generierung", 
                                      foreground=CONFIG.COLORS['success'])
            else:
                self.info_label.config(text=f"⚠️ {message}", 
                                      foreground=CONFIG.COLORS['warning'])
        
        except Exception as e:
            self.logger.error(f"Fehler bei Workflow-Update: {e}")
    
    def show_help(self):
        """Zeigt Hilfe-Dialog"""
        help_text = f"""
📊 VECTORBT PRO - PUNKT 3 KONFIGURATOR

🎯 ZWECK:
Erstellt erweiterte Multi-Timeframe Datenanalysen mit Indikatoren
für die Verwendung in Punkt 4 (Strategie-Entwicklung).

📋 WORKFLOW:
1️⃣ DATEI & TIMEFRAMES: Punkt 2 Datei auswählen und Timeframes konfigurieren
2️⃣ VISUALISIERUNG: Chart-Typ und Zeitraum für Darstellung wählen  
3️⃣ INDIKATOR-AUSWAHL: Aus 551 Indikatoren aus 8 Bibliotheken wählen
4️⃣ VERWALTUNG: Ausgewählte Indikatoren bearbeiten und verwalten
5️⃣ CODE & EXPORT: Python-Code generieren und exportieren

🔧 FEATURES:
• 551 Indikatoren aus 8 Bibliotheken (TA-Lib, Pandas-TA, VBT, etc.)
• Single & Multi-Timeframe Unterstützung
• Interaktive Charts mit Plotly
• Automatischer Export nach Punkt 4
• Intelligente Backups
• Parameter-Anpassung pro Indikator

💡 TIPPS:
• Verwenden Sie Quick-Sets für schnellen Start
• Weniger Indikatoren = Bessere Performance
• Multi-Timeframe für komplexe Strategien
• Backup-Option für Sicherheit aktivieren

📞 SUPPORT:
Bei Problemen prüfen Sie die Logs oder kontaktieren Sie den Support.
        """
        
        UIUtils.show_info("Hilfe - Punkt 3 Konfigurator", help_text)
    
    def show_about(self):
        """Zeigt Über-Dialog"""
        about_text = f"""
📊 VECTORBT PRO - PUNKT 3 KONFIGURATOR

Version: {CONFIG.APP_VERSION}
Entwickelt für: VectorBT Pro Workflow

🏗️ ARCHITEKTUR:
• Modulares Tab-Design
• Event-basierte Kommunikation
• Zentrales State Management
• Umfassende Fehlerbehandlung

📚 BIBLIOTHEKEN:
• TA-Lib: 158 Indikatoren
• Pandas-TA: 132 Indikatoren  
• VectorBT: 36 Indikatoren
• Technical: 70 Indikatoren
• TA: 43 Indikatoren
• Smart Money Concepts: 8 Indikatoren
• WQA101: 101 Indikatoren
• TechCon: 3 Indikatoren

GESAMT: 551 Indikatoren

🎯 ZWECK:
Brücke zwischen Punkt 2 (Multi-Timeframe Daten) 
und Punkt 4 (Strategie-Entwicklung)

© 2024 VectorBT Pro
        """
        
        print("ℹ️ Über - Punkt 3 Konfigurator:", about_text)
    
    def on_closing(self):
        """Wird aufgerufen beim Schließen der Anwendung"""
        try:
            # State speichern (optional)
            # Direkt beenden ohne Popup
            if True:
                
                # Cleanup
                event_manager.clear_all()
                
                # Logs schließen
                logging.shutdown()
                
                # Anwendung beenden
                self.root.destroy()
        
        except Exception as e:
            self.logger.error(f"Fehler beim Schließen: {e}")
            self.root.destroy()
    
    def run(self):
        """Startet die Anwendung"""
        try:
            self.logger.info("Starte Punkt 3 Konfigurator GUI")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Fehler beim Starten der GUI: {e}")
            messagebox.showerror("Kritischer Fehler", f"Anwendung konnte nicht gestartet werden:\n{e}")
            sys.exit(1)

def setup_logging():
    """Konfiguriert Logging"""
    logging.basicConfig(
        level=getattr(logging, CONFIG.LOGGING['level']),
        format=CONFIG.LOGGING['format'],
        handlers=[
            logging.FileHandler(CONFIG.LOGGING['file'], encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Haupt-Funktion"""
    try:
        # Logging konfigurieren
        setup_logging()
        
        # Anwendung erstellen und starten
        app = VectorBTPunkt3Main()
        app.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Anwendung durch Benutzer beendet")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
