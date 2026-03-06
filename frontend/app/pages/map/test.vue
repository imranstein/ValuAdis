<template>
  <div class="map-test-page">
    <h1>Map Test Page</h1>
    <p>This is a test to see if the map page loads correctly.</p>
    
    <div class="test-content">
      <h2>Ethiopian Properties</h2>
      <ul>
        <li v-for="property in properties" :key="property.id">
          {{ property.title }} - {{ property.address }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { seedProperties } from '~/data/seedProperties.js'

const properties = seedProperties
</script>

<style scoped>
.map-test-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.test-content {
  margin-top: 32px;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  padding: 8px 0;
  border-bottom: 1px solid #e5e7eb;
}
</style>
