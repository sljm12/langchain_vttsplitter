"""
Test VTTSplitter
"""
import pytest
from langchain_vttsplitter.vttsplitter import VTTSplitter, YoutubeSubtitleLoader

valid_url = "https://www.youtube.com/watch?v=LCcWWbx6pXU"
valid_doc = YoutubeSubtitleLoader(valid_url).load()[0]

def test_vttspliiter():
    """
    Test VTTSplitter with a valid URL
    checks if the metadata is promulgated from the parent doc to the chunks
    """

    chunks = VTTSplitter(chunk=512).split_text_docs(valid_doc)
    for ch in chunks:
        assert len(ch.page_content) <= 512
        assert ch.metadata["ytid"] == valid_doc.metadata["ytid"]