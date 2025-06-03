# 📊 PUNKT 3: EVENT-SYSTEM
# Ermöglicht Kommunikation zwischen Tabs ohne direkte Abhängigkeiten

import logging
from typing import Dict, List, Callable, Any
from Punkt3_settings import CONFIG

class EventManager:
    """Zentrales Event-System für Tab-Kommunikation"""
    
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)
        
    def on(self, event_name: str, callback: Callable):
        """Registriert einen Event-Listener"""
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        
        self.listeners[event_name].append(callback)
        self.logger.debug(f"Event-Listener registriert: {event_name}")
    
    def off(self, event_name: str, callback: Callable = None):
        """Entfernt Event-Listener"""
        if event_name not in self.listeners:
            return
        
        if callback is None:
            # Alle Listener für dieses Event entfernen
            self.listeners[event_name] = []
        else:
            # Spezifischen Listener entfernen
            if callback in self.listeners[event_name]:
                self.listeners[event_name].remove(callback)
        
        self.logger.debug(f"Event-Listener entfernt: {event_name}")
    
    def emit(self, event_name: str, data: Any = None):
        """Sendet ein Event an alle registrierten Listener"""
        if event_name not in self.listeners:
            self.logger.debug(f"Keine Listener für Event: {event_name}")
            return
        
        self.logger.debug(f"Event gesendet: {event_name} mit {len(self.listeners[event_name])} Listenern")
        
        for callback in self.listeners[event_name]:
            try:
                if data is not None:
                    callback(data)
                else:
                    callback()
            except Exception as e:
                self.logger.error(f"Fehler in Event-Callback für {event_name}: {e}")
    
    def get_listeners(self, event_name: str) -> List[Callable]:
        """Gibt alle Listener für ein Event zurück"""
        return self.listeners.get(event_name, [])
    
    def clear_all(self):
        """Entfernt alle Event-Listener"""
        self.listeners.clear()
        self.logger.debug("Alle Event-Listener entfernt")

class EventData:
    """Basis-Klasse für Event-Daten"""
    
    def __init__(self, source: str, **kwargs):
        self.source = source
        self.timestamp = CONFIG.get_timestamp()
        for key, value in kwargs.items():
            setattr(self, key, value)

class FileSelectedEvent(EventData):
    """Event für Datei-Auswahl"""
    
    def __init__(self, source: str, file_path: str, file_info: dict):
        super().__init__(source)
        self.file_path = file_path
        self.file_info = file_info

class TimeframesChangedEvent(EventData):
    """Event für Timeframe-Änderungen"""
    
    def __init__(self, source: str, timeframes: list, mode: str):
        super().__init__(source)
        self.timeframes = timeframes
        self.mode = mode

class IndicatorsChangedEvent(EventData):
    """Event für Indikator-Änderungen"""
    
    def __init__(self, source: str, indicators: list, action: str):
        super().__init__(source)
        self.indicators = indicators
        self.action = action  # 'added', 'removed', 'cleared', 'updated'

class VisualizationChangedEvent(EventData):
    """Event für Visualisierungs-Änderungen"""
    
    def __init__(self, source: str, mode: str, period: str):
        super().__init__(source)
        self.mode = mode
        self.period = period

class CodeGeneratedEvent(EventData):
    """Event für Code-Generierung"""
    
    def __init__(self, source: str, code: str, config: dict):
        super().__init__(source)
        self.code = code
        self.config = config

class StatusChangedEvent(EventData):
    """Event für Status-Änderungen"""
    
    def __init__(self, source: str, status: str, message: str, level: str = 'info'):
        super().__init__(source)
        self.status = status
        self.message = message
        self.level = level  # 'info', 'warning', 'error', 'success'

# Event-Konstanten für bessere Typsicherheit
class Events:
    """Konstanten für Event-Namen"""
    
    FILE_SELECTED = CONFIG.EVENTS['file_selected']
    TIMEFRAMES_CHANGED = CONFIG.EVENTS['timeframes_changed']
    INDICATORS_CHANGED = CONFIG.EVENTS['indicators_changed']
    VISUALIZATION_CHANGED = CONFIG.EVENTS['visualization_changed']
    CODE_GENERATED = CONFIG.EVENTS['code_generated']
    STATUS_CHANGED = CONFIG.EVENTS['status_changed']

# Globaler Event-Manager
event_manager = EventManager()

# Convenience-Funktionen für einfachere Nutzung
def on(event_name: str, callback: Callable):
    """Registriert Event-Listener"""
    event_manager.on(event_name, callback)

def off(event_name: str, callback: Callable = None):
    """Entfernt Event-Listener"""
    event_manager.off(event_name, callback)

def emit(event_name: str, data: Any = None):
    """Sendet Event"""
    event_manager.emit(event_name, data)

# Spezielle Emit-Funktionen für typisierte Events
def emit_file_selected(source: str, file_path: str, file_info: dict):
    """Sendet File-Selected Event"""
    event_data = FileSelectedEvent(source, file_path, file_info)
    emit(Events.FILE_SELECTED, event_data)

def emit_timeframes_changed(source: str, timeframes: list, mode: str):
    """Sendet Timeframes-Changed Event"""
    event_data = TimeframesChangedEvent(source, timeframes, mode)
    emit(Events.TIMEFRAMES_CHANGED, event_data)

def emit_indicators_changed(source: str, indicators: list, action: str):
    """Sendet Indicators-Changed Event"""
    event_data = IndicatorsChangedEvent(source, indicators, action)
    emit(Events.INDICATORS_CHANGED, event_data)

def emit_visualization_changed(source: str, mode: str, period: str):
    """Sendet Visualization-Changed Event"""
    event_data = VisualizationChangedEvent(source, mode, period)
    emit(Events.VISUALIZATION_CHANGED, event_data)

def emit_code_generated(source: str, code: str, config: dict):
    """Sendet Code-Generated Event"""
    event_data = CodeGeneratedEvent(source, code, config)
    emit(Events.CODE_GENERATED, event_data)

def emit_status_changed(source: str, status: str, message: str, level: str = 'info'):
    """Sendet Status-Changed Event"""
    event_data = StatusChangedEvent(source, status, message, level)
    emit(Events.STATUS_CHANGED, event_data)

# Debug-Funktionen
def debug_listeners():
    """Zeigt alle registrierten Listener"""
    print("🔍 Registrierte Event-Listener:")
    for event_name, listeners in event_manager.listeners.items():
        print(f"  {event_name}: {len(listeners)} Listener")

def debug_emit_test():
    """Test-Event für Debugging"""
    print("🧪 Sende Test-Event...")
    emit_status_changed("debug", "test", "Test-Nachricht", "info")

# Logging konfigurieren
logging.basicConfig(
    level=getattr(logging, CONFIG.LOGGING['level']),
    format=CONFIG.LOGGING['format']
)
