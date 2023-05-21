import os
import queue
import threading
import time
import re

import openai
import speech_recognition as sr
from gtts import gTTS
from pygame import mixer
from listener import Snowboy
from pydub import AudioSegment

from configs import *
from utils import *
from robots import *


class ChatGPTBot:
    def __init__(self):
        # Init chatting configs
        openai.api_key = OPENAI_API_KEY
        self.language = DEFAULT_LANGUAGE
        self.context = DEFAULT_CONTEXT

        # Init speech recognizer
        self.r = sr.Recognizer()
        self.phrase_time_limit = DEFAULT_PHRASE_TIME_LIMIT
        self.is_first_time = True

        # Init pygame mixer for audio playback
        mixer.init()

        # Init audio play thread
        self.stop_audio = threading.Event()
        self.q = queue.Queue()
        self.t = threading.Thread(target=self.audio_player)
        self.t.daemon = True
        self.t.start()

        # create a snowboy thread object
        self.snowboy = Snowboy()
        stop_snowboy_event = threading.Event()
        self.snowboy_thread = CustomThread(
            stop_snowboy_event, self.hotword_detect, 'snowboy')

        self.motion_control = False

    def record_audio(self):
        while True:
            try:
                # Record audio from microphone
                with sr.Microphone() as source:
                    if self.is_first_time:
                        self.is_first_time = False
                        self.snowboy_thread.start()
                        # Play hint audio after init complete
                        play_sound(mixer, "/sounds/chatgpt-response.oga")
                    print("Speak:")
                    self.r.adjust_for_ambient_noise(source, duration=1)
                    audio = self.r.listen(
                        source, phrase_time_limit=self.phrase_time_limit)

                print("Finished talking")

                # convert the user's speech to text
                text = self.r.recognize_google_cloud(
                    audio, language=self.language)
                print("You said:", text)

                return text

            except sr.WaitTimeoutError:
                print("No speech detected")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(
                    "Could not request results from Google Speech Recognition service; {0}".format(e))
            except KeyboardInterrupt:
                print("Keyboard interrupt detected. Exiting...")
                break
            except:
                print("An unknown error occurred")

    def audio_player(self):
        while True:
            if not self.stop_audio.is_set():
                try:
                    # Wait for up to 1 second for new item
                    chunk = self.q.get(timeout=1)

                    if not chunk:
                        continue
                except:
                    continue

                tts = gTTS(text=chunk, lang=self.language)
                tmp_file = "{0}/temp/response_chunk.mp3".format(SCRIPT_DIR)
                tts.save(tmp_file)
                audio = AudioSegment.from_file(tmp_file, format="mp3")

                # Increase playback speed
                faster_audio = audio.speedup(
                    playback_speed=DEFAULT_PLAYBACK_SPEED)

                mixer.music.load(faster_audio.export(format="mp3"))
                mixer.music.play()
                while not self.stop_audio.is_set() and mixer.music.get_busy():
                    pass
                mixer.music.stop()
                mixer.music.rewind()
                os.remove(tmp_file)

                self.q.task_done()

            else:
                while not self.q.empty():
                    self.q.get_nowait()
                    self.q.task_done()

    def chat_with_gpt(self, prompt):
        prompt = update_context(self, prompt)
        self.stop_audio.clear()

        if prompt == INTERNAL_VOICE_COMMAND:
            self.q.put(INTERNAL_VOICE_COMMAND_RECEIVED)
        elif prompt == INTERNAL_VOICE_COMMAND_MOTION_CONTROL:
            self.q.put(INTERNAL_VOICE_COMMAND_RECEIVED_MOTION_CONTROL +
                       ("activated" if self.motion_control else "released"))
        elif self.motion_control:
            # Call OpenAI api
            chatgpt_response = ''
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    *self.context,
                    {"role": "user", "content": prompt}
                ]
            )

            chatgpt_response = response.choices[0].message.content
            # Extract question content
            question_pattern = r'<question>(.*?)</question>'
            question_match = re.search(
                question_pattern, chatgpt_response, re.DOTALL)
            if question_match:
                question_content = question_match.group(1).strip()
                print("Question:", question_content)
                self.q.put(question_content)
            else:
                # Extract command content
                command_pattern = r'<command>(.*?)</command>'
                command_match = re.search(
                    command_pattern, chatgpt_response, re.DOTALL)
                if command_match:
                    command_content = command_match.group(1).strip()
                    print("Command:", command_content)
                    exec(command_content)

                # Extract reason content
                reason_pattern = r'<reason>(.*?)</reason>'
                reason_match = re.search(
                    reason_pattern, chatgpt_response, re.DOTALL)
                if reason_match:
                    reason_content = reason_match.group(1).strip()
                    print("Reason:", reason_content)
                    self.q.put(reason_content)
            self.context.append({"role": "user", "content": prompt})
            self.context.append(
                {"role": "assistant", "content": chatgpt_response})
        else:
            # STREAM CHATGPT API RESPONSES
            delay_time = 0.01  # faster
            answer = ''

            # Call OpenAI api
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                stream=True,
                messages=[
                    *self.context,
                    {"role": "user", "content": prompt}
                ]
            )

            chatgpt_response = ''
            audio_chunk = ''

            for event in response:
                # STREAM THE ANSWER
                print(answer, end='', flush=True)  # Print the response
                # RETRIEVE THE TEXT FROM THE RESPONSE
                # EVENT DELTA RESPONSE
                event_text = event['choices'][0]['delta']
                answer = event_text.get('content', '')  # RETRIEVE CONTENT
                chatgpt_response = chatgpt_response + answer
                audio_chunk = audio_chunk + answer
                if self.stop_audio.is_set():
                    break
                if not self.stop_audio.is_set() and len(audio_chunk) > DEFAULT_CHUNK_SIZE + 20:
                    # add chunk to queue
                    chunks = chunk_text(audio_chunk)
                    self.q.put(chunks[0])
                    # flush audio_chunk
                    audio_chunk = ''
                    if len(chunks) > 1:
                        audio_chunk = chunks[1]

                time.sleep(delay_time)

            if not self.stop_audio.is_set() and len(audio_chunk) > 0:
                # add last chunk to queue
                self.q.put(audio_chunk)
                # flush audio_chunk
                audio_chunk = ''

            self.context.append({"role": "user", "content": prompt})
            self.context.append(
                {"role": "assistant", "content": chatgpt_response})

        # Wait for all chunks to finish playing
        if not self.stop_audio.is_set():
            self.q.join()

    def hotword_detect(self):
        self.snowboy.listen_for_command(self.stop_audio_playback)

    def stop_audio_playback(self):
        print("interrupt audio playback")
        self.stop_audio.set()

    def run(self):
        # Define conversation loop
        while True:
            # Record audio from microphone
            prompt = self.record_audio()

            # Play hint audio
            play_sound(mixer, "/sounds/finished-talking.oga")

            # Send text to ChatGPT API for response generation
            self.chat_with_gpt(prompt)
