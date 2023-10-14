"""
loaders for YoutubeSubtittleLoader

"""
import re
from typing import List
from urllib.parse import parse_qs, urlparse
import requests
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
import yt_dlp
from langchain_vttsplitter.vttsplitter import clear_lines


def download_subtitles(video_url,language):
    '''
    Download subtitle given the youtube url and the language.

    Throws ValueError if there is an error in retriving based on the URL

    else returns a tuple of [video_subtitle_url, video_title]
    '''
    # check if valid youtube_link and remove playlist ID from url if exists.
    _temp = video_url.lower()
    if 'youtube.com' in _temp or 'youtu.be' in _temp:
        if '&list=' in video_url:
            video_url = video_url.split('&list=')[0].strip()


    ydl_opts = {'dump-json':True,
     'writesubtitles':True,
     'writeautomaticsub':True,
     'youtube_include_dash_manifest':False}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as (ydl):
            info_dict = ydl.extract_info(video_url, download=False)
            #print(info_dict)
            if not info_dict['formats']:
                print(text=' Status : Something went wrong retry or video is unavailable')
                raise ValueError('Status : Something went wrong retry or video is unavailable')
    except Exception as exc:
        raise ValueError("Check your url, video might not have subtitle") from exc


    video_title = info_dict['title']

    # replacing reserved characters for windows for filename.
    video_name = re.sub('[\\\\/*?:"<>|]', '', video_title)

    subtitles = info_dict.get('subtitles')
    automatic_captions = info_dict.get('automatic_captions')


    if subtitles:
        subtitle = subtitles.get(language)
        if subtitle:
            for fmt in subtitle:
                if fmt['ext']=='vtt':
                    sub_dlink = fmt['url']
                    return [sub_dlink,video_name]

    if automatic_captions:
        subtitle = automatic_captions.get(language)
        if subtitle:
            for fmt in subtitle:
                if fmt['ext']=='vtt':
                    sub_dlink = fmt['url']
                    return [sub_dlink,video_name]

    return [None, video_title]

class YoutubeSubtitleLoader(BaseLoader):
    """
    This loades the Youtube subtitles in VTT format given the language and the url of the youtube
    video
    """

    def __init__(self, youtube_url: str, language="en"):
        self.url = youtube_url
        self.language = language
        url_segments = urlparse(youtube_url)
        query = parse_qs(url_segments.query)
        if 'v' in query:
            self.ytid = query['v'][0]
        else:
            self.ytid = None
            raise ValueError("Youtube URL has no valid ID")

    def load(self) -> List[Document]:
        sub_url, title = download_subtitles(self.url, self.language)
        result = requests.get(sub_url, timeout=30)
        page_content, vtt_meta, timings, transcript = clear_lines(result.text)

        metadata = {}
        metadata["url"] = self.url
        metadata["title"] = title
        metadata["ytid"] = self.ytid
        metadata.update(vtt_meta)

        return [Document(page_content=page_content, metadata=metadata)]