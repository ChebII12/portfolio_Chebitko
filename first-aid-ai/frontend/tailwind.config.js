/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary Colors
        primary: 'rgb(var(--color-primary) / <alpha-value>)',
        'primary-container': 'rgb(var(--color-primary-container) / <alpha-value>)',
        'on-primary': 'rgb(var(--color-on-primary) / <alpha-value>)',
        'primary-fixed': 'rgb(var(--color-primary-fixed) / <alpha-value>)',
        'primary-fixed-dim': 'rgb(var(--color-primary-fixed-dim) / <alpha-value>)',
        'on-primary-fixed': 'rgb(var(--color-on-primary-fixed) / <alpha-value>)',
        'on-primary-container': 'rgb(var(--color-on-primary-container) / <alpha-value>)',
        'inverse-primary': 'rgb(var(--color-inverse-primary) / <alpha-value>)',

        // Secondary Colors
        secondary: 'rgb(var(--color-secondary) / <alpha-value>)',
        'secondary-container': 'rgb(var(--color-secondary-container) / <alpha-value>)',
        'on-secondary': 'rgb(var(--color-on-secondary) / <alpha-value>)',
        'secondary-fixed': 'rgb(var(--color-secondary-fixed) / <alpha-value>)',
        'secondary-fixed-dim': 'rgb(var(--color-secondary-fixed-dim) / <alpha-value>)',
        'on-secondary-fixed': 'rgb(var(--color-on-secondary-fixed) / <alpha-value>)',
        'on-secondary-container': 'rgb(var(--color-on-secondary-container) / <alpha-value>)',
        'on-secondary-fixed-variant': 'rgb(var(--color-on-secondary-fixed-variant) / <alpha-value>)',

        // Tertiary Colors (Critical/Alert)
        tertiary: 'rgb(var(--color-tertiary) / <alpha-value>)',
        'tertiary-container': 'rgb(var(--color-tertiary-container) / <alpha-value>)',
        'on-tertiary': 'rgb(var(--color-on-tertiary) / <alpha-value>)',
        'tertiary-fixed': 'rgb(var(--color-tertiary-fixed) / <alpha-value>)',
        'tertiary-fixed-dim': 'rgb(var(--color-tertiary-fixed-dim) / <alpha-value>)',
        'on-tertiary-fixed': 'rgb(var(--color-on-tertiary-fixed) / <alpha-value>)',
        'on-tertiary-container': 'rgb(var(--color-on-tertiary-container) / <alpha-value>)',
        'on-tertiary-fixed-variant': 'rgb(var(--color-on-tertiary-fixed-variant) / <alpha-value>)',

        // Neutral/Surface Colors
        surface: 'rgb(var(--color-surface) / <alpha-value>)',
        'surface-bright': 'rgb(var(--color-surface-bright) / <alpha-value>)',
        'surface-dim': 'rgb(var(--color-surface-dim) / <alpha-value>)',
        'surface-container': 'rgb(var(--color-surface-container) / <alpha-value>)',
        'surface-container-low': 'rgb(var(--color-surface-container-low) / <alpha-value>)',
        'surface-container-high': 'rgb(var(--color-surface-container-high) / <alpha-value>)',
        'surface-container-highest': 'rgb(var(--color-surface-container-highest) / <alpha-value>)',
        'surface-container-lowest': 'rgb(var(--color-surface-container-lowest) / <alpha-value>)',
        'surface-variant': 'rgb(var(--color-surface-variant) / <alpha-value>)',
        'surface-tint': 'rgb(var(--color-surface-tint) / <alpha-value>)',

        // Text & Outline Colors
        'on-surface': 'rgb(var(--color-on-surface) / <alpha-value>)',
        'on-surface-variant': 'rgb(var(--color-on-surface-variant) / <alpha-value>)',
        background: 'rgb(var(--color-background) / <alpha-value>)',
        'on-background': 'rgb(var(--color-on-background) / <alpha-value>)',
        outline: 'rgb(var(--color-outline) / <alpha-value>)',
        'outline-variant': 'rgb(var(--color-outline-variant) / <alpha-value>)',
        'inverse-surface': 'rgb(var(--color-inverse-surface) / <alpha-value>)',
        'inverse-on-surface': 'rgb(var(--color-inverse-on-surface) / <alpha-value>)',

        // Semantic Colors
        error: 'rgb(var(--color-error) / <alpha-value>)',
        'error-container': 'rgb(var(--color-error-container) / <alpha-value>)',
        'on-error': 'rgb(var(--color-on-error) / <alpha-value>)',
        'on-error-container': 'rgb(var(--color-on-error-container) / <alpha-value>)',
      },
      fontFamily: {
        headline: ['Manrope', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        label: ['Inter', 'sans-serif']
      },
      fontSize: {
        // Display sizes
        'display-small': ['32px', { lineHeight: '1.2', fontWeight: '700' }],
        'display-medium': ['28px', { lineHeight: '1.3', fontWeight: '700' }],
        'display-large': ['36px', { lineHeight: '1.1', fontWeight: '800' }],

        // Headline sizes
        'headline-1': ['24px', { lineHeight: '1.2', fontWeight: '800', letterSpacing: '-0.5px' }],
        'headline-2': ['20px', { lineHeight: '1.2', fontWeight: '700', letterSpacing: '-0.25px' }],
        'headline-3': ['18px', { lineHeight: '1.2', fontWeight: '700' }],

        // Body sizes
        'body-large': ['18px', { lineHeight: '1.6', fontWeight: '400' }],
        'body-medium': ['16px', { lineHeight: '1.5', fontWeight: '400' }],
        'body-small': ['14px', { lineHeight: '1.4', fontWeight: '400' }],

        // Label sizes
        'label-large': ['14px', { lineHeight: '1.2', fontWeight: '600', letterSpacing: '0.5px' }],
        'label-medium': ['12px', { lineHeight: '1.2', fontWeight: '600', letterSpacing: '0.4px' }],
        'label-small': ['11px', { lineHeight: '1.2', fontWeight: '600', letterSpacing: '0.3px' }],
      },
      borderRadius: {
        'DEFAULT': '1rem', // 16px
        'lg': '2rem',      // 32px
        'xl': '3rem',      // 48px
        'full': '9999px'   // Fully rounded
      },
      spacing: {
        'xs': '4px',    // 0.5 units
        'sm': '8px',    // 1 unit
        'md': '16px',   // 2 units
        'lg': '24px',   // 3 units
        'xl': '32px',   // 4 units
        '2xl': '48px',  // 6 units
        '3xl': '64px',  // 8 units
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        'card-hover': '0 12px 32px rgba(0, 50, 125, 0.06)',
        'emergency': '0 8px 30px rgba(116, 0, 10, 0.2)',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'progress-fill': 'progress-fill 700ms ease-out forwards',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(1.05)' },
        },
        'progress-fill': {
          'from': { width: '0%' },
          'to': { width: 'var(--progress-width, 33%)' },
        },
      },
      zIndex: {
        'base': '0',
        'dropdown': '1000',
        'sticky': '1020',
        'fixed': '1030',
        'modal': '1040',
        'popover': '1050',
        'tooltip': '1060',
        'toast': '1070',
      },
    },
  },
  plugins: [],
}
