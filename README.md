# 🌿 Shadow Garden — Smart Agriculture IoT System

An IoT-based smart agriculture platform that monitors soil and environmental conditions in real-time, provides AI-powered crop recommendations, and detects plant diseases using deep learning.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Hardware Components](#hardware-components)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [ESP8266 Setup](#esp8266-setup)
- [API Endpoints](#api-endpoints)
- [ML Models](#ml-models)
- [Team](#team)

---

## 🔍 Overview

**Shadow Garden** is a full-stack IoT smart farming system built as an academic project (4th Semester — IoT). It combines real-time sensor monitoring with machine learning to help farmers make data-driven decisions.

### Key Features

- **🌡️ Real-Time Monitoring** — Temperature, humidity, soil moisture, and air quality streamed live from ESP8266 sensors
- **🧠 Crop Recommendation** — ML model suggests the best crops based on soil and weather parameters
- **🦠 Disease Detection** — Upload a leaf image and get instant disease diagnosis using EfficientNet-B0
- **🌦️ Weather Integration** — Real-time weather data for informed farming decisions
- **📊 Dashboard** — Interactive web dashboard with live sensor graphs and analytics

---

## 🏗️ Architecture

```
┌──────────────┐       HTTP POST       ┌──────────────────┐       REST API       ┌──────────────┐
│   ESP8266 #1 │ ───────────────────► │                  │ ◄──────────────────► │              │
│  (DHT11 +    │   /api/iot/sensor-data│   FastAPI        │                      │   React +    │
│  Soil Moist.)│                       │   Backend        │                      │   Vite       │
├──────────────┤       HTTP POST       │   (Python)       │                      │   Frontend   │
│   ESP8266 #2 │ ───────────────────► │                  │                      │              │
│  (MQ-135     │   /api/iot/sensor-data│  ┌────────────┐  │                      │  ┌────────┐  │
│  Air Quality)│                       │  │  SQLite DB │  │                      │  │ MUI +  │  │
└──────────────┘                       │  │  ML Models │  │                      │  │Tailwind│  │
                                       │  └────────────┘  │                      │  └────────┘  │
                                       └──────────────────┘                      └──────────────┘
```

---

## 🔧 Hardware Components

### ESP8266 #1 — Soil & Climate Monitoring

| Sensor | Pin | Readings |
|--------|-----|----------|
| DHT11 (Temp & Humidity) | D4 (GPIO 2) | Temperature (°C), Humidity (%) |
| Soil Moisture Sensor | A0 | Soil Moisture (0–100%) |

### ESP8266 #2 — Air Quality Monitoring

| Sensor | Pin | Readings |
|--------|-----|----------|
| MQ-135 (Gas Sensor) | A0 | Air Quality Index (raw ADC) |

> ⚠️ **Note:** MQ-135 requires 5V via VIN pin and a 2-minute warm-up time for stable readings.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **IoT Devices** | ESP8266 (NodeMCU), Arduino IDE |
| **Backend** | Python, FastAPI, Uvicorn |
| **Frontend** | React 19, TypeScript, Vite |
| **UI Framework** | Material UI (MUI), Tailwind CSS |
| **ML / DL** | PyTorch, EfficientNet-B0, Scikit-learn |
| **Database** | SQLite |
| **Sensors** | DHT11, Soil Moisture (Capacitive), MQ-135 |
| **Libraries (ESP)** | ArduinoJson, ESP8266WiFi, DHT (Adafruit) |

---

## 📁 Project Structure

```
SHADOW-GARDEN/
├── backend/                  # FastAPI backend server
│   ├── main.py               # App entry point
│   ├── database.py           # SQLite database connection
│   ├── routes/               # API route handlers
│   │   ├── iot.py            # IoT sensor data ingestion
│   │   ├── crops.py          # Crop recommendation endpoint
│   │   ├── disease.py        # Disease detection endpoint
│   │   ├── weather.py        # Weather data endpoint
│   │   └── lifecycle.py      # Crop lifecycle data
│   ├── ml/                   # ML models & inference
│   │   ├── inference.py      # Model loading & prediction
│   │   └── research/         # Training scripts & analysis
│   ├── services/             # Business logic
│   └── data/                 # Static datasets (JSON, CSV)
│
├── frontend/                 # React + Vite frontend
│   ├── src/                  # Source code
│   ├── public/               # Static assets
│   ├── package.json          # Node dependencies
│   └── vite.config.ts        # Vite configuration
│
├── ESP/                      # ESP8266 Arduino sketches
│   ├── 1.ino/                # ESP1 — DHT11 + Soil Moisture
│   └── 2.ino/                # ESP2 — MQ-135 Air Quality
│
├── DATASET/                  # Training datasets (gitignored)
├── requirements.txt          # Python dependencies
├── SECURITY.md               # Security policy
└── README.md                 # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- Arduino IDE (with ESP8266 board package)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:5173`

### ESP8266 Setup

1. Open Arduino IDE
2. Install the **ESP8266** board package (via Board Manager)
3. Install libraries: **ArduinoJson**, **DHT sensor library** (Adafruit)
4. Open `ESP/1.ino/1.ino.ino` (or `ESP/2.ino/2.ino.ino`)
5. Update Wi-Fi credentials and server IP:
   ```cpp
   const char* WIFI_SSID     = "YourWiFi";
   const char* WIFI_PASSWORD = "YourPassword";
   const char* SERVER_URL    = "http://<YOUR_PC_IP>:8000/api/iot/sensor-data";
   ```
6. Select board: **NodeMCU 1.0 (ESP-12E Module)**
7. Upload!

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root — API health check |
| `POST` | `/api/iot/sensor-data` | Receive sensor data from ESP devices |
| `POST` | `/api/crops/recommend` | Get crop recommendations |
| `POST` | `/api/disease/predict` | Upload leaf image for disease detection |
| `GET` | `/api/weather/...` | Fetch weather data |

---

## 🤖 ML Models

### Crop Recommendation
- **Algorithm:** Scikit-learn classifier
- **Input:** Temperature, humidity, pH, rainfall, soil nutrients (N, P, K)
- **Output:** Recommended crop with confidence score

### Plant Disease Detection
- **Model:** EfficientNet-B0 (PyTorch, transfer learning)
- **Input:** Leaf image (uploaded via API)
- **Output:** Disease name, confidence score, and prevention guidance

---

## 👥 Team

**Shadow Garden** — 4th Semester IoT Project

---

## 📄 License

This project is developed for academic purposes.