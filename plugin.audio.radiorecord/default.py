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
        'url': plugin.url_for('podcast', id='777123'),
        'thumb': 'http://www.radiorecord.ru/upload/resize_cache/uf/902/372_372_1/902e949801fba494cda263b179bcd7e9.png',
        'is_folder': True,
        'info': {
            'music': {
                'genre': 'Подкаст',
                'mediatype': 'song'
            }
        }
    })
    listing.append({
        'label': 'Record MegaMix',
        'url': plugin.url_for('podcast', id='1144137'),
        'thumb': 'http://www.radiorecord.ru/upload/resize_cache/iblock/492/372_372_1/492a8db834aa7182b004d2dfb0414e90.jpg',
        'is_folder': True,
        'info':{
            'music':{
                'genre': 'Подкаст',
                'mediatype': 'song',
                }
            }
        })
    return plugin.create_listing(listing, content='albums', view_mode=500, sort_methods=xbmcplugin.SORT_METHOD_LABEL, cache_to_disk=True)

@plugin.route('/podcast/<id>', name='podcast')
def podcast(id):
    USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    url = 'http://www.radiorecord.ru/radio/heroes/{0}/'.format(id)
    headers = {'User-Agent' : USER_AGENT}
    request = urllib2.Request(url, None, headers)
    response = urllib2.urlopen(request).read()
    podcasts = re.finditer(r'item_url="(http:.+?)">.+?class="artist">(.+?) <.+?class="name"> (.+?)<', response, re.DOTALL)
    arts = re.search(r'vk_img="(.+?)"', response)
    listing = []
    num = 0
    for i in podcasts:
        thumb = arts.group(1)
        fanart = ''
        if id == "777123":
            fanart = 'https://www.infpol.ru/upload/iblock/ad0/ad009fba6d7082b0009a8fa679474e71.jpg'
        elif id == "1144137":
            fanart = 'https://viper-fm.ru/gallery_gen/f3d28b5cb13de8a9e6fbed9b7c2b20c2.jpg'
        artist = i.group(2)
        name = i.group(3)
        num = num + 1
        listing.append({
            'label': "%s - %s" % (artist, name),
            'thumb': 'http://www.radiorecord.ru{0}'.format(thumb),
            'fanart': fanart,
            'is_folder': False,
            'is_playable': True,
            'url': plugin.url_for('play', url=i.group(1)),
            'info': {
                'music': {
                        'tracknumber': num,
                        'title': name,
                        'artist': artist,
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