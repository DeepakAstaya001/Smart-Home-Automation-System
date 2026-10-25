import os
import speech_recognition as sr
import serial
import time

# Serial settings can be overridden with environment variables, e.g.
#   ARDUINO_PORT=/dev/ttyUSB0 python smarthome.py
SERIAL_PORT = os.environ.get("ARDUINO_PORT", "COM3")
BAUD_RATE = int(os.environ.get("ARDUINO_BAUD", "9600"))

# Set up serial communication
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except serial.SerialException as e:
    raise SystemExit(f"Could not open serial port {SERIAL_PORT}: {e}")
time.sleep(2)  # Wait for the connection to be established

# Function to send commands to Arduino
def send_to_arduino(command):
    # Newline-terminate so the Arduino parses the command immediately
    arduino.write((command + "\n").encode())
    arduino.flush()

# Initialize the recognizer
recognizer = sr.Recognizer()

# Define the command mappings
command_mappings = {
    "open hall door": "hall_door_open",
    "close hall door": "hall_door_close",
    "open kitchen door": "kitchen_door_open",
    "close kitchen door": "kitchen_door_close",
    "open living room door": "living_room_door_open",
    "close living room door": "living_room_door_close",
    "turn on hall light": "hall_light_on",
    "turn off hall light": "hall_light_off",
    "turn on kitchen light": "kitchen_light_on",
    "turn off kitchen light": "kitchen_light_off",
    "turn on living room light": "living_room_light_on",
    "turn off living room light": "living_room_light_off",
    "turn on hall fan": "hall_fan_on",
    "turn off hall fan": "hall_fan_off",
    "turn on kitchen fan": "kitchen_fan_on",
    "turn off kitchen fan": "kitchen_fan_off",
    "turn on living room fan": "living_room_fan_on",
    "turn off living room fan": "living_room_fan_off"
}

# Function to recognize speech and process commands
def recognize_and_process(source):
    print("Listening for commands...")
    audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        command = command.lower().strip()  # Normalize for consistent matching
        print(f"Recognized command: {command}")

        # Check if the command exists in our mappings
        if command in command_mappings:
            send_to_arduino(command_mappings[command])
            print(f"Sent command to Arduino: {command_mappings[command]}")
        else:
            print("Unknown command")

    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main loop to continuously listen for commands
if __name__ == "__main__":
    try:
        with sr.Microphone() as source:
            # Calibrate once instead of on every command, which added ~1s latency
            recognizer.adjust_for_ambient_noise(source)
            while True:
                recognize_and_process(source)
    except KeyboardInterrupt:
        print("\nStopping voice control.")
    finally:
        arduino.close()
