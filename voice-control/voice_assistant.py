"""
Advanced Voice Control System for Smart Home
Features: Multi-language support, Natural Language Processing, Wake Word Detection
Author: Deepak
Version: 2.0
"""

import speech_recognition as sr
import pyttsx3
import json
import threading
import time
import requests
import websocket
import paho.mqtt.client as mqtt
import numpy as np
import wave
import pyaudio
from datetime import datetime
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import openai
import google.generativeai as genai
from transformers import pipeline
import logging

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

# Configuration
class VoiceControlConfig:
    # API Keys (Replace with your actual keys)
    OPENAI_API_KEY = "your_openai_api_key_here"
    GOOGLE_API_KEY = "your_google_api_key_here"
    
    # Network Configuration
    ESP32_IP = "192.168.1.100"  # Your ESP32 IP address
    MQTT_BROKER = "localhost"
    MQTT_PORT = 1883
    MQTT_TOPIC_COMMAND = "smarthome/voice"
    
    # Voice Recognition Settings
    WAKE_WORDS = ["hey smart home", "smart home", "alexa", "google", "assistant"]
    LANGUAGES = {
        'en': 'english',
        'hi': 'hindi',
        'es': 'spanish',
        'fr': 'french',
        'de': 'german'
    }
    
    # Audio Settings
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    RECORD_SECONDS = 5
    CONFIDENCE_THRESHOLD = 0.7

