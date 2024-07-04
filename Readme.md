## Introduction
This code is an attempt to create a fully automatic subtitling system for vidoes.

The basic code is taken from [Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-generate-and-add-subtitles-to-videos-using-python-openai-whisper-and-ffmpeg)
and molded into a class with my own nips and tucks. The translation was not part of the original tutorial. 

Audio transcription is done **locally** through the [OpenAI Whisper](https://openai.com/research/whisper) model.
Text translation is done **locally** through [ArgosTranslate](https://pypi.org/project/argostranslate/).

## Usage
I have only tested this with mp4 videos, so YYMV. Here are the steps. 

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

## On language packs
> Argos Translate [...] manages automatically pivoting through 
> intermediate languages to translate between languages that don't have 
> a direct translation between them installed. For example, if you have 
> a **es → en** and **en → fr** translation installed you are able to translate 
> from **es → fr** as if you had that translation installed. This allows 
> for translating between a wide variety of languages at the cost of some 
> loss of translation quality.

*https://pypi.org/project/argostranslate/*

The following language packs (and thus direct translations) are currently available:

- Albanian -> English (no great results yet)
- Arabic -> English
- Azerbaijani -> English
- Bengali -> English
- Bulgarian -> English
- Catalan -> English
- Chinese (traditional) -> English
- Chinese -> English
- Czech -> English
- Danish -> English
- Dutch -> English
- English -> Albanian
- English -> Arabic
- English -> Azerbaijani
- English -> Bengali
- English -> Bulgarian
- English -> Catalan
- English -> Chinese
- English -> Chinese (traditional)
- English -> Czech
- English -> Danish
- English -> Dutch
- English -> Esperanto
- English -> Estonian
- English -> Finnish
- English -> French
- English -> German
- English -> Greek
- English -> Hebrew
- English -> Hindi
- English -> Hungarian
- English -> Indonesian
- English -> Irish
- English -> Italian
- English -> Japanese
- English -> Korean
- English -> Latvian
- English -> Lithuanian
- English -> Malay
- English -> Norwegian
- English -> Persian
- English -> Polish
- English -> Portuguese
- English -> Romanian
- English -> Russian
- English -> Slovak
- English -> Slovenian
- English -> Spanish
- English -> Swedish
- English -> Tagalog
- English -> Thai
- English -> Turkish
- English -> Ukranian
- English -> Urdu
- Esperanto -> English
- Estonian -> English
- Finnish -> English
- French -> English
- German -> English
- Greek -> English
- Hebrew -> English
- Hindi -> English
- Hungarian -> English
- Indonesian -> English
- Irish -> English
- Italian -> English
- Japanese -> English
- Korean -> English
- Latvian -> English
- Lithuanian -> English
- Malay -> English
- Norwegian -> English
- Persian -> English
- Polish -> English
- Portuguese -> English
- Portuguese -> Spanish
- Romanian -> English
- Russian -> English
- Slovak -> English
- Slovenian -> English
- Spanish -> English
- Spanish -> Portuguese
- Swedish -> English
- Tagalog -> English
- Thai -> English
- Turkish -> English
- Ukranian -> English
- Urdu -> English