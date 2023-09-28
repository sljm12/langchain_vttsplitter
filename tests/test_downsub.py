'''
Test Download subtitle 
'''
import pytest
from langchain_vttsplitter.vttsplitter import downSub

def test_downsub_fail():
    '''
    Test with a youtube url that has no subtitles
    '''
    with pytest.raises(ValueError) as excinfo:
        results = downSub("https://www.youtube.com/watch?v=eS2iEPAxNWY", language='en')
    #print(subtitle, title)
    #assert subtitle is None, title is not None

def test_downsub_pass():
    '''
    Test with a youtube url that has no subtitles
    '''
    with pytest.raises(ValueError) as excinfo:
        results = downSub("https://www.youtube.com/watch?v=eS2iEPAxNWY", language='en')
    #print(subtitle, title)
    #assert subtitle is None, title is not None
