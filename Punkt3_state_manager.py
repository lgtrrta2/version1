# 📊 PUNKT 3: STATE MANAGER
# Zentraler Zustand für alle Tabs

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from Punkt3_settings import CONFIG
from Punkt3_events import emit_status_changed, Events

@dataclass
class ApplicationState:
    """Haupt-Zustand der Anwendung"""

    # Datei-Zustand
    selected_file_path: Optional[str] = None
    available_files: Dict[str, Any] = None

    # Timeframe-Zustand
    timeframe_mode: str = CONFIG.DEFAULTS['timeframe_mode']
    selected_timeframes: List[str] = None
    multi_indicator_mode: str = CONFIG.DEFAULTS['multi_indicator_mode']

    # Indikator-Zustand
    selected_indicators: List[Dict] = None

    # Visualisierungs-Zustand
    visualization_mode: str = CONFIG.DEFAULTS['visualization_mode']
    visualization_period: str = CONFIG.DEFAULTS['visualization_period']

    # Chart-Segmentierung
    enable_segmentation: bool = False
    candles_per_chart: str = "100"
    quality: str = "Hoch"
    theme: str = "plotly_dark"

    # Speicher-Optionen
    save_punkt4: bool = CONFIG.DEFAULTS['save_punkt4']
    save_backup: bool = CONFIG.DEFAULTS['save_backup']
    save_charts: bool = CONFIG.DEFAULTS['save_charts']
    show_summary: bool = CONFIG.DEFAULTS['show_summary']

    # Code-Zustand
    generated_code: Optional[str] = None
    code_config: Optional[Dict] = None

    # UI-Zustand
    current_tab: int = 0
    status_message: str = "Bereit für Konfiguration"
    status_level: str = "info"

    def __post_init__(self):
        """Initialisiert Listen falls None"""
        if self.available_files is None:
            self.available_files = {}
        if self.selected_timeframes is None:
            self.selected_timeframes = []
        if self.selected_indicators is None:
            self.selected_indicators = []

