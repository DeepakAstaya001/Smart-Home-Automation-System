# Installation Guide

This comprehensive guide will walk you through setting up the Advanced Smart Home Automation System on your hardware and software environment.

## Prerequisites

### Hardware Requirements

#### Minimum Requirements
- **Microcontroller**: ESP32 or Arduino Uno with WiFi module
- **Computer**: Raspberry Pi 4 (4GB RAM) or equivalent
- **Network**: WiFi router with 2.4GHz support
- **Power**: 5V power supplies for components

#### Recommended Hardware
- **Microcontroller**: ESP32-DevKitC or ESP32-WROOM-32
- **Computer**: Raspberry Pi 4 (8GB RAM) or Ubuntu/Windows PC
- **Storage**: 32GB+ SD card or SSD
- **Network**: Dedicated IoT VLAN recommended

#### Sensors & Actuators
- **Temperature/Humidity**: DHT22 or SHT30
- **Motion Detection**: PIR sensor (HC-SR501)
- **Light Sensor**: LDR or BH1750
- **Gas Detection**: MQ-2 or MQ-135
- **Door/Window**: Magnetic reed switches
- **Relays**: 4-channel relay module (5V)
- **Cameras**: USB webcam or IP cameras
- **Fingerprint Scanner**: Adafruit fingerprint sensor
- **Display**: 16x2 LCD (optional)

### Software Requirements

#### Operating System
- **Raspberry Pi**: Raspberry Pi OS (64-bit recommended)
- **PC**: Ubuntu 20.04+, Windows 10+, or macOS 11+
- **Docker**: Docker and Docker Compose (recommended)

#### Development Tools
- **Arduino IDE**: Version 2.0+
- **Python**: Version 3.8+
- **Node.js**: Version 16+
- **Flutter**: Version 3.0+ (for mobile app)
- **Git**: For version control

## Installation Methods

### Method 1: Automated Installation (Recommended)

#### Quick Start Script

```bash
# Download and run the installation script
curl -fsSL https://raw.githubusercontent.com/yourusername/advanced-smart-home/main/scripts/install.sh | bash
```

#### What the Script Does
1. Installs system dependencies
2. Downloads the project
3. Sets up Python virtual environment
4. Installs Python packages
5. Sets up Node.js backend
6. Configures MQTT broker
7. Sets up database
8. Creates configuration files
9. Starts all services

### Method 2: Manual Installation

#### Step 1: System Update and Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nodejs npm git curl wget
sudo apt install -y mosquitto mosquitto-clients mongodb-server redis-server
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y espeak espeak-data libespeak1 libespeak-dev
sudo apt install -y portaudio19-dev python3-pyaudio
```

**CentOS/RHEL:**
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip nodejs npm git curl wget
sudo yum install -y mosquitto mongodb-server redis
sudo yum install -y opencv-devel python3-opencv
sudo yum install -y espeak espeak-devel
sudo yum install -y portaudio-devel
```

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 node mosquitto mongodb-community redis
brew install opencv espeak portaudio
brew install --cask arduino
```

**Windows:**
```powershell
# Install Chocolatey if not already installed
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies
choco install -y python3 nodejs git mosquitto mongodb redis
choco install -y arduino
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/advanced-smart-home.git
cd advanced-smart-home
```

#### Step 3: Python Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install additional dependencies for specific components
pip install opencv-python
pip install face-recognition
pip install speechrecognition
pip install pyttsx3
pip install paho-mqtt
pip install flask flask-socketio
pip install scikit-learn tensorflow
```

#### Step 4: Node.js Backend Setup

```bash
cd backend
npm install
npm install -g pm2  # Process manager
cd ..
```

#### Step 5: MQTT Broker Configuration

Create MQTT configuration file:
```bash
sudo mkdir -p /etc/mosquitto/conf.d
sudo tee /etc/mosquitto/conf.d/smarthome.conf << EOF
# Smart Home MQTT Configuration
port 1883
allow_anonymous true
max_connections 100

# Websocket support
listener 9001
protocol websockets

# Logging
log_type error
log_type warning
log_type notice
log_type information
connection_messages true
log_timestamp true

# Persistence
persistence true
persistence_location /var/lib/mosquitto/
EOF

# Restart mosquitto
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto
```

#### Step 6: Database Setup

**MongoDB:**
```bash
# Start MongoDB
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Create database and user
mongo --eval "
db = db.getSiblingDB('smarthome');
db.createUser({
  user: 'smarthome',
  pwd: 'your_password_here',
  roles: ['readWrite']
});
"
```

