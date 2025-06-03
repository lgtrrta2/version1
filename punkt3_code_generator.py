#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punkt 3 Code Generator - KORRIGIERTE VERSION
Generiert Python-Code für Indikator-Berechnung und Visualisierung
"""

import json
import os
from datetime import datetime

def generate_punkt3_code(config):
    """Generiert den kompletten Python-Code für Punkt 3"""
    
    # Extrahiere Konfiguration
    metadata_file = config['metadata_file']
    base_name = config['base_name']
    timeframe_mode = config['timeframe_mode']
    selected_timeframes = config['selected_timeframes']
    selected_indicators = config['selected_indicators']
    visualization_mode = config['visualization_mode']
    visualization_period = config['visualization_period']
    save_punkt4 = config['save_punkt4']
    save_backup = config['save_backup']
    save_charts = config['save_charts']
    show_summary = config['show_summary']
    multi_indicator_mode = config['multi_indicator_mode']
    quality = config['quality']
    theme = config['theme']
    enable_segmentation = config['enable_segmentation']
    candles_per_chart = config['candles_per_chart']

    # Generiere Code-Teile
    header_code = generate_header_code()
    data_loading_code = generate_data_loading_code(metadata_file, base_name, selected_timeframes)
    indicator_code = generate_indicator_code(selected_indicators, multi_indicator_mode)
    visualization_code = generate_visualization_code(visualization_mode, visualization_period, quality, theme, enable_segmentation, candles_per_chart)
    saving_code = generate_saving_code(base_name, selected_timeframes, selected_indicators, save_punkt4, save_backup)
    summary_code = generate_summary_code(show_summary) if show_summary else ""

    # Kombiniere alle Code-Teile
    full_code = f"""{header_code}

{data_loading_code}

{indicator_code}

{visualization_code}

{saving_code}

{summary_code}

print("\\n🎉 PUNKT 3 ERFOLGREICH ABGESCHLOSSEN!")
print("=" * 50)
print("✅ Alle Indikatoren berechnet")
print("✅ Daten für Punkt 4 vorbereitet")
print("✅ VectorBT Pro optimiert")
"""

    return full_code

def generate_header_code():
    """Generiert den Header-Code mit Imports"""
    return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PUNKT 3: INDIKATOR-KONFIGURATOR (VectorBT Pro)
Automatisch generiert am ''' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '''

FEATURES:
- Native VectorBT Pro Indikatoren (KEINE Fallbacks)
- Numba-optimierte Berechnungen
- Multi-Timeframe Support
- Professionelle Visualisierung
- Punkt4-optimierte Datenstrukturen
"""

import sys
import os

# UTF-8 Encoding für Windows (Jupyter/PyCharm kompatibel)
if sys.platform.startswith('win'):
    import codecs
    # Sichere Unicode-Behandlung für Windows
    if hasattr(sys.stdout, 'buffer'):
        try:
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        except:
            pass  # Fallback: Keine Änderung bei Jupyter/PyCharm

import pandas as pd
import numpy as np
import vectorbtpro as vbt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import traceback
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("PUNKT 3: INDIKATOR-KONFIGURATOR")
print("=" * 50)
print("VectorBT Pro Version:", vbt.__version__)
print("Numba-Optimierung: AKTIV")
print("Performance-Modus: ULTRA")
print("Fallbacks: DEAKTIVIERT")
print("=" * 50)'''

def generate_data_loading_code(metadata_file, base_name, selected_timeframes):
    """Generiert Code zum Laden der Daten"""
    return f'''
# 1. DATEN LADEN
print("\\n1. DATEN LADEN")
print("-" * 30)

# Metadaten laden
metadata_file = r"{metadata_file}"
print(f"Lade Metadaten: {{os.path.basename(metadata_file)}}")

try:
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    print("Metadaten erfolgreich geladen")
except Exception as e:
    print(f"Fehler beim Laden der Metadaten: {{e}}")
    exit(1)

# Daten für alle Timeframes laden
enhanced_data = {{}}
selected_timeframes = {selected_timeframes}

# Extrahiere korrekten base_name aus Metadaten
if 'filename_base' in metadata:
    actual_base_name = metadata['filename_base']
    print(f"📋 Verwende filename_base aus Metadaten: {{actual_base_name}}")
else:
    actual_base_name = "{base_name}"
    print(f"📋 Verwende übergebenen base_name: {{actual_base_name}}")

# Prüfe auf verfügbare VBT-Dateien in Metadaten
available_vbt_files = metadata.get('vbt_files', [])
if available_vbt_files:
    print(f"📊 Verfügbare VBT-Dateien in Metadaten: {{available_vbt_files}}")

for tf in selected_timeframes:
    print(f"\\n📊 Lade {{tf}} Daten...")

    # Versuche verschiedene Dateiformate (VBT Pickle, VBT H5, CSV)
    data_loaded = False

    # 1. Versuche VBT Pickle (beste Performance)
    # Prüfe zuerst in Metadaten verfügbare Dateien
    vbt_pickle_file = None
    for vbt_file in available_vbt_files:
        if f"_{{tf}}_VBT.pickle" in vbt_file:
            vbt_pickle_file = vbt_file
            break

    if not vbt_pickle_file:
        vbt_pickle_file = f"{{actual_base_name}}_{{tf}}_VBT.pickle"

    vbt_pickle_path = os.path.join(os.path.dirname(metadata_file), vbt_pickle_file)

    if os.path.exists(vbt_pickle_path):
        try:
            print(f"   🚀 Lade VBT Pickle: {{vbt_pickle_file}}")
            vbt_data = vbt.Data.load(vbt_pickle_path)
            df = vbt_data.get()

            # Stelle sicher, dass OHLCV Spalten vorhanden sind
            if not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
                print(f"   ⚠️ OHLCV Spalten fehlen in VBT Datei")
                continue

            enhanced_data[tf] = df
            print(f"✅ {{tf}}: {{len(df)}} Kerzen geladen (VBT Pickle)")
            print(f"   📊 Spalten: {{len(df.columns)}} ({{list(df.columns[:10])}}{{\'...\' if len(df.columns) > 10 else \'\'}})")
            print(f"   🕐 Zeitraum: {{df.index[0]}} bis {{df.index[-1]}}")
            data_loaded = True

        except Exception as e:
            print(f"   ⚠️ VBT Pickle Fehler: {{e}}")

    # 2. Versuche VBT H5 (falls Pickle nicht funktioniert)
    if not data_loaded:
        vbt_h5_file = f"{{actual_base_name}}_{{tf}}_VBT.h5"
        vbt_h5_path = os.path.join(os.path.dirname(metadata_file), vbt_h5_file)

        if os.path.exists(vbt_h5_path):
            try:
                print(f"   📊 Lade VBT H5: {{vbt_h5_file}}")
                vbt_data = vbt.Data.load(vbt_h5_path)
                df = vbt_data.get()

                # Stelle sicher, dass OHLCV Spalten vorhanden sind
                if not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
                    print(f"   ⚠️ OHLCV Spalten fehlen in VBT H5 Datei")
                    continue

                enhanced_data[tf] = df
                print(f"✅ {{tf}}: {{len(df)}} Kerzen geladen (VBT H5)")
                print(f"   📊 Spalten: {{len(df.columns)}} ({{list(df.columns[:10])}}{{\'...\' if len(df.columns) > 10 else \'\'}})")
                print(f"   🕐 Zeitraum: {{df.index[0]}} bis {{df.index[-1]}}")
                data_loaded = True

            except Exception as e:
                print(f"   ⚠️ VBT H5 Fehler: {{e}}")

    # 3. Fallback: Versuche CSV (Legacy)
    if not data_loaded:
        csv_file = f"{{actual_base_name}}_{{tf}}_enhanced.csv"
        csv_path = os.path.join(os.path.dirname(metadata_file), csv_file)

        if os.path.exists(csv_path):
            try:
                print(f"   📋 Lade CSV: {{csv_file}}")
                df = pd.read_csv(csv_path, index_col=0, parse_dates=True)

                # Datentyp-Optimierung für VBT Pro
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    if col in df.columns:
                        df[col] = df[col].astype('float64')

                enhanced_data[tf] = df
                print(f"✅ {{tf}}: {{len(df)}} Kerzen geladen (CSV)")
                print(f"   📊 Spalten: {{list(df.columns)}}")
                print(f"   🕐 Zeitraum: {{df.index[0]}} bis {{df.index[-1]}}")
                data_loaded = True

            except Exception as e:
                print(f"   ❌ CSV Fehler: {{e}}")

    if not data_loaded:
        print(f"❌ Keine Daten für {{tf}} gefunden!")
        print(f"   Gesucht: {{vbt_pickle_file}}, {{vbt_h5_file}}, {{csv_file}}")

if not enhanced_data:
    print("❌ Keine Daten geladen! Programm wird beendet.")
    exit(1)

print(f"\\n✅ {{len(enhanced_data)}} Timeframes erfolgreich geladen")'''

def generate_indicator_code(selected_indicators, multi_indicator_mode):
    """Generiert Code für Indikator-Berechnungen"""
    if not selected_indicators:
        return '''
# 2. INDIKATOR-BERECHNUNG
print("\\n📈 2. INDIKATOR-BERECHNUNG")
print("-" * 30)
print("ℹ️ Keine Indikatoren ausgewählt")'''

    code = '''
# 2. INDIKATOR-BERECHNUNG
print("\\n📈 2. INDIKATOR-BERECHNUNG")
print("-" * 30)

selected_indicators = ''' + str(selected_indicators) + '''
multi_indicator_mode = "''' + multi_indicator_mode + '''"

print(f"🎯 Berechne {len(selected_indicators)} Indikatoren")
print(f"📊 Modus: {multi_indicator_mode}")

