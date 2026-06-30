# -*- coding: utf-8 -*-
"""
extractor.py
------------
Responsabilidad UNICA: convertir el HTML de una pagina de producto en un
diccionario de datos (titulo, proveedor, moq, precio, url).
No hace red ni escribe archivos: solo transforma HTML -> datos.
"""

import re
from bs4 import BeautifulSoup


def _texto(soup, selectores):
    """Devuelve el texto del primer selector que tenga contenido."""
    for sel in selectores:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return ""


def parsear_producto(html, url):
    soup = BeautifulSoup(html, "html.parser")
    datos = {"titulo": "", "proveedor": "", "moq": "", "precio": "", "url": url}

    # --- Titulo ---
    datos["titulo"] = _texto(soup, [
        "h1.product-title", "h1[class*='title']", "h1", "div[class*='product-title']",
    ])
    if not datos["titulo"]:
        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            datos["titulo"] = og["content"].strip()

    # --- Proveedor ---
    datos["proveedor"] = _texto(soup, [
        "a[class*='company-name']", "div[class*='company-name']",
        "a[class*='supplier']", "span[class*='company']",
    ])

    # --- Precio ---
    datos["precio"] = _texto(soup, [
        "div[class*='price'] span", "span[class*='price']", "div[class*='price']",
    ])

    # --- MOQ (Minimum Order Quantity) ---
    texto_pagina = soup.get_text(" ", strip=True)
    m = re.search(
        r"(\d[\d,]*)\s*(?:pieces?|pcs|sets?|units?|unidades|piezas)\b.*?min",
        texto_pagina, re.I,
    )
    if not m:
        m = re.search(
            r"min(?:imum)?\.?\s*order[^0-9]{0,20}(\d[\d,]*\s*\w+)",
            texto_pagina, re.I,
        )
    if m:
        datos["moq"] = m.group(1) if m.lastindex else m.group(0)

    # --- Respaldo: JSON embebido en <script> ---
    if not datos["proveedor"] or not datos["titulo"]:
        for script in soup.find_all("script"):
            txt = script.string or ""
            if "companyName" in txt or "minOrderQuantity" in txt:
                cm = re.search(r'"companyName"\s*:\s*"([^"]+)"', txt)
                if cm and not datos["proveedor"]:
                    datos["proveedor"] = cm.group(1)
                mm = re.search(r'"minOrderQuantity"\s*:\s*"?([^",}]+)', txt)
                if mm and not datos["moq"]:
                    datos["moq"] = mm.group(1).strip()
                tm = re.search(r'"subject"\s*:\s*"([^"]+)"', txt)
                if tm and not datos["titulo"]:
                    datos["titulo"] = tm.group(1)
                break

    return datos
