import json
import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from .hybrid_spider import HybridSpider

logger = logging.getLogger(__name__)

class RynekPierwotnySpider(HybridSpider):
    def __init__(self, config: Dict[str, Any], proxy=None):
        super().__init__(proxy)
        self.config = config
        self.target_quarters = [q.lower() for q in config.get("filters", {}).get("delivery_quarters", [])]

    def _parse_price(self, text: str) -> float:
        """Extrae el primer número de un texto tipo 'od 11 500 zł/m2'."""
        nums = re.findall(r"[\d\s]+", text.replace("\xa0", " "))
        if nums:
            val = nums[0].replace(" ", "")
            try:
                return float(val)
            except ValueError:
                return 0.0
        return 0.0

    def _parse_area(self, text: str) -> float:
        """Extrae el metraje mínimo de 'Metraż 35-60 m2'."""
        nums = re.findall(r"(\d+[\d\s,.]*)", text.replace("\xa0", " "))
        if nums:
            val = nums[0].replace(" ", "").replace(",", ".")
            try:
                return float(val)
            except ValueError:
                return 0.0
        return 0.0

    def parse_listing(self, html: str, url: str, city: str) -> Optional[Dict[str, Any]]:
        """
        En RynekPierwotny, a veces parseamos la inversión completa o el apartamento.
        Intentamos extraer datos del HTML de la página de detalle.
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # En RynekPierwotny 2026, los datos suelen estar en un script con JSON o en atributos data-
        # Por simplicidad en esta versión, buscaremos selectores CSS directos detectados en el research
        
        try:
            title = soup.find("h1")
            title_text = title.get_text(strip=True) if title else "Inversión desconocida"
            
            # Ubicación
            location_tag = soup.find("span", class_=re.compile(r"location|address"))
            district = "N/A"
            if location_tag:
                parts = location_tag.get_text(strip=True).split(",")
                if len(parts) > 1:
                    district = parts[1].strip()

            # Fecha de entrega
            delivery_tag = soup.find(text=re.compile(r"kw\.|kwartał|gotowe"))
            delivery_date = delivery_tag.strip() if delivery_tag else "N/A"

            # Precios y Metraje (buscamos patrones en el texto)
            price_sqm = self._parse_price(soup.find(text=re.compile(r"zł/m²")) or "")
            area = self._parse_area(soup.find(text=re.compile(r"m²|metraż")) or "")

            # Si no hay precio o área clara en el detalle, es probable que sea una página de inversión
            # que requiere interactuar. Por ahora, devolvemos el primer apartamento encontrado o la inversión.
            
            return {
                "id": hashlib.md5(url.encode()).hexdigest(),
                "portal": "rynekpierwotny",
                "url": url,
                "city": city,
                "district": district,
                "developer": title_text, # En RP el título suele ser el nombre de la inversión
                "price_pln_gross": price_sqm * area if price_sqm and area else 0,
                "price_type": "gross",
                "price_per_sqm": price_sqm,
                "area_sqm": area,
                "rooms": 0, # Extraer si es posible
                "floor": 0,
                "total_floors": 0,
                "delivery_date": delivery_date,
                "phase": "construccion",
                "lat": None,
                "lon": None
            }
        except Exception as e:
            logger.error(f"Error parseando {url}: {e}")
            return None

    async def run(self, city: str) -> List[Dict]:
        portal_cfg = next(
            (p for p in self.config.get("portals", {}).get("primary", []) if p["name"] == "rynekpierwotny"),
            None
        )
        if not portal_cfg: return []

        base_url = portal_cfg["url_template"].format(city=city)
        ok = await self.warm_session(base_url, keep_browser=True)
        if not ok: return []

        all_results = []
        max_pages = self.config.get("scraper", {}).get("max_pages", 1)

        for page in range(1, max_pages + 1):
            # RynekPierwotny usa /?page=X
            current_url = f"{base_url}&page={page}" if page > 1 else base_url
            logger.info(f"[RynekPierwotny] Página {page}: {current_url}")

            html = await self.fetch(current_url)
            if not html: break

            soup = BeautifulSoup(html, "html.parser")
            # Encontrar links a inversiones
            links = soup.find_all("a", href=lambda h: h and "/oferta/" in h)
            detail_urls = list({
                (f"https://rynekpierwotny.pl{l['href']}" if l["href"].startswith("/") else l["href"])
                for l in links if l.get("href")
            })

            if not detail_urls: break

            logger.info(f"[RynekPierwotny] {len(detail_urls)} inversiones encontradas.")

            sem = asyncio.Semaphore(2) # Más lento para evitar bloqueos en RP
            for u in detail_urls[:10]: # Limitar para no saturar en el test
                res = await self.fetch(u)
                if res:
                    p = self.parse_listing(res, u, city)
                    if p:
                        all_results.append(p)
                        logger.info(f"✅ {p['developer']} | {p['price_per_sqm']:,.0f}/m²")
                await asyncio.sleep(1)

        await self.close()
        return all_results

import hashlib
