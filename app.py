import json
import os
import solara
from reglas import (
    FUENTE_LICENCIA,
    FUENTE_NOMBRE,
    FUENTE_URL,
    calcular_resumen,
    cargar_datos,
    comparar_zonas,
    filtrar_zonas,
    obtener_detalle_zona,
    obtener_opciones,
    obtener_puntos_mapa,
    ranking_barrios,
    resumir_por_columna,
    verificar_clave_admin,
)

DF_BASE = cargar_datos()
OPCIONES_ZONA = obtener_opciones(DF_BASE, "zona")
OPCIONES_CONEXION = obtener_opciones(DF_BASE, "conexion")
TODAS_LAS_ZONAS = (
    sorted(DF_BASE["zona_wifi"].dropna().unique().tolist())
    if "zona_wifi" in DF_BASE.columns
    else []
)

NOMBRE_APP = os.environ.get("NOMBRE_APP", "Buscador de Zonas Wi-Fi Gratis - Acacías")
CLAVE_ADMIN = os.environ.get("CLAVE_ADMIN", "")

SECCIONES = [
    "Explorador y Mapa",
    "Ranking y Análisis",
    "Comparador de Zonas",
    "Datos y Administración",
]


def _limpiar_filtros(zona_sel, conexion_sel, busqueda):
    zona_sel.set("Todas")
    conexion_sel.set("Todas")
    busqueda.set("")


def _render_desglose_barras(titulo: str, items: list[dict], color_barra: str):
    max_zonas = max((item["zonas"] for item in items), default=1) or 1
    with solara.Div(
        style={
            "background": "#ffffff",
            "border": "1px solid #e2e8f0",
            "border-radius": "12px",
            "padding": "20px 22px",
            "box-shadow": "0 1px 3px rgba(15, 23, 42, 0.04)",
        }
    ):
        solara.Markdown(f"### {titulo}")
        if not items:
            solara.Info("No hay datos disponibles para mostrar este desglose.")
            return

        bloques = []
        for item in items:
            ancho_rel = max(6, int(round((item["zonas"] / max_zonas) * 100)))
            bloques.append(
                f"<div style='margin-bottom:14px;'>"
                f"<div style='display:flex;justify-content:space-between;align-items:baseline;"
                f"font-size:14px;color:#0f172a;margin-bottom:5px;'>"
                f"<strong>{item['categoria']}</strong>"
                f"<span style='font-size:13px;color:#475569;font-variant-numeric:tabular-nums;'>"
                f"{item['zonas']} zonas ({item['porcentaje']}%) · {item['puntos_acceso']} APs</span>"
                f"</div>"
                f"<div style='width:100%;background:#f1f5f9;border-radius:999px;height:10px;"
                f"overflow:hidden;'>"
                f"<div style='width:{ancho_rel}%;background:{color_barra};height:100%;"
                f"border-radius:999px;'></div>"
                f"</div>"
                f"</div>"
            )
        solara.Markdown("".join(bloques))


