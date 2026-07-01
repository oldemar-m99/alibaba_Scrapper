# -*- coding: utf-8 -*-
"""
search.py
---------
Construye la URL de busqueda filtrada (interfaz clasica de Alibaba) con los
filtros de config.FILTROS. Deja el pageSize por defecto para no saltar
productos al paginar.
"""

from urllib.parse import quote_plus
import config

BASE = "https://www.alibaba.com/trade/search"


def construir_url(keyword, page):
    params = {
        "fsb": "y",
        "IndexArea": "product_en",
        "keywords": keyword,
        "originKeywords": keyword,
        "tab": "all",
        "viewtype": "G",
        "page": str(page),
    }
    params.update(config.FILTROS)
    q = "&".join(f"{k}={quote_plus(str(v))}" for k, v in params.items())
    return f"{BASE}?{q}"
