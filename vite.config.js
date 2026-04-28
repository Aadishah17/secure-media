import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/upload': {
        target: process.env.VITE_BACKEND_PROXY_TARGET || 'http://127.0.0.1:5000',
        changeOrigin: true
      },
      '/api/health': {
        target: process.env.VITE_BACKEND_PROXY_TARGET || 'http://127.0.0.1:5000',
        changeOrigin: true
      }
    }
  },
  test: {
    environment: 'jsdom',
    globals: true
  }
})
