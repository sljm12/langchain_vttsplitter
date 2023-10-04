"""
Test Youtube downloader
"""
import pytest
from langchain_vttsplitter.vttsplitter import YoutubeSubtitleLoader

def test_youtubeloader_parse_ytid():
    """
    Test if can successfully extract the yt id
    """
    c = YoutubeSubtitleLoader(youtube_url="https://www.youtube.com/watch?v=LCcWWbx6pXU")
    assert c.ytid == "LCcWWbx6pXU"

def test_youtubeloader_parse_ytid_failed():
    """
    Test if can successfully extract the yt id
    """

    with pytest.raises(ValueError):
        YoutubeSubtitleLoader(youtube_url="https://google.com")
    