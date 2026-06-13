from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import get_db_connection
import logging

logger = logging.getLogger("Shadow Garden-API")
router = APIRouter(prefix="/api/iot", tags=["IoT Sensors"])

class SensorData(BaseModel):
    device: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    moisture: Optional[float] = None
    air_quality: Optional[float] = None

@router.post("/sensor-data")
async def receive_sensor_data(data: SensorData):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        last_update = datetime.utcnow().isoformat()
        
        # Upsert logic for SQLite
        cursor.execute('''
            INSERT INTO latest_sensor_data (device, temperature, humidity, moisture, air_quality, last_update)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(device) DO UPDATE SET
                temperature = excluded.temperature,
                humidity = excluded.humidity,
                moisture = excluded.moisture,
                air_quality = excluded.air_quality,
                last_update = excluded.last_update
        ''', (data.device, data.temperature, data.humidity, data.moisture, data.air_quality, last_update))
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": f"Data received from {data.device}"}
    except Exception as e:
        logger.error(f"Error saving sensor data: {e}")
        return {"error": "Failed to save data"}

@router.get("/latest")
async def get_latest_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM latest_sensor_data")
        rows = cursor.fetchall()
        conn.close()
        
        combined = {
            "temperature": None,
            "humidity": None,
            "moisture": None,
            "air_quality": None,
            "devices": {}
        }
        
        for row in rows:
            dev_name = row["device"]
            combined["devices"][dev_name] = row["last_update"]
            
            # Map values if they are not None
            if row["temperature"] is not None: combined["temperature"] = row["temperature"]
            if row["humidity"] is not None: combined["humidity"] = row["humidity"]
            if row["moisture"] is not None: combined["moisture"] = row["moisture"]
            if row["air_quality"] is not None: combined["air_quality"] = row["air_quality"]
                    
        return combined
    except Exception as e:
        logger.error(f"Error fetching sensor data: {e}")
        return {"error": "Failed to fetch data"}
