import React from "react";
import { Link } from "react-router-dom";
import { Sprout, Microscope, Leaf } from "lucide-react";

const WelcomePage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 animate-float">
      <div className="text-center mb-16 relative">
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-fantasy-accent/20 rounded-full blur-[80px] -z-10"></div>
        <h1 className="text-5xl md:text-6xl font-extrabold mb-6 tracking-tight text-gray-900 dark:text-white drop-shadow-lg">
          Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-fantasy-indigo to-fantasy-cyan">Shadow Garden</span>
        </h1>
        <p className="text-xl text-gray-600 dark:text-fantasy-silver max-w-2xl mx-auto font-light leading-relaxed">
          Advanced agricultural intelligence forged through archaic wisdom and arcane technology. 
          Discover optimal crop selection, disease detection, and precision metrics.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto w-full">
        
        <Link to="/" className="fantasy-card p-8 group">
          <div className="w-14 h-14 rounded-full bg-fantasy-indigo/10 dark:bg-fantasy-indigo/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
            <Sprout className="text-fantasy-indigo w-7 h-7" />
          </div>
          <h2 className="text-2xl font-bold mb-3 text-gray-800 dark:text-white group-hover:text-fantasy-indigo transition-colors duration-300">Dashboard</h2>
          <p className="text-gray-600 dark:text-fantasy-silver/80">
            Monitor real-time arcane telemetry and environmental sensor arrays from the field.
          </p>
        </Link>

        <Link to="/recommendation" className="fantasy-card p-8 group">
          <div className="w-14 h-14 rounded-full bg-fantasy-accent/10 dark:bg-fantasy-accent/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
            <Leaf className="text-fantasy-accent w-7 h-7" />
          </div>
          <h2 className="text-2xl font-bold mb-3 text-gray-800 dark:text-white group-hover:text-fantasy-accent transition-colors duration-300">Crop Advisor</h2>
          <p className="text-gray-600 dark:text-fantasy-silver/80">
            Utilize predictive alchemy to determine the optimal crop and nutrient compounds for your soil.
          </p>
        </Link>

        <Link to="/disease" className="fantasy-card p-8 group">
          <div className="w-14 h-14 rounded-full bg-fantasy-cyan/10 dark:bg-fantasy-cyan/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
            <Microscope className="text-fantasy-cyan w-7 h-7" />
          </div>
          <h2 className="text-2xl font-bold mb-3 text-gray-800 dark:text-white group-hover:text-fantasy-cyan transition-colors duration-300">Pathogen Detection</h2>
          <p className="text-gray-600 dark:text-fantasy-silver/80">
            Scan botanical samples for biological threats and receive specialized prevention protocols.
          </p>
        </Link>

      </div>
    </div>
  );
};

export default WelcomePage;