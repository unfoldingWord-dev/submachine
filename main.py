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
        self.__input_video_name = input_video.replace(".mp4", "")

        self.__output_dir = os.getenv('OUTPUT_DIR')

    def __extract_audio(self, input_video):

        extracted_audio = f"{self.__output_dir}/{self.__input_video_name}-audio.wav"
        stream = ffmpeg.input(input_video)
        stream = ffmpeg.output(stream, extracted_audio)
        ffmpeg.run(stream, overwrite_output=True)
        return extracted_audio

    def __transcribe(self, audio):
        whisper_model = os.getenv('WHISPER_MODEL')

        model = WhisperModel(whisper_model)
        segments, info = model.transcribe(audio)
        language = info[0]
        print("Transcription language:", info[0])
        segments = list(segments)
        for segment in segments:
            # print(segment)
            print("[%.2fs -> %.2fs] %s" %
                  (segment.start, segment.end, segment.text))
        return language, segments

    def __translate_argos(self, segments, from_lc, to_lc):

        # Download and install Argos Translate package
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
            filter(
                lambda x: x.from_code == from_lc and x.to_code == to_lc, available_packages
            )
        )
        argostranslate.package.install_from_path(package_to_install.download())

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
            # segment_start = self.__format_time(segment.start)
            # segment_end = self.__format_time(segment.end)
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
        output_video = f"{self.__output_dir}/{self.__input_video_name}-output-{subtitle_language}.mp4"
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

        # Transcribe audio
        language, segments = self.__transcribe(audio)

        # Translate transcription
        if sub:
            target_lang = sub
            # First translate subtitles
            subtitles = self.__translate_argos(segments, from_lc=language, to_lc=target_lang)

        else:
            target_lang = language
            # Just generate subtitle file from transcription
            subtitles = self.__parse_segments_to_srt(segments)

        # Create the subtitle file
        subtitle_file = self.__generate_subtitle_file(target_lang, subtitles)

        # Glue transcription and video together
        soft_subtitle = True if os.getenv('BURNIN') == 'False' else False

        self.__add_subtitle_to_video(
            soft_subtitle=soft_subtitle,
            subtitle_file=subtitle_file,
            subtitle_language=target_lang
        )


obj_submachine = SubMachine(input_video=os.getenv('INPUT_VIDEO'))
obj_submachine.run(sub=os.getenv('SUB_LANGUAGE'))
