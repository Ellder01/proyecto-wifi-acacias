import os
import solara
from reglas import (
    FUENTE_LICENCIA,
    FUENTE_NOMBRE,
    FUENTE_URL,
    calcular_resumen,
    cargar_datos,
    filtrar_zonas,
    obtener_opciones,
    verificar_clave_admin,
)

DF_BASE = cargar_datos()
OPCIONES_ZONA = obtener_opciones(DF_BASE, "zona")
OPCIONES_CONEXION = obtener_opciones(DF_BASE, "conexion")

NOMBRE_APP = os.environ.get("NOMBRE_APP", "Buscador de Zonas Wi-Fi Gratis - Acacías")
CLAVE_ADMIN = os.environ.get("CLAVE_ADMIN", "")


@solara.component
def Page():
    zona_sel = solara.use_reactive("Todas")
    conexion_sel = solara.use_reactive("Todas")
    busqueda = solara.use_reactive("")
    clave_input = solara.use_reactive("")

    df_filtrado = filtrar_zonas(
        DF_BASE,
        zona=zona_sel.value,
        conexion=conexion_sel.value,
        texto_barrio=busqueda.value,
    )
    resumen = calcular_resumen(df_filtrado)
    columnas_visibles = [
        "zona_wifi",
        "barrio",
        "direccion",
        "zona",
        "conexion",
        "puntos_acceso",
        "radio_cobertura",
        "ssid",
    ]
    tabla = df_filtrado[[c for c in columnas_visibles if c in df_filtrado.columns]]

    with solara.Column(style={"max-width": "1100px", "margin": "0 auto", "padding": "20px"}):
        solara.Title(NOMBRE_APP)
        solara.Markdown(f"# {NOMBRE_APP}")

        solara.Info(
            label=(
                "Para quién es y qué necesidad resuelve: Dirigido a estudiantes, trabajadores "
                "independientes y ciudadanos del municipio de Acacías (Meta) que necesitan "
                "ubicar rápidamente puntos de internet público gratuito sin tener que navegar "
                "tablas extensas de datos crudos."
            )
        )

        with solara.Row(gap="16px"):
            solara.Select(label="Filtrar por Zona", value=zona_sel, values=OPCIONES_ZONA)
            solara.Select(label="Tipo de Conexión", value=conexion_sel, values=OPCIONES_CONEXION)
            solara.InputText(label="Buscar barrio o zona Wi-Fi", value=busqueda)

        with solara.Row(gap="16px"):
            solara.Card(title="Zonas encontradas", subtitle=str(resumen["total_zonas"]))
            solara.Card(title="Puntos de acceso (APs)", subtitle=str(resumen["total_puntos_acceso"]))
            solara.Card(title="Barrios cubiertos", subtitle=str(resumen["barrios_cubiertos"]))

        solara.Markdown("### Listado de puntos Wi-Fi disponibles")
        if len(tabla) == 0:
            solara.Warning("No se encontraron zonas Wi-Fi con los filtros seleccionados.")
        else:
            solara.DataFrame(tabla, items_per_page=10)

        with solara.Details("Panel técnico de verificación (requiere clave de administrador)"):
            solara.InputText(
                label="Ingrese clave de administrador",
                value=clave_input,
                password=True,
            )
            if not CLAVE_ADMIN:
                solara.Warning("Secreto CLAVE_ADMIN no configurado en el servidor.")
            elif clave_input.value:
                if verificar_clave_admin(clave_input.value, CLAVE_ADMIN):
                    resumen_total = calcular_resumen(DF_BASE)
                    solara.Success(
                        f"Acceso verificado. Dataset completo cargado: "
                        f"{resumen_total['total_zonas']} zonas y "
                        f"{resumen_total['total_puntos_acceso']} puntos de acceso totales."
                    )
                else:
                    solara.Error("Clave incorrecta.")

        solara.Markdown(
            f"---\n"
            f"**Fuente de datos abiertos:** [{FUENTE_NOMBRE}]({FUENTE_URL})  \n"
            f"**Licencia:** {FUENTE_LICENCIA}"
        )
