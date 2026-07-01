# Diagrama de flujo — Sourcing Tool (ScraperAPI + `__page__data_sse10`)

## 1) Flujo de ejecución

```mermaid
flowchart TD
    A([Inicio: python sourcing_tool.py])
    B{API_KEY valida?}
    Z1([Error: configura API_KEY en config.py])
    C["Para cada pagina 1..MAX_PAGES"]
    D["construir_url (search.py): URL filtrada + page=N"]
    E["fetch (proxy.py): ScraperAPI premium, sin render"]
    F{Pagina buena o CAPTCHA?}
    G["reintentar (hasta MAX_CAPTCHA_RETRIES)"]
    H["parsear_resultados (extractor.py)"]
    I["Localiza bloque __page__data_sse10 en el HTML"]
    J["JSON.parse -> offerResultData.offers[]"]
    K["Mapear cada offer -> fila (url, proveedor, MOQ...)"]
    L["storage.py: append incremental al CSV"]
    M([reporte_sourcing_alibaba.csv])
    N["build_xlsx.py: ordenar + Excel"]
    O([proveedores_squishy.xlsx])

    A --> B
    B -- No --> Z1
    B -- Si --> C
    C --> D
    D --> E
    E --> F
    F -- CAPTCHA --> G
    G --> E
    F -- Buena --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> C
    C -- Fin --> M
    M --> N
    N --> O

    classDef err fill:#ffd6d6,stroke:#c00;
    classDef ok fill:#d6ffd6,stroke:#0a0;
    class Z1 err;
    class M,O ok;
```

## 2) De dónde salen los datos (capas de la página)

```mermaid
flowchart TD
    SRV["Servidor Alibaba"]
    HTML["HTML crudo (lo que recibe ScraperAPI)"]
    SSE["Bloque de texto: __page__data_sse10 = { ... }"]
    OBJ["_offer_list.offerResultData.offers[]"]
    OFF["offer[i] = objeto cerrado por producto"]
    FILA["fila del CSV (alineada)"]

    SRV --> HTML
    HTML --> SSE
    SSE -->|JSON.parse| OBJ
    OBJ --> OFF
    OFF -->|url, company, years, reviews, moq, price| FILA

    style SSE fill:#fff3c4,stroke:#caa800
    style OFF fill:#cfe3ff,stroke:#3678d8
```

> El objeto viene **incrustado como texto** en el HTML, así que ScraperAPI lo
> obtiene **sin renderizar JavaScript**. Cada `offer` es un objeto completo →
> alineación exacta (no se cruzan URL / proveedor / métricas).

## 3) Dependencias entre módulos

```mermaid
flowchart LR
    MAIN["sourcing_tool.py (orquestador)"]
    CFG["config.py - keyword + filtros + API"]
    SRCH["search.py - URL filtrada"]
    PRX["proxy.py - ScraperAPI + anti-CAPTCHA"]
    EXT["extractor.py - __page__data_sse10"]
    STO["storage.py - CSV"]
    XLS["build_xlsx.py - reporte Excel"]

    MAIN --> SRCH
    MAIN --> PRX
    MAIN --> EXT
    MAIN --> STO
    SRCH --> CFG
    PRX --> CFG
    STO --> CFG
    MAIN --> CFG
    XLS --> STO

    style CFG fill:#fff3c4,stroke:#caa800
    style MAIN fill:#cfe3ff,stroke:#3678d8
```
