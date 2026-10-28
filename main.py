# main.py
# Punto de entrada e interfaz de usuario (capa de presentación) de FinTrack Py.

import datetime

from services.gestor import GestorGastos
from utils.validaciones import (validar_fecha, validar_monto, validar_categoria,
                                validar_descripcion, validar_rango_fechas)

SEPARADOR = "-" * 72


def mostrar_menu() -> str:
    """Muestra el menú principal y retorna la opción elegida."""
    print("\n=== GESTOR DE GASTOS PERSONALES ===")
    print("1. Agregar gasto")
    print("2. Listar gastos")
    print("3. Filtrar por categoría")
    print("4. Filtrar por rango de fechas")
    print("5. Ver totales")
    print("6. Salir")
    return input("Seleccione una opción: ").strip()


def pedir_con_reintento(prompt: str, validador, permitir_vacio_con=None):
    """Pide un dato al usuario y repite hasta que sea válido.

    Si permitir_vacio_con no es None y el usuario presiona Enter,
    retorna ese valor por defecto.
    """
    while True:
        valor = input(prompt).strip()
        if valor == "" and permitir_vacio_con is not None:
            return permitir_vacio_con
        try:
            return validador(valor)
        except ValueError as e:
            print(f"  ✗ {e}. Por favor, intenta de nuevo.")


def imprimir_gastos(gestor: GestorGastos, gastos, titulo: str) -> None:
    """Imprime una lista de gastos con su total (o un aviso si está vacía)."""
    if not gastos:
        print("  Sin resultados.")
        return
    print(f"\n--- {titulo} ({len(gastos)} registros) ---")
    print(SEPARADOR)
    for g in gastos:
        print(g)
    print(SEPARADOR)
    print(f"TOTAL: ${gestor.total(gastos):,.2f}")


def agregar_gasto(gestor: GestorGastos) -> bool:
    """Flujo para registrar un gasto. Retorna True si se agregó."""
    print("\n--- AGREGAR GASTO ---")
    hoy = datetime.date.today()
    fecha = pedir_con_reintento(f"Fecha (YYYY-MM-DD) [Enter para hoy {hoy}]: ",
                                validar_fecha, permitir_vacio_con=hoy)
    categoria = pedir_con_reintento("Categoría (ej: Comida, Transporte): ", validar_categoria)
    monto = pedir_con_reintento("Monto: ", validar_monto)
    descripcion = pedir_con_reintento("Descripción (opcional): ", validar_descripcion,
                                      permitir_vacio_con="")
    gasto = gestor.agregar(fecha, categoria, monto, descripcion)
    print(f"  ✓ Gasto agregado: {gasto}")
    return True


def listar_gastos(gestor: GestorGastos) -> None:
    gastos = gestor.listar_todos()
    if not gastos:
        print("  No hay gastos registrados.")
        return
    imprimir_gastos(gestor, gastos, "GASTOS")


def filtrar_por_categoria(gestor: GestorGastos) -> None:
    categorias = gestor.categorias_disponibles()
    if not categorias:
        print("  No hay gastos registrados.")
        return
    print(f"  Categorías disponibles: {', '.join(categorias)}")
    categoria = pedir_con_reintento("Categoría a filtrar: ", validar_categoria)
    imprimir_gastos(gestor, gestor.filtrar_por_categoria(categoria), f"CATEGORÍA {categoria.upper()}")


def filtrar_por_fechas(gestor: GestorGastos) -> None:
    inicio = pedir_con_reintento("Fecha inicial (YYYY-MM-DD): ", validar_fecha)
    fin = pedir_con_reintento("Fecha final   (YYYY-MM-DD): ", validar_fecha)
    try:
        validar_rango_fechas(inicio, fin)
    except ValueError as e:
        print(f"  ✗ {e}.")
        return
    imprimir_gastos(gestor, gestor.filtrar_por_fechas(inicio, fin), f"DEL {inicio} AL {fin}")


def ver_totales(gestor: GestorGastos) -> None:
    stats = gestor.estadisticas()
    if stats["cantidad"] == 0:
        print("  No hay gastos registrados.")
        return
    print("\n--- TOTALES Y ESTADÍSTICAS ---")
    print(SEPARADOR)
    total = stats["total"]
    for categoria, monto in gestor.totales_por_categoria().items():
        porcentaje = monto / total * 100
        barra = "█" * round(porcentaje / 5)
        print(f"  {categoria:<15} ${monto:>10,.2f}  {porcentaje:5.1f}%  {barra}")
    print(SEPARADOR)
    print(f"  Total general:   ${total:,.2f}")
    print(f"  Cantidad:        {stats['cantidad']} gastos")
    print(f"  Promedio:        ${stats['promedio']:,.2f}")
    print(f"  Mayor gasto:     {stats['mayor']}")
    print(f"  Menor gasto:     {stats['menor']}")


def guardar_seguro(gestor: GestorGastos) -> None:
    """Guarda en CSV informando al usuario si ocurre un error de disco."""
    try:
        gestor.guardar_en_csv()
    except OSError as e:
        print(f"  ✗ No se pudieron guardar los datos: {e}")


ACCIONES = {
    "2": listar_gastos,
    "3": filtrar_por_categoria,
    "4": filtrar_por_fechas,
    "5": ver_totales,
}


def main() -> None:
    gestor = GestorGastos()
    # Cargar datos existentes al arrancar
    try:
        n = gestor.cargar_desde_csv()
        print(f"  {n} gastos cargados desde archivo.")
    except OSError as e:
        print(f"  ✗ No se pudo leer el archivo de datos: {e}")

    while True:
        try:
            opcion = mostrar_menu()
            if opcion == "1":
                agregar_gasto(gestor)
                guardar_seguro(gestor)  # Guardar inmediatamente tras agregar
            elif opcion in ACCIONES:
                ACCIONES[opcion](gestor)
            elif opcion == "6":
                guardar_seguro(gestor)  # Guardar al salir también
                print("  Datos guardados. ¡Hasta pronto!")
                break
            else:
                print("  Opción no válida. Intenta de nuevo.")
        except KeyboardInterrupt:
            print("\n  Operación cancelada. Volviendo al menú...")
        except EOFError:
            guardar_seguro(gestor)
            print("\n  Datos guardados. ¡Hasta pronto!")
            break


if __name__ == "__main__":
    main()
