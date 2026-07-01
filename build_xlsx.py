# -*- coding: utf-8 -*-
"""Genera proveedores_squishy.xlsx desde squishy_clean.csv (datos alineados
extraidos del objeto JSON de la pagina de resultados).
Orden: # reviews desc, anios verified desc, service desc, precio minimo asc.
Una URL por fila; criterios por columna.
"""
import csv, re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

SRC = r"C:\Users\Usuario\Documents\alibaba Scrapper\reporte_sourcing_alibaba.csv"
OUT = r"C:\Users\Usuario\Documents\alibaba Scrapper\proveedores_squishy.xlsx"

def fnum(s, default=0.0):
    m = re.search(r"[\d.]+", str(s).replace(",", ""))
    return float(m.group()) if m else default

rows, seen = [], set()
with open(SRC, encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        u = r.get("url", "").strip()
        if not u or u in seen:
            continue
        seen.add(u)
        rows.append({
            "url": u,
            "title": r.get("title", ""),
            "company": r.get("company", ""),
            "country": r.get("country", ""),
            "years": int(fnum(r.get("years", 0))),
            "rating": fnum(r.get("rating", 0)),
            "reviews": int(fnum(r.get("reviews", 0))),
            "service": fnum(r.get("service", 0)),
            "shipping": fnum(r.get("shipping", 0)),
            "price_raw": r.get("price", ""),
            "price_min": fnum(r.get("price", ""), default=1e9),
            "moq": r.get("moq", "").replace("Min. order:", "").strip(),
        })

# Orden pedido: reviews desc, anios desc, service desc, precio_min asc
rows.sort(key=lambda x: (-x["reviews"], -x["years"], -x["service"], x["price_min"]))

wb = Workbook(); ws = wb.active; ws.title = "Proveedores squishy"
cols = [("#", 5), ("URL", 66), ("Producto", 34), ("Proveedor", 38), ("Pais", 6),
        ("Reviews", 9), ("Anios", 7), ("Service", 8), ("Shipping", 9),
        ("Rating", 7), ("Precio USD", 12), ("MOQ", 20)]
hf = PatternFill("solid", fgColor="1F4E78"); hfont = Font(color="FFFFFF", bold=True)
for i, (name, w) in enumerate(cols, 1):
    c = ws.cell(1, i, name); c.fill = hf; c.font = hfont
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.column_dimensions[get_column_letter(i)].width = w

for idx, r in enumerate(rows, 1):
    precio = "" if r["price_min"] >= 1e9 else r["price_raw"]
    ws.append([idx, r["url"], r["title"], r["company"], r["country"],
               r["reviews"], r["years"], r["service"], r["shipping"],
               r["rating"], precio, r["moq"]])

ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{len(rows)+1}"
wb.save(OUT)
print(f"OK -> {OUT}  ({len(rows)} filas)")
print(f'\n{"REVS":<6}{"AÑOS":<6}{"SERV":<6}{"PRECIO":<11}{"MOQ":<16}EMPRESA')
for r in rows[:10]:
    p = "" if r["price_min"] >= 1e9 else r["price_raw"]
    print(f'{r["reviews"]:<6}{r["years"]:<6}{r["service"]:<6}{p:<11}{r["moq"][:15]:<16}{r["company"][:32]}')
