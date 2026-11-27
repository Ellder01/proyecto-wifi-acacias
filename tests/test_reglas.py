import csv
import pandas as pd
from reglas import (
    RUTA_DATOS,
    calcular_resumen,
    cargar_datos,
    comparar_zonas,
    construir_url_mapa,
    filtrar_zonas,
    obtener_detalle_zona,
    obtener_puntos_mapa,
    parsear_coordenada,
    ranking_barrios,
    resumir_por_columna,
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


def test_resumir_por_columna():
    df = cargar_datos()
    desglose_zona = resumir_por_columna(df, "zona")
    assert len(desglose_zona) > 0
    assert sum(item["zonas"] for item in desglose_zona) == len(df)
    assert sum(item["puntos_acceso"] for item in desglose_zona) == int(df["puntos_acceso"].sum())
    assert resumir_por_columna(pd.DataFrame(), "zona") == []


def test_mapa_ranking_y_comparador():
    df = cargar_datos()
    puntos = obtener_puntos_mapa(df)
    assert len(puntos) > 0
    assert all("latitud" in p and "longitud" in p and "url_mapa" in p for p in puntos)

    top_barrios = ranking_barrios(df, top_n=5)
    assert len(top_barrios) <= 5
    assert len(top_barrios) > 0

    zonas_disp = df["zona_wifi"].unique().tolist()
    if len(zonas_disp) >= 2:
        comp = comparar_zonas(df, zonas_disp[0], zonas_disp[1])
        assert comp is not None
        assert comp["zona_a"]["zona_wifi"] == zonas_disp[0]
        assert comp["zona_b"]["zona_wifi"] == zonas_disp[1]
    assert comparar_zonas(df, zonas_disp[0], "ZONA_INEXISTENTE") is None
