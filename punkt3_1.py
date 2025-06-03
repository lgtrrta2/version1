#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punkt3.1 - Hauptstartdatei
GUI-Anwendung zum Scannen und Visualisieren von VectorbtPro-Daten

Autor: AI Assistant
Datum: 2025-06-02
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import traceback

# Eigene Module importieren
try:
    from punkt3_1_main import Punkt31MainApp
except ImportError as e:
    print(f"Fehler beim Importieren der Module: {e}")
    print("Stelle sicher, dass alle Punkt3.1 Module im gleichen Verzeichnis sind.")
    print("Benötigte Dateien:")
    print("- punkt3_1_main.py")
    print("- punkt3_1_settings.py")
    print("- punkt3_1_utils.py")
    print("- punkt3_1_tab1_datei_scanner.py")
    print("- punkt3_1_tab2_visualisierung.py")
    traceback.print_exc()
    sys.exit(1)

def main():
    """Hauptfunktion zum Starten der Anwendung"""
    try:
        # Anwendung starten
        app = Punkt31MainApp()
        
        # Fenster zentrieren
        window_width = 1200
        window_height = 800
        screen_width = app.root.winfo_screenwidth()
        screen_height = app.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        app.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Mindestgröße setzen
        app.root.minsize(800, 600)
        
        # Tkinter Mainloop starten
        app.run()
        
    except Exception as e:
        messagebox.showerror(
            "Fehler beim Starten", 
            f"Punkt3.1 konnte nicht gestartet werden:\n\n{str(e)}\n\n"
            "Bitte überprüfen Sie die Installation und stellen Sie sicher, "
            "dass alle erforderlichen Module vorhanden sind."
        )
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()