import React, { useEffect, useState } from "react";
import { useSensor } from "../context/SensorContext";
import { Thermometer, Droplets, Droplet, Wind, Activity, Zap } from "lucide-react";

export default function Home() {
  const sensor = useSensor();

  // Calculate seconds ago for display
  const [secondsAgo, setSecondsAgo] = useState<number | null>(null);

  useEffect(() => {
    const updateTimer = () => {
      // Find the most recent update time
      const time1 = sensor.lastUpdate1 ? new Date(sensor.lastUpdate1 + "Z").getTime() : 0;
      const time2 = sensor.lastUpdate2 ? new Date(sensor.lastUpdate2 + "Z").getTime() : 0;
      const latest = Math.max(time1, time2);

      if (latest > 0) {
        setSecondsAgo(Math.floor((Date.now() - latest) / 1000));
      } else {
        setSecondsAgo(null);
      }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  }, [sensor.lastUpdate1, sensor.lastUpdate2]);

  return (
    <div className="max-w-7xl mx-auto p-4 md:p-8 animate-float" style={{ animationDuration: '8s' }}>
      <div className="mb-12 text-center md:text-left flex flex-col md:flex-row items-center justify-between">
        <div>
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white drop-shadow-sm mb-2">
            Telemetry Overview
          </h1>
          <p className="text-gray-500 dark:text-fantasy-silver/70 text-sm md:text-base">
            Real-time arcane sensor network status and field metrics.
          </p>
        </div>

        <div className="mt-4 md:mt-0 flex items-center space-x-2 bg-white/50 dark:bg-fantasy-panel_light/50 px-4 py-2 rounded-full border border-gray-200 dark:border-fantasy-accent/20 shadow-sm backdrop-blur-md">
          <Activity size={18} className="text-fantasy-cyan animate-pulse" />
          <span className="text-sm font-semibold text-gray-700 dark:text-fantasy-silver">
            {secondsAgo !== null ? `Sync: ${secondsAgo}s ago` : "Awaiting uplink..."}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {/* Temperature Card */}
        <div className="fantasy-card p-6 relative overflow-hidden group">
          <div className="absolute -right-6 -top-6 w-24 h-24 bg-red-500/10 rounded-full blur-2xl group-hover:bg-red-500/20 transition-all duration-500"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-red-100 dark:bg-red-500/10 rounded-lg">
              <Thermometer size={24} className="text-red-500" />
            </div>
          </div>
          <h3 className="text-gray-500 dark:text-fantasy-silver/70 text-sm font-semibold uppercase tracking-widest mb-1">Ambient Heat</h3>
          <div className="text-4xl font-bold text-gray-800 dark:text-white tracking-tight">
            {sensor.temperature !== null ? `${sensor.temperature}°C` : "--"}
          </div>
        </div>

        {/* Humidity Card */}
        <div className="fantasy-card p-6 relative overflow-hidden group">
          <div className="absolute -right-6 -top-6 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl group-hover:bg-blue-500/20 transition-all duration-500"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-blue-100 dark:bg-blue-500/10 rounded-lg">
              <Droplets size={24} className="text-blue-500" />
            </div>
          </div>
          <h3 className="text-gray-500 dark:text-fantasy-silver/70 text-sm font-semibold uppercase tracking-widest mb-1">Atmospheric Moisture</h3>
          <div className="text-4xl font-bold text-gray-800 dark:text-white tracking-tight">
            {sensor.humidity !== null ? `${sensor.humidity}%` : "--"}
          </div>
        </div>

        {/* Soil Moisture Card */}
        <div className="fantasy-card p-6 relative overflow-hidden group">
          <div className="absolute -right-6 -top-6 w-24 h-24 bg-amber-500/10 rounded-full blur-2xl group-hover:bg-amber-500/20 transition-all duration-500"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-amber-100 dark:bg-amber-500/10 rounded-lg">
              <Droplet size={24} className="text-amber-500" />
            </div>
          </div>
          <h3 className="text-gray-500 dark:text-fantasy-silver/70 text-sm font-semibold uppercase tracking-widest mb-1">Earth Saturation</h3>
          <div className="text-4xl font-bold text-gray-800 dark:text-white tracking-tight">
            {sensor.moisture !== null ? `${sensor.moisture}%` : "--"}
          </div>
        </div>

        {/* Air Quality Card */}
        <div className="fantasy-card p-6 relative overflow-hidden group">
          <div className="absolute -right-6 -top-6 w-24 h-24 bg-fantasy-cyan/10 rounded-full blur-2xl group-hover:bg-fantasy-cyan/20 transition-all duration-500"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="p-3 bg-fantasy-cyan/10 rounded-lg">
              <Wind size={24} className="text-fantasy-cyan" />
            </div>
          </div>
          <h3 className="text-gray-500 dark:text-fantasy-silver/70 text-sm font-semibold uppercase tracking-widest mb-1">Aether Quality</h3>
          <div className="text-4xl font-bold text-gray-800 dark:text-white tracking-tight">
            {sensor.air_quality !== null ? `${sensor.air_quality} ppm` : "--"}
          </div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto">
        <div className="fantasy-card p-8">
          <div className="flex items-center space-x-3 mb-8 border-b border-gray-200 dark:border-fantasy-accent/20 pb-4">
            <Zap className="text-fantasy-indigo animate-pulse-glow rounded-full" />
            <h3 className="text-xl font-bold text-gray-800 dark:text-white tracking-wide">Network Nodes</h3>
          </div>

          <div className="space-y-6">
            <div className="flex justify-between items-center bg-gray-50 dark:bg-fantasy-darker/50 p-4 rounded-xl border border-gray-100 dark:border-fantasy-accent/10">
              <div className="flex items-center space-x-4">
                <div className={`status-dot ${sensor.esp1Online ? 'status-online' : 'status-offline'}`}></div>
                <div>
                  <span className="block font-semibold text-gray-800 dark:text-gray-200">Node Alpha</span>
                  <span className="text-xs text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-wider">Earth / Temp Array</span>
                </div>
              </div>
              <span className={`px-4 py-1.5 rounded-full text-xs font-bold tracking-wider ${sensor.esp1Online
                ? 'bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400 border border-green-200 dark:border-green-500/30'
                : 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400 border border-red-200 dark:border-red-500/30'
                }`}>
                {sensor.esp1Online ? 'ACTIVE' : 'OFFLINE'}
              </span>
            </div>

            <div className="flex justify-between items-center bg-gray-50 dark:bg-fantasy-darker/50 p-4 rounded-xl border border-gray-100 dark:border-fantasy-accent/10">
              <div className="flex items-center space-x-4">
                <div className={`status-dot ${sensor.esp2Online ? 'status-online' : 'status-offline'}`}></div>
                <div>
                  <span className="block font-semibold text-gray-800 dark:text-gray-200">Node Delta</span>
                  <span className="text-xs text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-wider">Atmospheric Array</span>
                </div>
              </div>
              <span className={`px-4 py-1.5 rounded-full text-xs font-bold tracking-wider ${sensor.esp2Online
                ? 'bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400 border border-green-200 dark:border-green-500/30'
                : 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400 border border-red-200 dark:border-red-500/30'
                }`}>
                {sensor.esp2Online ? 'ACTIVE' : 'OFFLINE'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
