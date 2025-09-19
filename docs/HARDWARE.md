# Smart Home Hardware Setup Guide

This guide provides detailed instructions for setting up the hardware components of your smart home automation system.

## Hardware Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Smart Home Hardware                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Central   │    │   Sensors   │    │  Actuators  │     │
│  │ Controller  │◄──►│  Network    │◄──►│  Network    │     │
│  │   (ESP32)   │    │             │    │             │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Power     │    │   Security  │    │   Camera    │     │
│  │   System    │    │   Devices   │    │   System    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Required Components

### Core Components

#### 1. Microcontroller - ESP32
**Recommended Model**: ESP32-DevKitC V4 or ESP32-WROOM-32

**Specifications:**
- **CPU**: Dual-core Tensilica LX6 @ 240MHz
- **Memory**: 520KB SRAM, 4MB Flash
- **WiFi**: 802.11 b/g/n
- **Bluetooth**: Classic + BLE
- **GPIO**: 34 programmable pins
- **ADC**: 18 channels, 12-bit
- **Power**: 3.3V operating, 5V input via USB

**Why ESP32?**
- Built-in WiFi and Bluetooth
- Sufficient GPIO pins for multiple sensors
- Over-the-air (OTA) update capability
- Low power consumption
- Strong community support

#### 2. Power Supply System

**Main Power Supply**: 5V 10A DC adapter
**Backup Power**: 12V UPS system (optional)
**Voltage Regulators**:
- 3.3V regulator for ESP32 and sensors
- 5V rail for relays and actuators

**Power Distribution:**
```
AC 220V/110V ──► DC 5V 10A ──┬── ESP32 (3.3V)
                              ├── Sensors (3.3V/5V)
                              ├── Relays (5V)
                              ├── Cameras (5V/12V)
                              └── Backup UPS (12V)
```

### Sensors Network

#### 1. Environmental Sensors

**DHT22 Temperature & Humidity Sensor**
- **Range**: -40°C to 80°C, 0-100% RH
- **Accuracy**: ±0.5°C, ±2-5% RH
- **Interface**: Digital (one-wire)
- **Connections**:
  - VCC → 3.3V
  - Data → GPIO2
  - GND → GND

**BMP280 Barometric Pressure Sensor**
- **Range**: 300-1100 hPa
- **Interface**: I2C/SPI
- **Connections**:
  - VCC → 3.3V
  - SDA → GPIO21
  - SCL → GPIO22
  - GND → GND

#### 2. Motion & Presence Sensors

**PIR Motion Sensor (HC-SR501)**
- **Detection Range**: 3-7 meters
- **Detection Angle**: 120 degrees
- **Delay Time**: 5-300 seconds (adjustable)
- **Connections**:
  - VCC → 5V
  - OUT → GPIO4
  - GND → GND

**Ultrasonic Distance Sensor (HC-SR04)**
- **Range**: 2cm - 4m
- **Accuracy**: 3mm
- **Connections**:
  - VCC → 5V
  - Trig → GPIO5
  - Echo → GPIO18
  - GND → GND

#### 3. Light & Environmental Monitoring

**Light Dependent Resistor (LDR)**
- **Resistance Range**: 200Ω - 10MΩ
- **Circuit**: Voltage divider with 10kΩ resistor
- **Connections**:
  - One end → 3.3V
  - Other end → GPIO32 & 10kΩ resistor
  - 10kΩ resistor → GND

**Air Quality Sensor (MQ-135)**
- **Detection**: CO2, NH3, NOx, alcohol, smoke
- **Interface**: Analog
- **Connections**:
  - VCC → 5V
  - A0 → GPIO33
  - GND → GND

#### 4. Safety Sensors

**Gas Sensor (MQ-2)**
- **Detection**: LPG, methane, hydrogen, smoke
- **Response Time**: <10 seconds
- **Connections**:
  - VCC → 5V
  - A0 → GPIO34
  - DO → GPIO35 (digital threshold)
  - GND → GND

**Smoke Detector (MQ-7)**
- **Detection**: Carbon monoxide
- **Sensitivity**: 20-2000ppm
- **Connections**:
  - VCC → 5V
  - A0 → GPIO36
  - GND → GND

### Actuators Network

