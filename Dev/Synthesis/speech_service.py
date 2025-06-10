import os
import re
import subprocess
import logging
import threading
import time
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='audioserver.log'
)
logger = logging.getLogger('speech_service')

def clean_text_for_speech(text):
    text = text.replace("'", "")

    # if not text:
    #     return ""
        
    # text = re.sub(r'https?://\S+', '', text)
    # text = re.sub(r'www\.\S+', '', text)
    
    # text = re.sub(r'\*+([^*]+)\*+', r'\1', text)
    # text = re.sub(r'`([^`]+)`', r'\1', text)
    # text = re.sub(r'#{1,6}\s+', '', text)
    
    # text = re.sub(r'^\s*[-*•]\s+', 'bullet point: ', text, flags=re.MULTILINE)
    # text = re.sub(r'^\s*\d+\.\s+', 'item: ', text, flags=re.MULTILINE)
    # text = re.sub(r'\s+', ' ', text).strip()
    # text = text.replace("'", "'\\''")
    
    return text

def generate_speech_file(text, output_file):
    """Generate a speech file from the given text"""
    try:
        model_path = "/home/zerone/KioskSystem/Dev/VSM_Serve/audioserver/voiceFiles/jarvis-medium.onnx"
        
        if not os.path.exists(model_path):
            logger.error(f"Speech model not found at: {model_path}")
            return False
            
        cmd = f"echo '{text}' | python3.10 -m piper --model {model_path} --output_file {output_file}"
        subprocess.run(cmd, shell=True, timeout=30, check=True)
        return True
    except Exception as e:
        logger.error(f"Error generating speech file: {str(e)}")
        return False

def play_audio(audio_file):
    """Play the audio file"""
    try:
        play_cmd = f"aplay {audio_file}"
        subprocess.run(play_cmd, shell=True, timeout=15, check=True)
        return True
    except Exception as e:
        logger.error(f"Error playing audio: {str(e)}")
        return False

def speak(data):
    try:
        # Split the text into sentences or logical chunks
        sentences = re.split(r'(?<=[.!?])\s+', data)
        
        if not sentences:
            logger.warning("No text to speak")
            return False
        
        # Clean up empty sentences
        sentences = [s for s in sentences if s.strip()]
        
        if not sentences:
            logger.warning("No valid sentences to speak after cleaning")
            return False
            
        # Process the first sentence immediately
        current_file = f"speech_{uuid.uuid4().hex[:8]}.wav"
        next_file = f"speech_{uuid.uuid4().hex[:8]}.wav"
        
        cleaned_text = clean_text_for_speech(sentences[0])
        print(f"Processing: {cleaned_text}")
        
        if not generate_speech_file(cleaned_text, current_file):
            return False
        
        # Process remaining sentences
        for i in range(1, len(sentences)):
            # Start processing next sentence in background
            next_text = clean_text_for_speech(sentences[i])
            thread = threading.Thread(target=generate_speech_file, args=(next_text, next_file))
            thread.start()
            
            # Play current sentence while next one is being processed
            print(f"Playing: {cleaned_text}")
            play_audio(current_file)
            
            # Wait for background processing to complete
            thread.join()
            
            # Clean up current file and prepare for next iteration
            os.remove(current_file)
            current_file, next_file = next_file, f"speech_{uuid.uuid4().hex[:8]}.wav"
            cleaned_text = next_text
        
        # Play the last processed file
        print(f"Playing: {cleaned_text}")
        play_audio(current_file)
        os.remove(current_file)
        
        logger.info(f"Successfully played speech with {len(sentences)} segments")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Speech synthesis or playback timed out")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with return code {e.returncode}: {e.cmd}")
        return False
    except Exception as e:
        logger.error(f"Error in speech synthesis: {str(e)}")
        return False