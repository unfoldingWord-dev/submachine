# import time
import math
import ffmpeg
import os
from dotenv import load_dotenv
from faster_whisper import WhisperModel
import argostranslate.package
import argostranslate.translate

load_dotenv()


class SubMachine:
    def __init__(self, input_video):

        self.__input_video = input_video
        self.__input_video_name = os.path.basename(input_video).replace(".mp4", "")

        self.__output_dir = os.getenv('OUTPUT_DIR')

    def __extract_audio(self, input_video):

        extracted_audio = f"{self.__output_dir}/{self.__input_video_name}-audio.wav"
        stream = ffmpeg.input(input_video)
        stream = ffmpeg.output(stream, extracted_audio)
        ffmpeg.run(stream, overwrite_output=True)
        return extracted_audio

    def __transcribe(self, audio):
        whisper_model = os.getenv('WHISPER_MODEL')

        # Compute type
        if os.getenv('WHISPER_COMPUTE_TYPE'):
            compute_type = os.getenv('WHISPER_COMPUTE_TYPE')
        else:
            compute_type = 'float16'

        model = WhisperModel(whisper_model, compute_type=compute_type)
        segments, info = model.transcribe(audio)

        language = info[0]
        print("Transcription language:", language)
        # segments is a generator, transcription only starts when you iterate over it.
        # Therefore, the following list() statement makes the transcription actually take place.
        segments = list(segments)
        # for segment in segments:
        #     # print(segment)
        #     print("[%.2fs -> %.2fs] %s" %
        #           (segment.start, segment.end, segment.text))
        return language, segments

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

    def __translate_argos(self, segments, from_lc, to_lc):

        if self.__install_translation_packages(from_lc, to_lc):

            # We keep timestamps out of the translation, as they are being localized as well,
            # which would make the resulting .srt file 'corrupt'.
            text = self.__create_translatable_text(segments)

            # print(text)

            translated_text = argostranslate.translate.translate(text, from_lc, to_lc)

            # print(translated_text)

            for index, segment in enumerate(segments):
                segment_start = self.__format_time(segment.start)
                segment_end = self.__format_time(segment.end)

                translated_text = translated_text.replace(f'[{str(index + 1)}]', f"{segment_start} --> {segment_end} ")

            # print(translated_text)

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

    def __create_translatable_text(self, segments):
        text = ""

        for index, segment in enumerate(segments):
            text += f"{str(index + 1)} \n"
            text += f"[{str(index + 1)}] \n"
            text += f"{segment.text} \n"
            text += "\n"

        return text

    def __parse_segments_to_srt(self, segments):
        text = ""

        for index, segment in enumerate(segments):
            segment_start = self.__format_time(segment.start)
            segment_end = self.__format_time(segment.end)
            text += f"{str(index + 1)} \n"
            text += f"{segment_start} --> {segment_end} \n"
            text += f"{segment.text} \n"
            text += "\n"

        return text

    def __generate_subtitle_file(self, language, text):
        subtitle_file = f"{self.__output_dir}/{self.__input_video_name}.{language}-sub.srt"

        f = open(subtitle_file, "w")
        f.write(text)
        f.close()

        return subtitle_file

    def __add_subtitle_to_video(self, soft_subtitle, subtitle_file, subtitle_language):

        video_input_stream = ffmpeg.input(self.__input_video)
        subtitle_input_stream = ffmpeg.input(subtitle_file)
        output_video = f"{self.__output_dir}/{self.__input_video_name}-with-subs-{subtitle_language}.mp4"
        subtitle_track_title = subtitle_file.replace(".srt", "")

        if soft_subtitle:
            stream = ffmpeg.output(
                video_input_stream, subtitle_input_stream, output_video, **{"c": "copy", "c:s": "mov_text"},
                **{"metadata:s:s:0": f"language={subtitle_language}",
                   "metadata:s:s:0": f"title={subtitle_track_title}"}
            )
            ffmpeg.run(stream, overwrite_output=True)

        else:
            # Subtitles burned in
            (
                ffmpeg
                .input(self.__input_video)
                .output(output_video, vf=f'subtitles={subtitle_file}')
                .run(overwrite_output=True)
            )

    def run(self, sub=None):

        # Rip out audio
        audio = self.__extract_audio(self.__input_video)
        print('Extracted audio...')

        # Transcribe audio
        language, segments = self.__transcribe(audio)
        print(f'Transcribed audio... ({len(segments)} subs)')

        # Always create subtitle with original language
        subtitles = self.__parse_segments_to_srt(segments)
        sub_lc = language
        subtitle_file = self.__generate_subtitle_file(sub_lc, subtitles)
        print(f'Subtitle created for \'{sub_lc}\'')

        # If sub has a language code, translate the subs to that lc
        if sub:
            if sub != language:
                sub_lc = sub
                subtitles = self.__translate_argos(segments, from_lc=language, to_lc=sub_lc)
                if subtitles:
                    subtitle_file = self.__generate_subtitle_file(sub_lc, subtitles)
                    print(f'Subtitle created for \'{sub_lc}\'')
                else:
                    print(f'Could not translate subtitles. Using original language ({language})')

        # Glue transcription and video together
        soft_subtitle = True if os.getenv('BURNIN') == 'False' else False

        self.__add_subtitle_to_video(
            soft_subtitle=soft_subtitle,
            subtitle_file=subtitle_file,
            subtitle_language=sub_lc
        )
        print(f'Video subtitled in \'{sub_lc}\'')


obj_submachine = SubMachine(input_video=os.getenv('INPUT_VIDEO'))
obj_submachine.run(sub=os.getenv('SUB_LANGUAGE'))
