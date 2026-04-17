import smtplib
import logging
import duckdb
import yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = "data/poland_real_estate.duckdb"


def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)


def get_opportunities(config: dict) -> list:
    """
    Devuelve listings cuyo precio/m² está por debajo del umbral configurado
    respecto a la media de su ciudad.
    """
    threshold = config.get("alerts", {}).get("discount_threshold_pct", 5)
    city_avgs = {c["id"]: c["avg_price_sqm"] for c in config.get("cities", [])}

    try:
        with duckdb.connect(DB_PATH, read_only=True) as con:
            rows = con.execute("""
                SELECT id, city, district, developer,
                       price_pln_gross, price_per_sqm, area_sqm,
                       delivery_date, url
                FROM listings
                ORDER BY price_per_sqm ASC
            """).fetchall()
    except Exception as e:
        logger.error(f"Error leyendo DuckDB: {e}")
        return []

    opportunities = []
    for row in rows:
        (lid, city, district, developer,
         price_gross, price_sqm, area,
         delivery, url) = row

        avg = city_avgs.get(city)
        if not avg or not price_sqm:
            continue

        discount_pct = (avg - price_sqm) / avg * 100
        if discount_pct >= threshold:
            opportunities.append({
                "id": lid, "city": city, "district": district,
                "developer": developer, "price_gross": price_gross,
                "price_sqm": price_sqm, "area": area,
                "delivery": delivery, "url": url,
                "discount_pct": round(discount_pct, 1),
                "avg_sqm": avg,
            })

    return sorted(opportunities, key=lambda x: x["discount_pct"], reverse=True)


def build_email_body(opportunities: list) -> str:
    lines = [
        f"<h2>🇵🇱 Poland House Hunter — {datetime.now().strftime('%d/%m/%Y %H:%M')}</h2>",
        f"<p><b>{len(opportunities)}</b> oportunidades por debajo de la media:</p>",
        "<table border='1' cellpadding='6' cellspacing='0' style='border-collapse:collapse'>",
        "<tr><th>Ciudad</th><th>Distrito</th><th>Promotor</th>"
        "<th>Precio total</th><th>€/m²</th><th>Descuento vs media</th>"
        "<th>Entrega</th><th>Link</th></tr>",
    ]
    for o in opportunities:
        lines.append(
            f"<tr>"
            f"<td>{o['city'].capitalize()}</td>"
            f"<td>{o['district']}</td>"
            f"<td>{o['developer']}</td>"
            f"<td>{o['price_gross']:,.0f} PLN</td>"
            f"<td>{o['price_sqm']:,.0f}</td>"
            f"<td style='color:green'><b>-{o['discount_pct']}%</b></td>"
            f"<td>{o['delivery']}</td>"
            f"<td><a href='{o['url']}'>Ver anuncio</a></td>"
            f"</tr>"
        )
    lines.append("</table>")
    return "\n".join(lines)


def send_alert(config: dict, opportunities: list):
    alerts_cfg = config.get("alerts", {})
    email_from = alerts_cfg.get("email_from", "")
    email_to   = alerts_cfg.get("email_to", "")
    password   = alerts_cfg.get("gmail_app_password", "")

    if not all([email_from, email_to, password]):
        logger.warning("Alerta email no configurada (faltan credenciales en config.yaml).")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🏠 {len(opportunities)} oportunidades Polonia — {datetime.now().strftime('%d/%m/%Y')}"
    msg["From"]    = email_from
    msg["To"]      = email_to
    msg.attach(MIMEText(build_email_body(opportunities), "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(email_from, password)
            server.send_message(msg)
        logger.info(f"Alerta enviada a {email_to} ({len(opportunities)} oportunidades).")
    except Exception as e:
        logger.error(f"Error enviando email: {e}")


def check_and_alert():
    """Función principal llamada por el scheduler."""
    config = load_config()
    opportunities = get_opportunities(config)
    logger.info(f"[Alerts] {len(opportunities)} oportunidades encontradas.")

    if opportunities:
        send_alert(config, opportunities)
    else:
        logger.info("[Alerts] Sin oportunidades nuevas. No se envía email.")

    return opportunities


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    ops = check_and_alert()
    if "--test" in sys.argv:
        for o in ops[:3]:
            print(o)
