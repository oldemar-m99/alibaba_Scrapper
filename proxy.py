# -*- coding: utf-8 -*-
"""
proxy.py
--------
Responsabilidad UNICA: descargar una URL a traves de ScraperAPI.
Si manana cambias de proveedor de proxy, solo tocas este archivo.
"""

import time
import requests

import config


def fetch(url):
    """Descarga 'url' via ScraperAPI con reintentos. Devuelve HTML (str) o None."""
    params = {
        "api_key": config.API_KEY,
        "url": url,
        "country_code": config.COUNTRY_CODE,
    }
    if config.USE_RENDER:
        params["render"] = "true"
    if config.USE_ULTRA_PREMIUM:
        params["ultra_premium"] = "true"

    for intento in range(1, config.MAX_RETRIES + 1):
        try:
            r = requests.get(
                config.SCRAPERAPI_ENDPOINT,
                params=params,
                timeout=config.REQUEST_TIMEOUT,
            )
            if r.status_code == 200 and r.text:
                return r.text
            print(f"   [aviso] status {r.status_code} (intento {intento}/{config.MAX_RETRIES})")
        except requests.RequestException as e:
            print(f"   [aviso] error de red: {e} (intento {intento}/{config.MAX_RETRIES})")
        time.sleep(2 * intento)  # backoff incremental
    return None
