"""
scheduler.py — Scraping diario automatizado con APScheduler.

Uso:
    python scheduler.py          # corre el scheduler en background (bloquea)
    python scheduler.py --now    # ejecuta un ciclo inmediatamente y sale
"""
import asyncio
import logging
import sys
import yaml

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from main_local import setup_duckdb, run_scraper, save_listings
from notifications.alerts import check_and_alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = "data/poland_real_estate.duckdb"


def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)


async def _scrape_all(config: dict):
    """Scraping de todas las ciudades activas y guardado en DuckDB."""
    total = 0
    for city in config.get("cities", []):
        listings = await run_scraper(config, city["id"])
        n = save_listings(listings)
        total += n
        logger.info(f"[Scheduler] {city['id']}: {n} nuevos guardados.")
    logger.info(f"[Scheduler] Ciclo completo. Total: {total} anuncios.")


def job_scrape():
    """Job de scraping (sync wrapper para APScheduler)."""
    config = load_config()
    setup_duckdb(DB_PATH)
    asyncio.run(_scrape_all(config))


def job_alerts():
    """Job de alertas email."""
    check_and_alert()


def run_once():
    """Ejecuta scraping + alertas una sola vez y sale."""
    logger.info("=== Ejecución única ===")
    job_scrape()
    job_alerts()
    logger.info("=== Listo ===")


def run_scheduler():
    """Lanza el scheduler bloqueante con cron diario."""
    scheduler = BlockingScheduler(timezone="Europe/Warsaw")

    # Scraping: 07:00 hora de Varsovia
    scheduler.add_job(job_scrape, CronTrigger(hour=7, minute=0), id="scrape_daily")

    # Alertas: 07:30 (después del scraping)
    scheduler.add_job(job_alerts, CronTrigger(hour=7, minute=30), id="alerts_daily")

    logger.info("Scheduler iniciado. Scraping diario a las 07:00 (Warsaw). Ctrl+C para detener.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler detenido.")


if __name__ == "__main__":
    if "--now" in sys.argv:
        run_once()
    else:
        run_scheduler()
