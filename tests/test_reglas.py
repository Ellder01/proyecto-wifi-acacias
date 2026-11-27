import csv
from reglas import (
    RUTA_DATOS,
    calcular_resumen,
    cargar_datos,
    filtrar_zonas,
    verificar_clave_admin,
)


def test_cifra_de_control_por_otro_camino():
    # Camino 1: lógica de la app con pandas
    df = cargar_datos()
    resumen = calcular_resumen(df)

    # Camino 2: lectura independiente con el módulo estándar csv
    total_filas = 0
    total_aps = 0
    with open(RUTA_DATOS, mode="r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            total_filas += 1
            valor = (fila.get("puntos_acceso") or "").strip()
            if valor.isdigit():
                total_aps += int(valor)

    assert total_filas > 0
    assert resumen["total_zonas"] == total_filas
    assert resumen["total_puntos_acceso"] == total_aps


def test_filtros_reducen_o_mantienen_resultados():
    df = cargar_datos()
    urbana = filtrar_zonas(df, zona="Urbana")
    assert len(urbana) <= len(df)
    if len(urbana) > 0:
        assert (urbana["zona"] == "Urbana").all()


def test_verificacion_clave_admin():
    assert verificar_clave_admin("mi_secreto_123", "mi_secreto_123") is True
    assert verificar_clave_admin("incorrecta", "mi_secreto_123") is False
    assert verificar_clave_admin("", "") is False