#### 1. Relay Module (4-Channel)

**Specifications:**
- **Control Voltage**: 5V
- **Load Capacity**: 10A 250VAC, 10A 30VDC
- **Isolation**: Optocoupler
- **LED Indicators**: Per channel

**Connections:**
```
Relay Module:
├── VCC → 5V
├── GND → GND
├── IN1 → GPIO19 (Living Room Light)
├── IN2 → GPIO21 (Bedroom Light)
├── IN3 → GPIO22 (Fan Control)
└── IN4 → GPIO23 (AC/Heater Control)

Load Connections:
├── Channel 1: Living Room Lights
├── Channel 2: Bedroom Lights
├── Channel 3: Ceiling Fan
└── Channel 4: Air Conditioner
```

#### 2. Servo Motors

**Standard Servo (SG90)**
- **Torque**: 2.5kg/cm
- **Speed**: 0.1sec/60°
- **Operating Voltage**: 4.8-6V
- **Applications**: Curtain control, damper control

**Connections:**
```
Servo 1 (Curtains):
├── Red → 5V
├── Brown → GND
└── Orange → GPIO25

Servo 2 (Vent Control):
├── Red → 5V
├── Brown → GND
└── Orange → GPIO26
```

#### 3. Stepper Motor (Optional)

**NEMA 17 Stepper Motor**
- **Steps**: 200 steps/revolution
- **Torque**: 59Ncm
- **Driver**: A4988 or DRV8825
- **Applications**: Door lock, window control

### Security Hardware

#### 1. Camera System

**USB Cameras**
- **Resolution**: 1080p minimum
- **Frame Rate**: 30fps
- **Interface**: USB 2.0/3.0
- **Mounting**: Adjustable brackets

**IP Cameras**
- **Resolution**: 2MP/4MP
- **Protocol**: RTSP/HTTP
- **Power**: PoE or 12V DC
- **Features**: Night vision, motion detection

**Camera Placement:**
```
Security Zones:
├── Front Door: 1x IP Camera (1080p)
├── Back Door: 1x IP Camera (1080p)
├── Living Room: 1x USB Camera (720p)
├── Driveway: 1x IP Camera (4MP)
└── Perimeter: 2x IP Cameras (2MP)
```

#### 2. Biometric Access Control

**Fingerprint Scanner (R307)**
- **Sensor**: Optical
- **Resolution**: 508dpi
- **Storage**: 1000 fingerprints
- **Interface**: UART
- **Connections**:
  - VCC → 3.3V
  - TX → GPIO16
  - RX → GPIO17
  - GND → GND

**RFID Reader (RC522)**
- **Frequency**: 13.56MHz
- **Protocol**: ISO14443A
- **Range**: 0-60mm
- **Interface**: SPI
- **Connections**:
  - VCC → 3.3V
  - RST → GPIO27
  - GND → GND
  - MISO → GPIO19
  - MOSI → GPIO23
  - SCK → GPIO18
  - SDA → GPIO5

#### 3. Door/Window Sensors

**Magnetic Reed Switches**
- **Type**: Normally open (NO)
- **Contact Rating**: 10W
- **Gap Sensitivity**: 10-20mm
- **Installation**: Door/window frames

**Connections per sensor:**
```
Door Sensor 1 (Front Door):
├── Common → GPIO12
└── NO → GND

Window Sensor 1 (Living Room):
├── Common → GPIO13
└── NO → GND
```

### Audio/Visual Components

#### 1. Sound System

**Speaker/Buzzer**
- **Type**: Piezo buzzer + small speaker
- **Power**: 5V, 500mW
- **Applications**: Alerts, voice feedback

**Connections:**
```
Buzzer:
├── + → GPIO14
└── - → GND

Speaker (via amplifier):
├── Audio In → DAC pin
├── VCC → 5V
└── GND → GND
```

#### 2. Display (Optional)

**16x2 LCD Display (HD44780)**
- **Interface**: I2C (via PCF8574)
- **Backlight**: LED
- **Applications**: Status display, settings

**Connections:**
```
I2C LCD:
├── VCC → 5V
├── GND → GND
├── SDA → GPIO21
└── SCL → GPIO22
```

## Circuit Diagrams

### Main Controller Circuit

