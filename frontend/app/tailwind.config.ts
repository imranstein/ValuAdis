import type { Config } from 'tailwindcss'

/**
 * ValuAdis "Ethiopian civic-tech ledger" tokens.
 * Source of truth: assets/css/main.css custom properties.
 * Mirror changes in frontend/design-tokens.json.
 */
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
        canvas: '#f6f3ea',
        surface: {
          DEFAULT: '#fcfaf3',
          2: '#eeeadd',
          3: '#e5e0cf'
        },
        ink: {
          DEFAULT: '#1b231d',
          soft: '#39443b',
          muted: '#5c665d'
        },
        line: {
          DEFAULT: '#ded8c6',
          strong: '#c2bba4'
        },
        primary: {
          50: '#eef3ee',
          100: '#dfe8dd',
          200: '#bcd1c2',
          300: '#8fb29b',
          400: '#5c8a70',
          500: '#235c43',
          600: '#1d4f39',
          700: '#163c2b',
          800: '#102c20',
          900: '#0a1d15'
        },
        gold: {
          50: '#faf4e4',
          100: '#f3e9d0',
          200: '#e7d3a2',
          300: '#d8b96c',
          400: '#c79a3e',
          500: '#a97c22',
          600: '#8a5f14',
          700: '#6e4b10',
          800: '#52370c',
          900: '#382507'
        },
        shell: {
          DEFAULT: '#131f18',
          raised: '#1c2b21',
          active: '#23392c',
          ink: '#f1eee0',
          muted: '#9db0a0',
          gold: '#d3a94c'
        },
        danger: {
          DEFAULT: '#9d3a28',
          soft: '#f3ddd5'
        },
        info: {
          DEFAULT: '#33566a',
          soft: '#dfe8ec'
        }
      },
      fontFamily: {
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
        display: ['DM Sans', 'system-ui', 'sans-serif'],
        serif: ['Cormorant Garamond', 'Georgia', 'serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      borderRadius: {
        sm: '4px',
        DEFAULT: '8px',
        lg: '12px',
        xl: '16px'
      },
      boxShadow: {
        sm: '0 8px 24px rgba(27, 35, 29, 0.06)',
        DEFAULT: '0 18px 45px rgba(27, 35, 29, 0.09)',
        lg: '0 28px 70px rgba(27, 35, 29, 0.14)'
      },
      transitionDuration: {
        fast: '120ms',
        normal: '180ms',
        slow: '320ms'
      },
      transitionTimingFunction: {
        ledger: 'cubic-bezier(0.23, 1, 0.32, 1)'
      },
      letterSpacing: {
        amharic: '0.05em',
        kicker: '0.18em'
      }
    }
  },
  plugins: []
} satisfies Config
