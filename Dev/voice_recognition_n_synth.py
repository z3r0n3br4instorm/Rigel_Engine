# import vosk
import os
from syslog import Syslog
# import sounddevice as sd


class Synthesizer:
    def __init__(self):
        self.syslog = Syslog(log_file="logs/synth.log")
        self.model = None
        self.recognizer = None
        self.syslog.log("Synthesizer initialized successfully.")


    def run_synth(self, synthesis):
        # Escape single quotes in synthesis text to prevent shell conflicts
        escaped_synthesis = synthesis.replace("'", "'\"'\"'")
        print(escaped_synthesis)
        os.system(f"echo '{escaped_synthesis}' | python3.9 -m piper --model voice_model_data/jarvis-medium.onnx --output_file welcome.wav && paplay welcome.wav")