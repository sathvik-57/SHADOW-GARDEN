import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface SensorData {
  temperature: number | null;
  humidity: number | null;
  moisture: number | null;
  air_quality: number | null;
  esp1Online: boolean;
  esp2Online: boolean;
  lastUpdate1: string | null;
  lastUpdate2: string | null;
}

const SensorContext = createContext<SensorData | null>(null);

export const SensorProvider = ({ children }: { children: ReactNode }) => {
  const [data, setData] = useState<SensorData>({
    temperature: null,
    humidity: null,
    moisture: null,
    air_quality: null,
    esp1Online: false,
    esp2Online: false,
    lastUpdate1: null,
    lastUpdate2: null
  });

  useEffect(() => {
    const fetchSensors = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/iot/latest');
        const resData = res.data;
        
        const now = new Date();
        const checkOnline = (updateTime: string | null) => {
            if (!updateTime) return false;
            // Parse UTC time
            const updateDate = new Date(updateTime + "Z");
            const diffSeconds = (now.getTime() - updateDate.getTime()) / 1000;
            return diffSeconds < 30; // 30 seconds threshold
        };

        const esp1Update = resData?.devices?.esp1 || null;
        const esp2Update = resData?.devices?.esp2 || null;

        setData({
          temperature: resData?.temperature ?? null,
          humidity: resData?.humidity ?? null,
          moisture: resData?.moisture ?? null,
          air_quality: resData?.air_quality ?? null,
          esp1Online: checkOnline(esp1Update),
          esp2Online: checkOnline(esp2Update),
          lastUpdate1: esp1Update,
          lastUpdate2: esp2Update
        });
      } catch (err) {
        console.error("Failed to fetch sensor data", err);
      }
    };

    fetchSensors(); // Initial fetch
    const intervalId = setInterval(fetchSensors, 10000); // Poll every 10 seconds

    return () => clearInterval(intervalId);
  }, []);

  return (
    <SensorContext.Provider value={data}>
      {children}
    </SensorContext.Provider>
  );
};

export const useSensor = () => {
  const context = useContext(SensorContext);
  if (!context) throw new Error("useSensor must be used within a SensorProvider");
  return context;
};