```
                    ESP32-DevKitC
                   ┌─────────────┐
    3V3 ┌──────────┤3V3       D23├──────────┐
    EN  │          ├EN        D22├────┐     │
    SVP │      ┌───┤SVP       D21├──┐ │     │
    SVN │      │   ├SVN       D19├┐ │ │     │
    D34 │      │   ├D34       D18├┘ │ │     │
    D35 │      │   ├D35        D5├──┘ │     │
    D32 │      │   ├D32       D17├────┘     │
    D33 │      │   ├D33       D16├──────────┘
    D25 │      │   ├D25        D4├───────── PIR Sensor
    D26 │      │   ├D26        D0├───────── Boot Button
    D27 │      │   ├D27        D2├───────── DHT22
    D14 │      │   ├D14       D15├───────── 
    D12 │      │   ├D12       SD1├───────── 
    GND ├──────┘   ├GND       SD0├───────── 
    D13 │          ├D13       SD2├───────── 
    SD2 │          ├SD2       SD3├───────── 
    SD3 │          ├SD3       CMD├───────── 
    CMD │          ├CMD      5V  ├──────────┐
                   └─────────────┘          │
                                           5V
```

### Power Distribution Circuit

```
AC Input ──► Transformer ──► Rectifier ──► Filter ──► Regulator
220V/110V     24V AC         24V DC        24V DC     5V DC
     │
     └──► UPS System ──► 12V DC ──► Buck Converter ──► 5V DC
          (Battery           │
           Backup)           └──► 3.3V Regulator ──► 3.3V DC
```

### Sensor Network Schematic

```
                        ESP32 GPIO Assignments
┌──────────────────────────────────────────────────────────┐
│ GPIO2  ── DHT22 (Temperature/Humidity)                   │
│ GPIO4  ── PIR Sensor (Motion Detection)                  │
│ GPIO5  ── RFID SDA                                       │
│ GPIO12 ── Door Sensor 1                                  │
│ GPIO13 ── Window Sensor 1                                │
│ GPIO14 ── Buzzer                                         │
│ GPIO16 ── Fingerprint Scanner TX                         │
│ GPIO17 ── Fingerprint Scanner RX                         │
│ GPIO18 ── Ultrasonic Echo                                │
│ GPIO19 ── Relay 1 (Living Room Light)                    │
│ GPIO21 ── I2C SDA (LCD, BMP280)                         │
│ GPIO22 ── I2C SCL (LCD, BMP280)                         │
│ GPIO23 ── Relay 4 (AC Control)                          │
│ GPIO25 ── Servo 1 (Curtain Control)                     │
│ GPIO26 ── Servo 2 (Vent Control)                        │
│ GPIO27 ── RFID Reset                                     │
│ GPIO32 ── LDR (Light Sensor)                            │
│ GPIO33 ── MQ-135 (Air Quality)                          │
│ GPIO34 ── MQ-2 (Gas Sensor)                             │
│ GPIO35 ── MQ-2 Digital Out                              │
│ GPIO36 ── MQ-7 (CO Sensor)                              │
└──────────────────────────────────────────────────────────┘
```

## Assembly Instructions

### Step 1: Prepare the Enclosure

**Recommended Enclosure:**
- **Type**: IP65 rated plastic enclosure
- **Size**: 300mm x 200mm x 120mm
- **Features**: Removable mounting plate, cable glands

**Preparation:**
1. Drill holes for cable glands
2. Mount DIN rail for component mounting
3. Install ventilation if needed
4. Apply anti-static measures

### Step 2: Mount Core Components

**Component Layout:**
```
Enclosure Layout (Top View):
┌─────────────────────────────────────┐
│  Power Supply    │    ESP32         │
│  (5V 10A)        │    Development   │
│                  │    Board         │
├─────────────────────────────────────┤
│  Relay Module    │    Voltage       │
│  (4-Channel)     │    Regulators    │
│                  │    (3.3V)        │
├─────────────────────────────────────┤
│  Terminal Blocks │    Fuse Panel    │
│  (Sensors)       │    (Protection)  │
└─────────────────────────────────────┘
```

**Mounting Steps:**
1. Install power supply on DIN rail
2. Mount ESP32 on standoffs
3. Install relay module with heat sink
4. Add voltage regulators with proper cooling
5. Install terminal blocks for connections
6. Add fuses for circuit protection

