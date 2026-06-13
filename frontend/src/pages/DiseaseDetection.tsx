import React, { useState, useRef } from "react";
import axios from "axios";
import { useLanguage } from "../context/LanguageContext";
import { UploadCloud, ShieldCheck, AlertCircle, ScanEye } from "lucide-react";

interface PredictionResult {
  disease: string;
  disease_kn: string;
  confidence: number;
  severity?: string;
  severity_kn?: string;
  severity_color?: string;
  severity_score?: number;
  yield_loss?: string;
  yield_loss_kn?: string;
  pathogen?: string;
  pathogen_kn?: string;
  description?: string;
  description_kn?: string;
  prevention_steps: string[];
  prevention_steps_kn: string[];
}

const DiseaseDetection: React.FC = () => {
  const { language } = useLanguage();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setError(null);
      setPrediction(null);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const selectedFile = e.dataTransfer.files[0];
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setError(null);
      setPrediction(null);
    }
  };

  const handleSubmit = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setPrediction(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        `http://localhost:8000/api/disease/predict`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setPrediction(response.data as PredictionResult);
    } catch (err: any) {
      console.error("Error predicting disease:", err);
      setError(
        err.response?.data?.detail ||
        "Failed to establish arcane uplink. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-4 md:p-8 mt-4 animate-float" style={{ animationDuration: '7s' }}>
      <div className="text-center mb-10">
        <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white drop-shadow-sm mb-2">
          {language === "en" ? "Pathogen Detection System" : "ರೋಗಕಾರಕ ಪತ್ತೆ ವ್ಯವಸ್ಥೆ"}
        </h2>
        <p className="text-gray-500 dark:text-fantasy-silver/70 text-sm md:text-base max-w-2xl mx-auto">
          {language === "en" 
            ? "Upload a botanical sample to engage the arcane visual analysis network for threat detection." 
            : "ಬೆದರಿಕೆ ಪತ್ತೆಗಾಗಿ ದೃಶ್ಯ ವಿಶ್ಲೇಷಣಾ ಜಾಲವನ್ನು ತೊಡಗಿಸಿಕೊಳ್ಳಲು ಸಸ್ಯದ ಮಾದರಿಯನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ."}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Upload Interface */}
        <div className="fantasy-card p-6 md:p-8 flex flex-col h-full">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-bold text-gray-800 dark:text-white flex items-center tracking-wide">
              <ScanEye size={18} className="text-fantasy-cyan mr-2" /> 
              {language === "en" ? "Sample Submission" : "ಮಾದರಿ ಸಲ್ಲಿಕೆ"}
            </h3>
          </div>

          <div 
            className={`flex-grow border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-8 transition-all duration-300 cursor-pointer text-center
              ${file ? 'border-fantasy-indigo dark:bg-fantasy-indigo/5 bg-fantasy-indigo/5' : 'border-gray-300 dark:border-fantasy-accent/30 hover:border-fantasy-cyan dark:hover:border-fantasy-cyan hover:bg-gray-50 dark:hover:bg-fantasy-cyan/5'}
            `}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              disabled={loading}
              ref={fileInputRef}
              className="hidden"
            />
            
            {preview ? (
              <div className="relative w-full aspect-square md:aspect-[4/3] rounded-lg overflow-hidden border border-fantasy-accent/30 shadow-glass">
                <img src={preview} alt="Sample Preview" className="w-full h-full object-cover" />
                <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                  <span className="text-white font-medium bg-black/60 px-4 py-2 rounded-lg backdrop-blur-sm">Resubmit Sample</span>
                </div>
              </div>
            ) : (
              <>
                <div className="w-20 h-20 rounded-full bg-gray-100 dark:bg-fantasy-darker flex items-center justify-center mb-4">
                  <UploadCloud size={40} className="text-gray-400 dark:text-fantasy-silver/50" />
                </div>
                <p className="text-gray-700 dark:text-white font-medium mb-1">
                  {language === "en" ? "Click to browse or drag and drop" : "ಬ್ರೌಸ್ ಮಾಡಲು ಕ್ಲಿಕ್ ಮಾಡಿ ಅಥವಾ ಎಳೆಯಿರಿ"}
                </p>
                <p className="text-gray-500 dark:text-fantasy-silver/60 text-sm">
                  {language === "en" ? "JPG, PNG, GIF up to 10MB" : "JPG, PNG, GIF 10MB ವರೆಗೆ"}
                </p>
              </>
            )}
          </div>

          <button
            onClick={handleSubmit}
            disabled={!file || loading}
            className="arcane-btn mt-6 flex items-center justify-center"
          >
            {loading ? (
              <>
                <ScanEye className="animate-spin mr-2" size={20} />
                {language === "en" ? "Scanning Matrix..." : "ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ..."}
              </>
            ) : (
              language === "en" ? "Initialize Analysis" : "ವಿಶ್ಲೇಷಣೆ ಪ್ರಾರಂಭಿಸಿ"
            )}
          </button>

          {error && (
            <div className="mt-4 p-4 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-500/30 rounded-lg text-red-700 dark:text-red-400 font-medium text-sm flex items-start">
              <AlertCircle className="mr-2 flex-shrink-0 mt-0.5" size={16} /> 
              {error}
            </div>
          )}
        </div>

        {/* Prediction Results */}
        <div className="fantasy-card p-6 md:p-8 flex flex-col h-full relative overflow-hidden">
          {!prediction ? (
            <div className="flex-grow flex flex-col items-center justify-center text-center opacity-50">
              <ShieldCheck size={64} className="text-gray-300 dark:text-fantasy-silver/20 mb-4" />
              <p className="text-gray-500 dark:text-fantasy-silver/60">
                {language === "en" ? "Awaiting sample submission to begin threat analysis." : "ಬೆದರಿಕೆ ವಿಶ್ಲೇಷಣೆಯನ್ನು ಪ್ರಾರಂಭಿಸಲು ಮಾದರಿ ಸಲ್ಲಿಕೆಗಾಗಿ ಕಾಯಲಾಗುತ್ತಿದೆ."}
              </p>
            </div>
          ) : (
            <>
              <div className="absolute top-0 right-0 w-32 h-32 bg-fantasy-cyan/10 rounded-full blur-3xl -z-10"></div>
              
              <div className="mb-6">
                <h3 className="text-xs font-semibold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-2 flex items-center">
                  <AlertCircle size={14} className="mr-1 text-fantasy-cyan" /> 
                  {language === "en" ? "Identified Threat" : "ಗುರುತಿಸಲಾದ ಬೆದರಿಕೆ"}
                </h3>
                <div className="text-3xl font-extrabold text-gray-900 dark:text-white break-words">
                  {language === "en" ? prediction.disease : prediction.disease_kn}
                </div>
              </div>

              <div className="mb-8">
                <div className="flex justify-between items-end mb-2">
                  <span className="text-sm font-medium text-gray-600 dark:text-fantasy-silver/80">
                    {language === "en" ? "Diagnostic Confidence" : "ರೋಗನಿರ್ಣಯದ ನಿಖರತೆ"}
                  </span>
                  <span className="text-lg font-bold text-fantasy-cyan">{(prediction.confidence * 100).toFixed(2)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-fantasy-darker rounded-full h-2.5 border border-gray-300 dark:border-fantasy-accent/20 overflow-hidden mb-2">
                  <div 
                    className="bg-gradient-to-r from-fantasy-indigo to-fantasy-cyan h-2.5 rounded-full" 
                    style={{ width: `${prediction.confidence * 100}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500 dark:text-fantasy-silver/70 italic text-right">
                  {prediction.confidence >= 0.9 ? (
                    language === "en" ? "High Confidence Prediction" : "ಹೆಚ್ಚಿನ ನಿಖರತೆಯ ಮುನ್ನೋಟ"
                  ) : prediction.confidence >= 0.6 ? (
                    language === "en" ? "Moderate Confidence Prediction" : "ಮಧ್ಯಮ ನಿಖರತೆಯ ಮುನ್ನೋಟ"
                  ) : (
                    language === "en" ? "Low confidence. Please upload a clearer image." : "ಕಡಿಮೆ ನಿಖರತೆ. ದಯವಿಟ್ಟು ಸ್ಪಷ್ಟವಾದ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ."
                  )}
                </div>
              </div>

              {(prediction.severity || prediction.yield_loss || prediction.pathogen) && (
                <div className="grid grid-cols-2 gap-3 mb-8">
                  {prediction.severity && (
                    <div className="bg-gray-50 dark:bg-fantasy-darker/50 p-3 rounded-lg border border-gray-100 dark:border-fantasy-accent/10">
                      <div className="text-[10px] font-bold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-1">
                        {language === "en" ? "Severity" : "ತೀವ್ರತೆ"}
                      </div>
                      <div className={`font-semibold flex items-center ${
                        prediction.severity_color === 'red' ? 'text-red-500' :
                        prediction.severity_color === 'orange' ? 'text-amber-500' :
                        prediction.severity_color === 'yellow' ? 'text-yellow-500' : 'text-green-500'
                      }`}>
                        <span className={`w-2 h-2 rounded-full mr-2 ${
                          prediction.severity_color === 'red' ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]' :
                          prediction.severity_color === 'orange' ? 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.8)]' :
                          prediction.severity_color === 'yellow' ? 'bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.8)]' : 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)]'
                        }`}></span>
                        {language === "en" ? prediction.severity : prediction.severity_kn}
                      </div>
                    </div>
                  )}
                  {prediction.yield_loss && (
                    <div className="bg-gray-50 dark:bg-fantasy-darker/50 p-3 rounded-lg border border-gray-100 dark:border-fantasy-accent/10">
                      <div className="text-[10px] font-bold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-1">
                        {language === "en" ? "Yield Loss" : "ಇಳುವರಿ ನಷ್ಟ"}
                      </div>
                      <div className="font-semibold text-gray-800 dark:text-gray-200">
                        {language === "en" ? prediction.yield_loss : prediction.yield_loss_kn}
                      </div>
                    </div>
                  )}
                  {prediction.pathogen && (
                    <div className="col-span-2 bg-gray-50 dark:bg-fantasy-darker/50 p-3 rounded-lg border border-gray-100 dark:border-fantasy-accent/10">
                      <div className="text-[10px] font-bold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-1">
                        {language === "en" ? "Pathogen" : "ರೋಗಕಾರಕ"}
                      </div>
                      <div className="font-semibold text-gray-800 dark:text-gray-200" title={language === "en" ? prediction.pathogen : prediction.pathogen_kn}>
                        {language === "en" ? prediction.pathogen : prediction.pathogen_kn}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {prediction.severity_score !== undefined && (
                <div className="mb-8">
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-sm font-medium text-gray-600 dark:text-fantasy-silver/80">
                      {language === "en" ? "Risk Meter" : "ಅಪಾಯದ ಮಟ್ಟ"}
                    </span>
                    <span className={`text-sm font-bold ${
                      prediction.severity_color === 'red' ? 'text-red-500' :
                      prediction.severity_color === 'orange' ? 'text-amber-500' :
                      prediction.severity_color === 'yellow' ? 'text-yellow-500' : 'text-green-500'
                    }`}>{prediction.severity_score}%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-fantasy-darker rounded-full h-1.5 border border-gray-300 dark:border-fantasy-accent/20 overflow-hidden">
                    <div 
                      className={`h-1.5 rounded-full ${
                        prediction.severity_color === 'red' ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]' :
                        prediction.severity_color === 'orange' ? 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.8)]' :
                        prediction.severity_color === 'yellow' ? 'bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.8)]' : 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)]'
                      }`}
                      style={{ width: `${prediction.severity_score}%` }}
                    ></div>
                  </div>
                </div>
              )}

              <div className="flex-grow">
                <h3 className="text-xs font-semibold text-gray-500 dark:text-fantasy-silver/60 uppercase tracking-widest mb-4">
                  {language === "en" ? "Countermeasure Protocols" : "ರೋಗ ನಿಯಂತ್ರಣ ಕ್ರಮಗಳು"}
                </h3>
                <ul className="space-y-3">
                  {(language === "en" ? prediction.prevention_steps : prediction.prevention_steps_kn).map((step, index) => (
                    <li key={index} className="flex items-start text-sm text-gray-700 dark:text-fantasy-silver/90 bg-white dark:bg-fantasy-panel p-4 rounded-lg border border-gray-100 dark:border-fantasy-accent/10 shadow-sm transition-all hover:border-fantasy-indigo/50">
                      <div className="w-6 h-6 rounded bg-fantasy-indigo/10 dark:bg-fantasy-indigo/20 flex items-center justify-center text-fantasy-indigo font-bold mr-3 flex-shrink-0 mt-[-2px]">
                        {index + 1}
                      </div>
                      <span className="leading-relaxed">{step}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default DiseaseDetection;