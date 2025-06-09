import os
import sys
from syslog import Syslog
from datetime import datetime, timedelta
import rcore

class RigelCore:
    def __init__(self):
        self.syslog = Syslog(log_file="logs/rigel_core.log")
        self.prefrontal_cortex = rcore.PreFrontalCortex()
        self.agentic_cortex = self.prefrontal_cortex.agentic_cortex  # Use the same AgenticCortex instance
        self.language_cortex = rcore.LanguageCortex()
        self.syslog.log("RigelCore initialized successfully.")
        
    async def initialize(self):
        """Initialize the system components"""
        self.syslog.log("Initializing Rigel Core components...", level="INFO")
        await self.prefrontal_cortex.initialize()
        self.syslog.log("Rigel Core initialization complete.", level="INFO")

    async def getInput(self, input):
        self.syslog.log(f"Received input: {input}")
        needs_tool = await self.prefrontal_cortex.checkInput(input)
        
        if needs_tool:
            self.syslog.log("Input requires tool invocation.")
            rcore.AgenticCortex()
            agent = await self.agentic_cortex.run()
            response = await self.agentic_cortex.invoke(agent, input)
            self.syslog.log(f"Tool invocation response: {response}")
            return agent
        else:
            self.syslog.log("Input does not require tool invocation.")
            return self.language_cortex.ollama_call(input, RAG=False)
        

class VocalBox:
    # TODO
    def __init__(self):
        self.syslog = Syslog(log_file="logs/vocal_box.log")
        self.syslog.log("VocalBox initialized successfully.")
        # Initialize any other components or configurations needed for VocalBox


async def main():
    try:
        rigel_core = RigelCore()
        vocal_box = VocalBox()
        
        # Initialize components before use
        await rigel_core.initialize()
        rigel_core.syslog.log("RigelCore and VocalBox are ready to use.")
        
        # Example usage
        input_text = "What is the time right now ?"
        response = await rigel_core.getInput(input_text)
        rigel_core.syslog.log(f"Response: {response}")
        print(response)
    except Exception as e:
        print(f"Error in main: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())