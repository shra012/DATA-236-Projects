import daisyui from 'daisyui';

const missionTheme = {
  primary: '#2563eb',
  'primary-content': '#ffffff',
  secondary: '#7c3aed',
  accent: '#f97316',
  neutral: '#1f2937',
  'neutral-content': '#f3f4f6',
  'base-100': '#f8fafc',
  'base-200': '#e2e8f0',
  'base-300': '#cbd5f5',
  info: '#2563eb',
  success: '#16a34a',
  warning: '#f59e0b',
  error: '#dc2626',
};

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Inter Tight"', 'Inter', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        mission: missionTheme,
      },
      'light',
    ],
    darkTheme: 'mission',
    base: true,
  },
};
