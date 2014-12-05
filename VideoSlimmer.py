import os
import re
import sys
import StringIO
import subprocess
from distutils.version import StrictVersion

# set this to the path for mkvmerge
MKVMERGE = "D:/Program Files/Apps/mkvtoolnix/mkvmerge.exe"

#set regex for audio and subtitle
AUDIO_RE = re.compile(ur"Track ID (\d+): audio.*")
SUBTITLE_RE = re.compile(ur"Track ID (\d+): subtitles.*")

LANG_RE = re.compile(ur"(?<=language:)[a-zA-Z]+")
TRACKID_RE = re.compile(ur"(?<=Track ID\s)\d+")

#get version number from mkvmerge
cmd = [MKVMERGE, "--vesion"]
mkvmerge = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = mkvmerge.communicate()

mkmerge_version = re.compile(ur"(?<=v)[\d.]+", re.IGNORECASE).search(stdout)

#used to decode string to utf-8 or windows 1252 - used with os.walk
def string_decode(name):

    #if not string then unicode, does not need to be modified
    if type(name) == str:
                
        try:

            #used for linux files
            name = name.decode('utf8')
                        
        except:

            #used for windows files
            name = name.decode('windows-1252')
                        
    return name

#debug for text type
def string_type(text):

    #prints out whether string, unicode or other
    if isinstance(text, str):

            print "byte string"

    elif isinstance(text, unicode):

            print "unicode string"

    else:

            print "not string"

#make sure min version of mkvmerge is 6.5.0
if StrictVersion(mkmerge_version.group()) < StrictVersion("6.5.0"):
    print u"MKVMerge version is less than 6.5.0, please upgrade"
    sys.exit()    

try:
    
    in_dir = sys.argv[1]

except IndexError:

    print "Please supply the base directory containing your media files to process, note processing will be recursive"
    sys.exit()

try:
    
    preferred_lang = sys.argv[2]

except IndexError:

    print "Please supply your preferred language e.g. 'eng' for english, for other language codes go here http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes"
    sys.exit()

