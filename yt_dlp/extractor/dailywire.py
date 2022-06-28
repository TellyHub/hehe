import json
from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    determine_ext,
    float_or_none,
    join_nonempty,
    traverse_obj,
    url_or_none,
)
from urllib.error import HTTPError
from urllib.parse import quote

class DailyWireBaseIE(InfoExtractor):
    _NETRC_MACHINE = True
    _JSON_PATH = {
        'episode': ('props', 'pageProps', 'episodeData', 'episode'),
        'videos': ('props', 'pageProps', 'videoData', 'video'),
        'podcasts': ('props', 'pageProps', 'episode'),
    }
    
    _HEADER = {
        'content-type': 'application/json',
    }
    _QUERY = '''
query getEpisodeBySlug($slug: String!) {
  episode(where: {slug: $slug}) {
    id
    title
    status
    slug
    isLive
    description
    createdAt
    scheduleAt
    updatedAt
    image
    allowedCountryNames
    allowedContinents
    rating
    show {
        id
        name
        slug
        belongsTo
    }
    segments {
        id
        image
        title
        liveChatAccess
        audio
        video
        duration
        watchTime
        description
        videoAccess
        muxAssetId
        muxPlaybackId
        captions {
            id
        }
    }
    createdBy {
        firstName
        lastName
    }
    discussionId
    }
}
'''    
    def real_initialize(self):
        pass 
    
    def _call_api(self, slug):
        # using graphql api
        query = {
            'query': self._QUERY, 
            'variables': {'slug': f'{slug}'}
        }
        json_page = self._download_json(
            'https://v2server.dailywire.com/app/graphql',
            slug, data=json.dumps(query).encode('utf-8'), headers=self._HEADER, fatal=False)
        self.write_debug(f'json page: {json_page}')
        return traverse_obj(json_page, ('data', 'episode'))
       
    def initialize_pre_login(self):
        # before login, to get _csrf, expected redirect to login?state=<state>
        self.write_debug('Before login')
        authentication_url = 'https://authorize.dailywire.com/authorize'
        authentication_query = {
            'audience': 'https://api.dailywire.com/',
            'client_id': 'hDgwLR0K67GTe9IuVKATlbohhsAbD37H',
            'redirect_uri': 'https://www.dailywire.com/callback',
            'scope': 'openid profile email',
            'response_type': 'code',
            'response_mode': 'query',
            'state': 'WkJMYVc0U1FMMFhpOVdVVUJGcmY0ZU5PUXhrdlpjOFg4LWxSNmVqQkJtSA==',
            'nonce': 'dFVvOWY4YURZbHFQLkVhTS42dF9HdERpR1Fjdml6Mlk0VDJwSWJrNkFpcw==',
            'code_challenge': 'jYovVPCO3IAuzh2lcDD2NZkUC61lKWbg8zkAbFfqKgM',
            'code_challenge_method': 'S256',
            'auth0Client': 'eyJuYW1lIjoiYXV0aDAtc3BhLWpzIiwidmVyc2lvbiI6IjEuMTkuMyJ9',
        }
        # the _csrf cookie in login?state=<state>
        authentication_request = self._request_webpage(
            authentication_url, 'auth:init', query=authentication_query, headers=self._HEADER
        )
        print(self._get_cookies(authentication_url))
        
    
    def _perform_login(self, username, password):
        self.write_debug('trying to login')
        # This site using Oauth2 for authorization
        login_url = 'https://authorize.dailywire.com/usernamepassword/login'
        # can be simplified with authentication_query
        # post_data={
            # "client_id": "hDgwLR0K67GTe9IuVKATlbohhsAbD37H",
            # "redirect_uri": "https://www.dailywire.com/callback",
            # "tenant": "dailywire",
            # "response_type": "code",
            # "scope": "openid profile email",
            # "state": "hKFo2SBWemhXcV9NZTdrdkFFby1JYTJtdzV3bjJ0UHR2RFB6UqFupWxvZ2luo3RpZNkgRW9hcU9HSmRSVGtXdHFlQlNJZy1HZXlmclNSLUt3a2SjY2lk2SBoRGd3TFIwSzY3R1RlOUl1VktBVGxib2hoc0FiRDM3SA",
            # "nonce": "dFVvOWY4YURZbHFQLkVhTS42dF9HdERpR1Fjdml6Mlk0VDJwSWJrNkFpcw==",
            # "connection": "Username-Password-Authentication",
            # "username": f"{username}",
            # "password": f"{password}",
            # "popup_options": {},
            # "sso": True,
            # "response_mode": "query",
            # "_intstate": "deprecated",
            # "_csrf": "2LQZ014Y-1c_Ebv2T6hUOm_EgsBihroWlKUA",
            # "audience": "https://api.dailywire.com/",
            # "code_challenge_method": "S256",
            # "code_challenge": "jYovVPCO3IAuzh2lcDD2NZkUC61lKWbg8zkAbFfqKgM",
            # "auth0Client": "eyJuYW1lIjoiYXV0aDAtc3BhLWpzIiwidmVyc2lvbiI6IjEuMTkuMyJ9",
            # "protocol": "oauth2"
        # }
        post_data = {
            "client_id":"hDgwLR0K67GTe9IuVKATlbohhsAbD37H",
            "redirect_uri":"https://www.dailywire.com/callback",
            "tenant":"dailywire",
            "response_type":"code",
            "scope":"openid profile email",
            "state":"hKFo2SAzSjI4N2hYRHFyUUVPQlhUel9saU0waEd6eF9RYk5aMaFupWxvZ2luo3RpZNkgRXBsMHRKYVhVTFB4OVp1azJPOWVjQ285bjhsaW1qWFKjY2lk2SBoRGd3TFIwSzY3R1RlOUl1VktBVGxib2hoc0FiRDM3SA",
            "nonce":"aWl0NmJBWWxTNmFmdzdkd1RWYzUyNjJrYUVCSlp3WTZ3MmdZQlFoS2VBQg==",
            "connection":"Username-Password-Authentication",
            "username": f"{username}",
            "password": f"{password}",
            "popup_options":{},
            "sso": True,
            "response_mode":"query",
            "_intstate":"deprecated",
            "_csrf":"A2VgD64n-wFCMM9oDScK4ahxB1cirAq_ivt0",
            "audience":"https://api.dailywire.com/",
            "code_challenge_method":"S256",
            "code_challenge":"yZEVzDVKqNWx_QtrGj9bBfffHvejXFy8i56LWcgILho",
            "auth0Client":"eyJuYW1lIjoiYXV0aDAtc3BhLWpzIiwidmVyc2lvbiI6IjEuMTkuMyJ9",
            "protocol":"oauth2"}
        
        
        # this site validate right account here
        
        # webpage can return html if success and json if not
        # the 'login_url' seems to redirect url to <redirect_url>?code=<code>, 
        # the <code> can be used in 'token_url'
        
        try:
            webpage = self._download_webpage(
            login_url, 'login', data=json.dumps(post_data).encode(), headers=self._HEADER )
            #self.write_debug(f'webpage: {webpage}')
            #self.write_debug(f'webpage_url {webpage.geturl()}')
        except ExtractorError as e:
            if not isinstance(e.cause, HTTPError):
                raise
            error = self._parse_json(e.cause.read(), 'login')
            self.write_debug(f'error: {error}')
        ###################################################
        # required data for callback url
        # wa
        # wresult
        # wctx (need to unquote)
        
        # this post data seems can be simplified 
        wctx = {
            'strategy': 'auth0',
            'auth0Client': '',
            'tenant': 'dailywire',
            'connection': post_data.get('connection'),
            'client_id': post_data.get('client_id'),
            'response_type': post_data.get('response_type'),
            'response_mode': post_data.get('state'),
            'nonce': post_data.get('nonce'),
            'sid': '97uVlCgP8TiP7eeOoOTGKxavrrnfIx74',
            'audience': post_data.get('audience'),
            'jti': '62b98fe0dced2742fff06890',
            'realm': 'Username-Password-Authentication',
        }
        wa = self._search_regex(
                r'<input\s*[\w=\"]+\s*name=\"wa\"\s*value=\"(?P<result>[\w\.-]+)',
                webpage, 'wa', group='result')
        wresult = self._search_regex(
                r'<input\s*[\w=\"]+\s*name=\"wresult\"\s*value=\"(?P<result>[\w\.-]+)', 
                webpage, 'wresult', group='result')
        
        # callback_post_data = {
            # 'wa': self._search_regex(
                # r'<input\s*[\w=\"]+\s*name=\"wa\"\s*value=\"(?P<result>[\w\.-]+)',
                # webpage, 'wa', group='result'),
            # 'wresult': self._search_regex(
                # r'<input\s*[\w=\"]+\s*name=\"wresult\"\s*value=\"(?P<result>[\w\.-]+)', 
                # webpage, 'wresult', group='result'),
            # 'wctx': wctx,
        # }
        
        self.write_debug(f'wa:{wa}, wresult: {wresult}, wctx={str(wctx)}')
        # this url should be redirect to resume?state then to callback?code=<code>
        callback_url = 'https://authorize.dailywire.com/login/callback'
        
        callback_request = self._request_webpage(
            callback_url, 
            'video_id', 
            data=f'wa={wa}&wresult={wresult}&wctx={quote(str(wctx))}'.encode(), 
            #headers={'Content-Type': 'application/x-www-form-urlencoded'})
        )
        callback_final_url = callback_request.geturl()
        self.write_debug(f'Final callback url: {callback_final_url}')
        # needed data to token
        # code (from callback?code=<code>)
        # client_id 
        # code_verifier (didn't where this value came from)
        # 
        self.write_debug('Trying to get token')
        # # actual token is taken here
        token_url = 'https://authorize.dailywire.com/oauth/token'
        token_post_data = {
            'client_id': 'hDgwLR0K67GTe9IuVKATlbohhsAbD37H',
            # 'code_verifier': 'oYtR0VP4SF8TD_v0.YW9i02VvBgJ1wDcxfb4GgtN1Sj', # always change
            'grant_type': 'authorization_code',
            #'code': 'Wr8E9G3IDOgagKcp-OVB3ZPbcFbhRFkQ-RSuvgtF2KpiH', # always change
            'redirect_uri': 'https://www.dailywire.com/callback',
            'code': self._search_regex(
                r'callback\?code=\"(?P<code>)\"', 
                callback_final_url, 'callback_code',group='code') 
        }
        token_data = self._download_json(
            'https://authorize.dailywire.com/oauth/token',
            'token', data=json.dumps(token_post_data).encode(), headers=self._HEADER,)
        
        self._HEADER['Authorization'] = f'{token_data.get("token_type")} {token_data.get("access_token")}'
        #bearer_token = access_token 
        #self._HEADER['Authorization'] = f'Bearer {bearer_token}'
        
    def _get_json(self, url):
        sites_type, slug = self._match_valid_url(url).group('sites_type', 'id')
        json_data = self._search_nextjs_data(self._download_webpage(url, slug), slug)
        return slug, traverse_obj(json_data, self._JSON_PATH[sites_type])


