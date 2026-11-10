# Verificación de coordenadas (PARADA 1) — borrador

Estado: **pendiente de revisión humana**. Nada de esto marca `verificado=True`; eso lo hace una persona al revisar cada punto en el mapa.

## 1. Cabeceras: pin de Google vs. plaza principal en OpenStreetMap

Referencia: `Plaza de Bolívar` del municipio en OSM (Nominatim, 2026-11-10). Distancia calculada con la fórmula de Haversine.

| Municipio | Pin del catálogo | Plaza en OSM | Distancia | Estado |
|---|---|---|---|---|
| Armenia | 4.5325725, -75.6730412 | (es la plaza) | 0 m | OK |
| Génova | 4.2066969, -75.7911047 | 4.2065017, -75.7906184 | 58 m | OK |
| Montenegro | 4.566637, -75.75012 | 4.5671760, -75.7504826 | 72 m | OK |
| Pijao | 4.3343461, -75.7036308 | 4.3341233, -75.7038431 (Parque Principal) | 34 m | OK |
| Salento | 4.637365, -75.5703107 | 4.6372361, -75.5698171 | 57 m | OK |
| La Tebaida | 4.453588, -75.79153 | 4.4536682, -75.7894510 ("Urbanización Villa Ruby") | 231 m | **Revisar** |
| Quimbaya | 4.625907, -75.761865 | 4.6224467, -75.7631359 ("San José") | 410 m | **Revisar** |
| Calarcá | 4.5266936, -75.6409574 | 4.5306393, -75.6405209 ("Cuatro Esquinas") | 441 m | **Revisar** |
| Buenavista | 4.3526315, -75.7487779 | 4.3594339, -75.7382658 | 1.389 m | **Revisar** (el pin cae en zona rural) |
| Circasia | 4.616094, -75.635595 | sin resultado en OSM | — | **Sin referencia** |
| Córdoba | 4.392095, -75.687434 | sin resultado en OSM | — | **Sin referencia** |
| Filandia | 4.6746953, -75.6577028 | sin resultado en OSM | — | **Sin referencia** |

Nota: las plazas de OSM de La Tebaida, Quimbaya y Calarcá tienen nombres de barrio o sector, así que tampoco son una referencia segura. Hay que decidir la plaza real en el mapa.

## 2. Otros 28 lugares

- Todos caen dentro del polígono OSM de su municipio (comprobado con shapely).
- Los atractivos, fincas y acopios fueron tomados de la búsqueda de Google Maps por nombre; el nombre del lugar devuelto por Google coincide con el del catálogo en todos los casos.
- Lo que **no** se ha comprobado: que el pin esté sobre la entrada o el predio correcto. Eso requiere revisión visual.

## 3. Pendiente para PARADA 1

1. Revisar en mapa las 3 cabeceras sin referencia (Circasia, Córdoba, Filandia) y elegir su plaza principal.
2. Decidir las 4 cabeceras marcadas **Revisar** (La Tebaida, Quimbaya, Calarcá, Buenavista).
3. Revisar visualmente los 28 lugares restantes.
4. Solo entonces marcar `verificado=True` fila por fila y regenerar `pares_dijkstra.csv` si cambió alguna coordenada.
