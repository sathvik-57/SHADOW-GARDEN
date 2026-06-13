from fastapi import APIRouter, Query, HTTPException
import requests
import logging
import time

logger = logging.getLogger("Shadow Garden-Weather")

router = APIRouter(prefix="/api/weather", tags=["Weather Info"])

# ── In-memory cache: stores last successful response per place ──
# Format: { "place_name": { "data": {...}, "timestamp": float } }
_weather_cache = {}
CACHE_TTL_SECONDS = 300  # 5 minutes

def _fetch_with_retry(url, max_retries=3, delay=2):
    """Fetch URL with retries for transient 5xx errors."""
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                return res
            logger.warning(f"Open-Meteo attempt {attempt}/{max_retries}: status {res.status_code}")
            last_error = f"HTTP {res.status_code}"
        except requests.exceptions.Timeout:
            logger.warning(f"Open-Meteo attempt {attempt}/{max_retries}: timed out")
            last_error = "Timeout"
        except requests.RequestException as e:
            logger.warning(f"Open-Meteo attempt {attempt}/{max_retries}: {e}")
            last_error = str(e)
        
        if attempt < max_retries:
            time.sleep(delay)
    
    return None  # All retries failed

# Accurate coordinates for major towns/taluks across Karnataka
KARNATAKA_PLACES = {
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Yelahanka": {"lat": 13.1007, "lon": 77.5963},
    "Anekal": {"lat": 12.7105, "lon": 77.6960},
    "Mysuru": {"lat": 12.2958, "lon": 76.6394},
    "Nanjangud": {"lat": 12.1168, "lon": 76.6790},
    "T. Narasipura": {"lat": 12.2100, "lon": 76.9000},
    "Mandya": {"lat": 12.5218, "lon": 76.8951},
    "Srirangapatna": {"lat": 12.4181, "lon": 76.6947},
    "Maddur": {"lat": 12.5838, "lon": 77.0440},
    "Malavalli": {"lat": 12.3828, "lon": 77.0604},
    "Hassan": {"lat": 13.0033, "lon": 76.1004},
    "Belur": {"lat": 13.1631, "lon": 75.8625},
    "Sakleshpur": {"lat": 12.9407, "lon": 75.7845},
    "Tumakuru": {"lat": 13.3392, "lon": 77.1016},
    "Tiptur": {"lat": 13.2567, "lon": 76.4763},
    "Chitradurga": {"lat": 14.2251, "lon": 76.3980},
    "Hosadurga": {"lat": 13.7935, "lon": 76.2822},
    "Davangere": {"lat": 14.4644, "lon": 75.9218},
    "Shivamogga": {"lat": 13.9299, "lon": 75.5681},
    "Sagar": {"lat": 14.1667, "lon": 75.0231},
    "Bhadravathi": {"lat": 13.8290, "lon": 75.7050},
    "Hosanagara": {"lat": 13.9141, "lon": 75.0686},
    "Thirthahalli": {"lat": 13.6879, "lon": 75.2436},
    "Shikaripura": {"lat": 14.2682, "lon": 75.3564},
    "Soraba": {"lat": 14.3831, "lon": 75.0962},
    "Dharwad": {"lat": 15.4589, "lon": 75.0078},
    "Hubli": {"lat": 15.3647, "lon": 75.1240},
    "Belagavi": {"lat": 15.8497, "lon": 74.4977},
    "Gokak": {"lat": 16.1679, "lon": 74.8237},
    "Ramdurg": {"lat": 15.9516, "lon": 75.2932},
    "Kalaburagi": {"lat": 17.3297, "lon": 76.8343},
    "Aland": {"lat": 17.5668, "lon": 76.5686},
    "Raichur": {"lat": 16.2076, "lon": 77.3463},
    "Sindhanur": {"lat": 15.7713, "lon": 76.7520},
    "Manvi": {"lat": 15.9897, "lon": 77.0510},
    "Ballari": {"lat": 15.1394, "lon": 76.9214},
    "Hospet": {"lat": 15.2689, "lon": 76.3909},
    "Koppal": {"lat": 15.3460, "lon": 76.1558},
    "Bagalkot": {"lat": 16.1817, "lon": 75.6958},
    "Badami": {"lat": 15.9196, "lon": 75.6812},
    "Vijayapura": {"lat": 16.8302, "lon": 75.7100},
    "Bidar": {"lat": 17.9104, "lon": 77.5199},
    "Mangaluru": {"lat": 12.8688, "lon": 74.8430},
    "Udupi": {"lat": 13.3409, "lon": 74.7421},
    "Kundapura": {"lat": 13.6233, "lon": 74.6942},
    "Madikeri": {"lat": 12.4244, "lon": 75.7382},
    "Virajpet": {"lat": 12.1940, "lon": 75.7997},
    "Haveri": {"lat": 14.7951, "lon": 75.4006},
    "Ranebennur": {"lat": 14.6234, "lon": 75.6295},
    "Gadag": {"lat": 15.4167, "lon": 75.6262},
    "Karwar": {"lat": 14.8026, "lon": 74.1240},
    "Sirsi": {"lat": 14.6181, "lon": 74.8346},
    "Chamarajanagar": {"lat": 11.9236, "lon": 76.9398},
    "Kollegal": {"lat": 12.1568, "lon": 77.1112},
    "Chikkamagaluru": {"lat": 13.3161, "lon": 75.7720},
    "Mudigere": {"lat": 13.1308, "lon": 75.6376},
    "Yadgir": {"lat": 16.7604, "lon": 77.1330},
}

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

