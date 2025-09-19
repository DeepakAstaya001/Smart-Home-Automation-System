/*
 * Advanced Smart Home Automation System - ESP32 Main Controller
 * Features: Voice Control, Mobile App, Web Interface, Security, Energy Management
 * Hardware: ESP32, Sensors, Actuators, Cameras, Biometric Sensors
 * Author: Deepak
 * Version: 2.0
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Servo.h>
#include <WiFiClient.h>
#include <PubSubClient.h>
#include <BluetoothSerial.h>
#include <ESP32Servo.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <SPIFFS.h>
#include <WebSocketsServer.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

// Network Configuration
const char* ssid = "Your_WiFi_SSID";
const char* password = "Your_WiFi_Password";
const char* mqtt_server = "mqtt.broker.address";
const char* device_id = "SmartHome_ESP32_01";

// Pin Definitions - Hardware Components
// Lighting Control
#define HALL_LIGHT_PIN 5
#define KITCHEN_LIGHT_PIN 6
#define LIVING_ROOM_LIGHT_PIN 7
#define BEDROOM_LIGHT_PIN 8
#define BATHROOM_LIGHT_PIN 9

// Fan Control
#define HALL_FAN_PIN 10
#define KITCHEN_FAN_PIN 11
#define LIVING_ROOM_FAN_PIN 12
#define BEDROOM_FAN_PIN 13

// Door Control (Servo Motors)
#define HALL_DOOR_PIN 14
#define KITCHEN_DOOR_PIN 15
#define LIVING_ROOM_DOOR_PIN 16
#define MAIN_DOOR_PIN 17

// Sensors
#define DHT_PIN 2
#define DHT_TYPE DHT22
#define PIR_HALL_PIN 18
#define PIR_KITCHEN_PIN 19
#define PIR_LIVING_ROOM_PIN 20
#define PIR_BEDROOM_PIN 21
#define SMOKE_SENSOR_PIN 22
#define GAS_SENSOR_PIN 23
#define SOUND_SENSOR_PIN 24
#define LIGHT_SENSOR_PIN 25

// Security System
#define BUZZER_PIN 26
#define LED_STATUS_PIN 27
#define FINGERPRINT_RX_PIN 28
#define FINGERPRINT_TX_PIN 29
#define CAMERA_PIN 30

// Energy Management
#define CURRENT_SENSOR_PIN 31
#define VOLTAGE_SENSOR_PIN 32
#define RELAY_MAIN_POWER_PIN 33

// Objects and Variables
DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient espClient;
PubSubClient mqttClient(espClient);
BluetoothSerial SerialBT;
AsyncWebServer server(80);
WebSocketsServer webSocket(81);
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 19800, 60000); // UTC+5:30 for India

// Servo objects for doors
Servo hallDoor, kitchenDoor, livingRoomDoor, mainDoor;

// System State Variables
struct DeviceStates {
    bool lights[5] = {false, false, false, false, false}; // hall, kitchen, living, bedroom, bathroom
    bool fans[4] = {false, false, false, false}; // hall, kitchen, living, bedroom
    bool doors[4] = {false, false, false, false}; // hall, kitchen, living, main
    bool security_armed = false;
    bool auto_mode = true;
    float temperature = 0.0;
    float humidity = 0.0;
    bool motion_detected[4] = {false, false, false, false}; // hall, kitchen, living, bedroom
    bool smoke_detected = false;
    bool gas_detected = false;
    float power_consumption = 0.0;
    String last_command = "";
    unsigned long last_motion_time[4] = {0, 0, 0, 0};
} deviceState;

// Energy Management
struct EnergyData {
    float voltage = 0.0;
    float current = 0.0;
    float power = 0.0;
    float daily_consumption = 0.0;
    unsigned long last_reading_time = 0;
} energyData;

// Auto-off timers (in milliseconds)
const unsigned long AUTO_OFF_DELAY = 300000; // 5 minutes
const unsigned long SECURITY_DELAY = 30000; // 30 seconds

// Function Prototypes
void setup_wifi();
void setup_mqtt();
void setup_ota();
void setup_webserver();
void setup_websocket();
void mqtt_callback(char* topic, byte* payload, unsigned int length);
void reconnect_mqtt();
void handle_sensors();
void handle_motion_detection();
void handle_energy_management();
void handle_security();
void handle_auto_mode();
void execute_command(String command, String value = "");
void send_sensor_data();
void webSocket_event(uint8_t num, WStype_t type, uint8_t * payload, size_t length);
String get_device_status();
void control_light(int room, bool state);
void control_fan(int room, bool state);
void control_door(int door, bool state);
void emergency_shutdown();

void setup() {
    Serial.begin(115200);
    SerialBT.begin("SmartHome_ESP32");
    
    // Initialize SPIFFS
    if (!SPIFFS.begin(true)) {
        Serial.println("SPIFFS Mount Failed");
        return;
    }
    
    // Initialize pins
    pinMode(HALL_LIGHT_PIN, OUTPUT);
    pinMode(KITCHEN_LIGHT_PIN, OUTPUT);
    pinMode(LIVING_ROOM_LIGHT_PIN, OUTPUT);
    pinMode(BEDROOM_LIGHT_PIN, OUTPUT);
    pinMode(BATHROOM_LIGHT_PIN, OUTPUT);
    
    pinMode(HALL_FAN_PIN, OUTPUT);
    pinMode(KITCHEN_FAN_PIN, OUTPUT);
    pinMode(LIVING_ROOM_FAN_PIN, OUTPUT);
    pinMode(BEDROOM_FAN_PIN, OUTPUT);
    
    pinMode(PIR_HALL_PIN, INPUT);
    pinMode(PIR_KITCHEN_PIN, INPUT);
    pinMode(PIR_LIVING_ROOM_PIN, INPUT);
    pinMode(PIR_BEDROOM_PIN, INPUT);
    
    pinMode(SMOKE_SENSOR_PIN, INPUT);
    pinMode(GAS_SENSOR_PIN, INPUT);
    pinMode(SOUND_SENSOR_PIN, INPUT);
    pinMode(LIGHT_SENSOR_PIN, INPUT);
    
    pinMode(BUZZER_PIN, OUTPUT);
    pinMode(LED_STATUS_PIN, OUTPUT);
    pinMode(RELAY_MAIN_POWER_PIN, OUTPUT);
    
    // Initialize servo motors
    hallDoor.attach(HALL_DOOR_PIN);
    kitchenDoor.attach(KITCHEN_DOOR_PIN);
    livingRoomDoor.attach(LIVING_ROOM_DOOR_PIN);
    mainDoor.attach(MAIN_DOOR_PIN);
    
    // Initialize all devices to OFF state
    for(int i = 0; i < 5; i++) {
        digitalWrite(HALL_LIGHT_PIN + i, LOW);
    }
    for(int i = 0; i < 4; i++) {
        digitalWrite(HALL_FAN_PIN + i, LOW);
    }
    
    // Close all doors initially
    hallDoor.write(0);
    kitchenDoor.write(0);
    livingRoomDoor.write(0);
    mainDoor.write(0);
    
    // Initialize sensors
    dht.begin();
    
    // Setup network and services
    setup_wifi();
    setup_mqtt();
    setup_ota();
    setup_webserver();
    setup_websocket();
    
    // Initialize NTP client
    timeClient.begin();
    
    digitalWrite(LED_STATUS_PIN, HIGH); // System ready indicator
    Serial.println("Advanced Smart Home System Ready!");
    
    // Send initial status
    send_sensor_data();
}

void loop() {
    // Handle network connections
    if (!WiFi.isConnected()) {
        setup_wifi();
    }
    
    if (!mqttClient.connected()) {
        reconnect_mqtt();
    }
    mqttClient.loop();
    
    // Handle OTA updates
    ArduinoOTA.handle();
    
    // Update time
    timeClient.update();
    
    // Handle WebSocket connections
    webSocket.loop();
    
    // Handle sensors and automation
    handle_sensors();
    handle_motion_detection();
    handle_energy_management();
    handle_security();
    handle_auto_mode();
    
    // Handle Bluetooth commands
    if (SerialBT.available()) {
        String bt_command = SerialBT.readString();
        bt_command.trim();
        execute_command(bt_command);
        SerialBT.println("Command executed: " + bt_command);
    }
    
    // Handle Serial commands
    if (Serial.available()) {
        String serial_command = Serial.readString();
        serial_command.trim();
        execute_command(serial_command);
        Serial.println("Command executed: " + serial_command);
    }
    
    // Send periodic updates
    static unsigned long last_update = 0;
    if (millis() - last_update > 10000) { // Every 10 seconds
        send_sensor_data();
        last_update = millis();
    }
    
    delay(100);
}

void setup_wifi() {
    delay(10);
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);
    
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.isConnected()) {
        Serial.println("");
        Serial.println("WiFi connected!");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("WiFi connection failed!");
    }
}

void setup_mqtt() {
    mqttClient.setServer(mqtt_server, 1883);
    mqttClient.setCallback(mqtt_callback);
}

void setup_ota() {
    ArduinoOTA.setHostname("SmartHome-ESP32");
    ArduinoOTA.setPassword("admin"); // Change this password
    
    ArduinoOTA.onStart([]() {
        String type;
        if (ArduinoOTA.getCommand() == U_FLASH) {
            type = "sketch";
        } else {
            type = "filesystem";
        }
        Serial.println("Start updating " + type);
    });
    
    ArduinoOTA.onEnd([]() {
        Serial.println("\nEnd");
    });
    
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    });
    
    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("Error[%u]: ", error);
        if (error == OTA_AUTH_ERROR) {
            Serial.println("Auth Failed");
        } else if (error == OTA_BEGIN_ERROR) {
            Serial.println("Begin Failed");
        } else if (error == OTA_CONNECT_ERROR) {
            Serial.println("Connect Failed");
        } else if (error == OTA_RECEIVE_ERROR) {
            Serial.println("Receive Failed");
        } else if (error == OTA_END_ERROR) {
            Serial.println("End Failed");
        }
    });
    
    ArduinoOTA.begin();
}

void setup_webserver() {
    // Serve static files
    server.serveStatic("/", SPIFFS, "/");
    
    // API endpoints
    server.on("/api/status", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send(200, "application/json", get_device_status());
    });
    
    server.on("/api/control", HTTP_POST, [](AsyncWebServerRequest *request) {
        if (request->hasParam("command", true) && request->hasParam("value", true)) {
            String command = request->getParam("command", true)->value();
            String value = request->getParam("value", true)->value();
            execute_command(command, value);
            request->send(200, "application/json", "{\"status\":\"success\"}");
        } else {
            request->send(400, "application/json", "{\"status\":\"error\",\"message\":\"Missing parameters\"}");
        }
    });
    
    server.on("/api/energy", HTTP_GET, [](AsyncWebServerRequest *request) {
        DynamicJsonDocument doc(1024);
        doc["voltage"] = energyData.voltage;
        doc["current"] = energyData.current;
        doc["power"] = energyData.power;
        doc["daily_consumption"] = energyData.daily_consumption;
        doc["timestamp"] = timeClient.getEpochTime();
        
        String response;
        serializeJson(doc, response);
        request->send(200, "application/json", response);
    });
    
    server.begin();
}

void setup_websocket() {
    webSocket.begin();
    webSocket.onEvent(webSocket_event);
}

void webSocket_event(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.printf("[%u] Disconnected!\n", num);
            break;
            
        case WStype_CONNECTED:
            {
                IPAddress ip = webSocket.remoteIP(num);
                Serial.printf("[%u] Connected from %d.%d.%d.%d url: %s\n", num, ip[0], ip[1], ip[2], ip[3], payload);
                webSocket.sendTXT(num, get_device_status());
            }
            break;
            
        case WStype_TEXT:
            {
                String command = String((char*)payload);
                Serial.printf("[%u] Received: %s\n", num, command.c_str());
                
                // Parse JSON command
                DynamicJsonDocument doc(1024);
                deserializeJson(doc, command);
                
                if (doc.containsKey("command")) {
                    String cmd = doc["command"];
                    String value = doc.containsKey("value") ? doc["value"] : "";
                    execute_command(cmd, value);
                    webSocket.broadcastTXT(get_device_status());
                }
            }
            break;
            
        default:
            break;
    }
}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
    String message;
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    Serial.println(message);
    
    // Parse MQTT commands
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, message);
    
    if (doc.containsKey("command")) {
        String command = doc["command"];
        String value = doc.containsKey("value") ? doc["value"] : "";
        execute_command(command, value);
    }
}

void reconnect_mqtt() {
    while (!mqttClient.connected()) {
        Serial.print("Attempting MQTT connection...");
        
        if (mqttClient.connect(device_id)) {
            Serial.println("connected");
            mqttClient.subscribe("smarthome/command");
            mqttClient.subscribe("smarthome/voice");
            mqttClient.subscribe("smarthome/mobile");
        } else {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}

void execute_command(String command, String value) {
    command.toLowerCase();
    value.toLowerCase();
    
    deviceState.last_command = command + ":" + value;
    
    // Light controls
    if (command.indexOf("light") != -1) {
        bool state = (value == "on" || value == "1" || value == "true");
        
        if (command.indexOf("hall") != -1) control_light(0, state);
        else if (command.indexOf("kitchen") != -1) control_light(1, state);
        else if (command.indexOf("living") != -1) control_light(2, state);
        else if (command.indexOf("bedroom") != -1) control_light(3, state);
        else if (command.indexOf("bathroom") != -1) control_light(4, state);
        else if (command.indexOf("all") != -1) {
            for (int i = 0; i < 5; i++) control_light(i, state);
        }
    }
    
    // Fan controls
    else if (command.indexOf("fan") != -1) {
        bool state = (value == "on" || value == "1" || value == "true");
        
        if (command.indexOf("hall") != -1) control_fan(0, state);
        else if (command.indexOf("kitchen") != -1) control_fan(1, state);
        else if (command.indexOf("living") != -1) control_fan(2, state);
        else if (command.indexOf("bedroom") != -1) control_fan(3, state);
        else if (command.indexOf("all") != -1) {
            for (int i = 0; i < 4; i++) control_fan(i, state);
        }
    }
    
    // Door controls
    else if (command.indexOf("door") != -1) {
        bool state = (value == "open" || value == "1" || value == "true");
        
        if (command.indexOf("hall") != -1) control_door(0, state);
        else if (command.indexOf("kitchen") != -1) control_door(1, state);
        else if (command.indexOf("living") != -1) control_door(2, state);
        else if (command.indexOf("main") != -1) control_door(3, state);
    }
    
    // Security system
    else if (command.indexOf("security") != -1) {
        if (value == "arm" || value == "on") {
            deviceState.security_armed = true;
            digitalWrite(LED_STATUS_PIN, HIGH);
        } else if (value == "disarm" || value == "off") {
            deviceState.security_armed = false;
            digitalWrite(BUZZER_PIN, LOW);
        }
    }
    
    // Auto mode
    else if (command.indexOf("auto") != -1) {
        deviceState.auto_mode = (value == "on" || value == "1" || value == "true");
    }
    
    // Emergency commands
    else if (command.indexOf("emergency") != -1 || command.indexOf("panic") != -1) {
        emergency_shutdown();
    }
    
    // All off command
    else if (command.indexOf("all_off") != -1 || command.indexOf("shutdown") != -1) {
        for (int i = 0; i < 5; i++) control_light(i, false);
        for (int i = 0; i < 4; i++) control_fan(i, false);
    }
    
    Serial.println("Executed: " + command + " = " + value);
}

void control_light(int room, bool state) {
    int pins[] = {HALL_LIGHT_PIN, KITCHEN_LIGHT_PIN, LIVING_ROOM_LIGHT_PIN, BEDROOM_LIGHT_PIN, BATHROOM_LIGHT_PIN};
    if (room >= 0 && room < 5) {
        digitalWrite(pins[room], state ? HIGH : LOW);
        deviceState.lights[room] = state;
    }
}

void control_fan(int room, bool state) {
    int pins[] = {HALL_FAN_PIN, KITCHEN_FAN_PIN, LIVING_ROOM_FAN_PIN, BEDROOM_FAN_PIN};
    if (room >= 0 && room < 4) {
        digitalWrite(pins[room], state ? HIGH : LOW);
        deviceState.fans[room] = state;
    }
}

void control_door(int door, bool state) {
    Servo* servos[] = {&hallDoor, &kitchenDoor, &livingRoomDoor, &mainDoor};
    if (door >= 0 && door < 4) {
        servos[door]->write(state ? 90 : 0);
        deviceState.doors[door] = state;
    }
}

void handle_sensors() {
    // Read temperature and humidity
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    
    if (!isnan(temp) && !isnan(hum)) {
        deviceState.temperature = temp;
        deviceState.humidity = hum;
    }
    
    // Read motion sensors
    deviceState.motion_detected[0] = digitalRead(PIR_HALL_PIN);
    deviceState.motion_detected[1] = digitalRead(PIR_KITCHEN_PIN);
    deviceState.motion_detected[2] = digitalRead(PIR_LIVING_ROOM_PIN);
    deviceState.motion_detected[3] = digitalRead(PIR_BEDROOM_PIN);
    
    // Read safety sensors
    deviceState.smoke_detected = digitalRead(SMOKE_SENSOR_PIN);
    deviceState.gas_detected = digitalRead(GAS_SENSOR_PIN);
    
    // Handle emergency situations
    if (deviceState.smoke_detected || deviceState.gas_detected) {
        emergency_shutdown();
    }
}

void handle_motion_detection() {
    for (int i = 0; i < 4; i++) {
        if (deviceState.motion_detected[i]) {
            deviceState.last_motion_time[i] = millis();
            
            // Auto turn on lights in auto mode
            if (deviceState.auto_mode && !deviceState.lights[i]) {
                control_light(i, true);
            }
        }
    }
}

void handle_auto_mode() {
    if (!deviceState.auto_mode) return;
    
    unsigned long current_time = millis();
    
    // Auto-off lights and fans after no motion
    for (int i = 0; i < 4; i++) {
        if (current_time - deviceState.last_motion_time[i] > AUTO_OFF_DELAY) {
            if (deviceState.lights[i]) {
                control_light(i, false);
            }
            if (deviceState.fans[i] && deviceState.temperature < 28.0) {
                control_fan(i, false);
            }
        }
    }
    
    // Auto fan control based on temperature
    if (deviceState.temperature > 30.0) {
        for (int i = 0; i < 4; i++) {
            if (deviceState.motion_detected[i] || (current_time - deviceState.last_motion_time[i] < AUTO_OFF_DELAY)) {
                control_fan(i, true);
            }
        }
    }
}

void handle_energy_management() {
    // Read voltage and current sensors
    energyData.voltage = analogRead(VOLTAGE_SENSOR_PIN) * (230.0 / 4095.0);
    energyData.current = analogRead(CURRENT_SENSOR_PIN) * (10.0 / 4095.0);
    energyData.power = energyData.voltage * energyData.current;
    
    // Calculate daily consumption
    unsigned long current_time = millis();
    if (energyData.last_reading_time > 0) {
        float time_diff = (current_time - energyData.last_reading_time) / 3600000.0; // hours
        energyData.daily_consumption += energyData.power * time_diff / 1000.0; // kWh
    }
    energyData.last_reading_time = current_time;
    
    deviceState.power_consumption = energyData.power;
}

void handle_security() {
    if (!deviceState.security_armed) return;
    
    bool intrusion_detected = false;
    
    // Check motion sensors
    for (int i = 0; i < 4; i++) {
        if (deviceState.motion_detected[i]) {
            intrusion_detected = true;
            break;
        }
    }
    
    // Check sound sensor
    if (digitalRead(SOUND_SENSOR_PIN)) {
        intrusion_detected = true;
    }
    
    if (intrusion_detected) {
        // Trigger alarm
        digitalWrite(BUZZER_PIN, HIGH);
        
        // Send alert via MQTT
        DynamicJsonDocument doc(512);
        doc["alert"] = "SECURITY_BREACH";
        doc["timestamp"] = timeClient.getEpochTime();
        doc["device_id"] = device_id;
        
        String alert_message;
        serializeJson(doc, alert_message);
        mqttClient.publish("smarthome/alert", alert_message.c_str());
        
        // Broadcast to WebSocket clients
        webSocket.broadcastTXT(alert_message);
    }
}

void emergency_shutdown() {
    // Turn off all electrical appliances
    for (int i = 0; i < 5; i++) control_light(i, false);
    for (int i = 0; i < 4; i++) control_fan(i, false);
    
    // Open all doors for emergency exit
    for (int i = 0; i < 4; i++) control_door(i, true);
    
    // Sound emergency alarm
    for (int i = 0; i < 10; i++) {
        digitalWrite(BUZZER_PIN, HIGH);
        delay(500);
        digitalWrite(BUZZER_PIN, LOW);
        delay(500);
    }
    
    // Send emergency alert
    DynamicJsonDocument doc(512);
    doc["alert"] = "EMERGENCY_SHUTDOWN";
    doc["reason"] = deviceState.smoke_detected ? "SMOKE_DETECTED" : "GAS_DETECTED";
    doc["timestamp"] = timeClient.getEpochTime();
    
    String alert_message;
    serializeJson(doc, alert_message);
    mqttClient.publish("smarthome/emergency", alert_message.c_str());
    webSocket.broadcastTXT(alert_message);
}

void send_sensor_data() {
    DynamicJsonDocument doc(2048);
    
    // Device states
    doc["device_id"] = device_id;
    doc["timestamp"] = timeClient.getEpochTime();
    doc["temperature"] = deviceState.temperature;
    doc["humidity"] = deviceState.humidity;
    doc["power_consumption"] = deviceState.power_consumption;
    doc["security_armed"] = deviceState.security_armed;
    doc["auto_mode"] = deviceState.auto_mode;
    doc["last_command"] = deviceState.last_command;
    
    // Light states
    JsonArray lights = doc.createNestedArray("lights");
    for (int i = 0; i < 5; i++) {
        lights.add(deviceState.lights[i]);
    }
    
    // Fan states
    JsonArray fans = doc.createNestedArray("fans");
    for (int i = 0; i < 4; i++) {
        fans.add(deviceState.fans[i]);
    }
    
    // Door states
    JsonArray doors = doc.createNestedArray("doors");
    for (int i = 0; i < 4; i++) {
        doors.add(deviceState.doors[i]);
    }
    
    // Motion detection
    JsonArray motion = doc.createNestedArray("motion_detected");
    for (int i = 0; i < 4; i++) {
        motion.add(deviceState.motion_detected[i]);
    }
    
    // Safety alerts
    doc["smoke_detected"] = deviceState.smoke_detected;
    doc["gas_detected"] = deviceState.gas_detected;
    
    String sensor_data;
    serializeJson(doc, sensor_data);
    
    // Send via MQTT
    mqttClient.publish("smarthome/status", sensor_data.c_str());
    
    // Broadcast to WebSocket clients
    webSocket.broadcastTXT(sensor_data);
}

String get_device_status() {
    DynamicJsonDocument doc(2048);
    
    doc["device_id"] = device_id;
    doc["timestamp"] = timeClient.getEpochTime();
    doc["uptime"] = millis();
    doc["wifi_connected"] = WiFi.isConnected();
    doc["mqtt_connected"] = mqttClient.connected();
    doc["ip_address"] = WiFi.localIP().toString();
    
    // Current sensor readings
    doc["temperature"] = deviceState.temperature;
    doc["humidity"] = deviceState.humidity;
    doc["power_consumption"] = deviceState.power_consumption;
    
    // System states
    doc["security_armed"] = deviceState.security_armed;
    doc["auto_mode"] = deviceState.auto_mode;
    doc["last_command"] = deviceState.last_command;
    
    // Device states
    JsonArray lights = doc.createNestedArray("lights");
    for (int i = 0; i < 5; i++) lights.add(deviceState.lights[i]);
    
    JsonArray fans = doc.createNestedArray("fans");
    for (int i = 0; i < 4; i++) fans.add(deviceState.fans[i]);
    
    JsonArray doors = doc.createNestedArray("doors");
    for (int i = 0; i < 4; i++) doors.add(deviceState.doors[i]);
    
    JsonArray motion = doc.createNestedArray("motion_detected");
    for (int i = 0; i < 4; i++) motion.add(deviceState.motion_detected[i]);
    
    // Safety status
    doc["smoke_detected"] = deviceState.smoke_detected;
    doc["gas_detected"] = deviceState.gas_detected;
    
    // Energy data
    doc["voltage"] = energyData.voltage;
    doc["current"] = energyData.current;
    doc["daily_consumption"] = energyData.daily_consumption;
    
    String status;
    serializeJson(doc, status);
    return status;
}