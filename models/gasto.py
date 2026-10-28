# models/gasto.py
# Clase que representa un gasto individual.
# Sigue el patrón de 'modelo de dominio': solo datos y comportamiento propio.

import datetime
from typing import Union


class Gasto:
    """Representa un gasto personal con fecha, categoría, monto y descripción."""

    def __init__(self, id: int, fecha: Union[str, datetime.date], categoria: str,
                 monto: float, descripcion: str = ""):
        self.id = int(id)
        # Convertimos la fecha a objeto date para poder compararla y ordenarla
        self.fecha = (fecha if isinstance(fecha, datetime.date)
                      else datetime.date.fromisoformat(str(fecha).strip()))  # YYYY-MM-DD
        self.categoria = categoria.strip().title()  # limpieza de texto
        if not self.categoria:
            raise ValueError("La categoría no puede estar vacía.")
        self.monto = round(float(monto), 2)
        if self.monto <= 0:
            raise ValueError("El monto debe ser mayor a cero.")
        self.descripcion = (descripcion or "").strip()

    def __str__(self) -> str:
        """Representación legible para mostrar al usuario."""
        return (f"[{self.id:03d}] {self.fecha} | {self.categoria:<15} |"
                f" ${self.monto:>10,.2f} | {self.descripcion}")

    def __repr__(self) -> str:
        return (f"Gasto(id={self.id}, fecha='{self.fecha}', categoria={self.categoria!r}, "
                f"monto={self.monto}, descripcion={self.descripcion!r})")

    def to_dict(self) -> dict:
        """Convierte el gasto a diccionario (necesario para guardar en CSV)."""
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat(),
            "categoria": self.categoria,
            "monto": f"{self.monto:.2f}",
            "descripcion": self.descripcion,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Gasto":
        """Crea un Gasto a partir de un diccionario (para leer desde CSV)."""
        return cls(
            id=int(d["id"]),
            fecha=d["fecha"],
            categoria=d["categoria"],
            monto=float(d["monto"]),
            descripcion=d.get("descripcion", ""),
        )
