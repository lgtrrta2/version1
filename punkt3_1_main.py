#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punkt3.1 - VectorbtPro Data Analyzer GUI
Hauptanwendung für die Analyse und Visualisierung von VectorbtPro-Daten

Autor: AI Assistant
Datum: 2025-06-02
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from pathlib import Path

# Lokale Imports
from punkt3_1_tab1_datei_scanner import Tab1DateiScanner
from punkt3_1_tab2_visualisierung import Tab2Visualisierung
from punkt3_1_utils import VBTDataManager
from punkt3_1_settings import AppSettings

class Punkt31MainApp:
    """
    Hauptklasse für die Punkt3.1 GUI-Anwendung
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.settings = AppSettings()
        self.data_manager = VBTDataManager()
        self.current_data = None
        self.current_metadata = None
        
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()
        
    def setup_window(self):
        """Konfiguriert das Hauptfenster"""
        self.root.title("Punkt3.1 - VectorbtPro Data Analyzer")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Icon setzen (falls vorhanden)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
            
        # Styling
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom Styles
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        
    def create_widgets(self):
        """Erstellt die GUI-Widgets"""
        # Hauptcontainer
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titel
        title_label = ttk.Label(
            main_frame, 
            text="Punkt3.1 - VectorbtPro Data Analyzer",
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Notebook für Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tab 1: Datei Scanner
        self.tab1 = Tab1DateiScanner(
            self.notebook, 
            self.data_manager,
            self.on_data_loaded
        )
        self.notebook.add(self.tab1.frame, text="Datei Scanner & Info")
        
        # Tab 2: Visualisierung
        self.tab2 = Tab2Visualisierung(
            self.notebook,
            self.data_manager
        )
        self.notebook.add(self.tab2.frame, text="Datenvisualisierung")
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Bereit")
        status_bar = ttk.Label(
            main_frame, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Grid-Konfiguration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def setup_bindings(self):
        """Setzt Event-Bindings auf"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Tab-Wechsel Event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    def on_data_loaded(self, data, metadata, file_path):
        """Callback wenn Daten geladen wurden"""
        self.current_data = data
        self.current_metadata = metadata
        
        # Tab2 über neue Daten informieren
        self.tab2.update_data(data, metadata, file_path)
        
        # Status aktualisieren
        filename = os.path.basename(file_path)
        self.status_var.set(f"Datei geladen: {filename}")
        
    def on_tab_changed(self, event):
        """Callback für Tab-Wechsel"""
        selected_tab = event.widget.tab('current')['text']
        
        if selected_tab == "Datenvisualisierung":
            if self.current_data is None:
                messagebox.showwarning(
                    "Keine Daten",
                    "Bitte laden Sie zuerst eine Datei in Tab 1."
                )
                # Zurück zu Tab 1
                self.notebook.select(0)
                return
                
    def on_closing(self):
        """Callback beim Schließen der Anwendung"""
        try:
            # Einstellungen speichern
            self.settings.save_settings()
            
            # Cleanup
            if hasattr(self.tab2, 'cleanup'):
                self.tab2.cleanup()
                
        except Exception as e:
            print(f"Fehler beim Schließen: {e}")
        finally:
            self.root.destroy()
            
    def run(self):
        """Startet die GUI-Anwendung"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
        except Exception as e:
            messagebox.showerror(
                "Fehler",
                f"Ein unerwarteter Fehler ist aufgetreten:\n{str(e)}"
            )
            self.on_closing()

def main():
    """Hauptfunktion"""
    try:
        # Arbeitsverzeichnis setzen
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # App starten
        app = Punkt31MainApp()
        app.run()
        
    except Exception as e:
        print(f"Fehler beim Starten der Anwendung: {e}")
        messagebox.showerror(
            "Startfehler",
            f"Die Anwendung konnte nicht gestartet werden:\n{str(e)}"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()