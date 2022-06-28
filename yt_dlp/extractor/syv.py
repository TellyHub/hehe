from .common import InfoExtractor
from ..utils import int_or_none, str_or_none, traverse_obj


class SyvIE(InfoExtractor):
    _VALID_URL = r'https?://24syv.dk/episode/(?P<id>[\w-]+)'
    _TESTS = [{
        'url': 'https://24syv.dk/episode/isabella-arendt-stiller-op-for-de-konservative-2',
        'info_dict': {
            'id': '12215',
            'ext': 'mp3',
            'title': 'Isabella Arendt stiller op for De Konservative',
            'display_id': 'isabella-arendt-stiller-op-for-de-konservative-2',
            'thumbnail': 'https://d1bm3dmew779uf.cloudfront.net/rss/show/5196630/4ceb292fd51c555feb652edfdf7291ed.png',
            'duration': 3218,
            
        }
    }]
    
    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        nextjs_data = self._search_nextjs_data(webpage, video_id)
        json_data = traverse_obj(
            nextjs_data, ('props','pageProps', 'episodeDetails', ..., 'details'))[0]
              
        return {
            'id': str_or_none(json_data['ID']),
            'title': json_data.get('post_content'),
            'url': json_data['enclosure'],
            'display_id': json_data.get('slug') or video_id,
            'thumbnail': json_data.get('image_url'),
            'duration': int_or_none(json_data.get('duration')),
            
        }
