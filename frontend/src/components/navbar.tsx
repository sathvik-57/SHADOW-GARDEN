import { Link } from "react-router-dom";
import { useState } from "react";
import { Menu, X } from "lucide-react";

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => setIsOpen(!isOpen);

  return (
    <nav className="bg-green-800 text-white px-4 py-3 shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold flex items-center gap-2">
          🌾 Shadow Garden
        </Link>

        {/* Desktop Menu */}
        <div className="hidden md:flex gap-6">
          <Link to="/" className="hover:text-yellow-300 transition">Home</Link>
          <Link to="/disease" className="hover:text-yellow-300 transition">Disease Detection</Link>
          <Link to="/recommend" className="hover:text-yellow-300 transition">Crop Advisor</Link>
        </div>

        {/* Mobile Hamburger */}
        <div className="md:hidden">
          <button onClick={toggleMenu}>
            {isOpen ? <X size={28} /> : <Menu size={28} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {isOpen && (
        <div className="md:hidden mt-2 space-y-2">
          <Link to="/" onClick={toggleMenu} className="block px-2 py-1 hover:bg-green-700 rounded">Home</Link>
          <Link to="/disease" onClick={toggleMenu} className="block px-2 py-1 hover:bg-green-700 rounded">Disease Detection</Link>
          <Link to="/recommend" onClick={toggleMenu} className="block px-2 py-1 hover:bg-green-700 rounded">Crop Advisor</Link>
        </div>
      )}
    </nav>
  );
}

export default Navbar;
