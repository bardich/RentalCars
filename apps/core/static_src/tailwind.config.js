/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../../../templates/**/*.html',
    '../../../**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0F172A',
        secondary: '#1E293B',
        accent: '#F59E0B',
        highlight: '#22C55E',
        background: '#F8FAFC',
        muted: '#64748B',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
