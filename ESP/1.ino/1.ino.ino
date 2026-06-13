/*
 * ═══════════════════════════════════════════════════════════════════
 *  SHADOW GARDEN — Smart Agriculture IoT System
 *  ESP8266 #1 (NodeMCU) — Temperature, Humidity & Soil Moisture
 * ═══════════════════════════════════════════════════════════════════
 *
 *  Hardware Connections:
 *  ┌────────────────────┬────────────────┐
 *  │  DHT11 Sensor      │  NodeMCU Pin   │
 *  ├────────────────────┼────────────────┤
 *  │  DATA              │  D4 (GPIO 2)   │
 *  │  VCC               │  3.3V          │
 *  │  GND               │  GND           │
 *  └────────────────────┴────────────────┘
 *  ┌────────────────────┬────────────────┐
 *  │  Soil Moisture     │  NodeMCU Pin   │
 *  ├────────────────────┼────────────────┤
 *  │  AO (Analog Out)   │  A0            │
 *  │  VCC               │  3.3V          │
 *  │  GND               │  GND           │
 *  │  DO (Digital Out)  │  Not Used      │
 *  └────────────────────┴────────────────┘
 *
 *  Sends HTTP POST every 10 seconds to:
 *    http://<SERVER_IP>:8000/api/iot/sensor-data
 *
 *  Payload:
 *    { "device": "esp1", "temperature": 29, "humidity": 70, "moisture": 45 }
 *
 *  Required Libraries (install via Arduino Library Manager):
 *    - ESP8266WiFi        (built-in with ESP8266 board package)
 *    - ESP8266HTTPClient  (built-in with ESP8266 board package)
 *    - ArduinoJson        (by Benoit Blanchon, v6 or v7)
 *    - DHT sensor library (by Adafruit)
 *    - Adafruit Unified Sensor (dependency of DHT library)
 *
 *  Board Settings in Arduino IDE:
 *    Board:  "NodeMCU 1.0 (ESP-12E Module)"
 *    Upload Speed: 115200
 *    Flash Size: 4MB (FS:2MB OTA:~1019KB)
 *
 * ═══════════════════════════════════════════════════════════════════
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// ╔═══════════════════════════════════════════════════════════╗
// ║  CONFIGURATION — Change these values for your network    ║
// ╚═══════════════════════════════════════════════════════════╝

const char* WIFI_SSID     = "Sathvik";
const char* WIFI_PASSWORD = "sathvik@57";
const char* SERVER_URL    = "http://10.24.102.99:8000/api/iot/sensor-data";

// ╔═══════════════════════════════════════════════════════════╗
// ║  SENSOR PIN DEFINITIONS                                  ║
// ╚═══════════════════════════════════════════════════════════╝

#define DHTPIN    2        // D4 on NodeMCU = GPIO 2
#define DHTTYPE   DHT11    // Change to DHT22 if using AM2302
#define SOIL_PIN  A0       // Analog pin for soil moisture sensor

// ╔═══════════════════════════════════════════════════════════╗
// ║  TIMING                                                  ║
// ╚═══════════════════════════════════════════════════════════╝

const unsigned long SEND_INTERVAL = 10000;  // Send data every 10 seconds
unsigned long lastSendTime = 0;

// ╔═══════════════════════════════════════════════════════════╗
// ║  SOIL MOISTURE CALIBRATION                               ║
// ║                                                          ║
// ║  These values depend on YOUR specific sensor.            ║
// ║  To calibrate:                                           ║
// ║    1. Read A0 with sensor in DRY AIR    → that's DRY_VAL ║
// ║    2. Read A0 with sensor in WATER      → that's WET_VAL ║
// ║    3. Update the values below.                           ║
// ║                                                          ║
// ║  Typical values for capacitive sensor:                   ║
// ║    DRY ≈ 1024, WET ≈ 300                                ║
// ║  Typical values for resistive sensor:                    ║
// ║    DRY ≈ 1024, WET ≈ 200                                ║
// ╚═══════════════════════════════════════════════════════════╝

const int SOIL_DRY_VALUE = 1024;   // Analog reading in completely dry air
const int SOIL_WET_VALUE = 200;    // Analog reading in water

// Initialize DHT sensor
DHT dht(DHTPIN, DHTTYPE);

// WiFi client for HTTP requests
WiFiClient wifiClient;

// ═══════════════════════════════════════════════════════════════
//  SETUP — Runs once when the board powers on or resets
// ═══════════════════════════════════════════════════════════════

void setup() {
  // Start serial communication for debugging
  Serial.begin(115200);
  delay(100);

  Serial.println();
  Serial.println("═══════════════════════════════════════════");
  Serial.println("  SHADOW GARDEN — ESP1 Booting...");
  Serial.println("  Sensors: DHT11 + Soil Moisture");
  Serial.println("═══════════════════════════════════════════");

  // Initialize the DHT11 sensor
  dht.begin();
  Serial.println("[OK] DHT11 sensor initialized on GPIO 2 (D4)");

  // A0 is input by default, no pinMode needed for analog read
  Serial.println("[OK] Soil moisture sensor on A0");

  // Connect to WiFi
  connectToWiFi();
}

// ═══════════════════════════════════════════════════════════════
//  LOOP — Runs continuously after setup()
// ═══════════════════════════════════════════════════════════════

void loop() {
  // ── Step 1: Ensure WiFi is connected ──
  // If WiFi drops mid-operation, reconnect automatically
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WARN] WiFi disconnected! Attempting reconnect...");
    connectToWiFi();
  }

  // ── Step 2: Check if it's time to send data ──
  unsigned long currentTime = millis();
  if (currentTime - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = currentTime;

    // ── Step 3: Read all sensors ──
    float temperature = readTemperature();
    float humidity    = readHumidity();
    int   moisture    = readSoilMoisture();

    // ── Step 4: Print readings to Serial Monitor ──
    Serial.println("───────────────────────────────────────────");
    Serial.println("  📡 ESP1 Sensor Readings:");
    Serial.print("    🌡️  Temperature : ");
    Serial.print(temperature);
    Serial.println(" °C");
    Serial.print("    💧 Humidity    : ");
    Serial.print(humidity);
    Serial.println(" %");
    Serial.print("    🌱 Soil Moist. : ");
    Serial.print(moisture);
    Serial.println(" %");

    // ── Step 5: Validate sensor readings ──
    // DHT11 can return NaN if it fails to read
    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("[ERROR] DHT11 read failed! Skipping this cycle.");
      return;  // Skip sending bad data
    }

    // ── Step 6: Build JSON and send HTTP POST ──
    sendSensorData(temperature, humidity, moisture);
  }
}

// ═══════════════════════════════════════════════════════════════
//  WiFi CONNECTION
// ═══════════════════════════════════════════════════════════════

void connectToWiFi() {
  Serial.print("[WiFi] Connecting to: ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);            // Station mode (client)
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    
    // Print WiFi status code every 5 attempts for debugging
    // 0=IDLE, 1=NO_SSID_AVAIL, 2=SCAN_COMPLETED, 3=CONNECTED,
    // 4=CONNECT_FAILED (wrong password), 5=CONNECTION_LOST, 6=DISCONNECTED
    if (attempts % 5 == 0 && attempts > 0) {
      Serial.print(" [status=");
      Serial.print(WiFi.status());
      Serial.print("] ");
    }
    attempts++;

    // After 30 seconds (60 * 500ms), restart the ESP
    if (attempts > 60) {
      Serial.println();
      Serial.println("[FATAL] WiFi connection failed after 30s. Restarting...");
      ESP.restart();
    }
  }

  Serial.println();
  Serial.println("[OK] WiFi connected!");
  Serial.print("     IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("     Signal (RSSI): ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
}

// ═══════════════════════════════════════════════════════════════
//  SENSOR READING FUNCTIONS
// ═══════════════════════════════════════════════════════════════

/**
 * Read temperature from DHT11 in Celsius.
 * Returns NaN if the sensor fails.
 */
