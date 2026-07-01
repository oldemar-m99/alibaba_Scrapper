# -*- coding: utf-8 -*-
"""
amz_bridge.py — FASE 1 del bridge Amazon -> Alibaba.
Convierte keywords de consumidor (Amazon) en CANDIDATOS de busqueda para
Alibaba, SIN buscar todavia (gratis):
  1) quita modificadores de intencion (for kids, bulk, cheap, gift, 2026...)
  2) agrupa keywords que se reducen al mismo candidato (suma su demanda/score)
  3) clasifica el tipo (variante / adyacente / generico)
  4) inyecta traducciones de fabrica (material/funcion)

La FASE 2 (medir relevancia buscando en Alibaba) NO se hace aqui.
"""
import re

# Palabras de INTENCION del comprador (no ayudan como termino de fabrica)
MODIFICADORES = {
    "for", "kids", "kid", "adults", "adult", "children", "child", "boys", "girls",
    "bulk", "cheap", "wholesale", "price", "gift", "gifts", "giveaway",
    "party", "favors", "favor", "pack", "packs", "set", "sets", "box", "boxes",
    "mystery", "blind", "new", "hot", "best", "top", "selling", "trending",
    "with", "and", "the", "your", "own", "custom",
    "2023", "2024", "2025", "2026", "toys", "toy", "assorted", "mixed", "random",
    "pcs", "pc", "pieces", "piece", "count", "cute", "soft", "mini",
}

VARIANTE = {"mochi", "dumpling", "slow", "rising", "glitter", "butter", "needoh",
            "taba", "steamer", "jumbo", "bun", "bread", "galaxy", "kawaii",
            "scented", "marine", "animal", "food", "cheese", "fruit", "dice", "seal"}
ADYACENTE = {"stress", "fidget", "sensory", "anxiety", "ball", "balls", "cube",
             "squeeze", "relief", "decompression", "sludge", "slime"}

# Marcas/estilos de Amazon -> equivalente generico de fabrica en Alibaba
MARCAS = {
    "needoh": "stress ball", "taba": "silicone squishy kit",
    "dolphineshow": "", "kawaii": "", "brinquedo": "",
}
# Vocabulario consumidor -> fabrica (se aplica sobre la frase)
REEMPLAZOS = [
    ("stress relief", "anti stress"), ("stress balls", "anti stress ball"),
    ("stress ball", "anti stress ball"), ("stress cube", "squeeze cube"),
    ("squishy stress", "anti stress squishy"),
]


def traducir(cand):
    """Convierte un candidato (termino de consumidor) a un termino mas 'de
    fabrica' para Alibaba: reemplaza marcas, ajusta vocabulario, especifica lo
    demasiado generico. Heuristico (sugerencia)."""
    toks = [MARCAS.get(w, w) for w in cand.split()]
    t = " ".join(w for w in toks if w).strip()
    for a, b in REEMPLAZOS:
        if a in t:
            t = t.replace(a, b)
    if t == "squishy":                       # demasiado generico
        t = "pu foam slow rising squishy"
    if t == "slow rising":
        t = "slow rising squishy"
    t = " ".join(dict.fromkeys(t.split()))   # quita palabras repetidas conservando orden
    return t.strip() or cand


# Traducciones de fabrica (mi conocimiento de dominio) que se agregan siempre
FABRICA = [
    ("pu foam slow rising squishy", "variante", "traduccion de fabrica (material PU)"),
    ("tpr squeeze stress toy", "adyacente", "traduccion de fabrica (material TPR)"),
    ("anti stress ball", "adyacente", "traduccion de fabrica (funcion)"),
    ("mochi squishy", "variante", "termino de fabrica comun"),
]


def _tokens(kw):
    toks = re.findall(r"[a-z0-9]+", kw.lower())
    return [t for t in toks if t not in MODIFICADORES and len(t) > 2]


def _tipo(toks):
    s = set(toks)
    if s & VARIANTE:
        return "variante"
    if s & ADYACENTE:
        return "adyacente"
    return "generico"


def generar_candidatos(keywords, top=30):
    """keywords: lista de dicts {kw|keyword, score}. Devuelve candidatos ordenados."""
    grupos = {}
    for k in keywords:
        texto = k.get("kw") or k.get("keyword") or ""
        toks = _tokens(texto)
        if not toks:
            continue
        cand = " ".join(toks)
        g = grupos.setdefault(cand, {"score": 0, "ejemplos": [], "tipo": _tipo(toks)})
        g["score"] += int(k.get("score", 0) or 0)
        if texto != cand and len(g["ejemplos"]) < 3:
            g["ejemplos"].append(texto)

    filas = [{"candidato": c, "traduccion": traducir(c), "score": v["score"],
              "tipo": v["tipo"], "ejemplos": v["ejemplos"], "origen": "auto (sin modificadores)"}
             for c, v in grupos.items()]

    existentes = {f["candidato"] for f in filas}
    for c, tipo, orig in FABRICA:
        if c not in existentes:
            filas.append({"candidato": c, "traduccion": c, "score": 0, "tipo": tipo,
                          "ejemplos": [], "origen": orig})

    filas.sort(key=lambda x: -x["score"])
    return filas[:top]
