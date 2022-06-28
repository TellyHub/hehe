from .common import InfoExtractor
from ..utils import str_or_none


class SyvIE(InfoExtractor):
    _VALID_URL = r'https?://24syv.dk/episode/<id>'
    _TESTS = [{
        'url': 'https://24syv.dk/episode/isabella-arendt-stiller-op-for-de-konservative-2',
        'info_dict': {
            'id': 'fixme',
            'ext': 'mp4',
            'title': 'fixme',
        }
    }]
    
    def _real_extract(self, url):
        video_id = self._match_id(url)
        json_data = self._search_nextjs_data(
            self._download_webpage(url, video_id), video_id)['props']['pageProps']['episodeDetails']['details']
            
        
        return {
            'id': str_or_none(json_data['id']),
            'title': json_data.get('post_content'),
            'url': json_data['enclosure'],
            'display_id': json_data.get('slug') or video_id,
            'thumbnail': json_data.get('image_url'),
            'duration': json_data.get('duration'),
            
        }