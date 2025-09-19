# 🏠 Advanced Smart Home Automation System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 16+](https://img.shields.io/badge/node-16+-green.svg)](https://nodejs.org/)
[![Flutter 3.0+](https://img.shields.io/badge/flutter-3.0+-blue.svg)](https://flutter.dev/)

A comprehensive, modern smart home automation system with voice control, mobile app, web dashboard, advanced security features, CCTV surveillance, and AI-powered energy management.

## 🌟 Features

### 🎙️ Voice Control
- Multi-language voice commands (English, Spanish, French, German, Hindi)
- Natural Language Processing with AI integration
- Offline voice recognition support
- Custom voice commands and macros

### 📱 Mobile Application
- Cross-platform Flutter app (iOS & Android)
- Real-time device control and monitoring
- Security system management
- Voice command integration
- Push notifications for alerts
- Data analytics and energy reports

### 🖥️ Web Dashboard
- Responsive React-based web interface
- Real-time device status and control
- Advanced analytics and charts
- Security camera live feeds
- Energy consumption monitoring
- System configuration and settings

### 🔐 Advanced Security
- **Biometric Authentication**: Fingerprint scanner integration
- **Face Recognition**: OpenCV-powered face detection and recognition
- **24/7 CCTV Surveillance**: Multi-camera support with motion detection
- **Real-time Alerts**: Email, SMS, and push notifications
- **Access Control**: Time-based and role-based access management

### 📹 CCTV System
- Multiple camera support (IP cameras, USB cameras)
- Motion detection and object tracking
- Automated recording with event triggers
- Live streaming to web and mobile
- Cloud storage integration
- Night vision support

### ⚡ Energy Management
- **AI-Powered Optimization**: Machine learning for energy predictions
- **Automated Control**: Smart scheduling based on occupancy
- **Real-time Monitoring**: Track consumption by device and room
- **Cost Analysis**: Detailed energy cost reports
- **Peak Load Management**: Automatic load balancing

### 🏠 Home Automation
- **Smart Lighting**: Automated on/off based on occupancy and time
- **Climate Control**: Smart thermostat and fan control
- **Appliance Control**: Remote control of all connected devices
- **Scene Management**: Pre-configured scenes for different activities
- **Scheduling**: Time-based automation rules

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Smart Home System                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Mobile    │  │     Web     │  │    Voice    │         │
│  │     App     │  │  Dashboard  │  │  Assistant  │         │
│  │  (Flutter)  │  │   (React)   │  │  (Python)   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Backend API Server (Node.js)              │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │ │
│  │  │   API   │ │  MQTT   │ │Database │ │   AI    │      │ │
│  │  │Gateway  │ │ Broker  │ │ (Mongo) │ │ Engine  │      │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Security   │  │    CCTV     │  │   Energy    │         │
│  │   System    │  │ Surveillance│  │ Management  │         │
│  │  (Python)   │  │  (Python)   │  │  (Python)   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                           │                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           Hardware Layer (ESP32/Arduino)               │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │ │
│  │  │Sensors  │ │ Relays  │ │Cameras  │ │Actuators│      │ │
│  │  │ (DHT,   │ │(Lights, │ │ (USB,   │ │(Servos, │      │ │
│  │  │ PIR,    │ │ Fans,   │ │  IP)    │ │ Motors) │      │ │
│  │  │ etc.)   │ │ etc.)   │ │         │ │         │      │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
advanced-smart-home/
├── 📁 hardware/
│   ├── esp32_main_controller.ino       # ESP32 main controller code
│   ├── libraries/                      # Custom Arduino libraries
│   └── schematics/                     # Circuit diagrams
├── 📁 backend/
│   ├── src/
│   │   ├── server.js                   # Express.js server
│   │   ├── routes/                     # API routes
│   │   ├── models/                     # Database models
│   │   ├── middleware/                 # Custom middleware
│   │   └── utils/                      # Utility functions
│   ├── package.json                    # Node.js dependencies
│   └── config/                         # Configuration files
├── 📁 mobile-app/
│   ├── lib/
│   │   ├── main.dart                   # Flutter app entry point
│   │   ├── src/
│   │   │   ├── app.dart               # App configuration
│   │   │   ├── screens/               # UI screens
│   │   │   ├── widgets/               # Reusable widgets
│   │   │   ├── services/              # API services
│   │   │   └── models/                # Data models
│   │   └── pubspec.yaml               # Flutter dependencies
├── 📁 web-dashboard/
│   ├── src/
│   │   ├── index.js                   # React app entry point
│   │   ├── App.js                     # Main app component
│   │   ├── pages/                     # Page components
│   │   ├── components/                # Reusable components
│   │   ├── services/                  # API services
│   │   └── styles/                    # CSS styles
│   ├── package.json                   # React dependencies
│   └── public/                        # Static assets
├── 📁 voice-control/
│   ├── voice_assistant.py             # Main voice control system
│   ├── models/                        # Voice recognition models
│   ├── languages/                     # Multi-language support
│   └── commands/                      # Custom commands
├── 📁 security/
│   ├── security_system.py             # Security management
│   ├── cctv_system.py                 # CCTV surveillance
│   ├── face_recognition/              # Face recognition models
│   └── fingerprint/                   # Fingerprint scanner integration
├── 📁 energy-management/
│   ├── energy_system.py               # Energy management system
│   ├── ml_models/                     # Machine learning models
│   └── reports/                       # Energy reports
├── 📁 config/
│   ├── system_config.json             # System configuration
│   ├── devices.json                   # Device definitions
│   └── users.json                     # User management
├── 📁 docs/
│   ├── API.md                         # API documentation
│   ├── INSTALLATION.md                # Installation guide
│   ├── HARDWARE.md                    # Hardware setup guide
│   └── TROUBLESHOOTING.md             # Troubleshooting guide
├── 📁 scripts/
│   ├── setup.sh                       # System setup script
│   ├── install_dependencies.sh        # Dependency installation
│   └── deploy.sh                      # Deployment script
├── .env.example                       # Environment variables template
├── docker-compose.yml                 # Docker deployment
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## 🚀 Quick Start

### Prerequisites

- **Hardware**: ESP32/Arduino Uno, sensors, relays, cameras
- **Software**: Python 3.8+, Node.js 16+, Flutter 3.0+
- **Services**: MQTT broker, MongoDB, Redis (optional)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/advanced-smart-home.git
cd advanced-smart-home
```

### 2. Environment Setup

Copy the environment template and configure your settings:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Quick Installation (Automated)

Run the automated setup script:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 4. Manual Installation

#### Backend Setup

```bash
cd backend
npm install
npm run dev
```

#### Python Services Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start voice control system
cd voice-control
python voice_assistant.py

# Start security system
cd ../security
python security_system.py

# Start CCTV system
python cctv_system.py

# Start energy management
cd ../energy-management
python energy_system.py
```

#### Mobile App Setup

```bash
cd mobile-app
flutter pub get
flutter run
```

#### Web Dashboard Setup

```bash
cd web-dashboard
npm install
npm start
```

#### Hardware Setup

1. Flash the ESP32 with the provided Arduino code
2. Connect sensors and actuators according to the schematic
3. Configure WiFi credentials in the Arduino code
4. Upload the code to your ESP32

## 📋 Installation Guide

### Detailed Hardware Setup

#### Required Components

**Core Hardware:**
- ESP32 Development Board
- Breadboard and jumper wires
- Power supply (5V/3.3V)

**Sensors:**
- DHT22 (Temperature/Humidity)
- PIR Motion Sensor
- Light Dependent Resistor (LDR)
- Gas/Smoke Sensor (MQ-2)
- Sound Sensor
- Door/Window Magnetic Sensors

**Actuators:**
- Relay modules (4-channel recommended)
- Servo motors
- LED strips/bulbs
- Buzzer/Speaker

**Security Hardware:**
- USB/IP Cameras
- Fingerprint Scanner (e.g., Adafruit)
- RFID Reader (optional)

**Optional Components:**
- LCD Display (16x2)
- Keypad
- Temperature sensors (DS18B20)

#### Wiring Diagram

```
ESP32 Pin Configuration:
├── GPIO 2  → DHT22 Data
├── GPIO 4  → PIR Sensor
├── GPIO 5  → Relay 1 (Lights)
├── GPIO 18 → Relay 2 (Fan)
├── GPIO 19 → Relay 3 (AC)
├── GPIO 21 → Relay 4 (Heater)
├── GPIO 22 → Servo Motor
├── GPIO 23 → Buzzer
├── GPIO 32 → LDR Sensor
├── GPIO 33 → Gas Sensor
├── GPIO 34 → Sound Sensor
└── GPIO 35 → Door Sensor
```

### Software Dependencies

#### Python Dependencies

```bash
# Core dependencies
pip install opencv-python
pip install face-recognition
pip install speechrecognition
pip install pyttsx3
pip install paho-mqtt
pip install flask
pip install flask-socketio
pip install numpy
pip install pandas
pip install scikit-learn
pip install tensorflow

# Additional dependencies
pip install pyserial
pip install requests
pip install schedule
pip install python-dotenv
pip install sqlalchemy
pip install redis
pip install celery
```

#### Node.js Dependencies

```bash
# Backend dependencies
npm install express
npm install socket.io
npm install mongodb
npm install mongoose
npm install redis
npm install jsonwebtoken
npm install bcryptjs
npm install cors
npm install helmet
npm install morgan
npm install dotenv

# Development dependencies
npm install --save-dev nodemon
npm install --save-dev jest
npm install --save-dev supertest
```

#### Flutter Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2
  http: ^0.13.5
  provider: ^6.0.3
  shared_preferences: ^2.0.15
  mqtt_client: ^9.6.8
  camera: ^0.10.0
  local_auth: ^2.1.6
  speech_to_text: ^6.1.1
  flutter_tts: ^3.6.3
  charts_flutter: ^0.12.0
  firebase_messaging: ^14.0.4
```

## 🔧 Configuration

### System Configuration

Edit `config/system_config.json`:

```json
{
  "system": {
    "name": "Smart Home System",
    "version": "1.0.0",
    "timezone": "UTC",
    "language": "en"
  },
  "network": {
    "wifi_ssid": "YourWiFiNetwork",
    "wifi_password": "YourWiFiPassword",
    "mqtt_broker": "localhost",
    "mqtt_port": 1883
  },
  "security": {
    "face_recognition_enabled": true,
    "fingerprint_enabled": true,
    "motion_detection_enabled": true,
    "alert_email": "admin@smarthome.com"
  },
  "energy": {
    "optimization_enabled": true,
    "peak_hours": ["18:00", "22:00"],
    "auto_schedule_enabled": true
  }
}
```

### Device Configuration

Edit `config/devices.json`:

```json
{
  "rooms": {
    "living_room": {
      "lights": ["relay_1"],
      "fans": ["relay_2"],
      "sensors": ["pir_1", "temp_1"]
    },
    "bedroom": {
      "lights": ["relay_3"],
      "ac": ["relay_4"],
      "sensors": ["pir_2", "temp_2"]
    }
  },
  "devices": {
    "relay_1": {
      "name": "Living Room Light",
      "type": "light",
      "pin": 5,
      "power_rating": 60
    },
    "relay_2": {
      "name": "Living Room Fan",
      "type": "fan",
      "pin": 18,
      "power_rating": 75
    }
  }
}
```

## 🎛️ Usage

### Voice Commands

**Basic Controls:**
- "Turn on the living room lights"
- "Set bedroom temperature to 22 degrees"
- "Turn off all lights"
- "Lock the front door"

**Advanced Commands:**
- "Good morning routine" (turns on lights, coffee maker, etc.)
- "Security mode on" (activates all security features)
- "Energy saving mode" (optimizes power consumption)
- "Play relaxing music" (controls smart speakers)

**Multi-language Support:**
- English: "Turn on the lights"
- Spanish: "Enciende las luces"
- French: "Allume les lumières"
- German: "Schalte das Licht ein"
- Hindi: "लाइट चालू करो"

### Mobile App Features

**Dashboard:**
- Real-time device status
- Quick control buttons
- Energy consumption graphs
- Security alerts

**Rooms:**
- Room-by-room control
- Scene management
- Environmental monitoring
- Automation rules

**Security:**
- Live camera feeds
- Motion detection alerts
- Access logs
- Emergency controls

**Voice Control:**
- Push-to-talk functionality
- Voice command history
- Custom voice commands
- Multi-language support

### Web Dashboard

Access the web dashboard at `http://localhost:3000`

**Features:**
- Real-time device monitoring
- Advanced analytics
- System configuration
- User management
- Energy reports
- Security footage

## 🔒 Security Features

### Access Control

**Multi-factor Authentication:**
1. **Primary**: Face recognition or fingerprint
2. **Secondary**: PIN or password
3. **Backup**: Mobile app authentication

**User Roles:**
- **Admin**: Full system access
- **Family**: Limited device control
- **Guest**: Restricted access with time limits
- **Service**: Maintenance access only

### Privacy & Data Protection

**Local Processing:**
- Face recognition runs locally
- Voice commands processed on-device when possible
- No sensitive data sent to cloud without encryption

**Data Encryption:**
- All communications encrypted with TLS 1.3
- Local database encryption
- Secure key management

### Emergency Features

**Panic Mode:**
- Silent alarm activation
- Emergency contact notification
- Automatic door unlocking
- Light strobing for emergency identification

**System Intrusion Response:**
- Automatic security recording
- Multiple alert channels
- System lockdown capability
- Remote monitoring access

## ⚡ Energy Management

### AI-Powered Optimization

**Machine Learning Features:**
- **Usage Pattern Learning**: Analyzes family routines
- **Predictive Scheduling**: Optimizes device operation times
- **Load Balancing**: Prevents power overload
- **Cost Optimization**: Minimizes electricity bills

**Automated Controls:**
- **Occupancy-based Lighting**: Turns lights on/off automatically
- **Smart Thermostat**: Learns preferences and schedules
- **Standby Power Management**: Eliminates phantom loads
- **Peak Hour Avoidance**: Shifts usage to off-peak times

### Energy Analytics

**Real-time Monitoring:**
- Device-level power consumption
- Room-by-room usage tracking
- Historical consumption trends
- Cost analysis and projections

**Reports & Insights:**
- Daily/weekly/monthly energy reports
- Efficiency recommendations
- Carbon footprint tracking
- Savings opportunities identification

## 📊 API Documentation

### REST API Endpoints

#### Device Control

```http
GET /api/devices
POST /api/devices/{id}/control
GET /api/devices/{id}/status
PUT /api/devices/{id}/settings
```

#### Security

```http
GET /api/security/status
POST /api/security/arm
POST /api/security/disarm
GET /api/security/events
```

#### Energy

```http
GET /api/energy/consumption
GET /api/energy/reports
POST /api/energy/optimize
GET /api/energy/predictions
```

### WebSocket Events

**Device Updates:**
```javascript
socket.on('device_status_changed', (data) => {
  console.log('Device:', data.device_id, 'Status:', data.status);
});
```

**Security Alerts:**
```javascript
socket.on('security_alert', (data) => {
  console.log('Alert:', data.type, 'Location:', data.location);
});
```

**Energy Updates:**
```javascript
socket.on('energy_update', (data) => {
  console.log('Power Usage:', data.current_usage, 'W');
});
```

### MQTT Topics

**Device Control:**
```
smarthome/devices/{room}/{device}/command
smarthome/devices/{room}/{device}/status
```

**Security:**
```
smarthome/security/alerts
smarthome/security/cameras/{id}/motion
smarthome/security/access/door
```

**Energy:**
```
smarthome/energy/consumption
smarthome/energy/optimization
smarthome/energy/alerts
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Compose Configuration

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - MONGODB_URI=mongodb://mongo:27017/smarthome
    depends_on:
      - mongo
      - redis
  
  mongo:
    image: mongo:5.0
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  mqtt:
    image: eclipse-mosquitto:2.0
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./config/mosquitto.conf:/mosquitto/config/mosquitto.conf
```

## 🧪 Testing

### Unit Tests

```bash
# Backend tests
cd backend
npm test

# Python service tests
cd voice-control
python -m pytest tests/

# Flutter tests
cd mobile-app
flutter test
```

### Integration Tests

```bash
# Full system test
./scripts/run_tests.sh

# Hardware-in-the-loop testing
python scripts/hardware_test.py
```

### Performance Testing

```bash
# Load testing
cd backend
npm run test:load

# Energy efficiency testing
python scripts/energy_test.py
```

## 🔧 Troubleshooting

### Common Issues

#### ESP32 Connection Issues

**Problem**: ESP32 not connecting to WiFi
**Solution**:
1. Check WiFi credentials in code
2. Ensure ESP32 is in range of router
3. Try 2.4GHz network (ESP32 doesn't support 5GHz)
4. Reset ESP32 and reflash firmware

#### MQTT Connection Issues

**Problem**: Devices not receiving commands
**Solution**:
1. Check MQTT broker is running: `systemctl status mosquitto`
2. Verify MQTT credentials and permissions
3. Test connection: `mosquitto_pub -h localhost -t test -m "hello"`
4. Check firewall settings for port 1883

#### Camera/OpenCV Issues

**Problem**: Camera not detected or poor performance
**Solution**:
1. Install OpenCV with proper codec support
2. Check camera permissions and USB connections
3. Try different camera indices (0, 1, 2...)
4. For IP cameras, verify network connectivity and RTSP URLs

#### Face Recognition Issues

**Problem**: Slow or inaccurate face recognition
**Solution**:
1. Use `hog` model for CPU, `cnn` for GPU
2. Ensure good lighting conditions
3. Add more training images for better accuracy
4. Consider using smaller image resolution for speed

### Performance Optimization

#### System Performance

**Memory Usage:**
- Monitor with `htop` or task manager
- Reduce image resolution for processing
- Implement frame skipping for video analysis
- Use Redis for caching frequently accessed data

**CPU Usage:**
- Use threading for parallel processing
- Implement proper sleep delays in loops
- Optimize OpenCV operations
- Consider using GPU acceleration for ML tasks

#### Network Optimization

**Bandwidth Management:**
- Compress video streams
- Use adaptive quality based on network conditions
- Implement frame rate limiting
- Cache static content

**Latency Reduction:**
- Use local MQTT broker
- Implement WebSocket connections
- Optimize database queries
- Use CDN for web assets

### Log Analysis

**Check System Logs:**
```bash
# System logs
tail -f logs/system.log

# Security logs
tail -f logs/security.log

# Energy management logs
tail -f logs/energy.log

# CCTV logs
tail -f logs/cctv.log
```

**Log Levels:**
- `DEBUG`: Detailed development information
- `INFO`: General system information
- `WARNING`: Potential issues
- `ERROR`: Error conditions
- `CRITICAL`: Serious problems requiring immediate attention

## 🤝 Contributing

### Development Guidelines

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Write tests** for new functionality
4. **Follow coding standards**:
   - Python: PEP 8
   - JavaScript: ESLint configuration
   - Dart: Flutter style guide
5. **Update documentation**
6. **Submit a pull request**

### Code Style

**Python:**
```python
# Use type hints
def process_sensor_data(data: Dict[str, Any]) -> bool:
    """Process sensor data and return success status."""
    pass

# Use descriptive variable names
temperature_reading = sensor.get_temperature()
```

**JavaScript:**
```javascript
// Use const/let instead of var
const deviceConfig = require('./config/devices');

// Use async/await for promises
async function updateDeviceStatus(deviceId, status) {
  try {
    await api.updateDevice(deviceId, status);
  } catch (error) {
    console.error('Failed to update device:', error);
  }
}
```

### Adding New Features

**New Device Support:**
1. Add device definition to `config/devices.json`
2. Update ESP32 code for hardware control
3. Add API endpoints in backend
4. Update mobile app and web dashboard
5. Add voice commands
6. Write tests and documentation

**New Sensor Integration:**
1. Add sensor library to ESP32 code
2. Update data models in backend
3. Add real-time data streaming
4. Update UI components
5. Add automation rules
6. Test and document

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenCV** for computer vision capabilities
- **Face Recognition** library for facial recognition
- **SpeechRecognition** for voice processing
- **Flutter** team for mobile development framework
- **React** community for web development tools
- **Arduino** and **ESP32** communities for hardware support
- **MQTT** for IoT messaging protocol
- **TensorFlow** for machine learning capabilities

## 📞 Support

### Community Support

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Join our community discussions
- **Wiki**: Access detailed documentation and tutorials

### Professional Support

For commercial deployments and custom implementations:
- Email: support@smarthome-system.com
- Website: https://smarthome-system.com
- Documentation: https://docs.smarthome-system.com

### Quick Links

- [📖 Installation Guide](docs/INSTALLATION.md)
- [🔧 Hardware Setup](docs/HARDWARE.md)
- [🚨 Troubleshooting](docs/TROUBLESHOOTING.md)
- [📡 API Reference](docs/API.md)
- [🎯 Roadmap](ROADMAP.md)
- [📝 Changelog](CHANGELOG.md)

---

**Made with ❤️ for the smart home community**

*Transform your home into an intelligent, secure, and energy-efficient living space with cutting-edge technology and AI-powered automation.*