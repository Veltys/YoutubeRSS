#!/usr/bin/env python3
# -*- coding: utf-8 -*-


'''!
    YoutubeRSS

    @file:           main.py
    @brief:          Sistema lector de los canales suscritos de YouTube dado un usuario concreto

    @author:         Veltys
    @Date:           2022-03-29
    @version:        1.0.2
    @usage:          python3 main.py channelID [-f FILENAME]
    @note:
'''


from html import escape                                                         # Funcionalidad de codificación de entidades HTML
import argparse                                                                 # Funcionalidades del procesador de argumentos
import os                                                                       # Funcionalidades varias del sistema operativo
import sys                                                                      # Funcionalidades varias del sistema

import google_auth_oauthlib.flow
import googleapiclient.discovery
# import googleapiclient.errors


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

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials = credentials)

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


def saveFile(file, filename):
    '''!
        Guarda el contenido de la variable en el archivo seleccionado

        @param file:        Contenido del archivo a guardar
        @param filename:    Nombre del archivo a guardar

        @return:            Resultado de la operación de guardado (True / False)
    '''

    try:
        f = open(filename, 'w', encoding = 'utf-8')

    except PermissionError:
        return False

    else:
        f.write(file + "\n")
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


    if saveFile(generateOPML(responses), args.filename):
        print(f'Subscripciones guardadas correctamente en el archivo <{args.filename}>')

    else:
        sys.exit(f'Ha sido imposible guardar las subscripciones en el archivo <{args.filename}>. Por favor inténtelo de nuevo o elija otro nombre de archivo.')


if __name__ == "__main__":
    main(sys.argv[1:])
