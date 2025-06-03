#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neue, korrekte Visualisierungsfunktion für Punkt 3
"""

def generate_visualization_code_fixed(visualization_mode, visualization_period, chart_quality, chart_theme, enable_segmentation, candles_per_chart):
    """Generiert den Code für Visualisierung basierend auf dem gewählten Modus - KORREKTE VERSION"""
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

    code = '''
# 3. VISUALISIERUNG
print("\\n📊 3. VISUALISIERUNG")
print("-" * 30)

# Visualisierungs-Modus: ''' + visualization_mode + '''
show_charts = ''' + str(show_charts) + '''
show_tables = ''' + str(show_tables) + '''

print(f"📊 Charts anzeigen: {show_charts}")
print(f"📋 Tabellen anzeigen: {show_tables}")

try:
    for tf, data in enhanced_data.items():
        print(f"\\n🎨 Verarbeite {tf} Daten...")

        # Zeitraum-Berechnung
        total_candles = len(data)
        ''' + f'''
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

        period = "''' + visualization_period + '''"
        candles_to_show = period_mapping.get(period, total_candles)
        candles_to_show = min(candles_to_show, total_candles)

        # Daten für Visualisierung vorbereiten
        viz_data = data.tail(candles_to_show).copy()
        print(f"📈 Verwende {len(viz_data)} Kerzen für {period}")

        # Chart-Segmentierung
        enable_segmentation = ''' + str(enable_segmentation) + '''
        candles_per_chart = ''' + str(candles_per_chart) + '''

        # TABELLEN-AUSGABE (VBT PRO PTABLE)
        if show_tables:
            print(f"\\n📋 DATEN-TABELLEN FÜR {tf.upper()}:")
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
            
            print(f"\\n📊 STATISTIKEN FÜR {tf.upper()}:")
            try:
                vbt.ptable(viz_data.describe())
            except:
                print(viz_data.describe())
            
            print(f"\\n📈 INDIKATOR-SPALTEN ({len([col for col in viz_data.columns if col not in ['open', 'high', 'low', 'close', 'volume']])}):")
            indicator_cols = [col for col in viz_data.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
            for i, col in enumerate(indicator_cols, 1):
                print(f"   {i:2d}. {col}")
            
            print("\\n" + "=" * 80)

        # CHART-AUSGABE (NUR WENN GEWÄHLT)
        if show_charts:
            print(f"\\n📊 ERSTELLE CHARTS FÜR {tf.upper()}:")
            
            # PROFESSIONELLE INDIKATOR-KATEGORISIERUNG (VBT PRO STANDARD)
            price_indicators = []  # Gehen auf Haupt-Chart (MA, Bollinger Bands, etc.)
            oscillators = []       # Gehen in separate Subplots (RSI, MACD, ADX, etc.)
            volume_indicators = [] # Gehen in Volume-Subplot (OBV, etc.)

            for col in viz_data.columns:
                if col not in ['open', 'high', 'low', 'close', 'volume']:
                    col_lower = col.lower()

                    # PRICE-BASED INDIKATOREN (auf Haupt-Chart)
                    if any(x in col_lower for x in ['ma(', 'sma', 'ema', 'bb', 'bollinger', 'vwap', 'pivot', 'support', 'resistance']):
                        price_indicators.append(col)

                    # VOLUME-INDIKATOREN (eigener Subplot)
                    elif any(x in col_lower for x in ['obv', 'volume', 'vpt', 'mfi']):
                        volume_indicators.append(col)

                    # OSZILLATOREN (eigene Subplots)
                    else:
                        # Alle anderen Indikatoren sind Oszillatoren: RSI, MACD, ADX, ATR, Stochastic, etc.
                        oscillators.append(col)

            # Berechne Subplot-Anzahl
            subplot_count = 1  # Haupt-Chart

            # IMMER Volume-Subplot anzeigen (VBT PRO STANDARD)
            show_volume = 'volume' in viz_data.columns or volume_indicators
            if show_volume:
                subplot_count += 1

            if oscillators:
                # KRITISCH: Maximal 5 Oszillator-Subplots (VBT PRO LIMIT)
                max_oscillator_subplots = 5
                subplot_count += min(len(oscillators), max_oscillator_subplots)

            # Erstelle Subplots mit korrekter VBT Pro Struktur
            fig = make_subplots(
                rows=subplot_count,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.6] + [0.4/(subplot_count-1)]*(subplot_count-1) if subplot_count > 1 else [1.0],
                subplot_titles=[f"{tf} Price Chart"] +
                              ([f"Volume"] if show_volume else []) +
                              [f"{osc}" for osc in oscillators]
            )

            # 1. HAUPT-CHART: Candlesticks + Price-Indikatoren
            fig.add_trace(go.Candlestick(
                x=viz_data.index,
                open=viz_data['open'],
                high=viz_data['high'],
                low=viz_data['low'],
                close=viz_data['close'],
                name=f"{tf} Kerzen"
            ), row=1, col=1)

            # Price-Indikatoren auf Haupt-Chart
            for indicator in price_indicators:
                fig.add_trace(go.Scatter(
                    x=viz_data.index,
                    y=viz_data[indicator],
                    mode='lines',
                    name=indicator,
                    line=dict(width=1)
                ), row=1, col=1)

            current_row = 2

            # 2. VOLUME-SUBPLOT (VBT PRO STANDARD)
            if show_volume:
                # ECHTE VOLUME-BARS (VBT PRO STANDARD)
                if 'volume' in viz_data.columns:
                    fig.add_trace(go.Bar(
                        x=viz_data.index,
                        y=viz_data['volume'],
                        name='Volume',
                        marker=dict(color='rgba(128,128,128,0.5)'),
                        showlegend=True
                    ), row=current_row, col=1)

                # VOLUME-INDIKATOREN (OBV, etc.)
                for indicator in volume_indicators:
                    fig.add_trace(go.Scatter(
                        x=viz_data.index,
                        y=viz_data[indicator],
                        mode='lines',
                        name=indicator,
                        line=dict(width=2, color='orange'),
                        yaxis='y2'  # Sekundäre Y-Achse für Indikatoren
                    ), row=current_row, col=1)

                current_row += 1

            # 3. OSZILLATOR-SUBPLOTS (OPTIMIERT: Maximal 5 Subplots)
            max_oscillator_subplots = 5
            oscillators_per_subplot = max(1, len(oscillators) // max_oscillator_subplots)

            for i in range(min(len(oscillators), max_oscillator_subplots)):
                start_idx = i * oscillators_per_subplot
                end_idx = min((i + 1) * oscillators_per_subplot, len(oscillators))
                subplot_oscillators = oscillators[start_idx:end_idx]

                for indicator in subplot_oscillators:
                    fig.add_trace(go.Scatter(
                        x=viz_data.index,
                        y=viz_data[indicator],
                        mode='lines',
                        name=indicator,
                        line=dict(width=1)
                    ), row=current_row, col=1)

                    # RSI-spezifische Levels
                    if 'rsi' in indicator.lower():
                        fig.add_hline(y=70, line_dash="dash", line_color="red",
                                    annotation_text="Overbought", row=current_row, col=1)
                        fig.add_hline(y=30, line_dash="dash", line_color="green",
                                    annotation_text="Oversold", row=current_row, col=1)

                current_row += 1

            # Chart-Layout mit optimaler Y-Achsen-Skalierung
            price_min = min(viz_data['low'].min(), viz_data['close'].min())
            price_max = max(viz_data['high'].max(), viz_data['close'].max())
            price_range = price_max - price_min
            y_margin = price_range * 0.1  # 10% Margin

            fig.update_layout(
                title=f"Punkt 3: {tf} Chart ({period})",
                template="''' + chart_theme + '''",
                xaxis_title="Zeit",
                yaxis_title="Preis",
                yaxis=dict(
                    range=[price_min - y_margin, price_max + y_margin],
                    autorange=False
                ),
                height=800,  # Mehr Höhe für bessere Sichtbarkeit
                showlegend=True,
                # PROFESSIONELLE LEGEND-OPTIMIERUNG (VBT PRO STANDARD)
                legend=dict(
                    orientation="h",  # Horizontal statt vertikal
                    yanchor="bottom",
                    y=-0.3,  # Unter dem Chart
                    xanchor="center",
                    x=0.5,
                    bgcolor="rgba(0,0,0,0.5)",  # Transparenter Hintergrund
                    bordercolor="rgba(255,255,255,0.2)",
                    borderwidth=1,
                    font=dict(size=10)  # Kleinere Schrift
                )
            )

            # Chart anzeigen
            fig.show()
            print(f"✅ {tf}: Charts erfolgreich erstellt")
        
        # Status-Meldungen
        if show_tables and not show_charts:
            print(f"✅ {tf}: Tabellen erfolgreich angezeigt")
        elif show_charts and show_tables:
            print(f"✅ {tf}: Charts und Tabellen erfolgreich erstellt")

except Exception as e:
    print(f"❌ Fehler bei Visualisierung: {e}")
    traceback.print_exc()

print("\\n✅ Visualisierung abgeschlossen!")
'''
    
    return code
