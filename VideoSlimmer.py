#!/usr/bin/env python
import os
import sys
import logging
import logging.handlers
import re
import subprocess
import packaging.version
import argparse
import json

# TODO add in --pref-audio-format specify quality of the audio you would ideally like, this is in conjunction with
#  keep-lang|remove-lang - if the audio quality found then remove all others, otherwise remove next best
# TODO keep audio format not done
# TODO bug in metadata - only edits/deletes track name for last track, may need to store track id's with comma's?


def videoslimmer_logging():

    # setup formatting for log messages
    videoslimmer_formatter = logging.Formatter(u"%(asctime)s %(module)s %(funcName)s :: [%(levelname)s] %(message)s")

    # setup logger for videoslimmer
    videoslimmer_logger = logging.getLogger(u"videoslimmer")

    # add rotating log handler
    videoslimmer_rotatingfilehandler = logging.handlers.RotatingFileHandler(
        videoslimmer_logs_file_uni, "a", maxBytes=10485760, backupCount=3, encoding="utf-8"
    )

    # set formatter for videoslimmer
    videoslimmer_rotatingfilehandler.setFormatter(videoslimmer_formatter)

    # add the log message handler to the logger
    videoslimmer_logger.addHandler(videoslimmer_rotatingfilehandler)

    # setup logging to console
    console_streamhandler = logging.StreamHandler()

    # set formatter for console
    console_streamhandler.setFormatter(videoslimmer_formatter)

    # add handler for formatter to the console
    videoslimmer_logger.addHandler(console_streamhandler)

    # set level of logging
    if log_level == u"debug":

        console_streamhandler.setLevel(logging.DEBUG)
        videoslimmer_logger.setLevel(logging.DEBUG)

    elif log_level == u"info":

        console_streamhandler.setLevel(logging.INFO)
        videoslimmer_logger.setLevel(logging.INFO)

    elif log_level == u"warning":

        console_streamhandler.setLevel(logging.WARNING)
        videoslimmer_logger.setLevel(logging.WARNING)

    elif log_level == u"exception":

        console_streamhandler.setLevel(logging.ERROR)
        videoslimmer_logger.setLevel(logging.ERROR)

    else:

        console_streamhandler.setLevel(logging.INFO)
        videoslimmer_logger.setLevel(logging.INFO)

    return videoslimmer_logger


