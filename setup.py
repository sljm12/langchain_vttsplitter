from setuptools import setup

setup(
   name='langchain_vttsplitter',
   version='0.0.1',
   description='A VTT Splitter for Langchain modules',
   author='Stephen Lee',
   author_email='stephenleejm@gmail.com',
   packages=['langchain_vttsplitter'],  #same as name
   install_requires=['langchain', 'yt-dlp'], #external packages as dependencies
)