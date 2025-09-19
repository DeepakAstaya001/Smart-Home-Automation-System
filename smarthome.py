import speech_recognition as sr
import serial
import time

# Set up serial communication (adjust the 'COM3' and '9600' according to your Arduino's port and baud rate)
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Wait for the connection to be established

# Function to send commands to Arduino
def send_to_arduino(command):
    arduino.write(command.encode())
    time.sleep(1)  # Give Arduino time to process the command

# Initialize the recognizer
recognizer = sr.Recognizer()

# Function to recognize speech and process commands
def recognize_and_process():
    with sr.Microphone() as source:
        print("Listening for commands...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
        audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            command = command.lower()  # Convert the command to lowercase for consistency
            print(f"Recognized command: {command}")

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
while True:
    recognize_and_process()
