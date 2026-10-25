#include <DHT.h>
#include <LiquidCrystal.h>

#define DHTPIN 2         // Pin where the DHT11 sensor is connected
#define BUZZER_PIN 9     // Blinks/beeps while temperature is too high
#define HUMIDITY_PIN 10  // Turns on while humidity is too high

const float TEMP_ALARM_C = 34.0;
const float HUMIDITY_ALARM = 95.5;

// Initialize DHT sensor
DHT dht(DHTPIN, DHT11);

const int rs = 3, en = 4, d4 = 8, d5 = 5, d6 = 6, d7 = 7;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// Show readings on the LCD and serial monitor
void showReadings(float temperature, float humidity) {
  lcd.clear();  // Avoid leftover characters when values get shorter
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(temperature);
  lcd.print((char)223);  // Degree symbol
  lcd.print("C");
  lcd.setCursor(0, 1);
  lcd.print("Humidity: ");
  lcd.print(humidity);
  lcd.print("%");

  Serial.print("temperature: ");
  Serial.print(temperature);
  Serial.print(" humidity: ");
  Serial.print(humidity);
  Serial.println(" %");
}

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(HUMIDITY_PIN, OUTPUT);
  Serial.begin(9600);
  Serial.println("DHT11 Temperature and Humidity Sensor");
  lcd.begin(16, 2);
  // Initialize DHT sensor
  dht.begin();
}

void loop() {
  // Read temperature and humidity from the DHT sensor
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Check if any reads failed; keep outputs off rather than acting on bad data
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    digitalWrite(BUZZER_PIN, LOW);
    lcd.clear();
    lcd.print("Sensor error");
    delay(2000);
    return;
  }

  showReadings(temperature, humidity);

  // Humidity output is re-evaluated on every reading, including while the
  // temperature alarm is active
  digitalWrite(HUMIDITY_PIN, humidity >= HUMIDITY_ALARM ? HIGH : LOW);

  if (temperature >= TEMP_ALARM_C) {
    // One blink cycle per reading; the alarm stops as soon as it cools down
    digitalWrite(BUZZER_PIN, HIGH);
    delay(500);
    digitalWrite(BUZZER_PIN, LOW);
    delay(500);
  } else {
    digitalWrite(BUZZER_PIN, LOW);
    delay(2000);  // DHT11 needs time between measurements
  }
}
