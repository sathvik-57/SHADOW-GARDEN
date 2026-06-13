/*
 * ═══════════════════════════════════════════════════════════════════
 *  SHADOW GARDEN — Smart Agriculture IoT System
 *  ESP8266 #2 (NodeMCU) — Air Quality Monitoring (MQ-135)
 * ═══════════════════════════════════════════════════════════════════
 *
 *  Hardware Connections:
 *  ┌────────────────────┬────────────────┐
 *  │  MQ-135 Sensor     │  NodeMCU Pin   │
 *  ├────────────────────┼────────────────┤
 *  │  AO (Analog Out)   │  A0            │
 *  │  VCC               │  VIN (5V)      │
 *  │  GND               │  GND           │
 *  │  DO (Digital Out)  │  Not Used      │
 *  └────────────────────┴────────────────┘
 *
 *  ⚠️  IMPORTANT: The MQ-135 heater requires 5V to function.
 *     Connect VCC to the VIN pin (which passes through USB 5V),
 *     NOT to 3.3V — it will not heat up properly on 3.3V.
 *
 *  ⚠️  WARM-UP TIME: The MQ-135 needs 2-3 minutes of pre-heating
 *     before its readings stabilize. Initial readings will be
 *     erratic — this is completely normal.
 *
 *  Sends HTTP POST every 10 seconds to:
 *    http://<SERVER_IP>:8000/api/iot/sensor-data
 *
 *  Payload:
 *    { "device": "esp2", "air_quality": 320 }
 *
 *  Required Libraries (install via Arduino Library Manager):
 *    - ESP8266WiFi        (built-in with ESP8266 board package)
 *    - ESP8266HTTPClient  (built-in with ESP8266 board package)
 *    - ArduinoJson        (by Benoit Blanchon, v6 or v7)
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

// ╔═══════════════════════════════════════════════════════════╗
// ║  CONFIGURATION — Change these values for your network    ║
// ╚═══════════════════════════════════════════════════════════╝

const char* WIFI_SSID     = "Sathvik";
const char* WIFI_PASSWORD = "sathvik@57";
const char* SERVER_URL    = "http://10.24.102.99:8000/api/iot/sensor-data";

// ╔═══════════════════════════════════════════════════════════╗
// ║  SENSOR PIN DEFINITIONS                                  ║
// ╚═══════════════════════════════════════════════════════════╝

#define MQ135_PIN  A0      // Analog pin for MQ-135 air quality sensor

// ╔═══════════════════════════════════════════════════════════╗
// ║  TIMING                                                  ║
// ╚═══════════════════════════════════════════════════════════╝

const unsigned long SEND_INTERVAL = 10000;  // Send data every 10 seconds
unsigned long lastSendTime = 0;

// ╔═══════════════════════════════════════════════════════════╗
// ║  MQ-135 AVERAGING                                        ║
// ║                                                          ║
// ║  The MQ-135 analog output can be noisy. We take multiple ║
// ║  samples and average them for a more stable reading.     ║
// ╚═══════════════════════════════════════════════════════════╝

const int NUM_SAMPLES = 10;         // Number of readings to average
const int SAMPLE_DELAY_MS = 20;     // Delay between each sample (ms)

// WiFi client for HTTP requests
WiFiClient wifiClient;

// Track warm-up status
bool isWarmedUp = false;
unsigned long bootTime = 0;
const unsigned long WARMUP_TIME = 120000;  // 2 minutes warm-up for MQ-135

// ═══════════════════════════════════════════════════════════════
//  SETUP — Runs once when the board powers on or resets
// ═══════════════════════════════════════════════════════════════

void setup() {
  // Start serial communication for debugging
  Serial.begin(115200);
  delay(100);

  Serial.println();
  Serial.println("═══════════════════════════════════════════");
  Serial.println("  SHADOW GARDEN — ESP2 Booting...");
  Serial.println("  Sensor: MQ-135 Air Quality");
  Serial.println("═══════════════════════════════════════════");

  // A0 is input by default, no pinMode needed for analog read
  Serial.println("[OK] MQ-135 sensor on A0");
  Serial.println("[INFO] MQ-135 needs ~2 min warm-up for stable readings.");

  // Record boot time for warm-up tracking
  bootTime = millis();

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

  // ── Step 2: Track MQ-135 warm-up status ──
  if (!isWarmedUp && (millis() - bootTime >= WARMUP_TIME)) {
    isWarmedUp = true;
    Serial.println("════════════════════════════════════════════");
    Serial.println("  ✅ MQ-135 warm-up complete! Readings are now stable.");
    Serial.println("════════════════════════════════════════════");
  }

  // ── Step 3: Check if it's time to send data ──
  unsigned long currentTime = millis();
  if (currentTime - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = currentTime;

    // ── Step 4: Read MQ-135 sensor ──
    int airQuality = readAirQuality();

    // ── Step 5: Print readings to Serial Monitor ──
    Serial.println("───────────────────────────────────────────");
    Serial.println("  📡 ESP2 Sensor Readings:");
    Serial.print("    🌫️  Air Quality : ");
    Serial.print(airQuality);
    Serial.println(" (raw ADC)");

    if (!isWarmedUp) {
      unsigned long remaining = (WARMUP_TIME - (millis() - bootTime)) / 1000;
      Serial.print("    ⏳ Warm-up: ");
      Serial.print(remaining);
      Serial.println("s remaining (readings may be unstable)");
    }

    // ── Step 6: Send data even during warm-up ──
    // The backend will still display the values; they just
    // might fluctuate during the first 2 minutes
    sendSensorData(airQuality);
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
//  SENSOR READING FUNCTION
// ═══════════════════════════════════════════════════════════════

/**
 * Read air quality from MQ-135 on analog pin A0.
 *
 * How it works:
 *   - The MQ-135 outputs an analog voltage proportional to the
 *     concentration of gases (CO2, NH3, benzene, smoke, etc.)
 *   - ESP8266 ADC reads 0-1024 (10-bit).
 *   - LOWER values  = cleaner air
 *   - HIGHER values = more polluted air
 *
 * Averaging:
 *   - We take multiple samples and average them because the
 *     MQ-135's analog output can be noisy and jittery.
 *   - This smooths out the reading significantly.
 *
 * Typical reading ranges:
 *   - Clean air:        50 - 200
 *   - Normal indoor:    200 - 400
 *   - Polluted/smoky:   400 - 800
 *   - Very poor:        800+
 */
int readAirQuality() {
  long total = 0;

  // Take multiple samples for a stable average
  for (int i = 0; i < NUM_SAMPLES; i++) {
    total += analogRead(MQ135_PIN);
    delay(SAMPLE_DELAY_MS);
  }

  int averageReading = total / NUM_SAMPLES;

  Serial.print("    [DEBUG] MQ-135 avg of ");
  Serial.print(NUM_SAMPLES);
  Serial.print(" samples: ");
  Serial.println(averageReading);

  return averageReading;
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
 *   "device": "esp2",
 *   "air_quality": 320
 * }
 */
void sendSensorData(int airQuality) {
  // ── Create JSON document ──
  // StaticJsonDocument allocates memory on the stack (fast, no fragmentation)
  // 128 bytes is more than enough for our small payload
  StaticJsonDocument<128> jsonDoc;

  jsonDoc["device"]      = "esp2";
  jsonDoc["air_quality"] = airQuality;

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
