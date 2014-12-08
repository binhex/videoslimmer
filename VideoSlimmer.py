#set videoslimmer version numbers
latest_vs_version = "1.0.0"

import os
import sys
import logging
import logging.handlers
import re
import StringIO
import subprocess
from distutils.version import StrictVersion

#define path to videoslimmer root path
videoslimmer_root_dir = os.path.dirname(os.path.realpath(__file__)).decode("utf-8")

#check version of python is 2.6.x or 2.7.x
if sys.version_info<(2,6,0) or sys.version_info>=(3,0,0):

    sys.stderr.write(u"You need Python 2.6.x/2.7.x installed to run videoslimmer, your running version %s" % (sys.version_info))
    sys.exit()

else:

    #create full path to bundles modules
    sitepackages_modules_full_path = os.path.join(videoslimmer_root_dir, u"modules/argparse")
    sitepackages_modules_full_path = os.path.normpath(sitepackages_modules_full_path)

    #append full path to sys path
    sys.path.insert(1, sitepackages_modules_full_path)

import argparse

#set regex for output from mkvmerge
audio_regex = re.compile(ur"Track ID (\d+): audio.*")
subtitle_regex = re.compile(ur"Track ID (\d+): subtitles.*")
language_regex = re.compile(ur"(?<=language:)[a-zA-Z]+")
trackid_regex = re.compile(ur"(?<=Track ID\s)\d+")

#custom argparse to redirect user to help if unknown argument specified
class argparse_custom(argparse.ArgumentParser):

    def error(self, message):
        
        sys.stderr.write('\n')
        sys.stderr.write('error: %s\n' % message)
        sys.stderr.write('\n')
        self.print_help()
        sys.exit(2)

#setup argparse description and usage, also increase spacing for help to 50
commandline_parser = argparse_custom(prog="VideoSlimmer", description="%(prog)s " + latest_vs_version, usage="%(prog)s [--help] --mkvmerge <path> --media <path> --lang <code> [--log <level>] [--version]", formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=70))

#add argparse command line flags
commandline_parser.add_argument(u"--mkvmerge",  metavar=u"<path>", required=True, help=u"specify the path to mkvmerge e.g. --mkvmerge c:\Program Files\mkvtoolnix\mkvmerge.exe")
commandline_parser.add_argument(u"--media",  metavar=u"<path>", required=True, help=u"specify the path to your media e.g. --media c:\media\movies")
commandline_parser.add_argument(u"--lang", metavar=u"<code>", required=True, help=u"specify the language you want to keep e.g. --lang eng")
commandline_parser.add_argument(u"--logpath", metavar=u"<path>", help=u"specify the path to your log files e.g. --logpath c:\videoslimmer")
commandline_parser.add_argument(u"--loglevel", metavar=u"<level>", help=u"specify the logging level, info, warning, error, info being the most verbose e.g. --loglevel info")
commandline_parser.add_argument(u"--version", action=u"version", version=latest_vs_version)

#save arguments in dictionary
args = vars(commandline_parser.parse_args())

#save mkvmerge location
if args["mkvmerge"] != None:

    mkvmerge_cli = args["mkvmerge"]

#save media location
if args["media"] != None:

    media_root = args["media"] 

#save preferred language
if args["lang"] != None:

    preferred_lang = args["lang"]

#save log path
if args["logpath"] != None:

    log_path = args["logpath"]
    videoslimmer_log = os.path.join(log_path, "videoslimmer.log")
        
else:

    log_path = videoslimmer_root_dir
    videoslimmer_log = os.path.join(log_path, "videoslimmer.log")
    
#save log level
if args["loglevel"] != None:

    log_level = args["loglevel"]

else:

    log_level = "info"

#check version of mkvmerge is 6.5.0 or greater
cmd = [mkvmerge_cli, "--vesion"]
mkvmerge = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = mkvmerge.communicate()

mkmerge_version = re.compile(ur"(?<=v)[\d.]+", re.IGNORECASE).search(stdout)

