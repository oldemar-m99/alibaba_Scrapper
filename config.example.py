# -*- coding: utf-8 -*-
"""
config.py
---------
Configuracion central de la herramienta. EDITA AQUI todo lo ajustable.
"""

# === 1) CREDENCIALES Y BUSQUEDA  (EDITA ESTO) ===
API_KEY = "TU_API_KEY_DE_SCRAPERAPI"   # tu API Key de ScraperAPI
KEYWORD = "squishy toys"                         # producto a investigar

# === 2) FILTROS DE ALIBABA (interfaz clasica, se aplican en la URL) ===
# Estos se descubrieron marcandolos en el panel izquierdo de Alibaba.
FILTROS = {
    "assessmentCompany": "true",   # Verified/Assessed Supplier
    "ta": "y",                     # Trade Assurance
    "productAuthTag": "CPC",       # Certificacion CPC (juguetes infantiles US)
    "reviewScore": "4",            # rating minimo 4
    "sortType": "prodSold180",     # ordenar por mas vendidos (180 dias)
}
# NO usamos pageSize: dejamos el default (~48/pag) para que la paginacion
# no se salte productos (el SSR solo hornea ~63 aunque pidas 100).

# === 3) ALCANCE ===
MAX_PAGES = 1              # paginas a traer (1 = prueba). ~48 productos por pagina
START_PAGE = 1

# === 4) ARCHIVOS DE SALIDA ===
CSV_FILE = "reporte_sourcing_alibaba.csv"

# === 5) OPCIONES DE SCRAPERAPI ===
SCRAPERAPI_ENDPOINT = "https://api.scraperapi.com/"
USE_RENDER = False          # NO render: el JSON ya viene incrustado en el HTML
COUNTRY_CODE = "us"         # visitante US -> precios USD, vista estandar Amazon
USE_PREMIUM = True          # Alibaba es dominio protegido; premium es necesario
USE_ULTRA_PREMIUM = False   # tu plan gratis NO permite ultra (da 403)

# === 6) RITMO Y REINTENTOS ===
PAUSE_BETWEEN_REQUESTS = 1.5   # segundos entre peticiones
MAX_RETRIES = 3                # reintentos por error de red/500
MAX_CAPTCHA_RETRIES = 12       # reintentos si vuelve pagina de CAPTCHA
REQUEST_TIMEOUT = 70           # segundos

# Campos del CSV (orden de columnas) - alineados con el objeto offers
CAMPOS_CSV = ["url", "title", "company", "country", "years", "rating",
              "reviews", "service", "shipping", "price", "moq"]
