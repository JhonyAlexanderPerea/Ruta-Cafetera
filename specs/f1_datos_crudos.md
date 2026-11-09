# Spec: F1 · Datos crudos (red vial, catálogo y pares de medición)

**Autor:** <nombre> · **Revisor:** <nombre distinto del autor> · **Estado:** borrador

## Objetivo
Dejar en `data/raw/` los datos de entrada del proyecto, sin transformarlos: la red vial del Quindío y las cuatro redes por radio alrededor de la plaza de Bolívar (descargadas con OSMnx), el catálogo de al menos 40 lugares con coordenadas verificadas, y los 20 pares de medición de Dijkstra. Todo con la evidencia necesaria para reproducirlo (fecha, versión, conteos y hash).

## Entradas y salidas
- **Entrada:**
  - Consulta a OpenStreetMap: `"Quindío, Colombia"` con `network_type="drive"`, y `graph_from_point` con centro en la plaza de Bolívar (Armenia) y radios de 2, 5, 10 y 20 km.
  - `catalogo_semilla.csv`: nombres, municipio, categoría y texto de consulta de cada lugar, armado a mano por el grupo.
  - Fuentes de la duración de las visitas (páginas oficiales de cada atractivo, guías o un criterio propio escrito).
- **Salida:**
  - 5 grafos en GraphML (`quindio`, `radio_2km`, `radio_5km`, `radio_10km`, `radio_20km`), cada uno con su archivo de metadatos.
  - `catalogo.csv` con todos los lugares verificados.
  - `pares_dijkstra.csv` con 20 pares origen-destino, 10 de ellos marcados para Dijkstra lineal.
- **Archivos que lee / escribe:**
  - Lee: `data/raw/catalogo_semilla.csv`, `data/raw/catalogo.csv`.
  - Escribe: `data/raw/*.graphml`, `data/raw/*.meta.json`, `data/raw/catalogo.csv`, `data/raw/pares_dijkstra.csv`, `data/raw/cache/` (caché de OSMnx, no se versiona).
  - Código: `src/rutas/data/descarga.py`, `catalogo_borrador.py`, `catalogo.py`, `pares.py`.

## Comportamiento esperado
**Descarga de redes**
- Cada red se guarda tal como la entrega OSMnx: aquí no se calculan pesos ni se filtra la componente fuerte (eso es la Fase 2).
- Cada GraphML va acompañado de `<nombre>.meta.json` con: consulta, `network_type`, fecha de descarga, versión de OSMnx, número de nodos y aristas, tamaño en MB, segundos de descarga y SHA-256.
- Comportamiento por defecto que se documenta en el informe: `graph_from_point` usa `dist_type="bbox"` (el radio es la mitad del lado de un cuadrado, no un círculo), y OSMnx conserva solo la componente débilmente conexa más grande (`retain_all=False`).
- La plaza de Bolívar se verifica en un mapa antes de descargar. Si la coordenada está mal, se corrige y se vuelve a descargar.
- Si una descarga falla, se reintenta (el caché evita repetir lo ya descargado). Si la del departamento no se logra tras varios intentos, se solicita el GraphML al docente.

**Catálogo**
- Mínimos por categoría: 12 cabeceras (una por municipio, ubicadas en su plaza principal), 15 atractivos, 8 fincas u hoteles rurales y 5 centros de acopio o trilladoras (≥ 40 lugares).
- Columnas obligatorias: `id`, `nombre`, `municipio`, `categoria`, `lat`, `lon`, `duracion_visita_min`, `fuente_duracion`, `fuente_coord`, `verificado`.
- Las coordenadas que propone el geocodificador son un borrador. Cada fila pasa a `verificado=True` solo cuando una persona la comprobó en un mapa y anotó cómo en `fuente_coord`.
- Cada atractivo tiene `duracion_visita_min > 0` y una fuente o criterio en `fuente_duracion`.
- Un lugar cuya ubicación no se pueda confirmar se reemplaza por otro.

**Pares de medición**
- Se eligen 20 pares con semilla fija 42, entre lugares a una distancia en línea recta ≤ 25 km (criterio de "cercanos", se justifica en el informe).
- La orientación de cada par se sortea, porque la red es dirigida.
- Los primeros 10 pares llevan `usa_lineal=True`. Entre esos 10 debe haber pares del mismo municipio y de municipios vecinos.

**Entradas inválidas**
- Catálogo con ids o nombres repetidos, categorías incompletas, coordenadas ausentes o fuera de la caja del Quindío, o filas sin verificar: el validador devuelve la lista de errores y termina con código 1.
- Consulta de geocodificación sin resultado: se deja la coordenada vacía, se imprime el aviso y se completa a mano.

## Complejidad esperada (con fuente)
Esta fase no implementa algoritmos de los requerimientos, así que no hay una complejidad que citar.
- **Descarga:** el costo lo domina la red (E/S), no el cómputo; el tiempo se registra como dato informativo, no entra en el protocolo de medición.
- **Validador del catálogo:** tiempo O(n), memoria O(n), con n = número de lugares.
- **Selección de pares:** tiempo O(n²), porque examina todos los pares de lugares, con n ≈ 40; memoria O(n²) en el peor caso.
- **Recurrencia:** no aplica.

## Casos de prueba
1. **Caso pequeño resuelto a mano:** un catálogo sintético con exactamente 12 + 15 + 8 + 5 lugares, coordenadas válidas y fuentes completas es aceptado por el validador, sin errores (`test_catalogo_valido`).
2. **Casos límite:**
   - Quitar la categoría `acopio` produce un error que la menciona.
   - Una latitud de 10.0 produce el error de coordenadas fuera del Quindío.
   - Un atractivo sin `fuente_duracion` produce el error de duración o fuente ausente.
   - Un id duplicado produce el error de ids repetidos.
   - Un catálogo con menos de 40 lugares es rechazado.
3. **Verificación contra otra fuente:**
   - Los nodos y aristas de cada `.meta.json` coinciden con los que se obtienen al cargar el GraphML con `ox.load_graphml`.
   - El SHA-256 de cada archivo, recalculado por otra persona tras bajarlo del Release, coincide con el del `.meta.json`.
   - Las coordenadas de las cabeceras y de una muestra del resto se comprueban en un mapa de forma independiente por el revisor.
   - Al ejecutar `pares.py` dos veces con la misma semilla se obtiene el mismo archivo.

## Cómo se mide
No hay mediciones de rendimiento en esta fase. Lo que se registra es información de reproducibilidad:
- Por cada red: nodos (V), aristas (E), tamaño en MB, segundos de descarga (informativo), fecha y versión de OSMnx.
- Semilla de los pares: 42 (definida en `config.py`).
- Máquina de la descarga: procesador, RAM, sistema operativo y versión de Python, anotados en el README.

Los conteos V y E de las cuatro redes por radio y de la red completa serán la base de la tabla "Red descargada" del requerimiento 1 (Fase 2).

## Criterio de terminado
- Los 5 GraphML existen con su `.meta.json` (fecha, versión, V, E y SHA-256), y están publicados en el Release `data-v1`.
- La plaza de Bolívar fue verificada en un mapa.
-  `make validar-catalogo` termina en verde y todas las filas tienen `verificado=True`.
-  Todos los atractivos tienen duración y fuente.
-  `pares_dijkstra.csv` tiene 20 pares, 10 con `usa_lineal=True`, y la mezcla pedida entre esos 10.
-  `make test` y CI en verde.
-  El README registra fecha de descarga, versión de OSMnx, V y E de cada red, y la máquina.
-  Milestone `Fase 1` cerrado y tag `fase-1-datos` creado.