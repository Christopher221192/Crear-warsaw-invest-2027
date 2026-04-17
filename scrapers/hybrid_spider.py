import os
import asyncio
import logging
from typing import Dict, Optional

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from playwright_stealth import Stealth
from curl_cffi import requests as cffi_requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

PAGE_TIMEOUT    = 30_000   # ms — timeout para navegacion
CONTENT_TIMEOUT = 15_000   # ms — timeout para get_content


class HybridSpider:
    """
    Spider base: Playwright + stealth calienta la sesion (cookies + UA),
    curl_cffi hace las peticiones masivas con TLS impersonation.
    El browser se usa solo cuando curl_cffi devuelve != 200.
    """

    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy or os.getenv("HTTP_PROXY") or None
        self.cookies: Dict[str, str] = {}
        self.user_agent: str = ""

        self._playwright = None
        self._browser: Optional[Browser]  = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._warm_url: Optional[str] = None
        self._warm_html: Optional[str] = None

        self.cffi_session = cffi_requests.Session(impersonate="chrome124")
        if self.proxy:
            self.cffi_session.proxies = {"http": self.proxy, "https": self.proxy}

    # ------------------------------------------------------------------
    # Calentamiento de sesion
    # ------------------------------------------------------------------
    async def warm_session(self, url: str, keep_browser: bool = False) -> bool:
        """
        Abre Playwright con stealth, navega a la URL, captura cookies + UA.
        """
        logger.info(f"[HybridSpider] Calentando sesion en {url}")

        proxy_config = {"server": self.proxy} if self.proxy else None

        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=False,          # visible: menos detectable por CloudFront
                proxy=proxy_config,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
            )
            self._context = await self._browser.new_context(
                locale="pl-PL",
                timezone_id="Europe/Warsaw",
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
            )
            self._page = await self._context.new_page()

            # Aplicar stealth (oculta navigator.webdriver, CDP, etc.)
            await Stealth().apply_stealth_async(self._page)

            # Esperar que el DOM cargue, luego esperar el contenido real (Next.js hydration)
            await self._page.goto(url, timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")

            # Esperar listings, "sin resultados", o cualquier articulo del feed
            try:
                await self._page.wait_for_selector(
                    'a[data-cy="listing-item-link"], '
                    'a[data-testid="listing-item-link"], '
                    'article[data-cy="listing-item"], '
                    '[data-cy="no-search-results"]',
                    timeout=25_000
                )
            except Exception:
                # Si no aparecen listings, esperar un poco más como fallback
                await asyncio.sleep(8)

            # Capturar HTML post-hydration
            self._warm_url  = url
            self._warm_html = await self._page.content()

            # Capturar cookies para curl_cffi
            cookies_list = await self._context.cookies()
            for c in cookies_list:
                self.cookies[c["name"]] = c["value"]
            self.cffi_session.cookies.update(self.cookies)

            # Capturar User-Agent
            ua = await self._page.evaluate("navigator.userAgent")
            if ua:
                self.user_agent = ua
                self.cffi_session.headers.update({
                    "User-Agent": ua,
                    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8",
                    "Referer": url,
                })

            logger.info(f"[HybridSpider] Sesion lista. {len(self.cookies)} cookies obtenidas.")

            if not keep_browser:
                await self._close_browser()

            return True

        except Exception as e:
            logger.error(f"[HybridSpider] Error calentando sesion: {e}")
            await self._close_browser()
            return False

    # ------------------------------------------------------------------
    # Fetch rapido (curl_cffi — TLS impersonation)
    # ------------------------------------------------------------------
    def fetch_fast(self, url: str) -> Optional[cffi_requests.Response]:
        """Intenta obtener la URL con curl_cffi. Retorna None si falla."""
        try:
            resp = self.cffi_session.get(url, timeout=15)
            if resp.status_code == 200 and len(resp.text) > 5000:
                return resp
            return None
        except Exception as e:
            logger.debug(f"[curl_cffi] Fallo en {url}: {e}")
            return None

    # ------------------------------------------------------------------
    # Fetch con browser (Playwright + stealth — fallback)
    # ------------------------------------------------------------------
    async def fetch_with_browser(self, url: str) -> Optional[str]:
        """Navega con Playwright. Retorna HTML o None si falla."""
        if self._page is None:
            ok = await self.warm_session(url, keep_browser=True)
            if not ok:
                return None
        try:
            await self._page.goto(url, timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")
            try:
                await self._page.wait_for_selector(
                    'a[data-cy="listing-item-link"], article[data-cy="listing-item"], '
                    '[data-cy="no-search-results"]',
                    timeout=20_000
                )
            except Exception:
                await asyncio.sleep(6)
            return await self._page.content()
        except Exception as e:
            logger.warning(f"[Browser] Error en {url}: {e}")
            return None

    # ------------------------------------------------------------------
    # Fetch hibrido: rapido primero, browser como ultimo recurso
    # ------------------------------------------------------------------
    async def fetch(self, url: str) -> Optional[str]:
        # Si ya calentamos esta URL, devolver el HTML capturado directamente
        if self._warm_url and url == self._warm_url and self._warm_html:
            logger.debug(f"[HybridSpider] Usando HTML del warm_session para {url}")
            return self._warm_html

        resp = self.fetch_fast(url)
        if resp is not None:
            return resp.text
        logger.debug(f"[HybridSpider] curl_cffi fallo → browser para {url}")
        return await self.fetch_with_browser(url)

    # ------------------------------------------------------------------
    # Limpieza
    # ------------------------------------------------------------------
    async def _close_browser(self):
        try:
            if self._page:
                await self._page.close()
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass
        finally:
            self._page = self._context = self._browser = self._playwright = None

    async def close(self):
        self.cffi_session.close()
        await self._close_browser()
