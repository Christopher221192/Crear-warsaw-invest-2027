import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from .hybrid_spider import HybridSpider

logger = logging.getLogger(__name__)


def _parse_floor(floor_raw) -> int:
    """Convierte ['floor_7'] o '7' o 7 a entero."""
    if floor_raw is None:
        return 0
    val = floor_raw[0] if isinstance(floor_raw, list) and floor_raw else floor_raw
    if isinstance(val, int):
        return val
    # Formato 'floor_7' → 7, 'ground_floor' → 0
    s = str(val).replace("floor_", "").replace("ground_floor", "0").replace("garret", "-1")
    try:
        return int(s)
    except ValueError:
        return 0


# Máximo de peticiones simultáneas al portal
CONCURRENCY = 3

# Quarters válidos en polaco (romano + arábigo) para Q1 y Q2 2027
VALID_QUARTERS = [
    "i kwartał 2027", "ii kwartał 2027",
    "1 kwartał 2027", "2 kwartał 2027",
    "q1 2027", "q2 2027",
    "i kw. 2027", "ii kw. 2027",
    "01/2027", "02/2027", "03/2027", "04/2027", "05/2027", "06/2027",
]


class OtodomSpider(HybridSpider):

    def __init__(self, config: Dict[str, Any], proxy=None):
        super().__init__(proxy)
        self.config = config
        self.target_quarters = [q.lower() for q in config.get("filters", {}).get("delivery_quarters", [])]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _is_target_delivery(self, delivery_raw: str, build_year: Any) -> bool:
        """Devuelve True si el anuncio es de entrega Q1/Q2 2027."""
        d = delivery_raw.lower().strip()
        if any(q in d for q in VALID_QUARTERS):
            return True
        # Fallback: build_year 2027 sin quarter explícito
        if "2027" in str(build_year) and d == "":
            return True
        return False

    def _detect_price_type(self, description: str) -> str:
        """Detecta si el precio es netto o gross."""
        desc = description.lower()
        if any(kw in desc for kw in ["netto", "cena netto", "bez vat", "+ vat", "+vat"]):
            return "netto"
        return "gross"

    def parse_listing(self, html: str, url: str, city: str) -> Optional[Dict[str, Any]]:
        """Extrae datos del JSON __NEXT_DATA__ embebido en la página."""
        soup = BeautifulSoup(html, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if not script:
            logger.debug(f"Sin __NEXT_DATA__ en {url}")
            return None

        try:
            raw = json.loads(script.string)
            ad = raw.get("props", {}).get("pageProps", {}).get("ad")
            if not ad or not isinstance(ad, dict):
                return None

            target    = ad.get("target") or {}
            category  = target.get("Category")
            t_type    = target.get("Type")
            
            # Solo venta de apartamentos
            if category != "sell" or t_type != "apartment":
                logger.debug(f"Descartando por categoría: {category} / {t_type}")
                return None

            build_year = target.get("Build_year")
            chars = {c["key"]: c["value"] for c in ad.get("characteristics", [])}
            delivery_raw = chars.get("delivery_date", "")

            if not self._is_target_delivery(delivery_raw, build_year):
                return None

            # Precio: target.Price primero, fallback a characteristics
            price_raw = float(target.get("Price", 0) or 0)
            if not price_raw:
                price_char = chars.get("price", "0").replace(" ", "").replace("zł", "").replace(",", ".")
                try:
                    price_raw = float(price_char)
                except ValueError:
                    price_raw = 0.0

            area_sqm = float(target.get("Area", 0) or 0)
            if not area_sqm:
                area_char = chars.get("m", "0").replace(" ", "").replace("m²", "")
                try:
                    area_sqm = float(area_char)
                except ValueError:
                    area_sqm = 0.0
            # description es string en Otodom 2026 (antes era {value: ...})
            desc_raw  = ad.get("description", "") or ""
            desc      = desc_raw if isinstance(desc_raw, str) else (desc_raw.get("value", "") or "")
            price_type = self._detect_price_type(desc)

            if price_type == "netto":
                price_gross = price_raw * 1.08
            else:
                price_gross = price_raw

            price_per_sqm = price_gross / area_sqm if area_sqm else 0

            return {
                "id":             str(ad.get("id", "")),
                "portal":         "otodom",
                "url":            url,
                "city":           city,
                "district":       ad.get("location", {}).get("address", {}).get("district", {}).get("name", "N/A"),
                "developer":      ad.get("advertiser", {}).get("name", "N/A"),
                "price_pln_gross": price_gross,
                "price_type":     price_type,
                "price_per_sqm":  price_per_sqm,
                "area_sqm":       area_sqm,
                "rooms":          int(str((target.get("Rooms_num") or [0])[0])) if isinstance(target.get("Rooms_num"), list) else 0,
                # Floor_no puede ser ['floor_7'] o un entero
                "floor":          _parse_floor(target.get("Floor_no")),
                "total_floors":   int(target.get("Building_floors_num", 0) or 0),
                "delivery_date":  delivery_raw or f"2027",
                "phase":          "construccion" if build_year else "planos",
                "lat":            ad.get("location", {}).get("coordinates", {}).get("latitude"),
                "lon":            ad.get("location", {}).get("coordinates", {}).get("longitude"),
                "description":    desc,
            }
        except Exception as e:
            logger.error(f"Error parseando {url}: {e}")
            return None

    # ------------------------------------------------------------------
    # Scraping de una URL de detalle (usado en gather)
    # ------------------------------------------------------------------
    async def _scrape_detail(self, url: str, city: str, sem: asyncio.Semaphore) -> Optional[Dict]:
        async with sem:
            html = await self.fetch(url)
            if not html:
                return None
            return self.parse_listing(html, url, city)

    # ------------------------------------------------------------------
    # Punto de entrada principal
    # ------------------------------------------------------------------
    async def run(self, city: str) -> List[Dict]:
        portal_cfg = next(
            (p for p in self.config.get("portals", {}).get("primary", []) if p["name"] == "otodom"),
            None
        )
        if not portal_cfg:
            logger.error("Configuración de otodom no encontrada en config.yaml")
            return []

        base_url = portal_cfg["url_template"].format(city=city)

        # Calentar sesión una sola vez
        ok = await self.warm_session(base_url, keep_browser=True)
        if not ok:
            logger.error("No se pudo calentar la sesión. Abortando.")
            return []

        all_results: List[Dict] = []
        max_pages = self.config.get("scraper", {}).get("max_pages", 3)

        for page in range(1, max_pages + 1):
            current_url = f"{base_url}&page={page}" if page > 1 else base_url
            logger.info(f"[Otodom] Página {page}: {current_url}")

            html = await self.fetch(current_url)
            if not html:
                logger.warning(f"[Otodom] Sin respuesta en página {page}. Deteniendo.")
                break

            soup = BeautifulSoup(html, "html.parser")

            # Selector primario: href que contenga /oferta/ (estable en Otodom 2026)
            links = soup.find_all("a", href=lambda h: h and "/oferta/" in h)
            detail_urls = list({
                (f"https://www.otodom.pl{l['href']}" if l["href"].startswith("/") else l["href"])
                for l in links if l.get("href")
            })

            # Debug: si no hay links, volcar fragmento del HTML para diagnóstico
            if not detail_urls:
                snippet = html[:2000] if html else "(vacío)"
                logger.warning(f"[Otodom] Sin anuncios en página {page}. HTML snippet:\n{snippet}")
                break

            logger.info(f"[Otodom] {len(detail_urls)} anuncios encontrados. Procesando en paralelo (max {CONCURRENCY})...")

            sem = asyncio.Semaphore(CONCURRENCY)
            tasks = [self._scrape_detail(u, city, sem) for u in detail_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for r in results:
                if isinstance(r, dict):
                    all_results.append(r)
                    logger.info(f"✅ {r['district']} | {r['price_pln_gross']:,.0f} PLN | {r['price_per_sqm']:,.0f}/m²")
                elif isinstance(r, Exception):
                    logger.error(f"Error en tarea: {r}")

            # Pausa entre páginas para no saturar
            if page < max_pages:
                await asyncio.sleep(2)

        await self.close()
        logger.info(f"[Otodom] Total recolectados para {city}: {len(all_results)}")
        return all_results


if __name__ == "__main__":
    import yaml
    logging.basicConfig(level=logging.INFO)

    async def test():
        with open("config.yaml") as f:
            config = yaml.safe_load(f)
        spider = OtodomSpider(config)
        results = await spider.run("warszawa")
        print(f"Total: {len(results)}")
        for r in results[:3]:
            print(r)

    asyncio.run(test())
