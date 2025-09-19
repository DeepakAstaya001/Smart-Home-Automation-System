# Smart Home System Troubleshooting Guide

This guide provides comprehensive troubleshooting steps for common issues in the Advanced Smart Home Automation System.

## Quick Diagnostics

### System Health Check

Run the system diagnostic script:
```bash
./scripts/system_diagnostics.sh
```

Expected output:
```
✓ ESP32 Controller: Online
✓ MQTT Broker: Running
✓ Database: Connected  
✓ Voice Service: Active
✓ Security System: Armed
✓ Energy Management: Monitoring
✓ Web Dashboard: Accessible
✓ Mobile App API: Responsive
```

### Emergency Recovery

If system is completely unresponsive:
```bash
# Stop all services
sudo systemctl stop smarthome-*

# Restart core services
sudo systemctl start mongodb redis mosquitto

# Restart application services
./scripts/restart_all_services.sh

# Check logs
./scripts/check_system_logs.sh
```

## Hardware Issues

### ESP32 Controller Problems

#### Problem: ESP32 not responding
**Symptoms:**
- No WiFi connection
- No MQTT messages
- Device control not working

**Diagnosis:**
```bash
# Check if ESP32 is connected to network
ping 192.168.1.100  # Replace with your ESP32 IP

# Check MQTT messages
mosquitto_sub -h localhost -t smarthome/devices/+/status

# Check serial output (if connected via USB)
screen /dev/ttyUSB0 115200
```

**Solutions:**
1. **Power cycle ESP32**:
   - Disconnect power for 10 seconds
   - Reconnect and wait 30 seconds for boot

2. **WiFi connection issues**:
   ```cpp
   // Check WiFi credentials in ESP32 code
   const char* ssid = "YourNetwork";
   const char* password = "YourPassword";
   
   // Ensure using 2.4GHz network, not 5GHz
   ```

3. **Flash ESP32 with latest firmware**:
   ```bash
   # In Arduino IDE
   Tools → Board → ESP32 Dev Module
   Tools → Flash Size → 4MB
   Tools → Upload Speed → 115200
   ```

4. **Factory reset ESP32**:
   ```cpp
   // Add to setup() function
   if (digitalRead(BOOT_PIN) == LOW) {
     WiFi.disconnect(true);
     ESP.restart();
   }
   ```

#### Problem: Sensors giving incorrect readings
**Symptoms:**
- Temperature readings way off
- Motion sensor always triggered
- Light sensor not responding

**Diagnosis:**
```python
# Test individual sensors
python scripts/test_individual_sensors.py

# Check sensor connections
python scripts/check_sensor_connections.py
```

**Solutions:**
1. **DHT22 Temperature/Humidity**:
   ```cpp
   // Add pull-up resistor (10kΩ)
   // Check connections: VCC → 3.3V, Data → GPIO2, GND → GND
   
   // In code, add error checking:
   if (isnan(temperature) || isnan(humidity)) {
     Serial.println("DHT22 read error");
     return;
   }
   ```

2. **PIR Motion Sensor**:
   ```cpp
   // Adjust sensitivity potentiometer
   // Check delay time setting
   // Ensure 5V power supply
   
   // Add debouncing in code:
   unsigned long lastMotion = 0;
   if (digitalRead(PIR_PIN) && millis() - lastMotion > 2000) {
     // Motion detected
     lastMotion = millis();
   }
   ```

3. **LDR Light Sensor**:
   ```cpp
   // Check voltage divider circuit
   // LDR → 3.3V, other end → GPIO + 10kΩ resistor → GND
   
   // Calibrate in code:
   int lightLevel = analogRead(LDR_PIN);
   int percentage = map(lightLevel, 0, 4095, 0, 100);
   ```

#### Problem: Relays not switching
**Symptoms:**
- Lights not turning on/off
- Fans not responding
- No relay clicking sound

**Diagnosis:**
```python
# Test relay control
python scripts/test_relay_control.py

# Check relay power
# Measure voltage at relay inputs
```

**Solutions:**
1. **Check relay module power**:
   ```
   VCC: Should be 5V
   GND: Connected to ESP32 GND
   Control pins: 3.3V when active
   ```

