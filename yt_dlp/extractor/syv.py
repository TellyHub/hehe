from .common import InfoExtractor
from ..utils import int_or_none, str_or_none, traverse_obj


class SyvIE(InfoExtractor):
    _VALID_URL = r'https?://24syv\.dk/episode/(?P<id>[\w-]+)'
    _TESTS = [{
        'url': 'https://24syv.dk/episode/isabella-arendt-stiller-op-for-de-konservative-2',
        'info_dict': {
            'id': '12215',
            'ext': 'mp3',
            'title': 'Isabella Arendt stiller op for De Konservative',
            'display_id': 'isabella-arendt-stiller-op-for-de-konservative-2',
            'thumbnail': 'https://d1bm3dmew779uf.cloudfront.net/rss/show/5196630/4ceb292fd51c555feb652edfdf7291ed.png',
            'description': 'md5:b9aefe6406345d5447b80d30a5f09aa3',
            'duration': 3218,
            'episode_id': '50183310',
        }
    }]

    def _get_json(self, url, video_id):
        webpage = self._download_webpage(url, video_id)
        nextjs_data = self._search_nextjs_data(webpage, video_id)
        # the return of api_json is different
        return nextjs_data

    def _real_extract(self, url):
        video_id = self._match_id(url)
        raw_json = self._get_json(url, video_id)
        json_data = traverse_obj(
            raw_json, ('props', 'pageProps', 'episodeDetails', ..., 'details'))[0]

        return {
            'id': str(json_data['ID']),
            'title': json_data.get('post_content'),
            'url': json_data['enclosure'],
            'display_id': json_data.get('slug') or video_id,
            'thumbnail': json_data.get('image_url'),
            'description': json_data.get('post_title'),
            'duration': int_or_none(json_data.get('duration')),
            'episode_id': json_data.get('episode_id'),
        }
