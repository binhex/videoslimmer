videoslimmer
============

Utility to remove unwanted audio and subtitles from mkv files.

Installation
------------

1. Install Python 2.6.x or greater (not version 3.x)

2. Install mkvtoolnix 6.5.0 or greater

3. Run from terminal/command prompt, syntax and examples below

Syntax
------
```
VideoSlimmer.py <path to your media collection> <preferred language code>
```

Examples
--------

Linux platform		
```
python2 VideoSlimmer.py /media/movies/ eng
```
Windows	platform	
```
VideoSlimmer.py c:\media\movies\ eng
```

Language codes can be found here http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes

Note - VideoSlimmer IS recursive, thus all files/folders will be processed from the root defined media folder.