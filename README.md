# Buscador de Zonas Wi-Fi Gratis - Acacías (Meta)

Aplicación web interactiva desarrollada en **Python** y **Solara** para consultar, filtrar, analizar y exportar información sobre los puntos de Wi-Fi público gratuito del municipio de **Acacías (Meta)** a partir de datos abiertos oficiales.

- **Aplicación en línea:** [https://proyecto-wifi-acacias.onrender.com](https://proyecto-wifi-acacias.onrender.com)
- **Fuente de datos abiertos:** [Alcaldía de Acacías - Datos Abiertos Colombia (datos.gov.co)](https://www.datos.gov.co/Ciencia-Tecnolog-a-e-Innovaci-n/Zonas-Wifi-Gratis-Municipio-de-Acac-as/r7mn-ty3w/about_data)
- **Licencia:** Licencia Abierta de Datos Públicos de Colombia (Creative Commons Attribution 4.0)

## Funcionalidades y secciones

- **Explorador de Zonas:** filtrado por zona (`Urbana` / `Rural`), tipo de conexión y búsqueda por barrio o nombre de zona Wi-Fi, con resumen de estado activo, botón para limpiar filtros, tarjetas de métricas (`Zonas encontradas`, `Puntos de acceso (APs)`, `Barrios cubiertos`), tabla paginada y **ficha de detalle** con coordenadas y enlace directo a Google Maps.
- **Análisis y Descarga:** desglose visual de zonas y puntos de acceso por tipo de conexión y por zona, además de exportación en **CSV** del conjunto filtrado actual.
- **Datos y Administración:** información de la fuente oficial, licencia y panel técnico de verificación protegido mediante clave de administrador (`CLAVE_ADMIN`).

## Estructura del proyecto

- `app.py`: interfaz web en Solara, navegación por secciones, visualizaciones y panel de verificación.
- `reglas.py`: carga y normalización de `datos/zonas_wifi.csv`, filtros, resúmenes, coordenadas/mapas y validación de clave.
- `tests/test_reglas.py`: pruebas automatizadas con `pytest`.
- `Dockerfile` y `.dockerignore`: empaquetado del contenedor para despliegue.
- `.github/workflows/ci.yml`: integración continua que ejecuta `pytest` en cada `push` o `pull request`.

## Variables de entorno y seguridad

Las credenciales y configuraciones sensibles se inyectan mediante variables de entorno (nunca se suben al repositorio; `.env` está ignorado en `.gitignore`):

- `NOMBRE_APP`: título mostrado en la aplicación.
- `CLAVE_ADMIN`: clave requerida en el panel técnico de verificación.

## Ejecución local y pruebas

### Pruebas automatizadas

`pytest -v`

### Contenedor Docker

`docker build -t app-wifi-acacias .`
`docker run --rm --env-file .env -p 8765:8765 app-wifi-acacias`
