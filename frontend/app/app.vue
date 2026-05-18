<template>
  <div id="app">
    <NuxtLayout>
      <NuxtPage :page-key="route => route.fullPath" />
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