class DailyWireIE(DailyWireBaseIE):
    _VALID_URL = r'https?://(?:www\.)dailywire(?:\.com)/(?P<sites_type>episode|videos)/(?P<id>[\w-]+)'
    _TESTS = [{
        'url': 'https://www.dailywire.com/episode/1-fauci',
        'info_dict': {
            'id': 'ckzsl50xnqpy30850in3v4bu7',
            'ext': 'mp4',
            'display_id': '1-fauci',
            'title': '1. Fauci',
            'description': 'md5:9df630347ef85081b7e97dd30bc22853',
            'thumbnail': 'https://daily-wire-production.imgix.net/episodes/ckzsl50xnqpy30850in3v4bu7/ckzsl50xnqpy30850in3v4bu7-1648237399554.jpg',
            'creator': 'Caroline Roberts',
            'series_id': 'ckzplm0a097fn0826r2vc3j7h',
            'series': 'China: The Enemy Within',
        }
    }, {
        'url': 'https://www.dailywire.com/episode/ep-124-bill-maher',
        'info_dict': {
            'id': 'cl0ngbaalplc80894sfdo9edf',
            'ext': 'mp3',
            'display_id': 'ep-124-bill-maher',
            'title': 'Ep. 124 - Bill Maher',
            'thumbnail': 'https://daily-wire-production.imgix.net/episodes/cl0ngbaalplc80894sfdo9edf/cl0ngbaalplc80894sfdo9edf-1647065568518.jpg',
            'creator': 'Caroline Roberts',
            'description': 'md5:adb0de584bcfa9c41374999d9e324e98',
            'series_id': 'cjzvep7270hp00786l9hwccob',
            'series': 'The Sunday Special',
        }
    }, {
        'url': 'https://www.dailywire.com/videos/the-hyperions',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        slug, episode_info = self._get_json(url)
        episode_info = self._call_api(slug) or episode_info
        urls = traverse_obj(
            episode_info, (('segments', 'videoUrl'), ..., ('video', 'audio')), expected_type=url_or_none)
       
        formats, subtitles = [], {}
        # 'or []' intended to give better error message at the end of processing not as fallback
        for url in urls or []:
            if determine_ext(url) != 'm3u8':
                formats.append({'url': url})
                continue
            format_, subs_ = self._extract_m3u8_formats_and_subtitles(url, slug)
            formats.extend(format_)
            self._merge_subtitles(subs_, target=subtitles)
        self._sort_formats(formats)
        return {
            'id': episode_info['id'],
            'display_id': slug,
            'title': traverse_obj(episode_info, 'title', 'name'),
            'description': episode_info.get('description'),
            'creator': join_nonempty(('createdBy', 'firstName'), ('createdBy', 'lastName'), from_dict=episode_info, delim=' '),
            'duration': float_or_none(episode_info.get('duration')),
            'is_live': episode_info.get('isLive'),
            'thumbnail': traverse_obj(episode_info, 'thumbnail', 'image', expected_type=url_or_none),
            'formats': formats,
            'subtitles': subtitles,
            'series_id': traverse_obj(episode_info, ('show', 'id')),
            'series': traverse_obj(episode_info, ('show', 'name')),
        }


class DailyWirePodcastIE(DailyWireBaseIE):
    _VALID_URL = r'https?://(?:www\.)dailywire(?:\.com)/(?P<sites_type>podcasts)/(?P<podcaster>[\w-]+/(?P<id>[\w-]+))'
    _TESTS = [{
        'url': 'https://www.dailywire.com/podcasts/morning-wire/get-ready-for-recession-6-15-22',
        'info_dict': {
            'id': 'cl4f01d0w8pbe0a98ydd0cfn1',
            'ext': 'm4a',
            'display_id': 'get-ready-for-recession-6-15-22',
            'title': 'Get Ready for Recession | 6.15.22',
            'description': 'md5:c4afbadda4e1c38a4496f6d62be55634',
            'thumbnail': 'https://daily-wire-production.imgix.net/podcasts/ckx4otgd71jm508699tzb6hf4-1639506575562.jpg',
            'duration': 900.117667,
        }
    }]

    def _real_extract(self, url):
        slug, episode_info = self._get_json(url)
        audio_id = traverse_obj(episode_info, 'audioMuxPlaybackId', 'VUsAipTrBVSgzw73SpC2DAJD401TYYwEp')

        return {
            'id': episode_info['id'],
            'url': f'https://stream.media.dailywire.com/{audio_id}/audio.m4a',
            'display_id': slug,
            'title': episode_info.get('title'),
            'duration': float_or_none(episode_info.get('duration')),
            'thumbnail': episode_info.get('thumbnail'),
            'description': episode_info.get('description'),
        }
