import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// In Docker the API is reachable as http://api:8000; running natively it's localhost.
const apiTarget = process.env.API_PROXY_TARGET ?? 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: apiTarget, changeOrigin: true, ws: true },
    },
  },
})
