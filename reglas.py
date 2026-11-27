from pathlib import Path
import pandas as pd

RUTA_DATOS = Path(__file__).parent / "datos" / "zonas_wifi.csv"

FUENTE_NOMBRE = "Alcaldía de Acacías - Datos Abiertos Colombia (datos.gov.co)"
FUENTE_URL = "https://www.datos.gov.co/Ciencia-Tecnolog-a-e-Innovaci-n/Zonas-Wifi-Gratis-Municipio-de-Acac-as/r7mn-ty3w/about_data"
FUENTE_LICENCIA = "Licencia Abierta de Datos Públicos de Colombia (Creative Commons Attribution 4.0)"

COLUMNAS_TEXTO = [
    "zona",
    "conexion",
    "barrio",
    "zona_wifi",
    "direccion",
    "ssid",
    "radio_cobertura",
    "instalacion",
    "energia",
    "imagen_ubicacion",
]


def cargar_datos(ruta: Path = RUTA_DATOS) -> pd.DataFrame:
    df = pd.read_csv(ruta, encoding="utf-8")
    df.columns = [c.strip().lower() for c in df.columns]
    for col in COLUMNAS_TEXTO:
        if col in df.columns:
            df[col] = df[col].fillna("Sin especificar").astype(str).str.strip()
            df.loc[df[col] == "", col] = "Sin especificar"
    df["puntos_acceso"] = pd.to_numeric(df["puntos_acceso"], errors="coerce").fillna(0).astype(int)
    return df


def obtener_opciones(df: pd.DataFrame, columna: str) -> list[str]:
    valores = sorted(df[columna].dropna().unique().tolist())
    return ["Todas"] + valores


def filtrar_zonas(
    df: pd.DataFrame,
    zona: str = "Todas",
    conexion: str = "Todas",
    texto_barrio: str = "",
) -> pd.DataFrame:
    resultado = df.copy()
    if zona != "Todas":
        resultado = resultado[resultado["zona"] == zona]
    if conexion != "Todas":
        resultado = resultado[resultado["conexion"] == conexion]
    if texto_barrio.strip():
        termino = texto_barrio.strip().lower()
        resultado = resultado[
            resultado["barrio"].str.lower().str.contains(termino, na=False)
            | resultado["zona_wifi"].str.lower().str.contains(termino, na=False)
        ]
    return resultado


def calcular_resumen(df: pd.DataFrame) -> dict:
    return {
        "total_zonas": int(len(df)),
        "total_puntos_acceso": int(df["puntos_acceso"].sum()),
        "barrios_cubiertos": int(df["barrio"].nunique()),
    }


def resumir_por_columna(df: pd.DataFrame, columna: str) -> list[dict]:
    if df.empty or columna not in df.columns:
        return []
    total_zonas = len(df)
    agrupado = (
        df.groupby(columna, dropna=False)
        .agg(
            zonas=("zona_wifi", "count") if "zona_wifi" in df.columns else (columna, "count"),
            puntos_acceso=("puntos_acceso", "sum"),
        )
        .reset_index()
        .sort_values(by=["zonas", "puntos_acceso"], ascending=[False, False])
    )
    filas = []
    for _, fila in agrupado.iterrows():
        zonas_num = int(fila["zonas"])
        porcentaje = round((zonas_num / total_zonas) * 100, 1) if total_zonas > 0 else 0.0
        filas.append(
            {
                "categoria": str(fila[columna]),
                "zonas": zonas_num,
                "puntos_acceso": int(fila["puntos_acceso"]),
                "porcentaje": porcentaje,
            }
        )
    return filas


def parsear_coordenada(valor: object) -> float | None:
    if valor is None or pd.isna(valor):
        return None
    texto = str(valor).strip().replace(",", ".")
    if not texto or texto.lower() in {"nan", "none", "sin especificar"}:
        return None
    try:
        return float(texto)
    except ValueError:
        return None


def construir_url_mapa(latitud: object, longitud: object) -> str | None:
    lat = parsear_coordenada(latitud)
    lon = parsear_coordenada(longitud)
    if lat is None or lon is None:
        return None
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return None
    if lat == 0.0 and lon == 0.0:
        return None
    return f"https://www.google.com/maps?q={lat},{lon}"


def obtener_detalle_zona(df: pd.DataFrame, nombre_zona: str) -> dict | None:
    if df.empty or not nombre_zona or "zona_wifi" not in df.columns:
        return None
    coincidencias = df[df["zona_wifi"] == nombre_zona]
    if coincidencias.empty:
        return None
    fila = coincidencias.iloc[0]

    def _campo(col: str, defecto: str = "Sin especificar") -> str:
        if col not in fila.index or pd.isna(fila[col]):
            return defecto
        val = str(fila[col]).strip()
        return val if val else defecto

    lat = parsear_coordenada(fila["latitud"]) if "latitud" in fila.index else None
    lon = parsear_coordenada(fila["longitud"]) if "longitud" in fila.index else None
    url_mapa = construir_url_mapa(lat, lon)
    imagen = _campo("imagen_ubicacion", defecto="")
    url_imagen = imagen if imagen.startswith(("http://", "https://")) else None

    return {
        "zona_wifi": _campo("zona_wifi"),
        "barrio": _campo("barrio"),
        "direccion": _campo("direccion"),
        "zona": _campo("zona"),
        "conexion": _campo("conexion"),
        "instalacion": _campo("instalacion"),
        "energia": _campo("energia"),
        "puntos_acceso": int(fila["puntos_acceso"]) if "puntos_acceso" in fila.index else 0,
        "radio_cobertura": _campo("radio_cobertura"),
        "ssid": _campo("ssid"),
        "latitud": lat,
        "longitud": lon,
        "url_mapa": url_mapa,
        "url_imagen": url_imagen,
    }


def verificar_clave_admin(clave_ingresada: str, clave_esperada: str) -> bool:
    if not clave_esperada:
        return False
    return clave_ingresada == clave_esperada
