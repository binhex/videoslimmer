VideoSlimmer
============

Description
-----------

VideoSlimmer is a utility to remove unwanted audio and subtitles from Matroska (mkv extension) container formatted files. This can help reduce the size of your media collection whilst maintaining the audio and subtitles that you need.

Installation
------------

1. Install Python 2.6.0 or greater (not version 3.x)
2. Install MKVToolnix 6.5.0 or greater
3. Run from terminal/command prompt, syntax and examples below

Syntax
------

```
VideoSlimmer.py --mkvmerge <path> --media <path> --lang <code> [--log <level>] [--version]
```

Language codes can be found [here](http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes)

Examples
--------

<u>Linux platform</u>
```
python2 VideoSlimmer.py --mkvmerge /opt/mkvtoolnix/mkvmerge --media /media/movies --lang eng
```

<u>Windows	platform</u>	
```
VideoSlimmer.py --mkvmerge "c:\Program Files\mkvtoolnix\mkvmerge.exe" --media D:\media\movies --lang eng
```
or specifying UNC path
```
VideoSlimmer.py --mkvmerge "c:\Program Files\mkvtoolnix\mkvmerge.exe" --media \\medaserver\media\movies --lang eng
```

Notes
-----

- VideoSlimmer will NOT remove audio or subtitles unless there is a match for the specified language.
- VideoSlimmer IS recursive, thus all files/folders will be processed from the root defined media folder.
