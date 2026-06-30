# -*- coding: utf-8 -*-
"""
config.py
---------
Configuracion central de la herramienta. EDITA AQUI todo lo ajustable.
Ningun otro modulo deberia tener "numeros magicos": todos viven aqui.
"""

# === 1) CREDENCIALES Y BUSQUEDA  (EDITA ESTO) ===
API_KEY = "TU_API_KEY_DE_SCRAPERAPI"   # <-- pega tu API Key real de ScraperAPI
KEYWORD = "industrial machinery"        # <-- producto a investigar

# === 2) ALCANCE ===
MAX_PRODUCTS = 20          # 20 = prueba; sube a 1000 cuando confirmes que funciona
START_PAGE = 1

# === 3) ARCHIVOS DE SALIDA ===
CSV_FILE = "reporte_sourcing_alibaba.csv"
URLS_CACHE = "urls_encontradas.txt"     # cache de links para reanudar sin re-buscar

# === 4) OPCIONES DE SCRAPERAPI ===
SCRAPERAPI_ENDPOINT = "https://api.scraperapi.com/"
USE_RENDER = True           # ejecuta JS en la nube del proxy (recomendado para Alibaba)
USE_ULTRA_PREMIUM = False   # True solo si te bloquean mucho (gasta MUCHOS mas creditos)
COUNTRY_CODE = "us"         # geolocaliza las peticiones

# === 5) RITMO Y REINTENTOS ===
PAUSE_BETWEEN_REQUESTS = 1.5   # segundos entre peticiones
MAX_RETRIES = 3                # reintentos por peticion fallida
REQUEST_TIMEOUT = 70           # segundos (el render puede tardar)

# Campos del CSV (orden de columnas)
CAMPOS_CSV = ["titulo", "proveedor", "moq", "precio", "url"]
