import { defineConfig } from 'vite'
import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8080',
      // [챗봇] 추가 : /pyapi/chat → Python 서버 http://localhost:8000/chat
      '/pyapi': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/pyapi/, ''),
      },
    },
  },
  plugins: [
    react(),
    babel({ presets: [reactCompilerPreset()] }),
    tailwindcss(),
  ],
})
