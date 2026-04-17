"""
Listing Analyzer — uses Claude vision + text to analyze a real estate listing.

Given a URL, it:
  1. Fetches the Otodom page HTML via httpx (Chrome UA)
  2. Parses __NEXT_DATA__ JSON to extract description + image URLs
  3. Sends to Claude claude-sonnet-4-6 with vision for structured analysis
  4. Returns orientation, light quality, distribution score, pros/cons
"""

from __future__ import annotations

import json
import base64
import logging
from typing import Optional
from dataclasses import dataclass, field

import httpx
import anthropic
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

CHROME_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}

SYSTEM_PROMPT = """
Eres un experto en bienes raíces, arquitectura y análisis de propiedades residenciales en Polonia.
Analizas anuncios inmobiliarios y proporcionas evaluaciones objetivas y detalladas en español.
Cuando analices imágenes de planos o fotos de apartamentos, evalúa:
- Distribución y aprovechamiento del espacio
- Orientación solar probable (busca ventanas, balcones, posición en el edificio)
- Calidad de luz natural esperada
- Puntos fuertes y débiles del inmueble
Responde SIEMPRE con JSON válido sin markdown ni texto extra.
""".strip()

ANALYSIS_PROMPT = """
Analiza este anuncio inmobiliario en Polonia. El texto de la descripción está en polaco, tradúcelo internamente para extraer información relevante.

DESCRIPCIÓN DEL ANUNCIO:
{description}

METADATOS:
- Ciudad: {city}
- Distrito: {district}
- Piso: {floor} de {total_floors}
- Área: {area} m²
- Habitaciones: {rooms}
- Precio: {price} PLN

{image_section}

Devuelve ÚNICAMENTE este JSON (sin markdown):
{{
  "orientation": "sur" | "norte" | "este" | "oeste" | "sureste" | "suroeste" | "noreste" | "noroeste" | "no determinado",
  "light_quality": "excelente" | "muy buena" | "buena" | "moderada" | "baja" | "muy baja",
  "distribution_score": <número 1-10>,
  "distribution_comment": "<comentario sobre la distribución del espacio en 1-2 frases>",
  "pros": ["<ventaja 1>", "<ventaja 2>", "<ventaja 3>"],
  "cons": ["<desventaja 1>", "<desventaja 2>"],
  "light_analysis": "<análisis de luz natural en 2-3 frases>",
  "orientation_reasoning": "<por qué determinas esa orientación, 1-2 frases>",
  "investment_verdict": "excelente" | "bueno" | "aceptable" | "dudoso" | "evitar",
  "summary": "<resumen ejecutivo de 3-4 frases para un inversor>"
}}
""".strip()


@dataclass
class ListingAnalysis:
    orientation: str = "no determinado"
    light_quality: str = "no determinado"
    distribution_score: float = 0.0
    distribution_comment: str = ""
    pros: list = field(default_factory=list)
    cons: list = field(default_factory=list)
    light_analysis: str = ""
    orientation_reasoning: str = ""
    investment_verdict: str = "aceptable"
    summary: str = ""
    images_analyzed: int = 0
    image_urls: list = field(default_factory=list)
    error: Optional[str] = None


def _fetch_listing_html(url: str, timeout: int = 20) -> Optional[str]:
    """Fetches listing page HTML using httpx with Chrome headers."""
    try:
        with httpx.Client(headers=CHROME_HEADERS, follow_redirects=True, timeout=timeout) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                return resp.text
            logger.warning(f"HTTP {resp.status_code} for {url}")
            return None
    except Exception as e:
        logger.error(f"Fetch error for {url}: {e}")
        return None


