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
    A([Inicio: python sourcing_tool.py]) --> B{API_KEY valida?}
    B -- No --> Z1([Error: configura API_KEY en config.py]):::err
    B -- Si --> C[ETAPA 1: recolectar_urls<br/><i>search.py</i>]

    C --> D{Existe cache<br/>urls_encontradas.txt?}
    D -- Si --> E[Reusar URLs del cache]
    D -- No --> F[Loop de paginas de busqueda]
    F --> G[fetch pagina<br/><i>proxy.py - ScraperAPI</i>]
    G --> H[extraer_links_de_busqueda<br/>BeautifulSoup]
    H --> I{Suficientes URLs<br/>o sin resultados?}
    I -- No --> F
    I -- Si --> J[Guardar cache de URLs]
    E --> K
    J --> K{Hay URLs?}
    K -- No --> Z2([Salir: sin resultados]):::err

    K -- Si --> L[ETAPA 2: etapa2_extraer<br/><i>sourcing_tool.py</i>]
    L --> M[cargar_urls_ya_procesadas<br/><i>storage.py</i> - reanudar]
    M --> N{Para cada URL}
    N --> O{Ya esta<br/>en el CSV?}
    O -- Si --> N
    O -- No --> P[fetch producto<br/><i>proxy.py</i>]
    P --> Q{Descarga OK?}
    Q -- No --> N
    Q -- Si --> R[parsear_producto<br/><i>extractor.py</i><br/>HTML to datos]
    R --> S[escritor.agregar<br/><i>storage.py</i> - append + flush]
    S --> N
    N -- Fin del loop --> T([CSV listo:<br/>reporte_sourcing_alibaba.csv]):::ok

    classDef err fill:#ffd6d6,stroke:#c00;
    classDef ok fill:#d6ffd6,stroke:#0a0;
```

## Dependencias entre módulos

```mermaid
flowchart LR
    MAIN[sourcing_tool.py<br/><b>orquestador</b>]
    CFG[config.py<br/>configuracion]
    PRX[proxy.py<br/>red / ScraperAPI]
    SRCH[search.py<br/>ETAPA 1: URLs]
    EXT[extractor.py<br/>HTML to datos]
    STO[storage.py<br/>CSV]

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
