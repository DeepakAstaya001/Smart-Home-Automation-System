#include <Servo.h>

// Define pins for doors, lights, and fans
const int hallDoorPin = 2;         // Hall door control pin
const int kitchenDoorPin = 3;      // Kitchen door control pin
const int livingRoomDoorPin = 4;   // Living room door control pin
const int hallLightPin = 5;        // Hall light control pin
const int kitchenLightPin = 6;     // Kitchen light control pin
const int livingRoomLightPin = 7;  // Living room light control pin
const int hallFanPin = 8;          // Hall fan control pin
const int kitchenFanPin = 9;       // Kitchen fan control pin
const int livingRoomFanPin = 10;   // Living room fan control pin

// Setup the servo motors (for doors)
Servo hallDoor, kitchenDoor, livingRoomDoor;

void setup() {
  // Initialize the serial communication
  Serial.begin(9600);
  delay(2000);  // Give time for the serial connection to establish

  // Set up pins for lights and fans
  pinMode(hallLightPin, OUTPUT);
  pinMode(kitchenLightPin, OUTPUT);
  pinMode(livingRoomLightPin, OUTPUT);
  pinMode(hallFanPin, OUTPUT);
  pinMode(kitchenFanPin, OUTPUT);
  pinMode(livingRoomFanPin, OUTPUT);

  // Initialize the servo motors for doors
  hallDoor.attach(11);      // Attach hall door to pin 11
  kitchenDoor.attach(12);   // Attach kitchen door to pin 12
  livingRoomDoor.attach(13); // Attach living room door to pin 13

  // Initially, set all lights and fans to OFF
  digitalWrite(hallLightPin, LOW);
  digitalWrite(kitchenLightPin, LOW);
  digitalWrite(livingRoomLightPin, LOW);
  digitalWrite(hallFanPin, LOW);
  digitalWrite(kitchenFanPin, LOW);
  digitalWrite(livingRoomFanPin, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readString();  // Read the command from the serial port
    command.trim();  // Remove any extra whitespace

    // Check for door commands
    if (command == "hall_door_open") {
      hallDoor.write(90);  // Open hall door
    }
    else if (command == "hall_door_close") {
      hallDoor.write(0);   // Close hall door
    }
    else if (command == "kitchen_door_open") {
      kitchenDoor.write(90);  // Open kitchen door
    }
    else if (command == "kitchen_door_close") {
      kitchenDoor.write(0);   // Close kitchen door
    }
    else if (command == "living_room_door_open") {
      livingRoomDoor.write(90);  // Open living room door
    }
    else if (command == "living_room_door_close") {
      livingRoomDoor.write(0);   // Close living room doors
    }
    
    // Check for light commands
    else if (command == "hall_light_on") {
      digitalWrite(hallLightPin, HIGH);  // Turn on hall light
    }
    else if (command == "hall_light_off") {
      digitalWrite(hallLightPin, LOW);   // Turn off hall light
    }
    else if (command == "kitchen_light_on") {
      digitalWrite(kitchenLightPin, HIGH);  // Turn on kitchen light
    }
    else if (command == "kitchen_light_off") {
      digitalWrite(kitchenLightPin, LOW);   // Turn off kitchen light
    }
    else if (command == "living_room_light_on") {
      digitalWrite(livingRoomLightPin, HIGH);  // Turn on living room light
    }
    else if (command == "living_room_light_off") {
      digitalWrite(livingRoomLightPin, LOW);   // Turn off living room light
    }

    // Check for fan commands
    else if (command == "hall_fan_on") {
      digitalWrite(hallFanPin, HIGH);  // Turn on hall fan
    }
    else if (command == "hall_fan_off") {
      digitalWrite(hallFanPin, LOW);   // Turn off hall fan
    }
    else if (command == "kitchen_fan_on") {
      digitalWrite(kitchenFanPin, HIGH);  // Turn on kitchen fan
    }
    else if (command == "kitchen_fan_off") {
      digitalWrite(kitchenFanPin, LOW);   // Turn off kitchen fan
    }
    else if (command == "living_room_fan_on") {
      digitalWrite(livingRoomFanPin, HIGH);  // Turn on living room fan
    }
    else if (command == "living_room_fan_off") {
      digitalWrite(livingRoomFanPin, LOW);   // Turn off living room fan
    }

    else {
      Serial.println("Unknown command: " + command);  // In case of an unrecognized command
    }
  }
}
