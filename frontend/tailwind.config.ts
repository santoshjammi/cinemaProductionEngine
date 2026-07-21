import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1440px',
      },
    },
    extend: {
      fontFamily: {
        display: ['SF Pro Display', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        body: ['SF Pro Text', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      fontSize: {
        'hero-display': ['56px', { lineHeight: '1.07', letterSpacing: '-0.28px', fontWeight: '600' }],
        'display-lg': ['40px', { lineHeight: '1.10', letterSpacing: '0', fontWeight: '600' }],
        'display-md': ['34px', { lineHeight: '1.47', letterSpacing: '-0.374px', fontWeight: '600' }],
        'lead': ['28px', { lineHeight: '1.14', letterSpacing: '0.196px', fontWeight: '400' }],
        'lead-airy': ['24px', { lineHeight: '1.5', letterSpacing: '0', fontWeight: '300' }],
        'tagline': ['21px', { lineHeight: '1.19', letterSpacing: '0.231px', fontWeight: '600' }],
        'body': ['17px', { lineHeight: '1.47', letterSpacing: '-0.374px', fontWeight: '400' }],
        'body-strong': ['17px', { lineHeight: '1.24', letterSpacing: '-0.374px', fontWeight: '600' }],
        'caption': ['14px', { lineHeight: '1.43', letterSpacing: '-0.224px', fontWeight: '400' }],
        'caption-strong': ['14px', { lineHeight: '1.29', letterSpacing: '-0.224px', fontWeight: '600' }],
        'fine-print': ['12px', { lineHeight: '1.0', letterSpacing: '-0.12px', fontWeight: '400' }],
        'nav-link': ['12px', { lineHeight: '1.0', letterSpacing: '-0.12px', fontWeight: '400' }],
      },
      colors: {
        primary: {
          DEFAULT: '#0066cc',
          foreground: '#ffffff',
          focus: '#0071e3',
          'on-dark': '#2997ff',
        },
        canvas: '#ffffff',
        'canvas-parchment': '#f5f5f7',
        'surface-pearl': '#fafafc',
        'surface-tile-1': '#272729',
        'surface-tile-2': '#2a2a2c',
        'surface-tile-3': '#252527',
        'surface-black': '#000000',
        ink: '#1d1d1f',
        'ink-muted-80': '#333333',
        'ink-muted-48': '#7a7a7a',
        'body-on-dark': '#ffffff',
        'body-muted': '#cccccc',
        'divider-soft': '#f0f0f0',
        hairline: '#e0e0e0',
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: '#0066cc',
        background: '#ffffff',
        foreground: '#1d1d1f',
        secondary: {
          DEFAULT: '#f5f5f7',
          foreground: '#1d1d1f',
        },
        destructive: {
          DEFAULT: '#ff3b30',
          foreground: '#ffffff',
        },
        muted: {
          DEFAULT: '#f5f5f7',
          foreground: '#7a7a7a',
        },
        accent: {
          DEFAULT: '#0066cc',
          foreground: '#ffffff',
        },
        popover: {
          DEFAULT: '#ffffff',
          foreground: '#1d1d1f',
        },
        card: {
          DEFAULT: '#ffffff',
          foreground: '#1d1d1f',
        },
      },
      borderRadius: {
        none: '0px',
        xs: '5px',
        sm: '8px',
        md: '11px',
        lg: '18px',
        pill: '9999px',
        full: '9999px',
      },
      spacing: {
        xxs: '4px',
        xs: '8px',
        sm: '12px',
        md: '17px',
        lg: '24px',
        xl: '32px',
        xxl: '48px',
        section: '80px',
      },
      boxShadow: {
        'product': 'rgba(0, 0, 0, 0.22) 3px 5px 30px 0px',
        'hairline': '0 0 0 1px rgba(0, 0, 0, 0.08)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
        'pulse-slow': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
        'pulse-slow': 'pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;
