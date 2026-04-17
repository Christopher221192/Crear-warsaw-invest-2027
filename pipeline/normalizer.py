import hashlib
from typing import Dict, Any

class Normalizer:
    @staticmethod
    def calculate_fingerprint(listing: Dict[str, Any]) -> str:
        """
        Genera fingerprint para detectar duplicados cross-portal 
        basado en los atributos clave inmutables del apartamento.
        """
        key = f"{listing.get('city', '')}|{listing.get('district', '')}|" \
              f"{listing.get('developer', '')}|{listing.get('area_sqm', 0):.1f}|" \
              f"{listing.get('rooms', 0)}|{listing.get('floor', 0)}"
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    def sanitize_gdpr(listing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Elimina PII (nombres y telefonos de agentes) conservando
        solo datos empresariales de la inversión.
        """
        gdpr_fields = ["agent_name", "agent_phone", "agent_email", "contact_person"]
        for field in gdpr_fields:
            listing.pop(field, None)
            
        # Anonimizar si no parece empresa
        dev = listing.get("developer", "")
        if dev:
            corp_suffixes = ["sp. z o.o.", "S.A.", "sp.k.", "sp.j.", "group", "development", "invest"]
            if not any(s.lower() in dev.lower() for s in corp_suffixes):
                listing["developer"] = "[INDIVIDUAL - REDACTED]"
                
        return listing
        
    @staticmethod
    def normalize_price(listing: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determina si el VAT estaba incluido (gross) o no (netto).
        Normaliza a un precio gross estandar (con 8% de VAT).
        Si el scraper ya calculó price_pln_gross, lo respeta.
        """
        # El scraper de Otodom ya entrega price_pln_gross calculado.
        # Sólo recalcular si viene price_pln (portales legados).
        price_gross = listing.get("price_pln_gross") or 0
        price_legacy = listing.get("price_pln", 0)
        area = listing.get("area_sqm", 1) or 1
        p_type = listing.get("price_type", "gross")

        if price_legacy and not price_gross:
            # Portales legados que envían price_pln sin VAT aplicado
            if p_type == "netto":
                price_gross = price_legacy * 1.08
            else:
                price_gross = price_legacy
            listing["price_pln_gross"] = price_gross

        # Recalcular price_per_sqm si está vacío o incorrecto
        if price_gross and not listing.get("price_per_sqm"):
            listing["price_per_sqm"] = price_gross / area

        return listing
    @staticmethod
    def is_valid_transaction(listing: Dict[str, Any]) -> bool:
        """
        Verifica si el anuncio parece una venta real y no un alquiler
        o un error de datos.
        """
        price = listing.get("price_pln_gross", 0)
        city = listing.get("city", "").lower()
        
        # Umbral dinámico por ciudad (Mercado Primario 2026/2027)
        # En capitales y ciudades grandes, < 200k PLN es casi siempre alquiler.
        major_cities = ["warszawa", "krakow", "wroclaw", "gdansk"]
        threshold = 200000 if city in major_cities else 100000
        
        if 0 < price < threshold:
            return False
            
        return True
