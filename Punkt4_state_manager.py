# 📊 PUNKT 4: PARAMETER-KONFIGURATOR - STATE MANAGEMENT
# Zentrales State Management für VectorBT Pro Parameter

import json
import copy
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from datetime import datetime

from Punkt4_settings import CONFIG
from Punkt4_events import emit, Events

class StateManager:
    """Zentraler State Manager für Punkt 4 VectorBT Pro Parameter"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._state = self._initialize_state()
        self._state_history = []
        self._max_history = 50
        self._dirty = False
    
    def _initialize_state(self) -> Dict[str, Any]:
        """Initialen State mit VBT Pro Defaults erstellen"""
        return {
            # Punkt 3 Daten
            'punkt3': {
                'metadata_file': None,
                'indicators_file': None,
                'metadata': None,
                'indicators_info': None,
                'timeframes': [],
                'indicators_list': [],
                'data_loaded': False
            },
            
            # VectorBT Pro Parameter State
            'vbt_parameters': copy.deepcopy(CONFIG.VBT_DEFAULTS),
            
            # UI State
            'ui': {
                'current_tab': 0,
                'status_message': 'Bereit für Parameter-Konfiguration',
                'status_level': 'info',
                'progress': {'current': 0, 'total': 100, 'message': ''},
                'validation_errors': [],
                'last_export_path': None
            },
            
            # Export State
            'export': {
                'punkt5_code': None,
                'punkt6_code': None,
                'punkt7_config': None,
                'last_export_time': None,
                'export_format': 'python'
            },
            
            # Validation State
            'validation': {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'last_check': None
            },
            
            # Meta Information
            'meta': {
                'created_at': datetime.now().isoformat(),
                'modified_at': datetime.now().isoformat(),
                'version': CONFIG.APP['version'],
                'punkt4_ready': False,
                'vbt_optimized': True
            }
        }
    
    def get_state(self, path: str = None) -> Any:
        """State oder State-Teil abrufen"""
        if path is None:
            return copy.deepcopy(self._state)
        
        try:
            keys = path.split('.')
            value = self._state
            for key in keys:
                value = value[key]
            return copy.deepcopy(value)
        except (KeyError, TypeError):
            self.logger.warning(f"State-Pfad nicht gefunden: {path}")
            return None
    
    def set_state(self, path: str, value: Any, emit_event: bool = True):
        """State oder State-Teil setzen"""
        try:
            # State-Historie speichern
            self._save_to_history()
            
            keys = path.split('.')
            target = self._state
            
            # Zum Ziel navigieren
            for key in keys[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]
            
            # Wert setzen
            old_value = target.get(keys[-1])
            target[keys[-1]] = value
            
            # Meta-Daten aktualisieren
            self._state['meta']['modified_at'] = datetime.now().isoformat()
            self._dirty = True
            
            # Event auslösen
            if emit_event and old_value != value:
                if path.startswith('vbt_parameters.'):
                    param_name = path.replace('vbt_parameters.', '')
                    emit(Events.PARAMETER_CHANGED, {
                        'parameter': param_name,
                        'value': value,
                        'old_value': old_value
                    }, 'StateManager')
                
                emit(Events.STATUS_CHANGED, {
                    'message': f'Parameter aktualisiert: {path}',
                    'level': 'debug'
                }, 'StateManager')
            
            self.logger.debug(f"State aktualisiert: {path} = {value}")
            
        except Exception as e:
            self.logger.error(f"State-Update Fehler ({path}): {e}")
            raise
    
    def update_state(self, updates: Dict[str, Any], emit_events: bool = True):
        """Mehrere State-Updates auf einmal"""
        for path, value in updates.items():
            self.set_state(path, value, emit_events)
    
    def reset_vbt_parameters(self):
        """VBT Parameter auf Defaults zurücksetzen"""
        self.set_state('vbt_parameters', copy.deepcopy(CONFIG.VBT_DEFAULTS))
        emit(Events.PARAMETER_RESET, None, 'StateManager')
        self.logger.info("VBT Parameter zurückgesetzt")
    
    def get_vbt_parameter(self, param_name: str) -> Any:
        """Einzelnen VBT Parameter abrufen"""
        return self.get_state(f'vbt_parameters.{param_name}')
    
    def set_vbt_parameter(self, param_name: str, value: Any):
        """Einzelnen VBT Parameter setzen"""
        self.set_state(f'vbt_parameters.{param_name}', value)
    
    def get_all_vbt_parameters(self) -> Dict[str, Any]:
        """Alle VBT Parameter abrufen"""
        return self.get_state('vbt_parameters')
    
    def _save_to_history(self):
        """Aktuellen State in Historie speichern"""
        self._state_history.append({
            'timestamp': datetime.now().isoformat(),
            'state': copy.deepcopy(self._state)
        })
        
        # Historie begrenzen
        if len(self._state_history) > self._max_history:
            self._state_history = self._state_history[-self._max_history:]
    
    def undo(self) -> bool:
        """Letzten State wiederherstellen"""
        if len(self._state_history) > 1:
            # Aktuellen State entfernen
            self._state_history.pop()
            # Vorherigen State wiederherstellen
            previous = self._state_history[-1]
            self._state = copy.deepcopy(previous['state'])
            
            emit(Events.STATUS_CHANGED, {
                'message': 'Änderung rückgängig gemacht',
                'level': 'info'
            }, 'StateManager')
            
            return True
        return False
    
    def save_to_file(self, file_path: Path) -> bool:
        """State in Datei speichern"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._state, f, indent=2, ensure_ascii=False, default=str)
            
            self._dirty = False
            emit(Events.CONFIG_SAVED, {'file_path': str(file_path)}, 'StateManager')
            self.logger.info(f"State gespeichert: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"State-Speichern Fehler: {e}")
            return False
    
    def load_from_file(self, file_path: Path) -> bool:
        """State aus Datei laden"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_state = json.load(f)
            
            # State validieren und mergen
            self._state = self._merge_loaded_state(loaded_state)
            self._dirty = False
            
            emit(Events.CONFIG_LOADED, {'file_path': str(file_path)}, 'StateManager')
            self.logger.info(f"State geladen: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"State-Laden Fehler: {e}")
            return False
    
    def _merge_loaded_state(self, loaded_state: Dict[str, Any]) -> Dict[str, Any]:
        """Geladenen State mit aktuellem State mergen"""
        # Basis-State erstellen
        merged_state = self._initialize_state()
        
        # Geladene Werte übernehmen (nur bekannte Schlüssel)
        for section, data in loaded_state.items():
            if section in merged_state:
                if isinstance(data, dict) and isinstance(merged_state[section], dict):
                    merged_state[section].update(data)
                else:
                    merged_state[section] = data
        
        # Meta-Daten aktualisieren
        merged_state['meta']['modified_at'] = datetime.now().isoformat()
        
        return merged_state
    
    def validate_vbt_parameters(self) -> Dict[str, Any]:
        """VBT Parameter validieren"""
        errors = []
        warnings = []
        
        vbt_params = self.get_all_vbt_parameters()
        
        # Parameter validieren basierend auf CONFIG.PARAMETER_VALIDATION
        for param_name, validation_rules in CONFIG.PARAMETER_VALIDATION.items():
            if param_name in vbt_params:
                value = vbt_params[param_name]
                
                # Typ-Validierung
                expected_type = validation_rules.get('type')
                if expected_type and not isinstance(value, expected_type):
                    try:
                        # Versuche Konvertierung
                        vbt_params[param_name] = expected_type(value)
                    except (ValueError, TypeError):
                        errors.append(f"{param_name}: Muss vom Typ {expected_type.__name__} sein")
                        continue
                
                # Bereich-Validierung
                if 'min' in validation_rules and value < validation_rules['min']:
                    errors.append(f"{param_name}: Muss mindestens {validation_rules['min']} sein")
                
                if 'max' in validation_rules and value > validation_rules['max']:
                    errors.append(f"{param_name}: Darf höchstens {validation_rules['max']} sein")
        
        # Spezielle VBT Validierungen
        
        # Stop Loss vs Take Profit
        sl_stop = vbt_params.get('sl_stop')
        tp_stop = vbt_params.get('tp_stop')
        if sl_stop and tp_stop:
            if tp_stop <= sl_stop:
                warnings.append("Take Profit sollte größer als Stop Loss sein")
            
            risk_reward = tp_stop / sl_stop if sl_stop > 0 else 0
            if risk_reward < 1.5:
                warnings.append(f"Risk-Reward Ratio ist niedrig: {risk_reward:.2f}:1")
        
        # Size Validierung
        size = vbt_params.get('size', 0)
        size_type = vbt_params.get('size_type', 'amount')
        if size_type in ['percent', 'valuepercent'] and size > 1.0:
            warnings.append(f"Size {size} bei {size_type} könnte zu groß sein (>100%)")
        
        # Cash Validierung
        init_cash = vbt_params.get('init_cash', 0)
        if init_cash < 1000:
            warnings.append("Initial Cash ist sehr niedrig für realistische Backtests")
        
        # Fees Validierung
        fees = vbt_params.get('fees', 0)
        if fees > 0.01:  # 1%
            warnings.append(f"Trading Fees sind sehr hoch: {fees*100:.2f}%")
        
        is_valid = len(errors) == 0
        
        # Validation State aktualisieren
        self.update_state({
            'validation.is_valid': is_valid,
            'validation.errors': errors,
            'validation.warnings': warnings,
            'validation.last_check': datetime.now().isoformat()
        }, emit_events=False)
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings
        }
    
    def is_dirty(self) -> bool:
        """Prüfen ob State geändert wurde"""
        return self._dirty
    
    def mark_clean(self):
        """State als gespeichert markieren"""
        self._dirty = False

# Globaler State Manager
state_manager = StateManager()

# Convenience-Funktionen
def get_state(path: str = None) -> Any:
    """State abrufen (Shortcut)"""
    return state_manager.get_state(path)

def set_state(path: str, value: Any, emit_event: bool = True):
    """State setzen (Shortcut)"""
    state_manager.set_state(path, value, emit_event)

def update_state(updates: Dict[str, Any], emit_events: bool = True):
    """State-Updates (Shortcut)"""
    state_manager.update_state(updates, emit_events)

def get_vbt_parameter(param_name: str) -> Any:
    """VBT Parameter abrufen (Shortcut)"""
    return state_manager.get_vbt_parameter(param_name)

def set_vbt_parameter(param_name: str, value: Any):
    """VBT Parameter setzen (Shortcut)"""
    state_manager.set_vbt_parameter(param_name, value)

def get_all_vbt_parameters() -> Dict[str, Any]:
    """Alle VBT Parameter abrufen (Shortcut)"""
    return state_manager.get_all_vbt_parameters()
