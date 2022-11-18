#!/usr/bin/env python3
# -*- coding: utf-8 -*-


'''!
    YoutubeRSS

    @file:           main.py
    @brief:          Sistema lector de los canales suscritos de YouTube dado un usuario concreto

    @author:         Veltys
    @Date:           2022-11-18
    @version:        1.0.3
    @usage:          python3 main.py channelID [-f FILENAME]
    @note:
'''


from html import escape                                                         # Funcionalidad de codificación de entidades HTML
import argparse                                                                 # Funcionalidades del procesador de argumentos
import os                                                                       # Funcionalidades varias del sistema operativo
import sys                                                                      # Funcionalidades varias del sistema

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery


def parseClArgs(argv):
    '''!
        Procesa los argumentos pasados al programa

        @param argv:    Vector de argumentos

        @return:        Argumentos procesados
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('channel', type = str, help = 'ID del usuario de Youtube')
    parser.add_argument('-f', '--filename', type = str, default = 'Youtube subscriptions.opml', dest = 'filename', help = 'Nombre del archivo a guardar')

    args = parser.parse_args(argv)

    return args


def apiQuery(channel):
    '''!
        Realiza la consulta contra la API de Youtube de forma iterativa hasta obtener todos los resultados y la devuelve

        @param channel:     ID del usuario de Youtube a procesar

        @return:            Respuesta de la API
    '''

    scopes = ['https://www.googleapis.com/auth/youtube.readonly']

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    api_service_name = 'youtube'
    api_version = 'v3'
    client_secrets_file = 'client_secret.json'
    token_file = 'token.json'
    creds = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            creds = flow.run_local_server(port = 0)

        if not saveFile(creds.to_json(), token_file):
            print(f'Aviso: Error al guardar las credenciales de acceso a las subscripciones en el archivo <{token_file}>.', file = sys.stderr)
            print(f'Aviso: Ha sido imposible guardar las credenciales de acceso a las subscripciones en el archivo <{token_file}>. Se puede continuar, pero la próxima vez se volverán a pedir.')

    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials = creds)

    responses = []

    request = youtube.subscriptions().list(
        part = 'id,snippet,contentDetails',
        channelId = channel,
        maxResults = 100
    )

    responses.append(request.execute())

    while responses[-1]['kind'] == 'youtube#SubscriptionListResponse':
        try:
            request = youtube.subscriptions().list(
                part = 'id,snippet,contentDetails',
                channelId = channel,
                maxResults = 100,
                pageToken = responses[-1]['nextPageToken']
            )

        except KeyError:
            break

        else:
            responses.append(request.execute())

    return responses


def generateOPML(responses):
    '''!
        Genera un archivo OPML 1.0 válido según https://web.archive.org/web/20160304125338/http://dev.opml.org/spec1.html

        @param responses:   Respuesta de la API de Youtube

        @return:            Documento en formato OPML
    '''

    opml = '''<?xml version="1.0" encoding="UTF-8"?>

<opml version="1.0">
    <head>
        <title>Youtube subscriptions</title>
    </head>
    <body>
        <outline text="Youtube">'''

    for r in responses:
        for _, i in enumerate(r['items']):
            title = escape(i["snippet"]["title"])

            opml += "\n" + f'        <outline type="rss" text="{title}" title="{title}" xmlUrl="https://www.youtube.com/feeds/videos.xml?channel_id={i["snippet"]["resourceId"]["channelId"]}" htmlUrl="https://www.youtube.com/channel/{i["snippet"]["resourceId"]["channelId"]}" />'

    opml += '''
        </outline>
    </body>
</opml>

'''
    return opml


def saveFile(content, filename):
    '''!
        Guarda el contenido de la variable en el archivo seleccionado

        @param content:     Contenido del archivo a guardar
        @param filename:    Nombre del archivo a guardar

        @return:            Resultado de la operación de guardado (True / False)
    '''

    try:
        f = open(filename, 'w', encoding = 'utf-8')

    except PermissionError:
        return False

    else:
        f.write(content + "\n")
        f.close()

        return True


def main(argv):
    '''!
        Ejecuta las operaciones necesarias para generar el archivo

        @param argv:    Argumentos del programa

        @return:        Código de retorno
    '''

    args = parseClArgs(argv)

    responses = apiQuery(args.channel)


    if not responses:
        sys.exit('Ha sido imposible recuperar las subscripciones. Por favor inténtelo de nuevo más tarde.')

    else:
        if not saveFile(generateOPML(responses), args.filename):
            sys.exit(f'Ha sido imposible guardar las subscripciones en el archivo <{args.filename}>. Por favor inténtelo de nuevo o elija otro nombre de archivo.')

        else:
            print(f'Subscripciones guardadas correctamente en el archivo <{args.filename}>')


if __name__ == "__main__":
    main(sys.argv[1:])
