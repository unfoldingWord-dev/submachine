## Introduction
This code is an attempt to create a fully automatic subtitling system for vidoes.

The basic code is taken from [Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-generate-and-add-subtitles-to-videos-using-python-openai-whisper-and-ffmpeg)
and molded into a class with my own nips and tucks. The translation was not part of the original tutorial. 

Audio transcription is done **locally** through [OpenAI Whisper](https://openai.com/research/whisper) model.
Text translation is done **locally** through [ArgosTranslate](https://pypi.org/project/argostranslate/).

## Usage
I have only tested this with mp4 videos, so YYMV. Here are the steps to do it yourself. 

1) Clone this repo
```bash
git pull https://github.com/unfoldingWord-dev/submachine.git
cd submachine
```
2) Create a `.env` file based on `example.env`
3) Create an output directory as defined in .env
4) Setup a virtual environment (or make a mess of your local Python setup)
```bash
python -m venv venv
source venv/bin/activate
```
5) Install all the requirements
```bash
pip install -r requirements
```
This will take a while, as the Whisper model is quite big.   

6) Run the code 
```bash
python3 main.py
```
For every language that you want a subtitle for, an additional package will be downloaded during runtime. This can take some time. 