2. **Verify relay wiring**:
   ```
   ESP32 GPIO19 → Relay IN1
   ESP32 GPIO21 → Relay IN2
   ESP32 GPIO22 → Relay IN3
   ESP32 GPIO23 → Relay IN4
   ```

3. **Test relay logic**:
   ```cpp
   // Some relays are active LOW
   digitalWrite(RELAY_PIN, LOW);  // Turn ON
   digitalWrite(RELAY_PIN, HIGH); // Turn OFF
   
   // Others are active HIGH
   digitalWrite(RELAY_PIN, HIGH); // Turn ON
   digitalWrite(RELAY_PIN, LOW);  // Turn OFF
   ```

### Camera System Issues

#### Problem: Cameras not detecting
**Symptoms:**
- "No camera found" errors
- Black video feeds
- Camera access denied

**Diagnosis:**
```bash
# List available cameras
lsusb | grep -i camera
v4l2-ctl --list-devices

# Test camera access
python3 -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# Check permissions
groups $USER | grep video
```

**Solutions:**
1. **Fix camera permissions**:
   ```bash
   sudo usermod -a -G video $USER
   sudo chmod 666 /dev/video*
   # Logout and login again
   ```

2. **Install camera drivers**:
   ```bash
   sudo apt update
   sudo apt install v4l-utils
   sudo apt install libv4l-dev
   ```

3. **Test different camera indices**:
   ```python
   import cv2
   
   # Try different camera indices
   for i in range(5):
       cap = cv2.VideoCapture(i)
       if cap.isOpened():
           print(f"Camera {i} is available")
           cap.release()
   ```

#### Problem: Poor video quality or lag
**Symptoms:**
- Blurry or pixelated video
- Delayed video feeds
- High CPU usage

**Solutions:**
1. **Optimize video settings**:
   ```python
   # Reduce resolution
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
   
   # Reduce frame rate
   cap.set(cv2.CAP_PROP_FPS, 15)
   
   # Adjust compression
   cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
   ```

2. **Implement frame skipping**:
   ```python
   frame_count = 0
   if frame_count % 3 == 0:  # Process every 3rd frame
       process_frame(frame)
   frame_count += 1
   ```

3. **Use threading for video processing**:
   ```python
   import threading
   
   def video_worker():
       while True:
           ret, frame = cap.read()
           if ret:
               # Process frame in separate thread
               threading.Thread(target=process_frame, args=(frame,)).start()
   ```

## Software Issues

### Backend Service Problems

#### Problem: Backend API not responding
**Symptoms:**
- HTTP 500/503 errors
- Connection refused
- Timeout errors

**Diagnosis:**
```bash
# Check if backend is running
ps aux | grep node
sudo netstat -tlnp | grep :3000

# Check backend logs
pm2 logs backend
# or
journalctl -u smarthome-backend -f

# Test API endpoint
curl http://localhost:3000/api/v1/status
```

**Solutions:**
1. **Restart backend service**:
   ```bash
   # Using PM2
   pm2 restart backend
   
   # Using systemd
   sudo systemctl restart smarthome-backend
   
   # Manual restart
   cd backend
   npm start
   ```

2. **Check database connections**:
   ```bash
   # MongoDB
   mongo --eval "db.stats()"
   
   # Redis
   redis-cli ping
   
   # Check connection strings in .env
   cat .env | grep -E "(MONGODB|REDIS)"
   ```

3. **Clear cache and rebuild**:
   ```bash
   cd backend
   rm -rf node_modules package-lock.json
   npm install
   npm start
   ```

#### Problem: MQTT broker issues
**Symptoms:**
- Devices not receiving commands
- No real-time updates
- MQTT connection errors

**Diagnosis:**
```bash
# Check mosquitto status
sudo systemctl status mosquitto

# Test MQTT functionality
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test

# Check MQTT logs
sudo journalctl -u mosquitto -f

# Test from ESP32 perspective
mosquitto_sub -h localhost -t smarthome/devices/+/+
```

**Solutions:**
1. **Restart MQTT broker**:
   ```bash
   sudo systemctl restart mosquitto
   sudo systemctl enable mosquitto
   ```

