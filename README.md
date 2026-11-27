# Buscador de Zonas Wi-Fi Gratis - Acacías (Meta)

Aplicación web interactiva en Python (Solara) para consultar puntos de Wi-Fi público gratuito en el municipio de Acacías usando datos abiertos oficiales de `datos.gov.co`.

- **URL pública:** *(Pendiente de despliegue en Render)*
- **Fuente de datos:** [Alcaldía de Acacías - datos.gov.co](https://www.datos.gov.co/Ciencia-Tecnolog-a-e-Innovaci-n/Zonas-Wifi-Gratis-Municipio-de-Acac-as/r7mn-ty3w/about_data)
- **Ejecución local con Docker:** `docker build -t app-wifi-acacias . && docker run --rm --env-file .env -p 8765:8765 app-wifi-acacias`
