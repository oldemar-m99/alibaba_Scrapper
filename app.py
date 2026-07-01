# -*- coding: utf-8 -*-
"""
app.py — servidor Flask para la UI de sourcing.
  /                -> sirve index.html (genera si no existe)
  /api/keywords    -> descubre keywords en vivo para un ?seed=... (ScraperAPI)

Uso:
    python app.py         ->  http://127.0.0.1:8000
"""
import os
import json
from flask import Flask, jsonify, request, send_file

import amz_keywords
import amz_bridge

app = Flask(__name__)
BASE = os.path.dirname(__file__)
HTML = os.path.join(BASE, "index.html")
CACHE = os.path.join(BASE, "keywords_cache.json")


def _load_cache():
    if os.path.exists(CACHE):
        try:
            with open(CACHE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_cache(c):
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=1)


@app.route("/")
def index():
    if not os.path.exists(HTML):
        import build_html  # genera index.html
    return send_file(HTML)


@app.route("/api/keywords")
def api_keywords():
    seed = (request.args.get("seed") or "").strip()
    if not seed:
        return jsonify({"error": "falta el parametro seed"}), 400
    force = request.args.get("force") == "1"   # ?force=1 recalcula ignorando cache
    key = seed.lower()

    cache = _load_cache()
    if not force and key in cache:
        filas = cache[key]
        cands = amz_bridge.generar_candidatos(filas)   # Fase 1: gratis, se recalcula
        return jsonify({"seed": seed, "count": len(filas), "keywords": filas,
                        "candidatos": cands, "cached": True})

    try:
        filas = amz_keywords.discover(seed)
        cache[key] = filas
        _save_cache(cache)
        cands = amz_bridge.generar_candidatos(filas)
        return jsonify({"seed": seed, "count": len(filas), "keywords": filas,
                        "candidatos": cands, "cached": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Servidor en http://127.0.0.1:8000  (Ctrl+C para detener)")
    app.run(host="127.0.0.1", port=8000, debug=False)
