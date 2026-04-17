import asyncio
import logging
import re
import hashlib
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from .hybrid_spider import HybridSpider

logger = logging.getLogger(__name__)

class GratkaSpider(HybridSpider):
    def __init__(self, config: Dict[str, Any], proxy=None):
        super().__init__(proxy)
        self.config = config

    def _clean_price(self, text: str) -> float:
        val = text.replace(" ", "").replace("zł", "").replace(",", ".").replace("\xa0", "")
        try:
            return float(re.findall(r"[\d.]+", val)[0])
        except (ValueError, IndexError):
            return 0.0

    def parse_listing(self, html: str, url: str, city: str) -> Optional[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        
        try:
            # Filtro estricto: si aparece "wynajem" o unidades de alquiler mensual, descartar
            blacklist = ["wynajmę", "do wynajęcia", "wynajem", "zł/mc", "zł / mc", "miesiąc", "miesięcznie", "rent"]
            if any(kw in html.lower() for kw in blacklist):
                logger.debug(f"Descartando Gratka por palabras clave de alquiler: {url}")
                return None

            # En Gratka 2026, los datos suelen estar en clases descriptivas
            price_tag = soup.find("span", class_="price") or soup.find("span", class_=re.compile(r"property-card__price"))
            price = self._clean_price(price_tag.get_text() if price_tag else "0")
            
            area_tag = soup.find(text=re.compile(r"m2|m²"))
            area = 0.0
            if area_tag:
                nums = re.findall(r"(\d+[\d\s,.]*)", area_tag)
                if nums: area = float(nums[0].replace(",", ".").replace(" ", ""))

            location_tag = soup.find("span", class_=re.compile(r"location"))
            district = location_tag.get_text(strip=True) if location_tag else "N/A"

            # Intentar extraer número de habitaciones
            rooms = 0
            rooms_tag = soup.find(text=re.compile(r"Liczba pokoi|pokoje"))
            if rooms_tag:
                r_nums = re.findall(r"(\d+)", rooms_tag.parent.get_text())
                if r_nums: rooms = int(r_nums[0])
            else:
                # Buscar en todo el texto si falla el tag específico
                r_nums = re.findall(r"(\d+)\s*(?:poko|pokoj)", html.lower())
                if r_nums: rooms = int(r_nums[0])

            return {
                "id": hashlib.md5(url.encode()).hexdigest(),
                "portal": "gratka",
                "url": url,
                "city": city,
                "district": district,
                "developer": "N/A",
                "price_pln_gross": price,
                "price_type": "gross",
                "price_per_sqm": price / area if area else 0,
                "area_sqm": area,
                "rooms": rooms,
                "floor": 0,
                "total_floors": 0,
                "delivery_date": "2027",
                "phase": "construccion",
                "lat": None,
                "lon": None
            }
        except Exception as e:
            logger.error(f"Error parseando Gratka {url}: {e}")
            return None

    async def run(self, city: str) -> List[Dict]:
        portal_cfg = next((p for p in self.config.get("portals", {}).get("primary", []) if p["name"] == "gratka"), None)
        if not portal_cfg: return []

        base_url = portal_cfg["url_template"].format(city=city)
        ok = await self.warm_session(base_url, keep_browser=True)
        if not ok: return []

        all_results = []
        html = await self.fetch(base_url)
        if not html: return []

        soup = BeautifulSoup(html, "html.parser")
        # Links a anuncios: suelen ser a.property-card o similar
        links = soup.find_all("a", href=lambda h: h and "/nieruchomosci/" in h)
        detail_urls = list({
            (f"https://gratka.pl{l['href']}" if l["href"].startswith("/") else l["href"])
            for l in links if l.get("href")
        })

        logger.info(f"[Gratka] {len(detail_urls)} anuncios encontrados.")
        
        for u in detail_urls[:5]: # Probar pocos para el demo
            res = await self.fetch(u)
            if res:
                p = self.parse_listing(res, u, city)
                if p: all_results.append(p)
            await asyncio.sleep(1)

        await self.close()
        return all_results
