import csv
import pandas as pd
from reglas import (
    RUTA_DATOS,
    calcular_resumen,
    cargar_datos,
    construir_url_mapa,
    filtrar_zonas,
    obtener_detalle_zona,
    parsear_coordenada,
    verificar_clave_admin,
)


def test_cifra_de_control_por_otro_camino():
    df = cargar_datos()
    resumen = calcular_resumen(df)

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


def test_coordenadas_y_enlace_mapa():
    assert parsear_coordenada("3,993251") == 3.993251
    assert parsear_coordenada("-73,774377") == -73.774377
    assert parsear_coordenada("no_es_numero") is None

    url = construir_url_mapa("3,993251", "-73,774377")
    assert url == "https://www.google.com/maps?q=3.993251,-73.774377"
    assert construir_url_mapa("95,0", "-73,774377") is None
    assert construir_url_mapa("", "-73,774377") is None


def test_obtener_detalle_zona():
    df_demo = pd.DataFrame(
        [
            {
                "zona_wifi": "ZW PRUEBA",
                "barrio": "Centro",
                "direccion": "Calle 10 # 5-20",
                "latitud": "4,1425",
                "longitud": "-73,6266",
                "zona": "Urbana",
                "conexion": "Fibra Óptica",
                "instalacion": "POSTE",
                "energia": "AC",
                "puntos_acceso": 2,
                "ssid": "WIFI GRATIS",
                "radio_cobertura": "60 Metros",
                "imagen_ubicacion": "https://example.com/foto.jpg",
            }
        ]
    )
    detalle = obtener_detalle_zona(df_demo, "ZW PRUEBA")
    assert detalle is not None
    assert detalle["barrio"] == "Centro"
    assert detalle["puntos_acceso"] == 2
    assert detalle["url_mapa"] == "https://www.google.com/maps?q=4.1425,-73.6266"
    assert detalle["url_imagen"] == "https://example.com/foto.jpg"
    assert obtener_detalle_zona(df_demo, "NO EXISTE") is None
