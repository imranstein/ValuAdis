<template>
  <div id="app">
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
    <Toast />
  </div>
</template>

<script setup lang="ts">
// Removed useHead to fix maximum call stack size exceeded error
</script>

<style>
#app {
  min-height: 100vh;
}
</style>