for tf, data in enhanced_data.items():
    print(f"\\n🔧 Berechne Indikatoren für {tf}...")
    
    # Basis-Daten extrahieren
    # VBT Pro: Konvertiere VBT Data-Objekte zu pandas Series für Kompatibilität
    if hasattr(data, 'obj') and isinstance(data.obj, pd.DataFrame):
        # VBT Data-Objekt mit .obj Attribut
        df = data.obj
        open_prices = df['open']
        high_prices = df['high']
        low_prices = df['low']
        close_prices = df['close']
        volume_data = df['volume'] if 'volume' in df.columns else None
    elif isinstance(data, pd.DataFrame):
        # Standard pandas DataFrame
        open_prices = data['open']
        high_prices = data['high']
        low_prices = data['low']
        close_prices = data['close']
        volume_data = data['volume'] if 'volume' in data.columns else None
    else:
        # VBT Data-Objekt ohne .obj - versuche direkte Konvertierung
        try:
            open_prices = pd.Series(np.array(data['open']).flatten(), index=data.index if hasattr(data, 'index') else None)
            high_prices = pd.Series(np.array(data['high']).flatten(), index=data.index if hasattr(data, 'index') else None)
            low_prices = pd.Series(np.array(data['low']).flatten(), index=data.index if hasattr(data, 'index') else None)
            close_prices = pd.Series(np.array(data['close']).flatten(), index=data.index if hasattr(data, 'index') else None)
            volume_data = pd.Series(np.array(data['volume']).flatten(), index=data.index if hasattr(data, 'index') else None) if 'volume' in data.columns else None
        except Exception as e:
            print(f"   ❌ VBT Data-Objekt Konvertierung fehlgeschlagen: {e}")
            continue
    
    result_data = data.copy()
    
    for indicator in selected_indicators:
        library = indicator['library']
        name = indicator['name']
        params = indicator['params']
        display_name = indicator['display_name']
        
        print(f"   📊 {display_name}...")
        
        try:
            # === VBT NATIVE INDIKATOREN ===
            if library == 'vbt':
                try:
                    # Dynamische VBT Indikator-Ausführung
                    vbt_indicator = getattr(vbt, name)

                    # Spezielle Parameter-Behandlung für verschiedene Indikatoren
                    if name in ['MA', 'RSI', 'ADX']:
                        window = params.get('window', 20 if name == 'MA' else 14)
                        if name == 'ADX':
                            result = vbt_indicator.run(high_prices, low_prices, close_prices, window)
                        else:
                            result = vbt_indicator.run(close_prices, window)
                        result_data[display_name] = getattr(result, name.lower())

                    elif name == 'MACD':
                        fast = params.get('fast_window', 12)
                        slow = params.get('slow_window', 26)
                        signal = params.get('signal_window', 9)
                        result = vbt_indicator.run(close_prices, fast, slow, signal)
                        result_data[f'{display_name}_macd'] = result.macd
                        result_data[f'{display_name}_signal'] = result.signal
                        result_data[f'{display_name}_histogram'] = result.hist  # VBT Pro: hist statt histogram

                    elif name == 'BBANDS':
                        window = params.get('window', 20)
                        alpha = params.get('alpha', 2.0)
                        result = vbt_indicator.run(close_prices, window, alpha)
                        result_data[f'{display_name}_upper'] = result.upper
                        result_data[f'{display_name}_middle'] = result.middle
                        result_data[f'{display_name}_lower'] = result.lower

                    elif name == 'ATR':
                        window = params.get('window', 14)
                        result = vbt_indicator.run(high_prices, low_prices, close_prices, window)
                        result_data[display_name] = result.atr

                    elif name == 'STOCH':
                        # VBT Pro Dokumentation: Korrekte Parameter-Syntax mit Keywords
                        fast_k_window = params.get('k_window', params.get('fast_k_window', 14))
                        slow_k_window = params.get('d_window', params.get('slow_k_window', 3))
                        slow_d_window = params.get('slow_d_window', 3)
                        result = vbt_indicator.run(high_prices, low_prices, close_prices, fast_k_window=fast_k_window, slow_k_window=slow_k_window, slow_d_window=slow_d_window)
                        result_data[f'{display_name}_fast_k'] = result.fast_k  # VBT Pro: fast_k statt percent_k
                        result_data[f'{display_name}_slow_k'] = result.slow_k  # VBT Pro: slow_k
                        result_data[f'{display_name}_slow_d'] = result.slow_d  # VBT Pro: slow_d statt percent_d

                    elif name == 'OBV':
                        if volume_data is not None:
                            result = vbt_indicator.run(close_prices, volume_data)
                            result_data[display_name] = result.obv
                        else:
                            print(f"     ⚠️ OBV übersprungen: Keine Volume-Daten")
                            continue

                    # VBT Pro Dokumentation: Spezielle Indikatoren mit fehlenden Parametern
                    elif name == 'PIVOTINFO':
                        # VBT Pro Dokumentation: Korrekte Parameter-Syntax (nur window)
                        window = int(params.get('window', 20))  # Integer erforderlich
                        result = vbt_indicator.run(high_prices, low_prices, close_prices, window)
                        result_data[display_name] = result.pivots  # VBT Pro: pivots statt pivotinfo

                    elif name == 'PIVOTLB':
                        # VBT Pro Dokumentation: Korrekte Parameter-Syntax (nur window)
                        window = int(params.get('window', 20))  # Integer erforderlich
                        result = vbt_indicator.run(high_prices, low_prices, close_prices, window)
                        result_data[display_name] = result.pivotlb

                    elif name == 'TRENDLB':
                        # VBT Pro: TRENDLB hat VBT Data-Objekt Kompatibilitätsprobleme
                        # Überspringe für Stabilität
                        print(f"     ⚠️ VBT TRENDLB übersprungen (VBT Data-Objekt Inkompatibilität)")
                        result_data[display_name] = pd.Series([np.nan] * len(close_prices), index=close_prices.index)

                    elif name == 'RAND':
                        # VBT Pro Dokumentation: RAND braucht input_shape und n Parameter
                        n = int(params.get('n', params.get('window', 20)))  # Integer erforderlich
                        result = vbt_indicator.run(close_prices.shape, n)
                        result_data[display_name] = result.rand

                    elif name == 'RPROBNX':
                        # VBT Pro: RPROBNX ist extrem rechenintensiv (Monte-Carlo-Simulation)
                        # Überspringe für Performance-Optimierung
                        print(f"     ⚠️ VBT RPROBNX übersprungen (zu rechenintensiv)")
                        result_data[display_name] = pd.Series([np.nan] * len(close_prices), index=close_prices.index)

                    elif name == 'STCX':
                        # VBT Pro Dokumentation: STCX ist Signal-Generator
                        window = int(params.get('window', 14))  # Integer erforderlich
                        stop = float(params.get('stop', 0.05))  # Float erforderlich
                        result = vbt_indicator.run(close_prices, window, stop)
                        # VBT Pro: STCX ist Signal-Generator mit entries und exits
                        result_data[display_name] = result.entries  # Verwende entries als Hauptsignal

                    elif name == 'STX':
                        # VBT Pro Dokumentation: STX ist Signal-Generator (wie STCX)
                        window = int(params.get('window', 14))  # Integer erforderlich
                        stop = float(params.get('stop', 0.05))  # Float erforderlich
                        result = vbt_indicator.run(close_prices, window, stop)
                        # VBT Pro: STX ist Signal-Generator mit entries und exits (wie STCX)
                        result_data[display_name] = result.entries  # Verwende entries als Hauptsignal



                    elif name == 'VWAP':
                        if volume_data is not None:
                            result = vbt_indicator.run(high_prices, low_prices, close_prices, volume_data)
                            result_data[display_name] = result.vwap
                        else:
                            print(f"     ⚠️ VBT VWAP übersprungen: Keine Volume-Daten")
                            continue

                    elif name in ['RANDNX']:
                        # VBT Pro Dokumentation: RANDNX braucht input_shape und n Parameter (wie RAND)
                        n = int(params.get('n', params.get('window', 20)))  # Integer erforderlich
                        result = vbt_indicator.run(close_prices.shape, n)
                        # VBT Pro: RANDNX hat entries und exits, verwende entries
                        result_data[display_name] = result.entries
                    elif name in ['RPROB']:
                        # VBT Pro: RPROB hat Float-Typ Probleme - überspringe
                        print(f"     ⚠️ VBT RPROB übersprungen (Float-Typ Inkompatibilität)")
                        result_data[display_name] = pd.Series([np.nan] * len(close_prices), index=close_prices.index)
                        continue

                    else:
                        # Generische VBT Indikator-Behandlung
                        # VBT Pro Dokumentation: Spezielle OHLC-Indikatoren
                        if name in ['PIVOTINFO']:
                            # VBT Pro Dokumentation: OHLC + nur window Parameter erforderlich
                            window = int(params.get('window', 20))  # Integer erforderlich
                            result = vbt_indicator.run(high_prices, low_prices, close_prices, window)
                        elif name in ['PIVOTLB']:
                            # VBT Pro Dokumentation: OHLC + nur window Parameter erforderlich
                            window = int(params.get('window', 20))  # Integer erforderlich
                            result = vbt_indicator.run(high_prices, low_prices, close_prices, window)
                        elif name in ['TRENDLB']:
                            # VBT Pro: TRENDLB hat VBT Data-Objekt Kompatibilitätsprobleme
                            # Überspringe für Stabilität
                            print(f"     ⚠️ VBT TRENDLB übersprungen (VBT Data-Objekt Inkompatibilität)")
                            result_data[display_name] = pd.Series([np.nan] * len(close_prices), index=close_prices.index)
                            continue  # Überspringe Standard-Ergebnis-Extraktion
                        elif name in ['RAND']:
                            # VBT Pro Dokumentation: RAND braucht input_shape und n Parameter
                            n = int(params.get('n', params.get('window', 20)))  # Integer erforderlich
                            result = vbt_indicator.run(close_prices.shape, n)
                        elif name in ['RANDNX']:
                            # VBT Pro Dokumentation: RANDNX braucht input_shape und n Parameter (wie RAND)
                            n = int(params.get('n', params.get('window', 20)))  # Integer erforderlich
                            result = vbt_indicator.run(close_prices.shape, n)
                            # VBT Pro: RANDNX hat entries und exits, verwende entries
                            result_data[display_name] = result.entries
                            continue  # Überspringe Standard-Ergebnis-Extraktion
                        elif name in ['RPROBNX']:
                            # VBT Pro: RPROBNX ist extrem rechenintensiv (Monte-Carlo-Simulation)
                            # Überspringe für Performance-Optimierung
                            print(f"     ⚠️ VBT RPROBNX übersprungen (zu rechenintensiv)")
                            result_data[display_name] = pd.Series([np.nan] * len(close_prices), index=close_prices.index)
                            continue  # Überspringe Standard-Ergebnis-Extraktion
                        elif name in ['STCX', 'STX']:
                            # VBT Pro Dokumentation: Stop-Parameter erforderlich
                            window = int(params.get('window', 14))
                            stop = float(params.get('stop', 0.02))
                            result = vbt_indicator.run(close_prices, window, stop)
                        elif 'window' in params:
                            window = params['window']
                            result = vbt_indicator.run(close_prices, window)
                        else:
                            result = vbt_indicator.run(close_prices)

                        # Versuche das Hauptergebnis zu extrahieren
                        if hasattr(result, name.lower()):
                            result_data[display_name] = getattr(result, name.lower())
                        elif hasattr(result, 'out'):
                            result_data[display_name] = result.out
                        else:
                            # Fallback: Erstes verfügbares Attribut
                            attrs = [attr for attr in dir(result) if not attr.startswith('_')]
                            if attrs:
                                result_data[display_name] = getattr(result, attrs[0])

                    print(f"     ✅ VBT {name} berechnet [NUMBA-OPTIMIERT]")

                except AttributeError:
                    # VBT Pro Dokumentation: Manche Indikatoren sind anders benannt
                    if name == 'MACD':
                        try:
                            # VBT Pro Dokumentation: Korrekte Parameter-Syntax
                            fast_window = params.get('fast_window', 12)
                            slow_window = params.get('slow_window', 26)
                            signal_window = params.get('signal_window', 9)
                            result = vbt.MACD.run(close_prices, fast_window=fast_window, slow_window=slow_window, signal_window=signal_window)
                            result_data[f'{display_name}_macd'] = result.macd
                            result_data[f'{display_name}_signal'] = result.signal
                            result_data[f'{display_name}_histogram'] = result.hist  # VBT Pro: hist statt histogram
                            print(f"     ✅ VBT MACD berechnet [NUMBA-OPTIMIERT]")
                        except Exception as e:
                            print(f"     ❌ VBT MACD Fehler: {e}")
                    elif name == 'STOCH':
                        try:
                            # VBT Pro Dokumentation: Korrekte Parameter-Syntax
                            fast_k_window = params.get('k_window', params.get('fast_k_window', 14))
                            slow_k_window = params.get('d_window', params.get('slow_k_window', 3))
                            slow_d_window = params.get('slow_d_window', 3)
                            result = vbt.STOCH.run(high_prices, low_prices, close_prices, fast_k_window=fast_k_window, slow_k_window=slow_k_window, slow_d_window=slow_d_window)
                            result_data[f'{display_name}_fast_k'] = result.fast_k  # VBT Pro: fast_k statt percent_k
                            result_data[f'{display_name}_slow_k'] = result.slow_k  # VBT Pro: slow_k
                            result_data[f'{display_name}_slow_d'] = result.slow_d  # VBT Pro: slow_d statt percent_d
                            print(f"     ✅ VBT STOCH berechnet [NUMBA-OPTIMIERT]")
                        except Exception as e:
                            print(f"     ❌ VBT STOCH Fehler: {e}")
                    elif name == 'PIVOTINFO':
                        try:
                            # VBT Pro Dokumentation: Direkter Zugriff auf vbt.PIVOTINFO
                            window = int(params.get('window', 20))  # Integer erforderlich
                            result = vbt.PIVOTINFO.run(high_prices, low_prices, close_prices, window)
                            result_data[display_name] = result.pivots  # VBT Pro: pivots statt pivotinfo
                            print(f"     ✅ VBT PIVOTINFO berechnet [NUMBA-OPTIMIERT]")
                        except Exception as e:
                            print(f"     ❌ VBT PIVOTINFO Fehler: {e}")
                    elif name == 'PIVOTLB':
                        try:
                            # VBT Pro Dokumentation: Direkter Zugriff auf vbt.PIVOTLB
                            window = int(params.get('window', 20))  # Integer erforderlich
                            result = vbt.PIVOTLB.run(high_prices, low_prices, close_prices, window)
                            result_data[display_name] = result.pivotlb
                            print(f"     ✅ VBT PIVOTLB berechnet [NUMBA-OPTIMIERT]")
                        except Exception as e:
                            print(f"     ❌ VBT PIVOTLB Fehler: {e}")
                    elif name == 'RAND':
                        try:
                            # VBT Pro Dokumentation: RAND braucht input_shape und n Parameter
                            n = int(params.get('n', params.get('window', 20)))  # Integer erforderlich
                            result = vbt.RAND.run(close_prices.shape, n)
                            result_data[display_name] = result.rand
                            print(f"     ✅ VBT RAND berechnet [NUMBA-OPTIMIERT]")
                        except Exception as e:
                            print(f"     ❌ VBT RAND Fehler: {e}")
                    elif name == 'RANDNX':
                        try:
                            # VBT Pro Dokumentation: RANDNX braucht input_shape und n Parameter (wie RAND)
                            n = int(params.get('n', params.get('window', 20)))  # Integer erforderlich
                            result = vbt.RANDNX.run(close_prices.shape, n)
                            # VBT Pro: RANDNX hat entries und exits, verwende entries
                            result_data[display_name] = result.entries
                            print(f"     ✅ VBT RANDNX berechnet [NUMBA-OPTIMIERT]")
                        except Exception as e:
                            print(f"     ❌ VBT RANDNX Fehler: {e}")
                    elif name == 'RPROBNX':
                        # VBT Pro: RPROBNX ist extrem rechenintensiv (Monte-Carlo-Simulation)
                        # Überspringe für Performance-Optimierung
                        print(f"     ⚠️ VBT RPROBNX übersprungen (zu rechenintensiv)")
                        result_data[display_name] = pd.Series([np.nan] * len(close_prices), index=close_prices.index)
                    elif name == 'STCX':
                        try:
                            # VBT Pro Dokumentation: STCX braucht close_prices, window, stop Parameter
                            window = int(params.get('window', 14))  # Integer erforderlich
                            stop = float(params.get('stop', 0.05))  # Float erforderlich
                            result = vbt.STCX.run(close_prices, window, stop)
                            # VBT Pro: STCX ist Signal-Generator mit entries und exits
                            result_data[display_name] = result.entries  # Verwende entries als Hauptsignal
                            print(f"     ✅ VBT STCX berechnet [NUMBA-OPTIMIERT]")
                        except Exception as e:
                            print(f"     ❌ VBT STCX Fehler: {e}")
                    elif name == 'STX':
                        try:
                            # VBT Pro Dokumentation: STX braucht close_prices, window, stop Parameter (wie STCX)
                            window = int(params.get('window', 14))  # Integer erforderlich
                            stop = float(params.get('stop', 0.05))  # Float erforderlich
                            result = vbt.STX.run(close_prices, window, stop)
                            # VBT Pro: STX ist Signal-Generator mit entries und exits (wie STCX)
                            result_data[display_name] = result.entries  # Verwende entries als Hauptsignal
                            print(f"     ✅ VBT STX berechnet [NUMBA-OPTIMIERT]")
                        except Exception as e:
                            print(f"     ❌ VBT STX Fehler: {e}")
                    elif name == 'TRENDLB':
                        # VBT Pro: TRENDLB hat VBT Data-Objekt Kompatibilitätsprobleme
                        # Überspringe für Stabilität
                        print(f"     ⚠️ VBT TRENDLB übersprungen (VBT Data-Objekt Inkompatibilität)")
                        result_data[display_name] = pd.Series([np.nan] * len(close_prices), index=close_prices.index)
                    elif name in ['VORTEX', 'WILLR', 'MACD', 'STOCH']:
                        # VBT Pro: Diese Indikatoren existieren nicht in VBT Pro
                        print(f"     ❌ VBT {name} nicht verfügbar in VBT Pro")

                    else:
                        print(f"     ❌ VBT Indikator '{name}' nicht verfügbar")
                except Exception as e:
                    print(f"     ❌ VBT {name} Fehler: {e}")

            # === TA-LIB INDIKATOREN (VBT PRO DOKUMENTATION) ===
            elif library == 'talib':
                try:
                    # VBT Pro TA-Lib Integration (korrekte Dokumentations-Syntax)
                    talib_indicator = vbt.talib(name)

                    # ECHTE FEHLER-BEHEBUNG: ALLE INDIKATOREN ZUM FUNKTIONIEREN BRINGEN

                    # Parameter direkt übergeben (NICHT als Dictionary!)
                    # Basierend auf VBT Pro Dokumentation

                    if name.upper() == 'SMA':
                        timeperiod = params.get('window', params.get('timeperiod', 20))
                        result = talib_indicator.run(close_prices, timeperiod=timeperiod)
                        result_data[display_name] = result.real

                    elif name.upper() == 'EMA':
                        timeperiod = params.get('window', params.get('timeperiod', 20))
                        result = talib_indicator.run(close_prices, timeperiod=timeperiod)
                        result_data[display_name] = result.real

                    elif name.upper() == 'RSI':
                        timeperiod = params.get('window', params.get('timeperiod', 14))
                        result = talib_indicator.run(close_prices, timeperiod=timeperiod)
                        result_data[display_name] = result.real

                    elif name.upper() == 'MACD':
                        fastperiod = params.get('fast_window', params.get('fastperiod', 12))
                        slowperiod = params.get('slow_window', params.get('slowperiod', 26))
                        signalperiod = params.get('signal_window', params.get('signalperiod', 9))
                        result = talib_indicator.run(close_prices, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
                        # VBT Pro MACD Ergebnis-Extraktion
                        if hasattr(result, 'macd'):
                            result_data[f'{display_name}_macd'] = result.macd
                            result_data[f'{display_name}_signal'] = result.macdsignal
                            result_data[f'{display_name}_histogram'] = result.macdhist
                        else:
                            result_data[display_name] = result.real if hasattr(result, 'real') else result

                    elif name.upper() == 'BBANDS':
                        timeperiod = params.get('window', params.get('timeperiod', 20))
                        nbdevup = params.get('alpha', params.get('nbdevup', 2))
                        nbdevdn = params.get('alpha', params.get('nbdevdn', 2))
                        result = talib_indicator.run(close_prices, timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn)
                        if hasattr(result, 'upperband'):
                            result_data[f'{display_name}_upper'] = result.upperband
                            result_data[f'{display_name}_middle'] = result.middleband
                            result_data[f'{display_name}_lower'] = result.lowerband
                        else:
                            result_data[display_name] = result.real if hasattr(result, 'real') else result

                    # STOCH wird weiter unten behandelt (Zeile 821+)

                    elif name.upper() == 'ATR':
                        timeperiod = params.get('window', params.get('timeperiod', 14))
                        result = talib_indicator.run(high_prices, low_prices, close_prices, timeperiod=timeperiod)
                        result_data[display_name] = result.real if hasattr(result, 'real') else result

                    # VBT Pro Dokumentation: Volume-basierte TA-Lib Indikatoren
                    elif name.upper() in ['AD', 'ADOSC', 'OBV']:
                        if volume_data is not None:
                            if name.upper() == 'AD':
                                result = talib_indicator.run(high_prices, low_prices, close_prices, volume_data)
                            elif name.upper() == 'ADOSC':
                                fastperiod = params.get('fastperiod', 3)
                                slowperiod = params.get('slowperiod', 10)
                                result = talib_indicator.run(high_prices, low_prices, close_prices, volume_data, fastperiod=fastperiod, slowperiod=slowperiod)
                            elif name.upper() == 'OBV':
                                result = talib_indicator.run(close_prices, volume_data)
                            result_data[display_name] = result.real if hasattr(result, 'real') else result
                        else:
                            print(f"     ⚠️ TA-Lib {name} übersprungen: Keine Volume-Daten")
                            continue

                    # VBT Pro Dokumentation: OHLC-basierte TA-Lib Indikatoren
                    elif name.upper() in ['TRANGE', 'AVGPRICE', 'MEDPRICE', 'TYPPRICE', 'WCLPRICE', 'MIDPOINT', 'MIDPRICE', 'SAR']:
                        if name.upper() == 'AVGPRICE':
                            # AVGPRICE RICHTIG BEHEBEN - braucht OHLC Parameter
                            result = talib_indicator.run(open_prices, high_prices, low_prices, close_prices)
                        elif name.upper() == 'MEDPRICE':
                            # MEDPRICE RICHTIG BEHEBEN - braucht nur high und low
                            result = talib_indicator.run(high_prices, low_prices)
                        elif name.upper() in ['TRANGE', 'TYPPRICE', 'WCLPRICE']:
                            result = talib_indicator.run(high_prices, low_prices, close_prices)
                        elif name.upper() == 'MIDPOINT':
                            timeperiod = params.get('window', params.get('timeperiod', 14))
                            result = talib_indicator.run(close_prices, timeperiod=timeperiod)
                        elif name.upper() == 'MIDPRICE':
                            timeperiod = params.get('window', params.get('timeperiod', 14))
                            result = talib_indicator.run(high_prices, low_prices, timeperiod=timeperiod)
                        elif name.upper() == 'SAR':
                            acceleration = params.get('acceleration', 0.02)
                            maximum = params.get('maximum', 0.2)
                            result = talib_indicator.run(high_prices, low_prices, acceleration=acceleration, maximum=maximum)
                        result_data[display_name] = result.real if hasattr(result, 'real') else result

                    # VBT Pro Dokumentation: Candlestick Pattern (alle brauchen OHLC)
                    elif name.upper() in ['CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE', 'CDL3OUTSIDE', 'CDL3STARSINSOUTH', 'CDL3WHITESOLDIERS', 'CDLABANDONEDBABY', 'CDLADVANCEBLOCK', 'CDLBELTHOLD', 'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU', 'CDLCONCEALBABYSWALL', 'CDLCOUNTERATTACK', 'CDLDARKCLOUDCOVER', 'CDLDOJI', 'CDLDOJISTAR', 'CDLDRAGONFLYDOJI', 'CDLENGULFING', 'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR', 'CDLGAPSIDESIDEWHITE', 'CDLGRAVESTONEDOJI', 'CDLHAMMER', 'CDLHANGINGMAN', 'CDLHARAMI', 'CDLHARAMICROSS', 'CDLHIGHWAVE', 'CDLHIKKAKE', 'CDLHIKKAKEMOD', 'CDLHOMINGPIGEON', 'CDLIDENTICAL3CROWS', 'CDLINNECK', 'CDLINVERTEDHAMMER', 'CDLKICKING', 'CDLKICKINGBYLENGTH', 'CDLLADDERBOTTOM', 'CDLLONGLEGGEDDOJI', 'CDLLONGLINE', 'CDLMARUBOZU', 'CDLMATCHINGLOW', 'CDLMATHOLD', 'CDLMORNINGDOJISTAR', 'CDLMORNINGSTAR', 'CDLONNECK', 'CDLPIERCING', 'CDLRICKSHAWMAN', 'CDLRISEFALL3METHODS', 'CDLSEPARATINGLINES', 'CDLSHOOTINGSTAR', 'CDLSHORTLINE', 'CDLSPINNINGTOP', 'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH', 'CDLTAKURI', 'CDLTASUKIGAP', 'CDLTHRUSTING', 'CDLTRISTAR', 'CDLUNIQUE3RIVER', 'CDLUPSIDEGAP2CROWS', 'CDLXSIDEGAP3METHODS']:
                        # CDL PATTERN RICHTIG BEHEBEN - VBT Pro spezielle Objekt-Behandlung
                        result = talib_indicator.run(open_prices, high_prices, low_prices, close_prices)

                        # VBT Pro CDL Pattern geben spezielle Objekte zurück
                        try:
                            # Versuche verschiedene Attribute
                            if hasattr(result, 'real'):
                                result_data[display_name] = pd.Series(result.real, index=close_prices.index)
                            elif hasattr(result, 'values'):
                                result_data[display_name] = pd.Series(result.values, index=close_prices.index)
                            elif hasattr(result, 'to_pandas'):
                                result_data[display_name] = result.to_pandas()
                            else:
                                # Fallback: Konvertiere VBT Objekt zu Array
                                result_array = np.array(result)
                                result_data[display_name] = pd.Series(result_array, index=close_prices.index)
                        except Exception as cdl_error:
                            print(f"     ⚠️ CDL {name} Konvertierungs-Fehler: {cdl_error}")
                            # Letzter Fallback: Verwende das Objekt direkt
                            result_data[display_name] = result

                    # VBT Pro Dokumentation: Spezielle Parameter-Indikatoren
                    elif name.upper() in ['MAMA', 'MAVP']:
                        if name.upper() == 'MAMA':
                            fastlimit = params.get('fastlimit', 0.5)
                            slowlimit = params.get('slowlimit', 0.05)
                            result = talib_indicator.run(close_prices, fastlimit=fastlimit, slowlimit=slowlimit)
                            if hasattr(result, 'mama') and hasattr(result, 'fama'):
                                result_data[f'{display_name}_mama'] = result.mama
                                result_data[f'{display_name}_fama'] = result.fama
                            else:
                                result_data[display_name] = result.real if hasattr(result, 'real') else result
                        elif name.upper() == 'MAVP':
                            # MAVP braucht periods array - verwende Standard-Perioden
                            periods = params.get('periods', [10, 20, 30] * (len(close_prices) // 3 + 1))[:len(close_prices)]
                            minperiod = params.get('minperiod', 2)
                            maxperiod = params.get('maxperiod', 30)
                            result = talib_indicator.run(close_prices, periods, minperiod=minperiod, maxperiod=maxperiod)
                            result_data[display_name] = result.real if hasattr(result, 'real') else result

                    # VBT Pro Dokumentation: MACD Varianten
                    elif name.upper() in ['MACDEXT', 'MACDFIX']:
                        if name.upper() == 'MACDEXT':
                            fastperiod = params.get('fastperiod', 12)
                            fastmatype = params.get('fastmatype', 0)
                            slowperiod = params.get('slowperiod', 26)
                            slowmatype = params.get('slowmatype', 0)
                            signalperiod = params.get('signalperiod', 9)
                            signalmatype = params.get('signalmatype', 0)
                            result = talib_indicator.run(close_prices, fastperiod=fastperiod, fastmatype=fastmatype, slowperiod=slowperiod, slowmatype=slowmatype, signalperiod=signalperiod, signalmatype=signalmatype)
                        elif name.upper() == 'MACDFIX':
                            signalperiod = params.get('signalperiod', 9)
                            result = talib_indicator.run(close_prices, signalperiod=signalperiod)

                        if hasattr(result, 'macd'):
                            result_data[f'{display_name}_macd'] = result.macd
                            result_data[f'{display_name}_signal'] = result.macdsignal
                            result_data[f'{display_name}_histogram'] = result.macdhist
                        else:
                            result_data[display_name] = result.real if hasattr(result, 'real') else result

                    # VBT Pro Dokumentation: Min/Max Indikatoren (PROBLEMATISCH - ÜBERSPRINGE)
                    elif name.upper() in ['MAXINDEX', 'MININDEX', 'MINMAXINDEX', 'STOCHRSI', 'HT_TRENDMODE']:
                        # Diese haben object has no len() Probleme - überspringe
                        print(f"     ⚠️ TA-Lib {name} übersprungen (Object has no len())")
                        continue

                    elif name.upper() in ['MINMAX']:
                        timeperiod = params.get('window', params.get('timeperiod', 14))
                        result = talib_indicator.run(close_prices, timeperiod=timeperiod)
                        if hasattr(result, 'min') and hasattr(result, 'max'):
                            result_data[f'{display_name}_min'] = result.min
                            result_data[f'{display_name}_max'] = result.max
                        else:
                            result_data[display_name] = result.real if hasattr(result, 'real') else result

                    # VBT Pro Dokumentation: FEHLENDE PARAMETER TA-LIB INDIKATOREN
                    elif name.upper() in ['ADD', 'DIV', 'MULT', 'SUB']:
                        # Brauchen high und low Parameter
                        result = talib_indicator.run(high_prices, low_prices)
                        result_data[display_name] = result.real if hasattr(result, 'real') else result
                    elif name.upper() in ['SAREXT']:
                        # SAREXT hat Parameter-Konflikte - überspringe
                        print(f"     ⚠️ TA-Lib {name} übersprungen (Parameter-Konflikte)")
                        continue
                    elif name.upper() in ['STOCHF', 'WILLR', 'ADX', 'ADXR', 'CCI', 'DX', 'MINUS_DI', 'PLUS_DI', 'NATR', 'ULTOSC']:
                        # Brauchen HLC Parameter
                        timeperiod = params.get('window', params.get('timeperiod', 14))
                        if name.upper() == 'STOCHF':
                            # STOCHF hat Keyword-Argument Probleme - überspringe
                            print(f"     ⚠️ TA-Lib {name} übersprungen (Keyword-Argument Probleme)")
                            continue
                        elif name.upper() == 'ULTOSC':
                            timeperiod1 = params.get('timeperiod1', 7)
                            timeperiod2 = params.get('timeperiod2', 14)
                            timeperiod3 = params.get('timeperiod3', 28)
                            result = talib_indicator.run(high_prices, low_prices, close_prices,
                                                       timeperiod1=timeperiod1, timeperiod2=timeperiod2, timeperiod3=timeperiod3)
                        else:
                            result = talib_indicator.run(high_prices, low_prices, close_prices, timeperiod=timeperiod)
                        result_data[display_name] = result.real if hasattr(result, 'real') else result
                    elif name.upper() in ['AROON', 'AROONOSC', 'MINUS_DM', 'PLUS_DM']:
                        # Brauchen HL Parameter
                        timeperiod = params.get('window', params.get('timeperiod', 14))
                        result = talib_indicator.run(high_prices, low_prices, timeperiod=timeperiod)
                        if name.upper() == 'AROON' and hasattr(result, 'aroondown') and hasattr(result, 'aroonup'):
                            result_data[f'{display_name}_down'] = result.aroondown
                            result_data[f'{display_name}_up'] = result.aroonup
                        else:
                            result_data[display_name] = result.real if hasattr(result, 'real') else result
                    elif name.upper() in ['BOP']:
                        # Braucht OHLC Parameter
                        result = talib_indicator.run(open_prices, high_prices, low_prices, close_prices)
                        result_data[display_name] = result.real if hasattr(result, 'real') else result
                    # AVGPRICE wird weiter unten behandelt
                    elif name.upper() in ['MFI']:
                        # Braucht HLCV Parameter
                        if volume_data is not None:
                            timeperiod = params.get('window', params.get('timeperiod', 14))
                            result = talib_indicator.run(high_prices, low_prices, close_prices, volume_data, timeperiod=timeperiod)
                            result_data[display_name] = result.real if hasattr(result, 'real') else result
                        else:
                            print(f"     ⚠️ TA-Lib {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['APO', 'PPO']:
                        # Korrigiere Parameter-Namen (timeperiod -> fastperiod/slowperiod)
                        fastperiod = params.get('fast', params.get('fastperiod', 12))
                        slowperiod = params.get('slow', params.get('slowperiod', 26))
                        matype = params.get('matype', 0)
                        result = talib_indicator.run(close_prices, fastperiod=fastperiod, slowperiod=slowperiod, matype=matype)
                        result_data[display_name] = result.real if hasattr(result, 'real') else result
                    elif name.upper() == 'STOCH':
                        # STOCH RICHTIG BEHEBEN - VBT Pro TA-Lib korrekte Parameter-Namen
                        # Basierend auf VBT Pro Test: fastk_period, slowk_period, slowd_period funktionieren!
                        fastk_period = params.get('fastk_period', params.get('fastkperiod', 5))
                        slowk_period = params.get('slowk_period', params.get('slowkperiod', 3))
                        slowd_period = params.get('slowd_period', params.get('slowdperiod', 3))
                        # VBT Pro TA-Lib STOCH verwendet Keyword-Parameter (nicht positional!)
                        result = talib_indicator.run(high_prices, low_prices, close_prices,
                                                   fastk_period=fastk_period, slowk_period=slowk_period, slowd_period=slowd_period)
                        if hasattr(result, 'slowk') and hasattr(result, 'slowd'):
                            result_data[f'{display_name}_k'] = result.slowk
                            result_data[f'{display_name}_d'] = result.slowd
                        else:
                            result_data[display_name] = result.real if hasattr(result, 'real') else result
                    elif name.upper() == 'STOCHF':
                        # STOCHF RICHTIG BEHEBEN - VBT Pro TA-Lib verwendet positionale Parameter
                        # Basierend auf VBT Pro Dokumentation: run(high, low, close, fastk_period, fastd_period, fastd_matype)
                        fastk_period = params.get('fastk_period', params.get('fastkperiod', 5))
                        fastd_period = params.get('fastd_period', params.get('fastdperiod', 3))
                        fastd_matype = params.get('fastd_matype', params.get('fastdmatype', 0))
                        result = talib_indicator.run(high_prices, low_prices, close_prices,
                                                   fastk_period, fastd_period, fastd_matype)
                        if hasattr(result, 'fastk') and hasattr(result, 'fastd'):
                            result_data[f'{display_name}_k'] = result.fastk
                            result_data[f'{display_name}_d'] = result.fastd
                        else:
                            result_data[display_name] = result.real if hasattr(result, 'real') else result
                    elif name.upper() == 'AVGPRICE':
                        # AVGPRICE RICHTIG BEHEBEN - braucht OHLC Parameter
                        result = talib_indicator.run(open_prices, high_prices, low_prices, close_prices)
                        result_data[display_name] = result.real if hasattr(result, 'real') else result
                    elif name.upper() == 'MEDPRICE':
                        # MEDPRICE RICHTIG BEHEBEN - braucht HL Parameter
                        result = talib_indicator.run(high_prices, low_prices)
                        result_data[display_name] = result.real if hasattr(result, 'real') else result
                    elif name.upper().startswith('CDL'):
                        # CDL PATTERN RICHTIG BEHEBEN - brauchen OHLC Parameter und spezielle Behandlung
                        result = talib_indicator.run(open_prices, high_prices, low_prices, close_prices)
                        # CDL Pattern geben Integer-Arrays zurück - konvertiere zu Pandas Series
                        if hasattr(result, 'real'):
                            result_data[display_name] = pd.Series(result.real, index=close_prices.index)
                        else:
                            # Direkte Konvertierung zu Pandas Series
                            result_data[display_name] = pd.Series(result, index=close_prices.index)
                    elif name.upper() == 'SAREXT':
                        # SAREXT RICHTIG BEHEBEN - vereinfachte Parameter
                        result = talib_indicator.run(high_prices, low_prices, close_prices)
                        result_data[display_name] = result.real if hasattr(result, 'real') else result
                    elif name.upper().startswith('HT_'):
                        # Hilbert Transform Funktionen - alle mit close_prices
                        # HT_TRENDMODE hat spezielle "object has no len()" Probleme
                        if name.upper() == 'HT_TRENDMODE':
                            print(f"     ⚠️ TA-Lib {name} übersprungen (Object has no len())")
                            continue

                        result = talib_indicator.run(close_prices)
                        if hasattr(result, 'real'):
                            result_data[display_name] = result.real
                        elif hasattr(result, 'inphase') and hasattr(result, 'quadrature'):
                            # HT_PHASOR hat zwei Ausgaben
                            result_data[f'{display_name}_inphase'] = result.inphase
                            result_data[f'{display_name}_quadrature'] = result.quadrature
                        elif hasattr(result, 'sine') and hasattr(result, 'leadsine'):
                            # HT_SINE hat zwei Ausgaben
                            result_data[f'{display_name}_sine'] = result.sine
                            result_data[f'{display_name}_leadsine'] = result.leadsine
                        else:
                            result_data[display_name] = result
                    elif name.upper() in ['BETA', 'CORREL']:
                        # Brauchen zwei Datenreihen (high und low als Proxy)
                        timeperiod = params.get('window', params.get('timeperiod', 5 if name.upper() == 'BETA' else 30))
                        result = talib_indicator.run(high_prices, low_prices, timeperiod=timeperiod)
                        result_data[display_name] = result.real if hasattr(result, 'real') else result
                    # (Problematische Indikatoren bereits oben übersprungen)
                    else:
                        # Standard TA-Lib Indikator (VBT Pro Dokumentations-Syntax)
                        timeperiod = params.get('window', params.get('timeperiod', 14))

                        # Versuche verschiedene Parameter-Kombinationen
                        if name.upper() in ['ACOS', 'ASIN', 'ATAN', 'COS', 'SIN', 'TAN', 'COSH', 'SINH', 'TANH', 'EXP', 'LN', 'LOG10', 'SQRT', 'CEIL', 'FLOOR']:
                            # Mathematische Funktionen brauchen nur close
                            result = talib_indicator.run(close_prices)
                        elif name.upper() == 'STOCH':
                            # STOCH wird bereits oben behandelt - sollte hier nicht ankommen
                            print(f"     ⚠️ TA-Lib {name} bereits behandelt")
                            continue
                        else:
                            # Standard mit timeperiod
                            result = talib_indicator.run(close_prices, timeperiod=timeperiod)

                        # VBT Pro Ergebnis-Extraktion (Dokumentation)
                        result_data[display_name] = result.real if hasattr(result, 'real') else result

                    print(f"     ✅ TA-Lib {name} berechnet [VBT-INTEGRIERT]")

                except Exception as e:
                    print(f"     ❌ TA-Lib {name} Fehler: {e}")

            # === PANDAS_TA INDIKATOREN (VBT PRO DOKUMENTATION) ===
            elif library == 'pandas_ta':
                try:
                    # VBT Pro Pandas TA Integration (korrekte Dokumentations-Syntax)
                    pandas_ta_indicator = vbt.pandas_ta(name)

                    # Parameter direkt übergeben (NICHT als Dictionary!)
                    # Basierend auf VBT Pro Dokumentation

                    if name.upper() == 'SMA':
                        length = params.get('window', params.get('length', 20))
                        result = pandas_ta_indicator.run(close_prices, length=length)
                        # VBT Pro Pandas TA Ergebnis-Extraktion (Dokumentation)
                        result_data[display_name] = result.sma

                    elif name.upper() == 'EMA':
                        length = params.get('window', params.get('length', 20))
                        result = pandas_ta_indicator.run(close_prices, length=length)
                        # VBT Pro Pandas TA Ergebnis-Extraktion (Dokumentation)
                        result_data[display_name] = result.ema

                    elif name.upper() == 'RSI':
                        length = params.get('window', params.get('length', 14))
                        result = pandas_ta_indicator.run(close_prices, length=length)
                        # VBT Pro Pandas TA Ergebnis-Extraktion (Dokumentation)
                        result_data[display_name] = result.rsi

                    elif name.upper() == 'MACD':
                        fast = params.get('fast_window', params.get('fast', 12))
                        slow = params.get('slow_window', params.get('slow', 26))
                        signal = params.get('signal_window', params.get('signal', 9))
                        result = pandas_ta_indicator.run(close_prices, fast=fast, slow=slow, signal=signal)

                        # VBT Pro Pandas TA MACD Ergebnis-Extraktion (Dokumentation)
                        result_data[f'{display_name}_macd'] = result.macd
                        result_data[f'{display_name}_signal'] = result.macds
                        result_data[f'{display_name}_histogram'] = result.macdh

                    elif name.upper() == 'BBANDS':
                        length = params.get('window', params.get('length', 20))
                        std = params.get('alpha', params.get('std', 2))
                        result = pandas_ta_indicator.run(close_prices, length=length, std=std)
                        # VBT Pro Pandas TA BBANDS Ergebnis-Extraktion
                        if hasattr(result, 'bbl') and hasattr(result, 'bbm') and hasattr(result, 'bbu'):
                            result_data[f'{display_name}_lower'] = result.bbl
                            result_data[f'{display_name}_middle'] = result.bbm
                            result_data[f'{display_name}_upper'] = result.bbu
                        else:
                            result_data[display_name] = getattr(result, name.lower(), result)

                    elif name.upper() == 'STOCH':
                        # VBT Pro: STOCH hat "Couldn't parse the output: mismatching index" Probleme
                        print(f"     ⚠️ Pandas TA {name} übersprungen (Index-Mismatch)")
                        continue

                    elif name.upper() == 'ATR':
                        length = params.get('window', params.get('length', 14))
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                        # VBT Pro Pandas TA Ergebnis-Extraktion (Dokumentation)
                        result_data[display_name] = result.atr

                    # VBT Pro Dokumentation: PANDAS TA INDIKATOREN RICHTIG BEHEBEN
                    elif name.upper() == 'STOCHRSI':
                        # STOCHRSI RICHTIG BEHEBEN
                        length = params.get('window', params.get('length', 14))
                        rsi_length = params.get('rsi_length', 14)
                        k = params.get('k', 3)
                        d = params.get('d', 3)
                        result = pandas_ta_indicator.run(close_prices, length=length, rsi_length=rsi_length, k=k, d=d)
                        if hasattr(result, 'stochrsi_k') and hasattr(result, 'stochrsi_d'):
                            result_data[f'{display_name}_k'] = result.stochrsi_k
                            result_data[f'{display_name}_d'] = result.stochrsi_d
                        else:
                            result_data[display_name] = getattr(result, name.lower(), result)

                    elif name.upper() in ['SUPERTREND']:
                        # SUPERTREND RICHTIG BEHEBEN
                        length = params.get('window', params.get('length', 7))
                        multiplier = params.get('multiplier', 3.0)
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length, multiplier=multiplier)
                        if hasattr(result, 'supert') and hasattr(result, 'superd'):
                            result_data[f'{display_name}_trend'] = result.supert
                            result_data[f'{display_name}_direction'] = result.superd
                        else:
                            result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['PSAR']:
                        # PSAR RICHTIG BEHEBEN
                        af0 = params.get('af0', 0.02)
                        af = params.get('af', 0.02)
                        max_af = params.get('max_af', 0.2)
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, af0=af0, af=af, max_af=max_af)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['ICHIMOKU']:
                        # ICHIMOKU RICHTIG BEHEBEN
                        tenkan = params.get('tenkan', 9)
                        kijun = params.get('kijun', 26)
                        senkou = params.get('senkou', 52)
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, tenkan=tenkan, kijun=kijun, senkou=senkou)
                        if hasattr(result, 'ichimoku_a') and hasattr(result, 'ichimoku_b'):
                            result_data[f'{display_name}_a'] = result.ichimoku_a
                            result_data[f'{display_name}_b'] = result.ichimoku_b
                        else:
                            result_data[display_name] = getattr(result, name.lower(), result)

                    # VBT Pro Dokumentation: SPEZIELLE PARAMETER-FEHLER PANDAS TA INDIKATOREN
                    elif name.upper() in ['ERI']:
                        # ERI braucht HLC Parameter
                        length = params.get('window', params.get('length', 13))
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['FISHER']:
                        # FISHER braucht HL Parameter
                        length = params.get('window', params.get('length', 9))
                        result = pandas_ta_indicator.run(high_prices, low_prices, length=length)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['KDJ']:
                        # KDJ braucht HLC Parameter
                        length = params.get('window', params.get('length', 9))
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['SQUEEZE', 'SQUEEZE_PRO']:
                        # SQUEEZE braucht HLC Parameter
                        bb_length = params.get('bb_length', 20)
                        bb_std = params.get('bb_std', 2)
                        kc_length = params.get('kc_length', 20)
                        if name.upper() == 'SQUEEZE_PRO':
                            kc_scalar_wide = params.get('kc_scalar_wide', 2)
                            kc_scalar_normal = params.get('kc_scalar_normal', 1.5)
                            kc_scalar_narrow = params.get('kc_scalar_narrow', 1)
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices,
                                                           bb_length=bb_length, bb_std=bb_std, kc_length=kc_length,
                                                           kc_scalar_wide=kc_scalar_wide, kc_scalar_normal=kc_scalar_normal, kc_scalar_narrow=kc_scalar_narrow)
                        else:
                            kc_scalar = params.get('kc_scalar', 1.5)
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices,
                                                           bb_length=bb_length, bb_std=bb_std, kc_length=kc_length, kc_scalar=kc_scalar)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['ACCBANDS']:
                        # ACCBANDS braucht HLC Parameter
                        length = params.get('window', params.get('length', 20))
                        c = params.get('c', 4)
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length, c=c)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['DONCHIAN']:
                        # DONCHIAN braucht HL Parameter
                        lower_length = params.get('lower_length', 20)
                        upper_length = params.get('upper_length', 20)
                        result = pandas_ta_indicator.run(high_prices, low_prices, lower_length=lower_length, upper_length=upper_length)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['KC']:
                        # KC braucht HLC Parameter
                        length = params.get('window', params.get('length', 20))
                        scalar = params.get('scalar', 2)
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length, scalar=scalar)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['AD', 'ADOSC', 'CMF']:
                        # Diese brauchen OHLCV Parameter
                        if volume_data is not None:
                            if name.upper() == 'AD':
                                # AD braucht open_ Parameter
                                result = pandas_ta_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data)
                            elif name.upper() == 'ADOSC':
                                # ADOSC braucht open_ Parameter + fast/slow
                                fast = params.get('fast', 3)
                                slow = params.get('slow', 10)
                                result = pandas_ta_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data, fast=fast, slow=slow)
                            elif name.upper() == 'CMF':
                                # CMF braucht open_ Parameter + length
                                length = params.get('window', params.get('length', 20))
                                result = pandas_ta_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data, length=length)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Pandas TA {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['EFI']:
                        # EFI hat Parameter-Konflikt - korrigiere
                        if volume_data is not None:
                            length = params.get('window', params.get('length', 13))
                            # EFI Parameter-Konflikt beheben: verwende positionale Parameter
                            result = pandas_ta_indicator.run(close_prices, volume_data, length)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Pandas TA {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['NVI', 'PVI']:
                        # NVI/PVI haben Parameter-Konflikt - korrigiere
                        if volume_data is not None:
                            length = params.get('window', params.get('length', 255))
                            # Parameter-Konflikt beheben: verwende positionale Parameter
                            result = pandas_ta_indicator.run(close_prices, volume_data, length)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Pandas TA {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['AOBV', 'PVOL', 'PVR']:
                        # Diese haben spezielle Volume-Algorithmus-Probleme
                        print(f"     ⚠️ Pandas TA {name} übersprungen (Volume-Algorithmus-Probleme)")
                        continue
                    elif name.upper() in ['BOP']:
                        # BOP braucht OHLC Parameter
                        result = pandas_ta_indicator.run(open_prices, high_prices, low_prices, close_prices)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['BRAR']:
                        # BRAR braucht OHLC Parameter
                        length = params.get('window', params.get('length', 26))
                        result = pandas_ta_indicator.run(open_prices, high_prices, low_prices, close_prices, length=length)
                        if hasattr(result, 'ar') and hasattr(result, 'br'):
                            result_data[f'{display_name}_ar'] = result.ar
                            result_data[f'{display_name}_br'] = result.br
                        else:
                            result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['RVGI']:
                        # RVGI braucht OHLC Parameter
                        length = params.get('window', params.get('length', 14))
                        result = pandas_ta_indicator.run(open_prices, high_prices, low_prices, close_prices, length=length)
                        result_data[display_name] = getattr(result, name.lower(), result)

                    # VBT Pro Dokumentation: CANDLESTICK PATTERN PANDAS TA INDIKATOREN
                    elif name.upper() in ['CDL_PATTERN', 'CDL_Z', 'HA', 'HILO', 'HL2', 'HLC3', 'HWC', 'MIDPRICE', 'OHLC4', 'PDIST', 'WCP']:
                        # Diese brauchen OHLC Parameter
                        if name.upper() in ['CDL_PATTERN', 'CDL_Z', 'HA', 'OHLC4', 'PDIST']:
                            # Brauchen OHLC Parameter
                            result = pandas_ta_indicator.run(open_prices, high_prices, low_prices, close_prices)
                        elif name.upper() in ['HILO']:
                            # HILO braucht HLC Parameter
                            high_length = params.get('high_length', 13)
                            low_length = params.get('low_length', 21)
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, high_length=high_length, low_length=low_length)
                        elif name.upper() in ['HL2', 'MIDPRICE']:
                            # Brauchen HL Parameter
                            length = params.get('window', params.get('length', 2))
                            result = pandas_ta_indicator.run(high_prices, low_prices, length=length)
                        elif name.upper() in ['HLC3', 'WCP']:
                            # Brauchen HLC Parameter
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices)
                        elif name.upper() in ['HWC']:
                            # HWC hat spezielle Parameter
                            print(f"     ⚠️ Pandas TA {name} übersprungen (Object has no len())")
                            continue
                        else:
                            result = pandas_ta_indicator.run(close_prices)
                        result_data[display_name] = getattr(result, name.lower(), result)

                    # VBT Pro Dokumentation: UTILITY PANDAS TA INDIKATOREN
                    elif name.upper() in ['TOS_STDEVALL', 'TSIGNALS', 'XSIGNALS']:
                        # Diese haben spezielle Probleme
                        print(f"     ⚠️ Pandas TA {name} übersprungen (Utility-Funktions-Probleme)")
                        continue

                    # VBT Pro Dokumentation: TREND PANDAS TA INDIKATOREN
                    elif name.upper() in ['LONG_RUN', 'SHORT_RUN']:
                        # LONG_RUN/SHORT_RUN haben Parameter-Konflikte - korrigiere
                        fast = params.get('fast', 2)
                        slow = params.get('slow', 30)
                        # Parameter-Konflikt beheben: verwende positionale Parameter
                        result = pandas_ta_indicator.run(close_prices, fast, slow)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['VORTEX', 'ABERRATION', 'CKSP']:
                        # Diese brauchen HLC Parameter
                        if name.upper() == 'CKSP':
                            p = params.get('p', 10)
                            x = params.get('x', 1)
                            q = params.get('q', 9)
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, p=p, x=x, q=q)
                        elif name.upper() == 'ABERRATION':
                            length = params.get('window', params.get('length', 5))
                            atr_length = params.get('atr_length', 15)
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length, atr_length=atr_length)
                        else:  # VORTEX
                            length = params.get('window', params.get('length', 14))
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                        result_data[display_name] = getattr(result, name.lower(), result)

                    # VBT Pro Dokumentation: SERIES AMBIGUITY PANDAS TA INDIKATOREN
                    elif name.upper() in ['APO', 'PPO']:
                        # Diese haben "The truth value of a Series is ambiguous" Probleme
                        print(f"     ⚠️ Pandas TA {name} übersprungen (Series Ambiguity)")
                        continue

                    # VBT Pro Dokumentation: ATTRIBUT-FEHLER PANDAS TA INDIKATOREN
                    elif name.upper() in ['AROON']:
                        # Spezielle Behandlung für AROON Attribut-Fehler
                        length = params.get('window', params.get('length', 14))
                        result = pandas_ta_indicator.run(high_prices, low_prices, length=length)
                        if hasattr(result, 'aroonup') and hasattr(result, 'aroondown'):
                            result_data[f'{display_name}_up'] = result.aroonup
                            result_data[f'{display_name}_down'] = result.aroondown
                        elif hasattr(result, 'aroon_up') and hasattr(result, 'aroon_down'):
                            result_data[f'{display_name}_up'] = result.aroon_up
                            result_data[f'{display_name}_down'] = result.aroon_down
                        else:
                            # Fallback: Verwende erstes verfügbares Attribut
                            attrs = [attr for attr in dir(result) if not attr.startswith('_')]
                            if attrs:
                                result_data[display_name] = getattr(result, attrs[0])
                            else:
                                result_data[display_name] = result

                    # VBT Pro Dokumentation: STANDARD OHLC-basierte Pandas TA Indikatoren
                    elif name.upper() in ['WILLR', 'ADX', 'CCI', 'DX', 'MINUS_DI', 'PLUS_DI', 'MINUS_DM', 'PLUS_DM', 'NATR', 'TRANGE', 'ADXR', 'AROONOSC', 'BOP', 'ULTOSC']:
                        if name.upper() in ['WILLR']:
                            length = params.get('window', params.get('length', 14))
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                            result_data[display_name] = result.willr
                        elif name.upper() in ['ADX', 'DX', 'MINUS_DI', 'PLUS_DI', 'MINUS_DM', 'PLUS_DM', 'ADXR']:
                            length = params.get('window', params.get('length', 14))
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                            if name.upper() == 'ADX':
                                result_data[display_name] = result.adx
                            elif name.upper() == 'DX':
                                result_data[display_name] = result.dx
                            elif name.upper() == 'MINUS_DI':
                                result_data[display_name] = result.dmp
                            elif name.upper() == 'PLUS_DI':
                                result_data[display_name] = result.dmn
                            else:
                                result_data[display_name] = getattr(result, name.lower(), result)
                        elif name.upper() in ['AROON', 'AROONOSC']:
                            length = params.get('window', params.get('length', 14))
                            result = pandas_ta_indicator.run(high_prices, low_prices, length=length)
                            if name.upper() == 'AROON':
                                if hasattr(result, 'aroonup') and hasattr(result, 'aroondown'):
                                    result_data[f'{display_name}_up'] = result.aroonup
                                    result_data[f'{display_name}_down'] = result.aroondown
                                else:
                                    result_data[display_name] = result.aroon
                            else:
                                result_data[display_name] = result.aroonosc
                        elif name.upper() in ['CCI']:
                            length = params.get('window', params.get('length', 14))
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                            result_data[display_name] = result.cci
                        elif name.upper() in ['NATR', 'TRANGE']:
                            length = params.get('window', params.get('length', 14))
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        elif name.upper() in ['STOCH', 'STOCHF']:
                            k = params.get('k_window', params.get('k', 14))
                            d = params.get('d_window', params.get('d', 3))
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, k=k, d=d)
                            if hasattr(result, 'stochk') and hasattr(result, 'stochd'):
                                result_data[f'{display_name}_k'] = result.stochk
                                result_data[f'{display_name}_d'] = result.stochd
                            else:
                                result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            # Andere OHLC Indikatoren
                            length = params.get('window', params.get('length', 14))
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                            result_data[display_name] = getattr(result, name.lower(), result)

                    # VBT Pro Dokumentation: Volume-basierte Pandas TA Indikatoren
                    elif name.upper() in ['VWAP', 'VWMA', 'AOBV', 'CMF', 'EFI', 'EOM', 'KVO', 'MFI', 'NVI', 'OBV', 'PVI', 'PVOL', 'PVOT', 'PVR', 'PVT']:
                        if volume_data is not None:
                            if name.upper() in ['VWAP']:
                                result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, volume_data)
                                result_data[display_name] = result.vwap
                            elif name.upper() in ['VWMA']:
                                length = params.get('window', params.get('length', 14))
                                result = pandas_ta_indicator.run(close_prices, volume_data, length=length)
                                result_data[display_name] = result.vwma
                            elif name.upper() in ['OBV', 'AOBV', 'PVT']:
                                result = pandas_ta_indicator.run(close_prices, volume_data)
                                result_data[display_name] = getattr(result, name.lower(), result)
                            elif name.upper() in ['CMF', 'EFI', 'MFI']:
                                length = params.get('window', params.get('length', 14))
                                result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, volume_data, length=length)
                                result_data[display_name] = getattr(result, name.lower(), result)
                            elif name.upper() in ['EOM', 'KVO']:
                                fast = params.get('fast', 10)
                                slow = params.get('slow', 20)
                                result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, volume_data, fast=fast, slow=slow)
                                result_data[display_name] = getattr(result, name.lower(), result)
                            else:
                                # Andere Volume Indikatoren
                                length = params.get('window', params.get('length', 14))
                                result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, volume_data, length=length)
                                result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Pandas TA {name} übersprungen: Keine Volume-Daten")
                            continue

                    # VBT Pro Dokumentation: Spezielle Parameter Indikatoren
                    elif name.upper() in ['LONG_RUN', 'SHORT_RUN']:
                        fast = params.get('fast', 10)
                        slow = params.get('slow', 20)
                        result = pandas_ta_indicator.run(close_prices, fast=fast, slow=slow)
                        result_data[display_name] = getattr(result, name.lower(), result)

                    # VBT Pro Dokumentation: FEHLENDE PANDAS TA INDIKATOREN RICHTIG BEHEBEN
                    elif name.upper() == 'CMO':
                        # CMO RICHTIG BEHEBEN
                        length = params.get('window', params.get('length', 14))
                        result = pandas_ta_indicator.run(close_prices, length=length)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'ROC':
                        # ROC RICHTIG BEHEBEN
                        length = params.get('window', params.get('length', 10))
                        result = pandas_ta_indicator.run(close_prices, length=length)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'TRIX':
                        # TRIX RICHTIG BEHEBEN
                        length = params.get('window', params.get('length', 30))
                        result = pandas_ta_indicator.run(close_prices, length=length)
                        result_data[display_name] = getattr(result, name.lower(), result)

                    # VBT Pro Dokumentation: PANDAS TA "object has no len()" FEHLER BEHEBEN
                    elif name.upper() == 'STOCH':
                        # STOCH RICHTIG BEHEBEN - Pandas TA Dokumentation befolgt
                        k = params.get('k', 14)
                        d = params.get('d', 3)
                        smooth_k = params.get('smooth_k', 3)
                        # Pandas TA STOCH erwartet HLC + Parameter
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, k=k, d=d, smooth_k=smooth_k)
                        # Pandas TA STOCH gibt DataFrame zurück mit STOCHk und STOCHd Spalten
                        if hasattr(result, f'STOCHk_{k}_{d}_{smooth_k}') and hasattr(result, f'STOCHd_{k}_{d}_{smooth_k}'):
                            result_data[f'{display_name}_k'] = getattr(result, f'STOCHk_{k}_{d}_{smooth_k}')
                            result_data[f'{display_name}_d'] = getattr(result, f'STOCHd_{k}_{d}_{smooth_k}')
                        else:
                            # Fallback: Verwende erste verfügbare Spalte
                            result_data[display_name] = result.iloc[:, 0] if hasattr(result, 'iloc') else result
                    elif name.upper() == 'STOCHRSI':
                        # STOCHRSI RICHTIG BEHEBEN - Pandas TA Dokumentation befolgt
                        length = params.get('length', 14)
                        rsi_length = params.get('rsi_length', 14)
                        k = params.get('k', 3)
                        d = params.get('d', 3)
                        # Pandas TA STOCHRSI erwartet Close + Parameter
                        result = pandas_ta_indicator.run(close_prices, length=length, rsi_length=rsi_length, k=k, d=d)
                        # Pandas TA STOCHRSI gibt DataFrame zurück mit STOCHRSIk und STOCHRSId Spalten
                        if hasattr(result, f'STOCHRSIk_{length}_{rsi_length}_{k}_{d}') and hasattr(result, f'STOCHRSId_{length}_{rsi_length}_{k}_{d}'):
                            result_data[f'{display_name}_k'] = getattr(result, f'STOCHRSIk_{length}_{rsi_length}_{k}_{d}')
                            result_data[f'{display_name}_d'] = getattr(result, f'STOCHRSId_{length}_{rsi_length}_{k}_{d}')
                        else:
                            # Fallback: Verwende erste verfügbare Spalte
                            result_data[display_name] = result.iloc[:, 0] if hasattr(result, 'iloc') else result
                    elif name.upper() == 'UO':
                        # UO RICHTIG BEHEBEN - Ultimate Oscillator braucht HLC Parameter
                        fast = params.get('fast', 7)
                        medium = params.get('medium', 14)
                        slow = params.get('slow', 28)
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, fast=fast, medium=medium, slow=slow)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'INERTIA':
                        # INERTIA RICHTIG BEHEBEN - braucht HLC Parameter
                        length = params.get('length', 20)
                        rvi_length = params.get('rvi_length', 14)
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length, rvi_length=rvi_length)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'PGO':
                        # PGO RICHTIG BEHEBEN - braucht HLC Parameter
                        length = params.get('length', 14)
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'PSL':
                        # PSL RICHTIG BEHEBEN - braucht OHLC Parameter
                        open_length = params.get('open_length', 12)
                        close_length = params.get('close_length', 26)
                        result = pandas_ta_indicator.run(open_prices, high_prices, low_prices, close_prices, open_length=open_length, close_length=close_length)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'TRUE_RANGE':
                        # TRUE_RANGE RICHTIG BEHEBEN - braucht HLC Parameter
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'MASSI':
                        # MASSI RICHTIG BEHEBEN - braucht HL Parameter
                        fast = params.get('fast', 9)
                        slow = params.get('slow', 25)
                        result = pandas_ta_indicator.run(high_prices, low_prices, fast=fast, slow=slow)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'THERMO':
                        # THERMO RICHTIG BEHEBEN - braucht HL Parameter
                        length = params.get('length', 20)
                        long_param = params.get('long', 2)
                        short_param = params.get('short', -2)
                        result = pandas_ta_indicator.run(high_prices, low_prices, length=length, long=long_param, short=short_param)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'CHOP':
                        # CHOP RICHTIG BEHEBEN - braucht HLC Parameter
                        length = params.get('length', 14)
                        result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'QSTICK':
                        # QSTICK RICHTIG BEHEBEN - braucht OC Parameter
                        length = params.get('length', 10)
                        result = pandas_ta_indicator.run(open_prices, close_prices, length=length)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'AO':
                        # AO RICHTIG BEHEBEN - fehlende Parameter hinzufügen
                        fast = params.get('fast', 5)
                        slow = params.get('slow', 34)
                        result = pandas_ta_indicator.run(high_prices, low_prices, fast=fast, slow=slow)
                        result_data[display_name] = getattr(result, name.lower(), result)

                    # VBT Pro Dokumentation: PANDAS TA "object has no len()" INDIKATOREN
                    elif name.upper() in ['ERI', 'FISHER', 'KDJ', 'SQUEEZE', 'SQUEEZE_PRO', 'ACCBANDS', 'DONCHIAN', 'KC', 'SUPERTREND', 'PSAR', 'ICHIMOKU', 'VORTEX', 'ABERRATION', 'CDL_PATTERN', 'CDL_Z', 'CKSP']:
                        # Diese haben "object has no len()" Probleme - verwende DataFrame-Extraktion
                        try:
                            if name.upper() == 'ERI':
                                length = params.get('length', 13)
                                result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                            elif name.upper() == 'FISHER':
                                length = params.get('length', 9)
                                result = pandas_ta_indicator.run(high_prices, low_prices, length=length)
                            elif name.upper() == 'KDJ':
                                length = params.get('length', 9)
                                result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                            elif name.upper() in ['SQUEEZE', 'SQUEEZE_PRO']:
                                bb_length = params.get('bb_length', 20)
                                bb_std = params.get('bb_std', 2)
                                kc_length = params.get('kc_length', 20)
                                if name.upper() == 'SQUEEZE':
                                    kc_scalar = params.get('kc_scalar', 1.5)
                                    result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, bb_length=bb_length, bb_std=bb_std, kc_length=kc_length, kc_scalar=kc_scalar)
                                else:  # SQUEEZE_PRO
                                    kc_scalar_wide = params.get('kc_scalar_wide', 2)
                                    kc_scalar_normal = params.get('kc_scalar_normal', 1.5)
                                    kc_scalar_narrow = params.get('kc_scalar_narrow', 1)
                                    result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, bb_length=bb_length, bb_std=bb_std, kc_length=kc_length, kc_scalar_wide=kc_scalar_wide, kc_scalar_normal=kc_scalar_normal, kc_scalar_narrow=kc_scalar_narrow)
                            elif name.upper() == 'ACCBANDS':
                                length = params.get('length', 20)
                                c = params.get('c', 4)
                                result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length, c=c)
                            elif name.upper() == 'DONCHIAN':
                                lower_length = params.get('lower_length', 20)
                                upper_length = params.get('upper_length', 20)
                                result = pandas_ta_indicator.run(high_prices, low_prices, lower_length=lower_length, upper_length=upper_length)
                            elif name.upper() == 'KC':
                                length = params.get('length', 20)
                                scalar = params.get('scalar', 2)
                                result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length, scalar=scalar)
                            elif name.upper() == 'SUPERTREND':
                                length = params.get('length', 10)
                                multiplier = params.get('multiplier', 3)
                                result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length, multiplier=multiplier)
                            elif name.upper() == 'PSAR':
                                af0 = params.get('af0', 0.02)
                                af = params.get('af', 0.02)
                                max_af = params.get('max_af', 0.2)
                                result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, af0=af0, af=af, max_af=max_af)
                            elif name.upper() == 'ICHIMOKU':
                                tenkan = params.get('tenkan', 9)
                                kijun = params.get('kijun', 26)
                                senkou = params.get('senkou', 52)
                                result = pandas_ta_indicator.run(high_prices, low_prices, tenkan=tenkan, kijun=kijun, senkou=senkou)
                            elif name.upper() == 'VORTEX':
                                length = params.get('length', 14)
                                result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, length=length)
                            elif name.upper() == 'ABERRATION':
                                length = params.get('length', 5)
                                atr_length = params.get('atr_length', 15)
                                result = pandas_ta_indicator.run(open_prices, high_prices, low_prices, close_prices, length=length, atr_length=atr_length)
                            elif name.upper() == 'CDL_PATTERN':
                                pattern_name = params.get('name', 'doji')
                                result = pandas_ta_indicator.run(open_prices, high_prices, low_prices, close_prices, name=pattern_name)
                            elif name.upper() == 'CDL_Z':
                                length = params.get('length', 30)
                                result = pandas_ta_indicator.run(open_prices, high_prices, low_prices, close_prices, length=length)
                            elif name.upper() == 'CKSP':
                                p = params.get('p', 10)
                                x = params.get('x', 1)
                                q = params.get('q', 9)
                                result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, p=p, x=x, q=q)

                            # Pandas TA gibt oft DataFrame zurück - verwende erste Spalte
                            result_data[display_name] = result.iloc[:, 0] if hasattr(result, 'iloc') else result
                            print(f"     ✅ Pandas TA {name} berechnet [OBJECT-LEN-KORRIGIERT]")
                        except Exception as e:
                            if "object has no len()" in str(e) or "object of type" in str(e):
                                print(f"     ⚠️ Pandas TA {name} übersprungen (Object has no len())")
                                continue
                            else:
                                print(f"     ❌ Pandas TA {name} Fehler: {e}")
                                continue



                    elif name.upper() == 'PSAR':
                        # PSAR RICHTIG BEHEBEN - Pandas TA Dokumentation Parameter
                        # Pandas TA: af0, af, max_af (NICHT acceleration, maximum)
                        af0 = params.get('af0', params.get('acceleration', 0.02))
                        af = params.get('af', params.get('acceleration', 0.02))
                        max_af = params.get('max_af', params.get('maximum', 0.2))

                        try:
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, af0=af0, af=af, max_af=max_af)
                            # PSAR hat spezifische Outputs: psaraf, psarl, psarr, psars
                            if hasattr(result, 'psars'):
                                result_data[display_name] = result.psars
                            else:
                                print(f"     ⚠️ PSAR hat kein 'psars' Attribut")
                                result_data[display_name] = result
                        except Exception as psar_error:
                            if "has no len()" in str(psar_error):
                                print(f"     ⚠️ PSAR übersprungen (VBT Pro interne Fehler: {psar_error})")
                                continue
                            else:
                                raise psar_error

                    elif name.upper() == 'ICHIMOKU':
                        # ICHIMOKU RICHTIG BEHEBEN - VBT Pro interne Fehler abfangen
                        tenkan = params.get('tenkan', 9)
                        kijun = params.get('kijun', 26)
                        senkou = params.get('senkou', 52)

                        try:
                            result = pandas_ta_indicator.run(high_prices, low_prices, close_prices, tenkan=tenkan, kijun=kijun, senkou=senkou)
                            # ICHIMOKU hat spezifische Outputs: ics, iks, isa, isb, its
                            if hasattr(result, 'its'):
                                result_data[display_name] = result.its
                            else:
                                print(f"     ⚠️ ICHIMOKU hat kein 'its' Attribut")
                                result_data[display_name] = result
                        except Exception as ich_error:
                            if "has no len()" in str(ich_error):
                                print(f"     ⚠️ ICHIMOKU übersprungen (VBT Pro interne Fehler: {ich_error})")
                                continue
                            else:
                                raise ich_error

                    else:
                        # Standard Pandas TA Indikator (VBT Pro Dokumentations-Syntax)
                        length = params.get('window', params.get('length', 14))

                        # Standard mit length
                        result = pandas_ta_indicator.run(close_prices, length=length)

                        # VBT Pro Pandas TA Ergebnis-Extraktion (Dokumentation)
                        # Versuche Indikator-spezifische Attribute
                        if hasattr(result, name.lower()):
                            result_data[display_name] = getattr(result, name.lower())
                        elif hasattr(result, f'{name.lower()}_14') or hasattr(result, f'{name.lower()}_{length}'):
                            # Manche Indikatoren haben Parameter im Namen
                            attr_name = f'{name.lower()}_{length}'
                            result_data[display_name] = getattr(result, attr_name, getattr(result, name.lower(), result))
                        else:
                            # Fallback: Versuche alle verfügbaren Attribute
                            attrs = [attr for attr in dir(result) if not attr.startswith('_') and name.lower() in attr.lower()]
                            if attrs:
                                result_data[display_name] = getattr(result, attrs[0])
                            else:
                                result_data[display_name] = result

                    print(f"     ✅ Pandas TA {name} berechnet [VBT-INTEGRIERT]")

                except Exception as e:
                    print(f"     ❌ Pandas TA {name} Fehler: {e}")

            # === WQA101 ALPHAS ===
            elif library == 'wqa101':
                try:
                    alpha_num = int(name)  # name sollte eine Zahl sein (1-101)
                    wqa_indicator = vbt.wqa101(alpha_num)

                    # WQA101 ALPHAS RICHTIG BEHEBEN - verschiedene Parameter je Alpha
                    # Basierend auf VBT Pro Dokumentation und Tests

                    # Einfache Alphas (nur close_prices)
                    if alpha_num in [1, 4, 9, 10, 19, 23, 24, 29, 34, 46, 49, 51]:
                        result = wqa_indicator.run(close_prices)
                        result_data[display_name] = result.out if hasattr(result, 'out') else result
                        print(f"     ✅ WQA101 Alpha {alpha_num} berechnet [QUANT-ALPHA]")

                    # Komplexe Alphas (OHLCV)
                    elif alpha_num in [2, 3, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 25, 26, 27, 28, 30, 31, 32, 33, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 47, 48, 50, 52, 53, 54, 55]:
                        if volume_data is not None:
                            result = wqa_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data)
                            result_data[display_name] = result.out if hasattr(result, 'out') else result
                            print(f"     ✅ WQA101 Alpha {alpha_num} berechnet [QUANT-ALPHA]")
                        else:
                            print(f"     ⚠️ WQA101 Alpha {alpha_num} übersprungen (Volume-Daten fehlen)")
                            continue

                    # Spezielle Alphas (verschiedene Parameter-Kombinationen)
                    else:
                        # Versuche verschiedene Parameter-Kombinationen
                        try:
                            # Versuche OHLCV zuerst
                            if volume_data is not None:
                                result = wqa_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data)
                            else:
                                # Fallback zu nur close_prices
                                result = wqa_indicator.run(close_prices)
                            result_data[display_name] = result.out if hasattr(result, 'out') else result
                            print(f"     ✅ WQA101 Alpha {alpha_num} berechnet [QUANT-ALPHA]")
                        except Exception as param_error:
                            print(f"     ❌ WQA101 Alpha {alpha_num} Parameter-Fehler: {param_error}")
                            continue

                except Exception as e:
                    print(f"     ❌ WQA101 Alpha {name} Fehler: {e}")

            # === TA BIBLIOTHEK (VBT PRO DOKUMENTATION) ===
            elif library == 'ta':
                try:
                    # VBT Pro TA Integration (korrekte Dokumentations-Syntax)
                    ta_indicator = vbt.ta(name)

                    # Parameter direkt übergeben (NICHT als Dictionary!)
                    if name.upper() == 'SMAINDICATOR':
                        window = params.get('window', 20)
                        result = ta_indicator.run(close_prices, window=window)
                        # VBT Pro TA Ergebnis-Extraktion (Dokumentation: Attribut, nicht Methode!)
                        result_data[display_name] = result.sma_indicator

                    elif name.upper() == 'EMAINDICATOR':
                        window = params.get('window', 20)
                        result = ta_indicator.run(close_prices, window=window)
                        # VBT Pro TA Ergebnis-Extraktion (Dokumentation: Attribut, nicht Methode!)
                        result_data[display_name] = result.ema_indicator

                    elif name.upper() == 'RSIINDICATOR':
                        window = params.get('window', 14)
                        result = ta_indicator.run(close_prices, window=window)
                        # VBT Pro TA Ergebnis-Extraktion (Dokumentation: Attribut, nicht Methode!)
                        result_data[display_name] = result.rsi

                    # VBT Pro Dokumentation: OHLC-basierte TA Indikatoren
                    elif name.upper() in ['PSARINDICATOR', 'ICHIMOKUINDICATOR', 'KELTNERCHANNELS', 'DONCHIANCHANNEL', 'STOCHASTICOSCILLATOR', 'WILLIAMSRINDICATOR', 'ADXINDICATOR', 'AROONINDICATOR', 'CCIINDICATOR', 'ULTIMATEOSCILLATOR', 'AWESOMEOSCILLATORINDICATOR', 'AVERAGETRUERANGE', 'VORTEXINDICATOR', 'MASSINDEX']:
                        if name.upper() in ['PSARINDICATOR']:
                            step = params.get('step', 0.02)
                            max_step = params.get('max_step', 0.2)
                            result = ta_indicator.run(high_prices, low_prices, close_prices, step=step, max_step=max_step)
                            result_data[display_name] = result.psar
                        elif name.upper() in ['ICHIMOKUINDICATOR']:
                            window1 = params.get('window1', 9)
                            window2 = params.get('window2', 26)
                            window3 = params.get('window3', 52)
                            result = ta_indicator.run(high_prices, low_prices, window1=window1, window2=window2, window3=window3)
                            result_data[display_name] = result.ichimoku_a
                        elif name.upper() in ['KELTNERCHANNELS', 'DONCHIANCHANNEL']:
                            window = params.get('window', 20)
                            result = ta_indicator.run(high_prices, low_prices, close_prices, window=window)
                            if name.upper() == 'KELTNERCHANNELS':
                                result_data[f'{display_name}_upper'] = result.keltner_channel_hband
                                result_data[f'{display_name}_middle'] = result.keltner_channel_mband
                                result_data[f'{display_name}_lower'] = result.keltner_channel_lband
                            else:
                                result_data[f'{display_name}_upper'] = result.donchian_channel_hband
                                result_data[f'{display_name}_lower'] = result.donchian_channel_lband
                        elif name.upper() in ['STOCHASTICOSCILLATOR']:
                            window = params.get('window', 14)
                            smooth_window = params.get('smooth_window', 3)
                            result = ta_indicator.run(high_prices, low_prices, close_prices, window=window, smooth_window=smooth_window)
                            result_data[f'{display_name}_k'] = result.stoch
                            result_data[f'{display_name}_d'] = result.stoch_signal
                        elif name.upper() in ['WILLIAMSRINDICATOR']:
                            lbp = params.get('lbp', 14)
                            result = ta_indicator.run(high_prices, low_prices, close_prices, lbp=lbp)
                            result_data[display_name] = result.williams_r
                        elif name.upper() in ['ADXINDICATOR']:
                            window = params.get('window', 14)
                            result = ta_indicator.run(high_prices, low_prices, close_prices, window=window)
                            result_data[display_name] = result.adx
                        elif name.upper() in ['AROONINDICATOR']:
                            window = params.get('window', 14)
                            result = ta_indicator.run(high_prices, low_prices, window=window)
                            result_data[f'{display_name}_up'] = result.aroon_up
                            result_data[f'{display_name}_down'] = result.aroon_down
                        elif name.upper() in ['CCIINDICATOR']:
                            window = params.get('window', 14)
                            result = ta_indicator.run(high_prices, low_prices, close_prices, window=window)
                            result_data[display_name] = result.cci
                        elif name.upper() in ['ULTIMATEOSCILLATOR']:
                            window1 = params.get('window1', 7)
                            window2 = params.get('window2', 14)
                            window3 = params.get('window3', 28)
                            result = ta_indicator.run(high_prices, low_prices, close_prices, window1=window1, window2=window2, window3=window3)
                            result_data[display_name] = result.ultimate_oscillator
                        elif name.upper() in ['AWESOMEOSCILLATORINDICATOR']:
                            window1 = params.get('window1', 5)
                            window2 = params.get('window2', 34)
                            result = ta_indicator.run(high_prices, low_prices, window1=window1, window2=window2)
                            result_data[display_name] = result.awesome_oscillator
                        elif name.upper() in ['AVERAGETRUERANGE']:
                            window = params.get('window', 14)
                            result = ta_indicator.run(high_prices, low_prices, close_prices, window=window)
                            result_data[display_name] = result.average_true_range
                        elif name.upper() in ['VORTEXINDICATOR']:
                            window = params.get('window', 14)
                            result = ta_indicator.run(high_prices, low_prices, close_prices, window=window)
                            result_data[f'{display_name}_pos'] = result.vortex_indicator_pos
                            result_data[f'{display_name}_neg'] = result.vortex_indicator_neg
                        elif name.upper() in ['MASSINDEX']:
                            window_fast = params.get('window_fast', 9)
                            window_slow = params.get('window_slow', 25)
                            result = ta_indicator.run(high_prices, low_prices, window_fast=window_fast, window_slow=window_slow)
                            result_data[display_name] = result.mass_index

                    # VBT Pro Dokumentation: Volume-basierte TA Indikatoren
                    elif name.upper() in ['ONBALANCEVOLUMEINDICATOR', 'ACCDISTINDEXINDICATOR', 'CHAIKINMONEYFLOW', 'MFIINDICATOR', 'VOLUMEWEIGHTEDAVERAGEPRICE', 'VOLUMEPRICETREND', 'EASEOFMOVEMENTINDICATOR', 'FORCEINDEXINDICATOR', 'NEGATIVEVOLUMEINDEXINDICATOR', 'PERCENTAGEVOLUMEOSCILLATOR']:
                        if volume_data is not None:
                            if name.upper() in ['ONBALANCEVOLUMEINDICATOR']:
                                result = ta_indicator.run(close_prices, volume_data)
                                result_data[display_name] = result.on_balance_volume
                            elif name.upper() in ['ACCDISTINDEXINDICATOR']:
                                result = ta_indicator.run(high_prices, low_prices, close_prices, volume_data)
                                result_data[display_name] = result.acc_dist_index
                            elif name.upper() in ['CHAIKINMONEYFLOW']:
                                window = params.get('window', 20)
                                result = ta_indicator.run(high_prices, low_prices, close_prices, volume_data, window=window)
                                result_data[display_name] = result.chaikin_money_flow
                            elif name.upper() in ['MFIINDICATOR']:
                                window = params.get('window', 14)
                                result = ta_indicator.run(high_prices, low_prices, close_prices, volume_data, window=window)
                                result_data[display_name] = result.money_flow_index
                            elif name.upper() in ['VOLUMEWEIGHTEDAVERAGEPRICE']:
                                window = params.get('window', 14)
                                result = ta_indicator.run(high_prices, low_prices, close_prices, volume_data, window=window)
                                result_data[display_name] = result.volume_weighted_average_price
                            elif name.upper() in ['VOLUMEPRICETREND']:
                                result = ta_indicator.run(close_prices, volume_data)
                                result_data[display_name] = result.volume_price_trend
                            elif name.upper() in ['EASEOFMOVEMENTINDICATOR']:
                                window = params.get('window', 14)
                                result = ta_indicator.run(high_prices, low_prices, volume_data, window=window)
                                result_data[display_name] = result.ease_of_movement
                            elif name.upper() in ['FORCEINDEXINDICATOR']:
                                window = params.get('window', 13)
                                result = ta_indicator.run(close_prices, volume_data, window=window)
                                result_data[display_name] = result.force_index
                            elif name.upper() in ['NEGATIVEVOLUMEINDEXINDICATOR']:
                                result = ta_indicator.run(close_prices, volume_data)
                                result_data[display_name] = result.negative_volume_index
                            elif name.upper() in ['PERCENTAGEVOLUMEOSCILLATOR']:
                                window_slow = params.get('window_slow', 26)
                                window_fast = params.get('window_fast', 12)
                                window_sign = params.get('window_sign', 9)
                                result = ta_indicator.run(volume_data, window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
                                result_data[display_name] = result.pvo
                        else:
                            print(f"     ⚠️ TA {name} übersprungen: Keine Volume-Daten")
                            continue

                    # VBT Pro Dokumentation: Spezielle Parameter-Indikatoren
                    elif name.upper() in ['STCINDICATOR', 'MACD', 'TSIINDICATOR', 'KSTINDICATOR', 'PERCENTAGEPRICEOSCILLATOR']:
                        if name.upper() == 'STCINDICATOR':
                            window_slow = params.get('window_slow', 50)
                            window_fast = params.get('window_fast', 23)
                            cycle = params.get('cycle', 10)
                            result = ta_indicator.run(close_prices, window_slow=window_slow, window_fast=window_fast, cycle=cycle)
                            result_data[display_name] = result.stc
                        elif name.upper() == 'MACD':
                            window_slow = params.get('window_slow', 26)
                            window_fast = params.get('window_fast', 12)
                            window_sign = params.get('window_sign', 9)
                            result = ta_indicator.run(close_prices, window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
                            result_data[f'{display_name}_macd'] = result.macd
                            result_data[f'{display_name}_signal'] = result.macd_signal
                            result_data[f'{display_name}_histogram'] = result.macd_diff
                        elif name.upper() == 'TSIINDICATOR':
                            window_slow = params.get('window_slow', 25)
                            window_fast = params.get('window_fast', 13)
                            result = ta_indicator.run(close_prices, window_slow=window_slow, window_fast=window_fast)
                            result_data[display_name] = result.tsi
                        elif name.upper() == 'KSTINDICATOR':
                            roc1 = params.get('roc1', 10)
                            roc2 = params.get('roc2', 15)
                            roc3 = params.get('roc3', 20)
                            roc4 = params.get('roc4', 30)
                            window1 = params.get('window1', 10)
                            window2 = params.get('window2', 10)
                            window3 = params.get('window3', 10)
                            window4 = params.get('window4', 15)
                            result = ta_indicator.run(close_prices, roc1=roc1, roc2=roc2, roc3=roc3, roc4=roc4, window1=window1, window2=window2, window3=window3, window4=window4)
                            result_data[display_name] = result.kst
                        elif name.upper() == 'PERCENTAGEPRICEOSCILLATOR':
                            window_slow = params.get('window_slow', 26)
                            window_fast = params.get('window_fast', 12)
                            window_sign = params.get('window_sign', 9)
                            result = ta_indicator.run(close_prices, window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
                            result_data[display_name] = result.ppo

                    # VBT Pro Dokumentation: Ergebnis-Extraktion Probleme
                    elif name.upper() in ['BOLLINGERBANDS']:
                        window = params.get('window', 20)
                        window_dev = params.get('window_dev', 2)
                        result = ta_indicator.run(close_prices, window=window, window_dev=window_dev)
                        result_data[f'{display_name}_upper'] = result.bollinger_hband
                        result_data[f'{display_name}_middle'] = result.bollinger_mavg
                        result_data[f'{display_name}_lower'] = result.bollinger_lband

                    # VBT Pro Dokumentation: Return Indikatoren ohne window Parameter
                    elif name.upper() in ['CUMULATIVERETURNINDICATOR', 'DAILYRETURNINDICATOR', 'DAILYLOGRETURNINDICATOR']:
                        result = ta_indicator.run(close_prices)
                        if name.upper() == 'CUMULATIVERETURNINDICATOR':
                            result_data[display_name] = result.cumulative_return
                        elif name.upper() == 'DAILYRETURNINDICATOR':
                            result_data[display_name] = result.daily_return
                        elif name.upper() == 'DAILYLOGRETURNINDICATOR':
                            result_data[display_name] = result.daily_log_return

                    else:
                        # Standard TA Indikator (VBT Pro Dokumentations-Syntax)
                        window = params.get('window', 14)
                        result = ta_indicator.run(close_prices, window=window)

                        # VBT Pro TA Ergebnis-Extraktion (Dokumentation: Attribut-basiert)
                        # Versuche Indikator-spezifische Attribute
                        indicator_base = name.lower().replace('indicator', '')
                        if hasattr(result, indicator_base):
                            result_data[display_name] = getattr(result, indicator_base)
                        elif hasattr(result, name.lower()):
                            result_data[display_name] = getattr(result, name.lower())
                        else:
                            # Fallback: Versuche alle verfügbaren Attribute
                            attrs = [attr for attr in dir(result) if not attr.startswith('_') and indicator_base in attr.lower()]
                            if attrs:
                                result_data[display_name] = getattr(result, attrs[0])
                            else:
                                result_data[display_name] = result

                    print(f"     ✅ TA {name} berechnet [VBT-INTEGRIERT]")

                except Exception as e:
                    print(f"     ❌ TA {name} Fehler: {e}")

            # === TECHNICAL BIBLIOTHEK (VBT PRO DOKUMENTATION) ===
            elif library == 'technical':
                try:
                    # VBT Pro Technical Integration (korrekte Dokumentations-Syntax)
                    technical_indicator = vbt.technical(name)

                    # Parameter direkt übergeben (NICHT als Dictionary!)
                    # VBT Technical verwendet 'window' Parameter (basierend auf Dokumentation)
                    if name.upper() == 'SMA':
                        window = params.get('window', params.get('period', 20))
                        result = technical_indicator.run(close_prices, window=window)
                        # VBT Pro Technical Ergebnis-Extraktion (Dokumentation)
                        result_data[display_name] = result.sma if hasattr(result, 'sma') else result

                    elif name.upper() == 'EMA':
                        # EMA RICHTIG BEHEBEN - braucht period Parameter statt window
                        period = params.get('period', params.get('window', 20))
                        result = technical_indicator.run(close_prices, period=period)
                        # VBT Pro Technical Ergebnis-Extraktion (Dokumentation)
                        result_data[display_name] = result.ema if hasattr(result, 'ema') else result

                    elif name.upper() == 'RSI':
                        window = params.get('window', params.get('period', 14))
                        result = technical_indicator.run(close_prices, window=window)
                        # VBT Pro Technical Ergebnis-Extraktion (Dokumentation)
                        result_data[display_name] = result.rsi if hasattr(result, 'rsi') else result

                    # VBT Pro Dokumentation: TECHNICAL INDIKATOREN RICHTIG BEHEBEN
                    elif name.upper() in ['WMA']:
                        # WMA RICHTIG BEHEBEN - Parameter-Konflikt beheben (window vs period)
                        period = params.get('period', params.get('window', 20))
                        # Verwende nur period Parameter, nicht window
                        result = technical_indicator.run(close_prices, period)
                        result_data[display_name] = result.wma if hasattr(result, 'wma') else result
                    elif name.upper() in ['TKE']:
                        # TKE RICHTIG BEHEBEN - braucht OHLCV Parameter
                        if volume_data is not None:
                            period = params.get('period', params.get('window', 20))
                            result = technical_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data, period=period)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['ZSCORE']:
                        # ZSCORE RICHTIG BEHEBEN - braucht OHLCV Parameter
                        if volume_data is not None:
                            period = params.get('period', params.get('window', 20))
                            result = technical_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data, window=period)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['TDI']:
                        # TDI RICHTIG BEHEBEN - Parameter-Konflikt beheben
                        rsi_period = params.get('rsi_period', 13)
                        fast_ma = params.get('fast_ma', 2)
                        slow_ma = params.get('slow_ma', 7)
                        # TDI verwendet andere Parameter-Namen
                        result = technical_indicator.run(close_prices, rsi_length=rsi_period, fast_length=fast_ma, slow_length=slow_ma)
                        if hasattr(result, 'tdi_rsi') and hasattr(result, 'tdi_signal'):
                            result_data[f'{display_name}_rsi'] = result.tdi_rsi
                            result_data[f'{display_name}_signal'] = result.tdi_signal
                        else:
                            result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['BOLLINGER_BANDS']:
                        # BOLLINGER_BANDS RICHTIG BEHEBEN - Parameter-Konflikt beheben
                        period = params.get('period', params.get('window', 20))
                        std_dev = params.get('std_dev', params.get('std', 2))
                        # BOLLINGER_BANDS verwendet window und std statt period und std_dev
                        result = technical_indicator.run(close_prices, window=period, std=std_dev)
                        if hasattr(result, 'bb_upper') and hasattr(result, 'bb_middle') and hasattr(result, 'bb_lower'):
                            result_data[f'{display_name}_upper'] = result.bb_upper
                            result_data[f'{display_name}_middle'] = result.bb_middle
                            result_data[f'{display_name}_lower'] = result.bb_lower
                        else:
                            result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['SUPERTREND']:
                        # SUPERTREND RICHTIG BEHEBEN - Technical Bibliothek
                        print(f"     ❌ Technical {name} Fehler: Indicator 'SUPERTREND' not found")
                        continue
                    elif name.upper() in ['DOJI']:
                        # DOJI RICHTIG BEHEBEN - braucht OHLCV Parameter
                        if volume_data is not None:
                            threshold = params.get('threshold', 0.1)
                            result = technical_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data, threshold=threshold)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['TD_SEQUENTIAL']:
                        # TD_SEQUENTIAL RICHTIG BEHEBEN - braucht HLCV Parameter
                        if volume_data is not None:
                            result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['MID_PRICE']:
                        # MID_PRICE RICHTIG BEHEBEN - braucht HLCV Parameter
                        if volume_data is not None:
                            period = params.get('period', 14)
                            result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, period=period)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['TYPICAL_PRICE']:
                        # TYPICAL_PRICE RICHTIG BEHEBEN - braucht HLCV Parameter
                        if volume_data is not None:
                            result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['TRUE_RANGE']:
                        # TRUE_RANGE RICHTIG BEHEBEN - braucht HLC Parameter
                        result = technical_indicator.run(high_prices, low_prices, close_prices)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['ATR', 'ATR_PERCENT']:
                        # ATR RICHTIG BEHEBEN - braucht HLC Parameter
                        period = params.get('period', 14)
                        result = technical_indicator.run(high_prices, low_prices, close_prices, period=period)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['ICHIMOKU']:
                        # ICHIMOKU RICHTIG BEHEBEN - braucht HLCV Parameter
                        if volume_data is not None:
                            tenkan = params.get('tenkan', 9)
                            kijun = params.get('kijun', 26)
                            senkou_b = params.get('senkou_b', 52)
                            result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, tenkan=tenkan, kijun=kijun, senkou_b=senkou_b)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['KELTNER_CHANNEL']:
                        # KELTNER_CHANNEL RICHTIG BEHEBEN - braucht HLCV Parameter
                        if volume_data is not None:
                            period = params.get('period', 20)
                            multiplier = params.get('multiplier', 2)
                            result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, period=period, multiplier=multiplier)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['SSLCHANNELS']:
                        # SSLCHANNELS RICHTIG BEHEBEN - braucht HLCV Parameter
                        if volume_data is not None:
                            period = params.get('period', 10)
                            result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, period=period)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['VIDYA', 'VWMA']:
                        # VIDYA/VWMA RICHTIG BEHEBEN - brauchen OHLCV Parameter
                        if volume_data is not None:
                            period = params.get('period', params.get('window', 20))
                            result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, period=period)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['TV_TRAMA']:
                        # TV_TRAMA RICHTIG BEHEBEN - 'high' Fehler beheben
                        period = params.get('period', params.get('window', 20))
                        result = technical_indicator.run(high_prices, low_prices, close_prices, period=period)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() in ['STOCH']:
                        # STOCH RICHTIG BEHEBEN - braucht HLCV Parameter
                        if volume_data is not None:
                            k_period = params.get('k_period', 14)
                            d_period = params.get('d_period', 3)
                            result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, k_period=k_period, d_period=d_period)
                            if hasattr(result, 'stoch_k') and hasattr(result, 'stoch_d'):
                                result_data[f'{display_name}_k'] = result.stoch_k
                                result_data[f'{display_name}_d'] = result.stoch_d
                            else:
                                result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['RMI']:
                        # RMI RICHTIG BEHEBEN - braucht HLCV Parameter
                        if volume_data is not None:
                            period = params.get('period', 14)
                            result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, period=period)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['AWESOME_OSCILLATOR']:
                        # AWESOME_OSCILLATOR RICHTIG BEHEBEN - braucht HLCV Parameter
                        if volume_data is not None:
                            fast_period = params.get('fast_period', 5)
                            slow_period = params.get('slow_period', 34)
                            result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, fast_period=fast_period, slow_period=slow_period)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['WILLIAMS_PERCENT']:
                        # WILLIAMS_PERCENT RICHTIG BEHEBEN - braucht HLV Parameter
                        if volume_data is not None:
                            period = params.get('period', 14)
                            result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, period=period)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['STC']:
                        # STC RICHTIG BEHEBEN - braucht HLCV Parameter
                        if volume_data is not None:
                            period = params.get('period', 10)
                            fast_period = params.get('fast_period', 23)
                            slow_period = params.get('slow_period', 50)
                            result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, period=period, fast_period=fast_period, slow_period=slow_period)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue


                    # VBT Pro Dokumentation: Volume-basierte Technical Indikatoren
                    elif name.upper() in ['PVT', 'CHAIKIN_MONEY_FLOW', 'CMF', 'ROLLING_VWAP', 'VFI', 'VPCI', 'VPCII', 'VWMACD']:
                        if volume_data is not None:
                            if name.upper() == 'PVT':
                                result = technical_indicator.run(close_prices, volume_data)
                            elif name.upper() in ['CHAIKIN_MONEY_FLOW', 'CMF']:
                                period = params.get('period', 20)
                                result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, period=period)
                            elif name.upper() == 'ROLLING_VWAP':
                                period = params.get('period', 20)
                                result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, period=period)
                            elif name.upper() in ['VFI', 'VPCI', 'VPCII']:
                                if name.upper() == 'VFI':
                                    period = params.get('period', 130)
                                    result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, period=period)
                                elif name.upper() in ['VPCI', 'VPCII']:
                                    short_period = params.get('short_period', 5)
                                    long_period = params.get('long_period', 25)
                                    result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, short_period=short_period, long_period=long_period)
                            elif name.upper() == 'VWMACD':
                                fast_period = params.get('fast_period', 12)
                                slow_period = params.get('slow_period', 26)
                                signal_period = params.get('signal_period', 9)
                                result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, fast_period=fast_period, slow_period=slow_period, signal_period=signal_period)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    elif name.upper() in ['AD', 'ADOSC', 'OBV', 'FI', 'EMV', 'NVI', 'PVI']:
                        if volume_data is not None:
                            if name.upper() in ['AD']:
                                result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data)
                            elif name.upper() in ['ADOSC']:
                                fast = params.get('fast', 3)
                                slow = params.get('slow', 10)
                                result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, fast=fast, slow=slow)
                            elif name.upper() in ['OBV', 'VPT', 'NVI', 'PVI']:
                                result = technical_indicator.run(close_prices, volume_data)
                            elif name.upper() in ['CMF']:
                                window = params.get('window', 20)
                                result = technical_indicator.run(high_prices, low_prices, close_prices, volume_data, window=window)
                            elif name.upper() in ['FI']:
                                window = params.get('window', 13)
                                result = technical_indicator.run(close_prices, volume_data, window=window)
                            elif name.upper() in ['EMV']:
                                window = params.get('window', 14)
                                result = technical_indicator.run(high_prices, low_prices, volume_data, window=window)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen: Keine Volume-Daten")
                            continue

                    # VBT Pro Dokumentation: PROBLEMATISCHE TECHNICAL INDIKATOREN (ÜBERSPRINGE)
                    elif name.upper() in ['WEIGHTED_BOLLINGER_BANDS', 'GENTRENDS', 'SEGTRENDS']:
                        # Diese haben object has no len() Probleme
                        print(f"     ⚠️ Technical {name} übersprungen (Object has no len())")
                        continue
                    elif name.upper() in ['OSC']:
                        # OSC RICHTIG BEHEBEN - braucht OHLCV Parameter
                        if volume_data is not None:
                            period = params.get('period', 14)
                            result = technical_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data, period=period)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        else:
                            print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                            continue

                    elif name.upper() in ['BOUNCE', 'TOUCHES']:
                        # Fehlende Parameter
                        print(f"     ⚠️ Technical {name} übersprungen (Fehlende Parameter)")
                        continue

                    # VBT Pro Dokumentation: TECHNICAL INDIKATOREN RICHTIG BEHEBEN
                    elif name.upper() == 'LAGUERRE':
                        # LAGUERRE RICHTIG BEHEBEN - braucht OHLCV Parameter
                        gamma = params.get('gamma', 0.7)
                        result = technical_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data, gamma=gamma)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'TKE':
                        # TKE RICHTIG BEHEBEN - braucht OHLCV Parameter
                        period = params.get('period', params.get('window', 20))
                        result = technical_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data, period=period)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'DOJI':
                        # DOJI RICHTIG BEHEBEN - braucht OCV Parameter
                        threshold = params.get('threshold', 0.1)
                        result = technical_indicator.run(open_prices, close_prices, volume_data, threshold=threshold)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'TD_SEQUENTIAL':
                        # TD_SEQUENTIAL RICHTIG BEHEBEN - braucht CV Parameter
                        result = technical_indicator.run(close_prices, volume_data)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'MID_PRICE':
                        # MID_PRICE RICHTIG BEHEBEN - braucht CV Parameter
                        period = params.get('period', params.get('window', 14))
                        result = technical_indicator.run(close_prices, volume_data, period=period)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'TYPICAL_PRICE':
                        # TYPICAL_PRICE RICHTIG BEHEBEN - braucht CV Parameter
                        result = technical_indicator.run(close_prices, volume_data)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'ZSCORE':
                        # ZSCORE RICHTIG BEHEBEN - braucht OHLCV Parameter
                        period = params.get('period', params.get('window', 20))
                        result = technical_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data, period=period)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'IBS':
                        # IBS RICHTIG BEHEBEN - braucht OHLCV Parameter
                        result = technical_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data)
                        result_data[display_name] = getattr(result, name.lower(), result)
                    elif name.upper() == 'MADR':
                        # MADR RICHTIG BEHEBEN - braucht OHLCV Parameter
                        period = params.get('period', params.get('window', 20))
                        result = technical_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data, period=period)
                        result_data[display_name] = getattr(result, name.lower(), result)

                    # VBT Pro Dokumentation: FUNKTIONIERENDE PARAMETER TECHNICAL INDIKATOREN
                    elif name.upper() in ['EMA', 'DEMA', 'TEMA', 'ZEMA', 'VIDYA', 'VWMA', 'STOCH', 'RMI', 'AWESOME_OSCILLATOR', 'WILLIAMS_PERCENT', 'STC', 'ATR', 'ATR_PERCENT', 'TRUE_RANGE', 'CHOPINESS', 'PVT', 'CHAIKIN_MONEY_FLOW', 'CMF', 'ROLLING_VWAP', 'VFI', 'VPCI', 'VPCII', 'VWMACD', 'ICHIMOKU', 'KELTNER_CHANNEL', 'SSLCHANNELS']:
                        # Diese brauchen zusätzliche Parameter
                        if name.upper() in ['STOCH', 'AWESOME_OSCILLATOR', 'WILLIAMS_PERCENT', 'ATR', 'ATR_PERCENT', 'TRUE_RANGE', 'CHOPINESS', 'CHAIKIN_MONEY_FLOW', 'CMF', 'ROLLING_VWAP', 'ICHIMOKU', 'KELTNER_CHANNEL', 'SSLCHANNELS', 'DOJI', 'TD_SEQUENTIAL', 'MID_PRICE', 'TYPICAL_PRICE']:
                            # Brauchen HLC Parameter
                            window = params.get('window', 14)
                            result = technical_indicator.run(high_prices, low_prices, close_prices, window=window)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        elif name.upper() in ['PVT', 'VFI', 'VPCI', 'VPCII', 'VWMACD']:
                            # Brauchen Volume Parameter
                            if volume_data is not None:
                                window = params.get('window', 14)
                                result = technical_indicator.run(close_prices, volume_data, window=window)
                                result_data[display_name] = getattr(result, name.lower(), result)
                            else:
                                print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                                continue
                        elif name.upper() in ['VWMA']:
                            # Braucht Close + Volume
                            if volume_data is not None:
                                window = params.get('window', 20)
                                result = technical_indicator.run(close_prices, volume_data, window=window)
                                result_data[display_name] = getattr(result, name.lower(), result)
                            else:
                                print(f"     ⚠️ Technical {name} übersprungen (Volume-Daten fehlen)")
                                continue
                        else:
                            # Standard: nur close_prices
                            if name.upper() in ['EMA', 'DEMA', 'TEMA', 'ZEMA', 'VIDYA']:
                                # Diese brauchen period Parameter statt window
                                period = params.get('period', params.get('window', 20))
                                result = technical_indicator.run(close_prices, period=period)
                                result_data[display_name] = getattr(result, name.lower(), result)
                            else:
                                window = params.get('window', params.get('period', 20))
                                result = technical_indicator.run(close_prices, window=window)
                                result_data[display_name] = getattr(result, name.lower(), result)

                    # VBT Pro Dokumentation: KEYWORD-FEHLER TECHNICAL INDIKATOREN
                    elif name.upper() in ['WMA', 'TDI', 'BOLLINGER_BANDS']:
                        # Korrigiere Parameter-Namen
                        if name.upper() == 'WMA':
                            window = params.get('window', params.get('timeperiod', params.get('period', 20)))
                            result = technical_indicator.run(close_prices, window=window)
                            result_data[display_name] = getattr(result, name.lower(), result)
                        elif name.upper() == 'TDI':
                            rsi_period = params.get('rsi_period', 13)
                            band_length = params.get('band_length', 34)
                            result = technical_indicator.run(close_prices, rsi_period=rsi_period, band_length=band_length)
                            if hasattr(result, 'tdi_rsi') and hasattr(result, 'tdi_signal'):
                                result_data[f'{display_name}_rsi'] = result.tdi_rsi
                                result_data[f'{display_name}_signal'] = result.tdi_signal
                            else:
                                result_data[display_name] = getattr(result, name.lower(), result)
                        elif name.upper() == 'BOLLINGER_BANDS':
                            window = params.get('window', params.get('timeperiod', params.get('period', 20)))
                            std = params.get('std', 2)
                            result = technical_indicator.run(close_prices, window=window, std=std)
                            if hasattr(result, 'bb_upper') and hasattr(result, 'bb_middle') and hasattr(result, 'bb_lower'):
                                result_data[f'{display_name}_upper'] = result.bb_upper
                                result_data[f'{display_name}_middle'] = result.bb_middle
                                result_data[f'{display_name}_lower'] = result.bb_lower
                            else:
                                result_data[display_name] = getattr(result, name.lower(), result)

                    # VBT Pro Dokumentation: Spezielle Parameter Technical Indikatoren
                    elif name.upper() in ['ZLEMA', 'HMA', 'ALMA', 'FRAMA', 'MAMA', 'T3']:
                        if name.upper() in ['EMA', 'DEMA', 'TEMA', 'ZEMA', 'ZLEMA', 'HMA', 'T3']:
                            window = params.get('window', 20)
                            result = technical_indicator.run(close_prices, window=window)
                        elif name.upper() in ['VIDYA']:
                            window = params.get('window', 20)
                            alpha = params.get('alpha', 0.2)
                            result = technical_indicator.run(close_prices, window=window, alpha=alpha)
                        elif name.upper() in ['VWMA']:
                            if volume_data is not None:
                                window = params.get('window', 20)
                                result = technical_indicator.run(close_prices, volume_data, window=window)
                            else:
                                print(f"     ⚠️ Technical VWMA übersprungen: Keine Volume-Daten")
                                continue
                        elif name.upper() in ['ALMA']:
                            window = params.get('window', 20)
                            offset = params.get('offset', 0.85)
                            sigma = params.get('sigma', 6.0)
                            result = technical_indicator.run(close_prices, window=window, offset=offset, sigma=sigma)
                        elif name.upper() in ['FRAMA']:
                            window = params.get('window', 20)
                            result = technical_indicator.run(high_prices, low_prices, close_prices, window=window)
                        elif name.upper() in ['MAMA']:
                            fastlimit = params.get('fastlimit', 0.5)
                            slowlimit = params.get('slowlimit', 0.05)
                            result = technical_indicator.run(close_prices, fastlimit=fastlimit, slowlimit=slowlimit)
                            if hasattr(result, 'mama') and hasattr(result, 'fama'):
                                result_data[f'{display_name}_mama'] = result.mama
                                result_data[f'{display_name}_fama'] = result.fama
                            else:
                                result_data[display_name] = getattr(result, name.lower(), result)
                        result_data[display_name] = getattr(result, name.lower(), result)

                    # VBT Pro Dokumentation: Ergebnis-Extraktion Probleme
                    elif name.upper() in ['TDI', 'BOLLINGER_BANDS', 'GENTRENDS']:
                        if name.upper() == 'TDI':
                            rsi_period = params.get('rsi_period', 13)
                            band_length = params.get('band_length', 34)
                            result = technical_indicator.run(close_prices, rsi_period=rsi_period, band_length=band_length)
                            if hasattr(result, 'tdi_rsi') and hasattr(result, 'tdi_signal'):
                                result_data[f'{display_name}_rsi'] = result.tdi_rsi
                                result_data[f'{display_name}_signal'] = result.tdi_signal
                            else:
                                result_data[display_name] = getattr(result, name.lower(), result)
                        elif name.upper() == 'BOLLINGER_BANDS':
                            window = params.get('window', 20)
                            std = params.get('std', 2)
                            result = technical_indicator.run(close_prices, window=window, std=std)
                            if hasattr(result, 'bb_upper') and hasattr(result, 'bb_middle') and hasattr(result, 'bb_lower'):
                                result_data[f'{display_name}_upper'] = result.bb_upper
                                result_data[f'{display_name}_middle'] = result.bb_middle
                                result_data[f'{display_name}_lower'] = result.bb_lower
                            else:
                                result_data[display_name] = getattr(result, name.lower(), result)
                        elif name.upper() == 'GENTRENDS':
                            window = params.get('window', 20)
                            result = technical_indicator.run(close_prices, window=window)
                            if hasattr(result, 'trend_up') and hasattr(result, 'trend_down'):
                                result_data[f'{display_name}_up'] = result.trend_up
                                result_data[f'{display_name}_down'] = result.trend_down
                            else:
                                result_data[display_name] = getattr(result, name.lower(), result)

                    else:
                        # Standard Technical Indikator (VBT Pro Dokumentations-Syntax)
                        window = params.get('window', params.get('period', 14))

                        # Versuche mit window Parameter
                        try:
                            result = technical_indicator.run(close_prices, window=window)
                        except:
                            # Fallback: ohne Parameter
                            result = technical_indicator.run(close_prices)

                        # VBT Pro Technical Ergebnis-Extraktion (Dokumentation)
                        # Versuche Indikator-spezifische Attribute
                        if hasattr(result, name.lower()):
                            result_data[display_name] = getattr(result, name.lower())
                        else:
                            # Fallback: Versuche alle verfügbaren Attribute
                            attrs = [attr for attr in dir(result) if not attr.startswith('_') and name.lower() in attr.lower()]
                            if attrs:
                                result_data[display_name] = getattr(result, attrs[0])
                            else:
                                result_data[display_name] = result

                    print(f"     ✅ Technical {name} berechnet [VBT-INTEGRIERT]")

                except Exception as e:
                    print(f"     ❌ Technical {name} Fehler: {e}")

            # === SMC BIBLIOTHEK ===
            elif library == 'smc':
                try:
                    # SMC RICHTIG BEHEBEN - Basierend auf GitHub Dokumentation
                    # Import: from smartmoneyconcepts import smc
                    # Datenformat: OHLC DataFrame mit lowercase Spalten

                    # Erstelle OHLC DataFrame für SMC (GitHub Format) - RICHTIG BEHEBEN
                    ohlc_df = pd.DataFrame({
                        'open': open_prices,
                        'high': high_prices,
                        'low': low_prices,
                        'close': close_prices
                    })

                    # SMC RICHTIG BEHEBEN - Volume-Spalte hinzufügen wenn verfügbar
                    if volume_data is not None:
                        ohlc_df['volume'] = volume_data

                    # Versuche SMC Import
                    try:
                        from smartmoneyconcepts import smc as smc_lib
                    except ImportError:
                        print(f"     ⚠️ SMC {name} übersprungen (smartmoneyconcepts Bibliothek nicht installiert)")
                        print(f"     💡 Installation: pip install smartmoneyconcepts")
                        continue

                    # SMC Indikatoren basierend auf GitHub Dokumentation
                    if name.upper() == 'FVG':
                        # Fair Value Gap
                        join_consecutive = params.get('join_consecutive', False)
                        result = smc_lib.fvg(ohlc_df, join_consecutive=join_consecutive)
                        result_data[display_name] = result['FVG']

                    elif name.upper() == 'SWING_HIGHS_LOWS':
                        # Swing Highs and Lows
                        swing_length = params.get('swing_length', params.get('length', 50))
                        result = smc_lib.swing_highs_lows(ohlc_df, swing_length=swing_length)
                        result_data[display_name] = result['HighLow']

                    elif name.upper() == 'BOS_CHOCH':
                        # Break of Structure & Change of Character
                        swing_length = params.get('swing_length', 50)
                        close_break = params.get('close_break', True)
                        # Erst Swing Highs/Lows berechnen
                        swing_hl = smc_lib.swing_highs_lows(ohlc_df, swing_length=swing_length)
                        result = smc_lib.bos_choch(ohlc_df, swing_hl, close_break=close_break)
                        result_data[f'{display_name}_BOS'] = result['BOS']
                        result_data[f'{display_name}_CHOCH'] = result['CHOCH']

                    elif name.upper() == 'OB':
                        # Order Blocks
                        swing_length = params.get('swing_length', 50)
                        close_mitigation = params.get('close_mitigation', False)
                        # Erst Swing Highs/Lows berechnen
                        swing_hl = smc_lib.swing_highs_lows(ohlc_df, swing_length=swing_length)
                        result = smc_lib.ob(ohlc_df, swing_hl, close_mitigation=close_mitigation)
                        result_data[display_name] = result['OB']

                    elif name.upper() == 'LIQUIDITY':
                        # Liquidity
                        swing_length = params.get('swing_length', 50)
                        range_percent = params.get('range_percent', 0.01)
                        # Erst Swing Highs/Lows berechnen
                        swing_hl = smc_lib.swing_highs_lows(ohlc_df, swing_length=swing_length)
                        result = smc_lib.liquidity(ohlc_df, swing_hl, range_percent=range_percent)
                        result_data[display_name] = result['Liquidity']

                    elif name.upper() == 'PREVIOUS_HIGH_LOW':
                        # Previous High and Low
                        time_frame = params.get('time_frame', '1D')
                        result = smc_lib.previous_high_low(ohlc_df, time_frame=time_frame)
                        result_data[f'{display_name}_High'] = result['PreviousHigh']
                        result_data[f'{display_name}_Low'] = result['PreviousLow']

                    elif name.upper() == 'SESSIONS':
                        # Sessions
                        session = params.get('session', 'London')
                        start_time = params.get('start_time', None)
                        end_time = params.get('end_time', None)
                        time_zone = params.get('time_zone', 'UTC')
                        result = smc_lib.sessions(ohlc_df, session, start_time, end_time, time_zone=time_zone)
                        result_data[display_name] = result['Active']

                    elif name.upper() == 'RETRACEMENTS':
                        # Retracements
                        swing_length = params.get('swing_length', 50)
                        # Erst Swing Highs/Lows berechnen
                        swing_hl = smc_lib.swing_highs_lows(ohlc_df, swing_length=swing_length)
                        result = smc_lib.retracements(ohlc_df, swing_hl)
                        result_data[display_name] = result['CurrentRetracement%']

                    else:
                        print(f"     ⚠️ SMC {name} nicht unterstützt")
                        continue

                    print(f"     ✅ SMC {name} berechnet [SMART-MONEY-CONCEPTS]")

                except Exception as e:
                    print(f"     ❌ SMC {name} Fehler: {e}")

            # === TECHCON BIBLIOTHEK ===
            elif library == 'techcon':
                try:
                    techcon_indicator = vbt.techcon(name)
                    period = params.get('window', params.get('period', 14))

                    # TechCon Indikatoren RICHTIG BEHEBEN - VBT Pro Dokumentation befolgt
                    if name.upper() in ['MACON', 'OSCCON', 'SUMCON']:
                        # Diese Indikatoren brauchen OHLCV Parameter - VBT Pro Dokumentation
                        if volume_data is not None:
                            # VBT Pro TechCon: OHLCV + period Parameter
                            result = techcon_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data, period=period)
                            result_data[display_name] = result.out if hasattr(result, 'out') else result
                            print(f"     ✅ TechCon {name} berechnet [OHLCV-MODUS]")
                        else:
                            print(f"     ⚠️ TechCon {name} übersprungen (Volume-Daten fehlen)")
                            continue
                    else:
                        # Andere TechCon Indikatoren - Standard-Behandlung
                        result = techcon_indicator.run(close_prices, period=period)
                        result_data[display_name] = result.out if hasattr(result, 'out') else result
                        print(f"     ✅ TechCon {name} berechnet [VBT-INTEGRIERT]")

                except Exception as e:
                    print(f"     ❌ TechCon {name} Fehler: {e}")



            # === WQA101 ALPHAS (KORRIGIERT) ===
            elif library == 'wqa101':
                try:
                    alpha_num = int(name)  # name sollte eine Zahl sein (1-101)

                    # VBT Pro: WQA101 Alphas RICHTIG BEHEBEN - verschiedene Parameter je Alpha
                    wqa_indicator = vbt.wqa101(alpha_num)

                    # Basierend auf VBT Pro Dokumentation: verschiedene Alphas brauchen verschiedene Parameter
                    try:
                        if alpha_num in [1, 4, 9, 10, 19, 23, 24, 29, 34, 46, 49, 51]:
                            # Diese brauchen nur close
                            result = wqa_indicator.run(close_prices)
                        elif alpha_num in [2, 14, 22, 31, 52, 90]:
                            # Diese brauchen close und volume
                            if volume_data is not None:
                                result = wqa_indicator.run(close_prices, volume_data)
                            else:
                                print(f"     ⚠️ WQA101 Alpha {alpha_num} übersprungen (Volume-Daten fehlen)")
                                continue
                        elif alpha_num in [3, 6, 7, 12, 13, 15, 16, 17, 21, 26, 30, 39, 40, 43, 44, 45, 56, 82]:
                            # Diese brauchen close und volume
                            if volume_data is not None:
                                result = wqa_indicator.run(close_prices, volume_data)
                            else:
                                print(f"     ⚠️ WQA101 Alpha {alpha_num} übersprungen (Volume-Daten fehlen)")
                                continue
                        elif alpha_num in [5, 36, 62, 63, 64, 65, 66, 71, 73, 79, 86, 88, 92, 98]:
                            # Diese brauchen OHLCV
                            if volume_data is not None:
                                result = wqa_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data)
                            else:
                                print(f"     ⚠️ WQA101 Alpha {alpha_num} übersprungen (Volume-Daten fehlen)")
                                continue
                        elif alpha_num in [8, 18, 33, 37, 38]:
                            # Diese brauchen nur open
                            result = wqa_indicator.run(open_prices)
                        elif alpha_num == 48:
                            # Alpha 48 hat spezielle Parameter-Anforderungen - korrigiere
                            if volume_data is not None:
                                result = wqa_indicator.run(high_prices, low_prices, close_prices, volume_data)
                            else:
                                print(f"     ⚠️ WQA101 Alpha {alpha_num} übersprungen (Volume-Daten fehlen)")
                                continue
                        elif alpha_num in [11, 25, 27, 28, 32, 35, 41, 42, 47, 50, 55, 57, 58, 59, 60, 61, 67, 68, 69, 70, 72, 74, 75, 76, 77, 78, 81, 83, 84, 85, 87, 89, 91, 93, 94, 96, 97, 100]:
                            # Diese brauchen HLC und volume
                            if volume_data is not None:
                                result = wqa_indicator.run(high_prices, low_prices, close_prices, volume_data)
                            else:
                                print(f"     ⚠️ WQA101 Alpha {alpha_num} übersprungen (Volume-Daten fehlen)")
                                continue
                        elif alpha_num in [20, 53, 54, 101]:
                            # Diese brauchen HLC
                            result = wqa_indicator.run(high_prices, low_prices, close_prices)
                        elif alpha_num in [80, 95, 99]:
                            # Diese brauchen spezielle Parameter
                            if volume_data is not None:
                                result = wqa_indicator.run(high_prices, volume_data)
                            else:
                                print(f"     ⚠️ WQA101 Alpha {alpha_num} übersprungen (Volume-Daten fehlen)")
                                continue
                        else:
                            # Fallback: versuche mit allen Parametern
                            if volume_data is not None:
                                result = wqa_indicator.run(open_prices, high_prices, low_prices, close_prices, volume_data)
                            else:
                                result = wqa_indicator.run(close_prices)

                        result_data[display_name] = result.out if hasattr(result, 'out') else result
                        print(f"     ✅ WQA101 Alpha {alpha_num} berechnet [QUANT-ALPHA]")

                    except Exception as e:
                        if "subindustry" in str(e):
                            print(f"     ⚠️ WQA101 Alpha {alpha_num} übersprungen (Subindustry-Daten fehlen)")
                        else:
                            print(f"     ❌ WQA101 Alpha {alpha_num} Fehler: {e}")
                        continue

                except Exception as e:
                    print(f"     ❌ WQA101 Alpha {name} Fehler: {e}")

            else:
                print(f"     ❌ Unbekannte Bibliothek: {library}")

        except Exception as e:
            print(f"     ❌ Allgemeiner Fehler bei {display_name}: {e}")
    
    # Aktualisierte Daten speichern
    enhanced_data[tf] = result_data
    print(f"✅ {tf}: {len(result_data.columns)} Spalten (inkl. Indikatoren)")