WEATHER_ICONS = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌦️", 53: "🌦️", 55: "🌧️",
    56: "🌨️", 57: "🌨️",
    61: "🌧️", 63: "🌧️", 65: "🌧️",
    66: "🌨️", 67: "🌨️",
    71: "❄️", 73: "❄️", 75: "❄️", 77: "❄️",
    80: "🌦️", 81: "🌧️", 82: "⛈️",
    85: "🌨️", 86: "🌨️",
    95: "⛈️", 96: "⛈️", 99: "⛈️"
}

@router.get("/places")
def get_places():
    return {"places": sorted(KARNATAKA_PLACES.keys())}

@router.get("/forecast")
def get_weather(place: str = Query(...)):
    try:
        if place not in KARNATAKA_PLACES:
            raise HTTPException(status_code=400, detail="Invalid location. Please select a valid Karnataka location.")

        location = KARNATAKA_PLACES[place]
        lat = location["lat"]
        lon = location["lon"]

        # Fetch current + hourly (24h) + daily (5 days)
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation,weather_code,wind_speed_10m,wind_gusts_10m,"
            "surface_pressure,cloud_cover"
            "&hourly=temperature_2m,precipitation_probability,weather_code"
            "&daily=weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_sum,precipitation_probability_max,sunrise,sunset,uv_index_max"
            "&timezone=Asia/Kolkata&forecast_days=5"
        )
        weather_res = _fetch_with_retry(weather_url)
        
        # If all retries failed, try to serve from cache
        if weather_res is None:
            cached = _weather_cache.get(place)
            if cached:
                logger.info(f"Serving cached weather for {place} (age: {int(time.time() - cached['timestamp'])}s)")
                return cached["data"]
            raise HTTPException(status_code=502, detail="Weather service is temporarily unavailable. Please try again in a few minutes.")
        
        weather_data = weather_res.json()

        current = weather_data.get("current", {})
        hourly = weather_data.get("hourly", {})
        daily = weather_data.get("daily", {})

        # Current weather
        code = current.get("weather_code", 0)
        temp = current.get("temperature_2m")
        feels_like = current.get("apparent_temperature")
        humidity = current.get("relative_humidity_2m")
        precipitation = current.get("precipitation")
        wind_speed = current.get("wind_speed_10m")
        wind_gust = current.get("wind_gusts_10m")
        pressure = current.get("surface_pressure")
        cloud_cover = current.get("cloud_cover")

        # Build hourly forecast (next 12 hours)
        hourly_forecast = []
        hourly_times = hourly.get("time", [])
        hourly_temps = hourly.get("temperature_2m", [])
        hourly_rain_prob = hourly.get("precipitation_probability", [])
        hourly_codes = hourly.get("weather_code", [])

        # Find current hour index
        from datetime import datetime
        now_str = datetime.now().strftime("%Y-%m-%dT%H:00")
        start_idx = 0
        for i, t in enumerate(hourly_times):
            if t >= now_str:
                start_idx = i
                break

        for i in range(start_idx, min(start_idx + 12, len(hourly_times))):
            time_str = hourly_times[i]
            hour_label = time_str.split("T")[1][:5]  # "HH:MM"
            hourly_forecast.append({
                "time": hour_label,
                "temp": hourly_temps[i] if i < len(hourly_temps) else None,
                "rain_prob": hourly_rain_prob[i] if i < len(hourly_rain_prob) else 0,
                "icon": WEATHER_ICONS.get(hourly_codes[i] if i < len(hourly_codes) else 0, "🌤️")
            })

        # Build daily forecast (5 days)
        daily_forecast = []
        daily_times = daily.get("time", [])
        daily_max = daily.get("temperature_2m_max", [])
        daily_min = daily.get("temperature_2m_min", [])
        daily_codes = daily.get("weather_code", [])
        daily_rain_prob = daily.get("precipitation_probability_max", [])
        daily_rain_sum = daily.get("precipitation_sum", [])

        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i in range(min(5, len(daily_times))):
            from datetime import date as dt_date
            d = dt_date.fromisoformat(daily_times[i])
            day_name = "Today" if i == 0 else days_of_week[d.weekday()]
            daily_forecast.append({
                "day": day_name,
                "date": daily_times[i],
                "max_temp": daily_max[i] if i < len(daily_max) else None,
                "min_temp": daily_min[i] if i < len(daily_min) else None,
                "rain_prob": daily_rain_prob[i] if i < len(daily_rain_prob) else 0,
                "rain_sum": daily_rain_sum[i] if i < len(daily_rain_sum) else 0,
                "icon": WEATHER_ICONS.get(daily_codes[i] if i < len(daily_codes) else 0, "🌤️"),
                "description": WEATHER_CODES.get(daily_codes[i] if i < len(daily_codes) else 0, "")
            })

        # UV index (today)
        uv_max = daily.get("uv_index_max", [])
        uv_today = uv_max[0] if uv_max else None
        uv_label = "Low"
        if uv_today is not None:
            if uv_today >= 11: uv_label = "Extreme"
            elif uv_today >= 8: uv_label = "Very High"
            elif uv_today >= 6: uv_label = "High"
            elif uv_today >= 3: uv_label = "Moderate"

        # Sunrise / Sunset
        sunrise = daily.get("sunrise", [])
        sunset = daily.get("sunset", [])
        sunrise_today = sunrise[0].split("T")[1] if sunrise else None
        sunset_today = sunset[0].split("T")[1] if sunset else None

        # Wind description
        wind_desc = "Calm"
        if wind_speed is not None:
            if wind_speed > 38: wind_desc = "Strong Wind"
            elif wind_speed > 19: wind_desc = "Moderate Breeze"
            elif wind_speed > 11: wind_desc = "Gentle Breeze"
            elif wind_speed > 5: wind_desc = "Light Breeze"

        result = {
            "location_name": f"{place}, Karnataka",
            "current": {
                "temperature": temp,
                "feels_like": feels_like,
                "humidity": humidity,
                "precipitation": precipitation,
                "description": WEATHER_CODES.get(code, "Unknown"),
                "icon": WEATHER_ICONS.get(code, "🌤️"),
                "wind_speed": wind_speed,
                "wind_gust": wind_gust,
                "wind_desc": wind_desc,
                "pressure": pressure,
                "cloud_cover": cloud_cover,
                "uv_index": uv_today,
                "uv_label": uv_label,
                "sunrise": sunrise_today,
                "sunset": sunset_today,
                "high": daily_max[0] if daily_max else None,
                "low": daily_min[0] if daily_min else None,
            },
            "hourly": hourly_forecast,
            "daily": daily_forecast
        }

        # Cache the successful response
        _weather_cache[place] = {"data": result, "timestamp": time.time()}
        logger.info(f"Weather data cached for {place}")

        return result

    except HTTPException:
        raise
    except Exception as e:
        # On any unexpected error, try to serve from cache
        cached = _weather_cache.get(place)
        if cached:
            logger.warning(f"Error occurred, serving cached data for {place}: {e}")
            return cached["data"]
        logger.error(f"Weather error (no cache available): {e}")
        raise HTTPException(status_code=500, detail="Weather service is temporarily unavailable.")