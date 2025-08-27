module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        neon: '#00fff7',
        glow: '#a855f7',
      },
      boxShadow: {
        glass: '0 4px 32px rgba(0,255,247,0.15), 0 1.5px 8px rgba(168,85,247,0.32)',
        neon: '0 0 24px #a855f7, 0 0 48px #00fff7',
      },
      backgroundImage: {
        'gradient-glass': 'linear-gradient(135deg, rgba(168,85,247,0.25) 0%, rgba(0,255,247,0.18) 100%)',
      }
    },
  },
  plugins: [],
}
