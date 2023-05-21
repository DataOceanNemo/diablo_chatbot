import threading
from nltk.tokenize import sent_tokenize
from pygame import time as pytime
from configs import *
from robots import activateMotionControl, releaseMotionControl


def chunk_text(text, max_chunk_length=DEFAULT_CHUNK_SIZE):
    # Split the input text into sentences
    sentences = sent_tokenize(text)

    # Initialize an empty list to store the chunks
    chunks = []

    # Initialize an empty string to store the current chunk
    current_chunk = ""

    # Loop through each sentence in the input text
    for sentence in sentences:
        # If the length of the current chunk plus the length of the next sentence is greater than the maximum chunk length
        if len(current_chunk) + len(sentence) > max_chunk_length:
            # Append the current chunk to the list of chunks and reset the current chunk
            chunks.append(current_chunk.strip())
            current_chunk = ""

        # Add the next sentence to the current chunk
        current_chunk += sentence + " "

    # If there is any text remaining in the current chunk, append it to the list of chunks
    if current_chunk:
        chunks.append(current_chunk.strip())

    # Check if the first element is an empty string
    if chunks[0] == '':
        # Remove the first element
        chunks.pop(0)

    return chunks


class CustomThread(threading.Thread):
    def __init__(self, stop_event, main_function, name):
        super().__init__()
        self.stop_event = stop_event
        self.main_function = main_function
        self.name = name

    def run(self):
        while not self.stop_event.is_set():
            print("Thread running", self.name)
            self.main_function()

    def stop(self):
        print('Stopping thread', self.name)
        self.stop_event.set()

    def is_alive(self):
        return not self.stop_event.is_set()


def update_context(self, prompt):
    if "can you speak chinese" in prompt.lower():
        self.language = 'zh'
        self.context.append({"role": "user", "content": "你好"})
    elif "你会说英语吗" in prompt:
        self.language = 'en'
        self.context.append({"role": "user", "content": "hello"})
    elif "can i ask you a long question" in prompt.lower():
        self.phrase_time_limit = 300
        prompt = INTERNAL_VOICE_COMMAND
    elif "can i ask you a short question" in prompt.lower():
        self.phrase_time_limit = DEFAULT_PHRASE_TIME_LIMIT
        prompt = INTERNAL_VOICE_COMMAND
    elif "activate motion control" in prompt.lower():
        self.context = MOTION_CONTROL_CONTEXT
        self.motion_control = True
        activateMotionControl()
        prompt = INTERNAL_VOICE_COMMAND_MOTION_CONTROL
    elif "release motion control" in prompt.lower():
        self.context = DEFAULT_CONTEXT
        self.motion_control = False
        releaseMotionControl()
        prompt = INTERNAL_VOICE_COMMAND_MOTION_CONTROL
    return prompt


def play_sound(mixer, audio_file_path):
    sound = mixer.Sound(SCRIPT_DIR + audio_file_path)
    sound.play()
    pytime.wait(int(sound.get_length() * 1000))
