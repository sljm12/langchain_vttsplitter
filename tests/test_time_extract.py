'''
Testing time functions
'''
import pytest

from langchain_vttsplitter.vttsplitter import get_time, extract_min_max_time

def test_get_time_correct():
    '''
    Test with correct values
    '''
    start, end = get_time("00:02:49.729 --> 00:02:49.739 align:start position:0%")
    assert start == "00:02:49.729"
    assert end == "00:02:49.739"

def test_get_time_nottime():
    '''
    Test with a nonsensical value
    '''
    with pytest.raises(ValueError):
        get_time("This is rubbish")


def test_extract_min_max_time_one():
    '''
    Test extraction with only one line
    '''
    start, end = extract_min_max_time("00:02:49.729 --> 00:02:49.739 align:start position:0%")
    assert start == "00:02:49.729"
    assert end == "00:02:49.739"

def test_extract_min_max_time_multi():
    '''
    Test extraction with only one line
    '''
    text = """
00:02:49.729 --> 00:02:49.739 align:start position:0%
Somthing here 

00:02:55.729 --> 00:02:56.739 align:start position:0%
Something else
    """
    start, end = extract_min_max_time(text)
    assert start == "00:02:49.729"
    assert end == "00:02:56.739"