**Redis:**
```bash
# Start Redis
sudo systemctl start redis
sudo systemctl enable redis
```

#### Step 7: Configuration Files

Create environment configuration:
```bash
cp .env.example .env
```

Edit `.env` file:
```bash
# System Configuration
NODE_ENV=production
PORT=3000

# Database Configuration
MONGODB_URI=mongodb://smarthome:your_password_here@localhost:27017/smarthome
REDIS_URL=redis://localhost:6379

# MQTT Configuration
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# Security Configuration
JWT_SECRET=your-super-secret-jwt-key
API_KEY=your-api-key-here

# Email Configuration (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Voice Service Configuration
OPENAI_API_KEY=your-openai-key
GOOGLE_SPEECH_API_KEY=your-google-key

# Camera Configuration
RTSP_STREAMS=rtsp://camera1:554/stream,rtsp://camera2:554/stream
```

### Method 3: Docker Installation

#### Prerequisites
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo pip3 install docker-compose
```

#### Docker Deployment
```bash
# Clone repository
git clone https://github.com/yourusername/advanced-smart-home.git
cd advanced-smart-home

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

## Hardware Setup

### ESP32 Programming

#### Install Arduino IDE
1. Download Arduino IDE 2.0+ from https://www.arduino.cc/
2. Install ESP32 board support:
   - File → Preferences
   - Add URL: `https://dl.espressif.com/dl/package_esp32_index.json`
   - Tools → Board → Boards Manager → Search "ESP32" → Install

#### Required Libraries
```cpp
// Install these libraries through Arduino IDE Library Manager:
#include <WiFi.h>           // ESP32 WiFi
#include <WebServer.h>      // Web server
#include <ArduinoJson.h>    // JSON parsing
#include <PubSubClient.h>   // MQTT client
#include <DHT.h>           // DHT sensor
#include <ArduinoOTA.h>    // Over-the-air updates
#include <SPIFFS.h>        // File system
#include <ESPmDNS.h>       // mDNS support
```

#### Flash ESP32
1. Connect ESP32 to computer via USB
2. Open `hardware/esp32_main_controller.ino`
3. Configure WiFi credentials:
   ```cpp
   const char* ssid = "YourWiFiNetwork";
   const char* password = "YourWiFiPassword";
   ```
4. Select board: ESP32 Dev Module
5. Select correct COM port
6. Upload code

### Wiring Diagram

```
ESP32 Pinout:
┌─────────────────────────────────────┐
│  3V3  ┌─┐ GND   GPIO23 ┌─┐ GPIO22  │
│  EN   └─┘ GPIO36 GPIO1 └─┘ GPIO3   │
│  GPIO36  GPIO39 GPIO3  GPIO21      │
│  GPIO39  GPIO34 GPIO1  GPIO19      │
│  GPIO34  GPIO35 GPIO5  GPIO18      │
│  GPIO35  GPIO32 GPIO17 GPIO5       │
│  GPIO32  GPIO33 GPIO16 GPIO17      │
│  GPIO33  GPIO25 GPIO4  GPIO16      │
│  GPIO25  GPIO26 GPIO0  GPIO4       │
│  GPIO26  GPIO27 GPIO2  GPIO0       │
│  GPIO27  GPIO14 GPIO15 GPIO2       │
│  GPIO14  GPIO12 GPIO8  GPIO15      │
│  GPIO12  GND   GPIO7  GPIO8        │
│  GND     GPIO13 GPIO6  GPIO7       │
│  VIN     GPIO9  GPIO11 GPIO6       │
└─────────────────────────────────────┘

Connections:
├── DHT22 Sensor
│   ├── VCC → 3.3V
│   ├── Data → GPIO2
│   └── GND → GND
├── PIR Motion Sensor
│   ├── VCC → 5V
│   ├── Out → GPIO4
│   └── GND → GND
├── Relay Module (4-channel)
│   ├── VCC → 5V
│   ├── IN1 → GPIO5  (Light 1)
│   ├── IN2 → GPIO18 (Light 2)
│   ├── IN3 → GPIO19 (Fan)
│   ├── IN4 → GPIO21 (AC/Heater)
│   └── GND → GND
├── LDR Light Sensor
│   ├── VCC → 3.3V
│   ├── OUT → GPIO32
│   └── GND → GND
├── Gas Sensor (MQ-2)
│   ├── VCC → 5V
│   ├── A0 → GPIO33
│   └── GND → GND
├── Servo Motor
│   ├── VCC → 5V
│   ├── Signal → GPIO22
│   └── GND → GND
├── Buzzer/Speaker
│   ├── + → GPIO23
│   └── - → GND
└── LCD Display (16x2) [Optional]
    ├── VCC → 5V
    ├── SDA → GPIO21
    ├── SCL → GPIO22
    └── GND → GND
```

