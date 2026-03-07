/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'sahayak-green': '#22c55e',
        'sahayak-amber': '#fbbf24',
        // Bharat theme: rich green (not black!), saffron
        'bharat-dark': '#071207',
        'bharat-green': '#0d2818',
        'bharat-green-mid': '#14532d',
        'bharat-saffron': '#f59e0b',
        'bharat-saffron-bright': '#fbbf24',
      },
      keyframes: {
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(24px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.96)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'slide-in-left': {
          '0%': { opacity: '0', transform: 'translateX(-24px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'slide-in-right': {
          '0%': { opacity: '0', transform: 'translateX(24px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        'glow-pulse': {
          '0%, 100%': { boxShadow: '0 0 20px -5px rgba(34, 197, 94, 0.4)' },
          '50%': { boxShadow: '0 0 40px -5px rgba(34, 197, 94, 0.6)' },
        },
        'gradient-shift': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        'soft-pulse': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.92' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'nav-glow': {
          '0%, 100%': { boxShadow: '0 0 0 2px rgba(15, 23, 42, 0.2), 0 4px 12px -2px rgba(15, 23, 42, 0.15)' },
          '50%': { boxShadow: '0 0 0 2px rgba(15, 23, 42, 0.3), 0 4px 20px -2px rgba(15, 23, 42, 0.2)' },
        },
        'nav-connector': {
          '0%': { transform: 'scaleX(0)', opacity: '0.6' },
          '100%': { transform: 'scaleX(1)', opacity: '1' },
        },
        'bharat-breathe': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        'bharat-glow': {
          '0%, 100%': { opacity: '0.85' },
          '50%': { opacity: '1' },
        },
        'chakra-spin': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.7s ease-out forwards',
        'fade-in': 'fade-in 0.6s ease-out forwards',
        'scale-in': 'scale-in 0.5s ease-out forwards',
        'slide-in-left': 'slide-in-left 0.6s ease-out forwards',
        'slide-in-right': 'slide-in-right 0.6s ease-out forwards',
        'float': 'float 4s ease-in-out infinite',
        'glow-pulse': 'glow-pulse 2.5s ease-in-out infinite',
        'gradient-shift': 'gradient-shift 10s ease infinite',
        'shimmer': 'shimmer 3s ease-in-out infinite',
        'soft-pulse': 'soft-pulse 4s ease-in-out infinite',
        'slide-up': 'slide-up 0.6s ease-out forwards',
        'nav-glow': 'nav-glow 2.5s ease-in-out infinite',
        'nav-connector': 'nav-connector 0.4s ease-out forwards',
        'bharat-breathe': 'bharat-breathe 12s ease-in-out infinite',
        'bharat-glow': 'bharat-glow 4s ease-in-out infinite',
        'chakra-spin': 'chakra-spin 90s linear infinite',
      },
      backgroundSize: {
        'gradient-move': '200% 200%',
      },
    },
  },
  plugins: [],
}

