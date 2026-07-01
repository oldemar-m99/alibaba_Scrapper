# -*- coding: utf-8 -*-
"""
sourcing_tool.py  (PUNTO DE ENTRADA)
------------------------------------
Orquesta la extraccion de proveedores de Alibaba via ScraperAPI.

    config.py     -> configuracion y filtros
    search.py     -> construye la URL filtrada + paginacion
    proxy.py      -> descarga via ScraperAPI (reintentos + anti-CAPTCHA)
    extractor.py  -> HTML -> lista de productos (objeto __page__data_sse10)
    storage.py    -> guarda en CSV

Uso:
    python sourcing_tool.py
"""

import sys
import time

import config
from search import construir_url
from proxy import fetch
from extractor import parsear_resultados
from storage import cargar_urls_ya_procesadas, EscritorCSV


def main():
    if config.API_KEY == "TU_API_KEY_DE_SCRAPERAPI" or not config.API_KEY:
        print("ERROR: Pon tu API Key real de ScraperAPI en config.py.")
        sys.exit(1)

    print("=" * 62)
    print(f"Sourcing Alibaba | keyword='{config.KEYWORD}' | paginas={config.MAX_PAGES}")
    print(f"Filtros: {config.FILTROS}")
    print("=" * 62)

    ya = cargar_urls_ya_procesadas()
    if ya:
        print(f"[info] {len(ya)} productos ya estaban en el CSV (se omiten).")

    total_nuevos = 0
    with EscritorCSV() as escritor:
        for page in range(config.START_PAGE, config.START_PAGE + config.MAX_PAGES):
            url = construir_url(config.KEYWORD, page)
            print(f"\n[PAGINA {page}] descargando via ScraperAPI...")
            html = fetch(url)
            if not html:
                print("   [error] no se logro pagina buena (CAPTCHA persistente).")
                continue

            filas = parsear_resultados(html)
            print(f"   [ok] {len(filas)} productos extraidos del objeto de datos.")
            nuevos = 0
            for f in filas:
                if f["url"] in ya:
                    continue
                ya.add(f["url"])
                escritor.agregar(f)
                nuevos += 1
            total_nuevos += nuevos
            print(f"   [guardado] {nuevos} nuevos (resto ya estaban).")
            time.sleep(config.PAUSE_BETWEEN_REQUESTS)

    print(f"\n[LISTO] {total_nuevos} productos nuevos en '{config.CSV_FILE}'.")


if __name__ == "__main__":
    main()
