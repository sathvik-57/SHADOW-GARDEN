import React, { useState, useEffect } from "react";
import axios from "axios";
import { useSensor } from "../context/SensorContext";
import { useLanguage } from "../context/LanguageContext";
import { Leaf, Activity, Beaker, FlaskConical, Droplets, Lock } from "lucide-react";

export default function CropRecommendation() {
  const sensor = useSensor();
  const { language } = useLanguage();

  const [form, setForm] = useState({
    temperature: "",
    humidity: "",
    moisture: "",
    soilType: "",
    ph: "",
    n: "",
    p: "",
    k: "",
    rainfall: ""
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    recommended_crop: string;
    crop_name_kn: string;
    fertilizer: string;
    fertilizer_name_kn: string;
    lifecycle: string[];
    lifecycle_kn: string[];
    why_fertilizer: string;
    why_fertilizer_kn: string;
    dosage: string;
    dosage_kn: string;
    water_requirement: string;
    water_requirement_kn: string;
    growth_duration: string;
    growth_duration_kn: string;
    ideal_temperature: string;
    ideal_temperature_kn: string;
  } | null>(null);

  useEffect(() => {
    if (sensor) {
      setForm(prev => ({
        ...prev,
        temperature: sensor.temperature !== null ? sensor.temperature.toString() : prev.temperature,
        humidity: sensor.humidity !== null ? sensor.humidity.toString() : prev.humidity,
        moisture: sensor.moisture !== null ? sensor.moisture.toString() : prev.moisture,
      }));
    }
  }, [sensor.temperature, sensor.humidity, sensor.moisture]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate sensor values exist
    if (!form.temperature || !form.humidity || !form.moisture) {
        setError("Please enter all required terrestrial and atmospheric parameters.");
        return;
    }

    try {
      setLoading(true);
      setError(null);
      setResult(null);

      // 1. Predict Crop
      const cropRes = await axios.post("http://localhost:8000/api/crops/recommend-crop", {
          temperature: parseFloat(form.temperature),
          humidity: parseFloat(form.humidity),
          ph: parseFloat(form.ph),
          n: parseFloat(form.n),
          p: parseFloat(form.p),
          k: parseFloat(form.k),
          rainfall: parseFloat(form.rainfall)
      });
      
      if (cropRes.data.error) {
          throw new Error(cropRes.data.error);
      }
      
      const recommendedCrop = cropRes.data.recommended_crop;

      // 2. Predict Fertilizer
      const fertRes = await axios.post("http://localhost:8000/api/crops/recommend-fertilizer", {
          temperature: parseFloat(form.temperature),
          humidity: parseFloat(form.humidity),
          moisture: parseFloat(form.moisture),
          soil_type: form.soilType,
          crop_type: recommendedCrop,
          n: parseFloat(form.n),
          p: parseFloat(form.p),
          k: parseFloat(form.k)
      });

      if (fertRes.data.error) {
          throw new Error(fertRes.data.error);
      }

      setResult({
        recommended_crop: recommendedCrop,
        crop_name_kn: fertRes.data.crop_name_kn || recommendedCrop,
        fertilizer: fertRes.data.fertilizer || "Unknown Compound",
        fertilizer_name_kn: fertRes.data.fertilizer_name_kn || "ಮಾಹಿತಿ ಇಲ್ಲ",
        lifecycle: Array.isArray(fertRes.data.lifecycle) ? fertRes.data.lifecycle : [],
        lifecycle_kn: Array.isArray(fertRes.data.lifecycle_kn) ? fertRes.data.lifecycle_kn : [],
        why_fertilizer: fertRes.data.why_fertilizer || "No reasoning provided.",
        why_fertilizer_kn: fertRes.data.why_fertilizer_kn || "ಮಾಹಿತಿ ಇಲ್ಲ.",
        dosage: fertRes.data.dosage || "Consult local guidelines",
        dosage_kn: fertRes.data.dosage_kn || "ಮಾಹಿತಿ ಇಲ್ಲ",
        water_requirement: fertRes.data.water_requirement || "Unknown",
        water_requirement_kn: fertRes.data.water_requirement_kn || "ಮಾಹಿತಿ ಇಲ್ಲ",
        growth_duration: fertRes.data.growth_duration || "Unknown",
        growth_duration_kn: fertRes.data.growth_duration_kn || "ಮಾಹಿತಿ ಇಲ್ಲ",
        ideal_temperature: fertRes.data.ideal_temperature || "Unknown",
        ideal_temperature_kn: fertRes.data.ideal_temperature_kn || "ಮಾಹಿತಿ ಇಲ್ಲ"
      });

    } catch (err: any) {
      console.error("Axios Error:", err);
      setError(err.response?.data?.error || err.message || "An anomaly occurred during the arcane calculation.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-8 mt-4 animate-float" style={{ animationDuration: '9s' }}>
      
      <div className="text-center mb-10 relative">
        <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white drop-shadow-sm mb-2">
          {language === "en" ? "Crop Advisor" : "ಬೆಳೆ ಸಲಹೆಗಾರ"}
        </h2>
        <p className="text-gray-500 dark:text-fantasy-silver/70 text-sm md:text-base max-w-2xl mx-auto">
          {language === "en" 
            ? "Input terrestrial parameters. Atmospheric variables are automatically retrieved from the sensor network."
            : "ಭೂಮಿಯ ನಿಯತಾಂಕಗಳನ್ನು ನಮೂದಿಸಿ. ಸಂವೇದಕ ಜಾಲದಿಂದ ವಾತಾವರಣದ ಅಸ್ಥಿರಗಳನ್ನು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಪಡೆಯಲಾಗುತ್ತದೆ."}
        </p>
      </div>

      <div className="fantasy-card p-6 md:p-8">
        <form onSubmit={handleSubmit} className="space-y-8">
          
          {/* Sensor Auto-filled Section */}
          <div className="bg-gray-50 dark:bg-fantasy-darker/60 p-5 rounded-xl border border-fantasy-accent/20 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-fantasy-cyan"></div>
              <h3 className="font-bold text-gray-800 dark:text-white mb-4 flex items-center tracking-wide">
                  <Activity size={18} className="text-fantasy-cyan mr-2 animate-pulse" /> 
                  Live Telemetry Injection
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="relative">
                      <label className="block text-xs font-semibold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-1">Ambient Temp</label>
                      <input 
                          name="temperature"
                          type="number"
                          step="0.1"
                          placeholder="Sensor Offline..."
                          value={form.temperature}
                          readOnly
                          className="w-full px-3 py-2 border border-fantasy-cyan/30 rounded bg-fantasy-cyan/5 text-gray-700 dark:text-fantasy-silver/80 text-sm font-medium cursor-not-allowed" 
                      />
                      <Lock size={12} className="absolute right-3 top-8 text-fantasy-cyan/50" />
                  </div>
                  <div className="relative">
                      <label className="block text-xs font-semibold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-1">Atmospheric Moist.</label>
                      <input 
                          name="humidity"
                          type="number"
                          step="0.1"
                          placeholder="Sensor Offline..."
                          value={form.humidity}
                          readOnly
                          className="w-full px-3 py-2 border border-fantasy-cyan/30 rounded bg-fantasy-cyan/5 text-gray-700 dark:text-fantasy-silver/80 text-sm font-medium cursor-not-allowed" 
                      />
                      <Lock size={12} className="absolute right-3 top-8 text-fantasy-cyan/50" />
                  </div>
                  <div className="relative">
                      <label className="block text-xs font-semibold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-1">Earth Saturation</label>
                      <input 
                          name="moisture"
                          type="number"
                          step="0.1"
                          placeholder="Sensor Offline..."
                          value={form.moisture}
                          readOnly
                          className="w-full px-3 py-2 border border-fantasy-cyan/30 rounded bg-fantasy-cyan/5 text-gray-700 dark:text-fantasy-silver/80 text-sm font-medium cursor-not-allowed" 
                      />
                      <Lock size={12} className="absolute right-3 top-8 text-fantasy-cyan/50" />
                  </div>
              </div>
          </div>

          {/* User Input Section */}
          <div>
              <h3 className="font-bold text-gray-800 dark:text-white mb-4 tracking-wide flex items-center">
                <Beaker size={18} className="text-fantasy-indigo mr-2" />
                Terrestrial Parameters
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div className="relative">
                    <select
                      name="soilType"
                      value={form.soilType}
                      onChange={handleChange}
                      required
                      className="arcane-input appearance-none"
                    >
                      <option value="">Select Earth Classification</option>
                      <option value="Sandy">Sandy</option>
                      <option value="Loamy">Loamy</option>
                      <option value="Clayey">Clayey</option>
                      <option value="Black">Black</option>
                      <option value="Red">Red</option>
                    </select>
                  </div>
                  
                  <input
                    name="ph"
                    type="number"
                    step="0.01"
                    placeholder="Alkalinity/Acidity (pH)"
                    value={form.ph}
                    onChange={handleChange}
                    required
                    className="arcane-input"
                  />
                  
                  <div className="relative">
                    <FlaskConical size={16} className="absolute top-4 right-4 text-fantasy-silver/40" />
                    <input
                      name="n"
                      type="number"
                      placeholder="Nitrogen Compound (N)"
                      value={form.n}
                      onChange={handleChange}
                      required
                      className="arcane-input"
                    />
                  </div>
                  
                  <div className="relative">
                    <FlaskConical size={16} className="absolute top-4 right-4 text-fantasy-silver/40" />
                    <input
                      name="p"
                      type="number"
                      placeholder="Phosphorus Compound (P)"
                      value={form.p}
                      onChange={handleChange}
                      required
                      className="arcane-input"
                    />
                  </div>
                  
                  <div className="relative">
                    <FlaskConical size={16} className="absolute top-4 right-4 text-fantasy-silver/40" />
                    <input
                      name="k"
                      type="number"
                      placeholder="Potassium Compound (K)"
                      value={form.k}
                      onChange={handleChange}
                      required
                      className="arcane-input"
                    />
                  </div>
                  
                  <div className="relative">
                    <Droplets size={16} className="absolute top-4 right-4 text-fantasy-cyan/40" />
                    <input
                      name="rainfall"
                      type="number"
                      step="0.1"
                      placeholder="Precipitation (mm)"
                      value={form.rainfall}
                      onChange={handleChange}
                      required
                      className="arcane-input"
                    />
                  </div>
              </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="arcane-btn"
          >
            {loading ? "Computing Arcane Matrix..." : "Calculate Optimal Yield"}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-500/30 rounded-lg text-red-700 dark:text-red-400 font-medium text-sm flex items-center">
            <span className="mr-2">⚠️</span> {error}
          </div>
        )}

        {result && (
          <div className="mt-10 bg-gray-50 dark:bg-fantasy-darker p-6 md:p-8 rounded-xl border border-fantasy-accent/30 shadow-glow-violet relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-fantasy-accent/10 rounded-full blur-3xl -z-10"></div>
            
            <div className="mb-8 border-b border-gray-200 dark:border-fantasy-panel_lighter pb-6">
              <h3 className="text-xs font-semibold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-2">
                {language === "en" ? "Optimal Crop Yield" : "ಸೂಕ್ತ ಬೆಳೆ ಇಳುವರಿ"}
              </h3>
              <div className="text-4xl font-extrabold text-gray-900 dark:text-white flex items-center mb-6">
                <Leaf className="text-fantasy-accent mr-3 w-8 h-8" />
                {language === "en" ? result.recommended_crop : result.crop_name_kn}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white dark:bg-fantasy-panel p-3 rounded-lg border border-gray-100 dark:border-fantasy-accent/10">
                  <div className="text-[10px] font-bold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-1">{language === "en" ? "Growth Duration" : "ಬೆಳವಣಿಗೆಯ ಅವಧಿ"}</div>
                  <div className="font-semibold text-gray-800 dark:text-gray-200">{language === "en" ? result.growth_duration : result.growth_duration_kn}</div>
                </div>
                <div className="bg-white dark:bg-fantasy-panel p-3 rounded-lg border border-gray-100 dark:border-fantasy-accent/10">
                  <div className="text-[10px] font-bold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-1">{language === "en" ? "Water Requirement" : "ನೀರಿನ ಅವಶ್ಯಕತೆ"}</div>
                  <div className="font-semibold text-gray-800 dark:text-gray-200">{language === "en" ? result.water_requirement : result.water_requirement_kn}</div>
                </div>
                <div className="bg-white dark:bg-fantasy-panel p-3 rounded-lg border border-gray-100 dark:border-fantasy-accent/10">
                  <div className="text-[10px] font-bold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-1">{language === "en" ? "Ideal Temperature" : "ಆದರ್ಶ ತಾಪಮಾನ"}</div>
                  <div className="font-semibold text-gray-800 dark:text-gray-200">{language === "en" ? result.ideal_temperature : result.ideal_temperature_kn}</div>
                </div>
              </div>
            </div>
            
            <div className="mb-8 border-b border-gray-200 dark:border-fantasy-panel_lighter pb-6">
                <h3 className="text-xs font-semibold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-2">
                  {language === "en" ? "Recommended Alchemical Compound" : "ಶಿಫಾರಸು ಮಾಡಿದ ರಸಗೊಬ್ಬರ"}
                </h3>
                <div className="text-2xl font-bold text-fantasy-cyan mb-4">
                  {language === "en" ? result.fertilizer : result.fertilizer_name_kn}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="col-span-1">
                    <div className="text-[10px] font-bold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-1">{language === "en" ? "Dosage" : "ಪ್ರಮಾಣ"}</div>
                    <div className="font-semibold text-gray-800 dark:text-gray-200 bg-white dark:bg-fantasy-panel p-3 rounded-lg border border-gray-100 dark:border-fantasy-accent/10">
                      {language === "en" ? result.dosage : result.dosage_kn}
                    </div>
                  </div>
                  <div className="col-span-2">
                    <div className="text-[10px] font-bold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-1">{language === "en" ? "Alchemical Reasoning" : "ವೈಜ್ಞಾನಿಕ ಕೃಷಿ ಕಾರಣ"}</div>
                    <p className="text-gray-600 dark:text-fantasy-silver/80 text-sm leading-relaxed border-l-2 border-fantasy-cyan pl-3 py-1">
                      {language === "en" ? result.why_fertilizer : result.why_fertilizer_kn}
                    </p>
                  </div>
                </div>
            </div>
            
            <div>
              <h3 className="text-xs font-semibold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-4">
                {language === "en" ? "Lifecycle & Cultivation Protocol" : "ಬೆಳವಣಿಗೆಯ ಹಂತಗಳು"}
              </h3>
              <ul className="space-y-3">
                {(language === "en" ? result.lifecycle : result.lifecycle_kn) && (language === "en" ? result.lifecycle : result.lifecycle_kn).length > 0 ? (
                  (language === "en" ? result.lifecycle : result.lifecycle_kn).map((step, idx) => (
                    <li key={idx} className="flex items-start text-sm text-gray-700 dark:text-fantasy-silver/90 bg-white dark:bg-fantasy-panel p-3 rounded-lg border border-gray-100 dark:border-fantasy-accent/10 shadow-sm">
                      <span className="text-fantasy-indigo font-bold mr-3 mt-0.5">{idx + 1}.</span>
                      {step}
                    </li>
                  ))
                ) : (
                  <li className="text-sm text-gray-500 dark:text-fantasy-silver/50 italic">{language === "en" ? "Protocols unavailable for this specimen." : "ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ."}</li>
                )}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}