class StateManager:
    """Verwaltet den globalen Anwendungszustand"""

    def __init__(self):
        self.state = ApplicationState()
        self.logger = logging.getLogger(__name__)
        self._observers = []

    def get_state(self) -> ApplicationState:
        """Gibt den aktuellen Zustand zurück"""
        return self.state

    def update_state(self, **kwargs):
        """Aktualisiert den Zustand"""
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
                self.logger.debug(f"State aktualisiert: {key} = {value}")
            else:
                self.logger.warning(f"Unbekannter State-Key: {key}")

        self._notify_observers()

    def add_observer(self, callback):
        """Fügt Observer für State-Änderungen hinzu"""
        self._observers.append(callback)

    def remove_observer(self, callback):
        """Entfernt Observer"""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self):
        """Benachrichtigt alle Observer über State-Änderungen"""
        for observer in self._observers:
            try:
                observer(self.state)
            except Exception as e:
                self.logger.error(f"Fehler in State-Observer: {e}")

    # Datei-Management
    def set_selected_file(self, file_path: str, file_info: Dict):
        """Setzt die ausgewählte Datei"""
        self.update_state(
            selected_file_path=file_path,
            selected_timeframes=[]  # Reset bei neuer Datei
        )

        # Timeframes aus file_info extrahieren
        if 'timeframes' in file_info:
            available_timeframes = file_info['timeframes']

            # Auto-Auswahl bei nur einem Timeframe
            if len(available_timeframes) == 1:
                self.update_state(
                    selected_timeframes=[available_timeframes[0]],
                    timeframe_mode='single'
                )
            else:
                # Ersten Timeframe auswählen
                self.update_state(selected_timeframes=[available_timeframes[0]])

        emit_status_changed("state_manager", "file_selected",
                           f"Datei ausgewählt: {os.path.basename(file_path)}", "success")

    def set_available_files(self, files: Dict):
        """Setzt verfügbare Dateien"""
        self.update_state(available_files=files)

    # Timeframe-Management
    def set_timeframe_mode(self, mode: str):
        """Setzt Timeframe-Modus"""
        self.update_state(timeframe_mode=mode)

        # Bei Single-Mode nur ersten Timeframe behalten
        if mode == 'single' and len(self.state.selected_timeframes) > 1:
            self.update_state(selected_timeframes=[self.state.selected_timeframes[0]])

    def set_selected_timeframes(self, timeframes: List[str]):
        """Setzt ausgewählte Timeframes"""
        # Validierung basierend auf Modus
        if self.state.timeframe_mode == 'single' and len(timeframes) > 1:
            timeframes = [timeframes[0]]

        self.update_state(selected_timeframes=timeframes)
        emit_status_changed("state_manager", "timeframes_changed",
                           f"{len(timeframes)} Timeframe(s) ausgewählt", "info")

    def add_timeframe(self, timeframe: str):
        """Fügt Timeframe hinzu"""
        if timeframe not in self.state.selected_timeframes:
            new_timeframes = self.state.selected_timeframes + [timeframe]
            self.set_selected_timeframes(new_timeframes)

    def remove_timeframe(self, timeframe: str):
        """Entfernt Timeframe"""
        if timeframe in self.state.selected_timeframes:
            new_timeframes = [tf for tf in self.state.selected_timeframes if tf != timeframe]
            self.set_selected_timeframes(new_timeframes)

    # Indikator-Management
    def add_indicator(self, indicator: Dict):
        """Fügt Indikator hinzu"""
        new_indicators = self.state.selected_indicators + [indicator]
        self.update_state(selected_indicators=new_indicators)
        # KORRIGIERT: Richtiges Event für GUI-Update mit korrekter Signatur
        from Punkt3_events import emit_indicators_changed
        emit_indicators_changed("state_manager", new_indicators, "added")
        emit_status_changed("state_manager", "indicator_added",
                           f"Indikator hinzugefügt: {indicator.get('display_name', 'Unbekannt')}", "success")

    def remove_indicator(self, index: int):
        """Entfernt Indikator nach Index"""
        if 0 <= index < len(self.state.selected_indicators):
            removed = self.state.selected_indicators.pop(index)
            self.update_state(selected_indicators=self.state.selected_indicators)
            # KORRIGIERT: Richtiges Event für GUI-Update mit korrekter Signatur
            from Punkt3_events import emit_indicators_changed
            emit_indicators_changed("state_manager", self.state.selected_indicators, "removed")
            emit_status_changed("state_manager", "indicator_removed",
                               f"Indikator entfernt: {removed.get('display_name', 'Unbekannt')}", "info")

    def clear_indicators(self):
        """Löscht alle Indikatoren"""
        count = len(self.state.selected_indicators)
        self.update_state(selected_indicators=[])
        # KORRIGIERT: Richtiges Event für GUI-Update mit korrekter Signatur
        from Punkt3_events import emit_indicators_changed
        emit_indicators_changed("state_manager", [], "cleared")
        emit_status_changed("state_manager", "indicators_cleared",
                           f"{count} Indikatoren gelöscht", "info")

    def update_indicator(self, index: int, indicator: Dict):
        """Aktualisiert Indikator"""
        if 0 <= index < len(self.state.selected_indicators):
            self.state.selected_indicators[index] = indicator
            self.update_state(selected_indicators=self.state.selected_indicators)
            # KORRIGIERT: Richtiges Event für GUI-Update mit korrekter Signatur
            from Punkt3_events import emit_indicators_changed
            emit_indicators_changed("state_manager", self.state.selected_indicators, "updated")
            emit_status_changed("state_manager", "indicator_updated",
                               f"Indikator aktualisiert: {indicator.get('display_name', 'Unbekannt')}", "success")

    # Visualisierungs-Management
    def set_visualization(self, mode: str, period: str = None):
        """Setzt Visualisierungs-Optionen"""
        updates = {'visualization_mode': mode}
        if period:
            updates['visualization_period'] = period

        self.update_state(**updates)
        emit_status_changed("state_manager", "visualization_changed",
                           f"Visualisierung: {mode}", "info")

    def set_segmentation(self, enable: bool, candles_per_chart: str = None):
        """Setzt Chart-Segmentierung"""
        updates = {'enable_segmentation': enable}
        if candles_per_chart:
            updates['candles_per_chart'] = candles_per_chart

        self.update_state(**updates)
        emit_status_changed("state_manager", "segmentation_changed",
                           f"Segmentierung: {'aktiviert' if enable else 'deaktiviert'}", "info")

    def set_chart_options(self, quality: str = None, theme: str = None):
        """Setzt Chart-Qualität und Theme"""
        updates = {}
        if quality:
            updates['quality'] = quality
        if theme:
            updates['theme'] = theme

        if updates:
            self.update_state(**updates)
            emit_status_changed("state_manager", "chart_options_changed",
                               f"Chart-Optionen aktualisiert", "info")

    # Code-Management
    def set_generated_code(self, code: str, config: Dict):
        """Setzt generierten Code"""
        self.update_state(generated_code=code, code_config=config)
        lines = len(code.split('\n'))
        emit_status_changed("state_manager", "code_generated",
                           f"Code generiert: {lines} Zeilen", "success")

    # Status-Management
    def set_status(self, message: str, level: str = "info"):
        """Setzt Status-Nachricht"""
        self.update_state(status_message=message, status_level=level)

    # Validierung
    def is_ready_for_generation(self) -> tuple[bool, str]:
        """Prüft ob bereit für Code-Generierung"""
        if not self.state.selected_file_path:
            return False, "Keine Datei ausgewählt"

        if not self.state.selected_timeframes:
            return False, "Keine Timeframes ausgewählt"

        if not self.state.selected_indicators:
            return False, "Keine Indikatoren ausgewählt"

        if not self.state.visualization_mode:
            return False, "Keine Visualisierung konfiguriert"

        return True, "Bereit für Code-Generierung"

    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken zurück"""
        return {
            'file_selected': bool(self.state.selected_file_path),
            'file_name': os.path.basename(self.state.selected_file_path) if self.state.selected_file_path else "Keine",
            'timeframe_count': len(self.state.selected_timeframes),
            'indicator_count': len(self.state.selected_indicators),
            'visualization_mode': self.state.visualization_mode,
            'ready_for_generation': self.is_ready_for_generation()[0]
        }

    # Persistierung
    def save_state(self, filename: str = None):
        """Speichert Zustand in Datei"""
        if not filename:
            filename = f"punkt3_state_{CONFIG.get_timestamp()}.json"

        try:
            state_dict = asdict(self.state)
            with open(filename, 'w') as f:
                json.dump(state_dict, f, indent=2)
            self.logger.info(f"State gespeichert: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern des States: {e}")
            return False

    def load_state(self, filename: str):
        """Lädt Zustand aus Datei"""
        try:
            with open(filename, 'r') as f:
                state_dict = json.load(f)

            # State aktualisieren
            for key, value in state_dict.items():
                if hasattr(self.state, key):
                    setattr(self.state, key, value)

            self._notify_observers()
            self.logger.info(f"State geladen: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Laden des States: {e}")
            return False

# Globaler State Manager
state_manager = StateManager()

# Convenience-Funktionen
def get_state() -> ApplicationState:
    """Gibt aktuellen State zurück"""
    return state_manager.get_state()

def update_state(**kwargs):
    """Aktualisiert State"""
    state_manager.update_state(**kwargs)

# Logging konfigurieren
logging.basicConfig(
    level=getattr(logging, CONFIG.LOGGING['level']),
    format=CONFIG.LOGGING['format']
)
