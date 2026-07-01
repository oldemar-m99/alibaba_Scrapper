# -*- coding: utf-8 -*-
"""
extractor.py
------------
Responsabilidad UNICA: convertir el HTML de una pagina de resultados en una
lista de productos (dicts), leyendo el objeto de datos '__page__data_sse10'
que Alibaba incrusta en el HTML (mismo objeto que en el navegador).

No hace red ni escribe archivos: solo transforma HTML -> datos.
"""

import re
import json

ANCLA = "__page__data_sse"


def _limpiar(s):
    if s is None:
        return ""
    s = str(s)
    s = re.sub(r"<[^>]+>", "", s)          # quitar tags HTML (<strong> etc.)
    s = s.replace("\\/", "/")
    return re.sub(r"\s+", " ", s).strip()


def _texto(v):
    """Devuelve texto util de un valor que puede ser str, num o dict."""
    if v is None:
        return ""
    if isinstance(v, dict):
        for k in ("text", "value", "display", "name"):
            if v.get(k):
                return _limpiar(v[k])
        return ""
    return _limpiar(v)


def _es_lista_ofertas(lst):
    return (isinstance(lst, list) and lst and isinstance(lst[0], dict) and
            ("productUrl" in lst[0] or "productId" in lst[0] or "detailUrl" in lst[0]) and
            ("companyName" in lst[0] or "reviewScore" in lst[0] or "originalMinPrice" in lst[0]))


def _todas_las_listas(obj, acc):
    """Recolecta todas las listas de ofertas del objeto."""
    if isinstance(obj, list):
        if _es_lista_ofertas(obj):
            acc.append(obj)
        for it in obj:
            _todas_las_listas(it, acc)
    elif isinstance(obj, dict):
        for v in obj.values():
            _todas_las_listas(v, acc)


def _buscar_offers(obj):
    """Devuelve la lista de ofertas MAS GRANDE (los resultados principales,
    no los mini-booth de 7 items)."""
    acc = []
    _todas_las_listas(obj, acc)
    return max(acc, key=len) if acc else None


def _extraer_objeto_datos(html):
    """Recorre todos los bloques '__page__data_sse' del HTML y devuelve la
    lista de ofertas mas grande encontrada en cualquiera de ellos."""
    dec = json.JSONDecoder()
    mejor = None
    for m in re.finditer(ANCLA, html):
        i = html.find("{", m.end())
        if i == -1:
            continue
        try:
            obj, _ = dec.raw_decode(html, i)
        except (json.JSONDecodeError, ValueError):
            continue
        offers = _buscar_offers(obj)
        if offers and (mejor is None or len(offers) > len(mejor)):
            mejor = offers
    return mejor


def _precio(v):
    s = _texto(v)
    for junk in ("PAB", " ", "US$", "$"):
        s = s.replace(junk, "")
    return s.strip()


def parsear_resultados(html):
    """HTML de una pagina de resultados -> lista de dicts (una por producto)."""
    offers = _extraer_objeto_datos(html)
    if not offers:
        return []

    filas, vistos = [], set()
    for o in offers:
        if not isinstance(o, dict):
            continue
        # URL: layout nuevo (productUrl) o viejo (detailUrl)
        url = o.get("productUrl") or o.get("detailUrl") or ""
        if url.startswith("//"):
            url = "https:" + url
        url = url.split("?")[0]
        if not url or url in vistos:
            continue
        vistos.add(url)
        # MOQ: nuevo (moq/moqV2) o viejo (minOrderQuality + minOrderUnit)
        moq = _texto(o.get("moq")) or _texto(o.get("moqV2"))
        if not moq and o.get("minOrderQuality"):
            moq = f"{_texto(o.get('minOrderQuality'))} {_texto(o.get('minOrderUnit'))}".strip()
        # Imagen principal
        img = o.get("mainImage") or o.get("imageUrl") or ""
        if isinstance(img, dict):
            img = img.get("url") or img.get("imgUrl") or ""
        img = str(img).replace("\\/", "/")
        if img.startswith("//"):
            img = "https:" + img
        filas.append({
            "url": url,
            "title": _limpiar(o.get("title"))[:120],
            "company": _limpiar(o.get("companyName")),
            "country": _texto(o.get("countryCode")),
            "years": re.sub(r"\D", "", str(o.get("goldSupplierYears") or o.get("goldYears") or "")),
            "rating": _texto(o.get("reviewScore")),
            "reviews": _texto(o.get("reviewCount")),
            "service": _texto(o.get("supplierServiceScore")),
            "shipping": _texto(o.get("shippingScore")),
            "price": _precio(o.get("price") or o.get("originalMinPrice")),
            "moq": moq,
            "image": img,
        })
    return filas