### Step 3: Wiring

**Safety First:**
- Turn off all power before wiring
- Use proper gauge wire for current requirements
- Install fuses and circuit breakers
- Follow local electrical codes

**Wire Gauge Requirements:**
- **Power Lines (AC)**: 14 AWG minimum
- **DC Power (5V)**: 18 AWG
- **Signal Lines**: 22-24 AWG
- **Ground Lines**: 18 AWG minimum

**Wiring Steps:**
1. **AC Power Wiring** (by qualified electrician):
   ```
   AC Input ──► Circuit Breaker ──► Power Supply
               (20A)               (5V 10A)
   ```

2. **DC Power Distribution**:
   ```
   5V Supply ──┬── ESP32 (via 3.3V regulator)
               ├── Relay Module
               ├── Sensors (5V)
               └── Cameras/Actuators
   ```

3. **Signal Wiring**:
   ```
   ESP32 GPIO ──► Sensor/Actuator
   (with appropriate pull-up/pull-down resistors)
   ```

4. **Ground System**:
   ```
   All grounds connected to common ground bus
   Ground bus connected to ESP32 GND and Power Supply GND
   ```

### Step 4: Sensor Installation

#### Environmental Sensors
1. **DHT22 Placement**:
   - Install in ventilated area away from heat sources
   - Protect from direct sunlight and moisture
   - Use 10kΩ pull-up resistor on data line

2. **Air Quality Sensors**:
   - Install in representative locations
   - Allow 24-48 hour warm-up period
   - Calibrate according to manufacturer specs

#### Motion Sensors
1. **PIR Sensor Placement**:
   - Mount 2-3 meters high
   - Avoid heat sources and air currents
   - Adjust sensitivity and delay settings
   - Cover angle: avoid pets if needed

#### Security Sensors
1. **Door/Window Sensors**:
   - Mount magnet on moving part
   - Mount switch on frame
   - Maintain 10-20mm gap when closed
   - Use shielded cable for long runs

### Step 5: Camera Installation

#### Camera Mounting
1. **Indoor Cameras**:
   - Mount high to avoid tampering
   - Ensure power and network access
   - Provide adequate lighting
   - Consider privacy zones

2. **Outdoor Cameras**:
   - Use weatherproof enclosures
   - Install surge protection
   - Use PoE for power and data
   - Ensure proper drainage

#### Network Configuration
```
Camera Network Topology:
Internet ──► Router ──┬── PoE Switch ──► IP Cameras
                      ├── WiFi AP ──► ESP32 Controller
                      └── Computer ──► Control System
```

## Testing Procedures

### Initial Power-On Tests

1. **Power Supply Test**:
   ```bash
   # Measure voltages with multimeter
   5V Rail: 4.9V - 5.1V ✓
   3.3V Rail: 3.2V - 3.4V ✓
   Ground: 0V ✓
   ```

2. **ESP32 Connectivity**:
   ```cpp
   // Upload basic test sketch
   void setup() {
     Serial.begin(115200);
     WiFi.begin("SSID", "password");
   }
   
   void loop() {
     Serial.println("ESP32 Running");
     delay(1000);
   }
   ```

### Sensor Testing

1. **Environmental Sensors**:
   ```python
   # Test script for sensor verification
   python scripts/test_sensors.py
   
   Expected Output:
   DHT22: Temperature: 22.5°C, Humidity: 45% ✓
   BMP280: Pressure: 1013.25 hPa ✓
   LDR: Light Level: 512 (0-1023) ✓
   ```

2. **Motion Detection Test**:
   ```bash
   # Monitor PIR sensor output
   mosquitto_sub -h localhost -t smarthome/sensors/motion
   
   # Walk in front of sensor
   Expected: {"motion": true, "timestamp": "..."}
   ```

### Actuator Testing

1. **Relay Testing**:
   ```python
   # Test each relay channel
   python scripts/test_relays.py
   
   # Should hear relay clicking and see LED indicators
   Relay 1: ON/OFF ✓
   Relay 2: ON/OFF ✓
   Relay 3: ON/OFF ✓
   Relay 4: ON/OFF ✓
   ```

