import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    include: ['**/*.{test,spec}.{ts,js,vue}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['components/**', 'composables/**', 'stores/**', 'utils/**'],
      exclude: ['node_modules', 'tests', '**/*.d.ts']
    }
  },
  resolve: {
    alias: {
      '~': fileURLToPath(new URL('./', import.meta.url)),
      '#app': fileURLToPath(new URL('./tests/stubs/nuxtApp.ts', import.meta.url)),
      '#imports': fileURLToPath(new URL('./tests/stubs/nuxtApp.ts', import.meta.url)),
    }
  }
})
