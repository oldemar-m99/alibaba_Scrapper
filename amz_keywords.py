# -*- coding: utf-8 -*-
"""
amz_keywords.py
---------------
Descubre keywords para un producto usando Amazon via ScraperAPI:
  1) AUTOCOMPLETE: sugerencias reales (lo que la gente teclea) -> demanda
  2) SEARCH: n-gramas frecuentes de los titulos de resultados  -> terminos usados
Salida: keywords_amazon.csv (keyword, origen, score)
"""
import requests, csv, re, time
from collections import Counter
import config

SEED = "squishy toys"            # semilla del producto
EXPANDIR = 12                    # cuantas sugerencias de nivel 1 expandir
ALFABETO = False                 # True = tambien "seed a".."seed z" (mas keywords, +26 req)

AC = "https://completion.amazon.com/api/2017/suggestions"
SEARCH = "https://api.scraperapi.com/structured/amazon/search"
STOP = set("for the and with of a to in on kids child your set pack pcs pc toy toys "
           "new hot 2024 2025 2026 gift gifts party favors bulk mini soft cute".split())


def sugerencias(prefix):
    qp = {"limit": 11, "prefix": prefix, "alias": "aps", "site-variant": "desktop",
          "mid": "ATVPDKIKX0DER", "fresh": 0, "b2b": 0, "suggestion-type": "KEYWORD"}
    target = AC + "?" + "&".join(f"{k}={requests.utils.quote(str(v))}" for k, v in qp.items())
    try:
        r = requests.get("https://api.scraperapi.com/",
                         params={"api_key": config.API_KEY, "url": target}, timeout=60)
        return [s.get("value", "").strip() for s in r.json().get("suggestions", []) if s.get("value")]
    except Exception as e:
        print("  [aviso] autocomplete fallo:", e); return []


def titulos(query):
    try:
        r = requests.get(SEARCH, params={"api_key": config.API_KEY, "query": query, "country": "us"}, timeout=70)
        return [x.get("name", "") for x in r.json().get("results", []) if x.get("name")]
    except Exception as e:
        print("  [aviso] search fallo:", e); return []


def ngramas(titles, n):
    c = Counter()
    for t in titles:
        words = [w for w in re.findall(r"[a-z0-9]+", t.lower()) if w not in STOP and len(w) > 2]
        for i in range(len(words) - n + 1):
            c[" ".join(words[i:i + n])] += 1
    return c


def discover(seed, expandir=EXPANDIR, alfabeto=ALFABETO):
    """Descubre keywords para 'seed'. Devuelve lista de dicts ordenada por score:
       {keyword, origen, autocomplete, titulo, score}. Reutilizable (Flask/CLI)."""
    kw = {}  # keyword -> {'ac':.., 'title':..}
    nivel1 = sugerencias(seed)
    for s in nivel1:
        kw.setdefault(s, {"ac": 0, "title": 0})["ac"] += 3   # nivel 1 pesa mas

    prefijos = nivel1[:expandir]
    if alfabeto:
        prefijos += [f"{seed} {ch}" for ch in "abcdefghijklmnopqrstuvwxyz"]
    for p in prefijos:
        for s in sugerencias(p):
            kw.setdefault(s, {"ac": 0, "title": 0})["ac"] += 1
        time.sleep(0.3)

    tt = titulos(seed)
    for n in (2, 3):
        for frase, veces in ngramas(tt, n).items():
            if veces >= 3:
                kw.setdefault(frase, {"ac": 0, "title": 0})["title"] += veces

    filas = []
    for k, v in kw.items():
        score = v["ac"] * 5 + v["title"]        # autocomplete pesa mas (demanda)
        origen = (("AC" if v["ac"] else "") + ("+TIT" if v["title"] else "")).strip("+")
        filas.append({"keyword": k, "origen": origen, "autocomplete": v["ac"],
                      "titulo": v["title"], "score": score})
    filas.sort(key=lambda x: -x["score"])
    return filas


def main():
    print(f"[DISCOVER] semilla '{SEED}'...")
    filas = discover(SEED)
    with open("keywords_amazon.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["keyword", "origen", "autocomplete", "titulo", "score"])
        for r in filas:
            w.writerow([r["keyword"], r["origen"], r["autocomplete"], r["titulo"], r["score"]])
    print(f"[LISTO] {len(filas)} keywords -> keywords_amazon.csv\n")
    print(f"{'SCORE':<7}{'ORIGEN':<8}KEYWORD")
    for r in filas[:25]:
        print(f"{r['score']:<7}{r['origen']:<8}{r['keyword']}")


if __name__ == "__main__":
    main()