### Camera Setup

#### USB Cameras
```bash
# List available cameras
lsusb | grep -i camera
v4l2-ctl --list-devices

# Test camera
fswebcam -r 1280x720 --no-banner /tmp/test.jpg
```

#### IP Cameras
```bash
# Test RTSP stream
ffmpeg -i rtsp://camera_ip:554/stream -frames:v 1 test.jpg

# Common RTSP URLs:
# Hikvision: rtsp://username:password@ip:554/Streaming/Channels/101
# Dahua: rtsp://username:password@ip:554/cam/realmonitor?channel=1&subtype=0
# Generic: rtsp://ip:554/stream
```

## Service Configuration

### Start Services

#### Method 1: Manual Start
```bash
# Start backend
cd backend
npm start &

# Start voice control
cd voice-control
python voice_assistant.py &

# Start security system
cd security
python security_system.py &

# Start CCTV system
python cctv_system.py &

# Start energy management
cd energy-management
python energy_system.py &
```

#### Method 2: Using PM2 (Recommended)
```bash
# Install PM2
npm install -g pm2

# Start all services using ecosystem file
pm2 start ecosystem.config.js

# Check status
pm2 status

# View logs
pm2 logs

# Restart services
pm2 restart all

# Stop services
pm2 stop all
```

#### Method 3: Systemd Services
Create systemd service files:

```bash
# Backend service
sudo tee /etc/systemd/system/smarthome-backend.service << EOF
[Unit]
Description=Smart Home Backend Service
After=network.target mongodb.service redis.service mosquitto.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/advanced-smart-home/backend
ExecStart=/usr/bin/node src/server.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable smarthome-backend
sudo systemctl start smarthome-backend
```

### Mobile App Setup

#### Flutter Installation
```bash
# Install Flutter
git clone https://github.com/flutter/flutter.git -b stable
export PATH="$PATH:`pwd`/flutter/bin"

# Verify installation
flutter doctor

# Accept Android licenses (if building for Android)
flutter doctor --android-licenses
```

#### Build Mobile App
```bash
cd mobile-app

# Get dependencies
flutter pub get

# For Android
flutter build apk

# For iOS (macOS only)
flutter build ios

# Run in development
flutter run
```

### Web Dashboard Setup

```bash
cd web-dashboard

# Install dependencies
npm install

# Build for production
npm run build

# Serve with nginx
sudo cp -r build/* /var/www/html/smarthome/
```

## Testing Installation

### Hardware Testing

```bash
# Test ESP32 connectivity
python scripts/test_hardware.py

# Test sensors
python scripts/test_sensors.py

# Test actuators
python scripts/test_actuators.py
```

### Software Testing

```bash
# Test backend API
curl http://localhost:3000/api/v1/status

# Test MQTT
mosquitto_pub -h localhost -t test -m "Hello World"
mosquitto_sub -h localhost -t test

# Test database
python scripts/test_database.py

# Test voice recognition
python scripts/test_voice.py

# Test camera system
python scripts/test_cameras.py
```

### System Integration Test

```bash
# Run comprehensive test suite
./scripts/run_integration_tests.sh

# Performance test
python scripts/performance_test.py

# Load test
npm run test:load
```

## Troubleshooting

### Common Issues

#### ESP32 Upload Failed
```bash
# Try different upload speed
# In Arduino IDE: Tools → Upload Speed → 115200

# Check USB drivers
lsusb  # Should show CP210x or CH340

# Reset ESP32 during upload
# Hold BOOT button while clicking upload
```

#### WiFi Connection Issues
```cpp
// Add debug output to ESP32 code
WiFi.printDiag(Serial);

// Check signal strength
int rssi = WiFi.RSSI();
Serial.println("Signal strength: " + String(rssi) + " dBm");
```

#### Camera Not Detected
```bash
# Check camera permissions
sudo usermod -a -G video $USER

# Test camera access
python3 -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# Install camera drivers
sudo apt install v4l-utils

# List camera capabilities
v4l2-ctl --list-devices
v4l2-ctl --list-formats-ext
```

