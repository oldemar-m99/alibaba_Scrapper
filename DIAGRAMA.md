# Diagrama de flujo — Sourcing Tool (arquitectura modular SRP)

## 1) Flujo de ejecución (qué pasa al correr `python sourcing_tool.py`)

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

## 2) Dependencias entre modulos (quien usa a quien)

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

> Nota: `extractor.py` NO depende de nada propio (solo de BeautifulSoup).
> Por eso es el modulo mas facil de probar de forma aislada.
