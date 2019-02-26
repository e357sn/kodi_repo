# -*- coding: utf-8 -*-
import json
import urllib2
import re
import xbmcplugin
from simpleplugin import RoutedPlugin
plugin = RoutedPlugin()

@plugin.route('/')
def root():
    listing = get_station_list()
    listing.append({
        'label': 'Крем и Хруст',
        'url': plugin.url_for('podcast'),
        'thumb': 'http://www.radiorecord.ru/upload/resize_cache/uf/902/372_372_1/902e949801fba494cda263b179bcd7e9.png',
        'is_folder': True,
        'info': {
            'music': {
                'genre': 'Подкаст',
                'mediatype': 'song'
            }
        }
    })
    return plugin.create_listing(listing, content='albums', view_mode=500, sort_methods=xbmcplugin.SORT_METHOD_LABEL, cache_to_disk=True)

@plugin.route('/podcast', name='podcast')
def podcast():
    USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    url = 'http://www.radiorecord.ru/radio/heroes/777123/'
    headers = {'User-Agent' : USER_AGENT}
    request = urllib2.Request(url, None, headers)
    response = urllib2.urlopen(request).read()
    test = re.finditer(r'item_url="(http:.+?)">.+?class="name"> (.+?)<', response, re.DOTALL)
    listing = []
    num = 0
    for i in test:
        name = i.group(2)
        num = num + 1
        listing.append({
            'label': "Крем и Хруст - %s" % name,
            'thumb': 'http://www.radiorecord.ru/upload/iblock/8aa/8aa72169cfa40478ac72ff015eeeadd9.png',
            'fanart': 'https://www.infpol.ru/upload/iblock/ad0/ad009fba6d7082b0009a8fa679474e71.jpg',
            'is_folder': False,
            'is_playable': True,
            'url': plugin.url_for('play', url=i.group(1)),
            'info': {
                'music': {
                        'tracknumber': num,
                        'title': name,
                        'artist': "Кремов и Хрусталев",
                        'mediatype': 'song',
                    }
                }
            })
    return plugin.create_listing(listing, content='songs', cache_to_disk=True)

@plugin.route('/play')
def play():
    return plugin.resolve_url(plugin.params.url, succeeded=True)

def get_station_list():
    page = urllib2.urlopen('http://www.radiorecord.ru/radioapi/stations/').read()
    apiResp = json.loads(page.decode('utf-8'))
    stations = apiResp['result']
    listing = []
    num = 0
    for station in stations:
        listing.append({
            'label': station['title'],
            'thumb': station['icon_png'],
            'icon': station['icon_png'].replace('3x.', '2x.'),
            'is_folder': False,
            'is_playable': True,
            'url': plugin.url_for('play', url=station['stream_320']),
            'info': {
                'music': {
                        'genre': station['title'],
                        'artist': station['artist'],
                        'mediatype': 'song',
                    }
                }
            })
    return listing
    

if __name__ == '__main__':
    api_page = 'http://www.radiorecord.ru/radioapi/stations/'
    plugin.run()