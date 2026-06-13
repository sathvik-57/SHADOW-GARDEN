import React, { useState, useEffect } from 'react';
import { Cloud, MapPin, Compass, Droplets, Wind, Sun, CloudRain, ThermometerSun, Search } from "lucide-react";

interface CurrentWeather {
  temperature: number;
  feels_like: number;
  humidity: number;
  precipitation: number;
  description: string;
  icon: string;
  wind_speed: number;
  wind_gust: number;
  wind_desc: string;
  pressure: number;
  cloud_cover: number;
  uv_index: number;
  uv_label: string;
  sunrise: string;
  sunset: string;
  high: number;
  low: number;
}

interface HourlyForecast {
  time: string;
  temp: number;
  rain_prob: number;
  icon: string;
}

interface DailyForecast {
  day: string;
  date: string;
  max_temp: number;
  min_temp: number;
  rain_prob: number;
  rain_sum: number;
  icon: string;
  description: string;
}

interface WeatherData {
  location_name: string;
  current: CurrentWeather;
  hourly: HourlyForecast[];
  daily: DailyForecast[];
}

const WeatherDashboard: React.FC = () => {
  const [location, setLocation] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [places, setPlaces] = useState<string[]>([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/weather/places')
      .then(res => res.json())
      .then(data => setPlaces(data.places || []))
      .catch(() => setPlaces([]));
  }, []);

  const handleSearch = async () => {
    if (!location.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/weather/forecast?place=${encodeURIComponent(location)}`);
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to establish atmospheric uplink.');
      }
      const data = await response.json();
      setWeatherData(data);
    } catch (err: any) {
      setError(err.message || "An anomaly occurred in the atmospheric sensors.");
    } finally {
      setLoading(false);
    }
  };

  const getUvColor = (label: string) => {
    switch (label) {
      case 'Low': return 'text-green-500';
      case 'Moderate': return 'text-yellow-500';
      case 'High': return 'text-orange-500';
      case 'Very High': return 'text-red-500';
      case 'Extreme': return 'text-fantasy-indigo';
      default: return 'text-gray-500';
    }
  };

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto animate-float" style={{ animationDuration: '10s' }}>
      <div className="mb-10 text-center">
        <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white drop-shadow-sm mb-2">
          Atmospheric Telemetry
        </h1>
        <p className="text-gray-500 dark:text-fantasy-silver/70 text-sm md:text-base">
          Analyze localized meteorological phenomena and aetheric pressure differentials.
        </p>
      </div>

      {/* Search */}
      <div className="mb-8 flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4 max-w-2xl mx-auto">
        <div className="relative flex-grow">
          <MapPin size={18} className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-fantasy-silver/50" />
          <select
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full pl-12 pr-4 py-3 rounded-lg outline-none transition-all duration-300
           dark:bg-fantasy-darker/80 dark:border-fantasy-accent/30 dark:text-fantasy-silver dark:focus:border-fantasy-cyan dark:focus:shadow-glow-cyan
           bg-white border-gray-200 text-gray-800 focus:border-fantasy-accent focus:ring-1 focus:ring-fantasy-accent appearance-none"
          >
            <option value="">Select Target Coordinates</option>
            {places.map((place) => (
              <option key={place} value={place}>{place}</option>
            ))}
          </select>
        </div>
        <button
          onClick={handleSearch}
          disabled={loading || !location}
          className="arcane-btn md:w-auto flex items-center justify-center px-8"
        >
          {loading ? (
             <span className="flex items-center"><Search className="animate-spin mr-2" size={18} /> Scanning...</span>
          ) : (
             <span className="flex items-center"><Search className="mr-2" size={18} /> Acquire Data</span>
          )}
        </button>
      </div>

      {error && (
        <div className="mb-8 max-w-2xl mx-auto p-4 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-500/30 rounded-lg text-red-700 dark:text-red-400 font-medium text-sm text-center">
          {error}
        </div>
      )}

      {weatherData && (
        <div className="space-y-6">
          {/* Main Display Area */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Primary Arcane Weather Readout */}
            <div className="fantasy-card p-8 lg:col-span-2 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-fantasy-cyan/10 rounded-full blur-[100px] -z-10"></div>
              <div className="absolute bottom-0 left-0 w-64 h-64 bg-fantasy-indigo/10 rounded-full blur-[100px] -z-10"></div>
              
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
                <div>
                  <h2 className="text-xl font-bold text-gray-800 dark:text-white flex items-center mb-1">
                    <MapPin size={18} className="text-fantasy-cyan mr-2" />
                    {weatherData.location_name}
                  </h2>
                  <p className="text-xs text-gray-500 dark:text-fantasy-silver/50 tracking-widest uppercase">Live Uplink Established</p>
                  
                  <div className="flex items-center mt-6">
                    <span className="text-7xl mr-6 filter drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]">{weatherData.current.icon}</span>
                    <div>
                      <p className="text-6xl font-extrabold text-gray-900 dark:text-white tracking-tighter">{weatherData.current.temperature}°</p>
                      <p className="text-xl font-medium text-fantasy-indigo dark:text-fantasy-cyan capitalize mt-1">{weatherData.current.description}</p>
                    </div>
                  </div>
                  
                  <div className="mt-6 flex space-x-6 text-sm text-gray-600 dark:text-fantasy-silver/80">
                    <span className="bg-gray-100 dark:bg-fantasy-panel_lighter px-3 py-1 rounded-md">
                      Sensory: {weatherData.current.feels_like}°C
                    </span>
                    <span className="bg-gray-100 dark:bg-fantasy-panel_lighter px-3 py-1 rounded-md flex space-x-3">
                      <span>Max: {weatherData.current.high}°</span>
                      <span className="text-gray-400">Min: {weatherData.current.low}°</span>
                    </span>
                  </div>
                </div>
              </div>

              {/* Hourly Matrix */}
              <div className="mt-10 border-t border-gray-200 dark:border-fantasy-accent/20 pt-6 overflow-x-auto pb-2 custom-scrollbar">
                <div className="flex space-x-6 min-w-max px-2">
                  {weatherData.hourly.map((h, i) => (
                    <div key={i} className="flex flex-col items-center justify-center text-center group cursor-pointer">
                      <p className="text-xs text-gray-500 dark:text-fantasy-silver/60 mb-2">{h.time}</p>
                      <div className="p-3 bg-white dark:bg-fantasy-darker border border-gray-100 dark:border-fantasy-accent/10 rounded-xl group-hover:border-fantasy-cyan transition-colors mb-2">
                        <p className="text-2xl drop-shadow-sm">{h.icon}</p>
                      </div>
                      <p className="font-bold text-gray-800 dark:text-white">{h.temp}°</p>
                      {h.rain_prob > 0 && (
                        <p className="text-[10px] text-fantasy-cyan font-bold mt-1 flex items-center">
                          <Droplets size={10} className="mr-0.5" />{h.rain_prob}%
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 5-Day Forecast Panel */}
            <div className="fantasy-card p-6">
              <h3 className="font-bold text-gray-800 dark:text-white mb-6 text-lg flex items-center border-b border-gray-200 dark:border-fantasy-accent/20 pb-3">
                <Compass size={18} className="text-fantasy-indigo mr-2" />
                Extended Projection
              </h3>
              <div className="space-y-4">
                {weatherData.daily.map((d, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-fantasy-panel_lighter transition-colors">
                    <div className="w-16">
                      <p className="font-bold text-sm text-gray-800 dark:text-white">{d.day}</p>
                    </div>
                    <span className="text-2xl filter drop-shadow-sm">{d.icon}</span>
                    <div className="w-16 flex justify-center">
                      {d.rain_prob > 0 && (
                        <span className="text-xs font-bold text-fantasy-cyan flex items-center">
                          <Droplets size={12} className="mr-1" />{d.rain_prob}%
                        </span>
                      )}
                    </div>
                    <div className="text-right w-16">
                      <span className="font-bold text-gray-900 dark:text-white">{d.max_temp}°</span>
                      <span className="text-gray-400 dark:text-fantasy-silver/50 text-sm ml-2">{d.min_temp}°</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Meteorological Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            
            <div className="fantasy-card p-5 group hover:border-fantasy-cyan">
              <h3 className="text-xs text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest font-semibold mb-3 flex items-center">
                <Wind size={14} className="mr-2 text-fantasy-cyan" /> Wind Vector
              </h3>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">{weatherData.current.wind_speed} <span className="text-sm font-medium text-gray-400">km/h</span></p>
              <p className="text-xs text-gray-500 mt-2 font-medium">Gusts {weatherData.current.wind_gust} km/h</p>
            </div>

            <div className="fantasy-card p-5 group hover:border-fantasy-indigo">
              <h3 className="text-xs text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest font-semibold mb-3 flex items-center">
                <Droplets size={14} className="mr-2 text-fantasy-indigo" /> Air Saturation
              </h3>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">{weatherData.current.humidity}<span className="text-sm font-medium text-gray-400">%</span></p>
              <p className="text-xs text-gray-500 mt-2 font-medium">
                {weatherData.current.humidity >= 80 ? 'Heavy Density' : weatherData.current.humidity >= 60 ? 'Moderate' : 'Optimal'}
              </p>
            </div>

            <div className="fantasy-card p-5 group hover:border-fantasy-accent">
              <h3 className="text-xs text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest font-semibold mb-3 flex items-center">
                <ThermometerSun size={14} className="mr-2 text-fantasy-accent" /> Pressure
              </h3>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">{Math.round(weatherData.current.pressure)} <span className="text-sm font-medium text-gray-400">hPa</span></p>
              <p className="text-xs text-gray-500 mt-2 font-medium">
                {weatherData.current.pressure >= 1013 ? 'High Density' : 'Low Density'}
              </p>
            </div>

            <div className="fantasy-card p-5 group hover:border-yellow-500">
              <h3 className="text-xs text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest font-semibold mb-3 flex items-center">
                <Sun size={14} className="mr-2 text-yellow-500" /> Radiation (UV)
              </h3>
              <p className={`text-2xl font-bold ${getUvColor(weatherData.current.uv_label)}`}>
                {weatherData.current.uv_index}
              </p>
              <p className={`text-xs mt-2 font-bold ${getUvColor(weatherData.current.uv_label)}`}>
                {weatherData.current.uv_label} Exposure
              </p>
            </div>

            <div className="fantasy-card p-5 group hover:border-gray-400">
              <h3 className="text-xs text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest font-semibold mb-3 flex items-center">
                <Cloud size={14} className="mr-2 text-gray-400" /> Obscuration
              </h3>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">{weatherData.current.cloud_cover}<span className="text-sm font-medium text-gray-400">%</span></p>
            </div>

            <div className="fantasy-card p-5 group hover:border-blue-500">
              <h3 className="text-xs text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest font-semibold mb-3 flex items-center">
                <CloudRain size={14} className="mr-2 text-blue-500" /> Precipitation
              </h3>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">{weatherData.current.precipitation} <span className="text-sm font-medium text-gray-400">mm</span></p>
              <p className="text-xs text-gray-500 mt-2 font-medium">Current Rainfall</p>
            </div>

            <div className="fantasy-card p-5 group hover:border-orange-400">
              <h3 className="text-xs text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest font-semibold mb-3 flex items-center">
                <Sun size={14} className="mr-2 text-orange-400" /> Dawn
              </h3>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">{weatherData.current.sunrise}</p>
            </div>

            <div className="fantasy-card p-5 group hover:border-purple-400">
              <h3 className="text-xs text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest font-semibold mb-3 flex items-center">
                <Cloud size={14} className="mr-2 text-purple-400" /> Dusk
              </h3>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">{weatherData.current.sunset}</p>
            </div>
          </div>
        </div>
      )}

      {!weatherData && !loading && (
        <div className="mt-16 text-center text-gray-500 dark:text-fantasy-silver/40 flex flex-col items-center">
          <Compass size={48} className="mb-4 opacity-50" />
          <p className="text-lg">Input coordinates to establish atmospheric scan.</p>
        </div>
      )}
    </div>
  );
};

export default WeatherDashboard;