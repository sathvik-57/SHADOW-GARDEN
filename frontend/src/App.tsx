import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from "react-router-dom";
import WelcomePage from "./pages/WelcomePage";
import WeatherDashboard from "./pages/WeatherDashboard";
import CropRecommendation from "./pages/CropRecommendation";
import DiseaseDetection from "./pages/DiseaseDetection";
import Home from "./pages/Home";
import { useTheme } from "./context/ThemeContext";
import { useLanguage } from "./context/LanguageContext";
import { Moon, Sun, Menu, X, Languages, Leaf, Sparkles, Users } from "lucide-react";
import ParticleBackground from "./components/ParticleBackground";

const Navigation = () => {
  const { theme, toggleTheme } = useTheme();
  const { language, toggleLanguage } = useLanguage();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { path: "/", label: "Dashboard" },
    { path: "/recommendation", label: "Crop Advisor" },
    { path: "/disease", label: "Disease Detection" },
    { path: "/weather", label: "Atmosphere" },
  ];

  return (
    <>
      <nav className="sticky top-0 z-50 glass-panel-light dark:glass-panel-dark mx-4 mt-4 px-6 py-4 flex justify-between items-center transition-all duration-300">
        <Link to="/" className="flex items-center space-x-3 group cursor-pointer z-50">
          <div className="relative flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-tr from-[#4c1d95] via-fantasy-indigo to-fantasy-cyan shadow-[0_0_15px_rgba(99,102,241,0.5)] overflow-hidden group-hover:shadow-[0_0_25px_rgba(34,211,238,0.7)] transition-all duration-1000 transform group-hover:rotate-[360deg]">
            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-20"></div>
            <div className="absolute inset-0 bg-white/0 group-hover:bg-white/20 blur-md group-hover:scale-150 transition-all duration-700 ease-out"></div>
            <Leaf size={22} className="text-white relative z-10 animate-float drop-shadow-md" style={{ animationDuration: '3.5s' }} />
            <Sparkles size={12} className="text-yellow-200 absolute top-2 right-2 opacity-0 group-hover:opacity-100 group-hover:animate-pulse transition-opacity duration-700 delay-300 z-20" />
            <Sparkles size={8} className="text-cyan-200 absolute bottom-2 left-2 opacity-0 group-hover:opacity-100 group-hover:animate-pulse transition-opacity duration-700 delay-100 z-20" />
          </div>
          <div className="flex flex-col justify-center ml-2">
            <span style={{ fontFamily: 'Georgia, "Times New Roman", serif' }} className="text-3xl font-bold italic tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600 dark:from-purple-200 dark:via-indigo-200 dark:to-cyan-200 group-hover:from-purple-500 group-hover:to-cyan-400 transition-all duration-700 leading-none drop-shadow-sm">
              Shadow
            </span>
            <span className="text-xs font-bold tracking-[0.4em] text-fantasy-indigo dark:text-fantasy-cyan uppercase opacity-70 group-hover:opacity-100 group-hover:tracking-[0.6em] transition-all duration-700 ease-out leading-none mt-1 pl-1">
              Garden
            </span>
          </div>
        </Link>
        
        {/* Desktop Nav */}
        <div className="hidden md:flex items-center space-x-1">
          {navLinks.map((link) => {
            const isActive = location.pathname === link.path || 
                            (link.path === "/" && location.pathname === "/dashboard");
            return (
              <Link 
                key={link.path} 
                to={link.path} 
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  isActive 
                    ? "bg-fantasy-accent/10 text-fantasy-accent dark:text-fantasy-cyan dark:bg-fantasy-cyan/10" 
                    : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-fantasy-panel_lighter"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </div>

        <div className="flex items-center space-x-4">
          <button 
            onClick={toggleLanguage}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gray-100 dark:bg-fantasy-panel_lighter text-gray-600 dark:text-fantasy-silver hover:bg-gray-200 dark:hover:bg-fantasy-accent/20 transition-all duration-300 text-sm font-medium"
            aria-label="Toggle Language"
          >
            <Languages size={16} className={language === 'kn' ? 'text-fantasy-cyan' : 'text-fantasy-indigo'} />
            {language === 'en' ? 'ಕನ್ನಡ' : 'EN'}
          </button>
          
          <button 
            onClick={toggleTheme}
            className="p-2 rounded-full bg-gray-100 dark:bg-fantasy-panel_lighter text-gray-600 dark:text-fantasy-silver hover:bg-gray-200 dark:hover:bg-fantasy-accent/20 transition-all duration-300"
            aria-label="Toggle Theme"
          >
            {theme === 'dark' ? <Sun size={20} className="text-fantasy-cyan" /> : <Moon size={20} className="text-fantasy-accent" />}
          </button>
          
          {/* About Us Hover Dropdown */}
          <div className="relative group">
            <button 
              className="p-2 rounded-full bg-gray-100 dark:bg-fantasy-panel_lighter text-gray-600 dark:text-fantasy-silver hover:bg-gray-200 dark:hover:bg-fantasy-accent/20 transition-all duration-300"
              aria-label="About Us"
            >
              <Users size={20} className="group-hover:text-fantasy-cyan transition-colors" />
            </button>
            
            <div className="absolute right-0 top-full mt-2 w-72 glass-panel-light dark:glass-panel-dark p-5 rounded-xl shadow-2xl transition-all duration-300 opacity-0 invisible group-hover:opacity-100 group-hover:visible translate-y-2 group-hover:translate-y-0 border border-gray-200 dark:border-fantasy-accent/30 z-50">
              <div className="absolute -top-2 right-4 w-4 h-4 bg-white dark:bg-[#1a1c29] border-t border-l border-gray-200 dark:border-fantasy-accent/30 rotate-45"></div>
              <h4 className="text-xs font-bold text-gray-800 dark:text-white uppercase tracking-widest mb-4 flex items-center border-b border-gray-200 dark:border-fantasy-panel_lighter pb-3 relative z-10">
                <Sparkles size={14} className="text-fantasy-cyan mr-2" />
                {language === 'en' ? 'Project Team' : 'ಯೋಜನಾ ತಂಡ'}
              </h4>
              <ul className="space-y-4 relative z-10">
                <li className="flex items-center group/item">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-fantasy-indigo to-fantasy-cyan flex items-center justify-center text-white font-bold text-sm mr-3 shadow-glow-violet group-hover/item:scale-110 transition-transform">
                    SK
                  </div>
                  <div>
                    <div className="text-sm font-bold text-gray-800 dark:text-gray-200">Sathvik K Y</div>
                    <div className="text-[10px] text-gray-500 dark:text-fantasy-silver/70 uppercase tracking-widest">Developer</div>
                  </div>
                </li>
                <li className="flex items-center group/item">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#8b5cf6] to-[#ec4899] flex items-center justify-center text-white font-bold text-sm mr-3 shadow-[0_0_10px_rgba(236,72,153,0.5)] group-hover/item:scale-110 transition-transform">
                    ST
                  </div>
                  <div>
                    <div className="text-sm font-bold text-gray-800 dark:text-gray-200">Sashank Talapaneni</div>
                    <div className="text-[10px] text-gray-500 dark:text-fantasy-silver/70 uppercase tracking-widest">Developer</div>
                  </div>
                </li>
              </ul>
            </div>
          </div>
          
          {/* Mobile Menu Button */}
          <button 
            className="md:hidden p-2 text-gray-600 dark:text-fantasy-silver focus:outline-none"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </nav>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-40 bg-black/50 backdrop-blur-sm animate-fade-in" onClick={() => setMobileMenuOpen(false)}>
          <div 
            className="absolute right-0 top-0 bottom-0 w-64 glass-panel-light dark:glass-panel-dark p-6 flex flex-col space-y-4 shadow-[-10px_0_30px_rgba(0,0,0,0.5)] animate-slide-up"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex justify-end mb-4">
              <button onClick={() => setMobileMenuOpen(false)} className="text-gray-500 dark:text-fantasy-silver">
                <X size={24} />
              </button>
            </div>
            {navLinks.map((link) => {
              const isActive = location.pathname === link.path || 
                              (link.path === "/" && location.pathname === "/dashboard");
              return (
                <Link 
                  key={link.path} 
                  to={link.path} 
                  onClick={() => setMobileMenuOpen(false)}
                  className={`px-4 py-3 rounded-lg text-base font-medium transition-all duration-300 block ${
                    isActive 
                      ? "bg-fantasy-accent/10 text-fantasy-accent dark:text-fantasy-cyan dark:bg-fantasy-cyan/10" 
                      : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-fantasy-panel_lighter"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </>
  );
};

const App: React.FC = () => {
  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <div className="min-h-screen flex flex-col relative">
        <ParticleBackground />
        <Navigation />

        <main className="container mx-auto p-4 flex-grow flex flex-col animate-fade-in">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/welcome" element={<WelcomePage />} />
            <Route path="/recommendation" element={<CropRecommendation />} />
            <Route path="/disease" element={<DiseaseDetection />} />
            <Route path="/weather" element={<WeatherDashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;