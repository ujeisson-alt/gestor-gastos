# services/gestor.py
# GestorGastos es el 'cerebro' de la aplicación:
# conoce la lista de gastos y sabe qué hacer con ella (incluida su persistencia).

import csv
import datetime
import os
from typing import Dict, List, Optional, Union

from models.gasto import Gasto

DIRECTORIO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_CSV = os.path.join(DIRECTORIO_BASE, "data", "gastos.csv")
CAMPOS = ["id", "fecha", "categoria", "monto", "descripcion"]

FechaEntrada = Union[str, datetime.date]


def _a_fecha(valor: FechaEntrada) -> datetime.date:
    """Acepta un date o un string YYYY-MM-DD y retorna un date."""
    return valor if isinstance(valor, datetime.date) else datetime.date.fromisoformat(valor)


class GestorGastos:
    """Gestiona la colección de gastos y provee operaciones sobre ella."""

    def __init__(self, ruta_csv: str = RUTA_CSV):
        self.ruta_csv = ruta_csv
        self._gastos: List[Gasto] = []  # lista privada de gastos en memoria
        self._siguiente_id: int = 1     # contador autoincremental de IDs

    # ------------------------------------------------------------------
    # Operaciones principales
    # ------------------------------------------------------------------
    def agregar(self, fecha: FechaEntrada, categoria: str,
                monto: float, descripcion: str = "") -> Gasto:
        """Crea y agrega un nuevo gasto. Retorna el gasto creado."""
        gasto = Gasto(self._siguiente_id, fecha, categoria, monto, descripcion)
        self._gastos.append(gasto)
        self._siguiente_id += 1
        return gasto

    def listar_todos(self) -> List[Gasto]:
        """Retorna todos los gastos ordenados por fecha (y por ID en empates)."""
        return sorted(self._gastos, key=lambda g: (g.fecha, g.id))

    def filtrar_por_categoria(self, categoria: str) -> List[Gasto]:
        """Retorna gastos cuya categoría coincide (ignorando mayúsculas)."""
        cat = categoria.strip().title()
        return [g for g in self.listar_todos() if g.categoria == cat]

    def filtrar_por_fechas(self, fecha_inicio: FechaEntrada,
                           fecha_fin: FechaEntrada) -> List[Gasto]:
        """Retorna gastos dentro del rango de fechas (inclusive).

        Si fecha_fin es anterior a fecha_inicio, retorna lista vacía.
        """
        inicio, fin = _a_fecha(fecha_inicio), _a_fecha(fecha_fin)
        return [g for g in self.listar_todos() if inicio <= g.fecha <= fin]

    # ------------------------------------------------------------------
    # Reportes y estadísticas
    # ------------------------------------------------------------------
    def total(self, gastos: Optional[List[Gasto]] = None) -> float:
        """Calcula el monto total. Si no se pasa lista, usa todos los gastos."""
        lista = gastos if gastos is not None else self._gastos
        return round(sum(g.monto for g in lista), 2)

    def totales_por_categoria(self) -> Dict[str, float]:
        """Retorna {categoría: total}, ordenado de mayor a menor gasto."""
        totales: Dict[str, float] = {}
        for g in self._gastos:
            totales[g.categoria] = round(totales.get(g.categoria, 0) + g.monto, 2)
        return dict(sorted(totales.items(), key=lambda kv: kv[1], reverse=True))

    def estadisticas(self) -> dict:
        """Estadísticas básicas: cantidad, total, promedio, mayor y menor gasto."""
        if not self._gastos:
            return {"cantidad": 0, "total": 0.0, "promedio": 0.0, "mayor": None, "menor": None}
        return {
            "cantidad": len(self._gastos),
            "total": self.total(),
            "promedio": round(self.total() / len(self._gastos), 2),
            "mayor": max(self._gastos, key=lambda g: g.monto),
            "menor": min(self._gastos, key=lambda g: g.monto),
        }

    def categorias_disponibles(self) -> List[str]:
        """Retorna lista de categorías únicas registradas."""
        return sorted({g.categoria for g in self._gastos})

    def __len__(self) -> int:
        return len(self._gastos)

    # ------------------------------------------------------------------
    # Persistencia CSV
    # ------------------------------------------------------------------
    def cargar_desde_csv(self, ruta: Optional[str] = None) -> int:
        """Carga gastos desde el CSV al iniciar la app. Retorna cantidad cargada.

        Las filas corruptas se omiten e informan, sin detener la carga.
        """
        ruta = ruta or self.ruta_csv
        if not os.path.exists(ruta):
            return 0  # primera vez que se ejecuta la app
        cargados = 0
        with open(ruta, newline="", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            for numero_fila, fila in enumerate(lector, start=2):
                try:
                    gasto = Gasto.from_dict(fila)
                except (ValueError, KeyError, TypeError, AttributeError) as e:
                    print(f"  Aviso: fila {numero_fila} del CSV omitida ({e}).")
                    continue
                self._gastos.append(gasto)
                # Sincronizar el contador de IDs con el mayor ID existente
                if gasto.id >= self._siguiente_id:
                    self._siguiente_id = gasto.id + 1
                cargados += 1
        return cargados

    def guardar_en_csv(self, ruta: Optional[str] = None) -> None:
        """Guarda TODOS los gastos en CSV, sobrescribiendo el archivo."""
        ruta = ruta or self.ruta_csv
        os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=CAMPOS)
            escritor.writeheader()
            for gasto in self.listar_todos():
                escritor.writerow(gasto.to_dict())