for root, dirs, files in os.walk(in_dir):

    #decode root to unicode
    root = string_decode(root)
    
    for f in files:

        #decode filename to unicode
        f = string_decode(f)        

        #filter out non mkv files
        if not f.endswith(".mkv"):
            
            continue
    
        #path to file, encode to byte string (required for subprocess and print)
        path = os.path.join(root.encode("utf-8"), f.encode("utf-8"))

        #create temp merge file, will be renamed to source if succesful merge
        temp_file = "%s-vs.temp" % (path)

        #delete any previously failed merge files        
        if os.path.exists(temp_file):
                          
            os.remove(temp_file)
            print  >> sys.stderr, "Deleted temporary file %s" % (temp_file)

        #os.environ['PYTHONIOENCODING'] = 'utf-8'
        print "processing file %s" % (path)        
        
        # build command line
        cmd = [MKVMERGE, "--identify-verbose", path]

        #get mkv info
        mkvmerge = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = mkvmerge.communicate()
        
        if mkvmerge.returncode != 0:
            print >> sys.stderr, "mkvmerge failed to identify file %s" % (path)
            continue

        #find audio and subtitle tracks
        audio_track_list = []
        subtitle_track_list = []
        
        for line in StringIO.StringIO(stdout):

            audio_track_search = AUDIO_RE.search(line)
            
            if audio_track_search:
                
                audio_track_list.append(audio_track_search.group())
                
            else:
                
                subtitle_track_search = SUBTITLE_RE.search(line)
                
                if subtitle_track_search:
                    
                    subtitle_track_list.append(subtitle_track_search.group())

        #find audio to remove and keep
        if audio_track_list:

            remove_audio_list = []
            pref_audio_list = []
            
            #find audio tracks to remove, if not found then skip
            for audio_track_item in audio_track_list:

                audio_lang_search = LANG_RE.search(audio_track_item)

                if audio_lang_search != None:

                    audio_lang = audio_lang_search.group()                    
                
                    if audio_lang != preferred_lang:

                        remove_audio_trackid_search = TRACKID_RE.search(audio_track_item)

                        if remove_audio_trackid_search != None:

                            remove_audio_trackid = remove_audio_trackid_search.group()                    
                        
                            print "audio track id to remove is %s" % (remove_audio_trackid)                
                            remove_audio_list.append(remove_audio_trackid)

            if not remove_audio_list:
                
                print >> sys.stderr, "no audio tracks to remove"
            
            #find audio tracks with preferred language, if not found then skip
            for audio_track_item in audio_track_list:

                audio_lang_search = LANG_RE.search(audio_track_item)

                if audio_lang_search != None:

                    audio_lang = audio_lang_search.group()                    
                
                    if audio_lang == preferred_lang:

                        pref_audio_trackid_search = TRACKID_RE.search(audio_track_item)

                        if pref_audio_trackid_search != None:

                            pref_audio_trackid = pref_audio_trackid_search.group()                    
                        
                            print "audio track id with preferred language is %s" % (pref_audio_trackid)                
                            pref_audio_list.append(pref_audio_trackid)

            if not pref_audio_list:
                
                print >> sys.stderr, "no audio tracks with preferred language"
                
        else:

            print >> sys.stderr, "no audio tracks present"
            remove_audio_list = []
            pref_audio_list = []

        # find subtitle to remove and keep
        if subtitle_track_list:

            remove_subtitle_list = []
            pref_subtitle_list = []
            
            #find subtitle tracks to remove, if not found then skip
            for subtitle_track_item in subtitle_track_list:

                subtitle_lang_search = LANG_RE.search(subtitle_track_item)

                if subtitle_lang_search != None:

                    subtitle_lang = subtitle_lang_search.group()                    
                
                    if subtitle_lang != preferred_lang:

                        remove_subtitle_trackid_search = TRACKID_RE.search(subtitle_track_item)

                        if remove_subtitle_trackid_search != None:

                            remove_subtitle_trackid = remove_subtitle_trackid_search.group()                    
                        
                            print "subtitle track id to remove is %s" % (remove_subtitle_trackid)                
                            remove_subtitle_list.append(remove_subtitle_trackid)

            if not remove_subtitle_list:
                
                print >> sys.stderr, "no subtitle tracks to remove"
            
            #find subtitle tracks with preferred language, if not found then skip
            for subtitle_track_item in subtitle_track_list:

                subtitle_lang_search = LANG_RE.search(subtitle_track_item)

                if subtitle_lang_search != None:

                    subtitle_lang = subtitle_lang_search.group()                    
                
                    if subtitle_lang == preferred_lang:

                        pref_subtitle_trackid_search = TRACKID_RE.search(subtitle_track_item)

                        if pref_subtitle_trackid_search != None:

                            pref_subtitle_trackid = pref_subtitle_trackid_search.group()                    
                        
                            print "subtitle track id with preferred language is %s" % (pref_subtitle_trackid)                
                            pref_subtitle_list.append(pref_subtitle_trackid)

            if not pref_subtitle_list:
                
                print >> sys.stderr, "no subtitle tracks with preferred language"
                
        else:

            print >> sys.stderr, "no subtitle tracks present"
            remove_subtitle_list = []
            pref_subtitle_list = []

        #if no audio or subtitles to remove then skip to next iteration
        if not ((pref_audio_list and remove_audio_list) or (pref_subtitle_list and remove_subtitle_list)):

            continue
                         
        #build command line
        cmd = [MKVMERGE, "-o", temp_file]

        #check preferred audio exists, and there are audio tracks to remove
        if pref_audio_list and remove_audio_list:
                
            cmd+= ["--audio-tracks", "%s" % (",".join(pref_audio_list))]
            cmd+= ["--default-track", "%s" % (",".join(pref_audio_list))]

        #check preferred subtitle exists, and there are subtitles to remove
        if pref_subtitle_list and remove_subtitle_list:

            cmd+= ["--subtitle-tracks", "%s" % (",".join(pref_subtitle_list))]
            cmd+= ["--default-track", "%s" % (",".join(pref_subtitle_list))]

        cmd += [path]
        
        print "send command %s to mkvmerge" % (cmd)
                    
        #process file
        print  >> sys.stderr, "Processing file...",
        mkvmerge = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = mkvmerge.communicate()

        if mkvmerge.returncode != 0:
            
            print >> sys.stderr, "FAILED, output from mkvmerge is %s" % (stdout)

            if os.path.exists(temp_file):
                              
                #if failed then delete temp file                
                os.remove(temp_file)
                print  >> sys.stderr, "Deleted temporary file %s" % (temp_file)
                              
            continue
        
        print  >> sys.stderr, "SUCCESS"

        # remove source file and rename temp 
        os.remove(path)
        os.rename(temp_file, path)
