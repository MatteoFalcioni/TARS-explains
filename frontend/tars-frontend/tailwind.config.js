/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html","./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      keyframes: {
        glow: {
          '0%,100%': { boxShadow: '0 0 0px 0 rgba(56,189,248,0.0)' },
          '50%': { boxShadow: '0 0 28px 6px rgba(56,189,248,0.45)' },
        },
        ripple: {
          '0%':   { transform: 'scale(1)',   opacity: '0.6' },
          '100%': { transform: 'scale(1.9)', opacity: '0'   },
        },
      },
      animation: {
        'glow-slow': 'glow 2.4s ease-in-out infinite',
        'ripple-slow': 'ripple 1.6s ease-out infinite',
      },
    },
  },
  plugins: [],
}