2. **Servo Motor Test**:
   ```python
   # Test servo movement
   python scripts/test_servos.py
   
   # Should see smooth movement between positions
   Servo 1: 0° → 90° → 180° ✓
   Servo 2: 0° → 90° → 180° ✓
   ```

### Security System Testing

1. **Camera Test**:
   ```bash
   # Test each camera
   python scripts/test_cameras.py
   
   # Should capture test images
   Camera 1: Image captured ✓
   Camera 2: Image captured ✓
   Motion Detection: Active ✓
   ```

2. **Access Control Test**:
   ```python
   # Test fingerprint scanner
   python scripts/test_fingerprint.py
   
   # Test RFID reader
   python scripts/test_rfid.py
   ```

## Maintenance Procedures

### Daily Checks
- [ ] System status indicators
- [ ] Camera functionality
- [ ] Motion sensor response
- [ ] Network connectivity

### Weekly Maintenance
- [ ] Clean camera lenses
- [ ] Check sensor calibration
- [ ] Verify backup power system
- [ ] Review system logs

### Monthly Maintenance
- [ ] Dust removal from enclosures
- [ ] Check electrical connections
- [ ] Update firmware if available
- [ ] Test emergency procedures

### Annual Maintenance
- [ ] Replace backup batteries
- [ ] Recalibrate all sensors
- [ ] Inspect and tighten all connections
- [ ] Update system documentation

## Troubleshooting Hardware Issues

### Power Issues

**Problem**: System not powering on
**Checks**:
1. Verify AC input voltage
2. Check fuse continuity
3. Measure DC output voltages
4. Inspect for loose connections

**Problem**: Intermittent power loss
**Checks**:
1. Check for overloading
2. Verify proper heat dissipation
3. Inspect power supply capacity
4. Check for voltage drops

### Sensor Issues

**Problem**: Sensor readings inaccurate
**Solutions**:
1. Recalibrate sensors
2. Check wiring connections
3. Verify power supply stability
4. Replace sensor if faulty

**Problem**: Motion sensor false triggers
**Solutions**:
1. Adjust sensitivity settings
2. Check for heat sources
3. Verify mounting stability
4. Shield from air currents

### Communication Issues

**Problem**: ESP32 not connecting to WiFi
**Solutions**:
1. Check WiFi credentials
2. Verify signal strength
3. Use 2.4GHz network
4. Reset network settings

**Problem**: MQTT messages not received
**Solutions**:
1. Check MQTT broker status
2. Verify topic subscriptions
3. Check firewall settings
4. Restart MQTT service

## Safety Considerations

### Electrical Safety
- All AC wiring by qualified electrician
- Proper grounding and bonding
- GFCI protection for wet areas
- Circuit breakers and fuses

### Fire Safety
- Heat detection and ventilation
- Proper wire gauge selection
- Component derating
- Emergency shutdown procedures

### Data Security
- Secure network configuration
- Regular security updates
- Access control implementation
- Data encryption

### Physical Security
- Tamper-evident enclosures
- Hidden cable routing
- Secure mounting hardware
- Backup communication paths

## Expansion Capabilities

### Additional Sensors
- Weather station integration
- Water leak detectors
- Vibration sensors
- Soil moisture sensors

### Enhanced Actuators
- Smart switches and dimmers
- Motorized blinds/curtains
- HVAC integration
- Pool/spa controls

### Advanced Security
- Facial recognition cameras
- Thermal imaging
- Perimeter detection
- Drone integration

### Energy Management
- Smart meter integration
- Solar panel monitoring
- Battery storage systems
- Load balancing controls

## Conclusion

This hardware setup provides a robust foundation for your smart home automation system. The modular design allows for easy expansion and maintenance while ensuring reliable operation.

### Key Benefits
- **Scalability**: Easy to add new devices
- **Reliability**: Redundant systems and backup power
- **Security**: Multiple layers of protection
- **Efficiency**: Optimized power consumption
- **Maintainability**: Accessible components and clear documentation

### Next Steps
1. Complete hardware assembly and testing
2. Install and configure software components
3. Perform system integration testing
4. Train users on operation and maintenance
5. Establish monitoring and support procedures

For additional support or custom hardware configurations, please refer to our community forums or contact professional installation services.