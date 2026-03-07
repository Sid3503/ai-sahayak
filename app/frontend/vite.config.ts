import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Proxy friend's Control Centre so iframe loads from SAME ORIGIN (avoids cross-origin framing block)
      // No rewrite: friend's app has base '/control-centre/' so it only serves at that path
      '/control-centre': {
        target: 'http://localhost:5174',
        changeOrigin: true,
        ws: true,
      },
      // Friend's dashboard API (Flask on 8001) – needed when Control Centre is embedded in our app
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
})