#if min version not met, then exit
if StrictVersion(mkmerge_version.group()) < StrictVersion("6.5.0"):
    
    print u"MKVMerge version is less than 6.5.0, please upgrade"
    sys.exit()    
    
#########
# tools #
#########

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

###########
# logging #
###########

def videoslimmer_logging():

    #setup formatting for log messages
    videoslimmer_formatter = logging.Formatter("%(asctime)s %(levelname)s %(module)s %(funcName)s :: %(message)s")

    #setup logger for videoslimmer
    videoslimmer_logger = logging.getLogger("videoslimmer")

    #add rotating log handler
    videoslimmer_rotatingfilehandler = logging.handlers.RotatingFileHandler(videoslimmer_log, "a", maxBytes=10485760, backupCount=3, encoding = "utf-8")
    
    #set formatter for videoslimmer
    videoslimmer_rotatingfilehandler.setFormatter(videoslimmer_formatter)

    #add the log message handler to the logger
    videoslimmer_logger.addHandler(videoslimmer_rotatingfilehandler)

    #set level of logging to file to info
    videoslimmer_logger.setLevel(logging.INFO)

    #setup logging to console
    console_streamhandler = logging.StreamHandler()

    #set formatter for console
    console_streamhandler.setFormatter(videoslimmer_formatter)

    #add handler for formatter to the console
    videoslimmer_logger.addHandler(console_streamhandler)

    #set level of logging for console
    if log_level == "info":

            console_streamhandler.setLevel(logging.INFO)

    elif log_level == "warning":

            console_streamhandler.setLevel(logging.WARNING)

    elif log_level == "exception":

            console_streamhandler.setLevel(logging.ERROR)
    
    return videoslimmer_logger

#store the logger instances
vs_log = videoslimmer_logging()

