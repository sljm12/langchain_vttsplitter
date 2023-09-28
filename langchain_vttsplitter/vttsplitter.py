'''
vttsplitter contains methods for splitting VTT files
'''

import re
from typing import List, Iterable, Dict
import copy
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

import requests
import yt_dlp

def downSub(video_url,language):
    '''
    Download subtitle given the youtube url and the language
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

def clear_lines(text):
    """
    Process the VTT text
    data : The VTT Clean text
    metadata : Metadata in the VTT
    timings : The Timings information in an array
    transcripts : The Transcript portion in an array

    """
    data = ""
    prev_timing = ""
    prev_text = ""
    lines = text.split("\n")
    #prev = ""
    metadata = {}
    metasection = True
    timings = []
    transcripts = []

    for current_line in lines:
        # Removes all the um, uhs etc from the text
        for sound in ["um", "uh"]:
            current_line = current_line.replace(sound, "")

        if current_line == "WEBVTT":
            pass
        elif "<c>" in current_line:  # This is one of the duplicate lines
            pass
        elif "-->" in current_line:  # Save the timing info to see
            metasection = False
            prev_timing = current_line
        elif len(current_line.strip()) == 0:
            pass
        elif metasection:
            meta = current_line.split(":")
            metadata[meta[0].strip()] = meta[1].strip()
        else:
            if current_line.strip() != prev_text:
                prev_text = current_line.strip()
                data = data + prev_timing + "\n"
                timings.append(prev_timing)
                data = data + current_line + "\n"
                transcripts.append(current_line)
    return data, metadata, timings, transcripts


def get_time(text):
    """
    Gets the start time and end time from a time segment
    """
    segments = text.split(" --> ")
    return (segments[0], segments[1].split(" align:")[0])


def extract_min_max_time(text):
    """
    Extract the min max time from a segment of VTT text
    """
    first = ""
    last = ""
    lines = text.split("\n")
    for current_line in lines:
        if len(first) == 0 and "->" in current_line:
            first = current_line

        if "->" in current_line:
            last = current_line
    return get_time(first)[0], get_time(last)[1]


def convert_text_time_to_seconds(text):
    """
    Converts the VTT formatted time to seconds for use in the YT embed player
    """
    segments = [float(i) for i in text.split(":")]
    return segments[0] * 60 * 60 + segments[1] * 60 + segments[2]


class YoutubeSubtitleLoader(BaseLoader):
    """
    This loades the Youtube subtitles in VTT format given the language and the url of the youtube
    video
    """

    def __init__(self, youtube_url: str, language="en"):
        self.url = youtube_url
        self.language = language

    def load(self) -> List[Document]:
        sub_url, title = downSub(self.url, self.language)
        result = requests.get(sub_url, timeout=30)
        page_content, vtt_meta, timings, transcript = clear_lines(result.text)

        metadata = {}
        metadata["url"] = self.url
        metadata["title"] = title
        metadata.update(vtt_meta)

        return [Document(page_content=page_content, metadata=metadata)]

class VTTSplitter:
    """
    VTTSplitter splits the VTT text into chunks, it removes the timing information from
    the text and stores the start and end time in the metadata.
    """

    def __init__(self, chunk: int = 512):
        self.chunk = chunk

    def process_chunk_doc(self, chunk: str, timings, parent_metadata: Dict) -> Document:
        _, end = extract_min_max_time(timings[-1])
        start, _ = extract_min_max_time(timings[0])
        metadata = copy.deepcopy(parent_metadata)
        metadata["start_time"] = int(convert_text_time_to_seconds(start))
        metadata["end_time"] = int(convert_text_time_to_seconds(end))
        return Document(page_content=chunk, metadata=metadata)

    def split_text_docs(self, doc: Document) -> List[Document]:
        """
        Spilts the Document into smaller Document chunks
        """
        page_content, vtt_meta, timings, transcript = clear_lines(doc.page_content)
        # stores the consolidated captions
        temp = ""
        # Stores the current length of the chunks so that we dont exceed the chunk size
        current_length = 0
        # Stores the processed Documents
        documents = []
        # stores the timings associated with the captions
        timings_arr = []
        i=0
        for i, t in enumerate(transcript):
            # t is the current text in the transcript
            length = len(t + "\n")

            # Still processing a chunk
            if current_length + length <= self.chunk:
                timings_arr.append(timings[i])

                temp = temp + t + "\n"

                current_length = current_length + length
            else:
                # The Chunk is compeleted
                timings_arr.append(timings[i])
                documents.append(self.process_chunk_doc(temp, timings_arr, doc.metadata))

                # start a new chunk
                temp = ""
                timings_arr = []

                temp = temp + t + "\n"
                current_length = length

        # Process the last
        timings_arr.append(timings[i])
        documents.append(self.process_chunk_doc(temp, timings_arr, doc.metadata))
        return documents

    def split_text(self, text: str) -> List[str]:
        """Split text into multiple components."""
        page_content, vtt_meta, timings, transcript = clear_lines(text)
        temp = ""
        current_length = 0
        chunks = []
        for i, t in enumerate(transcript):
            length = len(t)
            if current_length + length <= self.chunk:
                temp = temp + timings[i] + "\n"
                temp = temp + t + "\n"
                # print(temp)
                current_length = current_length + length
            else:
                chunks.append(temp)
                temp = ""
                temp = temp + timings[i] + "\n"
                temp = temp + t + "\n"
                current_length = len(t)
        chunks.append(temp)
        return chunks

    def split_documents(self, documents: Iterable[Document]) -> List[Document]:
        docs = []
        for d in documents:
            chuncks = self.split_text(d.page_content)
            for c in chuncks:
                page_content, vtt_meta, timings, transcript = clear_lines(c)

                start, end = extract_min_max_time(c)
                current_md = copy.deepcopy(d.metadata)
                current_md["start_time"] = int(convert_text_time_to_seconds(start))
                current_md["end_time"] = int(convert_text_time_to_seconds(end))
                docs.append(
                    Document(page_content="\n".join(transcript), metadata=current_md)
                )
        return docs
