import os

# Define constants
DEFAULT_BOT_NAME = 'dee-ablo'
DEFAULT_CHUNK_SIZE = 120
DEFAULT_PLAYBACK_SPEED = 1.3
DEFAULT_PHRASE_TIME_LIMIT = 5
DEFAULT_LANGUAGE = 'en'
INTERNAL_VOICE_COMMAND = 'internal settings'
INTERNAL_VOICE_COMMAND_RECEIVED = 'sure, no problem'
INTERNAL_VOICE_COMMAND_MOTION_CONTROL = 'internal settings - motion control'
INTERNAL_VOICE_COMMAND_RECEIVED_MOTION_CONTROL = 'motion control '
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_MODEL = 'gpt-3.5-turbo'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_CONTEXT = [{"role": "system", "content": "Hi, I'm {0}. How can I assist you today?".format(
    DEFAULT_BOT_NAME)}]
MOTION_CONTROL_CONTEXT = [{
    "role": "system",
    "content": """
Imagine you are helping me interact with a mobile ground robot. 
The job of this robot is to do simple movements, eg. spin, move forward, move backward, move in a square path, move in a triangle path, etc.
The main functions you can use are:
---
move_forward(duration): Move forward for specified duration(in seconds). Maximum allowed duration is 2 seconds.
move_backward(duration): Move backward in specified duration(in seconds). Maximum allowed duration is 2 seconds.
turn(degree): Turn around for a specified degree on the spot.
stop(): Stop moving and turning.
---
Can you make use of these to write code to perform simple movements? Please do not create new functions.

All of your outputs need to be identified by one of the following tags:
<question> Always ask me a clarification questions if you are unsure </question>
<command> Output only code command that achieves the desired goal </command>
<reason> Explain why you did something the way you did it </reason>
For example:
Me: can you spin
You: <question> How many times do you want me to spin? </question>
Me: only once
You: <command> turn(360) </command> <reason> I am moving the robot 360 degrees to achieve spin action </reason>

Let's start!
"""
}]
