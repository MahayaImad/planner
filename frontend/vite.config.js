import path from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      injectRegister: "auto",
      registerType: "autoUpdate",
      devOptions: { enabled: false }, // désactivé en dev (évite les conflits)
      workbox: {
        clientsClaim: true,
        skipWaiting: true,
        // SPA routing : le SW sert toujours index.html pour les navigations
        navigateFallback: "index.html",
        navigateFallbackDenylist: [/^\/api/], // ne pas intercepter les appels API
      }
    })
  ],
  build: {
    chunkSizeWarningLimit: 2000
  },
  resolve: {
    alias: {
      app: path.resolve(__dirname, "src/app")
    }
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, "")
      }
    }
  }
});
