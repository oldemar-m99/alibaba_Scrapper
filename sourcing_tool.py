# -*- coding: utf-8 -*-
"""
sourcing_tool.py  (PUNTO DE ENTRADA)
------------------------------------
Orquesta la herramienta de sourcing de Alibaba. No contiene logica de
detalle: solo coordina los modulos.

    config.py     -> configuracion
    proxy.py      -> descargas via ScraperAPI
    search.py     -> ETAPA 1: recolectar URLs
    extractor.py  -> HTML -> datos de producto
    storage.py    -> guardar en CSV

Uso:
    pip install requests beautifulsoup4 pandas
    python sourcing_tool.py
"""

import sys
import time

import config
from proxy import fetch
from search import recolectar_urls
from extractor import parsear_producto
from storage import cargar_urls_ya_procesadas, EscritorCSV


def etapa2_extraer(urls):
    """ETAPA 2: descarga cada producto, lo parsea y lo guarda."""
    ya_procesadas = cargar_urls_ya_procesadas()
    if ya_procesadas:
        print(f"[ETAPA 2] Reanudando: {len(ya_procesadas)} productos ya estaban en el CSV.")

    total = len(urls)
    with EscritorCSV() as escritor:
        for i, url in enumerate(urls, 1):
            if url in ya_procesadas:
                continue
            print(f"[ETAPA 2] ({i}/{total}) {url[:80]}")
            html = fetch(url)
            if not html:
                print("    [aviso] no se pudo descargar; lo salto.")
                continue
            datos = parsear_producto(html, url)
            escritor.agregar(datos)
            print(f"    OK -> proveedor='{datos['proveedor'][:40]}' | moq='{datos['moq']}'")
            time.sleep(config.PAUSE_BETWEEN_REQUESTS)

    print(f"\n[LISTO] Reporte guardado en '{config.CSV_FILE}'.")


def main():
    if config.API_KEY == "TU_API_KEY_DE_SCRAPERAPI" or not config.API_KEY:
        print("ERROR: Pon tu API Key real de ScraperAPI en config.py (variable API_KEY).")
        sys.exit(1)

    print("=" * 60)
    print(f"Sourcing Alibaba | keyword='{config.KEYWORD}' | objetivo={config.MAX_PRODUCTS}")
    print("=" * 60)

    urls = recolectar_urls()                 # ETAPA 1
    if not urls:
        print("No se encontraron URLs. Revisa el KEYWORD o prueba USE_ULTRA_PREMIUM=True.")
        sys.exit(1)

    etapa2_extraer(urls)                      # ETAPA 2


if __name__ == "__main__":
    main()