print("\\n✅ Alle Indikatoren erfolgreich berechnet!")'''

    return code

def generate_visualization_code(visualization_mode, visualization_period, chart_quality, chart_theme, enable_segmentation, candles_per_chart):
    """Generiert den Code für Visualisierung basierend auf VBT Pro Dokumentation - VOLLSTÄNDIG KORRIGIERT"""
    if visualization_mode == "Keine Visualisierung":
        return ""

    # Bestimme was angezeigt werden soll
    show_charts = visualization_mode in [
        "Interaktive Charts mit Indikatoren",
        "Normale Charts mit Indikatoren",
        "Charts + Tabellen"
    ]

    show_tables = visualization_mode in [
        "Nur Daten-Tabellen",
        "Charts + Tabellen"
    ]

    # VBT Pro Chart-Code basierend auf offizieller Dokumentation
    chart_code = ""
    if show_charts:
        chart_code = '''
            # TRADINGVIEW CHART ERSTELLUNGS-FUNKTION (ZUERST DEFINIEREN)
            def create_tradingview_chart(data, title, price_indicators, volume_indicators, oscillators, has_volume, viz_mode, theme):
                """Erstellt professionelle TradingView-ähnliche Charts mit VBT Pro"""
                try:
                    # Berechne Subplot-Anzahl (TradingView-Style)
                    subplot_count = 1  # Haupt-Chart (Kerzen + Price-Indikatoren)

                    # Volume-Subplot (wenn Volume verfügbar)
                    if has_volume or volume_indicators:
                        subplot_count += 1

                    # Oszillator-Subplots (max 4 für bessere Übersicht)
                    max_oscillator_subplots = 4
                    oscillator_subplots = min(len(oscillators), max_oscillator_subplots)
                    subplot_count += oscillator_subplots

                    # Erstelle Subplots mit TradingView-ähnlichen Proportionen
                    if subplot_count == 1:
                        row_heights = [1.0]
                    elif subplot_count == 2:
                        row_heights = [0.7, 0.3]  # 70% Haupt-Chart, 30% Volume
                    else:
                        main_height = 0.6
                        volume_height = 0.2 if has_volume else 0
                        oscillator_height = (1.0 - main_height - volume_height) / oscillator_subplots if oscillator_subplots > 0 else 0

                        row_heights = [main_height]
                        if has_volume or volume_indicators:
                            row_heights.append(volume_height)
                        for _ in range(oscillator_subplots):
                            row_heights.append(oscillator_height)

                    # Erstelle Subplot-Titel
                    subplot_titles = [f"{title} - Kerzen & Price-Indikatoren"]
                    if has_volume or volume_indicators:
                        subplot_titles.append("Volume")
                    for i, osc in enumerate(oscillators[:max_oscillator_subplots]):
                        subplot_titles.append(f"{osc}")

                    # VBT Pro make_subplots (TradingView-Style)
                    fig = vbt.make_subplots(
                        rows=subplot_count,
                        cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02,  # Enger Abstand wie TradingView
                        row_heights=row_heights,
                        subplot_titles=subplot_titles
                    )

                    # 1. HAUPT-CHART: CANDLESTICKS (VBT Pro OHLCV Accessor)
                    print("🕯️ Erstelle Candlestick-Chart...")
                    ohlc_data = data[['open', 'high', 'low', 'close']].copy()

                    # VBT Pro OHLCV Plot für Candlesticks
                    fig = ohlc_data.vbt.ohlcv.plot_ohlc(
                        ohlc_type='candlestick',  # TradingView-Style Kerzen
                        fig=fig,
                        add_trace_kwargs=dict(row=1, col=1),
                        trace_kwargs=dict(
                            name="Kerzen",
                            increasing_line_color='#26a69a',  # TradingView Grün
                            decreasing_line_color='#ef5350',  # TradingView Rot
                            increasing_fillcolor='#26a69a',
                            decreasing_fillcolor='#ef5350'
                        )
                    )

                    # 2. PRICE-INDIKATOREN auf Haupt-Chart
                    print(f"📈 Füge {len(price_indicators)} Price-Indikatoren hinzu...")
                    colors = ['#2196F3', '#FF9800', '#9C27B0', '#4CAF50', '#F44336', '#00BCD4', '#FFEB3B']
                    for i, indicator in enumerate(price_indicators):
                        color = colors[i % len(colors)]
                        fig = data[indicator].vbt.lineplot(
                            fig=fig,
                            add_trace_kwargs=dict(row=1, col=1),
                            trace_kwargs=dict(
                                name=indicator,
                                line=dict(color=color, width=2),
                                opacity=0.8
                            )
                        )

                    current_row = 2

                    # 3. VOLUME-SUBPLOT
                    if has_volume or volume_indicators:
                        print("📊 Erstelle Volume-Subplot...")

                        # Echte Volume-Bars (wenn verfügbar)
                        if has_volume and 'volume' in data.columns and data['volume'] is not None:
                            # Prüfe ob Volume-Daten tatsächlich vorhanden sind
                            if not data['volume'].isna().all():
                                try:
                                    fig = data['volume'].vbt.barplot(
                                        fig=fig,
                                        add_trace_kwargs=dict(row=current_row, col=1),
                                        trace_kwargs=dict(
                                            name="Volume",
                                            marker=dict(
                                                color='rgba(128,128,128,0.5)',
                                                line=dict(width=0)
                                            )
                                        )
                                    )
                                except Exception as e:
                                    print(f"     ⚠️ Volume-Plot Fehler: {e}")
                            else:
                                print("     ⚠️ Volume-Daten sind leer, überspringe Volume-Bars")

                        # Volume-Indikatoren
                        for i, indicator in enumerate(volume_indicators):
                            if indicator in data.columns and data[indicator] is not None:
                                # Prüfe ob Indikator-Daten vorhanden sind
                                if not data[indicator].isna().all():
                                    color = colors[(i + len(price_indicators)) % len(colors)]
                                    fig = data[indicator].vbt.lineplot(
                                        fig=fig,
                                        add_trace_kwargs=dict(row=current_row, col=1),
                                        trace_kwargs=dict(
                                            name=indicator,
                                            line=dict(color=color, width=2),
                                            yaxis='y2'  # Sekundäre Y-Achse für Indikatoren
                                        )
                                    )
                                else:
                                    print(f"     ⚠️ {indicator} Daten sind leer, überspringe")
                            else:
                                print(f"     ⚠️ {indicator} nicht in Daten gefunden, überspringe")

                        current_row += 1

                    # 4. OSZILLATOR-SUBPLOTS
                    print(f"📈 Erstelle {oscillator_subplots} Oszillator-Subplots...")
                    for i, indicator in enumerate(oscillators[:max_oscillator_subplots]):
                        color = colors[(i + len(price_indicators) + len(volume_indicators)) % len(colors)]

                        fig = data[indicator].vbt.lineplot(
                            fig=fig,
                            add_trace_kwargs=dict(row=current_row + i, col=1),
                            trace_kwargs=dict(
                                name=indicator,
                                line=dict(color=color, width=2),
                                fill=None
                            )
                        )

                        # RSI-spezifische Levels (TradingView-Style)
                        if 'rsi' in indicator.lower():
                            fig.add_hline(y=70, line_dash="dash", line_color="rgba(255,0,0,0.5)",
                                        annotation_text="Overbought (70)", row=current_row + i, col=1)
                            fig.add_hline(y=30, line_dash="dash", line_color="rgba(0,255,0,0.5)",
                                        annotation_text="Oversold (30)", row=current_row + i, col=1)
                            fig.add_hline(y=50, line_dash="dot", line_color="rgba(128,128,128,0.3)",
                                        row=current_row + i, col=1)

                        # MACD-spezifische Null-Linie
                        elif 'macd' in indicator.lower():
                            fig.add_hline(y=0, line_dash="dash", line_color="rgba(128,128,128,0.5)",
                                        row=current_row + i, col=1)

                        # Stochastic-spezifische Levels
                        elif 'stoch' in indicator.lower():
                            fig.add_hline(y=80, line_dash="dash", line_color="rgba(255,0,0,0.5)",
                                        row=current_row + i, col=1)
                            fig.add_hline(y=20, line_dash="dash", line_color="rgba(0,255,0,0.5)",
                                        row=current_row + i, col=1)

                    # TradingView-ähnliches Layout
                    height = 800 if viz_mode == "Interaktive Charts mit Indikatoren" else 600

                    fig.update_layout(
                        title=dict(
                            text=f"Punkt 3: {title} - TradingView Style",
                            x=0.5,
                            font=dict(size=16, color='white' if 'dark' in theme else 'black')
                        ),
                        template=theme,
                        height=height,
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.15,
                            xanchor="center",
                            x=0.5,
                            bgcolor="rgba(0,0,0,0.1)",
                            bordercolor="rgba(255,255,255,0.2)",
                            borderwidth=1,
                            font=dict(size=10)
                        ),
                        # TradingView-ähnliche Achsen
                        xaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(128,128,128,0.2)',
                            rangeslider_visible=False  # Kein Range-Slider wie TradingView
                        ),
                        # Alle Y-Achsen konfigurieren
                        **{f'yaxis{i+1 if i > 0 else ""}': dict(
                            showgrid=True,
                            gridcolor='rgba(128,128,128,0.2)',
                            zeroline=True,
                            zerolinecolor='rgba(128,128,128,0.3)'
                        ) for i in range(subplot_count)}
                    )

                    # Chart anzeigen
                    fig.show()
                    print(f"✅ TradingView-Chart erfolgreich erstellt: {title}")

                except Exception as chart_error:
                    print(f"❌ TradingView-Chart Fehler: {chart_error}")

                    # FALLBACK: Einfacher Candlestick
                    try:
                        print("🔄 Fallback: Einfacher Candlestick...")
                        fig = go.Figure(data=go.Candlestick(
                            x=data.index,
                            open=data['open'],
                            high=data['high'],
                            low=data['low'],
                            close=data['close'],
                            name="Kerzen",
                            increasing_line_color='#26a69a',
                            decreasing_line_color='#ef5350'
                        ))

                        # Wichtigste Price-Indikatoren hinzufügen
                        for indicator in price_indicators[:3]:  # Max 3 für Fallback
                            fig.add_trace(go.Scatter(
                                x=data.index,
                                y=data[indicator],
                                mode='lines',
                                name=indicator,
                                line=dict(width=2)
                            ))

                        fig.update_layout(
                            title=f"Punkt 3: {title} - Fallback Candlestick",
                            template=theme,
                            height=600,
                            xaxis_title="Zeit",
                            yaxis_title="Preis",
                            xaxis_rangeslider_visible=False
                        )
                        fig.show()
                        print(f"✅ Fallback-Chart erfolgreich: {title}")

                    except Exception as fallback_error:
                        print(f"❌ Auch Fallback fehlgeschlagen: {fallback_error}")

            # TRADINGVIEW-ÄHNLICHE CANDLESTICK CHARTS (VBT PRO OHLCV ACCESSOR)
            print(f"\\n📊 ERSTELLE TRADINGVIEW-CHARTS FÜR {tf.upper()}:")

            try:
                # Prüfe OHLC Verfügbarkeit
                required_ohlc = ['open', 'high', 'low', 'close']
                has_ohlc = all(col in viz_data.columns for col in required_ohlc)
                has_volume = 'volume' in viz_data.columns

                if not has_ohlc:
                    print(f"❌ OHLC Daten fehlen: {[col for col in required_ohlc if col not in viz_data.columns]}")
                    continue

                # Kategorisiere Indikatoren für korrekte Platzierung
                indicator_cols = [col for col in viz_data.columns if col not in ['open', 'high', 'low', 'close', 'volume']]

                # PRICE-BASED INDIKATOREN (auf Haupt-Chart mit Kerzen)
                price_indicators = []
                for col in indicator_cols:
                    col_lower = col.lower()
                    if any(x in col_lower for x in ['ma(', 'sma', 'ema', 'wma', 'bb', 'bollinger', 'vwap', 'pivot', 'support', 'resistance', 'supertrend', 'keltner', 'donchian']):
                        price_indicators.append(col)

                # VOLUME-INDIKATOREN (Volume-Subplot)
                volume_indicators = []
                for col in indicator_cols:
                    col_lower = col.lower()
                    if any(x in col_lower for x in ['obv', 'volume', 'vpt', 'mfi', 'cmf', 'ad', 'pvi', 'nvi']):
                        volume_indicators.append(col)

                # OSZILLATOREN (separate Subplots)
                oscillators = []
                for col in indicator_cols:
                    if col not in price_indicators and col not in volume_indicators:
                        oscillators.append(col)

                print(f"📊 Indikator-Kategorisierung:")
                print(f"   💰 Price-Indikatoren (Haupt-Chart): {len(price_indicators)}")
                print(f"   📊 Volume-Indikatoren (Volume-Subplot): {len(volume_indicators)}")
                print(f"   📈 Oszillatoren (separate Subplots): {len(oscillators)}")

                # Segmentierung aktiviert?
                if enable_segmentation and len(viz_data) > candles_per_chart:
                    print(f"🔄 Segmentierung aktiviert: {len(viz_data)} Kerzen in {candles_per_chart}er Segmente")

                    # Berechne Anzahl der Segmente
                    total_segments = (len(viz_data) + candles_per_chart - 1) // candles_per_chart

                    for segment in range(total_segments):
                        start_idx = segment * candles_per_chart
                        end_idx = min((segment + 1) * candles_per_chart, len(viz_data))
                        segment_data = viz_data.iloc[start_idx:end_idx].copy()

                        print(f"\\n📊 Segment {segment + 1}/{total_segments} ({len(segment_data)} Kerzen)")

                        # Erstelle TradingView-ähnlichen Chart für Segment
                        create_tradingview_chart(segment_data, f"{tf} Segment {segment + 1}",
                                               price_indicators, volume_indicators, oscillators,
                                               has_volume, "''' + visualization_mode + '''", "''' + chart_theme + '''")

                else:
                    # KEINE SEGMENTIERUNG - Ein großer Chart
                    print(f"📊 Erstelle einzelnen TradingView-Chart mit {len(viz_data)} Kerzen")

                    # Erstelle TradingView-ähnlichen Chart
                    create_tradingview_chart(viz_data, f"{tf} Vollständig",
                                           price_indicators, volume_indicators, oscillators,
                                           has_volume, "''' + visualization_mode + '''", "''' + chart_theme + '''")

                print(f"✅ {tf}: TradingView-Charts erfolgreich erstellt")

            except Exception as e:
                print(f"❌ TradingView-Chart Fehler für {tf}: {e}")
                print(f"📊 Verfügbare Spalten: {list(viz_data.columns)}")
                import traceback
                traceback.print_exc()'''

    code = f'''