2. **Check MQTT configuration**:
   ```bash
   # Verify config file
   sudo nano /etc/mosquitto/mosquitto.conf
   
   # Basic working config:
   port 1883
   allow_anonymous true
   
   # Test configuration
   sudo mosquitto -v -c /etc/mosquitto/mosquitto.conf
   ```

3. **Check firewall settings**:
   ```bash
   sudo ufw status
   sudo ufw allow 1883/tcp
   sudo ufw allow 9001/tcp  # WebSocket
   ```

### Voice Control Issues

#### Problem: Voice recognition not working
**Symptoms:**
- "Could not understand audio" errors
- No response to voice commands
- Microphone not detected

**Diagnosis:**
```bash
# Check microphone
arecord -l
pactl list sources short

# Test microphone
arecord -d 5 test.wav
aplay test.wav

# Check voice service logs
tail -f logs/voice.log

# Test speech recognition
python scripts/test_speech_recognition.py
```

**Solutions:**
1. **Fix microphone permissions**:
   ```bash
   sudo usermod -a -G audio $USER
   
   # Check PulseAudio
   pulseaudio --check -v
   
   # Restart audio services
   sudo systemctl restart alsa-state
   ```

2. **Install audio dependencies**:
   ```bash
   sudo apt install portaudio19-dev python3-pyaudio
   sudo apt install espeak espeak-data libespeak1
   
   # Reinstall speech recognition
   pip uninstall SpeechRecognition
   pip install SpeechRecognition
   ```

3. **Configure audio settings**:
   ```python
   # In voice_assistant.py
   import pyaudio
   
   # List audio devices
   p = pyaudio.PyAudio()
   for i in range(p.get_device_count()):
       info = p.get_device_info_by_index(i)
       print(f"Device {i}: {info['name']}")
   
   # Use specific microphone
   recognizer.listen(source, microphone_index=1)
   ```

#### Problem: Text-to-speech not working
**Symptoms:**
- No audio output
- "espeak not found" errors
- Robotic or garbled speech

**Solutions:**
1. **Install TTS dependencies**:
   ```bash
   sudo apt install espeak espeak-data
   sudo apt install festival festvox-kallpc16k
   
   # Test espeak
   espeak "Hello, this is a test"
   ```

2. **Configure audio output**:
   ```bash
   # Check audio output devices
   aplay -l
   
   # Set default audio device
   sudo nano /etc/asound.conf
   
   # Add:
   defaults.pcm.card 1
   defaults.ctl.card 1
   ```

3. **Alternative TTS engines**:
   ```python
   # Try different TTS engines
   import pyttsx3
   
   engine = pyttsx3.init()
   voices = engine.getProperty('voices')
   for voice in voices:
       print(f"Voice: {voice.id}")
   
   # Set specific voice
   engine.setProperty('voice', voices[0].id)
   ```

### Security System Issues

#### Problem: Face recognition not accurate
**Symptoms:**
- Unknown faces not detected
- Known faces not recognized
- High false positive rate

**Diagnosis:**
```bash
# Check face recognition service
ps aux | grep face
tail -f logs/security.log

# Test face recognition manually
python scripts/test_face_recognition.py

# Check known faces database
ls data/known_faces/
```

**Solutions:**
1. **Improve lighting conditions**:
   ```python
   # Add lighting enhancement
   frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=30)
   
   # Use histogram equalization
   gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
   gray = cv2.equalizeHist(gray)
   ```

2. **Add more training images**:
   ```bash
   # Add multiple angles and lighting conditions
   mkdir -p data/known_faces/person_name/
   # Add 5-10 different photos per person
   ```

3. **Adjust recognition parameters**:
   ```python
   # In security_system.py
   face_locations = face_recognition.face_locations(
       rgb_frame, 
       model="cnn"  # Use CNN model for better accuracy (requires GPU)
   )
   
   # Adjust tolerance
   matches = face_recognition.compare_faces(
       known_encodings, 
       face_encoding, 
       tolerance=0.5  # Lower = more strict
   )
   ```

#### Problem: Motion detection false alarms
**Symptoms:**
- Too many motion alerts
- Motion detected when no movement
- Pets triggering alarms

