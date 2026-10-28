# utils/validaciones.py
# Validaciones centralizadas. Cada función lanza ValueError con un mensaje
# descriptivo si el dato es inválido, o retorna el valor ya limpio/convertido.

import datetime
from decimal import Decimal, ROUND_HALF_UP

MAX_LARGO_CATEGORIA = 30
MAX_LARGO_DESCRIPCION = 100


def validar_fecha(texto: str) -> datetime.date:
    """Valida y convierte un string a date. Acepta YYYY-MM-DD.

    No se permiten fechas futuras: un gasto registrado ya ocurrió.
    """
    try:
        fecha = datetime.date.fromisoformat(texto.strip())
    except ValueError:
        raise ValueError(f"Fecha inválida: '{texto}'. Usa el formato YYYY-MM-DD") from None
    if fecha > datetime.date.today():
        raise ValueError(f"La fecha {fecha} es futura. Registra solo gastos ya realizados")
    return fecha


def validar_monto(texto: str) -> float:
    """Valida que el monto sea un número positivo mayor a cero.

    Acepta coma o punto como separador decimal (ej: 12,50 o 12.50).
    """
    try:
        monto = float(texto.strip().replace(",", "."))
    except ValueError:
        raise ValueError(f"Monto inválido: '{texto}'. Debe ser un número") from None
    if monto != monto or monto in (float("inf"), float("-inf")):  # NaN / infinito
        raise ValueError("Monto inválido")
    # Redondeo comercial (12,555 -> 12.56); round() de float puede dar 12.55
    redondeado = float(Decimal(str(monto)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    if redondeado <= 0:
        raise ValueError(f"El monto debe ser mayor a cero. Recibido: {monto}")
    return redondeado


def validar_categoria(texto: str) -> str:
    """Valida que la categoría no esté vacía ni sea demasiado larga."""
    cat = " ".join(texto.split())
    if not cat:
        raise ValueError("La categoría no puede estar vacía")
    if len(cat) > MAX_LARGO_CATEGORIA:
        raise ValueError(f"La categoría no puede superar {MAX_LARGO_CATEGORIA} caracteres")
    return cat.title()


def validar_descripcion(texto: str) -> str:
    """La descripción es opcional, pero con un largo máximo."""
    desc = texto.strip()
    if len(desc) > MAX_LARGO_DESCRIPCION:
        raise ValueError(f"La descripción no puede superar {MAX_LARGO_DESCRIPCION} caracteres")
    return desc


def validar_rango_fechas(inicio: datetime.date, fin: datetime.date) -> None:
    """Verifica que la fecha de inicio no sea posterior a la de fin."""
    if fin < inicio:
        raise ValueError(f"La fecha final ({fin}) es anterior a la inicial ({inicio})")
