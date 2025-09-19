#include <DHT.h>
#include <LiquidCrystal.h>

#define DHTPIN 2         // Pin where the DHT11 sensor is connected

// Initialize DHT sensor
DHT dht(DHTPIN, DHT11);

const int rs = 3, en = 4, d4 = 8, d5 = 5, d6 = 6, d7 = 7;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);


void setup() {
  pinMode(9,OUTPUT);
  pinMode(10,OUTPUT);
  Serial.begin(9600);
  Serial.println("DHT11 Temperature and Humidity Sensor");
  lcd.begin(16, 2);
  // Initialize DHT sensor
  dht.begin();
}

void loop() {
  // Wait a few seconds between measurements
  delay(2000);

  // Read temperature and humidity from the DHT sensor
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Check if any reads failed and exit early
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  if(temperature >=34 )
  {
for(int i = 0;i<100;i++){
   temperature = dht.readTemperature();
   lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  Serial.print("temperature: ");
  Serial.print(temperature);
  lcd.print(temperature);
  lcd.setCursor(0, 1);
  Serial.print(" humidity: ");
  Serial.print(humidity);
  lcd.print("Humidity: ");
  lcd.print(humidity);
  Serial.println(" %");
    digitalWrite(9,1);
    delay(500);
    digitalWrite(9,0);
    delay(500);
    if(temperature<34){
    break;      
    }
}
      } 
  else {
    digitalWrite(9,0);
  } 
if(humidity >= 95.50){
  digitalWrite(10,1);
}
else{
  digitalWrite(10,0);  
}

  // Print temperature and humidity values
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  Serial.print("temperature: ");
  Serial.print(temperature);
  lcd.print(temperature);
  lcd.setCursor(0, 1);
  Serial.print(" humidity: ");
  Serial.print(humidity);
  lcd.print("Humidity: ");
  lcd.print(humidity);
  Serial.println(" %");
}