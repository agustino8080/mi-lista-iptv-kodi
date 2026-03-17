import sys
import xbmcgui
import xbmcplugin
import xbmc
import urllib.request
import urllib.parse
import re

addon_handle = int(sys.argv[1])
M3U_URL = 'https://iptv-org.github.io/iptv/index.m3u'  # Tu lista específica

def cargar_lista_m3u(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Kodi/20.0'})
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')
        return data
    except:
        xbmcgui.Dialog().ok('Error', 'No se pudo cargar la lista M3U. Verifica la URL.')
        return None

def parsear_m3u(contenido):
    canales = []
    lines = contenido.split('\n')
    actual = None
    for line in lines:
        line = line.strip()
        if line.startswith('#EXTINF'):
            match = re.search(r'#EXTINF:.*?,(.*?)(?:\s|$)', line)
            if match:
                nombre = match.group(1).strip()
                actual = {'name': nombre}
        elif line.startswith('http') and actual:
            actual['url'] = line
            canales.append(actual)
            actual = None
    return canales

def crear_menu():
    xbmcplugin.setContent(addon_handle, 'videos')
    contenido = cargar_lista_m3u(M3U_URL)
    if not contenido:
        return
    canales = parsear_m3u(contenido)
    dialog = xbmcgui.DialogProgress()
    dialog.create('Cargando canales...', 'Procesando...')
    total = len(canales)
    for i, canal in enumerate(canales[:200]):  # Limita a 200 por rendimiento
        li = xbmcgui.ListItem(canal['name'])
        li.setInfo('video', {'title': canal['name'], 'mediatype': 'video'})
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=canal['url'], listitem=li, isFolder=False)
        percent = (i / total) * 100
        dialog.update(int(percent))
    dialog.close()
    xbmcplugin.endOfDirectory(addon_handle)

if __name__ == '__main__':
    crear_menu()
