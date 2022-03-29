# YoutubeRSS
Small Python program to get a Youtube user's subscriptions and convert them to OPML 1.0 format [![Codacy Badge](https://app.codacy.com/project/badge/Grade/a5b0c10762c14877a1926981b9dd64bf)](https://www.codacy.com/gh/Veltys/YoutubeRSS/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Veltys/YoutubeRSS&amp;utm_campaign=Badge_Grade)


## Descripción
Pequeño programa en Python para obtener las suscripciones de un usuario de Youtube y convertirlas al formato OPML 1.0


## Requisitos
- [Python 3.9 o superior](https://www.python.org/downloads/)
- [Google client library](https://developers.google.com/docs/api/quickstart/python#step_1_install_the_google_client_library)
- [Credenciales de autorización de la API de Youtube en formato JSON](https://developers.google.com/youtube/registering_an_application)


## Agradecimientos, fuentes consultadas y otros créditos
* A la [documentación oficial de Python](https://docs.python.org/3/), por motivos evidentes.
* A la [documentación oficial de la API de Youtube](https://developers.google.com/youtube/v3), porque me ha facilitado mucho el hacer este proyecto.


## Changelog
Su formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) y este proyecto se adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


### [Por hacer (*TODO*)]
- [ ] Conversión (automática) usuario de Youtube ➡ ID de Youtube
- [ ] Integración con la API de Feedly


## [1.0.2] - 2022-03-29
### Arreglado
- Los nombres de los canales necesitan ser *escapados*

### Eliminado
- Código de depuración no necesario en la rama **master**

## [1.0.1] - 2022-03-02
### Arreglado
- Calidad de código

### [1.0.0] - 2022-03-02
### Añadido
- Script con las funcionalidades esperadas