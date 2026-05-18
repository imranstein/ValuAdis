<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const route = useRoute()

await navigateTo({
  path: '/vehicles/create',
  query: route.query,
}, { replace: true })
</script>
