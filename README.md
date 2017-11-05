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
VideoSlimmer.py --mkvmerge <path> --media <path> --lang <code> [--edit-title yes] [--delete-title yes] [--dry-run no] [--log <level>] [--keep-all-subtitles] [--version]
```

Language codes can be found [here](http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes)

Examples
--------

<u>Linux platform</u>
```
python2 VideoSlimmer.py --mkvmerge /opt/mkvtoolnix/mkvmerge --media /media/movies --lang eng --dry-run no
```

<u>Windows    platform</u>    
```
VideoSlimmer.py --mkvmerge "c:\Program Files\mkvtoolnix\mkvmerge.exe" --media D:\media\movies --lang eng --dry-run no --edit-title yes
```
or specifying UNC path
```
VideoSlimmer.py --mkvmerge "c:\Program Files\mkvtoolnix\mkvmerge.exe" --media \\medaserver\media\movies --lang eng --dry-run no --delete-title yes
```

Notes
-----

- VideoSlimmer will NOT remove audio or subtitles unless there is a match for the specified preferred language.
- VideoSlimmer IS recursive, thus all files/folders will be processed from the root defined media folder.

___
If you appreciate my work, then please consider buying me a beer  :D

[![PayPal donation](https://www.paypal.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=H8PWP3RLBDCBQ)
