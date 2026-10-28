# 💸 FinTrack Py — Gestor de Gastos Personales

Aplicación de línea de comandos para **registrar, filtrar y analizar gastos personales**.
Desarrollada en Python 3.10+ como MVP para *FinTrack Studio*, siguiendo una
arquitectura en capas y buenas prácticas profesionales.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Tests](https://img.shields.io/badge/tests-unittest-green)
![Dependencias](https://img.shields.io/badge/dependencias-ninguna-lightgrey)

## Características
- ➕ Agregar gastos con fecha (Enter = hoy), categoría, monto y descripción
- 📋 Listar todos los gastos ordenados por fecha, siempre con el total
- 🏷️ Filtrar por categoría (sin distinguir mayúsculas)
- 📆 Filtrar por rango de fechas (inclusive)
- 📊 Ver totales por categoría con porcentaje y barra, promedio, mayor y menor gasto
- 💾 Persistencia automática en `data/gastos.csv` (se carga al iniciar)
- ✅ Validación robusta con reintentos: formato de fecha, fechas futuras, montos
  no numéricos o negativos, categorías vacías, coma o punto decimal
- 🛡️ No se rompe ante entradas inválidas, filas corruptas en el CSV ni Ctrl+C

## Instalación y uso
```bash
# Clonar el repositorio
git clone https://github.com/ujeisson-alt/gestor-gastos.git
cd gestor-gastos

# Ejecutar (requiere Python 3.10+, sin dependencias externas)
python main.py
```

### Ejemplo
```
=== GESTOR DE GASTOS PERSONALES ===
1. Agregar gasto
2. Listar gastos
3. Filtrar por categoría
4. Filtrar por rango de fechas
5. Ver totales
6. Salir
Seleccione una opción: 5

--- TOTALES Y ESTADÍSTICAS ---
  Entretenimiento $    200.00   40.3%  ████████
  Transporte      $    120.50   24.3%  █████
  Servicios       $     89.90   18.1%  ████
  Comida          $     85.75   17.3%  ███
  Total general:   $496.15
  Cantidad:        5 gastos
  Promedio:        $99.23
```

## Pruebas
```bash
python -m unittest discover -s tests -v
```
`tests/test_basico.py` documenta los casos de prueba manuales y automatiza la
lógica: validaciones, filtros, totales, persistencia y CSV corrupto.

## Estructura del proyecto
```
gestor-gastos/
├── main.py                 # Punto de entrada e interfaz de usuario
├── models/
│   └── gasto.py            # Modelo de datos (Gasto)
├── services/
│   └── gestor.py           # Lógica de negocio + persistencia (GestorGastos)
├── utils/
│   └── validaciones.py     # Validaciones de entrada
├── data/
│   └── gastos.csv          # Datos de ejemplo / persistidos
├── tests/
│   └── test_basico.py      # Casos de prueba manuales + unittest
├── DEVLOG.md               # Diario de desarrollo y decisiones
└── README.md
```

## Arquitectura
```
┌──────────────────────────────────────────────┐
│ PRESENTACIÓN  main.py — menú, input, print() │
└───────────────────────┬──────────────────────┘
                        ▼
┌──────────────────────────────────────────────┐
│ SERVICIO  services/gestor.py — negocio       │
└───────────┬───────────────────────┬──────────┘
            ▼                       ▼
┌──────────────────────┐ ┌─────────────────────┐
│ MODELOS  gasto.py    │ │ PERSISTENCIA  CSV   │
└──────────────────────┘ └─────────────────────┘
```

## Stack tecnológico
- Python 3.10+
- Módulos estándar: `csv`, `datetime`, `decimal`, `os`, `unittest`

## Aprendizajes clave
POO (modelo vs. servicio), persistencia CSV, manejo de errores con `try/except`,
validación centralizada, redondeo monetario con `Decimal`, control de versiones con
Git (Conventional Commits) y documentación profesional.

## Autor
**Jeisson Uribe** — [LinkedIn](https://linkedin.com/in/jeisson-uribe-qa-data) · [GitHub](https://github.com/ujeisson-alt)
