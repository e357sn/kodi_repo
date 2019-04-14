# -*- coding: utf-8 -*-
import json
import urllib2
import xbmcgui
import urllib
from simpleplugin import RoutedPlugin


plugin = RoutedPlugin()
chsv_page = 'http://chsv.ml/releases.json'
ndr_page = 'http://ndr-ru.surge.sh/releases.json'


@plugin.route('/')
def root():
    listing = get_releases_list()
    return plugin.create_listing(listing, content='movies', cache_to_disk=True)


@plugin.route('/film')
def film():
    use_torrserve = plugin.get_setting('use_engine', True)
    id = int(plugin.params.id)
    info = []
    with plugin.get_storage() as storage:  # Create a storage object
        info = storage[str(id)]

    list_torrent = []
    list = []
    for i in info:
        list_torrent.append(i['magnet'])
        date = i['date'].split('-')
        lic = ""
        if i['license']:
            lic = u"Лицензия"
        list.append(i['type'].replace('UHD', '4K')+" / "+date[2]+"."+date[1]+"."+date[0]+" / "+ lic)
    
    dialog = xbmcgui.Dialog()
    ret = dialog.select('Список торрентов', list=list)
    if ret > -1:
        t_url = list_torrent[ret]
        if use_torrserve:
            ip = plugin.get_setting('ts-host', True)
            port = plugin.get_setting('ts-port', True)
            path = "http://{0}:{1}/torrent/play?link={2}&preload=0&file=0&save=true".format(ip, port, t_url)
        else:
            path = "plugin://plugin.video.elementum/play?uri={0}".format(t_url)
        return plugin.resolve_url(path, succeeded=True)
    return False

@plugin.cached(60)
def get_releases_list():
    api_page = plugin.get_setting('api_page', True)
    if api_page:
        api_page = ndr_page
    else:
        api_page = chsv_page
    page = urllib2.urlopen(api_page).read()
    apiResp = json.loads(page.decode('utf-8'))
    releases = apiResp
    listing = []
    num = 0
    for release in releases:
        with plugin.get_storage() as storage:  # Create a storage object
            storage[str(release['filmID'])] = release['torrents']  # Store data
        timestr = release['filmLength']
        ftr = [3600,60]
        duration = sum([a*b for a,b in zip(ftr, map(int,timestr.split(':')))])
        use_proxy = plugin.get_setting('unblock_ua', True)
        if use_proxy:
            release['bigPosterURL'] = unblock_ua(release['bigPosterURL'])
            release['posterURL'] = unblock_ua(release['posterURL'])

        listing.append({
            'label': release['nameRU'],
            'label2': release['torrentsDate'],
            'art': {
                'thumb': release['bigPosterURL'],
                'poster': release['posterURL'],
                'fanart': release['bigPosterURL']
            },
            'info': {
                'video': {
                    'cast': release['actors'].split(','),
                    'director': release['directors'].split(','),
                    'genre': release['genre'].split(','),
                    'country': release['country'],
                    'year': int(release['year']),
                    'rating': float(release['ratingFloat']),
                    'plot': release['description'],
                    'plotoutline': release['description'],
                    'title': release['nameRU'],
                    'sorttitle': release['nameRU'],
                    'duration': duration,
                    'originaltitle': release['nameOriginal'],
                    'premiered': release['premierDate'],
                    'votes': int(release['ratingKPCount']),
                    'trailer': release['trailerURL'],
                    'mediatype': 'movie',
                    'tagline': release['torrentsDateType'],
                    'mpaa': release['ratingMPAA'] if release['ratingAgeLimits'] == "" else release['ratingAgeLimits']+"+",
                }
            },
            'is_folder': False,
            'is_playable': True,
            'url': plugin.url_for('film', id=release['filmID']),
            })
    return listing


mirror_list=[
	'http://www.pitchoo.net/zob_/index.php?q=', 
	'http://thely.fr/proxy/?q=', 
	'http://xawos.ovh/index.php?q=', 
	'http://prx.afkcz.eu/prx/index.php?q=', 
	'https://derzeko.de/Proxy/index.php?q=', 
	'https://dev.chamoun.fr/proxy/index.php?q=',
]


def unblock_ua(url):
    import base64
    import random
    b64=base64.b64encode(url)
    redir="{0}{1}".format(mirror_list[random.randint(0, 5)], urllib.quote_plus(b64))
    return redir


if __name__ == '__main__':
    plugin.run()