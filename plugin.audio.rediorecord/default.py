import json
import sys
import urllib
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
from urllib2 import urlopen, Request

def build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)
    
def get_page(url):
    return urlopen(Request(url)).read()
    
def parse_page(page):
    resp_dict = json.loads(page.decode('utf-8'))
    stations = resp_dict['result']
    stations_sorted = sorted(stations, key=lambda x: x['title'])
    return stations_sorted
    
def build_station_list(stations):
    station_list = []
    for station in stations:
        li = xbmcgui.ListItem(
            label=station['title'],
            thumbnailImage=station['icon_png'],
        )
        li.setInfo('music', { 
                    'artist': station['artist'],
                    'titles': station['song'],
                    })
        li.setProperty('IsPlayable', 'true')
        url = build_url({'mode': 'stream', 'url': station['stream_320'], 'title': station['prefix']})
        station_list.append((url, li, False))
    xbmcplugin.addDirectoryItems(addon_handle, station_list, len(station_list))
    xbmcplugin.setContent(addon_handle, 'albums')
    xbmc.executebuiltin('Container.SetViewMode(500)')
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
    
def play_station(url):
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    
def main():
    args = urlparse.parse_qs(sys.argv[2][1:])
    mode = args.get('mode', None)
    
    if mode is None:
        page = get_page(api_page)
        content = parse_page(page)
        build_station_list(content)
    elif mode[0] == 'stream':
        play_station(args['url'][0])
    
if __name__ == '__main__':
    api_page = 'http://www.radiorecord.ru/radioapi/stations/'
    addon_handle = int(sys.argv[1])
    main()