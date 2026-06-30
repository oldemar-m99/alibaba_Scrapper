# -*- coding: utf-8 -*-
"""
storage.py
----------
Responsabilidad UNICA: persistencia en CSV. Sabe leer que URLs ya se
procesaron (para reanudar) y agregar filas nuevas de forma incremental.
"""

import os
import csv

import config


def cargar_urls_ya_procesadas():
    """Devuelve un set con las URLs que ya estan en el CSV (para no repetir)."""
    if not os.path.exists(config.CSV_FILE):
        return set()
    procesadas = set()
    with open(config.CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("url"):
                procesadas.add(row["url"])
    return procesadas


class EscritorCSV:
    """Context manager que abre el CSV en modo 'append' y escribe encabezado
    si el archivo es nuevo. Uso:

        with EscritorCSV() as escritor:
            escritor.agregar(datos)
    """

    def __init__(self):
        self._f = None
        self._writer = None

    def __enter__(self):
        archivo_existe = os.path.exists(config.CSV_FILE)
        self._f = open(config.CSV_FILE, "a", encoding="utf-8-sig", newline="")
        self._writer = csv.DictWriter(self._f, fieldnames=config.CAMPOS_CSV)
        if not archivo_existe:
            self._writer.writeheader()
        return self

    def agregar(self, datos):
        self._writer.writerow(datos)
        self._f.flush()  # escribe a disco al instante (no se pierde si se corta)

    def __exit__(self, *exc):
        if self._f:
            self._f.close()
