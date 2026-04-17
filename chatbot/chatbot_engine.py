import re
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from analysis.mortgage_calc import MortgageCalculator

class ChatbotEngine:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.calc = MortgageCalculator()

    def process_query(self, query: str) -> Tuple[str, Optional[pd.DataFrame]]:
        query = query.lower()
        response = ""
        filtered_df = self.data.copy()
        
        # 1. Detectar filtros de Ciudad
        cities = self.data['city'].unique()
        for city in cities:
            if city in query:
                filtered_df = filtered_df[filtered_df['city'] == city]
                response += f"📍 Filtrando por ciudad: **{city.capitalize()}**. "

        # 2. Detectar Cuartos / Habitaciones
        rooms_match = re.search(r"(\d+)\s*(cuartos|habitaciones|pokoje|rooms)", query)
        if rooms_match:
            rooms = int(rooms_match.group(1))
            filtered_df = filtered_df[filtered_df['rooms'] >= rooms]
            response += f"🛏️ Buscando {rooms}+ cuartos. "

        # 3. Detectar Precio
        price_match = re.search(r"(debajo|menos|bajo|under|below|max)\s*(?:de)?\s*(\d+(?:[.,]\d+)?)\s*(k|m|millon|mil)?", query)
        if price_match:
            val = float(price_match.group(2).replace(",", "."))
            multiplier = price_match.group(3)
            if multiplier in ['k', 'mil']: val *= 1000
            elif multiplier in ['m', 'millon']: val *= 1000000
            
            filtered_df = filtered_df[filtered_df['price_pln_gross'] <= val]
            response += f"💰 Precio máximo: {val:,.0f} PLN. "

        # 4. Detectar Simulación de Hipoteca
        if any(kw in query for kw in ["cuota", "pagaria", "hipoteca", "simula", "mortgage", "loan"]):
            target_item = None
            sim_prefix = ""
            
            if filtered_df.empty:
                # Fallback: Usar el mejor del dataset general para no dejar al usuario sin análisis
                if not self.data.empty:
                    target_item = self.data.sort_values(by='opportunity_score', ascending=False).iloc[0]
                    sim_prefix = "⚠️ *No encontré resultados exactos con esos filtros, pero te muestro la simulación para la mejor oportunidad disponible en el mercado:* \n\n"
                else:
                    return "❌ No hay datos en la base de datos para simular.", None
            else:
                target_item = filtered_df.sort_values(by='opportunity_score', ascending=False).iloc[0]

            # Detectar años
            term = 30 # Default
            term_match = re.search(r"(\d+)\s*(años|lata|years)", query)
            if term_match: term = int(term_match.group(1))
            
            monthly = self.calc.calculate_monthly_payment(target_item['price_pln_gross'], term)
            
            response += sim_prefix
            response += f"🏠 **Análisis Financiero para: {target_item['district']}**\n"
            response += f"- Precio Total: {target_item['price_pln_gross']:,.0f} PLN\n"
            response += f"- Pago Inicial (20%): {target_item['price_pln_gross']*0.2:,.0f} PLN\n"
            response += f"- Monto Financiado: {target_item['price_pln_gross']*0.8:,.0f} PLN\n"
            response += f"- Plazo: {term} años\n"
            response += f"- **Cuota Mensual Estimada: {monthly:,.2f} PLN**\n\n"
            response += f"_{self.calc.get_market_context()}_"
            
            return response, filtered_df

        if filtered_df.empty:
            return "❌ No encontré resultados que coincidan con esos criterios.", None
            
        if response == "":
            response = "Dispongo de datos de 2027 en Polonia. ¿Qué te gustaría filtrar? (Ej: '3 cuartos en Varsovia')"
        else:
            response = "✅ Aquí tienes los resultados:\n" + response
            
        return response, filtered_df
