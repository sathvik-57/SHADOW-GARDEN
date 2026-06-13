/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Outfit', 'sans-serif'],
      },
      colors: {
        fantasy: {
          dark: '#09090B',
          darker: '#050507',
          panel: '#111827',
          panel_light: '#1A1A2E',
          panel_lighter: '#16213E',
          accent: '#8B5CF6', // Violet
          accent_hover: '#7C3AED',
          cyan: '#06B6D4',
          indigo: '#4F46E5',
          silver: '#E5E7EB',
          // Light theme
          ivory: '#F9FAFB',
          soft_gray: '#F3F4F6',
          muted_blue: '#E0E7FF'
        }
      },
      boxShadow: {
        'glow-violet': '0 0 15px -3px rgba(139, 92, 246, 0.4)',
        'glow-cyan': '0 0 15px -3px rgba(6, 182, 212, 0.4)',
        'glow-indigo': '0 0 15px -3px rgba(79, 70, 229, 0.4)',
        'glass': '0 4px 30px rgba(0, 0, 0, 0.1)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: 1, boxShadow: '0 0 10px rgba(139, 92, 246, 0.5)' },
          '50%': { opacity: .5, boxShadow: '0 0 20px rgba(139, 92, 246, 0.8)' },
        }
      }
    },
  },
  plugins: [],
}
