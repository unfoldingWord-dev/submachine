# import time
import math
import ffmpeg
import os
from dotenv import load_dotenv
from faster_whisper import WhisperModel
import argostranslate.package
import argostranslate.translate
from iso639 import Lang
import subprocess
import pprint
import pysrt

load_dotenv()


class SubMachine:
    def __init__(self, input_video):

        self.__input_video = input_video

        # Remove file extension
        lst_exts = ['mp4', 'mov', 'avi']
        for ext in lst_exts:
            if ext not in os.path.basename(input_video):
                continue

            self.__input_video_name = os.path.basename(input_video).replace(f".{ext}", "")

        self.__output_dir = os.getenv('OUTPUT_DIR')

    def __extract_audio(self, input_video):
        extracted_audio = f"{self.__output_dir}/{self.__input_video_name}-audio.wav"

        if os.path.exists(extracted_audio):
            print(f"File {extracted_audio} already exists. Skipping extraction...")
        else:
            stream = ffmpeg.input(input_video)
            stream = ffmpeg.output(stream, extracted_audio)
            ffmpeg.run(stream, overwrite_output=True)

            print(f'Extracted audio to {extracted_audio}')

        return extracted_audio

    def __transcribe_audio(self, audio):
        whisper_model = os.getenv('WHISPER_MODEL')

        # Compute type
        if os.getenv('WHISPER_COMPUTE_TYPE'):
            compute_type = os.getenv('WHISPER_COMPUTE_TYPE')
        else:
            compute_type = 'float16'

        model = WhisperModel(whisper_model, compute_type=compute_type)
        segments, info = model.transcribe(audio)

        lc_code = info[0]
        print("Language detected in audio: ", lc_code)
        # segments is a generator, transcription only starts when you iterate over it.
        # Therefore, the following list() statement makes the transcription actually take place.
        segments = list(segments)
        # for segment in segments:
        #     # print(segment)
        #     print("[%.2fs -> %.2fs] %s" %
        #           (segment.start, segment.end, segment.text))
        return lc_code, segments

    def __install_translation_packages(self, from_lc, to_lc):
        # Download and install Argos Translate package
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()

        try:
            package_to_install = next(
                filter(
                    lambda x: x.from_code == from_lc and x.to_code == to_lc, available_packages
                )
            )
            argostranslate.package.install_from_path(package_to_install.download())

        except StopIteration:
            # Can't find direct translation route. Will try to use multiple packages
            # Warning: this only works because I assume that you somehow already installed the intermediate packages
            print(f'No direct translation from \'{from_lc}\' to \'{to_lc}\' available. Will try to use '
                  f'intermediate translation (en). This will result in a slightly degraded translation.')

            intermediate_lc = 'en'

            try:
                package_to_install = next(
                    filter(
                        lambda x: x.from_code == from_lc and x.to_code == intermediate_lc, available_packages
                    )
                )
                argostranslate.package.install_from_path(package_to_install.download())

                try:
                    package_to_install = next(
                        filter(
                            lambda x: x.from_code == intermediate_lc and x.to_code == to_lc, available_packages
                        )
                    )
                    argostranslate.package.install_from_path(package_to_install.download())
                except StopIteration:
                    print(f'No intermediate translation from \'{intermediate_lc}\' to \'{to_lc}\' available.')
                    return False
            except StopIteration:
                print(f'No intermediate translation from \'{from_lc}\' to \'{intermediate_lc}\' available.')
                return False

        # All went well. We could install a direct translation package,
        # or we were able to install intermediate packages
        return True

    def __translate(self, arr_subs, from_lc, to_lc):

        if self.__install_translation_packages(from_lc, to_lc):

            # First, remove timestamps from the text to be translated.
            # They would be localized/translated as well, resulting
            # in a corrupt .srt file.
            text = self.__create_translatable_text(arr_subs)

            translated_text = argostranslate.translate.translate(text, from_lc, to_lc)

            arr_subs_translated = translated_text.split('\n\n')

            # Put all the markers and timestamps back in. Eew...
            sub_count = 0
            lst_translated_text = list()
            for sub in arr_subs:

                lst_translated_text.append(str(sub_count + 1))  # An .srt file starts counting from 1
                lst_translated_text.append(f"{sub.start} --> {sub.end}")
                lst_translated_text.append(arr_subs_translated[sub_count])
                lst_translated_text.append('')

                sub_count += 1

            translated_text = '\n'.join(lst_translated_text)

            # Return the translated text
            return translated_text

        else:
            return None

    def __format_time(self, seconds):
        hours = math.floor(seconds / 3600)
        seconds %= 3600
        minutes = math.floor(seconds / 60)
        seconds %= 60
        milliseconds = round((seconds - math.floor(seconds)) * 1000)
        seconds = math.floor(seconds)
        formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"

        return formatted_time

    def __create_translatable_text(self, arr_subs):
        text = ""

        sub_count = 0
        for sub in arr_subs:
            sub_count += 1

            #text += f"{str(sub_count)} \n"
            #text += f"[{str(sub_count)}] \n"
            text += f"{sub.text} \n"
            text += "\n"

        return text

    def __parse_segments_to_srt(self, segments):
        text = ""

        for index, segment in enumerate(segments):
            segment_start = self.__format_time(segment.start)
            segment_end = self.__format_time(segment.end)
            text += f"{str(index + 1)} \n"
            text += f"{segment_start} --> {segment_end} \n"
            text += f"{segment.text.strip()} \n"
            text += "\n"

        return text

    def __generate_subtitle_file(self, text, subtitle_file):

        with open(subtitle_file, "w") as f:
            f.write(text)

        return True

    def __ffprobe(self, file_path):
        command_array = ["ffprobe",
                         "-v", "quiet",
                         "-print_format", "json",
                         "-show_format",
                         "-show_streams",
                         file_path]
        result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return {
            'return_code': result.returncode,
            'json': result.stdout,
            'error': result.stderr
        }

    def __add_subtitle_to_video(self, soft_subtitle, subtitle_file, subtitle_language):

        # video_input_stream = ffmpeg.input(self.__input_video)
        # subtitle_input_stream = ffmpeg.input(subtitle_file)
        output_video = f"{self.__output_dir}/{self.__input_video_name}-with-subs-{subtitle_language}.mp4"

        if os.path.exists(output_video):
            print(f"File {output_video} already exists. Skipping merging...")
            return False

        # Get language name
        lang = Lang(subtitle_language)
        lname = lang.name
        lcode = lang.pt3

        if soft_subtitle:
            # Currently, this adds the subtitle to the first title stream. This overwrites the title of any other subtitle
            # TODO: Need to figure out if there are other subtitles, so I can title the correct stream
            # (metadata:s:s:1 or up)
            # print(lcode)
            # print(lname)

            lst_commands = [
                'ffmpeg',
                '-y',
                '-i', self.__input_video,
                '-i', subtitle_file,
                '-c', 'copy',
                '-c:s', 'mov_text',
                '-metadata:s:s:0', f"language={lcode}",
                '-metadata:s:s:0', f"title={lname}",
                '-metadata:s:s:0', f"handler_name={lname}",
                '-disposition:s:0', "default",
                output_video
            ]
            result = subprocess.run(lst_commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)
            if result.returncode > 0:
                print(result.stderr)

        else:
            # Subtitles burned in
            (
                ffmpeg
                .input(self.__input_video)
                .output(output_video, vf=f'subtitles={subtitle_file}')
                .run(overwrite_output=True)
            )

        return True

    def run(self, target_language=None):

        # Rip out audio
        audio = self.__extract_audio(self.__input_video)

        # If there is already a subtitle file available in the source language,
        # don't transcribe nor create
        source_language = os.getenv('LANGUAGE_FROM')
        file_subtitle_source = f"{self.__input_video}.{source_language}-sub.srt"

        if source_language is not None and os.path.exists(file_subtitle_source):
            print(f"File {file_subtitle_source} already exists. Skipping transcription...")

        else:

            # Transcribe audio
            language, segments = self.__transcribe_audio(audio)
            print(f'Transcribed audio... ({len(segments)} subs)')

            # Always create subtitle with original language
            subtitles = self.__parse_segments_to_srt(segments)
            source_language = language

            self.__generate_subtitle_file(subtitles, file_subtitle_source)
            print(f'Subtitle created for \'{source_language}\'')

        # We now surely have a subtitle file in the original language
        # Let's make it parseable
        arr_subs = pysrt.open(file_subtitle_source)

        # Translate the subs to another language if needed
        file_subtitle_target = ''
        sub_translated = False
        if target_language:
            if target_language != source_language:

                file_subtitle_target = f"{self.__input_video}.{target_language}-sub.srt"

                if os.path.exists(file_subtitle_target):
                    print(f'File {file_subtitle_target} already exists. Skipping translation...')
                    sub_translated = True

                else:
                    subtitles = self.__translate(arr_subs, from_lc=source_language, to_lc=target_language)
                    if subtitles:

                        sub_translated = True

                        self.__generate_subtitle_file(subtitles, file_subtitle_target)
                        print(f'File {file_subtitle_target} created.')
                    else:
                        print(f'Could not translate subtitles. Using original language ({source_language})')
        else:
            print(f'No target language defined. Using original language ({source_language})')

        # Which language are we using for subtitling
        if sub_translated is True:
            sub_file = file_subtitle_target
            sub_language = target_language
        else:
            sub_file = file_subtitle_source
            sub_language = source_language

        # Glue transcription and video together
        soft_subtitle = True if os.getenv('BURNIN') == 'False' else False

        subs_merged = self.__add_subtitle_to_video(
            soft_subtitle=soft_subtitle,
            subtitle_file=sub_file,
            subtitle_language=sub_language
        )

        if subs_merged is True:
            print(f'Video subtitled in \'{target_language}\'')


obj_submachine = SubMachine(input_video=os.getenv('INPUT_VIDEO'))
obj_submachine.run(target_language=os.getenv('LANGUAGE_TO'))
