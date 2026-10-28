# tests/test_basico.py
# Pruebas de FinTrack Py.
#
# Ejecutar desde la raíz del proyecto:
#     python -m unittest discover -s tests -v
#
# ---------------------------------------------------------------------------
# CASOS DE PRUEBA MANUALES (ejecutados sobre la app con `python main.py`)
# ---------------------------------------------------------------------------
# | # | Caso de prueba                         | Resultado esperado                          | Estado |
# |---|----------------------------------------|---------------------------------------------|--------|
# | 1 | Agregar gasto con datos válidos        | Aparece en la lista con ID asignado         | OK     |
# | 2 | Agregar gasto con monto='abc'          | Error descriptivo, no crash; pide reintentar| OK     |
# | 3 | Agregar gasto con fecha='99-99-99'     | Error descriptivo de formato de fecha       | OK     |
# | 4 | Agregar gasto con monto negativo       | Error: el monto debe ser mayor a cero       | OK     |
# | 5 | Cerrar y reabrir la app                | Los gastos del CSV se cargan correctamente  | OK     |
# | 6 | Filtrar por categoría inexistente      | Mensaje 'Sin resultados.'                   | OK     |
# | 7 | Filtrar con fecha_fin < fecha_inicio   | Mensaje de aviso                            | OK     |
# | 8 | Listar con 0 gastos registrados        | Mensaje 'No hay gastos registrados.'        | OK     |
# | 9 | Ctrl+C dentro de una opción            | Vuelve al menú sin perder datos             | OK     |
# ---------------------------------------------------------------------------
# Los casos 1-8 también están automatizados abajo a nivel de lógica.

import datetime
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.gasto import Gasto  # noqa: E402
from services.gestor import GestorGastos  # noqa: E402
from utils.validaciones import (validar_fecha, validar_monto, validar_categoria,  # noqa: E402
                                validar_rango_fechas)


class TestGasto(unittest.TestCase):

    def test_crear_gasto_limpia_datos(self):
        g = Gasto(1, "2025-01-15", "  comida ", 50, " Almuerzo ")
        self.assertEqual(g.fecha, datetime.date(2025, 1, 15))
        self.assertEqual(g.categoria, "Comida")
        self.assertEqual(g.descripcion, "Almuerzo")

    def test_to_dict_from_dict(self):
        g = Gasto(3, "2025-01-17", "Ocio", 200, "Cine")
        self.assertEqual(Gasto.from_dict(g.to_dict()).to_dict(), g.to_dict())

    def test_monto_no_positivo_es_invalido(self):
        with self.assertRaises(ValueError):
            Gasto(1, "2025-01-15", "Comida", 0, "")


class TestValidaciones(unittest.TestCase):

    def test_caso2_monto_texto(self):
        with self.assertRaises(ValueError):
            validar_monto("abc")

    def test_caso3_fecha_invalida(self):
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            validar_fecha("99-99-99")

    def test_caso4_monto_negativo(self):
        with self.assertRaisesRegex(ValueError, "mayor a cero"):
            validar_monto("-10")

    def test_monto_con_coma_decimal(self):
        self.assertEqual(validar_monto("12,555"), 12.56)

    def test_fecha_futura_rechazada(self):
        manana = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError):
            validar_fecha(manana)

    def test_categoria_vacia(self):
        with self.assertRaises(ValueError):
            validar_categoria("   ")

    def test_caso7_rango_invertido(self):
        with self.assertRaises(ValueError):
            validar_rango_fechas(datetime.date(2025, 2, 1), datetime.date(2025, 1, 1))


class TestGestorGastos(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.tmp.name, "data", "gastos.csv")
        self.gestor = GestorGastos(ruta_csv=self.ruta)
        self.gestor.agregar("2025-01-16", "Transporte", 120.50, "Uber")
        self.gestor.agregar("2025-01-15", "Comida", 50, "Almuerzo")
        self.gestor.agregar("2025-01-20", "comida", 35.75, "Mercado")

    def tearDown(self):
        self.tmp.cleanup()

    def test_caso1_ids_y_orden_por_fecha(self):
        self.assertEqual([g.id for g in self.gestor.listar_todos()], [2, 1, 3])

    def test_filtrar_por_categoria_ignora_mayusculas(self):
        self.assertEqual(len(self.gestor.filtrar_por_categoria("COMIDA")), 2)

    def test_caso6_categoria_inexistente(self):
        self.assertEqual(self.gestor.filtrar_por_categoria("Viajes"), [])

    def test_filtrar_por_fechas_inclusivo(self):
        resultado = self.gestor.filtrar_por_fechas("2025-01-15", "2025-01-16")
        self.assertEqual([g.id for g in resultado], [2, 1])

    def test_caso7_rango_invertido_lista_vacia(self):
        self.assertEqual(self.gestor.filtrar_por_fechas("2025-02-01", "2025-01-01"), [])

    def test_totales(self):
        self.assertEqual(self.gestor.total(), 206.25)
        self.assertEqual(self.gestor.totales_por_categoria(),
                         {"Transporte": 120.5, "Comida": 85.75})
        stats = self.gestor.estadisticas()
        self.assertEqual(stats["promedio"], 68.75)
        self.assertEqual(stats["mayor"].categoria, "Transporte")

    def test_caso8_sin_gastos(self):
        vacio = GestorGastos(ruta_csv=self.ruta)
        self.assertEqual(vacio.listar_todos(), [])
        self.assertEqual(vacio.estadisticas()["cantidad"], 0)

    def test_caso5_persistencia(self):
        self.gestor.guardar_en_csv()
        nuevo = GestorGastos(ruta_csv=self.ruta)
        self.assertEqual(nuevo.cargar_desde_csv(), 3)
        self.assertEqual(nuevo.total(), 206.25)
        # El contador de IDs continúa después del mayor ID cargado
        self.assertEqual(nuevo.agregar("2025-02-01", "Ocio", 10, "").id, 4)

    def test_csv_con_fila_corrupta(self):
        os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
        with open(self.ruta, "w", encoding="utf-8") as f:
            f.write("id,fecha,categoria,monto,descripcion\n"
                    "1,2025-01-15,Comida,50,ok\n"
                    "2,fecha-mala,Comida,10,x\n")
        self.assertEqual(GestorGastos(ruta_csv=self.ruta).cargar_desde_csv(), 1)


if __name__ == "__main__":
    unittest.main()
