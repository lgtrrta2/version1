# 📊 PUNKT 4: PARAMETER-KONFIGURATOR - EINSTELLUNGEN
# VectorBT Pro optimierte Konfiguration basierend auf Portfolio-Dokumentation

import os
from pathlib import Path
from typing import Dict, Any, List, Union
import vectorbtpro as vbt
import numpy as np

class CONFIG:
    """Zentrale Konfiguration für Punkt 4 - VectorBT Pro Parameter"""
    
    # === ANWENDUNGS-EINSTELLUNGEN ===
    APP = {
        'title': 'PUNKT 4: PARAMETER-KONFIGURATOR',
        'version': '1.0.0',
        'geometry': '1400x900',
        'min_size': (1200, 800),
        'icon_path': None,
        'theme': 'default'
    }
    
    # === VERZEICHNIS-STRUKTUR ===
    PATHS = {
        'punkt3_data': Path('data/punkt3'),
        'punkt4_exports': Path('data/punkt4'),
        'punkt4_configs': Path('data/punkt4/configs'),
        'punkt4_templates': Path('data/punkt4/templates'),
        'logs': Path('logs'),
        'temp': Path('temp')
    }
    
    # === DATEI-FILTER ===
    FILE_FILTERS = {
        'punkt3_metadata': [
            ('JSON Metadaten', '*.json'),
            ('Alle Dateien', '*.*')
        ],
        'punkt3_indicators': [
            ('VBT Pickle', '*.pickle'),
            ('VBT Pickle Blosc', '*.pickle.blosc'),
            ('CSV Backup', '*.csv'),
            ('Alle Dateien', '*.*')
        ],
        'export_config': [
            ('JSON Konfiguration', '*.json'),
            ('Python Code', '*.py'),
            ('Alle Dateien', '*.*')
        ]
    }
    
    # === VECTORBT PRO OPTIMIERUNG ===
    VBT_SETTINGS = {
        'numba_parallel': True,
        'numba_cache': True,
        'chunking_enabled': True,
        'chunk_size': 10000,
        'memory_optimization': True,
        'float_precision': 'float64',  # VBT Standard
        'compression': 'blosc',        # Beste Performance
        'freq_inference': True
    }
    
    # === GUI EINSTELLUNGEN ===
    GUI = {
        'tab_padding': 10,
        'widget_spacing': 5,
        'label_width': 150,
        'entry_width': 200,
        'button_width': 120,
        'listbox_height': 10,
        'text_height': 15,
        'progress_length': 400
    }
    
    # === VECTORBT PRO PARAMETER DEFAULTS ===
    # Basierend auf vbt.Portfolio.from_signals() Dokumentation
    VBT_DEFAULTS = {
        # === POSITION MANAGEMENT ===
        'init_cash': 5000.0,             # Initial cash (Mini-Futures Standard)
        'cash_sharing': False,           # Cash sharing between assets
        'call_seq': 'auto',             # Call sequence
        'group_by': None,                # Grouping
        
        # === SIZE & DIRECTION (NQ FUTURES STANDARD) ===
        'size': 1,                       # Position size (1 contract = NQ mini)
        'size_type': 'amount',           # SizeType: amount (contracts)
        'direction': 'both',             # Direction: both (long & short)
        'accumulate': False,             # AccumulationMode

        # === FUTURES SPECIFICATIONS ===
        'tick_size': 0.25,               # NQ Tick Size (0.25 points)
        'tick_value': 5.0,               # NQ Tick Value ($5 per tick)

        # === PRICE & EXECUTION ===
        'price': None,                   # Custom price (None = close)
        'val_price': None,               # Valuation price
        'open': None,                    # Open price
        'high': None,                    # High price
        'low': None,                     # Low price
        'close': None,                   # Close price

        # === FEES & SLIPPAGE (FUTURES STANDARD) ===
        'fees': 0.0,                     # No percentage fees for futures
        'fixed_fees': 4.20,              # NQ Standard: $4.20 round-turn
        'slippage': 1.0,                 # Slippage in ticks (1-2 ticks typical)

        # === STOP LOSS & TAKE PROFIT (IN TICKS) ===
        'sl_stop': 25,                   # Stop loss: 25 ticks = 6.25 points = $31.25
        'sl_trail': False,               # Trailing stop loss
        'tp_stop': 50,                   # Take profit: 50 ticks = 12.5 points = $62.50
        'stop_entry_price': 'close',     # StopEntryPrice
        'stop_exit_price': 'stop',       # StopExitPrice
        'stop_exit_type': 'close',       # StopExitType
        'stop_update_mode': 'override',  # StopUpdateMode
        
        # === CONFLICT RESOLUTION ===
        'upon_long_conflict': 'ignore',      # ConflictMode for long signals
        'upon_short_conflict': 'ignore',     # ConflictMode for short signals  
        'upon_dir_conflict': 'ignore',       # DirectionConflictMode
        'upon_opposite_entry': 'ignore',     # OppositeEntryMode
        
        # === ADVANCED ===
        'log': False,                    # Logging
        'use_numba': True,               # Numba optimization
        'seed': "",                      # Random seed (leer = None)
        'freq': None,                    # Frequency
        'attach_call_seq': False,        # Attach call sequence
        'template_context': None,        # Template context
        'broadcast_named_args': None,    # Broadcasting
        'wrapper_kwargs': None,          # Wrapper kwargs
        'jitted': None,                  # Jitted functions

        # === SESSION TRADING ===
        'session_enabled': False,        # Session trading enabled
        'session_type': 'NEW_YORK',      # Session type (ASIA, LONDON, NEW_YORK, CUSTOM)
        'session_part': 'FULL',          # Session part (FULL, PART_1, PART_2)
        'custom_start': '09:30',         # Custom start time
        'custom_end': '16:00',           # Custom end time
        'sim_start': None,               # Simulation start (calculated from session)
        'sim_end': None,                 # Simulation end (calculated from session)
    }
    
    # === PARAMETER KATEGORIEN ===
    PARAMETER_CATEGORIES = {
        'essential': {
            'name': 'Essential Parameters',
            'description': 'Grundlegende Trading-Parameter',
            'parameters': [
                'init_cash', 'size', 'size_type', 'direction',
                'fixed_fees', 'slippage', 'sl_stop', 'tp_stop', 'tick_size',
                'log', 'use_numba', 'cash_sharing', 'jitted', 'seed',
                'session_enabled', 'session_type', 'session_part'
            ]
        },
        'advanced': {
            'name': 'Advanced Parameters', 
            'description': 'Erweiterte Risk Management Parameter',
            'parameters': [
                'accumulate', 'cash_sharing', 'stop_entry_price',
                'stop_exit_price', 'stop_update_mode', 'sl_trail'
            ]
        },
        'professional': {
            'name': 'Professional Parameters',
            'description': 'Professionelle Portfolio-Optimierung',
            'parameters': [
                'upon_long_conflict', 'upon_short_conflict', 
                'upon_dir_conflict', 'call_seq', 'group_by'
            ]
        }
    }
    
    # === PARAMETER VALIDIERUNG ===
    PARAMETER_VALIDATION = {
        'init_cash': {'min': 1000, 'max': 10000000, 'type': float},
        'size': {'min': 0.01, 'max': 1000000, 'type': float},
        'fees': {'min': 0.0, 'max': 0.1, 'type': float},
        'slippage': {'min': 0.0, 'max': 0.05, 'type': float},
        'sl_stop': {'min': 0.001, 'max': 0.5, 'type': float},
        'tp_stop': {'min': 0.001, 'max': 2.0, 'type': float},
    }
    
    # === ENUM CHOICES (aus VBT Pro Dokumentation) ===
    ENUM_CHOICES = {
        'size_type': [
            ('amount', 'Amount - Anzahl Assets'),
            ('value', 'Value - Geldwert'),
            ('percent', 'Percent - Prozent (0.01 = 1%)'),
            ('percent100', 'Percent100 - Prozent (1.0 = 1%)'),
            ('valuepercent', 'ValuePercent - Prozent des Portfolio-Werts'),
            ('targetamount', 'TargetAmount - Ziel-Position'),
            ('targetpercent', 'TargetPercent - Ziel-Prozent')
        ],
        'direction': [
            ('longonly', 'Long Only - Nur Käufe'),
            ('shortonly', 'Short Only - Nur Verkäufe'),
            ('both', 'Both - Long & Short')
        ],
        'accumulate': [
            (False, 'Disabled - Keine Akkumulation'),
            (True, 'Enabled - Akkumulation aktiviert'),
            ('addonly', 'AddOnly - Nur hinzufügen'),
            ('removeonly', 'RemoveOnly - Nur reduzieren')
        ],
        'stop_entry_price': [
            ('valprice', 'ValPrice - Bewertungspreis'),
            ('open', 'Open - Eröffnungspreis'),
            ('close', 'Close - Schlusskurs'),
            ('price', 'Price - Order-Preis'),
            ('fillprice', 'FillPrice - Ausführungspreis')
        ],
        'stop_exit_price': [
            ('stop', 'Stop - Stop-Preis'),
            ('hardstop', 'HardStop - Harter Stop'),
            ('close', 'Close - Schlusskurs')
        ],
        'stop_exit_type': [
            ('close', 'Close - Position schließen'),
            ('closereduce', 'CloseReduce - Schließen/Reduzieren'),
            ('reverse', 'Reverse - Position umkehren'),
            ('reversereduce', 'ReverseReduce - Umkehren/Reduzieren')
        ],
        'upon_long_conflict': [
            ('ignore', 'Ignore - Konflikt ignorieren'),
            ('entry', 'Entry - Entry bevorzugen'),
            ('exit', 'Exit - Exit bevorzugen'),
            ('adjacent', 'Adjacent - Benachbarte Signale'),
            ('opposite', 'Opposite - Entgegengesetzte Signale')
        ],
        'upon_dir_conflict': [
            ('ignore', 'Ignore - Konflikt ignorieren'),
            ('long', 'Long - Long bevorzugen'),
            ('short', 'Short - Short bevorzugen'),
            ('adjacent', 'Adjacent - Benachbarte Richtung'),
            ('opposite', 'Opposite - Entgegengesetzte Richtung')
        ]
    }
    
    # === EXPORT TEMPLATES ===
    EXPORT_TEMPLATES = {
        'punkt5_strategy': {
            'format': 'python',
            'include_metadata': True,
            'include_indicators': False,
            'include_data_path': True,
            'compression': False
        },
        'punkt6_backtest': {
            'format': 'python',
            'include_metadata': True,
            'include_indicators': True,
            'include_data_path': True,
            'compression': False
        },
        'punkt7_optimization': {
            'format': 'json',
            'include_metadata': True,
            'include_indicators': False,
            'include_ranges': True,
            'compression': False
        }
    }

    @classmethod
    def ensure_directories(cls):
        """Erstellt notwendige Verzeichnisse"""
        for path in cls.PATHS.values():
            path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def apply_vbt_settings(cls):
        """Wendet VectorBT Pro Optimierungen an"""
        try:
            # Numba Optimierungen (vorsichtiger Ansatz)
            try:
                if cls.VBT_SETTINGS['numba_parallel']:
                    vbt.settings.numba['parallel'] = True
            except Exception:
                pass  # Ignoriere wenn nicht verfügbar

            try:
                if cls.VBT_SETTINGS['chunking_enabled']:
                    vbt.settings.chunking['enabled'] = True
                    vbt.settings.chunking['chunk_size'] = cls.VBT_SETTINGS['chunk_size']
            except Exception:
                pass  # Ignoriere wenn nicht verfügbar

            # Portfolio Einstellungen
            try:
                vbt.settings.portfolio['init_cash'] = cls.VBT_DEFAULTS['init_cash']
            except Exception:
                pass  # Ignoriere wenn nicht verfügbar

            print("✅ VectorBT Pro Optimierungen angewendet")

        except Exception as e:
            print(f"⚠️ VBT Einstellungen Warnung: {e}")

# Initialisierung beim Import
CONFIG.ensure_directories()
CONFIG.apply_vbt_settings()
