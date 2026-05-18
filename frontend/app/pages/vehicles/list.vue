<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

await navigateTo('/vehicles', { replace: true })
</script>
