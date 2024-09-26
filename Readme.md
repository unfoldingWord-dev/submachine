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
git clone https://github.com/unfoldingWord-dev/submachine.git
cd submachine
```
2) Create a `.env` file based on `example.env`
3) Create an output directory as defined in .env
4) Setup a virtual environment (or make a mess of your local Python setup)
```bash
python3 -m venv venv
source venv/bin/activate
```
5) Install all the requirements
```bash
pip install -r requirements.txt
```
This will take a while, as the Whisper model is quite big.

6) Run the code 
```bash
python3 main.py
```
For every language that you want a subtitle for, an additional package will be downloaded during runtime. This can take some time.

## Known issues
You might encounter an error like `Could not load library libcudnn_ops_infer.so.8`. In that case, you need to install the CUDNN library. On Ubuntu, you need to run `sudo apt install libcudnn8` or `sudo apt install nvidia-cudnn`. (I have no idea about any other platform).
*(Time to start wrapping the whole thing in a Docker container)*

## On languages detected by Whisper
The following languages can be detected by Whisper 
(_as deducted from Whisper output_):

Afrikaans (af), Albanian (sq), Amharic (am), Arabic (ar), Armenian (hy), 
Assamese (as), Azerbaijani (az), Bashkir (ba), Basque (eu), 
Belarusian (be), Bengali (bn), Bosnian (bs), Breton (br), Bulgarian (bg), 
Burmese (my), Catalan (ca), Chinese (zh), Croatian (hr), Czech (cs), 
Danish (da), Dutch (nl), English (en), Estonian (et), Faroese (fo), 
Filipino (tl), Finnish (fi), French (fr), Galician (gl), Georgian (ka), 
German (de), Greek (el), Gujarati (gu), Haitian Creole (ht), Hausa (ha), 
Hawaiian (haw), Hebrew (he), Hindi (hi), Hungarian (hu), Icelandic (is), 
Indonesian (id), Italian (it), Japanese (ja), Javanese (jw), Kannada (kn), 
Kazakh (kk), Khmer (km), Korean (ko), Lao (lo), Latin (la), Latvian (lv), 
Lingala (ln), Lithuanian (lt), Luxembourgish (lb), Macedonian (mk), 
Malagasy (mg), Malayalam (ml), Malay (ms), Maltese (mt), Maori (mi), 
Marathi (mr), Mongolian (mn), Nepali (ne), Norwegian (no), 
Norwegian Nynorsk (nn), Occitan (oc), Pashto (ps), Persian (fa), 
Polish (pl), Portuguese (pt), Punjabi (pa), Romanian (ro), Russian (ru), 
Sanskrit (sa), Serbian (sr), Shona (sn), Sindhi (sd), Sinhala (si), 
Slovak (sk), Slovenian (sl), Somali (so), Spanish (es), Sundanese (su), 
Swahili (sw), Swedish (sv), Tajik (tg), Tamil (ta), Tatar (tt), 
Telugu (te), Thai (th), Tibetan (bo), Turkish (tr), Turkmen (tk), 
Ukrainian (uk), Urdu (ur), Uzbek (uz), Vietnamese (vi), Welsh (cy), 
Yiddish (yi), Yoruba (yo)

## On language packs in Argos
> Argos Translate [...] manages automatically pivoting through 
> intermediate languages to translate between languages that don't have 
> a direct translation between them installed. For example, if you have 
> a **es → en** and **en → fr** translation installed you are able to translate 
> from **es → fr** as if you had that translation installed. This allows 
> for translating between a wide variety of languages at the cost of some 
> loss of translation quality.

*https://pypi.org/project/argostranslate/*

The following language packs (and thus direct translations) are currently available:

- Albanian -> English
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
