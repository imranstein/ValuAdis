import type { Config } from 'tailwindcss'

export default {
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}',
    './app.vue',
    './error.vue'
  ],
  theme: {
    extend: {
      colors: {
        // Ethiopian Color Palette
        ethiopian: {
          green: '#078160',
          'green-light': '#10B981',
          'green-dark': '#065F46',
          blue: '#1E3A8A',
          'blue-light': '#3B82F6',
          'blue-dark': '#1E40AF',
          orange: '#EA580C',
          'orange-light': '#F97316',
          'orange-dark': '#C2410C',
          teal: '#0F766E',
          gold: '#F59E0B',
          brown: '#92400E',
          'sky-blue': '#0EA5E9',
          'earth-brown': '#A16207'
        },
        // Primary/Secondary/Accent
        primary: {
          50: '#F0FDF4',
          100: '#DCFCE7',
          200: '#BBF7D0',
          300: '#86EFAC',
          400: '#4ADE80',
          500: '#078160',
          600: '#065F46',
          700: '#064E3B',
          800: '#053B29',
          900: '#022C1F'
        },
        secondary: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#1E3A8A',
          600: '#1E40AF',
          700: '#1D4ED8',
          800: '#1E3A8A',
          900: '#1E3A8A'
        },
        accent: {
          50: '#FFF7ED',
          100: '#FFEDD5',
          200: '#FED7AA',
          300: '#FDBA74',
          400: '#FB923C',
          500: '#EA580C',
          600: '#DC2626',
          700: '#C2410C',
          800: '#9A3412',
          900: '#7C2D12'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem'
      },
      letterSpacing: {
        'amharic': '0.05em'
      },
      boxShadow: {
        'ethiopian': '0 4px 6px -1px rgba(7, 129, 96, 0.1), 0 2px 4px -1px rgba(7, 129, 96, 0.06)',
        'ethiopian-lg': '0 10px 15px -3px rgba(7, 129, 96, 0.1), 0 4px 6px -2px rgba(7, 129, 96, 0.05)'
      }
    }
  },
  plugins: []
} satisfies Config
