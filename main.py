import time
import math
import ffmpeg
import os
from dotenv import load_dotenv
from groq import Groq
import deepl
from faster_whisper import WhisperModel


class SubMachine:
    def __init__(self, input_video):
        load_dotenv()

        self.__input_video = input_video
        self.__input_video_name = input_video.replace(".mp4", "")

        self.__output_dir = os.getenv('OUTPUT_DIR')
        self.__groq_api_key = os.getenv('GROQ_API_KEY')

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

    def __translate_groq(self, segments, language_to):
        client = Groq(api_key=self.__groq_api_key)
        model = os.getenv('GROQ_MODEL')

        sequence = self.__parse_segments_to_srt(segments)

        instruction_message = (
            "You are a translator. You are analyzing a text and providing answers that exactly match that text. \
            You should not provide any introductions, explanations and interpretation unless you are specifically asked to do so."
        )

        prompt = f"Please translate the following subtitle file from English to {language_to}\n\n{sequence}. "

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": instruction_message
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def __translate(self, segments, language):
        auth_key = os.getenv('DEEPL_API_KEY')
        translator = deepl.Translator(auth_key)

        sequence = self.__parse_segments_to_srt(segments)

        result = translator.translate_text(sequence, target_lang=language)
        return result.text

    def __format_time(self, seconds):
        hours = math.floor(seconds / 3600)
        seconds %= 3600
        minutes = math.floor(seconds / 60)
        seconds %= 60
        milliseconds = round((seconds - math.floor(seconds)) * 1000)
        seconds = math.floor(seconds)
        formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"

        return formatted_time

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

    def __generate_subtitle_file(self, language, segments):
        subtitle_file = f"{self.__output_dir}/{self.__input_video_name}.{language}-sub.srt"
        text = ""

        text = self.__parse_segments_to_srt(segments)

        f = open(subtitle_file, "w")
        f.write(text)
        f.close()

        return subtitle_file

    def __add_subtitle_to_video(self, soft_subtitle, subtitle_file, subtitle_language):

        video_input_stream = ffmpeg.input(self.__input_video)
        subtitle_input_stream = ffmpeg.input(subtitle_file)
        output_video = f"{self.__output_dir}/{self.__input_video_name}-output.mp4"
        subtitle_track_title = subtitle_file.replace(".srt", "")

        if soft_subtitle:
            stream = ffmpeg.output(
                video_input_stream, subtitle_input_stream, output_video, **{"c": "copy", "c:s": "mov_text"},
                **{"metadata:s:s:0": f"language={subtitle_language}",
                   "metadata:s:s:0": f"title={subtitle_track_title}"}
            )
            ffmpeg.run(stream, overwrite_output=True)

    def run(self, translate=False):

        # Rip out audio
        audio = self.__extract_audio(self.__input_video)

        # Transcribe audio
        language, segments = self.__transcribe(audio)

        # Translate transcription
        if translate is True:

            # Translate using deepl
            translated_subs = self.__translate(segments, 'NL')
            print(translated_subs)
            exit()

        # Generate subtitle file from transcription
        subtitle_file = self.__generate_subtitle_file(language, segments)

        # Glue transcription and video together
        self.__add_subtitle_to_video(
            soft_subtitle=True,
            subtitle_file=subtitle_file,
            subtitle_language=language
        )


obj_submachine = SubMachine(input_video='input.mp4')
obj_submachine.run(translate=True)
