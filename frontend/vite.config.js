import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev server will forward API/image calls to Flask (http://localhost:5000)
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '^/(analyze|build_report|dataset|viz|reports)': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})