def _render_mapa_interactivo(puntos: list[dict]):
    with solara.Div(
        style={
            "background": "#ffffff",
            "border": "1px solid #e2e8f0",
            "border-radius": "12px",
            "padding": "20px 22px",
            "box-shadow": "0 1px 3px rgba(15, 23, 42, 0.04)",
        }
    ):
        solara.Markdown("### Mapa interactivo de zonas Wi-Fi (Acacías)")
        if not puntos:
            solara.Info("No hay coordenadas válidas para mostrar en el mapa con el filtro actual.")
            return

        lat_centro = sum(p["latitud"] for p in puntos) / len(puntos)
        lon_centro = sum(p["longitud"] for p in puntos) / len(puntos)
        puntos_json = json.dumps(puntos, ensure_ascii=False)

        html_mapa = f"""
        <div style="width:100%;height:420px;border-radius:10px;overflow:hidden;border:1px solid #cbd5e1;">
          <div id="mapa-acacias" style="width:100%;height:100%;"></div>
        </div>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
          (function() {{
            const puntos = {puntos_json};
            if (!puntos.length || typeof L === "undefined") return;
            const map = L.map("mapa-acacias").setView([{lat_centro}, {lon_centro}], 13);
            L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
              maxZoom: 19,
              attribution: "&copy; OpenStreetMap"
            }}).addTo(map);
            const bounds = [];
            puntos.forEach((p) => {{
              const color = p.zona === "Urbana" ? "#0f4c81" : "#0d9488";
              const marker = L.circleMarker([p.latitud, p.longitud], {{
                radius: 7,
                fillColor: color,
                color: "#ffffff",
                weight: 2,
                opacity: 1,
                fillOpacity: 0.9
              }}).addTo(map);
              marker.bindPopup(
                "<strong>" + p.zona_wifi + "</strong><br>" +
                "Barrio: " + p.barrio + "<br>" +
                "Dirección: " + p.direccion + "<br>" +
                "Zona: " + p.zona + " · " + p.conexion + "<br>" +
                "Energía: " + p.energia + " · APs: " + p.puntos_acceso + "<br>" +
                "<a href='" + p.url_mapa + "' target='_blank'>Abrir en Google Maps</a>"
              );
              bounds.push([p.latitud, p.longitud]);
            }});
            if (bounds.length > 1) {{
              map.fitBounds(bounds, {{ padding: [24, 24] }});
            }}
          }})();
        </script>
        """
        solara.HTML(html_mapa)


def _tarjeta_comparacion(titulo_rol: str, det: dict, color_borde: str):
    coords = (
        f"{det['latitud']}, {det['longitud']}"
        if det["latitud"] is not None and det["longitud"] is not None
        else "No reportadas"
    )
    enlace_mapa = (
        f"<div style='margin-top:12px;'><a href='{det['url_mapa']}' target='_blank' "
        f"style='color:#0f4c81;font-weight:600;font-size:13px;'>Ver en Google Maps</a></div>"
        if det["url_mapa"]
        else ""
    )
    with solara.Div(
        style={
            "flex": "1 1 320px",
            "background": "#ffffff",
            "border": "1px solid #e2e8f0",
            "border-top": f"4px solid {color_borde}",
            "border-radius": "12px",
            "padding": "18px 20px",
            "box-shadow": "0 1px 3px rgba(15, 23, 42, 0.05)",
        }
    ):
        solara.Markdown(
            f"<div style='font-size:11px;font-weight:700;color:{color_borde};"
            f"letter-spacing:0.04em;'>{titulo_rol.upper()}</div>"
            f"<div style='font-size:20px;font-weight:700;color:#0f172a;margin-top:4px;'>"
            f"{det['zona_wifi']}</div>"
            f"<div style='font-size:13px;color:#475569;margin-bottom:12px;'>"
            f"{det['barrio']} · {det['zona']}</div>"
            f"<div style='font-size:14px;color:#0f172a;line-height:1.65;'>"
            f"<div><strong>Dirección:</strong> {det['direccion']}</div>"
            f"<div><strong>Conexión:</strong> {det['conexion']}</div>"
            f"<div><strong>Puntos de acceso:</strong> {det['puntos_acceso']}</div>"
            f"<div><strong>Radio cobertura:</strong> {det['radio_cobertura']}</div>"
            f"<div><strong>Energía:</strong> {det['energia']}</div>"
            f"<div><strong>Instalación:</strong> {det['instalacion']}</div>"
            f"<div><strong>SSID:</strong> {det['ssid']}</div>"
            f"<div><strong>Coordenadas:</strong> {coords}</div>"
            f"</div>"
            f"{enlace_mapa}"
        )


