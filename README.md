# Diablo ChatGPT For Robotics

Main tools used in this repo:

- openai chatGPT api
- google speech recognition
- `snowboy` hotword detection engine
- `nltk` natural language toolkit
- ros2

To improve the performance of chatbot, techniques have been used:

- api streaming
- breaking up long conversation with meaningful chunks
- invoking google text to speech api with small chunks
- audio processing and playing queue


## Prerequisites

You are using Linux and have ROS2 installed.

You have followed [these steps](https://github.com/DDTRobot/diablo_ros2) to build Diablo source code.

### Install required apt libs

```bash
sudo apt install python3-pyaudio python3-pyqt5.qtmultimedia libatlas-base-dev swig portaudio19-dev ffmpeg
```

### Install required python3 libs

```bash
pip3 install openai SpeechRecognition google-cloud-speech gTTS nltk pygame pyaudio pydub
```

`snowboy` is also needed to run this code. `pip3 install snowboy` failed during test, so here are the alternative steps:

```bash
git clone https://github.com/Kitt-AI/snowboy.git
cd snowboy/swig/Python3
make
cd ../../
python3 setup.py install
```

Note: you might also need to copy `_snowboydetect.so` generated from above steps to `./snowboy/` folder and overwrite existing file.

### Add required env vars

Add openai API Key to env var, inside `~/.bashrc`

```
export OPENAI_API_KEY=[your key here]
```

Add google cloud service account key json path to env var, inside `~/.bashrc`
(here are [the steps](https://developers.google.com/workspace/guides/create-credentials#create_credentials_for_a_service_account) how you can generate the json file)

```
export GOOGLE_APPLICATION_CREDENTIALS=[path/to/json]
```

## Start

To start the chatbot

```bash
python3 main.py
```

### Tips for chat

- different tones will play indicating chatbot is listening, receiving data, getting interrupted or about to play response audio.
- during chatbot playing response audio (eg. a long story), use hotword detection to interrupt and stop it, say hotword: `snowboy`. A 'ding' tone will play if the hotword detected.
- switch language (currently only supporting English and Mandarin). Say `can you speak chinese?`, chatbot will switch to Mandarin mode. To switch back, say `你会说英语吗?`
- the default phrase limit time (the duration you can say your prompt) is 5s. This is to prevent chatbot from hanging in a noisy environment.
- if you want to say a long prompt, say `Can I ask you a long question?`. Chatbot will reply `Sure, no problem.`. Then the phrase limit time will be increased to 5 mins, and you will be able to ask a really long question. (note: please try it in a quiet environment for better performance.)

### Tips for robot control

Inspired by [Microsoft chatGPT for robotics](https://www.microsoft.com/en-us/research/group/autonomous-systems-group-robotics/articles/chatgpt-for-robotics/).

- to allow chatGPT to control diablo robot, say `activate motion control`
- during motion control, try these commands `move forward`, `move backward`, `turn left`, `spin` in natural language
- to deactivate chatGPT for robotics, say `release motion control`
