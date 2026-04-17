import duckdb
import os
import logging
import asyncio
import yaml

from pipeline.normalizer import Normalizer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = "data/poland_real_estate.duckdb"


def setup_duckdb(db_path: str = DB_PATH):
    """Inicializa tablas de DuckDB si no existen."""
    os.makedirs("data", exist_ok=True)

    with duckdb.connect(db_path) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id               VARCHAR PRIMARY KEY,
                portal           VARCHAR,
                url              VARCHAR,
                city             VARCHAR,
                district         VARCHAR,
                developer        VARCHAR,
                price_pln_gross  DOUBLE,
                price_type       VARCHAR DEFAULT 'gross',
                price_per_sqm    DOUBLE,
                area_sqm         DOUBLE,
                rooms            INTEGER,
                floor            INTEGER,
                total_floors     INTEGER,
                delivery_date    VARCHAR,
                phase            VARCHAR,
                lat              DOUBLE,
                lon              DOUBLE,
                description      VARCHAR,
                last_updated     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS listing_fingerprints (
                fingerprint_hash VARCHAR PRIMARY KEY,
                canonical_id     VARCHAR REFERENCES listings(id),
                duplicate_ids    JSON,
                first_seen       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    logger.info("DuckDB schema inicializado.")


def save_listings(listings: list, db_path: str = DB_PATH):
    """Inserta o actualiza listings en DuckDB con deduplicación por fingerprint."""
    if not listings:
        return 0

    saved = 0
    with duckdb.connect(db_path) as con:
        for item in listings:
            # Normalizar precio (VAT) antes de guardar
            item = Normalizer.normalize_price(item)
            item = Normalizer.sanitize_gdpr(item)
            fp   = Normalizer.calculate_fingerprint(item)

            if not Normalizer.is_valid_transaction(item):
                logger.debug(f"Anuncio descartado (posible alquiler o precio inválido): {item.get('id')} - {item.get('price_pln_gross')} PLN")
                continue

            # Deduplicación cross-portal por fingerprint
            existing = con.execute(
                "SELECT canonical_id FROM listing_fingerprints WHERE fingerprint_hash = ?", [fp]
            ).fetchone()

            if existing:
                logger.debug(f"Duplicado detectado: {item['id']} ≈ {existing[0]}")
                continue

            try:
                con.execute("""
                    INSERT OR REPLACE INTO listings
                    (id, portal, url, city, district, developer,
                     price_pln_gross, price_type, price_per_sqm,
                     area_sqm, rooms, floor, total_floors,
                     delivery_date, phase, lat, lon, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item["id"], item["portal"], item["url"], item["city"],
                    item["district"], item["developer"],
                    item["price_pln_gross"], item.get("price_type", "gross"),
                    item["price_per_sqm"], item["area_sqm"], item["rooms"],
                    item["floor"], item["total_floors"], item["delivery_date"],
                    item["phase"], item.get("lat"), item.get("lon"), item.get("description", "")
                ))
                con.execute("""
                    INSERT OR IGNORE INTO listing_fingerprints (fingerprint_hash, canonical_id)
                    VALUES (?, ?)
                """, [fp, item["id"]])
                saved += 1
            except Exception as e:
                logger.error(f"Error insertando {item.get('id')}: {e}")

    return saved


async def run_scraper(config: dict, city_id: str, portal_name: str):
    """Ejecuta el scraper de un portal específico para una ciudad."""
    try:
        if portal_name == "otodom":
            from scrapers.otodom import OtodomSpider
            spider_cls = OtodomSpider
        elif portal_name == "rynekpierwotny":
            from scrapers.rynekpierwotny import RynekPierwotnySpider
            spider_cls = RynekPierwotnySpider
        elif portal_name == "gratka":
            from scrapers.gratka import GratkaSpider
            spider_cls = GratkaSpider
        elif portal_name == "nieruchomosci_online":
            from scrapers.nieruchomosci_online import NieruchomosciOnlineSpider
            spider_cls = NieruchomosciOnlineSpider
        else:
            logger.warning(f"Portal no soportado o implementado: {portal_name}")
            return []

        logger.info(f"Iniciando scraping {portal_name} → {city_id}")
        spider = spider_cls(config)
        return await spider.run(city_id)
    except Exception as e:
        logger.error(f"Error en scraper {portal_name} ({city_id}): {e}")
        return []


async def main():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    setup_duckdb()

    active_cities = config.get("cities", [])
    total_saved = 0
    portals = config.get("portals", {}).get("primary", [])

    # Iterar por ciudades y por cada portal activo
    for city in active_cities:
        city_id = city["id"]
        for portal in portals:
            if not portal.get("active", False):
                continue
            
            listings = await run_scraper(config, city_id, portal["name"])
            if listings:
                n = save_listings(listings)
                total_saved += n
                logger.info(f"[{portal['name']} | {city_id}] {n} anuncios guardados (de {len(listings)} encontrados).")
            
            # Pausa breve entre portales/ciudades
            await asyncio.sleep(2)

    logger.info(f"=== Proceso completo. Total guardados: {total_saved} ===")

    # Resumen rápido desde DuckDB
    with duckdb.connect(DB_PATH) as con:
        summary = con.execute("""
            SELECT portal, city, COUNT(*) as total, ROUND(AVG(price_per_sqm)) as avg_sqm
            FROM listings GROUP BY portal, city ORDER BY portal, avg_sqm
        """).df()
    if not summary.empty:
        print("\n--- Resumen por portal y ciudad ---")
        print(summary.to_string(index=False))


if __name__ == "__main__":
    # Un solo event loop para todas las ciudades — evita conflictos de nodriver
    asyncio.run(main())