#### MQTT Connection Failed
```bash
# Check service status
sudo systemctl status mosquitto

# Test connection
mosquitto_pub -h localhost -p 1883 -t test -m "hello"

# Check logs
sudo journalctl -u mosquitto -f

# Restart service
sudo systemctl restart mosquitto
```

#### Database Connection Issues
```bash
# MongoDB
sudo systemctl status mongodb
mongo --eval "db.stats()"

# Redis
redis-cli ping
redis-cli info
```

### Performance Optimization

#### System Resources
```bash
# Monitor system usage
htop
sudo iotop
sudo nethogs

# Optimize for Raspberry Pi
# Add to /boot/config.txt:
gpu_mem=16
disable_camera_led=1
dtoverlay=disable-wifi
dtoverlay=disable-bt  # If not using Bluetooth
```

#### Memory Management
```python
# Reduce image resolution for processing
frame = cv2.resize(frame, (640, 480))

# Use frame skipping for video analysis
if frame_count % 3 == 0:  # Process every 3rd frame
    process_frame(frame)
```

#### Network Optimization
```bash
# QoS settings for router
# Prioritize smart home traffic
# Separate IoT devices on VLAN
```

### Log Analysis

```bash
# System logs
sudo journalctl -f

# Application logs
tail -f logs/system.log
tail -f logs/voice.log
tail -f logs/security.log
tail -f logs/energy.log

# MQTT logs
mosquitto_sub -h localhost -t smarthome/logs/+

# Database logs
sudo tail -f /var/log/mongodb/mongod.log
```

## Security Configuration

### SSL/TLS Setup

```bash
# Generate SSL certificates
sudo certbot --nginx -d yourdomain.com

# Configure MQTT with SSL
sudo tee /etc/mosquitto/conf.d/ssl.conf << EOF
listener 8883
cafile /etc/ssl/certs/ca-certificates.crt
certfile /etc/letsencrypt/live/yourdomain.com/cert.pem
keyfile /etc/letsencrypt/live/yourdomain.com/privkey.pem
require_certificate false
EOF
```

### Firewall Configuration

```bash
# Configure UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 3000/tcp  # Backend API
sudo ufw allow 1883/tcp  # MQTT
sudo ufw allow 8883/tcp  # MQTT SSL
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
```

### User Authentication

```bash
# Create MQTT users
sudo mosquitto_passwd -c /etc/mosquitto/passwd smarthome
sudo mosquitto_passwd /etc/mosquitto/passwd admin

# Update MQTT config
echo "password_file /etc/mosquitto/passwd" | sudo tee -a /etc/mosquitto/mosquitto.conf
echo "allow_anonymous false" | sudo tee -a /etc/mosquitto/mosquitto.conf
```

## Backup and Recovery

### Database Backup

```bash
# MongoDB backup
mongodump --db smarthome --out /backup/mongodb/

# Restore
mongorestore --db smarthome /backup/mongodb/smarthome/

# Redis backup
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb /backup/redis/
```

### Configuration Backup

```bash
# Backup configuration
tar -czf /backup/config-$(date +%Y%m%d).tar.gz \
  config/ \
  .env \
  ecosystem.config.js \
  /etc/mosquitto/conf.d/

# System backup script
./scripts/backup_system.sh
```

### Automated Backups

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /home/pi/advanced-smart-home/scripts/backup_system.sh

# Weekly configuration backup
0 3 * * 0 /home/pi/advanced-smart-home/scripts/backup_config.sh
```

## Next Steps

1. **Complete Configuration**: Review and customize all configuration files
2. **Add Devices**: Register your physical devices in the system
3. **Test Features**: Verify all components work correctly
4. **Mobile App**: Install and configure the mobile application
5. **Voice Training**: Train the voice recognition with your voice
6. **Security Setup**: Configure face recognition and fingerprint access
7. **Energy Optimization**: Set up energy management rules
8. **Automation Rules**: Create custom automation scenarios
9. **Monitoring**: Set up system monitoring and alerts
10. **Documentation**: Review the full documentation for advanced features

## Support

If you encounter issues during installation:

1. **Check Logs**: Review system and application logs
2. **GitHub Issues**: Search existing issues or create a new one
3. **Documentation**: Review the troubleshooting guide
4. **Community**: Join our Discord server for real-time help
5. **Professional Support**: Contact us for enterprise installation support

### Quick Commands Reference

```bash
# Check system status
./scripts/system_status.sh

# Restart all services
./scripts/restart_services.sh

# Update system
git pull && ./scripts/update_system.sh

# View real-time logs
./scripts/view_logs.sh

# Backup system
./scripts/backup_system.sh
```