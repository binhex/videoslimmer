#!/bin/bash

# Remove unwanted audio and subtitles from MKV files.

##############################################################################
### NZBGET POST-PROCESSING SCRIPT                                          ###

# Remove unwanted audio and subtitles from MKV files.


##############################################################################
#### OPTIONS                                                               ###

# Full path to VideoSlimmer.py
#VIDEOSLIMMER_PATH=~/videoslimmer/VideoSlimmer.py

# Full path to mkvmerge
#MKVMERGE_PATH=/usr/bin/mkvmerge

# 3 Character language you want to keep
#LANG_KEEP=eng

### NZBGET POST-PROCESSING SCRIPT                                          ###
##############################################################################

#Clean the mkv (will make a clean.<filename>

echo "Running VideoSlimmer..."
python2 "$NZBPO_VIDEOSLIMMER_PATH" --mkvmerge "$NZBPO_MKVMERGE_PATH" --media "$NZBPP_DIRECTORY" --lang "$NZBPO_LANG_KEEP"

# Exit good no matter what
exit 93