def mkvmerge_version_check():

    mkvmerge_min_version = "58.0.0"

    mkvmerge_cmd = r"%s --version" % mkvmerge_file_path
    mkvmerge_info = subprocess.Popen(
        mkvmerge_cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    mkvmerge_info_stdout, mkvmerge_info_stderr = mkvmerge_info.communicate()

    mkvmerge_version = re.compile(r'(?<=v)[\d.]+', re.IGNORECASE).search(str(mkvmerge_info_stdout))

    # if min version not met, then exit
    if packaging.version.Version(mkvmerge_version.group()) < packaging.version.Version(mkvmerge_min_version):
        sys.stderr.write(u"mkvmerge version is less than %s, please upgrade" % mkvmerge_min_version)
        sys.exit(1)


def identify_metadata(mkvmerge_json, metadata_name, process_dict):

    try:

        filepath = mkvmerge_json['file_name']

    except KeyError:

        return process_dict

    filename_with_ext = os.path.basename(filepath)
    filename = os.path.splitext(filename_with_ext)[0]
    process_dict.update({'filename': filename})

    for i in mkvmerge_json['tracks']:

        try:

            metadata_name_value = (i['properties'][metadata_name])

        except KeyError:

            continue

        if metadata_name_value:

            try:

                track_id = (i['id'])

            except KeyError:

                continue

            if delete_title:

                process_dict.update({'%s_metadata_delete' % metadata_name: '--track-name %s:""' % track_id})

            if edit_title:

                if metadata_name_value != filename:

                    process_dict.update({
                        '%s_metadata_edit' % metadata_name: '--track-name %s:"%s"' % (track_id, filename)})

    vs_log.debug(u"process_dict after identify_metadata is'%s'" % process_dict)
    return process_dict


def identify_tracks(mkvmerge_json, track_type, process_dict):

    process_dict.update({'%s_keep_lang_present' % track_type: 'no'})

    tracks_id_remove_dict_value_list = []
    tracks_id_keep_dict_value_list = []

    if keep_lang_str:

        # strip all spaces, tabs, and newlines from string
        keep_lang_str_strip = ''.join(keep_lang_str.split())

        # create list of languages to keep
        lang_str_list = keep_lang_str_strip.split(u",")

    else:

        # strip all spaces, tabs, and newlines from string
        remove_lang_str_strip = ''.join(remove_lang_str.split())

        # create list of languages to remove
        lang_str_list = remove_lang_str_strip.split(u",")

    for i in mkvmerge_json['tracks']:

        try:

            tracks_type = (i['type'])

        except KeyError:

            continue

        if tracks_type == track_type:

            try:

                tracks_id = (i['id'])

            except KeyError:

                continue

            try:

                tracks_language = (i['properties']['language'])

            except KeyError:

                continue

            if keep_lang_str:

                if tracks_language not in lang_str_list:

                    tracks_id_remove_dict_value_list.append(tracks_id)
                    process_dict.update({'%s_tracks_id_remove' % track_type: tracks_id_remove_dict_value_list})

                else:

                    tracks_id_keep_dict_value_list.append(tracks_id)
                    process_dict.update({'%s_tracks_id_keep' % track_type: tracks_id_keep_dict_value_list})
                    process_dict.update({'%s_keep_lang_present' % track_type: 'yes'})

            if remove_lang_str:

                if tracks_language in lang_str_list:

                    tracks_id_remove_dict_value_list.append(tracks_id)
                    process_dict.update({'%s_tracks_id_remove' % track_type: tracks_id_remove_dict_value_list})

                else:

                    tracks_id_keep_dict_value_list.append(tracks_id)
                    process_dict.update({'%s_tracks_id_keep' % track_type: tracks_id_keep_dict_value_list})
                    process_dict.update({'%s_keep_lang_present' % track_type: 'yes'})

    vs_log.debug(u"process_dict after identify_tracks is'%s'" % process_dict)
    return process_dict


def videoslimmer():

    # walk media root path, convert to byte string before walk
    for root, dirs, files in os.walk(media_root_path_str):

        for input_filename in files:

            # filter out non mkv files
            if not input_filename.endswith(u".mkv"):
                vs_log.debug(f"Skipping file '{input_filename}' as it is not a Matroska container formatted file")
                continue

            # create full path to media file
            input_filename_path = os.path.join(root, input_filename)
            vs_log.info(u"Analysing file at path '%s' using mkvmerge..." % input_filename_path)

            process_dict = {}

            mkvmerge_cmd = r'%s --identification-format json --identify "%s"' % (
                mkvmerge_file_path, input_filename_path
            )

            vs_log.debug(u"Command to identify media is '%s'" % mkvmerge_cmd)
            mkvmerge_info = subprocess.Popen(
                mkvmerge_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            mkvmerge_info_stdout, mkvmerge_info_stderr = mkvmerge_info.communicate()
            mkvmerge_json_parsed = json.loads(mkvmerge_info_stdout)

            if keep_all_audio:

                audio_tracks_id_remove = None

            else:

                process_dict = identify_tracks(mkvmerge_json_parsed, "audio", process_dict)

                try:

                    audio_tracks_id_remove = (process_dict['audio_tracks_id_remove'])

                except KeyError:

                    audio_tracks_id_remove = ''

            if keep_all_subtitles:

                subtitles_tracks_id_remove = ''

            else:

                process_dict = identify_tracks(mkvmerge_json_parsed, "subtitles", process_dict)

                try:

                    subtitles_tracks_id_remove = (process_dict['subtitles_tracks_id_remove'])

                except KeyError:

                    subtitles_tracks_id_remove = ''

            process_dict = identify_metadata(mkvmerge_json_parsed, "track_name", process_dict)

            vs_log.debug(u"Dictionary to process is '%s'" % process_dict)

            try:

                track_name_metadata_edit = (process_dict['track_name_metadata_edit'])

            except KeyError:

                track_name_metadata_edit = ''

            try:

                track_name_metadata_delete = (process_dict['track_name_metadata_delete'])

            except KeyError:

                track_name_metadata_delete = ''

            if audio_tracks_id_remove or subtitles_tracks_id_remove or track_name_metadata_edit or track_name_metadata_delete:

                if audio_tracks_id_remove:

                    audio_tracks_id_remove = ','.join(str(e) for e in audio_tracks_id_remove)
                    audio_tracks_id_remove = "--audio-tracks !%s" % audio_tracks_id_remove

                if subtitles_tracks_id_remove:

                    subtitles_tracks_id_remove = ','.join(str(e) for e in subtitles_tracks_id_remove)
                    subtitles_tracks_id_remove = "--subtitle-tracks !%s" % subtitles_tracks_id_remove

                temp_output_filename_path = r'%s.tmp' % input_filename_path

                mkvmerge_cmd = r'%s --output "%s" %s %s %s %s "%s"' % (
                    mkvmerge_file_path, temp_output_filename_path, audio_tracks_id_remove, subtitles_tracks_id_remove,
                    track_name_metadata_edit, track_name_metadata_delete, input_filename_path
                )

                vs_log.debug(u"mkvmerge command to execute is '%s'" % mkvmerge_cmd)

                if dry_run:

                    vs_log.info(u"dry run enabled, command that would of been executed is '%s'" % mkvmerge_cmd)
                    continue

                else:

                    mkvmerge_info = subprocess.Popen(
                        mkvmerge_cmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    mkvmerge_info_stdout, mkvmerge_info_stderr = mkvmerge_info.communicate()

                    vs_log.debug(u"output from mkvmerge is %s" % mkvmerge_info_stdout)

                    if mkvmerge_info.returncode != 0:

                        vs_log.warning(u"output from mkvmerge is %s" % mkvmerge_info_stdout)
                        vs_log.warning(u"deleting temporary output file '%s'" % temp_output_filename_path)
                        continue

                    elif keep_orig:

                        output_filename_path = r'vs-%s' % input_filename_path
                        os.rename(temp_output_filename_path, output_filename_path)
                        vs_log.debug(u"renamed temporary file from '%s' to '%s'" % (
                            temp_output_filename_path, output_filename_path
                        ))

                    else:

                        output_filename_path = input_filename_path
                        os.remove(input_filename_path)
                        vs_log.debug(u"removed source file '%s'" % input_filename_path)

                        os.rename(temp_output_filename_path, output_filename_path)
                        vs_log.debug(u"renamed temporary file from '%s' to '%s'" % (
                            temp_output_filename_path, output_filename_path
                        ))

            else:

                vs_log.info(f"Skipping processing, '{input_filename}' does not have audio, subtitles, or metadata to "
                            f"remove")
                continue


if __name__ == '__main__':

    # set videoslimmer version numbers
    videoslimmer_version = "2.0.0"

    # define path to videoslimmer root
    videoslimmer_root_path_uni = os.path.dirname(os.path.realpath(__file__))

    # define path to videoslimmer logs folder
    videoslimmer_logs_path_uni = os.path.join(videoslimmer_root_path_uni, u"logs")

    # define path to mkvmerge binary
    videoslimmer_amd64_linux_mkvmerge_path_uni = os.path.join(
        videoslimmer_root_path_uni, u"static/amd64/mkvtoolnix/linux/mkvmerge"
    )

    # check version of python is 3.8.0 or higher
    if sys.version_info < (3, 8, 0):
        sys.stderr.write(u"videoslimmer requires Python 3.8.0 or later, your running version is %s"), sys.version_info
        sys.exit()

    # custom argparse to redirect user to help if unknown argument specified
    class ArgparseCustom(argparse.ArgumentParser):

        def error(self, message):

            sys.stderr.write('\n')
            sys.stderr.write('error: %s\n' % message)
            sys.stderr.write('\n')
            self.print_help()
            sys.exit(2)


    # setup argparse description and usage, also increase spacing for help to 50
    commandline_parser = ArgparseCustom(
        prog="VideoSlimmer",
        description="%(prog)s " + videoslimmer_version,
        epilog="Language codes can be found at: http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes",
        usage="%(prog)s [--help] "
              "--mkvmerge <path> --media <path> "
              "--keep-lang <code>|"
              "--remove-lang <code> "
              "[--edit-title] "
              "[--delete-title] "
              "[--keep-all-subtitles] "
              "[--keep-all-audio] "
              "[--keep-audio-format] "
              "[--keep-orig-file] "
              "[--dry-run] "
              "[--log <level>] "
              "[--logpath <path>] "
              "[--version]",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30))

    # create mutual exclusion group to force either --kep-lang or --remove-lang to be set, not both
    mutual_exclusion_group = commandline_parser.add_mutually_exclusive_group(required=True)

    # add argparse command line flags
    commandline_parser.add_argument(
        u"--mkvmerge", metavar=u"<path>", help=r"specify the location of mkvmerge e.g. --mkvmerge "
                                               r"'C:\Program Files\mkvtoolnix\mkvmerge.exe'. If path isn't specified "
                                               r"then the included statically built mkvmerge will be used."
    )
    commandline_parser.add_argument(
        u"--media", metavar=u"<path>", required=True, help=r"specify the path to your media, note only mkv container "
                                                           r"format is currently supported e.g. --media "
                                                           r"'C:\media\movies'."
    )
    mutual_exclusion_group.add_argument(
        u"--keep-lang", metavar=u"<code>", help=r"specify the language(s) you want to keep, all other languages will "
                                                r"be removed. If you want to keep multiple languages then use comma's "
                                                r"as a separator e.g. --keep-lang eng,ger."
    )
    mutual_exclusion_group.add_argument(
        u"--remove-lang", metavar=u"<code>", help=r"specify the language(s) you want to remove, all other languages "
                                                  r"will be kept. If you want to keep multiple languages then use "
                                                  r"comma's as a separator e.g. --remove-lang fra,eng."
    )
    commandline_parser.add_argument(
        u"--edit-title", action=u"store_true", help=r"specify whether you want to change the title metadata to match "
                                                    r"the filename, no value required."
    )
    commandline_parser.add_argument(
        u"--delete-title", action=u"store_true", help=r"specify whether you want to delete the title metadata, no "
                                                      r"value required."
    )
    commandline_parser.add_argument(
        u"--keep-all-subtitles", action=u"store_true", help=r"Keep all subtitles regardless of language, no value "
                                                            r"required."
    )
    commandline_parser.add_argument(
        u"--keep-all-audio", action=u"store_true", help=r"Keep all audio regardless of language, no value required."
    )
    commandline_parser.add_argument(
        u"--keep-audio-format", metavar=u"<format>", help=r"keep specified audio formats, all other audio formats "
                                                          r"will be removed. If you want to keep multiple audio "
                                                          r"formats then use comma's as a separator e.g. "
                                                          r"--keep-audio-format atmos,dts-hd."
    )
    commandline_parser.add_argument(
        u"--keep-orig-file", action=u"store_true", help=r"Keep original video file, do not overwrite once processed, "
                                                        r"no value required."
    )
    commandline_parser.add_argument(
        u"--dry-run",  action=u"store_true", help=r"specify whether you want to perform a dry run, no value required."
    )
    commandline_parser.add_argument(
        u"--logpath", metavar=u"<path>", help=r"specify the path to your log files e.g. --logpath "
                                              r"'C:\videoslimmer\logs'."
    )
    commandline_parser.add_argument(
        u"--loglevel", metavar=u"<level>", help=r"specify the logging level, valid values are "
                                                r"debug|info|warning|error, where  debug is the most verbose e.g. "
                                                r"--loglevel info."
    )
    commandline_parser.add_argument(
        u"--version", action=u"version", version=videoslimmer_version
    )

    # save arguments in dictionary
    args = vars(commandline_parser.parse_args())

    if args["mkvmerge"] is None:

        mkvmerge_file_path = videoslimmer_amd64_linux_mkvmerge_path_uni

    elif os.path.exists(args["mkvmerge"]):

        mkvmerge_file_path = args["mkvmerge"]

    else:

        sys.stderr.write(u"mkvmerge location does not exist")
        sys.exit()

    # save media location
    if os.path.exists(args["media"]):

        if os.path.isfile(args["media"]):

            sys.stderr.write(u"media path specifies a file not a folder")
            sys.exit()

        else:

            media_root_path_str = args["media"]

    else:

        sys.stderr.write(u"media location does not exist")
        sys.exit()

    # define languages we want to keep only, all other languages will be deleted
    if args["keep_lang"] is not None:

        if len(args["keep_lang"]) == 3:

            keep_lang_str = args["keep_lang"]

        else:

            sys.stderr.write(
                u"language code incorrect length, should be 3 characters, see this link for a full list:- "
                u"http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes"
            )
            sys.exit()

    else:

        keep_lang_str = ''

    # define languages we want to remove only, all other languages will be kept
    if args["remove_lang"] is not None:

        if len(args["remove_lang"]) == 3:

            remove_lang_str = args["remove_lang"]

        else:

            sys.stderr.write(u"language code incorrect length, should be 3 characters")
            sys.exit()

    else:

        remove_lang_str = ''

    # if enabled then edit metadata "title" field to filename minus extension
    if args["edit_title"]:

        edit_title = True

    else:

        edit_title = False

    # if enabled then delete metadata in "title" field
    if args["delete_title"]:

        delete_title = True

    else:

        delete_title = False

    # if enabled then do not strip out subtitles
    if args["keep_all_subtitles"]:

        keep_all_subtitles = True

    else:

        keep_all_subtitles = False

    # if enabled then do not strip out audio
    if args["keep_all_audio"]:

        keep_all_audio = True

    else:

        keep_all_audio = False

    # audio format that we want to keep, all other audio formats will be removed if a match is found.
    if args["keep_audio_format"] is not None:

        keep_audio_format_str = args["keep_audio_format"]

    else:

        keep_audio_format_str = ''

    # if enabled then do not overwrite original mkv
    if args["keep_orig_file"]:

        keep_orig = True

    else:

        keep_orig = False

    # if enabled then perform dry run
    if args["dry_run"]:

        dry_run = True

    else:

        dry_run = False

    # save log path
    if args["logpath"] is None:

        videoslimmer_logs_file_uni = os.path.join(videoslimmer_logs_path_uni, u"videoslimmer.log")

    else:

        logpath = args["logpath"]

        if not os.path.exists(logpath):
            os.makedirs(logpath)

        videoslimmer_logs_file_uni = os.path.join(logpath, u"videoslimmer.log")

    # save log level
    if args["loglevel"] is None:

        log_level = u"info"

    elif args["loglevel"] == "debug" or \
            args["loglevel"] == "info" or \
            args["loglevel"] == "warning" or \
            args["loglevel"] == "error":

        log_level = args["loglevel"]

    else:

        sys.stderr.write(u"incorrect logging level specified, defaulting to log level 'info'")
        log_level = u"info"

    # check mkvmerge version
    mkvmerge_version_check()

    # store the logger instances
    vs_log = videoslimmer_logging()

    # run main function
    videoslimmer()
