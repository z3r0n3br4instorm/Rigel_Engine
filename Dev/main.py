import os
import sys
from syslog import Syslog
from datetime import datetime, timedelta
from voice_recognition_n_synth import Synthesizer

import rcore

class RigelCore:
    def __init__(self):
        self.syslog = Syslog(log_file="logs/rigel_core.log")
        self.prefrontal_cortex = rcore.PreFrontalCortex()
        self.agentic_cortex = self.prefrontal_cortex.agentic_cortex
        self.language_cortex = rcore.LanguageCortex()
        self.syslog.log("RigelCore initialized successfully.")
        
        
        
    async def initialize(self):
        """Initialize the system components"""
        self.syslog.log("Initializing Rigel Core components...", level="INFO")
        await self.prefrontal_cortex.initialize()
        self.syslog.log("Rigel Core initialization complete.", level="INFO")

    async def getInput(self, input):
        self.syslog.log(f"Received input: {input}")
        output = await self.prefrontal_cortex.checkInput(input)
        return output
        

class VocalBox:
    # TODO
    def __init__(self):
        self.syslog = Syslog(log_file="logs/vocal_box.log")
        self.syslog.log("VocalBox initialized successfully.")
        # Initialize any other components or configurations needed for VocalBox


async def main():
    try:
        rigel_core = RigelCore()
        synth = Synthesizer()
        await rigel_core.initialize()
        rigel_core.syslog.log("RigelCore and Synthesizer are ready to use.")
        
        # Example usage
        while True:
            input_text = input("Enter your input: ")
            response = await rigel_core.getInput(input_text)
            rigel_core.syslog.log(f"Response: {response}")
            synth.run_synth(f"{response}")
    except Exception as e:
        print(f"Error in main: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())