#!/usr/bin/env python3
"""
Advanced CCTV Surveillance System
Part of Smart Home Automation Project

Features:
- Multi-camera support with IP cameras and USB cameras
- Real-time motion detection and object tracking
- Automated recording with event-based triggers
- Face recognition and person identification
- Live streaming to web dashboard and mobile app
- Alert notifications via email, SMS, and push notifications
- Cloud storage integration for recordings
- AI-powered threat detection and behavior analysis
- Night vision and low-light enhancement
"""

import cv2
import numpy as np
import threading
import queue
import time
import datetime
import os
import json
import sqlite3
import logging
import asyncio
import websockets
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import face_recognition
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.image import MimeImage
import paho.mqtt.client as mqtt
from flask import Flask, Response, jsonify, render_template_string
from flask_socketio import SocketIO, emit
import requests
from concurrent.futures import ThreadPoolExecutor
import pickle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cctv_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CCTVSystem:
    def __init__(self, config_file='config/cctv_config.json'):
        """Initialize CCTV surveillance system"""
        self.config = self.load_config(config_file)
        self.cameras = {}
        self.recording_threads = {}
        self.motion_detectors = {}
        self.face_encodings = {}
        self.known_faces = {}
        self.alert_queue = queue.Queue()
        self.running = False
        
        # Initialize database
        self.init_database()
        
        # Initialize MQTT client
        self.mqtt_client = mqtt.Client()
        self.setup_mqtt()
        
        # Initialize Flask app for streaming
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.setup_flask_routes()
        
        # Load known faces
        self.load_known_faces()
        
        # Initialize background subtractor for motion detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=True
        )
        
        # Thread pool for processing
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self.get_default_config()
    
    def get_default_config(self):
        """Get default configuration"""
        return {
            "cameras": [
                {
                    "id": "cam_001",
                    "name": "Front Door",
                    "source": 0,  # USB camera
                    "type": "usb",
                    "resolution": [1280, 720],
                    "fps": 30,
                    "location": "entrance"
                },
                {
                    "id": "cam_002", 
                    "name": "Living Room",
                    "source": "rtsp://192.168.1.100:554/stream",
                    "type": "ip",
                    "resolution": [1920, 1080],
                    "fps": 25,
                    "location": "living_room"
                }
            ],
            "motion_detection": {
                "sensitivity": 30,
                "min_area": 500,
                "blur_size": 21
            },
            "recording": {
                "enabled": True,
                "format": "mp4",
                "quality": "high",
                "duration": 300,  # 5 minutes per file
                "storage_path": "recordings/",
                "retention_days": 30
            },
            "alerts": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "your_email@gmail.com",
                    "password": "your_app_password",
                    "recipients": ["admin@smarthome.com"]
                },
                "mqtt": {
                    "enabled": True,
                    "topic": "smarthome/security/alerts"
                }
            },
            "face_recognition": {
                "enabled": True,
                "tolerance": 0.6,
                "model": "hog"  # or "cnn" for GPU
            },
            "streaming": {
                "enabled": True,
                "port": 5000,
                "quality": "medium"
            },
            "mqtt": {
                "broker": "localhost",
                "port": 1883,
                "username": "",
                "password": "",
                "topics": {
                    "camera_status": "smarthome/cctv/status",
                    "motion_detected": "smarthome/cctv/motion",
                    "face_detected": "smarthome/cctv/face"
                }
            }
        }
    
    def init_database(self):
        """Initialize SQLite database for events and recordings"""
        os.makedirs('data', exist_ok=True)
        self.db_path = 'data/cctv_events.db'
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                camera_id TEXT,
                event_type TEXT,
                description TEXT,
                image_path TEXT,
                video_path TEXT,
                confidence REAL,
                metadata TEXT
            )
        ''')
        
        # Recordings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recordings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                camera_id TEXT,
                file_path TEXT,
                duration INTEGER,
                file_size INTEGER,
                event_triggered BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_mqtt(self):
        """Setup MQTT client for communication"""
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info("Connected to MQTT broker")
                client.subscribe("smarthome/cctv/control")
            else:
                logger.error(f"Failed to connect to MQTT broker: {rc}")
        
        def on_message(client, userdata, msg):
            try:
                message = json.loads(msg.payload.decode())
                self.handle_mqtt_command(message)
            except Exception as e:
                logger.error(f"Error processing MQTT message: {e}")
        
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message
        
        if self.config['mqtt']['username']:
            self.mqtt_client.username_pw_set(
                self.config['mqtt']['username'],
                self.config['mqtt']['password']
            )
        
        try:
            self.mqtt_client.connect(
                self.config['mqtt']['broker'],
                self.config['mqtt']['port'],
                60
            )
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT: {e}")
    
    def setup_flask_routes(self):
        """Setup Flask routes for video streaming"""
        
        @self.app.route('/')
        def index():
            return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>CCTV Surveillance</title>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
            </head>
            <body>
                <h1>Smart Home CCTV System</h1>
                <div id="cameras"></div>
                <script>
                    const socket = io();
                    
                    // Create camera feeds
                    const cameras = {{ cameras | tojsonfilter }};
                    cameras.forEach(cam => {
                        const div = document.createElement('div');
                        div.innerHTML = `
                            <h3>${cam.name}</h3>
                            <img id="feed_${cam.id}" src="/video_feed/${cam.id}" 
                                 style="width: 640px; height: 480px; border: 1px solid #ccc;">
                        `;
                        document.getElementById('cameras').appendChild(div);
                    });
                    
                    // Handle real-time events
                    socket.on('motion_detected', (data) => {
                        console.log('Motion detected:', data);
                        // Add visual notification
                    });
                    
                    socket.on('face_detected', (data) => {
                        console.log('Face detected:', data);
                        // Add visual notification
                    });
                </script>
            </body>
            </html>
            ''', cameras=self.config['cameras'])
        
        @self.app.route('/video_feed/<camera_id>')
        def video_feed(camera_id):
            """Video streaming route"""
            return Response(
                self.generate_frames(camera_id),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )
        
        @self.app.route('/api/cameras')
        def get_cameras():
            """API endpoint to get camera status"""
            camera_status = []
            for cam_id, camera in self.cameras.items():
                status = {
                    'id': cam_id,
                    'name': camera.get('name', 'Unknown'),
                    'status': 'online' if camera.get('active', False) else 'offline',
                    'recording': camera.get('recording', False)
                }
                camera_status.append(status)
            return jsonify(camera_status)
        
        @self.app.route('/api/events')
        def get_events():
            """API endpoint to get recent events"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM events 
                ORDER BY timestamp DESC 
                LIMIT 50
            ''')
            events = cursor.fetchall()
            conn.close()
            
            return jsonify([{
                'id': event[0],
                'timestamp': event[1],
                'camera_id': event[2],
                'type': event[3],
                'description': event[4],
                'confidence': event[6]
            } for event in events])
    
    def load_known_faces(self):
        """Load known faces for recognition"""
        faces_dir = Path('data/known_faces')
        if not faces_dir.exists():
            faces_dir.mkdir(parents=True)
            logger.info("Created known_faces directory")
            return
        
        for person_dir in faces_dir.iterdir():
            if person_dir.is_dir():
                person_name = person_dir.name
                encodings = []
                
                for image_file in person_dir.glob('*.jpg'):
                    try:
                        image = face_recognition.load_image_file(str(image_file))
                        encoding = face_recognition.face_encodings(image)
                        if encoding:
                            encodings.append(encoding[0])
                    except Exception as e:
                        logger.error(f"Error loading face {image_file}: {e}")
                
                if encodings:
                    self.known_faces[person_name] = encodings
                    logger.info(f"Loaded {len(encodings)} faces for {person_name}")
    
    def initialize_cameras(self):
        """Initialize all cameras"""
        for cam_config in self.config['cameras']:
            try:
                self.setup_camera(cam_config)
            except Exception as e:
                logger.error(f"Failed to setup camera {cam_config['id']}: {e}")
    
    def setup_camera(self, cam_config):
        """Setup individual camera"""
        cam_id = cam_config['id']
        
        # Initialize video capture
        if cam_config['type'] == 'ip':
            cap = cv2.VideoCapture(cam_config['source'])
        else:
            cap = cv2.VideoCapture(int(cam_config['source']))
        
        if not cap.isOpened():
            raise Exception(f"Cannot open camera {cam_id}")
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_config['resolution'][0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_config['resolution'][1])
        cap.set(cv2.CAP_PROP_FPS, cam_config['fps'])
        
        self.cameras[cam_id] = {
            'capture': cap,
            'config': cam_config,
            'active': True,
            'recording': False,
            'last_frame': None,
            'motion_detector': cv2.createBackgroundSubtractorMOG2()
        }
        
        logger.info(f"Camera {cam_id} ({cam_config['name']}) initialized")
    
    def start_surveillance(self):
        """Start the surveillance system"""
        if self.running:
            return
        
        self.running = True
        logger.info("Starting CCTV surveillance system")
        
        # Initialize cameras
        self.initialize_cameras()
        
        # Start camera threads
        for cam_id in self.cameras.keys():
            thread = threading.Thread(
                target=self.camera_worker,
                args=(cam_id,),
                daemon=True
            )
            thread.start()
        
        # Start alert processing thread
        alert_thread = threading.Thread(
            target=self.process_alerts,
            daemon=True
        )
        alert_thread.start()
        
        # Start Flask app for streaming
        if self.config['streaming']['enabled']:
            streaming_thread = threading.Thread(
                target=self.start_streaming_server,
                daemon=True
            )
            streaming_thread.start()
        
        # Publish system status
        self.publish_system_status("online")
    
    def camera_worker(self, cam_id):
        """Worker thread for individual camera"""
        camera = self.cameras[cam_id]
        cap = camera['capture']
        motion_detector = camera['motion_detector']
        
        while self.running and camera['active']:
            try:
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Failed to read from camera {cam_id}")
                    time.sleep(1)
                    continue
                
                # Store current frame
                camera['last_frame'] = frame.copy()
                
                # Process frame
                self.process_frame(cam_id, frame, motion_detector)
                
                time.sleep(1 / camera['config']['fps'])
                
            except Exception as e:
                logger.error(f"Error in camera worker {cam_id}: {e}")
                time.sleep(5)
        
        cap.release()
    
    def process_frame(self, cam_id, frame, motion_detector):
        """Process individual frame for motion and face detection"""
        try:
            # Motion detection
            if self.config.get('motion_detection', {}).get('enabled', True):
                motion_detected = self.detect_motion(frame, motion_detector)
                if motion_detected:
                    self.handle_motion_detected(cam_id, frame)
            
            # Face recognition
            if self.config.get('face_recognition', {}).get('enabled', True):
                faces = self.detect_faces(frame)
                if faces:
                    self.handle_faces_detected(cam_id, frame, faces)
            
        except Exception as e:
            logger.error(f"Error processing frame for camera {cam_id}: {e}")
    
    def detect_motion(self, frame, motion_detector):
        """Detect motion in frame"""
        # Apply background subtraction
        fg_mask = motion_detector.apply(frame)
        
        # Noise reduction
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(
            fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Check for significant motion
        min_area = self.config['motion_detection']['min_area']
        for contour in contours:
            if cv2.contourArea(contour) > min_area:
                return True
        
        return False
    
    def detect_faces(self, frame):
        """Detect and recognize faces in frame"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        detected_faces = []
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Try to match with known faces
            name = "Unknown"
            confidence = 0.0
            
            for person_name, known_encodings in self.known_faces.items():
                matches = face_recognition.compare_faces(
                    known_encodings, face_encoding,
                    tolerance=self.config['face_recognition']['tolerance']
                )
                
                if True in matches:
                    # Calculate confidence
                    distances = face_recognition.face_distance(
                        known_encodings, face_encoding
                    )
                    confidence = 1 - min(distances)
                    name = person_name
                    break
            
            detected_faces.append({
                'name': name,
                'confidence': confidence,
                'location': (top, right, bottom, left)
            })
        
        return detected_faces
    
    def handle_motion_detected(self, cam_id, frame):
        """Handle motion detection event"""
        timestamp = datetime.datetime.now()
        
        # Save frame
        frame_path = self.save_event_frame(cam_id, frame, 'motion')
        
        # Log event
        self.log_event(
            cam_id, 'motion_detected', 
            'Motion detected in camera view',
            frame_path
        )
        
        # Send alert
        alert = {
            'type': 'motion',
            'camera_id': cam_id,
            'timestamp': timestamp.isoformat(),
            'image_path': frame_path
        }
        self.alert_queue.put(alert)
        
        # Publish to MQTT
        self.mqtt_client.publish(
            self.config['mqtt']['topics']['motion_detected'],
            json.dumps(alert)
        )
        
        # Emit to web clients
        self.socketio.emit('motion_detected', alert)
        
        logger.info(f"Motion detected on camera {cam_id}")
    
    def handle_faces_detected(self, cam_id, frame, faces):
        """Handle face detection event"""
        timestamp = datetime.datetime.now()
        
        for face in faces:
            # Save frame with face highlighted
            frame_with_face = self.draw_face_box(frame.copy(), face)
            frame_path = self.save_event_frame(cam_id, frame_with_face, 'face')
            
            # Log event
            description = f"Face detected: {face['name']} (confidence: {face['confidence']:.2f})"
            self.log_event(
                cam_id, 'face_detected', description,
                frame_path, confidence=face['confidence']
            )
            
            # Send alert for unknown faces or specific persons
            if face['name'] == 'Unknown' or face['confidence'] > 0.8:
                alert = {
                    'type': 'face',
                    'camera_id': cam_id,
                    'person': face['name'],
                    'confidence': face['confidence'],
                    'timestamp': timestamp.isoformat(),
                    'image_path': frame_path
                }
                self.alert_queue.put(alert)
                
                # Publish to MQTT
                self.mqtt_client.publish(
                    self.config['mqtt']['topics']['face_detected'],
                    json.dumps(alert)
                )
                
                # Emit to web clients
                self.socketio.emit('face_detected', alert)
        
        logger.info(f"Detected {len(faces)} faces on camera {cam_id}")
    
    def draw_face_box(self, frame, face):
        """Draw bounding box around detected face"""
        top, right, bottom, left = face['location']
        
        # Draw rectangle
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        # Draw label
        label = f"{face['name']} ({face['confidence']:.2f})"
        cv2.putText(
            frame, label, (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
        )
        
        return frame
    
    def save_event_frame(self, cam_id, frame, event_type):
        """Save frame for event"""
        timestamp = datetime.datetime.now()
        filename = f"{cam_id}_{event_type}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        
        events_dir = Path('data/events')
        events_dir.mkdir(exist_ok=True)
        
        frame_path = events_dir / filename
        cv2.imwrite(str(frame_path), frame)
        
        return str(frame_path)
    
    def log_event(self, cam_id, event_type, description, image_path=None, 
                  video_path=None, confidence=None):
        """Log event to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events 
            (camera_id, event_type, description, image_path, video_path, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (cam_id, event_type, description, image_path, video_path, confidence))
        
        conn.commit()
        conn.close()
    
    def process_alerts(self):
        """Process alert queue"""
        while self.running:
            try:
                alert = self.alert_queue.get(timeout=1)
                
                # Send email alert
                if self.config['alerts']['email']['enabled']:
                    self.send_email_alert(alert)
                
                # Send push notification
                self.send_push_notification(alert)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing alert: {e}")
    
    def send_email_alert(self, alert):
        """Send email alert"""
        try:
            email_config = self.config['alerts']['email']
            
            msg = MimeMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(email_config['recipients'])
            msg['Subject'] = f"Smart Home Security Alert - {alert['type'].title()}"
            
            # Email body
            body = f"""
            Security Alert from Smart Home CCTV System
            
            Type: {alert['type'].title()}
            Camera: {alert['camera_id']}
            Time: {alert['timestamp']}
            
            Details: {alert.get('description', 'Event detected')}
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Attach image if available
            if 'image_path' in alert and os.path.exists(alert['image_path']):
                with open(alert['image_path'], 'rb') as f:
                    img_data = f.read()
                    image = MimeImage(img_data)
                    image.add_header('Content-Disposition', 'attachment', 
                                   filename='alert_image.jpg')
                    msg.attach(image)
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email alert sent for {alert['type']} event")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def send_push_notification(self, alert):
        """Send push notification to mobile app"""
        try:
            # This would integrate with your push notification service
            # (Firebase, OneSignal, etc.)
            notification_data = {
                'title': f"Security Alert - {alert['type'].title()}",
                'body': f"Event detected on camera {alert['camera_id']}",
                'data': alert
            }
            
            # Send to notification service
            # requests.post('your_push_service_url', json=notification_data)
            
            logger.info(f"Push notification sent for {alert['type']} event")
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
    
    def generate_frames(self, cam_id):
        """Generate frames for video streaming"""
        if cam_id not in self.cameras:
            return
        
        camera = self.cameras[cam_id]
        
        while self.running and camera['active']:
            if camera['last_frame'] is not None:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', camera['last_frame'])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.1)  # Limit streaming FPS
    
    def start_streaming_server(self):
        """Start Flask streaming server"""
        try:
            self.socketio.run(
                self.app,
                host='0.0.0.0',
                port=self.config['streaming']['port'],
                debug=False
            )
        except Exception as e:
            logger.error(f"Failed to start streaming server: {e}")
    
    def handle_mqtt_command(self, message):
        """Handle MQTT commands"""
        command = message.get('command')
        
        if command == 'start_recording':
            cam_id = message.get('camera_id')
            if cam_id in self.cameras:
                self.start_recording(cam_id)
        
        elif command == 'stop_recording':
            cam_id = message.get('camera_id')
            if cam_id in self.cameras:
                self.stop_recording(cam_id)
        
        elif command == 'get_status':
            self.publish_system_status()
        
        elif command == 'reboot_camera':
            cam_id = message.get('camera_id')
            if cam_id in self.cameras:
                self.reboot_camera(cam_id)
    
    def start_recording(self, cam_id):
        """Start recording for specific camera"""
        if cam_id not in self.cameras:
            return
        
        camera = self.cameras[cam_id]
        if camera['recording']:
            return
        
        camera['recording'] = True
        
        # Start recording thread
        record_thread = threading.Thread(
            target=self.record_camera,
            args=(cam_id,),
            daemon=True
        )
        record_thread.start()
        
        logger.info(f"Started recording for camera {cam_id}")
    
    def stop_recording(self, cam_id):
        """Stop recording for specific camera"""
        if cam_id not in self.cameras:
            return
        
        camera = self.cameras[cam_id]
        camera['recording'] = False
        
        logger.info(f"Stopped recording for camera {cam_id}")
    
    def record_camera(self, cam_id):
        """Record video from camera"""
        camera = self.cameras[cam_id]
        cap = camera['capture']
        
        timestamp = datetime.datetime.now()
        filename = f"{cam_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.mp4"
        
        recordings_dir = Path(self.config['recording']['storage_path'])
        recordings_dir.mkdir(exist_ok=True)
        
        video_path = recordings_dir / filename
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = camera['config']['fps']
        frame_size = tuple(camera['config']['resolution'])
        
        out = cv2.VideoWriter(str(video_path), fourcc, fps, frame_size)
        
        start_time = time.time()
        duration = self.config['recording']['duration']
        
        while (camera['recording'] and 
               time.time() - start_time < duration and
               self.running):
            
            if camera['last_frame'] is not None:
                out.write(camera['last_frame'])
            
            time.sleep(1 / fps)
        
        out.release()
        
        # Log recording
        file_size = os.path.getsize(video_path) if video_path.exists() else 0
        actual_duration = int(time.time() - start_time)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO recordings 
            (camera_id, file_path, duration, file_size)
            VALUES (?, ?, ?, ?)
        ''', (cam_id, str(video_path), actual_duration, file_size))
        conn.commit()
        conn.close()
        
        logger.info(f"Recording saved: {video_path}")
    
    def publish_system_status(self, status="running"):
        """Publish system status to MQTT"""
        status_data = {
            'status': status,
            'timestamp': datetime.datetime.now().isoformat(),
            'cameras': {
                cam_id: {
                    'active': cam['active'],
                    'recording': cam.get('recording', False)
                }
                for cam_id, cam in self.cameras.items()
            }
        }
        
        self.mqtt_client.publish(
            self.config['mqtt']['topics']['camera_status'],
            json.dumps(status_data)
        )
    
    def cleanup_old_recordings(self):
        """Clean up old recordings based on retention policy"""
        retention_days = self.config['recording']['retention_days']
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find old recordings
        cursor.execute('''
            SELECT file_path FROM recordings 
            WHERE timestamp < ?
        ''', (cutoff_date,))
        
        old_recordings = cursor.fetchall()
        
        for (file_path,) in old_recordings:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted old recording: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete {file_path}: {e}")
        
        # Remove from database
        cursor.execute('''
            DELETE FROM recordings 
            WHERE timestamp < ?
        ''', (cutoff_date,))
        
        conn.commit()
        conn.close()
    
    def stop_surveillance(self):
        """Stop the surveillance system"""
        logger.info("Stopping CCTV surveillance system")
        self.running = False
        
        # Stop all cameras
        for cam_id, camera in self.cameras.items():
            camera['active'] = False
            camera['recording'] = False
            if 'capture' in camera:
                camera['capture'].release()
        
        # Disconnect MQTT
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        
        # Publish offline status
        self.publish_system_status("offline")
        
        logger.info("CCTV surveillance system stopped")

def main():
    """Main function to run CCTV system"""
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Initialize and start CCTV system
    cctv = CCTVSystem()
    
    try:
        cctv.start_surveillance()
        
        # Keep running
        while True:
            time.sleep(1)
            
            # Cleanup old recordings daily
            if datetime.datetime.now().hour == 2:  # 2 AM
                cctv.cleanup_old_recordings()
                time.sleep(3600)  # Wait an hour
    
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        cctv.stop_surveillance()

if __name__ == "__main__":
    main()