float readTemperature() {
  float t = dht.readTemperature();  // Celsius by default
  return t;
}

/**
 * Read relative humidity from DHT11 as percentage.
 * Returns NaN if the sensor fails.
 */
float readHumidity() {
  float h = dht.readHumidity();
  return h;
}

/**
 * Read soil moisture from analog pin A0 and convert to percentage.
 *
 * How it works:
 *   - The soil moisture sensor outputs a voltage proportional to moisture.
 *   - ESP8266 A0 reads 0-1024 (10-bit ADC).
 *   - DRY soil = HIGH analog value (near 1024).
 *   - WET soil = LOW analog value (near 200-300).
 *   - We INVERT and MAP this to 0-100% where:
 *       0%   = completely dry
 *       100% = submerged in water
 */
int readSoilMoisture() {
  int rawValue = analogRead(SOIL_PIN);

  Serial.print("    [DEBUG] Soil raw A0: ");
  Serial.println(rawValue);

  // Map the raw value to percentage (inverted: high raw = dry = 0%)
  int percentage = map(rawValue, SOIL_DRY_VALUE, SOIL_WET_VALUE, 0, 100);

  // Clamp to 0-100 range to prevent overshoot
  percentage = constrain(percentage, 0, 100);

  return percentage;
}

// ═══════════════════════════════════════════════════════════════
//  HTTP POST — Send sensor data to the backend server
// ═══════════════════════════════════════════════════════════════

/**
 * Constructs a JSON payload and sends it via HTTP POST to the
 * FastAPI backend at /api/iot/sensor-data.
 *
 * Payload format:
 * {
 *   "device": "esp1",
 *   "temperature": 29.5,
 *   "humidity": 70.2,
 *   "moisture": 45
 * }
 */
void sendSensorData(float temperature, float humidity, int moisture) {
  // ── Create JSON document ──
  // StaticJsonDocument allocates memory on the stack (fast, no fragmentation)
  // 256 bytes is more than enough for our small payload
  StaticJsonDocument<256> jsonDoc;

  jsonDoc["device"]      = "esp1";
  jsonDoc["temperature"] = round(temperature * 10.0) / 10.0;  // 1 decimal place
  jsonDoc["humidity"]    = round(humidity * 10.0) / 10.0;      // 1 decimal place
  jsonDoc["moisture"]    = moisture;                            // integer percentage

  // Serialize JSON to a string
  String jsonPayload;
  serializeJson(jsonDoc, jsonPayload);

  Serial.print("    📤 Sending POST: ");
  Serial.println(jsonPayload);

  // ── Send HTTP POST request ──
  HTTPClient http;
  http.begin(wifiClient, SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  // Send the POST request and capture the response code
  int httpResponseCode = http.POST(jsonPayload);

  // ── Handle the response ──
  if (httpResponseCode > 0) {
    // Successful HTTP response (could be 200, 201, 400, 500, etc.)
    String response = http.getString();
    Serial.print("    ✅ Server Response [");
    Serial.print(httpResponseCode);
    Serial.print("]: ");
    Serial.println(response);
  } else {
    // Negative value = connection error (not an HTTP error)
    Serial.print("    ❌ HTTP POST failed! Error: ");
    Serial.println(http.errorToString(httpResponseCode));
    Serial.println("       Check: Is the server running? Is the IP correct?");
    Serial.print("       Server URL: ");
    Serial.println(SERVER_URL);
  }

  // Always close the connection to free resources
  http.end();
  Serial.println("───────────────────────────────────────────");
}
