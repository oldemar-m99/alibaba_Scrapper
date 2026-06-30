# -*- coding: utf-8 -*-
"""
search.py
---------
ETAPA 1. Responsabilidad: dado un KEYWORD, devolver una lista de URLs de
productos de Alibaba. Maneja paginacion y cache en disco.
"""

import os
import re
import time

import requests
from bs4 import BeautifulSoup

import config
from proxy import fetch


def construir_url_busqueda(keyword, page):
    kw = requests.utils.quote(keyword)
    return f"https://www.alibaba.com/trade/search?SearchText={kw}&page={page}"


def extraer_links_de_busqueda(html):
    """Extrae URLs de paginas de producto desde el HTML de una pagina de busqueda."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/product-detail/" in href or re.search(r"alibaba\.com/.+_\d+\.html", href):
            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                href = "https://www.alibaba.com" + href
            href = href.split("?")[0]  # quita parametros de tracking
            if "alibaba.com" in href:
                links.add(href)
    return links


def _leer_cache():
    if not os.path.exists(config.URLS_CACHE):
        return []
    with open(config.URLS_CACHE, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]


def _guardar_cache(urls):
    with open(config.URLS_CACHE, "w", encoding="utf-8") as f:
        f.write("\n".join(urls))


def recolectar_urls():
    """Devuelve hasta MAX_PRODUCTS URLs de producto. Reusa cache si existe."""
    cached = _leer_cache()
    if cached:
        print(f"[ETAPA 1] Reusando {len(cached)} URLs de '{config.URLS_CACHE}'")
        return cached[:config.MAX_PRODUCTS]

    print(f"[ETAPA 1] Buscando '{config.KEYWORD}' en Alibaba...")
    encontrados, vistos = [], set()
    page = config.START_PAGE
    paginas_vacias = 0

    while len(encontrados) < config.MAX_PRODUCTS:
        url = construir_url_busqueda(config.KEYWORD, page)
        print(f"  - Pagina {page} ... ({len(encontrados)} URLs hasta ahora)")
        html = fetch(url)
        if not html:
            print("    [aviso] no se pudo descargar esta pagina.")
            paginas_vacias += 1
            if paginas_vacias >= 3:
                break
            page += 1
            continue

        nuevos = [u for u in extraer_links_de_busqueda(html) if u not in vistos]
        if not nuevos:
            paginas_vacias += 1
            if paginas_vacias >= 3:
                print("    [info] varias paginas sin resultados nuevos; finalizo busqueda.")
                break
        else:
            paginas_vacias = 0
            for u in nuevos:
                vistos.add(u)
                encontrados.append(u)

        page += 1
        time.sleep(config.PAUSE_BETWEEN_REQUESTS)

    encontrados = encontrados[:config.MAX_PRODUCTS]
    _guardar_cache(encontrados)
    print(f"[ETAPA 1] {len(encontrados)} URLs guardadas en '{config.URLS_CACHE}'.")
    return encontrados
