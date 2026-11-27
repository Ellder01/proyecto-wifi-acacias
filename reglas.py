from pathlib import Path
import pandas as pd

RUTA_DATOS = Path(__file__).parent / "datos" / "zonas_wifi.csv"

FUENTE_NOMBRE = "Alcaldía de Acacías - Datos Abiertos Colombia (datos.gov.co)"
FUENTE_URL = "https://www.datos.gov.co/Ciencia-Tecnolog-a-e-Innovaci-n/Zonas-Wifi-Gratis-Municipio-de-Acac-as/r7mn-ty3w/about_data"
FUENTE_LICENCIA = "Licencia Abierta de Datos Públicos de Colombia (Creative Commons Attribution 4.0)"


def cargar_datos(ruta: Path = RUTA_DATOS) -> pd.DataFrame:
    df = pd.read_csv(ruta, encoding="utf-8")
    df.columns = [c.strip().lower() for c in df.columns]
    for col in ["zona", "conexion", "barrio", "zona_wifi", "direccion", "ssid", "radio_cobertura"]:
        if col in df.columns:
            df[col] = df[col].fillna("Sin especificar").astype(str).str.strip()
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


def verificar_clave_admin(clave_ingresada: str, clave_esperada: str) -> bool:
    if not clave_esperada:
        return False
    return clave_ingresada == clave_esperada