**Solutions:**
1. **Adjust motion sensitivity**:
   ```python
   # In cctv_system.py
   # Increase minimum area for motion detection
   min_area = 1000  # Increase from 500
   
   # Add motion filtering
   if cv2.contourArea(contour) > min_area:
       # Additional checks
       x, y, w, h = cv2.boundingRect(contour)
       if w > 50 and h > 50:  # Minimum size
           return True
   ```

2. **Implement motion zones**:
   ```python
   # Define detection zones
   detection_zones = [
       {"name": "door", "coords": [(100, 100), (200, 300)]},
       {"name": "window", "coords": [(300, 150), (400, 250)]}
   ]
   
   # Check if motion is in zone
   def is_motion_in_zone(contour, zone):
       x, y, w, h = cv2.boundingRect(contour)
       center_x, center_y = x + w//2, y + h//2
       return cv2.pointPolygonTest(np.array(zone["coords"]), 
                                  (center_x, center_y), False) >= 0
   ```

3. **Time-based filtering**:
   ```python
   # Ignore motion during certain hours
   import datetime
   
   current_hour = datetime.datetime.now().hour
   if 23 <= current_hour or current_hour <= 6:  # Night hours
       # Reduce sensitivity or ignore small motions
       min_area *= 2
   ```

### Energy Management Issues

#### Problem: Inaccurate power consumption readings
**Symptoms:**
- Power readings don't match actual usage
- Negative power values
- Unrealistic consumption spikes

**Diagnosis:**
```bash
# Check energy management logs
tail -f logs/energy.log

# Test power measurement manually
python scripts/test_power_monitoring.py

# Compare with actual meter readings
```

**Solutions:**
1. **Calibrate power sensors**:
   ```python
   # In energy_system.py
   # Add calibration factors
   calibration_factors = {
       "living_room_light": 0.95,
       "bedroom_fan": 1.05,
       "ac_unit": 0.98
   }
   
   actual_power = raw_reading * calibration_factors[device_id]
   ```

2. **Implement power smoothing**:
   ```python
   # Moving average filter
   def smooth_power_reading(device_id, new_reading):
       if device_id not in power_history:
           power_history[device_id] = []
       
       power_history[device_id].append(new_reading)
       if len(power_history[device_id]) > 10:
           power_history[device_id].pop(0)
       
       return sum(power_history[device_id]) / len(power_history[device_id])
   ```

3. **Add validation checks**:
   ```python
   def validate_power_reading(device_id, reading):
       device_max_power = device_specs[device_id]["max_power"]
       
       if reading < 0 or reading > device_max_power * 1.2:
           logger.warning(f"Invalid power reading for {device_id}: {reading}")
           return False
       return True
   ```

## Network Issues

### WiFi Connectivity Problems

#### Problem: Devices randomly disconnecting
**Symptoms:**
- Intermittent device control
- Devices showing offline status
- WiFi signal drops

**Diagnosis:**
```bash
# Check WiFi signal strength
iwconfig wlan0

# Monitor connection stability
ping -i 1 192.168.1.1

# Check router logs
# (Access router admin interface)
```

**Solutions:**
1. **Improve WiFi coverage**:
   - Add WiFi extenders/repeaters
   - Position router centrally
   - Use 2.4GHz for IoT devices (better range)
   - Upgrade to WiFi 6 router

2. **Optimize ESP32 WiFi settings**:
   ```cpp
   // In ESP32 code
   WiFi.setAutoReconnect(true);
   WiFi.persistent(true);
   
   // Add connection monitoring
   void checkWiFiConnection() {
     if (WiFi.status() != WL_CONNECTED) {
       Serial.println("WiFi disconnected. Reconnecting...");
       WiFi.reconnect();
     }
   }
   
   // Call in loop()
   if (millis() - lastWiFiCheck > 30000) {
     checkWiFiConnection();
     lastWiFiCheck = millis();
   }
   ```

3. **Create dedicated IoT network**:
   ```
   Main Network: 192.168.1.0/24 (computers, phones)
   IoT Network: 192.168.10.0/24 (smart home devices)
   
   Configure VLAN separation for security
   ```

### Internet Connectivity Issues

#### Problem: Remote access not working
**Symptoms:**
- Can't access system from outside
- Mobile app can't connect remotely
- Webhook notifications failing

