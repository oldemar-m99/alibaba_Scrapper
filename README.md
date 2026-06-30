# Alibaba Sourcing Tool

Herramienta de sourcing que busca productos en **Alibaba.com** a través de
**ScraperAPI** (proxy que resuelve bloqueos y CAPTCHAs en la nube) y exporta
un reporte CSV con **título, proveedor, MOQ y precio**.

Diseño **modular (SRP)**: cada archivo tiene una única responsabilidad y la
escritura del CSV es incremental (bajo uso de RAM y se puede reanudar).

## Módulos

| Archivo | Responsabilidad |
|---|---|
| `config.py` | Configuración central (API key, keyword, opciones). |
| `proxy.py` | Descargas vía ScraperAPI (red). |
| `search.py` | ETAPA 1: recolectar URLs de productos. |
| `extractor.py` | Transformar HTML → datos del producto. |
| `storage.py` | Persistencia en CSV. |
| `sourcing_tool.py` | Punto de entrada: orquesta todo. |

## Instalación

```bash
pip install requests beautifulsoup4 pandas
```

## Uso

1. Edita `config.py`: pon tu `API_KEY` de ScraperAPI y tu `KEYWORD`.
2. Ejecuta:

```bash
python sourcing_tool.py
```

3. Se genera `reporte_sourcing_alibaba.csv` (abrible en Excel).

> Empieza con `MAX_PRODUCTS = 20` para validar antes de lanzar los 1000.

---

## Diagrama de flujo (ejecución)

```mermaid
flowchart TD
    A([Inicio: python sourcing_tool.py])
    B{API_KEY valida?}
    Z1([Error: configura API_KEY en config.py])
    C["ETAPA 1: recolectar_urls (search.py)"]
    D{Existe cache urls_encontradas.txt?}
    E[Reusar URLs del cache]
    F[Loop de paginas de busqueda]
    G["fetch pagina (proxy.py - ScraperAPI)"]
    H[extraer_links_de_busqueda - BeautifulSoup]
    I{Suficientes URLs o sin resultados?}
    J[Guardar cache de URLs]
    K{Hay URLs?}
    Z2([Salir: sin resultados])
    L["ETAPA 2: etapa2_extraer (sourcing_tool.py)"]
    M["cargar_urls_ya_procesadas (storage.py)"]
    N{Para cada URL}
    O{Ya esta en el CSV?}
    P["fetch producto (proxy.py)"]
    Q{Descarga OK?}
    R["parsear_producto (extractor.py): HTML to datos"]
    S["escritor.agregar (storage.py): append + flush"]
    T([CSV listo: reporte_sourcing_alibaba.csv])

    A --> B
    B -- No --> Z1
    B -- Si --> C
    C --> D
    D -- Si --> E
    D -- No --> F
    F --> G
    G --> H
    H --> I
    I -- No --> F
    I -- Si --> J
    E --> K
    J --> K
    K -- No --> Z2
    K -- Si --> L
    L --> M
    M --> N
    N --> O
    O -- Si --> N
    O -- No --> P
    P --> Q
    Q -- No --> N
    Q -- Si --> R
    R --> S
    S --> N
    N -- Fin del loop --> T

    classDef err fill:#ffd6d6,stroke:#c00;
    classDef ok fill:#d6ffd6,stroke:#0a0;
    class Z1,Z2 err;
    class T ok;
```

## Dependencias entre módulos

```mermaid
flowchart LR
    MAIN["sourcing_tool.py (orquestador)"]
    CFG["config.py - configuracion"]
    PRX["proxy.py - red / ScraperAPI"]
    SRCH["search.py - ETAPA 1: URLs"]
    EXT["extractor.py - HTML to datos"]
    STO["storage.py - CSV"]

    MAIN --> SRCH
    MAIN --> EXT
    MAIN --> STO
    MAIN --> PRX
    SRCH --> PRX
    SRCH --> CFG
    PRX --> CFG
    STO --> CFG
    MAIN --> CFG

    style CFG fill:#fff3c4,stroke:#caa800
    style MAIN fill:#cfe3ff,stroke:#3678d8
```

## Aviso sobre créditos

Alibaba requiere `render=true` (JS), por lo que cada producto puede costar
~10 créditos en ScraperAPI. 1000 productos ≈ 10 000 créditos (más que el plan
gratuito de 5000). Haz pruebas pequeñas y revisa el consumo en tu panel.
