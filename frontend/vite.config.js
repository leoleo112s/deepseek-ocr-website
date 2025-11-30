import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5287,
    proxy: {
      '/api': {
        target: 'http://localhost:7539',
        changeOrigin: true
      }
    }
  }
})
