# -*- coding: utf-8 -*-
"""
proxy.py
--------
Responsabilidad UNICA: descargar una URL a traves de ScraperAPI.
Incluye reintentos por error de red/500 y por pagina de CAPTCHA de Alibaba.
"""

import time
import requests

import config


def _es_captcha(html):
    """Detecta la pagina de verificacion/CAPTCHA de Alibaba."""
    cabeza = html[:6000].lower()
    return ("punish" in cabeza or "slider" in cabeza or
            "captcha" in cabeza or "verify" in cabeza)


def _es_buena(html):
    """Una pagina buena trae el objeto de datos con las ofertas."""
    return "__page__data_sse" in html or '"offerResultData"' in html


def _params(url):
    p = {"api_key": config.API_KEY, "url": url, "country_code": config.COUNTRY_CODE}
    if config.USE_RENDER:
        p["render"] = "true"
    if config.USE_ULTRA_PREMIUM:
        p["ultra_premium"] = "true"
    elif config.USE_PREMIUM:
        p["premium"] = "true"
    return p


def _peticion(url):
    """Una sola peticion a ScraperAPI con reintentos por error de red/500."""
    for intento in range(1, config.MAX_RETRIES + 1):
        try:
            r = requests.get(config.SCRAPERAPI_ENDPOINT, params=_params(url),
                             timeout=config.REQUEST_TIMEOUT)
            if r.status_code == 200 and r.text:
                return r.text
            print(f"     [aviso] status {r.status_code} (intento {intento}/{config.MAX_RETRIES})")
        except requests.RequestException as e:
            print(f"     [aviso] error de red: {e} (intento {intento}/{config.MAX_RETRIES})")
        time.sleep(2 * intento)
    return None


def fetch(url):
    """Descarga 'url' insistiendo hasta obtener una pagina buena (no CAPTCHA).
    Devuelve el HTML bueno o None si se agotan los reintentos."""
    for intento in range(1, config.MAX_CAPTCHA_RETRIES + 1):
        html = _peticion(url)
        if html is None:
            continue
        if _es_captcha(html) and not _es_buena(html):
            print(f"   [captcha] intento {intento}/{config.MAX_CAPTCHA_RETRIES}, reintento...")
            time.sleep(config.PAUSE_BETWEEN_REQUESTS)
            continue
        if _es_buena(html):
            return html
        print(f"   [aviso] pagina sin datos (intento {intento}), reintento...")
        time.sleep(config.PAUSE_BETWEEN_REQUESTS)
    return None