def videoslimmer():
    
    for root, dirs, files in os.walk(media_root):

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
                vs_log.info(u"Deleted temporary file %s" % (temp_file))

            vs_log.info(u"processing file %s" % (path))                
            
            #build command line
            cmd = [mkvmerge_cli, "--identify-verbose", path]

            #get mkv info
            mkvmerge = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = mkvmerge.communicate()
            
            if mkvmerge.returncode != 0:
                
                vs_log.warning(u"mkvmerge failed to identify file %s" % (path))
                continue

            #create empty lists for audio and subs
            audio_track_list = []
            subtitle_track_list = []
            
            #find audio and subtitle tracks            
            for line in StringIO.StringIO(stdout):

                audio_track_search = audio_regex.search(line)
                
                if audio_track_search:
                    
                    audio_track_list.append(audio_track_search.group())
                    
                else:
                    
                    subtitle_track_search = subtitle_regex.search(line)
                    
                    if subtitle_track_search:
                        
                        subtitle_track_list.append(subtitle_track_search.group())

            #find audio to remove and keep
            if audio_track_list:

                remove_audio_list = []
                pref_audio_list = []
                
                #find audio tracks to remove, if not found then skip
                for audio_track_item in audio_track_list:

                    audio_lang_search = language_regex.search(audio_track_item)

                    if audio_lang_search != None:

                        audio_lang = audio_lang_search.group()                    
                    
                        if audio_lang != preferred_lang:

                            remove_audio_trackid_search = trackid_regex.search(audio_track_item)

                            if remove_audio_trackid_search != None:

                                remove_audio_trackid = remove_audio_trackid_search.group()                    

                                vs_log.info(u"audio track id to remove is %s" % (remove_audio_trackid))
                                remove_audio_list.append(remove_audio_trackid)

                if not remove_audio_list:

                    vs_log.info(u"no audio tracks to remove")
                
                #find audio tracks with preferred language, if not found then skip
                for audio_track_item in audio_track_list:

                    audio_lang_search = language_regex.search(audio_track_item)

                    if audio_lang_search != None:

                        audio_lang = audio_lang_search.group()                    
                    
                        if audio_lang == preferred_lang:

                            pref_audio_trackid_search = trackid_regex.search(audio_track_item)

                            if pref_audio_trackid_search != None:

                                pref_audio_trackid = pref_audio_trackid_search.group()
                                
                                vs_log.info(u"audio track id with preferred language is %s" % (pref_audio_trackid))
                                pref_audio_list.append(pref_audio_trackid)

                if not pref_audio_list:

                    vs_log.info(u"no audio tracks with preferred language")
                    
            else:

                vs_log.info(u"no audio tracks present")
                remove_audio_list = []
                pref_audio_list = []

            # find subtitle to remove and keep
            if subtitle_track_list:

                remove_subtitle_list = []
                pref_subtitle_list = []
                
                #find subtitle tracks to remove, if not found then skip
                for subtitle_track_item in subtitle_track_list:

                    subtitle_lang_search = language_regex.search(subtitle_track_item)

                    if subtitle_lang_search != None:

                        subtitle_lang = subtitle_lang_search.group()                    
                    
                        if subtitle_lang != preferred_lang:

                            remove_subtitle_trackid_search = trackid_regex.search(subtitle_track_item)

                            if remove_subtitle_trackid_search != None:

                                remove_subtitle_trackid = remove_subtitle_trackid_search.group()                    

                                vs_log.info(u"subtitle track id to remove is %s" % (remove_subtitle_trackid))
                                remove_subtitle_list.append(remove_subtitle_trackid)

                if not remove_subtitle_list:

                    vs_log.info(u"no subtitle tracks to remove")
                
                #find subtitle tracks with preferred language, if not found then skip
                for subtitle_track_item in subtitle_track_list:

                    subtitle_lang_search = language_regex.search(subtitle_track_item)

                    if subtitle_lang_search != None:

                        subtitle_lang = subtitle_lang_search.group()                    
                    
                        if subtitle_lang == preferred_lang:

                            pref_subtitle_trackid_search = trackid_regex.search(subtitle_track_item)

                            if pref_subtitle_trackid_search != None:

                                pref_subtitle_trackid = pref_subtitle_trackid_search.group()                    

                                vs_log.info(u"subtitle track id with preferred language is %s" % (pref_subtitle_trackid))
                                pref_subtitle_list.append(pref_subtitle_trackid)

                if not pref_subtitle_list:

                    vs_log.info(u"no subtitle tracks with preferred language")      
                    
            else:

                vs_log.info(u"no subtitle tracks present")
                remove_subtitle_list = []
                pref_subtitle_list = []

            #if no audio or subtitles to remove then skip to next iteration
            if not ((pref_audio_list and remove_audio_list) or (pref_subtitle_list and remove_subtitle_list)):

                continue
                             
            #build command line
            cmd = [mkvmerge_cli, "-o", temp_file]

            #check preferred audio exists, and there are audio tracks to remove
            if pref_audio_list and remove_audio_list:
                    
                cmd+= ["--audio-tracks", "%s" % (",".join(pref_audio_list))]
                cmd+= ["--default-track", "%s" % (",".join(pref_audio_list))]

            #check preferred subtitle exists, and there are subtitles to remove
            if pref_subtitle_list and remove_subtitle_list:

                cmd+= ["--subtitle-tracks", "%s" % (",".join(pref_subtitle_list))]
                cmd+= ["--default-track", "%s" % (",".join(pref_subtitle_list))]

            cmd += [path]

            vs_log.info(u"send command %s to mkvmerge" % (cmd))
                        
            #process file
            vs_log.info(u"Processing file...")
            mkvmerge = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = mkvmerge.communicate()

            if mkvmerge.returncode != 0:

                vs_log.warning(u"FAILED, output from mkvmerge is %s" % (stdout))

                if os.path.exists(temp_file):
                                  
                    #if failed then delete temp file                
                    os.remove(temp_file)
                    vs_log.info(u"Deleted temporary file %s" % (temp_file))               
                                  
                continue

            vs_log.info(u"SUCCESS")

            # remove source file and rename temp 
            os.remove(path)
            os.rename(temp_file, path)

if __name__ == '__main__':

    #run main function
    videoslimmer()
