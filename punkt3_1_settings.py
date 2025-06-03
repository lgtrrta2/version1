#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punkt3.1 Settings - Konfigurationsmanagement
Verwaltet Anwendungseinstellungen und Benutzereinstellungen

Autor: AI Assistant
Datum: 2025-06-02
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class AppSettings:
    """
    Verwaltet Anwendungseinstellungen
    """
    
    def __init__(self, config_file: str = "punkt3_1_config.json"):
        self.config_file = Path(config_file)
        self.settings = self._load_default_settings()
        self.load_settings()
        
    def _load_default_settings(self) -> Dict[str, Any]:
        """Lädt Standard-Einstellungen"""
        return {
            "window": {
                "width": 1200,
                "height": 800,
                "min_width": 800,
                "min_height": 600
            },
            "scanner": {
                "default_directory": ".",
                "auto_scan_on_startup": True,
                "supported_extensions": [
                    ".pickle.blosc",
                    ".pickle", 
                    ".h5",
                    ".hdf5",
                    ".parquet",
                    ".csv"
                ],
                "scan_subdirectories": True,
                "max_scan_depth": 3
            },
            "visualization": {
                "default_chart_type": "candlestick",
                "default_timeframe": "1w",
                "max_data_points": 10000,
                "chart_theme": "plotly_white",
                "show_volume": True,
                "show_indicators": True
            },
            "data": {
                "cache_enabled": True,
                "cache_size_mb": 500,
                "auto_detect_metadata": True,
                "preferred_data_format": "vbt"
            },
            "ui": {
                "theme": "clam",
                "font_family": "Arial",
                "font_size": 10,
                "show_tooltips": True,
                "auto_refresh": True
            },
            "performance": {
                "max_memory_usage_mb": 2048,
                "enable_multiprocessing": True,
                "chunk_size": 10000,
                "lazy_loading": True
            }
        }
        
    def load_settings(self) -> None:
        """Lädt Einstellungen aus der Konfigurationsdatei"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    # Merge mit Default-Einstellungen
                    self._merge_settings(self.settings, saved_settings)
        except Exception as e:
            print(f"Fehler beim Laden der Einstellungen: {e}")
            
    def save_settings(self) -> None:
        """Speichert aktuelle Einstellungen"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Einstellungen: {e}")
            
    def _merge_settings(self, default: Dict, saved: Dict) -> None:
        """Merged gespeicherte Einstellungen mit Standard-Einstellungen"""
        for key, value in saved.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_settings(default[key], value)
                else:
                    default[key] = value
                    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Holt einen Einstellungswert über einen Pfad (z.B. 'window.width')"""
        keys = key_path.split('.')
        current = self.settings
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
            
    def set(self, key_path: str, value: Any) -> None:
        """Setzt einen Einstellungswert über einen Pfad"""
        keys = key_path.split('.')
        current = self.settings
        
        # Navigiere zu dem Punkt, wo der Wert gesetzt werden soll
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        # Setze den Wert
        current[keys[-1]] = value
        
    def get_scanner_settings(self) -> Dict[str, Any]:
        """Gibt Scanner-spezifische Einstellungen zurück"""
        return self.settings.get("scanner", {})
        
    def get_visualization_settings(self) -> Dict[str, Any]:
        """Gibt Visualisierungs-spezifische Einstellungen zurück"""
        return self.settings.get("visualization", {})
        
    def get_window_settings(self) -> Dict[str, Any]:
        """Gibt Fenster-spezifische Einstellungen zurück"""
        return self.settings.get("window", {})
        
    def update_window_settings(self, width: int, height: int) -> None:
        """Aktualisiert Fenstereinstellungen"""
        self.set("window.width", width)
        self.set("window.height", height)
        
    def update_scanner_directory(self, directory: str) -> None:
        """Aktualisiert das Standard-Scanner-Verzeichnis"""
        self.set("scanner.default_directory", directory)
        
    def get_supported_extensions(self) -> list:
        """Gibt unterstützte Dateierweiterungen zurück"""
        return self.get("scanner.supported_extensions", [])
        
    def is_extension_supported(self, file_path: str) -> bool:
        """Prüft ob eine Dateierweiterung unterstützt wird"""
        file_path = file_path.lower()
        extensions = self.get_supported_extensions()
        
        for ext in extensions:
            if file_path.endswith(ext.lower()):
                return True
        return False
        
    def get_chart_settings(self) -> Dict[str, Any]:
        """Gibt Chart-spezifische Einstellungen zurück"""
        viz_settings = self.get_visualization_settings()
        return {
            'theme': viz_settings.get('chart_theme', 'plotly_white'),
            'show_volume': viz_settings.get('show_volume', True),
            'show_indicators': viz_settings.get('show_indicators', True),
            'max_points': viz_settings.get('max_data_points', 10000)
        }
        
    def reset_to_defaults(self) -> None:
        """Setzt alle Einstellungen auf Standard zurück"""
        self.settings = self._load_default_settings()
        
    def export_settings(self, file_path: str) -> bool:
        """Exportiert Einstellungen in eine Datei"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Fehler beim Exportieren der Einstellungen: {e}")
            return False
            
    def import_settings(self, file_path: str) -> bool:
        """Importiert Einstellungen aus einer Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
                self._merge_settings(self.settings, imported_settings)
            return True
        except Exception as e:
            print(f"Fehler beim Importieren der Einstellungen: {e}")
            return False