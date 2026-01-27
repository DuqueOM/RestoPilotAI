/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fef7ee',
          100: '#fdedd6',
          200: '#f9d7ad',
          300: '#f5b978',
          400: '#f09242',
          500: '#ec751d',
          600: '#dd5a13',
          700: '#b74312',
          800: '#923616',
          900: '#762e15',
        },
        secondary: {
          50: '#f4f7f7',
          100: '#e2ebea',
          200: '#c8d9d6',
          300: '#a1bfba',
          400: '#739d97',
          500: '#58827c',
          600: '#456a65',
          700: '#3a5753',
          800: '#324845',
          900: '#2c3e3c',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
