## Introduction
This code is an attempt to create a fully automatic subtitling system for vidoes.

The basic code is taken from [Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-generate-and-add-subtitles-to-videos-using-python-openai-whisper-and-ffmpeg)
and molded into something more useful than just a tutorial. 

I have added the translation part.

## Usage
I have only tested this with mp4 videos. 
You should be able to run this code by
1) Cloning this repo
```bash
git pull https://github.com/unfoldingWord-dev/submachine.git
cd submachine
```
2) creating a `.env` file based on `example.env`
3) creating an output directory as defined in .env
4) Setup a virtual environment (or make a mess of your local Python setup)
```bash
python -m venv venv
source venv/bin/activate
```
5) install all the requirements
```bash
pip install -r requirements
```
6) Run the code 
```bash
python3 main.py
```