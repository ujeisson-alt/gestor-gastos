# DEVLOG — FinTrack Py

## Análisis
**Datos de un gasto:** id, fecha, categoría, monto, descripción.

**Historias de usuario**
1. Como usuario, quiero agregar un gasto con fecha, categoría y monto, para llevar un registro organizado.
2. Como usuario, quiero listar todos mis gastos, para ver en qué gasté mi dinero.
3. Como usuario, quiero filtrar por categoría, para saber cuánto gasto en cada rubro.
4. Como usuario, quiero filtrar por rango de fechas, para revisar un mes o una semana.
5. Como usuario, quiero ver totales y estadísticas, para tomar decisiones sobre mi presupuesto.

**Fuera del MVP:** GUI, base de datos, múltiples usuarios, gráficos, sincronización en la nube.

## Decisiones de diseño (mini-ADR)
- **Fecha como `datetime.date`** dentro del modelo: permite comparar y ordenar rangos sin errores de texto.
- **Categoría en Title Case**: "comida", "COMIDA" y "Comida" son la misma categoría.
- **Validaciones en `utils/validaciones.py`** que lanzan `ValueError` con mensaje claro; `main.py` las reintenta con `pedir_con_reintento()`.
- **Se rechazan fechas futuras**: un gasto registrado ya ocurrió.
- **Redondeo con `Decimal` (ROUND_HALF_UP)**: `round(12.555, 2)` en float da 12.55; para dinero se espera 12.56. Lo detectó una prueba unitaria.
- **Rutas del CSV relativas al proyecto**: la app funciona aunque se ejecute desde otra carpeta.
- **Carga tolerante**: una fila corrupta del CSV se informa y se omite, sin perder el resto.

## Registro de sesiones
- **Día 1** — Análisis, historias de usuario, clase `Gasto` y menú inicial.
- **Días 2-3** — Clase `GestorGastos` (agregar, listar, filtros, totales) e integración con el menú.
- **Días 6-7** — Persistencia CSV: carga al iniciar, guardado tras agregar y al salir. Prueba de cierre/reapertura OK.
- **Día 8** — Validaciones con reintentos; manejo de Ctrl+C / Ctrl+D.
- **Días 9-10** — Revisión de código, estadísticas por categoría, pruebas unitarias y README.
