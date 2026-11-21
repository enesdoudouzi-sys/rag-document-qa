import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/dokument': 'http://localhost:8000', '/fragen': 'http://localhost:8000', '/dokumente': 'http://localhost:8000', '/health': 'http://localhost:8000' } }
})
