import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { SensorProvider } from "./context/SensorContext";
import { ThemeProvider } from "./context/ThemeContext";
import { LanguageProvider } from "./context/LanguageContext";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeProvider>
      <LanguageProvider>
        <SensorProvider>
          <App />
        </SensorProvider>
      </LanguageProvider>
    </ThemeProvider>
  </React.StrictMode>
);