class SmartHomeVoiceAssistant:
    def __init__(self):
        self.config = VoiceControlConfig()
        self.setup_logging()
        self.setup_speech_recognition()
        self.setup_text_to_speech()
        self.setup_mqtt()
        self.setup_ai_models()
        self.setup_command_mappings()
        
        # State variables
        self.listening = False
        self.current_language = 'en'
        self.wake_word_detected = False
        self.conversation_context = []
        
        # Device states cache
        self.device_states = {}
        
        print("Advanced Voice Control System Initialized!")
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('voice_control.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_speech_recognition(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self.microphone as source:
            print("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
        # Setup wake word detection
        self.setup_wake_word_detection()
        
    def setup_text_to_speech(self):
        self.tts_engine = pyttsx3.init()
        
        # Configure TTS settings
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)  # Use first available voice
        self.tts_engine.setProperty('rate', 150)  # Speech rate
        self.tts_engine.setProperty('volume', 0.8)  # Volume level
        
    def setup_mqtt(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        try:
            self.mqtt_client.connect(self.config.MQTT_BROKER, self.config.MQTT_PORT, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            self.logger.error(f"MQTT connection failed: {e}")
            
    def setup_ai_models(self):
        try:
            # Setup OpenAI
            if self.config.OPENAI_API_KEY != "your_openai_api_key_here":
                openai.api_key = self.config.OPENAI_API_KEY
                
            # Setup Google Generative AI
            if self.config.GOOGLE_API_KEY != "your_google_api_key_here":
                genai.configure(api_key=self.config.GOOGLE_API_KEY)
                
            # Setup local NLP model
            self.nlp_classifier = pipeline("text-classification", 
                                         model="distilbert-base-uncased-finetuned-sst-2-english")
            
            self.logger.info("AI models initialized successfully")
        except Exception as e:
            self.logger.error(f"AI model setup failed: {e}")
            
    def setup_wake_word_detection(self):
        """Setup wake word detection using audio analysis"""
        self.wake_word_model = None
        try:
            # You can integrate with libraries like snowboy, porcupine, or vosk
            # For now, we'll use simple keyword matching
            pass
        except Exception as e:
            self.logger.error(f"Wake word detection setup failed: {e}")
            
    def setup_command_mappings(self):
        """Define natural language to device command mappings"""
        self.command_mappings = {
            # Light controls
            'lights': {
                'patterns': [
                    r'turn (on|off) (?:the )?(.+) light',
                    r'(switch|toggle) (?:the )?(.+) light (on|off)',
                    r'(.+) light (on|off)',
                    r'(brighten|dim) (?:the )?(.+) light',
                    r'set (.+) light to (\d+)%?'
                ],
                'rooms': ['hall', 'kitchen', 'living room', 'bedroom', 'bathroom', 'all']
            },
            
            # Fan controls
            'fans': {
                'patterns': [
                    r'turn (on|off) (?:the )?(.+) fan',
                    r'(start|stop) (?:the )?(.+) fan',
                    r'(.+) fan (on|off)',
                    r'set (.+) fan speed to (\d+)',
                    r'(increase|decrease) (.+) fan speed'
                ],
                'rooms': ['hall', 'kitchen', 'living room', 'bedroom', 'all']
            },
            
            # Door controls
            'doors': {
                'patterns': [
                    r'(open|close) (?:the )?(.+) door',
                    r'(lock|unlock) (?:the )?(.+) door',
                    r'(.+) door (open|close|lock|unlock)'
                ],
                'doors': ['hall', 'kitchen', 'living room', 'main', 'front', 'all']
            },
            
            # Security system
            'security': {
                'patterns': [
                    r'(arm|disarm) (?:the )?security (?:system)?',
                    r'(activate|deactivate) (?:the )?alarm',
                    r'security (on|off)',
                    r'set security mode to (.+)'
                ]
            },
            
            # Climate control
            'climate': {
                'patterns': [
                    r'set temperature to (\d+)',
                    r'(increase|decrease) temperature',
                    r'make it (warmer|cooler|hotter|colder)',
                    r'turn on (?:the )?ac',
                    r'what is (?:the )?temperature'
                ]
            },
            
            # Scene controls
            'scenes': {
                'patterns': [
                    r'activate (.+) scene',
                    r'set (.+) mode',
                    r'good (morning|night)',
                    r'movie time',
                    r'party mode',
                    r'sleep mode'
                ]
            },
            
            # System queries
            'queries': {
                'patterns': [
                    r'what is (?:the )?status',
                    r'show me (?:the )?(.+) status',
                    r'how much power (?:are we using|consumption)',
                    r'what time is it',
                    r'weather (?:forecast|today|tomorrow)'
                ]
            }
        }
        
    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("Connected to MQTT broker")
            client.subscribe("smarthome/status")
        else:
            self.logger.error(f"Failed to connect to MQTT broker: {rc}")
            
    def on_mqtt_message(self, client, userdata, msg):
        try:
            message = json.loads(msg.payload.decode())
            self.device_states = message
        except Exception as e:
            self.logger.error(f"Error processing MQTT message: {e}")
            
    def listen_for_wake_word(self):
        """Continuously listen for wake words"""
        self.logger.info("Listening for wake words...")
        
        while True:
            try:
                with self.microphone as source:
                    # Listen for wake word with shorter timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    
                    # Check for wake words
                    for wake_word in self.config.WAKE_WORDS:
                        if wake_word in text:
                            self.wake_word_detected = True
                            self.speak("Yes, I'm listening!")
                            self.process_voice_command()
                            break
                            
                except sr.UnknownValueError:
                    # No speech detected, continue listening
                    pass
                except sr.RequestError as e:
                    self.logger.error(f"Could not request results: {e}")
                    
            except sr.WaitTimeoutError:
                # Timeout is expected, continue listening
                pass
            except Exception as e:
                self.logger.error(f"Error in wake word detection: {e}")
                time.sleep(1)
                
    def process_voice_command(self):
        """Process voice command after wake word detection"""
        try:
            self.speak("What can I help you with?")
            
            with self.microphone as source:
                # Listen for command with longer timeout
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            # Try multiple recognition services
            command_text = self.recognize_speech(audio)
            
            if command_text:
                self.logger.info(f"Recognized command: {command_text}")
                response = self.process_natural_language_command(command_text)
                self.speak(response)
            else:
                self.speak("Sorry, I didn't understand that. Please try again.")
                
        except sr.WaitTimeoutError:
            self.speak("I didn't hear anything. Try saying the wake word again.")
        except Exception as e:
            self.logger.error(f"Error processing voice command: {e}")
            self.speak("Sorry, there was an error processing your command.")
            
    def recognize_speech(self, audio):
        """Try multiple speech recognition services"""
        recognition_services = [
            ('google', lambda: self.recognizer.recognize_google(audio)),
            ('sphinx', lambda: self.recognizer.recognize_sphinx(audio)),
            ('wit', lambda: self.recognizer.recognize_wit(audio, key="YOUR_WIT_AI_KEY") if hasattr(self.recognizer, 'recognize_wit') else None)
        ]
        
        for service_name, recognize_func in recognition_services:
            try:
                result = recognize_func()
                if result:
                    self.logger.info(f"Recognized using {service_name}: {result}")
                    return result.lower()
            except Exception as e:
                self.logger.debug(f"{service_name} recognition failed: {e}")
                continue
                
        return None
        
    def process_natural_language_command(self, text):
        """Process natural language command using NLP"""
        try:
            # Add to conversation context
            self.conversation_context.append({
                'timestamp': datetime.now().isoformat(),
                'user_input': text,
                'type': 'command'
            })
            
            # Clean and tokenize text
            cleaned_text = self.clean_text(text)
            
            # Extract intent and entities
            intent, entities = self.extract_intent_and_entities(cleaned_text)
            
            if intent:
                # Execute command based on intent
                return self.execute_intent(intent, entities, text)
            else:
                # Use AI for complex queries
                return self.handle_with_ai(text)
                
        except Exception as e:
            self.logger.error(f"Error in NLP processing: {e}")
            return "Sorry, I had trouble understanding your request."
            
    def clean_text(self, text):
        """Clean and normalize text"""
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Tokenize and remove stop words
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word not in stop_words]
        
        return ' '.join(filtered_tokens)
        
    def extract_intent_and_entities(self, text):
        """Extract intent and entities from text"""
        intent = None
        entities = {}
        
        # Check each command category
        for category, config in self.command_mappings.items():
            for pattern in config['patterns']:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    intent = category
                    entities['action'] = match.group(1) if match.lastindex >= 1 else None
                    entities['target'] = match.group(2) if match.lastindex >= 2 else None
                    entities['value'] = match.group(3) if match.lastindex >= 3 else None
                    entities['full_match'] = match.groups()
                    break
            if intent:
                break
                
        return intent, entities
        
    def execute_intent(self, intent, entities, original_text):
        """Execute command based on detected intent"""
        try:
            if intent == 'lights':
                return self.control_lights(entities)
            elif intent == 'fans':
                return self.control_fans(entities)
            elif intent == 'doors':
                return self.control_doors(entities)
            elif intent == 'security':
                return self.control_security(entities)
            elif intent == 'climate':
                return self.control_climate(entities)
            elif intent == 'scenes':
                return self.activate_scene(entities)
            elif intent == 'queries':
                return self.handle_query(entities, original_text)
            else:
                return "I'm not sure how to handle that command yet."
                
        except Exception as e:
            self.logger.error(f"Error executing intent {intent}: {e}")
            return "Sorry, there was an error executing that command."
            
    def control_lights(self, entities):
        """Control lighting systems"""
        action = entities.get('action', '').lower()
        target = entities.get('target', '').lower()
        
        # Map natural language to device commands
        state = 'on' if action in ['on', 'brighten', 'switch', 'turn'] else 'off'
        
        # Determine room
        room_mapping = {
            'hall': 'hall_light',
            'kitchen': 'kitchen_light',
            'living': 'living_room_light',
            'bedroom': 'bedroom_light',
            'bathroom': 'bathroom_light',
            'all': 'all_lights'
        }
        
        room = None
        for key, value in room_mapping.items():
            if key in target or key in entities.get('target', ''):
                room = value
                break
                
        if room:
            command = f"{room}_{state}"
            self.send_command(command)
            return f"Turning {state} the {target} light."
        else:
            return "I couldn't determine which light you want to control."
            
    def control_fans(self, entities):
        """Control fan systems"""
        action = entities.get('action', '').lower()
        target = entities.get('target', '').lower()
        
        state = 'on' if action in ['on', 'start', 'turn'] else 'off'
        
        room_mapping = {
            'hall': 'hall_fan',
            'kitchen': 'kitchen_fan',
            'living': 'living_room_fan',
            'bedroom': 'bedroom_fan',
            'all': 'all_fans'
        }
        
        room = None
        for key, value in room_mapping.items():
            if key in target:
                room = value
                break
                
        if room:
            command = f"{room}_{state}"
            self.send_command(command)
            return f"Turning {state} the {target} fan."
        else:
            return "I couldn't determine which fan you want to control."
            
    def control_doors(self, entities):
        """Control door systems"""
        action = entities.get('action', '').lower()
        target = entities.get('target', '').lower()
        
        state = 'open' if action in ['open', 'unlock'] else 'close'
        
        door_mapping = {
            'hall': 'hall_door',
            'kitchen': 'kitchen_door',
            'living': 'living_room_door',
            'main': 'main_door',
            'front': 'main_door'
        }
        
        door = None
        for key, value in door_mapping.items():
            if key in target:
                door = value
                break
                
        if door:
            command = f"{door}_{state}"
            self.send_command(command)
            return f"{action.capitalize()}ing the {target} door."
        else:
            return "I couldn't determine which door you want to control."
            
    def control_security(self, entities):
        """Control security system"""
        action = entities.get('action', '').lower()
        
        if action in ['arm', 'activate', 'on']:
            self.send_command("security_arm")
            return "Security system armed."
        elif action in ['disarm', 'deactivate', 'off']:
            self.send_command("security_disarm")
            return "Security system disarmed."
        else:
            return "I couldn't understand the security command."
            
    def control_climate(self, entities):
        """Control climate systems"""
        # Implementation for climate control
        return "Climate control is not yet implemented."
        
    def activate_scene(self, entities):
        """Activate predefined scenes"""
        target = entities.get('target', '').lower()
        
        scenes = {
            'morning': ['all_lights_on', 'coffee_maker_on'],
            'night': ['all_lights_off', 'security_arm'],
            'movie': ['living_room_light_dim', 'tv_on'],
            'party': ['all_lights_on', 'music_on'],
            'sleep': ['all_lights_off', 'bedroom_fan_on']
        }
        
        if target in scenes:
            for command in scenes[target]:
                self.send_command(command)
            return f"Activated {target} scene."
        else:
            return "I couldn't find that scene."
            
    def handle_query(self, entities, original_text):
        """Handle status queries and information requests"""
        if 'status' in original_text:
            return self.get_system_status()
        elif 'power' in original_text or 'consumption' in original_text:
            return self.get_power_consumption()
        elif 'time' in original_text:
            return f"The current time is {datetime.now().strftime('%I:%M %p')}"
        elif 'weather' in original_text:
            return self.get_weather_info()
        else:
            return "I'm not sure what information you're looking for."
            
    def handle_with_ai(self, text):
        """Handle complex queries using AI"""
        try:
            # Use OpenAI GPT for complex queries
            if hasattr(openai, 'api_key') and openai.api_key:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a smart home assistant. Respond helpfully and concisely."},
                        {"role": "user", "content": text}
                    ],
                    max_tokens=150
                )
                return response.choices[0].message.content
            else:
                return "I don't have enough information to answer that question."
                
        except Exception as e:
            self.logger.error(f"AI processing error: {e}")
            return "I'm having trouble processing that request."
            
    def send_command(self, command):
        """Send command to smart home system"""
        try:
            # Send via MQTT
            command_data = {
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'source': 'voice_control'
            }
            
            self.mqtt_client.publish(
                self.config.MQTT_TOPIC_COMMAND,
                json.dumps(command_data)
            )
            
            # Also send via HTTP to ESP32
            url = f"http://{self.config.ESP32_IP}/api/control"
            data = {'command': command, 'value': '1'}
            requests.post(url, data=data, timeout=5)
            
            self.logger.info(f"Sent command: {command}")
            
        except Exception as e:
            self.logger.error(f"Error sending command: {e}")
            
    def speak(self, text):
        """Convert text to speech"""
        try:
            self.logger.info(f"Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
            
    def get_system_status(self):
        """Get current system status"""
        if self.device_states:
            temp = self.device_states.get('temperature', 'unknown')
            humidity = self.device_states.get('humidity', 'unknown')
            power = self.device_states.get('power_consumption', 'unknown')
            
            lights_on = sum(self.device_states.get('lights', []))
            fans_on = sum(self.device_states.get('fans', []))
            
            return f"Temperature is {temp}°C, humidity {humidity}%, {lights_on} lights and {fans_on} fans are on. Power consumption is {power} watts."
        else:
            return "I don't have current status information."
            
    def get_power_consumption(self):
        """Get power consumption information"""
        if self.device_states:
            power = self.device_states.get('power_consumption', 0)
            daily = self.device_states.get('daily_consumption', 0)
            return f"Current power consumption is {power} watts. Daily consumption is {daily} kilowatt hours."
        else:
            return "Power consumption data is not available."
            
    def get_weather_info(self):
        """Get weather information (placeholder)"""
        # You can integrate with weather APIs here
        return "Weather information is not currently available."
        
    def run(self):
        """Main run loop"""
        print("Starting Advanced Voice Control System...")
        
        # Start wake word detection in a separate thread
        wake_word_thread = threading.Thread(target=self.listen_for_wake_word, daemon=True)
        wake_word_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down Voice Control System...")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

def main():
    assistant = SmartHomeVoiceAssistant()
    assistant.run()

if __name__ == "__main__":
    main()