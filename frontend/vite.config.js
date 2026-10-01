import { sveltekit } from '@sveltejs/kit/vite'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'
import { SvelteKitPWA } from '@vite-pwa/sveltekit'
import adapter from '@sveltejs/adapter-static'

export default defineConfig({
  plugins: [
    tailwindcss(),
    // 1. Pass the static adapter configuration directly to the sveltekit plugin
    sveltekit({
      adapter: adapter({
        pages: 'build',
        assets: 'build',
        fallback: 'index.html', // Crucial for client-side routing in a true SPA
        precompress: false,
        strict: true,
      }),
    }),
    // 2. Add the PWA build generator configuration block
    SvelteKitPWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'CeroHumano',
        short_name: 'CeroHumano',
        description: 'Mobile-first CeroHumano JavaScript SPA PWA',
        theme_color: '#ffffff',
        background_color: '#ffffff',
        display: 'standalone', // Hides the web browser address bars
        orientation: 'portrait',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
    }),
  ],
})
