"""
Advanced Energy Management System with AI-Powered Optimization
Features: Smart scheduling, consumption monitoring, cost optimization, predictive analytics
Author: Deepak
Version: 2.0
"""

import time
import json
import sqlite3
import threading
import schedule
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import requests
import logging
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import seaborn as sns

# Machine Learning imports
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

# Time series analysis
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

class EnergyManagementSystem:
    def __init__(self, config_file="energy_config.json"):
        self.load_config(config_file)
        self.setup_logging()
        self.initialize_database()
        self.initialize_mqtt()
        self.initialize_ml_models()
        
        # Energy monitoring data
        self.current_readings = {}
        self.consumption_history = deque(maxlen=1000)
        self.device_power_ratings = {}
        self.optimization_schedule = {}
        self.peak_hours = []
        self.off_peak_hours = []
        
        # Occupancy and environmental data
        self.occupancy_sensors = {}
        self.weather_data = {}
        self.room_temperatures = {}
        
        # AI models
        self.ml_models = {}
        self.scaler = StandardScaler()
        
        # Control flags
        self.auto_optimization_enabled = True
        self.emergency_mode = False
        self.learning_mode = True
        
        print("Advanced Energy Management System Initialized!")
        
    def load_config(self, config_file):
        """Load energy management configuration"""
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "devices": {
                    "lights": [
                        {"id": "hall_light", "power_rating": 60, "room": "hall", "priority": 3},
                        {"id": "kitchen_light", "power_rating": 60, "room": "kitchen", "priority": 2},
                        {"id": "living_room_light", "power_rating": 100, "room": "living_room", "priority": 2},
                        {"id": "bedroom_light", "power_rating": 40, "room": "bedroom", "priority": 1}
                    ],
                    "fans": [
                        {"id": "hall_fan", "power_rating": 75, "room": "hall", "priority": 2},
                        {"id": "kitchen_fan", "power_rating": 50, "room": "kitchen", "priority": 1},
                        {"id": "living_room_fan", "power_rating": 75, "room": "living_room", "priority": 1},
                        {"id": "bedroom_fan", "power_rating": 75, "room": "bedroom", "priority": 1}
                    ],
                    "appliances": [
                        {"id": "refrigerator", "power_rating": 150, "room": "kitchen", "priority": 1, "always_on": True},
                        {"id": "washing_machine", "power_rating": 500, "room": "utility", "priority": 3},
                        {"id": "air_conditioner", "power_rating": 1500, "room": "living_room", "priority": 2},
                        {"id": "water_heater", "power_rating": 2000, "room": "utility", "priority": 2}
                    ]
                },
                "tariff": {
                    "peak_hours": [{"start": "18:00", "end": "22:00"}],
                    "off_peak_hours": [{"start": "22:00", "end": "06:00"}],
                    "peak_rate": 12.50,
                    "off_peak_rate": 8.00,
                    "normal_rate": 10.00,
                    "currency": "INR"
                },
                "thresholds": {
                    "max_daily_consumption": 25.0,
                    "high_usage_alert": 2000,
                    "cost_alert": 500,
                    "efficiency_target": 0.85
                },
                "optimization": {
                    "auto_schedule": True,
                    "load_balancing": True,
                    "predictive_control": True,
                    "weather_integration": True
                },
                "mqtt": {
                    "broker": "localhost",
                    "port": 1883,
                    "topics": {
                        "energy_data": "energy/consumption",
                        "device_control": "energy/control",
                        "optimization": "energy/optimization",
                        "alerts": "energy/alerts"
                    }
                }
            }
            
    def setup_logging(self):
        """Setup logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('energy_management.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def initialize_database(self):
        """Initialize SQLite database for energy data"""
        self.db_path = "energy_database.db"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS energy_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                device_id TEXT,
                power_consumption REAL,
                voltage REAL,
                current REAL,
                power_factor REAL,
                frequency REAL,
                room TEXT,
                device_type TEXT
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_consumption (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                total_consumption REAL,
                peak_consumption REAL,
                off_peak_consumption REAL,
                total_cost REAL,
                average_power REAL,
                max_power REAL,
                efficiency_score REAL
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                start_time TIME,
                end_time TIME,
                days_of_week TEXT,
                power_level REAL,
                condition_type TEXT,
                condition_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                optimization_type TEXT,
                devices_affected TEXT,
                estimated_savings REAL,
                actual_savings REAL,
                success BOOLEAN
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS occupancy_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                room TEXT,
                occupancy_count INTEGER,
                motion_detected BOOLEAN,
                light_level REAL,
                temperature REAL,
                humidity REAL
            )
        """)
        
        self.conn.commit()
        
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
            
    def initialize_ml_models(self):
        """Initialize machine learning models for energy prediction and optimization"""
        try:
            # Load existing models or create new ones
            self.ml_models = {
                'consumption_predictor': self.load_or_create_model('consumption_predictor'),
                'demand_forecaster': self.load_or_create_model('demand_forecaster'),
                'efficiency_optimizer': self.load_or_create_model('efficiency_optimizer'),
                'anomaly_detector': self.load_or_create_model('anomaly_detector')
            }
            
            # Initialize feature scaler
            self.scaler = self.load_or_create_scaler()
            
            self.logger.info("ML models initialized successfully")
        except Exception as e:
            self.logger.error(f"ML model initialization error: {e}")
            
    def load_or_create_model(self, model_name):
        """Load existing ML model or create a new one"""
        model_path = f"models/{model_name}.pkl"
        try:
            if os.path.exists(model_path):
                return joblib.load(model_path)
            else:
                # Create new model based on type
                if model_name == 'consumption_predictor':
                    return RandomForestRegressor(n_estimators=100, random_state=42)
                elif model_name == 'demand_forecaster':
                    return LinearRegression()
                elif model_name == 'efficiency_optimizer':
                    return RandomForestRegressor(n_estimators=50, random_state=42)
                elif model_name == 'anomaly_detector':
                    from sklearn.ensemble import IsolationForest
                    return IsolationForest(contamination=0.1, random_state=42)
        except Exception as e:
            self.logger.error(f"Error loading/creating model {model_name}: {e}")
            return None
            
    def load_or_create_scaler(self):
        """Load existing scaler or create new one"""
        scaler_path = "models/feature_scaler.pkl"
        try:
            if os.path.exists(scaler_path):
                return joblib.load(scaler_path)
            else:
                return StandardScaler()
        except Exception as e:
            self.logger.error(f"Error loading/creating scaler: {e}")
            return StandardScaler()
            
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            client.subscribe(self.config["mqtt"]["topics"]["energy_data"])
            client.subscribe("smarthome/status")
            client.subscribe("sensors/+/occupancy")
            client.subscribe("weather/current")
            self.logger.info("MQTT connected and subscribed to topics")
        else:
            self.logger.error(f"MQTT connection failed with code {rc}")
            
    def on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            topic = msg.topic
            message = json.loads(msg.payload.decode())
            
            if topic == self.config["mqtt"]["topics"]["energy_data"]:
                self.process_energy_reading(message)
            elif topic == "smarthome/status":
                self.process_device_status(message)
            elif "occupancy" in topic:
                self.process_occupancy_data(message)
            elif topic == "weather/current":
                self.process_weather_data(message)
                
        except Exception as e:
            self.logger.error(f"MQTT message processing error: {e}")
            
    def process_energy_reading(self, data):
        """Process energy consumption reading"""
        try:
            timestamp = data.get('timestamp', datetime.now().isoformat())
            device_id = data.get('device_id')
            power = data.get('power_consumption', 0.0)
            voltage = data.get('voltage', 0.0)
            current = data.get('current', 0.0)
            
            # Store in database
            self.cursor.execute("""
                INSERT INTO energy_readings 
                (timestamp, device_id, power_consumption, voltage, current)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, device_id, power, voltage, current))
            
            self.conn.commit()
            
            # Update current readings
            self.current_readings[device_id] = {
                'timestamp': timestamp,
                'power': power,
                'voltage': voltage,
                'current': current
            }
            
            # Add to consumption history
            self.consumption_history.append({
                'timestamp': timestamp,
                'device_id': device_id,
                'power': power
            })
            
            # Check for anomalies
            self.detect_energy_anomalies(device_id, power)
            
            # Trigger optimization if needed
            if self.auto_optimization_enabled:
                self.check_optimization_triggers()
                
        except Exception as e:
            self.logger.error(f"Error processing energy reading: {e}")
            
    def process_device_status(self, data):
        """Process device status updates"""
        try:
            devices = data.get('devices', {})
            for device_type, device_list in devices.items():
                if isinstance(device_list, list):
                    for i, status in enumerate(device_list):
                        device_id = f"{device_type}_{i}"
                        self.update_device_status(device_id, status)
                        
        except Exception as e:
            self.logger.error(f"Error processing device status: {e}")
            
    def process_occupancy_data(self, data):
        """Process occupancy sensor data"""
        try:
            room = data.get('room')
            occupancy_count = data.get('occupancy_count', 0)
            motion_detected = data.get('motion_detected', False)
            temperature = data.get('temperature', 0.0)
            
            self.occupancy_sensors[room] = {
                'occupancy_count': occupancy_count,
                'motion_detected': motion_detected,
                'temperature': temperature,
                'timestamp': datetime.now()
            }
            
            # Store in database
            self.cursor.execute("""
                INSERT INTO occupancy_data 
                (room, occupancy_count, motion_detected, temperature)
                VALUES (?, ?, ?, ?)
            """, (room, occupancy_count, motion_detected, temperature))
            
            self.conn.commit()
            
            # Trigger occupancy-based optimization
            self.optimize_based_on_occupancy(room)
            
        except Exception as e:
            self.logger.error(f"Error processing occupancy data: {e}")
            
    def process_weather_data(self, data):
        """Process weather data for optimization"""
        try:
            self.weather_data = {
                'temperature': data.get('temperature', 0.0),
                'humidity': data.get('humidity', 0.0),
                'cloud_cover': data.get('cloud_cover', 0.0),
                'wind_speed': data.get('wind_speed', 0.0),
                'timestamp': datetime.now()
            }
            
            # Optimize based on weather conditions
            self.optimize_based_on_weather()
            
        except Exception as e:
            self.logger.error(f"Error processing weather data: {e}")
            
    def detect_energy_anomalies(self, device_id, current_power):
        """Detect energy consumption anomalies using ML"""
        try:
            if self.ml_models['anomaly_detector'] is None:
                return
                
            # Get historical data for this device
            self.cursor.execute("""
                SELECT power_consumption FROM energy_readings 
                WHERE device_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 100
            """, (device_id,))
            
            historical_data = [row[0] for row in self.cursor.fetchall()]
            
            if len(historical_data) < 10:
                return  # Not enough data for anomaly detection
                
            # Prepare features
            features = np.array(historical_data).reshape(-1, 1)
            
            # Detect anomaly
            anomaly_score = self.ml_models['anomaly_detector'].decision_function([[current_power]])
            is_anomaly = self.ml_models['anomaly_detector'].predict([[current_power]])[0] == -1
            
            if is_anomaly:
                self.handle_energy_anomaly(device_id, current_power, anomaly_score[0])
                
        except Exception as e:
            self.logger.error(f"Anomaly detection error: {e}")
            
    def handle_energy_anomaly(self, device_id, power, anomaly_score):
        """Handle detected energy anomaly"""
        try:
            self.logger.warning(f"Energy anomaly detected: {device_id} consuming {power}W (score: {anomaly_score})")
            
            # Send alert
            alert_data = {
                'type': 'ENERGY_ANOMALY',
                'device_id': device_id,
                'power_consumption': power,
                'anomaly_score': float(anomaly_score),
                'timestamp': datetime.now().isoformat(),
                'severity': 'medium' if abs(anomaly_score) < 0.5 else 'high'
            }
            
            self.mqtt_client.publish(
                self.config["mqtt"]["topics"]["alerts"],
                json.dumps(alert_data)
            )
            
            # Automatic action for severe anomalies
            if abs(anomaly_score) > 0.7:
                self.emergency_device_shutdown(device_id)
                
        except Exception as e:
            self.logger.error(f"Error handling energy anomaly: {e}")
            
    def predict_energy_consumption(self, hours_ahead=24):
        """Predict energy consumption for the next N hours"""
        try:
            if self.ml_models['consumption_predictor'] is None:
                return None
                
            # Get historical data
            end_time = datetime.now()
            start_time = end_time - timedelta(days=30)
            
            self.cursor.execute("""
                SELECT timestamp, power_consumption FROM energy_readings 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            """, (start_time.isoformat(), end_time.isoformat()))
            
            data = self.cursor.fetchall()
            if len(data) < 100:
                return None
                
            # Prepare features
            df = pd.DataFrame(data, columns=['timestamp', 'power'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            
            # Resample to hourly data
            hourly_data = df.resample('H').mean()
            
            # Create features
            features = self.create_prediction_features(hourly_data)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make predictions
            predictions = self.ml_models['consumption_predictor'].predict(features_scaled[-hours_ahead:])
            
            # Create prediction timestamps
            prediction_times = [end_time + timedelta(hours=i+1) for i in range(hours_ahead)]
            
            return list(zip(prediction_times, predictions))
            
        except Exception as e:
            self.logger.error(f"Energy prediction error: {e}")
            return None
            
    def create_prediction_features(self, df):
        """Create features for energy prediction"""
        try:
            features = []
            
            for i in range(len(df)):
                feature_row = []
                
                # Time-based features
                timestamp = df.index[i]
                feature_row.extend([
                    timestamp.hour,
                    timestamp.day,
                    timestamp.month,
                    timestamp.weekday(),
                    1 if timestamp.weekday() >= 5 else 0  # Weekend flag
                ])
                
                # Historical consumption features
                if i >= 24:  # Previous day same hour
                    feature_row.append(df.iloc[i-24]['power'])
                else:
                    feature_row.append(0)
                    
                if i >= 7*24:  # Previous week same hour
                    feature_row.append(df.iloc[i-7*24]['power'])
                else:
                    feature_row.append(0)
                    
                # Moving averages
                if i >= 6:
                    feature_row.append(df.iloc[i-6:i]['power'].mean())  # 6-hour average
                else:
                    feature_row.append(df.iloc[:i+1]['power'].mean())
                    
                # Weather features (if available)
                if self.weather_data:
                    feature_row.extend([
                        self.weather_data.get('temperature', 20),
                        self.weather_data.get('humidity', 50),
                        self.weather_data.get('cloud_cover', 50)
                    ])
                else:
                    feature_row.extend([20, 50, 50])  # Default values
                    
                features.append(feature_row)
                
            return np.array(features)
            
        except Exception as e:
            self.logger.error(f"Feature creation error: {e}")
            return np.array([[]])
            
    def optimize_based_on_occupancy(self, room):
        """Optimize energy usage based on occupancy"""
        try:
            occupancy = self.occupancy_sensors.get(room, {})
            is_occupied = occupancy.get('motion_detected', False) or occupancy.get('occupancy_count', 0) > 0
            
            room_devices = self.get_devices_in_room(room)
            
            for device in room_devices:
                if device['id'].endswith('_light'):
                    # Auto turn off lights in unoccupied rooms
                    if not is_occupied and not self.is_peak_hour():
                        self.control_device(device['id'], False)
                        self.log_optimization('occupancy_based', device['id'], 'light_auto_off')
                        
                elif device['id'].endswith('_fan'):
                    # Auto control fans based on occupancy and temperature
                    if is_occupied:
                        room_temp = occupancy.get('temperature', 25)
                        if room_temp > 28:
                            self.control_device(device['id'], True)
                        elif room_temp < 22:
                            self.control_device(device['id'], False)
                    else:
                        # Turn off fan if room unoccupied for > 10 minutes
                        last_activity = occupancy.get('timestamp', datetime.now())
                        if (datetime.now() - last_activity).seconds > 600:
                            self.control_device(device['id'], False)
                            self.log_optimization('occupancy_based', device['id'], 'fan_auto_off')
                            
        except Exception as e:
            self.logger.error(f"Occupancy-based optimization error: {e}")
            
    def optimize_based_on_weather(self):
        """Optimize energy usage based on weather conditions"""
        try:
            if not self.weather_data:
                return
                
            outdoor_temp = self.weather_data.get('temperature', 25)
            humidity = self.weather_data.get('humidity', 50)
            cloud_cover = self.weather_data.get('cloud_cover', 50)
            
            # Natural lighting optimization
            if cloud_cover < 30 and self.is_daytime():
                # Good natural light available
                for device in self.config['devices']['lights']:
                    room = device['room']
                    if not self.is_room_occupied(room):
                        self.control_device(device['id'], False)
                        self.log_optimization('weather_based', device['id'], 'natural_light_available')
                        
            # Temperature-based fan/AC optimization
            if outdoor_temp < 20:
                # Cool weather - reduce fan usage
                for device in self.config['devices']['fans']:
                    room = device['room']
                    if not self.is_room_occupied(room):
                        self.control_device(device['id'], False)
                        self.log_optimization('weather_based', device['id'], 'cool_weather_optimization')
                        
            elif outdoor_temp > 35:
                # Hot weather - predictive cooling
                for device in self.config['devices']['appliances']:
                    if 'air_conditioner' in device['id']:
                        # Pre-cool before peak hours
                        if not self.is_peak_hour() and self.is_room_occupied(device['room']):
                            self.control_device(device['id'], True)
                            self.log_optimization('weather_based', device['id'], 'predictive_cooling')
                            
        except Exception as e:
            self.logger.error(f"Weather-based optimization error: {e}")
            
    def optimize_load_balancing(self):
        """Optimize load balancing to prevent peak demand"""
        try:
            current_total_load = sum(
                reading.get('power', 0) for reading in self.current_readings.values()
            )
            
            max_safe_load = self.config['thresholds']['high_usage_alert']
            
            if current_total_load > max_safe_load * 0.8:
                # Approaching high usage threshold
                self.logger.info(f"High load detected: {current_total_load}W, initiating load balancing")
                
                # Get non-essential devices that can be temporarily turned off
                non_essential_devices = self.get_non_essential_devices()
                
                # Sort by priority (higher priority = less essential)
                non_essential_devices.sort(key=lambda x: x['priority'], reverse=True)
                
                load_to_reduce = current_total_load - (max_safe_load * 0.7)
                reduced_load = 0
                
                for device in non_essential_devices:
                    if reduced_load >= load_to_reduce:
                        break
                        
                    device_power = device.get('power_rating', 0)
                    if self.is_device_on(device['id']):
                        self.control_device(device['id'], False)
                        reduced_load += device_power
                        self.log_optimization('load_balancing', device['id'], f'reduced_load_{device_power}W')
                        
                        # Schedule to turn back on after peak
                        self.schedule_device_restoration(device['id'], 30)  # 30 minutes
                        
        except Exception as e:
            self.logger.error(f"Load balancing optimization error: {e}")
            
    def optimize_cost_efficiency(self):
        """Optimize for cost efficiency based on time-of-use tariffs"""
        try:
            current_hour = datetime.now().hour
            is_peak = self.is_peak_hour()
            is_off_peak = self.is_off_peak_hour()
            
            if is_peak:
                # Peak hours - minimize usage
                self.logger.info("Peak hours detected - optimizing for cost efficiency")
                
                # Defer non-essential appliances
                for device in self.config['devices']['appliances']:
                    if not device.get('always_on', False) and device['priority'] >= 3:
                        if self.is_device_on(device['id']):
                            # Check if it can be deferred
                            if self.can_defer_device(device['id']):
                                self.control_device(device['id'], False)
                                self.schedule_device_restoration(device['id'], self.get_off_peak_delay())
                                self.log_optimization('cost_efficiency', device['id'], 'deferred_to_off_peak')
                                
            elif is_off_peak:
                # Off-peak hours - run deferred appliances
                self.logger.info("Off-peak hours detected - running deferred appliances")
                self.run_deferred_appliances()
                
        except Exception as e:
            self.logger.error(f"Cost efficiency optimization error: {e}")
            
    def smart_scheduling(self):
        """Implement smart scheduling based on predictions and patterns"""
        try:
            # Get energy predictions
            predictions = self.predict_energy_consumption(24)
            if not predictions:
                return
                
            # Find optimal time slots for high-power appliances
            high_power_devices = [
                device for device in self.config['devices']['appliances']
                if device['power_rating'] > 1000 and not device.get('always_on', False)
            ]
            
            for device in high_power_devices:
                optimal_time = self.find_optimal_time_slot(
                    predictions,
                    device['power_rating'],
                    device.get('duration', 2)  # Default 2 hours
                )
                
                if optimal_time:
                    self.schedule_device_operation(device['id'], optimal_time)
                    self.log_optimization('smart_scheduling', device['id'], f'scheduled_for_{optimal_time}')
                    
        except Exception as e:
            self.logger.error(f"Smart scheduling error: {e}")
            
    def find_optimal_time_slot(self, predictions, device_power, duration_hours):
        """Find optimal time slot for device operation"""
        try:
            min_cost = float('inf')
            optimal_time = None
            
            for i in range(len(predictions) - duration_hours):
                time_slot = predictions[i:i+duration_hours]
                
                # Calculate cost for this time slot
                total_cost = 0
                for timestamp, predicted_load in time_slot:
                    hourly_rate = self.get_hourly_rate(timestamp.hour)
                    total_cost += (predicted_load + device_power) * hourly_rate / 1000  # Convert W to kW
                    
                if total_cost < min_cost:
                    min_cost = total_cost
                    optimal_time = time_slot[0][0]
                    
            return optimal_time
            
        except Exception as e:
            self.logger.error(f"Error finding optimal time slot: {e}")
            return None
            
    def control_device(self, device_id, state):
        """Control device state"""
        try:
            command_data = {
                'device_id': device_id,
                'command': 'on' if state else 'off',
                'timestamp': datetime.now().isoformat(),
                'source': 'energy_management'
            }
            
            self.mqtt_client.publish(
                self.config["mqtt"]["topics"]["device_control"],
                json.dumps(command_data)
            )
            
            self.logger.info(f"Device control: {device_id} -> {'ON' if state else 'OFF'}")
            
        except Exception as e:
            self.logger.error(f"Device control error: {e}")
            
    def log_optimization(self, optimization_type, device_id, description):
        """Log optimization action"""
        try:
            self.cursor.execute("""
                INSERT INTO optimization_logs (optimization_type, devices_affected, estimated_savings)
                VALUES (?, ?, ?)
            """, (optimization_type, device_id, 0.0))  # TODO: Calculate actual savings
            
            self.conn.commit()
            
            self.logger.info(f"Optimization logged: {optimization_type} - {device_id} - {description}")
            
        except Exception as e:
            self.logger.error(f"Optimization logging error: {e}")
            
    def generate_energy_report(self, days=7):
        """Generate comprehensive energy report"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get consumption data
            self.cursor.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    SUM(power_consumption) as total_consumption,
                    AVG(power_consumption) as avg_consumption,
                    MAX(power_consumption) as peak_consumption,
                    COUNT(*) as reading_count
                FROM energy_readings 
                WHERE DATE(timestamp) BETWEEN ? AND ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (start_date, end_date))
            
            consumption_data = self.cursor.fetchall()
            
            # Calculate costs and efficiency
            report = {
                'period': f"{start_date} to {end_date}",
                'total_consumption_kwh': 0,
                'total_cost': 0,
                'average_daily_consumption': 0,
                'peak_consumption': 0,
                'efficiency_score': 0,
                'cost_savings': 0,
                'carbon_footprint': 0,
                'daily_breakdown': []
            }
            
            for date, total, avg, peak, count in consumption_data:
                daily_kwh = total / 1000  # Convert W to kWh
                daily_cost = self.calculate_daily_cost(date, total)
                
                report['daily_breakdown'].append({
                    'date': date,
                    'consumption_kwh': daily_kwh,
                    'cost': daily_cost,
                    'peak_power': peak,
                    'efficiency_score': self.calculate_efficiency_score(total, avg)
                })
                
                report['total_consumption_kwh'] += daily_kwh
                report['total_cost'] += daily_cost
                report['peak_consumption'] = max(report['peak_consumption'], peak)
                
            # Calculate averages
            if len(consumption_data) > 0:
                report['average_daily_consumption'] = report['total_consumption_kwh'] / len(consumption_data)
                report['efficiency_score'] = sum(
                    day['efficiency_score'] for day in report['daily_breakdown']
                ) / len(report['daily_breakdown'])
                
            # Calculate carbon footprint (assuming 0.82 kg CO2 per kWh)
            report['carbon_footprint'] = report['total_consumption_kwh'] * 0.82
            
            return report
            
        except Exception as e:
            self.logger.error(f"Report generation error: {e}")
            return None
            
    def calculate_daily_cost(self, date, total_consumption_w):
        """Calculate daily electricity cost"""
        try:
            # This is a simplified calculation
            # In reality, you'd need to account for time-of-use rates
            daily_kwh = total_consumption_w / 1000
            average_rate = self.config['tariff']['normal_rate']
            return daily_kwh * average_rate / 100  # Convert paise to rupees
            
        except Exception as e:
            self.logger.error(f"Cost calculation error: {e}")
            return 0.0
            
    def calculate_efficiency_score(self, total_consumption, avg_consumption):
        """Calculate efficiency score (0-100)"""
        try:
            # This is a simplified efficiency calculation
            # Based on how close actual consumption is to optimal
            target_consumption = 20000  # 20kW daily target
            efficiency = max(0, 100 - abs(total_consumption - target_consumption) / target_consumption * 100)
            return min(100, efficiency)
            
        except Exception as e:
            self.logger.error(f"Efficiency calculation error: {e}")
            return 50.0
            
    # Utility methods
    def is_peak_hour(self):
        """Check if current time is peak hour"""
        current_time = datetime.now().time()
        for peak_period in self.config['tariff']['peak_hours']:
            start = datetime.strptime(peak_period['start'], '%H:%M').time()
            end = datetime.strptime(peak_period['end'], '%H:%M').time()
            if start <= current_time <= end:
                return True
        return False
        
    def is_off_peak_hour(self):
        """Check if current time is off-peak hour"""
        current_time = datetime.now().time()
        for off_peak_period in self.config['tariff']['off_peak_hours']:
            start = datetime.strptime(off_peak_period['start'], '%H:%M').time()
            end = datetime.strptime(off_peak_period['end'], '%H:%M').time()
            if start <= current_time or current_time <= end:  # Handle midnight crossing
                return True
        return False
        
    def is_daytime(self):
        """Check if it's daytime (6 AM to 6 PM)"""
        current_hour = datetime.now().hour
        return 6 <= current_hour <= 18
        
    def get_devices_in_room(self, room):
        """Get all devices in a specific room"""
        devices = []
        for device_type in self.config['devices'].values():
            for device in device_type:
                if device.get('room') == room:
                    devices.append(device)
        return devices
        
    def is_room_occupied(self, room):
        """Check if room is currently occupied"""
        occupancy = self.occupancy_sensors.get(room, {})
        return occupancy.get('motion_detected', False) or occupancy.get('occupancy_count', 0) > 0
        
    def get_hourly_rate(self, hour):
        """Get electricity rate for specific hour"""
        if self.is_peak_hour():
            return self.config['tariff']['peak_rate']
        elif self.is_off_peak_hour():
            return self.config['tariff']['off_peak_rate']
        else:
            return self.config['tariff']['normal_rate']
            
    def check_optimization_triggers(self):
        """Check if optimization should be triggered"""
        total_power = sum(reading.get('power', 0) for reading in self.current_readings.values())
        
        if total_power > self.config['thresholds']['high_usage_alert']:
            self.optimize_load_balancing()
            
        if self.is_peak_hour():
            self.optimize_cost_efficiency()
            
    def run_optimization_cycle(self):
        """Run complete optimization cycle"""
        try:
            self.logger.info("Starting optimization cycle")
            
            if self.auto_optimization_enabled:
                self.optimize_load_balancing()
                self.optimize_cost_efficiency()
                self.smart_scheduling()
                
            self.logger.info("Optimization cycle completed")
            
        except Exception as e:
            self.logger.error(f"Optimization cycle error: {e}")
            
    def run(self):
        """Main energy management system loop"""
        try:
            self.logger.info("Energy Management System started")
            
            # Schedule optimization tasks
            schedule.every(5).minutes.do(self.run_optimization_cycle)
            schedule.every().hour.do(self.generate_hourly_summary)
            schedule.every().day.at("00:00").do(self.generate_daily_report)
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("Energy Management System shutdown requested")
        except Exception as e:
            self.logger.error(f"Energy Management System error: {e}")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.conn.close()
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            self.logger.info("Energy Management System cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

def main():
    energy_system = EnergyManagementSystem()
    energy_system.run()

if __name__ == "__main__":
    main()