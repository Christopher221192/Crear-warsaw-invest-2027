import asyncio
import logging
import re
import hashlib
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from .hybrid_spider import HybridSpider

logger = logging.getLogger(__name__)

class NieruchomosciOnlineSpider(HybridSpider):
    def __init__(self, config: Dict[str, Any], proxy=None):
        super().__init__(proxy)
        self.config = config

    def _extract_number(self, text: str) -> float:
        val = text.replace(" ", "").replace("\xa0", "").replace(",", ".")
        nums = re.findall(r"[\d.]+", val)
        return float(nums[0]) if nums else 0.0

    def parse_listing(self, html: str, url: str, city: str) -> Optional[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        
        try:
            # Filtro estricto: si aparece "wynajem" o unidades de alquiler mensual, descartar
            blacklist = ["wynajmę", "do wynajęcia", "wynajem", "zł/mc", "zł / mc", "miesiąc", "miesięcznie", "rent"]
            if any(kw in html.lower() for kw in blacklist):
                logger.debug(f"Descartando Nieruchomosci-online por palabras clave de alquiler: {url}")
                return None

            # Seleccionamos datos por texto o clases comunes
            price_tag = soup.find("span", class_="price") or soup.find(text=re.compile(r"zł$"))
            price = self._extract_number(price_tag if isinstance(price_tag, str) else (price_tag.get_text() if price_tag else "0"))
            
            area_tag = soup.find(text=re.compile(r"m²|m2"))
            area = self._extract_number(area_tag if area_tag else "0")

            district_tag = soup.find("span", class_="location") or soup.find("h1")
            district = "N/A"
            if district_tag:
                text = district_tag.get_text() if not isinstance(district_tag, str) else district_tag
                parts = text.split(",")
                district = parts[-1].strip() if len(parts) > 1 else text.strip()

            # Intentar extraer número de habitaciones
            rooms = 0
            rooms_tag = soup.find(text=re.compile(r"Liczba pokoi|pokoje"))
            if rooms_tag:
                r_nums = re.findall(r"(\d+)", rooms_tag if isinstance(rooms_tag, str) else rooms_tag.parent.get_text())
                if r_nums: rooms = int(r_nums[0])
            else:
                # Fallback: buscar patrones comunes en el resumen
                r_nums = re.findall(r"(\d+)\s*(?:poko|pokoj)", html.lower())
                if r_nums: rooms = int(r_nums[0])

            return {
                "id": hashlib.md5(url.encode()).hexdigest(),
                "portal": "nieruchomosci_online",
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
            logger.error(f"Error parseando Nieruchomosci-online {url}: {e}")
            return None

    async def run(self, city: str) -> List[Dict]:
        portal_cfg = next((p for p in self.config.get("portals", {}).get("primary", []) if p["name"] == "nieruchomosci_online"), None)
        if not portal_cfg: return []

        base_url = portal_cfg["url_template"].format(city=city)
        ok = await self.warm_session(base_url, keep_browser=True)
        if not ok: return []

        all_results = []
        html = await self.fetch(base_url)
        if not html: return []

        soup = BeautifulSoup(html, "html.parser")
        # Links a anuncios
        links = soup.find_all("a", href=lambda h: h and ".html" in h and "/oferta/" not in h)
        # Nieruchomosci-online usa links relativos tipo /mieszkanie-na-sprzedaz-X.html
        detail_urls = list({
            (f"https://{city}.nieruchomosci-online.pl{l['href']}" if l["href"].startswith("/") else l["href"])
            for l in links if l.get("href") and ("mieszkanie" in l["href"] or "oferta" in l["href"])
        })

        logger.info(f"[Nieruchomosci-online] {len(detail_urls)} anuncios encontrados.")
        
        for u in detail_urls[:5]:
            res = await self.fetch(u)
            if res:
                p = self.parse_listing(res, u, city)
                if p: all_results.append(p)
            await asyncio.sleep(1)

        await self.close()
        return all_results
