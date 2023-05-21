from snowboy import snowboydecoder

from configs import SCRIPT_DIR

model = "{0}/snowboy/resources/models/snowboy.umdl".format(SCRIPT_DIR)
detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)


class Snowboy:
    def listen_for_command(self, callback):
        def callback_function():
            # Replace with your desired callback function
            snowboydecoder.play_audio_file()
            callback()

        # Start listening for the hotword and run the callback function when detected
        detector.start(detected_callback=callback_function, sleep_time=0.03)

    def stop_listening(self):
        print("snowboy stop listening")
        # When finished, stop listening for the hotword
        detector.terminate()
