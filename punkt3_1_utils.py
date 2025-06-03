#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punkt3.1 Utils - Hilfsfunktionen und Datenmanagement
Enthält VBTDataManager und weitere Utility-Funktionen

Autor: AI Assistant
Datum: 2025-06-02
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime, timedelta

try:
    import vectorbtpro as vbt
    VBT_AVAILABLE = True
except ImportError:
    VBT_AVAILABLE = False
    print("VectorbtPro nicht verfügbar. Einige Funktionen sind eingeschränkt.")

try:
    import blosc
    BLOSC_AVAILABLE = True
except ImportError:
    BLOSC_AVAILABLE = False
    print("Blosc nicht verfügbar. .blosc Dateien können nicht geladen werden.")

try:
    import h5py
    H5PY_AVAILABLE = True
except ImportError:
    H5PY_AVAILABLE = False
    print("h5py nicht verfügbar. HDF5 Dateien können nicht geladen werden.")

class VBTDataManager:
    """
    Verwaltet das Laden und Analysieren von VectorbtPro-Daten
    """
    
    def __init__(self):
        self.supported_extensions = [
            '.pickle.blosc',
            '.pickle', 
            '.h5',
            '.hdf5',
            '.parquet',
            '.csv'
        ]
        self.cache = {}
        
    def scan_directory(self, directory: str, recursive: bool = True, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Scannt ein Verzeichnis nach unterstützten Dateien
        
        Args:
            directory: Zu scannendes Verzeichnis
            recursive: Rekursiv scannen
            max_depth: Maximale Scan-Tiefe
            
        Returns:
            Liste von Datei-Informationen
        """
        files = []
        directory = Path(directory)
        
        if not directory.exists():
            return files
            
        try:
            self._scan_directory_recursive(directory, files, recursive, max_depth, 0)
        except Exception as e:
            print(f"Fehler beim Scannen von {directory}: {e}")
            
        return sorted(files, key=lambda x: x['name'])
        
    def _scan_directory_recursive(self, directory: Path, files: List, recursive: bool, max_depth: int, current_depth: int):
        """Rekursive Hilfsfunktion für Directory-Scan"""
        if current_depth > max_depth:
            return
            
        try:
            for item in directory.iterdir():
                if item.is_file():
                    if self._is_supported_file(item):
                        file_info = self._get_file_info(item)
                        if file_info:
                            files.append(file_info)
                elif item.is_dir() and recursive and current_depth < max_depth:
                    self._scan_directory_recursive(item, files, recursive, max_depth, current_depth + 1)
        except PermissionError:
            pass  # Überspringe Verzeichnisse ohne Berechtigung
            
    def _is_supported_file(self, file_path: Path) -> bool:
        """Prüft ob eine Datei unterstützt wird"""
        file_str = str(file_path).lower()
        return any(file_str.endswith(ext) for ext in self.supported_extensions)
        
    def _get_file_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extrahiert Basis-Informationen über eine Datei"""
        try:
            stat = file_path.stat()
            
            # Dateityp bestimmen
            file_type = self._determine_file_type(file_path)
            
            return {
                'name': file_path.name,
                'path': str(file_path.absolute()),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'type': file_type,
                'extension': self._get_extension(file_path),
                'is_single_timeframe': self._is_single_timeframe(file_path),
                'is_multi_timeframe': self._is_multi_timeframe(file_path)
            }
        except Exception as e:
            print(f"Fehler beim Analysieren von {file_path}: {e}")
            return None
            
    def _determine_file_type(self, file_path: Path) -> str:
        """Bestimmt den Dateityp basierend auf der Erweiterung"""
        file_str = str(file_path).lower()
        
        if file_str.endswith('.pickle.blosc'):
            return 'VBT Blosc Pickle'
        elif file_str.endswith('.pickle'):
            return 'VBT Pickle'
        elif file_str.endswith(('.h5', '.hdf5')):
            return 'VBT HDF5'
        elif file_str.endswith('.parquet'):
            return 'Parquet'
        elif file_str.endswith('.csv'):
            return 'CSV'
        else:
            return 'Unknown'
            
    def _get_extension(self, file_path: Path) -> str:
        """Gibt die vollständige Erweiterung zurück"""
        file_str = str(file_path).lower()
        
        for ext in self.supported_extensions:
            if file_str.endswith(ext):
                return ext
        return file_path.suffix
        
    def _is_single_timeframe(self, file_path: Path) -> bool:
        """Prüft ob es sich um Single-Timeframe Daten handelt"""
        name = file_path.name.lower()
        return 'single' in name or ('multi' not in name and any(tf in name for tf in ['1m', '5m', '15m', '30m', '1h', '4h', '1d']))
        
    def _is_multi_timeframe(self, file_path: Path) -> bool:
        """Prüft ob es sich um Multi-Timeframe Daten handelt"""
        name = file_path.name.lower()
        return 'multi' in name or name.count('m') > 1 or name.count('h') > 1
        
    def load_data(self, file_path: str) -> Tuple[Any, Dict[str, Any]]:
        """
        Lädt Daten aus einer Datei
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            Tuple von (Daten, Metadata)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Datei nicht gefunden: {file_path}")
            
        # Cache prüfen
        cache_key = str(file_path.absolute())
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            data, metadata = self._load_data_by_type(file_path)
            
            # In Cache speichern
            self.cache[cache_key] = (data, metadata)
            
            return data, metadata
            
        except Exception as e:
            raise Exception(f"Fehler beim Laden von {file_path}: {str(e)}")
            
    def _load_data_by_type(self, file_path: Path) -> Tuple[Any, Dict[str, Any]]:
        """Lädt Daten basierend auf dem Dateityp"""
        file_str = str(file_path).lower()
        
        if file_str.endswith('.pickle.blosc'):
            return self._load_blosc_pickle(file_path)
        elif file_str.endswith('.pickle'):
            return self._load_pickle(file_path)
        elif file_str.endswith(('.h5', '.hdf5')):
            return self._load_hdf5(file_path)
        elif file_str.endswith('.parquet'):
            return self._load_parquet(file_path)
        elif file_str.endswith('.csv'):
            return self._load_csv(file_path)
        else:
            raise ValueError(f"Nicht unterstützter Dateityp: {file_path}")
            
    def _load_blosc_pickle(self, file_path: Path) -> Tuple[Any, Dict[str, Any]]:
        """Lädt .pickle.blosc Dateien"""
        if not BLOSC_AVAILABLE:
            raise ImportError("Blosc ist nicht verfügbar")
            
        try:
            # Versuche VBT-Loader
            if VBT_AVAILABLE:
                try:
                    data = vbt.Data.load(str(file_path))
                    metadata = self._extract_vbt_metadata(data)
                    return data, metadata
                except:
                    pass
                    
            # Fallback: Manuelles Laden
            with open(file_path, 'rb') as f:
                compressed_data = f.read()
                decompressed_data = blosc.decompress(compressed_data)
                data = pickle.loads(decompressed_data)
                
            metadata = self._extract_metadata(data, file_path)
            return data, metadata
            
        except Exception as e:
            raise Exception(f"Fehler beim Laden der Blosc-Datei: {e}")
            
    def _load_pickle(self, file_path: Path) -> Tuple[Any, Dict[str, Any]]:
        """Lädt .pickle Dateien"""
        try:
            # Versuche VBT-Loader
            if VBT_AVAILABLE:
                try:
                    data = vbt.load(str(file_path))
                    metadata = self._extract_vbt_metadata(data)
                    return data, metadata
                except:
                    pass
                    
            # Fallback: Standard Pickle
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                
            metadata = self._extract_metadata(data, file_path)
            return data, metadata
            
        except Exception as e:
            raise Exception(f"Fehler beim Laden der Pickle-Datei: {e}")
            
    def _load_hdf5(self, file_path: Path) -> Tuple[Any, Dict[str, Any]]:
        """Lädt HDF5 Dateien"""
        if not H5PY_AVAILABLE:
            raise ImportError("h5py ist nicht verfügbar")
            
        try:
            # Versuche VBT-Loader
            if VBT_AVAILABLE:
                try:
                    data = vbt.Data.load(str(file_path))
                    metadata = self._extract_vbt_metadata(data)
                    return data, metadata
                except:
                    pass
                    
            # Fallback: Pandas HDF5
            data = pd.read_hdf(str(file_path))
            metadata = self._extract_metadata(data, file_path)
            return data, metadata
            
        except Exception as e:
            raise Exception(f"Fehler beim Laden der HDF5-Datei: {e}")
            
    def _load_parquet(self, file_path: Path) -> Tuple[Any, Dict[str, Any]]:
        """Lädt Parquet Dateien"""
        try:
            data = pd.read_parquet(str(file_path))
            metadata = self._extract_metadata(data, file_path)
            return data, metadata
        except Exception as e:
            raise Exception(f"Fehler beim Laden der Parquet-Datei: {e}")
            
    def _load_csv(self, file_path: Path) -> Tuple[Any, Dict[str, Any]]:
        """Lädt CSV Dateien"""
        try:
            # Versuche verschiedene CSV-Formate
            for sep in [',', ';', '\t']:
                try:
                    data = pd.read_csv(str(file_path), sep=sep, index_col=0, parse_dates=True)
                    if len(data.columns) > 1:  # Erfolgreich geladen
                        break
                except:
                    continue
            else:
                # Standard CSV
                data = pd.read_csv(str(file_path))
                
            metadata = self._extract_metadata(data, file_path)
            return data, metadata
        except Exception as e:
            raise Exception(f"Fehler beim Laden der CSV-Datei: {e}")
            
    def _extract_vbt_metadata(self, data) -> Dict[str, Any]:
        """Extrahiert Metadaten aus VBT-Objekten"""
        metadata = {
            'source': 'VectorbtPro',
            'type': type(data).__name__,
            'loaded_at': datetime.now().isoformat()
        }
        
        try:
            if hasattr(data, 'wrapper'):
                wrapper = data.wrapper
                metadata.update({
                    'shape': wrapper.shape,
                    'columns': list(wrapper.columns) if hasattr(wrapper, 'columns') else [],
                    'index_start': str(wrapper.index[0]) if len(wrapper.index) > 0 else None,
                    'index_end': str(wrapper.index[-1]) if len(wrapper.index) > 0 else None,
                    'freq': str(wrapper.freq) if hasattr(wrapper, 'freq') else None
                })
                
            if hasattr(data, 'close'):
                metadata['has_ohlcv'] = True
                metadata['symbols'] = list(data.close.columns) if hasattr(data.close, 'columns') else []
                
        except Exception as e:
            print(f"Fehler beim Extrahieren von VBT-Metadaten: {e}")
            
        return metadata
        
    def _extract_metadata(self, data, file_path: Path) -> Dict[str, Any]:
        """Extrahiert allgemeine Metadaten"""
        metadata = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_size': file_path.stat().st_size,
            'loaded_at': datetime.now().isoformat(),
            'data_type': type(data).__name__
        }
        
        try:
            if isinstance(data, pd.DataFrame):
                metadata.update({
                    'shape': data.shape,
                    'columns': list(data.columns),
                    'index_start': str(data.index[0]) if len(data.index) > 0 else None,
                    'index_end': str(data.index[-1]) if len(data.index) > 0 else None,
                    'memory_usage': data.memory_usage(deep=True).sum()
                })
            elif isinstance(data, dict):
                metadata.update({
                    'keys': list(data.keys()),
                    'num_keys': len(data)
                })
                
                # Analysiere Dictionary-Inhalte
                for key, value in data.items():
                    if isinstance(value, pd.DataFrame):
                        metadata[f'{key}_shape'] = value.shape
                        metadata[f'{key}_columns'] = list(value.columns)
                        
        except Exception as e:
            print(f"Fehler beim Extrahieren von Metadaten: {e}")
            
        # Suche nach separater Metadaten-Datei
        metadata_file = self._find_metadata_file(file_path)
        if metadata_file:
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    external_metadata = json.load(f)
                metadata['external_metadata'] = external_metadata
            except Exception as e:
                print(f"Fehler beim Laden der externen Metadaten: {e}")
                
        return metadata
        
    def _find_metadata_file(self, data_file: Path) -> Optional[Path]:
        """Sucht nach einer separaten Metadaten-Datei"""
        base_name = data_file.stem
        if base_name.endswith('.pickle'):
            base_name = base_name[:-7]  # Entferne .pickle
            
        metadata_patterns = [
            f"{base_name}_metadata.json",
            f"{base_name}.metadata.json",
            f"{base_name}_meta.json",
            f"{data_file.stem}_metadata.json"
        ]
        
        for pattern in metadata_patterns:
            metadata_file = data_file.parent / pattern
            if metadata_file.exists():
                return metadata_file
                
        return None
        
    def analyze_data(self, data, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analysiert geladene Daten und erstellt einen detaillierten Bericht
        
        Args:
            data: Die geladenen Daten
            metadata: Metadaten
            
        Returns:
            Analyse-Bericht
        """
        analysis = {
            'basic_info': self._analyze_basic_info(data, metadata),
            'timeframe_info': self._analyze_timeframe(data, metadata),
            'asset_info': self._analyze_assets(data, metadata),
            'indicators': self._analyze_indicators(data, metadata),
            'performance_features': self._analyze_performance_features(data, metadata),
            'available_features': self._get_available_vbt_features(data)
        }
        
        return analysis
        
    def _analyze_basic_info(self, data, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analysiert Basis-Informationen"""
        info = {
            'data_type': type(data).__name__,
            'file_size_mb': metadata.get('file_size', 0) / (1024 * 1024),
            'loaded_at': metadata.get('loaded_at')
        }
        
        if isinstance(data, pd.DataFrame):
            info.update({
                'shape': data.shape,
                'columns': list(data.columns),
                'memory_usage_mb': data.memory_usage(deep=True).sum() / (1024 * 1024)
            })
        elif isinstance(data, dict):
            info.update({
                'num_keys': len(data),
                'keys': list(data.keys())
            })
            
        return info
        
    def _analyze_timeframe(self, data, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analysiert Zeitrahmen-Informationen"""
        timeframe_info = {
            'is_single_timeframe': False,
            'is_multi_timeframe': False,
            'timeframes': [],
            'date_range': None
        }
        
        try:
            if isinstance(data, dict):
                # Multi-Timeframe Daten
                timeframes = []
                for key in data.keys():
                    if any(tf in str(key).lower() for tf in ['1m', '5m', '15m', '30m', '1h', '4h', '1d']):
                        timeframes.append(key)
                        
                if timeframes:
                    timeframe_info['is_multi_timeframe'] = True
                    timeframe_info['timeframes'] = timeframes
                    
            elif hasattr(data, 'wrapper') and hasattr(data.wrapper, 'freq'):
                # VBT Data mit Frequenz
                freq = str(data.wrapper.freq)
                timeframe_info['is_single_timeframe'] = True
                timeframe_info['timeframes'] = [freq]
                
                if hasattr(data.wrapper, 'index') and len(data.wrapper.index) > 0:
                    timeframe_info['date_range'] = {
                        'start': str(data.wrapper.index[0]),
                        'end': str(data.wrapper.index[-1]),
                        'periods': len(data.wrapper.index)
                    }
                    
        except Exception as e:
            print(f"Fehler bei Zeitrahmen-Analyse: {e}")
            
        return timeframe_info
        
    def _analyze_assets(self, data, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analysiert Asset-Informationen"""
        asset_info = {
            'symbols': [],
            'num_symbols': 0
        }
        
        try:
            if hasattr(data, 'close') and hasattr(data.close, 'columns'):
                symbols = list(data.close.columns)
                asset_info['symbols'] = symbols
                asset_info['num_symbols'] = len(symbols)
            elif isinstance(data, pd.DataFrame) and 'symbol' in data.columns:
                symbols = data['symbol'].unique().tolist()
                asset_info['symbols'] = symbols
                asset_info['num_symbols'] = len(symbols)
                
        except Exception as e:
            print(f"Fehler bei Asset-Analyse: {e}")
            
        return asset_info
        
    def _analyze_indicators(self, data, metadata: Dict[str, Any]) -> List[str]:
        """Analysiert vorhandene Indikatoren"""
        indicators = []
        
        try:
            if isinstance(data, dict):
                for key, value in data.items():
                    if 'indicator' in str(key).lower() or 'ta' in str(key).lower():
                        indicators.append(key)
                        
            elif isinstance(data, pd.DataFrame):
                # Suche nach typischen Indikator-Spalten
                indicator_patterns = ['sma', 'ema', 'rsi', 'macd', 'bb', 'atr', 'stoch']
                for col in data.columns:
                    col_lower = str(col).lower()
                    if any(pattern in col_lower for pattern in indicator_patterns):
                        indicators.append(col)
                        
        except Exception as e:
            print(f"Fehler bei Indikator-Analyse: {e}")
            
        return indicators
        
    def _analyze_performance_features(self, data, metadata: Dict[str, Any]) -> List[str]:
        """Analysiert vorhandene Performance-Features"""
        features = []
        
        try:
            if hasattr(data, '__dict__'):
                attrs = dir(data)
                vbt_features = ['returns', 'trades', 'positions', 'orders', 'portfolio']
                for feature in vbt_features:
                    if feature in attrs:
                        features.append(feature)
                        
        except Exception as e:
            print(f"Fehler bei Performance-Feature-Analyse: {e}")
            
        return features
        
    def _get_available_vbt_features(self, data) -> List[str]:
        """Gibt verfügbare VBT-Features zurück, die hinzugefügt werden könnten"""
        if not VBT_AVAILABLE:
            return []
            
        available_features = [
            'Technical Indicators (RSI, MACD, Bollinger Bands)',
            'Portfolio Analytics',
            'Risk Metrics',
            'Performance Statistics',
            'Drawdown Analysis',
            'Trade Analysis',
            'Position Sizing',
            'Backtesting Framework'
        ]
        
        return available_features
        
    def clear_cache(self):
        """Leert den Daten-Cache"""
        self.cache.clear()
        
    def get_cache_info(self) -> Dict[str, Any]:
        """Gibt Cache-Informationen zurück"""
        return {
            'cached_files': len(self.cache),
            'cache_keys': list(self.cache.keys())
        }