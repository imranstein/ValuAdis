// Runs only on the client.  Restores the user session from the stored JWT
// so the Pinia auth store is populated on every page load / refresh.
export default defineNuxtPlugin(async () => {
  const authStore = useAuthStore()
  await authStore.initialize()
})
