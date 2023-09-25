# langchain_vttsplitter

This repo contains a vtt subtitle splitter that can generate langchain Documents in order to do RAG kind of applications.

The splitter takes into account the timing information that is in the VTT file and will extract that information and put it into the metadata so that your RAG application can playback the exact location where the information is in the video.

There are 2 main classes 
1. VTTSplitter
2. YoutuebSubtitleLoader

# Installation
## pip install from git
`pip install git+https://github.com/sljm12/langchain_vttsplitter`

## git clone and install
```
git clone https://github.com/sljm12/langchain_vttsplitter`
cd /langchain_vttsplitter
python setup.py install
```

# Example Code

```
from langchain_vttsplitter.vttsplitter import YoutubeSubtitleLoader, VTTSplitter

vtt_doc = YoutubeSubtitleLoader(youtube_url="").load()
arr_docs = VTTSplitter(chunk=512).split_text_docs(vtt_doc)
```

YoutubeSubtitleLoader will download the VTT subtitle and covert it to a langchain Document.
The document is passed to the VTTSplitter to split into the chunk size.
