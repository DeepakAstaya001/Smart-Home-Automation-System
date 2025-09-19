"""
Advanced Security System with Face Detection, Biometric Authentication, and Access Control
Features: OpenCV face recognition, fingerprint authentication, real-time monitoring
Author: Deepak
Version: 2.0
"""

import cv2
import numpy as np
import face_recognition
import pickle
import sqlite3
import hashlib
import time
import threading
import json
import os
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import requests
import logging
from collections import defaultdict
import serial
import base64

# Machine Learning imports
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import joblib

# Biometric sensor imports
try:
    import adafruit_fingerprint
    FINGERPRINT_AVAILABLE = True
except ImportError:
    FINGERPRINT_AVAILABLE = False
    print("Fingerprint sensor library not available")

class SecuritySystem:
    def __init__(self, config_file="security_config.json"):
        self.load_config(config_file)
        self.setup_logging()
        self.initialize_database()
        self.initialize_face_recognition()
        self.initialize_biometric_scanner()
        self.initialize_mqtt()
        self.initialize_ai_detection()
        
        # Security state
        self.system_armed = False
        self.authorized_users = []
        self.face_encodings = {}
        self.fingerprint_templates = {}
        self.intrusion_detected = False
        self.failed_attempts = defaultdict(int)
        self.last_detection_time = {}
        
        # Camera setup
        self.cameras = {}
        self.recording_threads = {}
        
        print("Advanced Security System Initialized!")
        
    def load_config(self, config_file):
        """Load security system configuration"""
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "cameras": [
                    {"id": 0, "name": "Front Door", "location": "entrance"},
                    {"id": 1, "name": "Back Door", "location": "rear"},
                    {"id": 2, "name": "Living Room", "location": "interior"},
                    {"id": 3, "name": "Garage", "location": "garage"}
                ],
                "mqtt": {
                    "broker": "localhost",
                    "port": 1883,
                    "topics": {
                        "alerts": "security/alerts",
                        "status": "security/status",
                        "commands": "security/commands"
                    }
                },
                "recognition": {
                    "face_threshold": 0.6,
                    "detection_interval": 1.0,
                    "max_failed_attempts": 3,
                    "lockout_duration": 300
                },
                "recording": {
                    "motion_sensitivity": 1000,
                    "recording_duration": 30,
                    "storage_days": 30,
                    "video_format": "mp4"
                }
            }
            
    def setup_logging(self):
        """Setup logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('security_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def initialize_database(self):
        """Initialize SQLite database for security logs"""
        self.db_path = "security_database.db"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                face_encoding BLOB,
                fingerprint_template BLOB,
                access_level INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_access TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                access_method TEXT,
                location TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN,
                confidence REAL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                description TEXT,
                location TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                severity INTEGER DEFAULT 1,
                resolved BOOLEAN DEFAULT 0,
                image_path TEXT,
                video_path TEXT
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS intrusion_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                detection_method TEXT,
                confidence REAL,
                image_path TEXT,
                ip_address TEXT
            )
        """)
        
        self.conn.commit()
        
    def initialize_face_recognition(self):
        """Initialize face recognition system"""
        try:
            # Load known face encodings
            self.load_known_faces()
            
            # Initialize face detection cascade
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Initialize face recognition model
            self.face_recognition_model = cv2.face.LBPHFaceRecognizer_create()
            
            self.logger.info("Face recognition system initialized")
        except Exception as e:
            self.logger.error(f"Face recognition initialization error: {e}")
            
    def initialize_biometric_scanner(self):
        """Initialize fingerprint scanner"""
        self.fingerprint_scanner = None
        if FINGERPRINT_AVAILABLE:
            try:
                # Initialize UART for fingerprint sensor
                uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
                self.fingerprint_scanner = adafruit_fingerprint.Adafruit_Fingerprint(uart)
                
                if self.fingerprint_scanner.verify_password():
                    self.logger.info("Fingerprint scanner initialized successfully")
                else:
                    self.logger.error("Failed to connect to fingerprint scanner")
                    self.fingerprint_scanner = None
            except Exception as e:
                self.logger.error(f"Fingerprint scanner initialization error: {e}")
                self.fingerprint_scanner = None
        else:
            self.logger.warning("Fingerprint scanner not available")
            
    def initialize_mqtt(self):
        """Initialize MQTT communication"""
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        try:
            self.mqtt_client.connect(
                self.config["mqtt"]["broker"],
                self.config["mqtt"]["port"],
                60
            )
            self.mqtt_client.loop_start()
            self.logger.info("MQTT client connected")
        except Exception as e:
            self.logger.error(f"MQTT connection error: {e}")
            
    def initialize_ai_detection(self):
        """Initialize AI-based detection models"""
        try:
            # Load pre-trained models for object detection
            self.ai_models = {}
            
            # Initialize person detection model
            self.ai_models['person_detector'] = cv2.dnn.readNetFromDarknet(
                'models/yolov3.cfg',
                'models/yolov3.weights'
            ) if os.path.exists('models/yolov3.weights') else None
            
            # Initialize suspicious activity detection
            self.ai_models['activity_classifier'] = joblib.load(
                'models/activity_classifier.pkl'
            ) if os.path.exists('models/activity_classifier.pkl') else None
            
            self.logger.info("AI detection models loaded")
        except Exception as e:
            self.logger.error(f"AI model initialization error: {e}")
            
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            client.subscribe(self.config["mqtt"]["topics"]["commands"])
            self.logger.info("MQTT connected and subscribed to commands")
        else:
            self.logger.error(f"MQTT connection failed with code {rc}")
            
    def on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            message = json.loads(msg.payload.decode())
            self.handle_mqtt_command(message)
        except Exception as e:
            self.logger.error(f"MQTT message processing error: {e}")
            
    def handle_mqtt_command(self, command):
        """Handle MQTT commands"""
        cmd_type = command.get('type')
        
        if cmd_type == 'ARM_SYSTEM':
            self.arm_system()
        elif cmd_type == 'DISARM_SYSTEM':
            self.disarm_system()
        elif cmd_type == 'ADD_USER':
            self.add_user_from_command(command)
        elif cmd_type == 'DELETE_USER':
            self.delete_user(command.get('user_id'))
        elif cmd_type == 'EMERGENCY_LOCKDOWN':
            self.emergency_lockdown()
        elif cmd_type == 'GET_STATUS':
            self.send_system_status()
            
    def load_known_faces(self):
        """Load known face encodings from database"""
        try:
            self.cursor.execute("SELECT id, name, face_encoding FROM users WHERE is_active = 1")
            users = self.cursor.fetchall()
            
            self.face_encodings = {}
            for user_id, name, encoding_blob in users:
                if encoding_blob:
                    encoding = pickle.loads(encoding_blob)
                    self.face_encodings[user_id] = {
                        'name': name,
                        'encoding': encoding
                    }
                    
            self.logger.info(f"Loaded {len(self.face_encodings)} known faces")
        except Exception as e:
            self.logger.error(f"Error loading known faces: {e}")
            
    def add_user(self, name, image_path=None, fingerprint_scan=False):
        """Add new user to the system"""
        try:
            face_encoding = None
            fingerprint_template = None
            
            # Process face encoding
            if image_path and os.path.exists(image_path):
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                
                if encodings:
                    face_encoding = encodings[0]
                else:
                    self.logger.warning(f"No face found in image {image_path}")
                    
            # Process fingerprint
            if fingerprint_scan and self.fingerprint_scanner:
                fingerprint_template = self.scan_fingerprint_for_enrollment()
                
            # Store in database
            face_blob = pickle.dumps(face_encoding) if face_encoding is not None else None
            fingerprint_blob = pickle.dumps(fingerprint_template) if fingerprint_template else None
            
            self.cursor.execute("""
                INSERT INTO users (name, face_encoding, fingerprint_template)
                VALUES (?, ?, ?)
            """, (name, face_blob, fingerprint_blob))
            
            user_id = self.cursor.lastrowid
            self.conn.commit()
            
            # Update runtime data
            if face_encoding is not None:
                self.face_encodings[user_id] = {
                    'name': name,
                    'encoding': face_encoding
                }
                
            self.logger.info(f"User {name} added successfully with ID {user_id}")
            return user_id
            
        except Exception as e:
            self.logger.error(f"Error adding user {name}: {e}")
            return None
            
    def scan_fingerprint_for_enrollment(self):
        """Scan fingerprint for user enrollment"""
        if not self.fingerprint_scanner:
            return None
            
        try:
            print("Place finger on scanner for enrollment...")
            
            # Get fingerprint image
            i = self.fingerprint_scanner.get_image()
            if i != adafruit_fingerprint.OK:
                return None
                
            # Convert to template
            i = self.fingerprint_scanner.image_2_tz(1)
            if i != adafruit_fingerprint.OK:
                return None
                
            # Get template data
            template = self.fingerprint_scanner.get_fpdata("char", 1)
            return template
            
        except Exception as e:
            self.logger.error(f"Fingerprint enrollment error: {e}")
            return None
            
    def detect_faces_in_frame(self, frame):
        """Detect and recognize faces in video frame"""
        try:
            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find faces
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            detected_faces = []
            
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(
                    [data['encoding'] for data in self.face_encodings.values()],
                    face_encoding,
                    tolerance=self.config["recognition"]["face_threshold"]
                )
                
                name = "Unknown"
                confidence = 0.0
                user_id = None
                
                if True in matches:
                    match_index = matches.index(True)
                    user_ids = list(self.face_encodings.keys())
                    user_id = user_ids[match_index]
                    name = self.face_encodings[user_id]['name']
                    
                    # Calculate confidence
                    face_distances = face_recognition.face_distance(
                        [self.face_encodings[user_id]['encoding']],
                        face_encoding
                    )
                    confidence = 1.0 - face_distances[0]
                    
                detected_faces.append({
                    'user_id': user_id,
                    'name': name,
                    'confidence': confidence,
                    'location': (top, right, bottom, left),
                    'recognized': user_id is not None
                })
                
            return detected_faces
            
        except Exception as e:
            self.logger.error(f"Face detection error: {e}")
            return []
            
    def verify_fingerprint(self):
        """Verify fingerprint against enrolled templates"""
        if not self.fingerprint_scanner:
            return None, 0.0
            
        try:
            print("Place finger on scanner for verification...")
            
            # Get fingerprint image
            i = self.fingerprint_scanner.get_image()
            if i != adafruit_fingerprint.OK:
                return None, 0.0
                
            # Convert to template
            i = self.fingerprint_scanner.image_2_tz(2)
            if i != adafruit_fingerprint.OK:
                return None, 0.0
                
            # Search for match
            i = self.fingerprint_scanner.finger_search()
            if i == adafruit_fingerprint.OK:
                user_id = self.fingerprint_scanner.finger_id
                confidence = self.fingerprint_scanner.confidence / 100.0
                
                # Get user name from database
                self.cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
                result = self.cursor.fetchone()
                name = result[0] if result else "Unknown"
                
                return {'user_id': user_id, 'name': name}, confidence
            else:
                return None, 0.0
                
        except Exception as e:
            self.logger.error(f"Fingerprint verification error: {e}")
            return None, 0.0
            
    def detect_motion(self, frame1, frame2):
        """Detect motion between two frames"""
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Calculate difference
            diff = cv2.absdiff(gray1, gray2)
            blur = cv2.GaussianBlur(diff, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_detected = False
            for contour in contours:
                if cv2.contourArea(contour) > self.config["recording"]["motion_sensitivity"]:
                    motion_detected = True
                    break
                    
            return motion_detected, thresh
            
        except Exception as e:
            self.logger.error(f"Motion detection error: {e}")
            return False, None
            
    def analyze_suspicious_activity(self, frame, motion_mask):
        """Analyze frame for suspicious activities using AI"""
        try:
            if not self.ai_models.get('person_detector'):
                return False, "No AI model available"
                
            # Detect persons
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            self.ai_models['person_detector'].setInput(blob)
            outputs = self.ai_models['person_detector'].forward()
            
            # Process detections
            suspicious_score = 0.0
            reasons = []
            
            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > 0.5 and class_id == 0:  # Person detected
                        # Check time of day
                        current_hour = datetime.now().hour
                        if current_hour < 6 or current_hour > 22:
                            suspicious_score += 0.3
                            reasons.append("Activity during unusual hours")
                            
                        # Check if system is armed
                        if self.system_armed:
                            suspicious_score += 0.5
                            reasons.append("Movement while system armed")
                            
                        # Check loitering (staying in same area)
                        # This would require tracking implementation
                        
            return suspicious_score > 0.5, reasons
            
        except Exception as e:
            self.logger.error(f"Suspicious activity analysis error: {e}")
            return False, ["Analysis error"]
            
    def log_access_attempt(self, user_id, method, location, success, confidence=0.0):
        """Log access attempt to database"""
        try:
            self.cursor.execute("""
                INSERT INTO access_logs (user_id, access_method, location, success, confidence)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, method, location, success, confidence))
            
            # Update last access time for successful attempts
            if success and user_id:
                self.cursor.execute("""
                    UPDATE users SET last_access = CURRENT_TIMESTAMP WHERE id = ?
                """, (user_id,))
                
            self.conn.commit()
            
        except Exception as e:
            self.logger.error(f"Error logging access attempt: {e}")
            
    def log_security_event(self, event_type, description, location, severity=1, image_path=None):
        """Log security event"""
        try:
            self.cursor.execute("""
                INSERT INTO security_events (event_type, description, location, severity, image_path)
                VALUES (?, ?, ?, ?, ?)
            """, (event_type, description, location, severity, image_path))
            
            self.conn.commit()
            
            # Send MQTT alert
            alert_data = {
                'type': event_type,
                'description': description,
                'location': location,
                'severity': severity,
                'timestamp': datetime.now().isoformat(),
                'image_path': image_path
            }
            
            self.mqtt_client.publish(
                self.config["mqtt"]["topics"]["alerts"],
                json.dumps(alert_data)
            )
            
        except Exception as e:
            self.logger.error(f"Error logging security event: {e}")
            
    def handle_intrusion(self, location, detection_method, confidence, frame=None):
        """Handle detected intrusion"""
        try:
            self.intrusion_detected = True
            
            # Save evidence
            image_path = None
            if frame is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = f"evidence/intrusion_{location}_{timestamp}.jpg"
                os.makedirs("evidence", exist_ok=True)
                cv2.imwrite(image_path, frame)
                
            # Log intrusion attempt
            self.cursor.execute("""
                INSERT INTO intrusion_attempts (location, detection_method, confidence, image_path)
                VALUES (?, ?, ?, ?)
            """, (location, detection_method, confidence, image_path))
            
            self.conn.commit()
            
            # Send emergency alert
            self.log_security_event(
                "INTRUSION_DETECTED",
                f"Unauthorized access detected in {location}",
                location,
                severity=3,
                image_path=image_path
            )
            
            # Trigger alarm
            self.trigger_alarm()
            
            self.logger.critical(f"INTRUSION DETECTED: {location} via {detection_method}")
            
        except Exception as e:
            self.logger.error(f"Error handling intrusion: {e}")
            
    def trigger_alarm(self):
        """Trigger security alarm"""
        try:
            # Send alarm command via MQTT
            alarm_data = {
                'type': 'TRIGGER_ALARM',
                'timestamp': datetime.now().isoformat(),
                'reason': 'intrusion_detected'
            }
            
            self.mqtt_client.publish(
                self.config["mqtt"]["topics"]["commands"],
                json.dumps(alarm_data)
            )
            
            # Send notifications (email, SMS, push notifications)
            self.send_emergency_notifications()
            
        except Exception as e:
            self.logger.error(f"Error triggering alarm: {e}")
            
    def send_emergency_notifications(self):
        """Send emergency notifications to authorities and users"""
        try:
            # This would integrate with notification services
            # Email, SMS, push notifications, etc.
            pass
        except Exception as e:
            self.logger.error(f"Error sending emergency notifications: {e}")
            
    def arm_system(self):
        """Arm the security system"""
        self.system_armed = True
        self.log_security_event("SYSTEM_ARMED", "Security system armed", "system")
        self.logger.info("Security system ARMED")
        
    def disarm_system(self):
        """Disarm the security system"""
        self.system_armed = False
        self.intrusion_detected = False
        self.log_security_event("SYSTEM_DISARMED", "Security system disarmed", "system")
        self.logger.info("Security system DISARMED")
        
    def start_monitoring(self, camera_id=0):
        """Start monitoring a specific camera"""
        try:
            cap = cv2.VideoCapture(camera_id)
            self.cameras[camera_id] = cap
            
            # Start monitoring thread
            thread = threading.Thread(
                target=self.monitor_camera,
                args=(camera_id,),
                daemon=True
            )
            thread.start()
            
            self.logger.info(f"Started monitoring camera {camera_id}")
            
        except Exception as e:
            self.logger.error(f"Error starting camera {camera_id}: {e}")
            
    def monitor_camera(self, camera_id):
        """Monitor camera feed for security events"""
        cap = self.cameras[camera_id]
        previous_frame = None
        
        while True:
            try:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Detect faces
                faces = self.detect_faces_in_frame(frame)
                
                # Process detected faces
                for face in faces:
                    if face['recognized']:
                        self.log_access_attempt(
                            face['user_id'],
                            'face_recognition',
                            f"camera_{camera_id}",
                            True,
                            face['confidence']
                        )
                    elif self.system_armed:
                        self.handle_intrusion(
                            f"camera_{camera_id}",
                            "unknown_face",
                            face['confidence'],
                            frame
                        )
                        
                # Detect motion
                if previous_frame is not None:
                    motion_detected, motion_mask = self.detect_motion(previous_frame, frame)
                    
                    if motion_detected and self.system_armed:
                        # Analyze for suspicious activity
                        is_suspicious, reasons = self.analyze_suspicious_activity(frame, motion_mask)
                        
                        if is_suspicious:
                            self.handle_intrusion(
                                f"camera_{camera_id}",
                                "suspicious_motion",
                                0.8,
                                frame
                            )
                            
                previous_frame = frame.copy()
                
                # Small delay to prevent overwhelming the system
                time.sleep(self.config["recognition"]["detection_interval"])
                
            except Exception as e:
                self.logger.error(f"Camera {camera_id} monitoring error: {e}")
                break
                
    def get_system_status(self):
        """Get current system status"""
        return {
            'armed': self.system_armed,
            'intrusion_detected': self.intrusion_detected,
            'active_cameras': len(self.cameras),
            'registered_users': len(self.face_encodings),
            'last_activity': self.get_last_activity(),
            'timestamp': datetime.now().isoformat()
        }
        
    def get_last_activity(self):
        """Get last security activity"""
        try:
            self.cursor.execute("""
                SELECT event_type, description, location, timestamp
                FROM security_events
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            result = self.cursor.fetchone()
            
            if result:
                return {
                    'type': result[0],
                    'description': result[1],
                    'location': result[2],
                    'timestamp': result[3]
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting last activity: {e}")
            return None
            
    def run(self):
        """Main security system loop"""
        try:
            self.logger.info("Security system started")
            
            # Start monitoring all configured cameras
            for camera_config in self.config["cameras"]:
                self.start_monitoring(camera_config["id"])
                
            # Keep the main thread alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Security system shutdown requested")
        except Exception as e:
            self.logger.error(f"Security system error: {e}")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Close cameras
            for cap in self.cameras.values():
                cap.release()
                
            # Close database
            self.conn.close()
            
            # Disconnect MQTT
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            
            self.logger.info("Security system cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

def main():
    security_system = SecuritySystem()
    security_system.run()

if __name__ == "__main__":
    main()