# Diagrama de flujo — Sourcing Tool (arquitectura modular SRP)

## 1) Flujo de ejecución (qué pasa al correr `python sourcing_tool.py`)

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

## 2) Dependencias entre modulos (quien usa a quien)

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

> Nota: `extractor.py` NO depende de nada propio (solo de BeautifulSoup).
> Por eso es el modulo mas facil de probar de forma aislada.
