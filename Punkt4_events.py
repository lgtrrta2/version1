# 📊 PUNKT 4: PARAMETER-KONFIGURATOR - EVENT SYSTEM
# Zentrales Event Management für Tab-Kommunikation

from typing import Dict, List, Callable, Any
from enum import Enum
import logging

class Events(Enum):
    """Event-Typen für Punkt 4"""
    
    # Datei Events
    PUNKT3_FILE_SELECTED = "punkt3_file_selected"
    PUNKT3_DATA_LOADED = "punkt3_data_loaded"
    PUNKT3_DATA_ERROR = "punkt3_data_error"
    
    # Parameter Events
    PARAMETER_CHANGED = "parameter_changed"
    PARAMETER_VALIDATED = "parameter_validated"
    PARAMETER_ERROR = "parameter_error"
    PARAMETER_RESET = "parameter_reset"
    
    # Export Events
    EXPORT_STARTED = "export_started"
    EXPORT_COMPLETED = "export_completed"
    EXPORT_ERROR = "export_error"
    CODE_GENERATED = "code_generated"
    
    # UI Events
    TAB_CHANGED = "tab_changed"
    STATUS_CHANGED = "status_changed"
    PROGRESS_UPDATED = "progress_updated"
    
    # Validation Events
    VALIDATION_PASSED = "validation_passed"
    VALIDATION_FAILED = "validation_failed"
    
    # Configuration Events
    CONFIG_LOADED = "config_loaded"
    CONFIG_SAVED = "config_saved"
    CONFIG_RESET = "config_reset"

class EventManager:
    """Zentraler Event Manager für Punkt 4"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._listeners: Dict[Events, List[Callable]] = {}
        self._event_history: List[Dict[str, Any]] = []
        self._max_history = 100
    
    def subscribe(self, event: Events, callback: Callable):
        """Event-Listener registrieren"""
        if event not in self._listeners:
            self._listeners[event] = []
        
        if callback not in self._listeners[event]:
            self._listeners[event].append(callback)
            self.logger.debug(f"Event-Listener registriert: {event.value}")
    
    def unsubscribe(self, event: Events, callback: Callable):
        """Event-Listener entfernen"""
        if event in self._listeners and callback in self._listeners[event]:
            self._listeners[event].remove(callback)
            self.logger.debug(f"Event-Listener entfernt: {event.value}")
    
    def emit(self, event: Events, data: Any = None, source: str = None):
        """Event auslösen"""
        try:
            # Event in Historie speichern
            event_record = {
                'event': event.value,
                'data': data,
                'source': source,
                'timestamp': self._get_timestamp()
            }
            self._add_to_history(event_record)
            
            # Listener benachrichtigen
            if event in self._listeners:
                for callback in self._listeners[event]:
                    try:
                        callback(data)
                    except Exception as e:
                        self.logger.error(f"Event-Callback Fehler ({event.value}): {e}")
            
            self.logger.debug(f"Event ausgelöst: {event.value} von {source}")
            
        except Exception as e:
            self.logger.error(f"Event-Emission Fehler: {e}")
    
    def _add_to_history(self, event_record: Dict[str, Any]):
        """Event zur Historie hinzufügen"""
        self._event_history.append(event_record)
        
        # Historie begrenzen
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
    
    def _get_timestamp(self) -> str:
        """Aktuellen Zeitstempel generieren"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    def get_event_history(self, event_type: Events = None) -> List[Dict[str, Any]]:
        """Event-Historie abrufen"""
        if event_type is None:
            return self._event_history.copy()
        
        return [e for e in self._event_history if e['event'] == event_type.value]
    
    def clear_history(self):
        """Event-Historie löschen"""
        self._event_history.clear()
        self.logger.debug("Event-Historie gelöscht")

# Globaler Event Manager
event_manager = EventManager()

# Convenience-Funktionen
def on(event: Events, callback: Callable):
    """Event-Listener registrieren (Decorator-Style)"""
    event_manager.subscribe(event, callback)
    return callback

def emit(event: Events, data: Any = None, source: str = None):
    """Event auslösen (Shortcut)"""
    event_manager.emit(event, data, source)

def emit_status_changed(message: str, level: str = "info", source: str = None):
    """Status-Änderung Event auslösen"""
    emit(Events.STATUS_CHANGED, {
        'message': message,
        'level': level
    }, source)

def emit_progress_updated(current: int, total: int, message: str = "", source: str = None):
    """Progress-Update Event auslösen"""
    emit(Events.PROGRESS_UPDATED, {
        'current': current,
        'total': total,
        'message': message,
        'percentage': (current / total * 100) if total > 0 else 0
    }, source)

def emit_parameter_changed(parameter: str, value: Any, source: str = None):
    """Parameter-Änderung Event auslösen"""
    emit(Events.PARAMETER_CHANGED, {
        'parameter': parameter,
        'value': value
    }, source)

def emit_validation_result(is_valid: bool, errors: List[str] = None, source: str = None):
    """Validierungs-Ergebnis Event auslösen"""
    event = Events.VALIDATION_PASSED if is_valid else Events.VALIDATION_FAILED
    emit(event, {
        'is_valid': is_valid,
        'errors': errors or []
    }, source)

def emit_export_status(status: str, file_path: str = None, error: str = None, source: str = None):
    """Export-Status Event auslösen"""
    if status == "started":
        emit(Events.EXPORT_STARTED, {'file_path': file_path}, source)
    elif status == "completed":
        emit(Events.EXPORT_COMPLETED, {'file_path': file_path}, source)
    elif status == "error":
        emit(Events.EXPORT_ERROR, {'error': error, 'file_path': file_path}, source)

def emit_code_generated(code: str, target: str, source: str = None):
    """Code-Generation Event auslösen"""
    emit(Events.CODE_GENERATED, {
        'code': code,
        'target': target,
        'lines': len(code.split('\n'))
    }, source)

# Event-Logging Setup
def setup_event_logging():
    """Event-Logging konfigurieren"""
    logger = logging.getLogger(__name__)

    def log_status_change(data):
        level = data.get('level', 'info').upper()
        message = data.get('message', '')
        getattr(logger, level.lower(), logger.info)(f"Status: {message}")

    def log_parameter_change(data):
        parameter = data.get('parameter', '')
        value = data.get('value', '')
        logger.debug(f"Parameter geändert: {parameter} = {value}")

    def log_validation_error(data):
        errors = data.get('errors', [])
        for error in errors:
            logger.warning(f"Validierungsfehler: {error}")

    def log_export_success(data):
        file_path = data.get('file_path', '')
        logger.info(f"Export erfolgreich: {file_path}")

    def log_export_error(data):
        error = data.get('error', '')
        file_path = data.get('file_path', '')
        logger.error(f"Export-Fehler ({file_path}): {error}")

    def log_code_generation(data):
        target = data.get('target', '')
        lines = data.get('lines', 0)
        logger.info(f"Code generiert für {target}: {lines} Zeilen")

    # Event-Listener registrieren
    on(Events.STATUS_CHANGED, log_status_change)
    on(Events.PARAMETER_CHANGED, log_parameter_change)
    on(Events.VALIDATION_FAILED, log_validation_error)
    on(Events.EXPORT_COMPLETED, log_export_success)
    on(Events.EXPORT_ERROR, log_export_error)
    on(Events.CODE_GENERATED, log_code_generation)