**Solutions:**
1. **Configure port forwarding**:
   ```
   Router Configuration:
   Port 3000 → 192.168.1.100:3000 (Backend API)
   Port 1883 → 192.168.1.100:1883 (MQTT)
   Port 8080 → 192.168.1.100:80   (Web Dashboard)
   ```

2. **Set up dynamic DNS**:
   ```bash
   # Install ddclient
   sudo apt install ddclient
   
   # Configure for your DNS provider
   sudo nano /etc/ddclient.conf
   ```

3. **Use VPN for secure access**:
   ```bash
   # Install OpenVPN server
   sudo apt install openvpn easy-rsa
   
   # Configure VPN access
   # Generate client certificates
   ```

## Database Issues

### MongoDB Problems

#### Problem: Database connection failures
**Symptoms:**
- "Connection refused" errors
- Data not saving
- Slow query responses

**Diagnosis:**
```bash
# Check MongoDB status
sudo systemctl status mongodb

# Test connection
mongo --eval "db.stats()"

# Check database logs
sudo tail -f /var/log/mongodb/mongod.log

# Check disk space
df -h
```

**Solutions:**
1. **Restart MongoDB**:
   ```bash
   sudo systemctl restart mongodb
   sudo systemctl enable mongodb
   ```

2. **Check MongoDB configuration**:
   ```bash
   sudo nano /etc/mongod.conf
   
   # Ensure these settings:
   net:
     port: 27017
     bindIp: 127.0.0.1
   
   storage:
     dbPath: /var/lib/mongodb
   ```

3. **Repair database if corrupted**:
   ```bash
   sudo systemctl stop mongodb
   sudo mongod --repair --dbpath /var/lib/mongodb
   sudo systemctl start mongodb
   ```

### Redis Cache Issues

#### Problem: Redis memory issues
**Symptoms:**
- "Out of memory" errors
- Slow cache responses
- Cache misses

**Solutions:**
1. **Configure Redis memory**:
   ```bash
   # Edit Redis config
   sudo nano /etc/redis/redis.conf
   
   # Set memory limit
   maxmemory 256mb
   maxmemory-policy allkeys-lru
   
   # Restart Redis
   sudo systemctl restart redis
   ```

2. **Monitor Redis usage**:
   ```bash
   # Check memory usage
   redis-cli info memory
   
   # Clear cache if needed
   redis-cli flushall
   ```

## Performance Issues

### High CPU Usage

#### Diagnosis and Solutions

```bash
# Identify high CPU processes
top -p $(pgrep -d',' python)
htop

# Check specific services
ps aux | grep -E "(node|python)" | sort -k3 -nr

# Monitor system resources
iostat 1
vmstat 1
```

**Optimizations:**
1. **Reduce video processing load**:
   ```python
   # Process fewer frames
   if frame_count % 5 == 0:  # Every 5th frame
       process_frame(frame)
   
   # Use smaller frame sizes
   frame = cv2.resize(frame, (320, 240))
   
   # Use threading
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor(max_workers=2) as executor:
       future = executor.submit(process_frame, frame)
   ```

2. **Optimize database queries**:
   ```javascript
   // Add database indexes
   db.events.createIndex({ "timestamp": -1 })
   db.devices.createIndex({ "room": 1, "type": 1 })
   
   // Use aggregation pipelines
   db.energy_data.aggregate([
     { $match: { timestamp: { $gte: new Date() } } },
     { $group: { _id: "$device", total: { $sum: "$consumption" } } }
   ])
   ```

### Memory Leaks

#### Diagnosis:
```bash
# Monitor memory usage over time
watch -n 5 'free -h'

# Check for memory leaks in Python processes
pip install memory-profiler
python -m memory_profiler voice_assistant.py
```

**Solutions:**
1. **Fix OpenCV memory leaks**:
   ```python
   # Properly release resources
   cap.release()
   cv2.destroyAllWindows()
   
   # Limit frame buffer size
   frame_buffer = collections.deque(maxlen=10)
   ```

2. **Clean up temporary files**:
   ```bash
   # Add to crontab
   0 2 * * * find /tmp -name "*.jpg" -mtime +1 -delete
   0 2 * * * find logs/ -name "*.log" -size +100M -delete
   ```