def _parse_otodom_data(html: str) -> dict:
    """Parses __NEXT_DATA__ from Otodom page."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        return {}
    try:
        raw = json.loads(script.string)
        ad = raw.get("props", {}).get("pageProps", {}).get("ad") or {}
        return ad
    except Exception:
        return {}


def _extract_images(ad: dict, max_images: int = 5) -> list[str]:
    """Extracts image URLs from Otodom ad data, preferring floor plans."""
    images = ad.get("images") or []
    urls = []

    # Otodom image objects: {"large": "...", "medium": "...", "small": "..."}
    for img in images:
        url = img.get("large") or img.get("medium") or img.get("small") or ""
        if url:
            urls.append(url)

    # Heuristic: floor plans often have 'rzut' in the URL or come last
    floor_plans = [u for u in urls if "rzut" in u.lower() or "floor" in u.lower()]
    regular = [u for u in urls if u not in floor_plans]

    # Priority: floor plans first, then regular photos
    ordered = floor_plans + regular
    return ordered[:max_images]


def _image_to_base64(url: str, timeout: int = 15) -> Optional[tuple[str, str]]:
    """Downloads image and returns (base64_data, media_type)."""
    try:
        with httpx.Client(headers=CHROME_HEADERS, follow_redirects=True, timeout=timeout) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                content_type = resp.headers.get("content-type", "image/jpeg").split(";")[0]
                return base64.standard_b64encode(resp.content).decode("utf-8"), content_type
    except Exception as e:
        logger.debug(f"Image download failed {url}: {e}")
    return None


def analyze_listing(
    url: str,
    city: str = "",
    district: str = "",
    floor: int = 0,
    total_floors: int = 0,
    area: float = 0,
    rooms: int = 0,
    price: float = 0,
) -> ListingAnalysis:
    """
    Full pipeline: fetch → parse → analyze with Claude.
    Returns a ListingAnalysis dataclass.
    """
    # 1. Fetch HTML
    html = _fetch_listing_html(url)
    if not html:
        return ListingAnalysis(error="No se pudo obtener el anuncio (posible bloqueo anti-bot).")

    # 2. Parse Otodom data
    ad = _parse_otodom_data(html)
    if not ad:
        return ListingAnalysis(error="No se pudo parsear el anuncio (formato inesperado).")

    # 3. Extract description
    desc_raw = ad.get("description", "") or ""
    description = desc_raw if isinstance(desc_raw, str) else (desc_raw.get("value", "") or "")
    description = description[:4000]  # cap to avoid token overflow

    # 4. Extract and download images
    image_urls = _extract_images(ad, max_images=5)
    image_contents = []
    for img_url in image_urls:
        result = _image_to_base64(img_url)
        if result:
            image_contents.append(result)
        if len(image_contents) >= 4:  # max 4 images to Claude
            break

    # 5. Build prompt
    if image_contents:
        image_section = f"Se incluyen {len(image_contents)} imágenes del anuncio (fotos y/o planos) para tu análisis visual."
    else:
        image_section = "No se pudieron obtener imágenes. Basa el análisis solo en la descripción y metadatos."

    prompt = ANALYSIS_PROMPT.format(
        description=description or "No disponible",
        city=city or "Polonia",
        district=district or "—",
        floor=floor or "—",
        total_floors=total_floors or "—",
        area=f"{area:.0f}" if area else "—",
        rooms=rooms or "—",
        price=f"{int(price):,}" if price else "—",
        image_section=image_section,
    )

    # 6. Build Claude message content
    content: list = []
    for b64_data, media_type in image_contents:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": b64_data,
            },
        })
    content.append({"type": "text", "text": prompt})

    # 7. Call Claude
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}],
        )
        raw_json = response.content[0].text.strip()

        # Strip markdown code fences if Claude wraps in ```json
        if raw_json.startswith("```"):
            raw_json = raw_json.split("```")[1]
            if raw_json.startswith("json"):
                raw_json = raw_json[4:]
            raw_json = raw_json.strip()

        data = json.loads(raw_json)
        return ListingAnalysis(
            orientation=data.get("orientation", "no determinado"),
            light_quality=data.get("light_quality", "no determinado"),
            distribution_score=float(data.get("distribution_score", 5)),
            distribution_comment=data.get("distribution_comment", ""),
            pros=data.get("pros", []),
            cons=data.get("cons", []),
            light_analysis=data.get("light_analysis", ""),
            orientation_reasoning=data.get("orientation_reasoning", ""),
            investment_verdict=data.get("investment_verdict", "aceptable"),
            summary=data.get("summary", ""),
            images_analyzed=len(image_contents),
            image_urls=image_urls,
        )
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error from Claude: {e}")
        return ListingAnalysis(error=f"Error parseando respuesta de Claude: {e}")
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return ListingAnalysis(error=f"Error en API de Claude: {e}")