@solara.component
def Page():
    seccion_activa = solara.use_reactive("Explorador y Mapa")
    zona_sel = solara.use_reactive("Todas")
    conexion_sel = solara.use_reactive("Todas")
    busqueda = solara.use_reactive("")
    zona_elegida = solara.use_reactive("")
    zona_comp_a = solara.use_reactive(TODAS_LAS_ZONAS[0] if TODAS_LAS_ZONAS else "")
    zona_comp_b = solara.use_reactive(
        TODAS_LAS_ZONAS[1] if len(TODAS_LAS_ZONAS) > 1 else (TODAS_LAS_ZONAS[0] if TODAS_LAS_ZONAS else "")
    )
    clave_input = solara.use_reactive("")

    df_filtrado = filtrar_zonas(
        DF_BASE,
        zona=zona_sel.value,
        conexion=conexion_sel.value,
        texto_barrio=busqueda.value,
    )
    resumen = calcular_resumen(df_filtrado)

    opciones_zonas_filtradas = (
        sorted(df_filtrado["zona_wifi"].dropna().unique().tolist())
        if not df_filtrado.empty and "zona_wifi" in df_filtrado.columns
        else []
    )
    if opciones_zonas_filtradas and zona_elegida.value not in opciones_zonas_filtradas:
        zona_elegida.set(opciones_zonas_filtradas[0])
    elif not opciones_zonas_filtradas and zona_elegida.value != "":
        zona_elegida.set("")

    detalle_zona = (
        obtener_detalle_zona(df_filtrado, zona_elegida.value)
        if zona_elegida.value
        else None
    )

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

    filtros_activos = []
    if zona_sel.value != "Todas":
        filtros_activos.append(f"Zona: {zona_sel.value}")
    if conexion_sel.value != "Todas":
        filtros_activos.append(f"Conexión: {conexion_sel.value}")
    if busqueda.value.strip():
        filtros_activos.append(f"Búsqueda: '{busqueda.value.strip()}'")

    estado_filtro = (
        "Mostrando resultados filtrados (" + ", ".join(filtros_activos) + ")"
        if filtros_activos
        else "Mostrando todas las zonas registradas en Acacías"
    )

    with solara.Div(style={"background": "#f8fafc", "min-height": "100vh"}):
        with solara.Column(
            style={
                "max-width": "1160px",
                "margin": "0 auto",
                "padding": "24px 20px 44px 20px",
                "gap": "18px",
            }
        ):
            solara.Title(NOMBRE_APP)

            # Encabezado institucional
            with solara.Div(
                style={
                    "background": "linear-gradient(135deg, #0f4c81 0%, #0d9488 100%)",
                    "color": "#ffffff",
                    "border-radius": "14px",
                    "padding": "22px 26px",
                    "box-shadow": "0 4px 12px rgba(15, 76, 129, 0.14)",
                }
            ):
                solara.Markdown(
                    f"<span style='display:inline-block;background:rgba(255,255,255,0.18);"
                    f"color:#f0fdfa;font-size:12px;font-weight:600;padding:4px 11px;"
                    f"border-radius:999px;letter-spacing:0.03em;margin-bottom:8px;'>"
                    f"PORTAL CIUDADANO · ACACÍAS, META</span>\n"
                    f"<h1 style='margin:0 0 6px 0;font-size:28px;font-weight:700;color:#ffffff;'>"
                    f"{NOMBRE_APP}</h1>\n"
                    f"<p style='margin:0;font-size:14px;color:#e0f2fe;max-width:820px;'>"
                    f"Explora puntos de Wi-Fi público gratuito, visualiza su ubicación en mapa, "
                    f"analiza infraestructura por barrio y compara zonas en Acacías.</p>"
                )

            # Navegación por secciones
            with solara.Row(gap="10px", style={"flex-wrap": "wrap"}):
                for sec in SECCIONES:
                    activa = seccion_activa.value == sec
                    solara.Button(
                        sec,
                        on_click=lambda s=sec: seccion_activa.set(s),
                        outlined=not activa,
                        style={
                            "background": "#0f4c81" if activa else "#ffffff",
                            "color": "#ffffff" if activa else "#0f4c81",
                            "border-color": "#0f4c81",
                            "font-weight": "600",
                        },
                    )

            # Tarjetas de métricas
            metricas = [
                ("Zonas encontradas", resumen["total_zonas"], "#0f4c81"),
                ("Puntos de acceso (APs)", resumen["total_puntos_acceso"], "#0d9488"),
                ("Barrios cubiertos", resumen["barrios_cubiertos"], "#1e3a8a"),
            ]
            with solara.Row(gap="16px", style={"flex-wrap": "wrap"}):
                for etiqueta, valor, color_borde in metricas:
                    with solara.Div(
                        style={
                            "flex": "1 1 220px",
                            "background": "#ffffff",
                            "border": "1px solid #e2e8f0",
                            "border-top": f"4px solid {color_borde}",
                            "border-radius": "12px",
                            "padding": "16px 20px",
                            "box-shadow": "0 1px 3px rgba(15, 23, 42, 0.05)",
                        }
                    ):
                        solara.Markdown(
                            f"<div style='font-size:28px;font-weight:700;color:#0f172a;"
                            f"font-variant-numeric:tabular-nums;line-height:1.15;'>"
                            f"{valor}</div>"
                            f"<div style='font-size:13px;font-weight:500;color:#475569;"
                            f"margin-top:6px;'>{etiqueta}</div>"
                        )

            # SECCIÓN 1: EXPLORADOR + FICHA + MAPA INTERACTIVO
            if seccion_activa.value == "Explorador y Mapa":
                with solara.Div(
                    style={
                        "background": "#ffffff",
                        "border": "1px solid #e2e8f0",
                        "border-radius": "12px",
                        "padding": "18px 20px",
                        "box-shadow": "0 1px 3px rgba(15, 23, 42, 0.04)",
                    }
                ):
                    with solara.Row(gap="16px", style={"align-items": "end", "flex-wrap": "wrap"}):
                        with solara.Div(style={"flex": "1 1 190px"}):
                            solara.Select(
                                label="Filtrar por Zona", value=zona_sel, values=OPCIONES_ZONA
                            )
                        with solara.Div(style={"flex": "1 1 210px"}):
                            solara.Select(
                                label="Tipo de Conexión",
                                value=conexion_sel,
                                values=OPCIONES_CONEXION,
                            )
                        with solara.Div(style={"flex": "2 1 260px"}):
                            solara.InputText(label="Buscar barrio o zona Wi-Fi", value=busqueda)
                        if filtros_activos:
                            solara.Button(
                                "Limpiar filtros",
                                on_click=lambda: _limpiar_filtros(zona_sel, conexion_sel, busqueda),
                                outlined=True,
                            )

                    solara.Markdown(
                        f"<p style='margin:12px 0 0 0;font-size:13px;color:#475569;'>"
                        f"<strong style='color:#0f4c81;'>Estado:</strong> {estado_filtro}</p>"
                    )

                solara.Markdown("### Listado de puntos Wi-Fi disponibles")
                if len(tabla) == 0:
                    solara.Warning("No se encontraron zonas Wi-Fi con los filtros seleccionados.")
                else:
                    solara.DataFrame(tabla, items_per_page=10)

                    solara.Markdown("### Detalle de la zona seleccionada")
                    with solara.Div(
                        style={
                            "background": "#ffffff",
                            "border": "1px solid #cbd5e1",
                            "border-left": "5px solid #0d9488",
                            "border-radius": "12px",
                            "padding": "20px 22px",
                            "box-shadow": "0 2px 6px rgba(15, 23, 42, 0.04)",
                        }
                    ):
                        solara.Select(
                            label="Selecciona una zona para ver su ficha completa",
                            value=zona_elegida,
                            values=opciones_zonas_filtradas,
                        )

                        if detalle_zona:
                            enlaces_html = []
                            if detalle_zona["url_mapa"]:
                                enlaces_html.append(
                                    f"<a href='{detalle_zona['url_mapa']}' target='_blank' "
                                    f"style='display:inline-block;margin-top:12px;margin-right:14px;"
                                    f"background:#0f4c81;color:#ffffff;padding:8px 14px;"
                                    f"border-radius:8px;text-decoration:none;font-size:13px;"
                                    f"font-weight:600;'>Abrir ubicación en Google Maps</a>"
                                )
                            if detalle_zona["url_imagen"]:
                                enlaces_html.append(
                                    f"<a href='{detalle_zona['url_imagen']}' target='_blank' "
                                    f"style='display:inline-block;margin-top:12px;"
                                    f"color:#0d9488;font-size:13px;font-weight:600;'>"
                                    f"Ver foto de referencia (Drive)</a>"
                                )

                            coords_texto = (
                                f"{detalle_zona['latitud']}, {detalle_zona['longitud']}"
                                if detalle_zona["latitud"] is not None
                                and detalle_zona["longitud"] is not None
                                else "No reportadas"
                            )

                            solara.Markdown(
                                f"<div style='margin-top:14px;'>"
                                f"<div style='font-size:20px;font-weight:700;color:#0f4c81;'>"
                                f"{detalle_zona['zona_wifi']}</div>"
                                f"<div style='font-size:13px;color:#0d9488;font-weight:600;"
                                f"margin-top:2px;'>{detalle_zona['zona']} · "
                                f"{detalle_zona['conexion']}</div>"
                                f"<div style='margin-top:14px;display:grid;"
                                f"grid-template-columns:repeat(auto-fit,minmax(220px,1fr));"
                                f"gap:10px;font-size:14px;color:#0f172a;'>"
                                f"<div><strong>Barrio:</strong> {detalle_zona['barrio']}</div>"
                                f"<div><strong>Dirección:</strong> {detalle_zona['direccion']}</div>"
                                f"<div><strong>SSID:</strong> {detalle_zona['ssid']}</div>"
                                f"<div><strong>Puntos de acceso:</strong> {detalle_zona['puntos_acceso']}</div>"
                                f"<div><strong>Radio cobertura:</strong> {detalle_zona['radio_cobertura']}</div>"
                                f"<div><strong>Instalación:</strong> {detalle_zona['instalacion']}</div>"
                                f"<div><strong>Energía:</strong> {detalle_zona['energia']}</div>"
                                f"<div><strong>Coordenadas:</strong> {coords_texto}</div>"
                                f"</div>"
                                f"{''.join(enlaces_html)}"
                                f"</div>"
                            )

                _render_mapa_interactivo(obtener_puntos_mapa(df_filtrado))

            # SECCIÓN 2: RANKING Y ANÁLISIS DE INFRAESTRUCTURA + CSV
            elif seccion_activa.value == "Ranking y Análisis":
                solara.Markdown(
                    f"<p style='margin:0;font-size:13px;color:#475569;'>"
                    f"<strong style='color:#0f4c81;'>Contexto del análisis:</strong> "
                    f"{estado_filtro}</p>"
                )
                desglose_conexion = resumir_por_columna(df_filtrado, "conexion")
                desglose_zona = resumir_por_columna(df_filtrado, "zona")
                desglose_energia = resumir_por_columna(df_filtrado, "energia")
                desglose_instalacion = resumir_por_columna(df_filtrado, "instalacion")
                top_barrios = ranking_barrios(df_filtrado, top_n=10)

                _render_desglose_barras(
                    "Distribución por tipo de conexión", desglose_conexion, "#0f4c81"
                )
                _render_desglose_barras(
                    "Distribución por zona (Urbana / Rural)", desglose_zona, "#0d9488"
                )
                _render_desglose_barras(
                    "Respaldo energético (SOLAR / AC)", desglose_energia, "#0284c7"
                )
                _render_desglose_barras(
                    "Tipo de instalación física", desglose_instalacion, "#1e3a8a"
                )

                with solara.Div(
                    style={
                        "background": "#ffffff",
                        "border": "1px solid #e2e8f0",
                        "border-radius": "12px",
                        "padding": "20px 22px",
                        "box-shadow": "0 1px 3px rgba(15, 23, 42, 0.04)",
                    }
                ):
                    solara.Markdown("### Ranking de barrios con más puntos de acceso (Top 10)")
                    if not top_barrios:
                        solara.Info("No hay barrios disponibles para el filtro actual.")
                    else:
                        max_aps = max((b["puntos_acceso"] for b in top_barrios), default=1) or 1
                        filas_html = []
                        for idx, b in enumerate(top_barrios, start=1):
                            ancho = max(8, int(round((b["puntos_acceso"] / max_aps) * 100)))
                            filas_html.append(
                                f"<div style='margin-bottom:12px;'>"
                                f"<div style='display:flex;justify-content:space-between;"
                                f"font-size:14px;color:#0f172a;margin-bottom:4px;'>"
                                f"<span><strong>#{idx} {b['barrio']}</strong></span>"
                                f"<span style='color:#475569;font-variant-numeric:tabular-nums;'>"
                                f"<strong>{b['puntos_acceso']} APs</strong> · {b['zonas']} zonas</span>"
                                f"</div>"
                                f"<div style='width:100%;background:#f1f5f9;border-radius:999px;height:9px;"
                                f"overflow:hidden;'>"
                                f"<div style='width:{ancho}%;background:#0d9488;height:100%;"
                                f"border-radius:999px;'></div>"
                                f"</div>"
                                f"</div>"
                            )
                        solara.Markdown("".join(filas_html))

                with solara.Div(
                    style={
                        "background": "#ffffff",
                        "border": "1px solid #e2e8f0",
                        "border-radius": "12px",
                        "padding": "18px 22px",
                    }
                ):
                    solara.Markdown("### Exportar resultados actuales")
                    if not df_filtrado.empty:
                        csv_bytes = df_filtrado.to_csv(index=False).encode("utf-8")
                        solara.FileDownload(
                            csv_bytes,
                            filename="zonas_wifi_acacias_filtrado.csv",
                            label="Descargar selección actual en CSV",
                        )
                    else:
                        solara.Info("Ajusta los filtros para habilitar la descarga CSV.")

            # SECCIÓN 3: COMPARADOR ENTRE DOS ZONAS
            elif seccion_activa.value == "Comparador de Zonas":
                with solara.Div(
                    style={
                        "background": "#ffffff",
                        "border": "1px solid #e2e8f0",
                        "border-radius": "12px",
                        "padding": "20px 22px",
                    }
                ):
                    solara.Markdown("### Comparar dos zonas Wi-Fi lado a lado")
                    solara.Markdown(
                        "Elige dos puntos del catálogo para contrastar su cobertura, "
                        "tipo de conexión, energía, instalación y ubicación."
                    )
                    with solara.Row(gap="16px", style={"flex-wrap": "wrap"}):
                        with solara.Div(style={"flex": "1 1 260px"}):
                            solara.Select(
                                label="Zona A", value=zona_comp_a, values=TODAS_LAS_ZONAS
                            )
                        with solara.Div(style={"flex": "1 1 260px"}):
                            solara.Select(
                                label="Zona B", value=zona_comp_b, values=TODAS_LAS_ZONAS
                            )

                par = comparar_zonas(DF_BASE, zona_comp_a.value, zona_comp_b.value)
                if par:
                    with solara.Row(gap="16px", style={"flex-wrap": "wrap"}):
                        _tarjeta_comparacion("Zona A", par["zona_a"], "#0f4c81")
                        _tarjeta_comparacion("Zona B", par["zona_b"], "#0d9488")

            # SECCIÓN 4: DATOS Y ADMINISTRACIÓN
            else:
                with solara.Div(
                    style={
                        "background": "#ffffff",
                        "border": "1px solid #e2e8f0",
                        "border-radius": "12px",
                        "padding": "20px 22px",
                    }
                ):
                    solara.Markdown("### Fuente de datos abiertos y verificación técnica")
                    solara.Markdown(
                        f"**Conjunto de datos:** [{FUENTE_NOMBRE}]({FUENTE_URL})  \n"
                        f"**Licencia:** {FUENTE_LICENCIA}"
                    )

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
                f"<span style='font-size:13px;color:#475569;'>"
                f"<strong>Fuente:</strong> <a href='{FUENTE_URL}' target='_blank'>{FUENTE_NOMBRE}</a> · "
                f"{FUENTE_LICENCIA}</span>"
            )