## Emergency Procedures

### System Recovery

#### Complete System Failure

1. **Safe Mode Boot**:
   ```bash
   # Boot from backup SD card/disk
   # Mount main storage as secondary
   # Copy critical data to backup location
   ```

2. **Service-by-Service Recovery**:
   ```bash
   # Start minimal services first
   sudo systemctl start mongodb
   sudo systemctl start redis
   sudo systemctl start mosquitto
   
   # Test each service
   ./scripts/test_service.sh mongodb
   ./scripts/test_service.sh redis
   ./scripts/test_service.sh mosquitto
   
   # Start application services
   pm2 start ecosystem.config.js
   ```

3. **Factory Reset**:
   ```bash
   # Backup current configuration
   ./scripts/backup_config.sh
   
   # Reset to defaults
   ./scripts/factory_reset.sh
   
   # Restore from backup
   ./scripts/restore_backup.sh
   ```

### Security Incident Response

#### Suspected Breach

1. **Immediate Actions**:
   ```bash
   # Disconnect from internet
   sudo ufw deny out
   
   # Change all passwords
   ./scripts/change_all_passwords.sh
   
   # Review access logs
   tail -n 1000 logs/security.log | grep -i "unauthorized"
   ```

2. **Investigation**:
   ```bash
   # Check for unusual network activity
   sudo netstat -tulnp
   sudo ss -tulnp
   
   # Review system logs
   sudo journalctl --since "1 hour ago" | grep -i "error\|fail\|denied"
   
   # Check file integrity
   sudo aide --check
   ```

3. **Recovery**:
   ```bash
   # Update all systems
   sudo apt update && sudo apt upgrade
   
   # Regenerate certificates
   ./scripts/regenerate_certificates.sh
   
   # Restore from clean backup
   ./scripts/restore_clean_backup.sh
   ```

## Getting Help

### Self-Help Resources

1. **System Logs**:
   ```bash
   # Application logs
   tail -f logs/system.log
   tail -f logs/voice.log
   tail -f logs/security.log
   tail -f logs/energy.log
   
   # System logs
   sudo journalctl -f
   sudo dmesg | tail -20
   ```

2. **Configuration Validation**:
   ```bash
   # Validate JSON config files
   ./scripts/validate_config.sh
   
   # Test all connections
   ./scripts/test_connections.sh
   
   # Run health checks
   ./scripts/health_check.sh
   ```

### Community Support

1. **GitHub Issues**: https://github.com/yourusername/advanced-smart-home/issues
2. **Discord Server**: https://discord.gg/smarthome
3. **Reddit Community**: r/HomeAutomation
4. **Documentation**: https://docs.smarthome-system.com

### Professional Support

1. **Email**: support@smarthome-system.com
2. **Priority Support**: Available for Enterprise users
3. **Custom Installation**: Professional services available
4. **Training**: Remote and on-site training programs

### Creating Effective Bug Reports

When reporting issues, include:

```
**System Information:**
- OS: Ubuntu 20.04 LTS
- Hardware: Raspberry Pi 4 (8GB)
- Python Version: 3.8.10
- Node.js Version: 16.14.0

**Issue Description:**
- What were you trying to do?
- What did you expect to happen?
- What actually happened?

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Logs:**
```
[Paste relevant log entries here]
```

**Configuration:**
- Any custom configurations
- Recent changes made

**Additional Context:**
- Screenshots if applicable
- Network setup details
- Hardware specifications
```

## Preventive Maintenance

### Daily Monitoring

- [ ] Check system status dashboard
- [ ] Review error logs
- [ ] Verify backup operations
- [ ] Test critical functions

### Weekly Tasks

- [ ] Update system packages
- [ ] Review security logs
- [ ] Clean temporary files
- [ ] Test backup restoration

### Monthly Maintenance

- [ ] Full system backup
- [ ] Security audit
- [ ] Performance optimization
- [ ] Hardware inspection

### Quarterly Reviews

- [ ] Update documentation
- [ ] Review user access
- [ ] Plan system upgrades
- [ ] Disaster recovery testing

This troubleshooting guide should help you resolve most common issues with your smart home system. For complex problems or custom configurations, don't hesitate to reach out to the community or professional support services.