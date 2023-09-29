'''
Test Download subtitle 
'''
import pytest
from langchain_vttsplitter.vttsplitter import download_subtitles

def test_downsub_fail():
    '''
    Test with a url that is invalid
    '''
    with pytest.raises(ValueError) as excinfo:
        results = download_subtitles("https://www.gg.abc/testtes", language='en')
    #print(subtitle, title)
    #assert subtitle is None, title is not None

def test_downsub_no_subtitles():
    '''
    Test with a youtube url that has no subtitles
    '''
    subtitle, title = download_subtitles("https://www.youtube.com/watch?v=eS2iEPAxNWY", language='en')

    assert subtitle is None, title is not None
