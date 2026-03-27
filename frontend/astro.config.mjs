// @ts-check
import { defineConfig } from 'astro/config';

export default defineConfig({
  devToolbar: { enabled: false },
  server: {
    port: 4321,
    host: true,
    headers: {
      // ACTUALIZADO: Añadimos Google Fonts y Cloudinary (que veo que usas en los logs)
      "Content-Security-Policy": "default-src 'self' 'unsafe-inline' 'unsafe-eval'; " +
      "connect-src 'self' https://yaretzi-asbestous-jerrell.ngrok-free.dev https://*.ngrok-free.app ws://localhost:* wss://yaretzi-asbestous-jerrell.ngrok-free.dev http://localhost:8000 https://localhost:8000;" +
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; " + // Permite SweetAlert y Chart.js
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; " + // Permite Bootstrap y FontAwesome
      "img-src 'self' data: https://res.cloudinary.com https:; " +
      "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com;"
    }
  },
  vite: {
    esbuild: { target: 'es2020' },
    build: { target: 'es2020' },
    server: {
      hmr: {
        clientPort: 443, // Forzar a que use el puerto seguro de ngrok
      },
      allowedHosts: ['.ngrok-free.dev', '.ngrok-free.app'],
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          // rewrite: (path) => path.replace(/^\/api/, '') // Solo si tu FastAPI NO espera el prefijo /api
        }
      }
    }
  }
});