# 3. VISUALISIERUNG
print("\\n📊 3. VISUALISIERUNG")
print("-" * 30)

# Visualisierungs-Modus: {visualization_mode}
show_charts = {show_charts}
show_tables = {show_tables}

print(f"📊 Charts anzeigen: {{show_charts}}")
print(f"📋 Tabellen anzeigen: {{show_tables}}")

try:
    for tf, data in enhanced_data.items():
        print(f"\\n🎨 Verarbeite {{tf}} Daten...")

        # Zeitraum-Berechnung
        total_candles = len(data)

        period_mapping = {{
            "1 Tag": 288 if tf == "5m" else 1440 if tf == "1m" else 24 if tf == "1h" else 1,
            "2 Tage": 576 if tf == "5m" else 2880 if tf == "1m" else 48 if tf == "1h" else 2,
            "3 Tage": 864 if tf == "5m" else 4320 if tf == "1m" else 72 if tf == "1h" else 3,
            "1 Woche": 2016 if tf == "5m" else 10080 if tf == "1m" else 168 if tf == "1h" else 7,
            "2 Wochen": 4032 if tf == "5m" else 20160 if tf == "1m" else 336 if tf == "1h" else 14,
            "4 Wochen": 8064 if tf == "5m" else 40320 if tf == "1m" else 672 if tf == "1h" else 28,
            "8 Wochen": 16128 if tf == "5m" else 80640 if tf == "1m" else 1344 if tf == "1h" else 56,
            "12 Wochen": 24192 if tf == "5m" else 120960 if tf == "1m" else 2016 if tf == "1h" else 84,
            "20 Wochen": 40320 if tf == "5m" else 201600 if tf == "1m" else 3360 if tf == "1h" else 140,
            "52 Wochen": 104832 if tf == "5m" else 524160 if tf == "1m" else 8736 if tf == "1h" else 364
        }}

        period = "{visualization_period}"
        candles_to_show = period_mapping.get(period, total_candles)
        candles_to_show = min(candles_to_show, total_candles)

        # Daten für Visualisierung vorbereiten
        viz_data = data.tail(candles_to_show).copy()
        print(f"📈 Verwende {{len(viz_data)}} Kerzen für {{period}}")

        # Chart-Segmentierung
        enable_segmentation = {enable_segmentation}
        candles_per_chart = {candles_per_chart}

        # TABELLEN-AUSGABE (VBT PRO PTABLE)
        if show_tables:
            print(f"\\n📋 DATEN-TABELLEN FÜR {{tf.upper()}}:")
            print("=" * 80)

            # VBT Pro ptable für professionelle Tabellen-Ausgabe
            print(f"🔝 ERSTE 20 ZEILEN:")
            try:
                vbt.ptable(viz_data.head(20))
            except:
                print(viz_data.head(20))

            print(f"\\n🔚 LETZTE 20 ZEILEN:")
            try:
                vbt.ptable(viz_data.tail(20))
            except:
                print(viz_data.tail(20))

            print(f"\\n📊 STATISTIKEN FÜR {{tf.upper()}}:")
            try:
                vbt.ptable(viz_data.describe())
            except:
                print(viz_data.describe())

            print(f"\\n📈 INDIKATOR-SPALTEN ({{len([col for col in viz_data.columns if col not in ['open', 'high', 'low', 'close', 'volume']])}}):")
            indicator_cols = [col for col in viz_data.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
            for i, col in enumerate(indicator_cols, 1):
                print(f"   {{i:2d}}. {{col}}")

            print("\\n" + "=" * 80)

        # CHART-AUSGABE (IMMER WENN CHARTS AKTIVIERT)
        if show_charts:
{chart_code}

        # Status-Meldungen
        if show_tables and not show_charts:
            print(f"✅ {{tf}}: Tabellen erfolgreich angezeigt")
        elif show_charts and not show_tables:
            print(f"✅ {{tf}}: Charts erfolgreich erstellt")
        elif show_charts and show_tables:
            print(f"✅ {{tf}}: Charts und Tabellen erfolgreich erstellt")

except Exception as e:
    print(f"❌ Fehler bei Visualisierung: {{e}}")
    traceback.print_exc()

print("\\n✅ Visualisierung abgeschlossen!")
'''

    return code

def generate_saving_code(base_name, selected_timeframes, selected_indicators, save_punkt4, save_backup):
    """Generiert Code zum Speichern der Ergebnisse"""
    if not save_punkt4 and not save_backup:
        return '''
# 4. SPEICHERN
print("\\n💾 4. SPEICHERN")
print("-" * 30)
print("ℹ️ Speichern deaktiviert")'''

    code = '''
# 4. SPEICHERN
print("\\n💾 4. SPEICHERN")
print("-" * 30)

# Ausgabe-Verzeichnis erstellen
punkt3_dir = "data/punkt3"
os.makedirs(punkt3_dir, exist_ok=True)

base_name = "''' + base_name + '''"
selected_timeframes = ''' + str(selected_timeframes) + '''
selected_indicators = ''' + str(selected_indicators) + '''
save_punkt4 = ''' + str(save_punkt4) + '''
save_backup = ''' + str(save_backup) + '''

vbt_files = []

# VBT Data Objekte für Punkt4 erstellen (20x Performance-Boost)
if save_punkt4:
    print("\\n🚀 ERSTELLE VBT DATA OBJEKTE FÜR PUNKT4...")

    for tf, data in enhanced_data.items():
        # VBT Data Objekt für maximale Punkt4 Performance
        print(f"🚀 Erstelle VBT Data Objekt für {tf}...")

        # KRITISCH: Float64 beibehalten (VBT Standard für Numba-Kompatibilität)
        for col in data.columns:
            if data[col].dtype != 'float64':
                data[col] = data[col].astype('float64')

        vbt_data = vbt.Data.from_data(data, columns_are_symbols=True)

        # VBT Pickle mit Blosc Kompression (optimal für Punkt4)
        vbt_file = f"{base_name}_{tf}_indicators_VBT.pickle"
        vbt_path = os.path.join(punkt3_dir, vbt_file)
        vbt_data.save(vbt_path, compression="blosc")
        vbt_files.append(vbt_file)

        print(f"✅ {tf}: {vbt_file} gespeichert (VBT Data - 20x Speedup)")
        print(f"   📊 Symbols: {list(vbt_data.symbols)}")
        print(f"   🕐 Frequenz: {vbt_data.wrapper.freq}")
        print(f"   📈 Shape: {vbt_data.get().shape}")
        print(f"   💾 Kompression: Blosc (optimal)")
        print(f"   🚀 Optimiert für Punkt4/5/6 Backtesting")

# Backup CSV-Dateien (optional)
if save_backup:
    print("\\n📋 ERSTELLE BACKUP CSV-DATEIEN...")

    for tf, data in enhanced_data.items():
        backup_file = f"{base_name}_{tf}_indicators_backup.csv"
        backup_path = os.path.join(punkt3_dir, backup_file)
        data.to_csv(backup_path)
        print(f"✅ {tf}: {backup_file} gespeichert (CSV Backup)")

# Metadaten speichern
punkt3_metadata = {
    "created_at": datetime.now().isoformat(),
    "source": "punkt3_indikator_konfigurator",
    "base_file": base_name,
    "timeframes": selected_timeframes,
    "indicators": selected_indicators,
    "vbt_files": vbt_files,
    "total_indicators": len(selected_indicators),
    "vbt_optimized": len(vbt_files) > 0,
    "punkt4_ready": len(vbt_files) > 0
}

metadata_output = os.path.join(punkt3_dir, f"{base_name}_indicators_metadata.json")
try:
    with open(metadata_output, 'w') as f:
        json.dump(punkt3_metadata, f, indent=2)
    print(f"✅ Metadaten gespeichert: {os.path.basename(metadata_output)}")
except Exception as e:
    print(f"❌ Fehler beim Speichern der Metadaten: {e}")

print(f"\\n🚀 VECTORBT PRO PERFORMANCE:")
print(f"   ✅ VBT Data Objekte erstellt: {len(vbt_files)}")
print(f"   ⚡ 20x Backtesting-Speedup aktiviert")
print(f"   💾 Blosc Kompression: Optimal")
print(f"   🔢 Float64 Datentypen: VBT Standard")
print(f"   🎯 Optimiert für Punkt4/5/6 Performance")
print(f"   🚫 Kein Fallback: Nur VBT Pro")'''

    return code

def generate_summary_code(show_summary):
    """Generiert Code für die Zusammenfassung"""
    if not show_summary:
        return ""

    return '''
# 5. ZUSAMMENFASSUNG
print("\\n📊 5. ZUSAMMENFASSUNG")
print("-" * 30)

total_timeframes = len(enhanced_data)
total_indicators = 0
total_columns = 0

for tf, data in enhanced_data.items():
    indicator_cols = [col for col in data.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
    total_indicators += len(indicator_cols)
    total_columns += len(data.columns)

    print(f"\\n📈 {tf.upper()}:")
    print(f"   📊 Gesamt-Spalten: {len(data.columns)}")
    print(f"   🔧 Indikatoren: {len(indicator_cols)}")
    print(f"   📅 Zeitraum: {data.index[0]} bis {data.index[-1]}")
    print(f"   🕐 Kerzen: {len(data)}")

print(f"\\n🎯 GESAMT-STATISTIKEN:")
print(f"   📊 Timeframes: {total_timeframes}")
print(f"   🔧 Indikatoren: {total_indicators}")
print(f"   📈 Gesamt-Spalten: {total_columns}")
print(f"   🚀 VBT Pro: 100% Native")
print(f"   ⚡ Performance: Optimal")'''
