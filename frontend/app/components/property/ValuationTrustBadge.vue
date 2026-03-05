<template>
  <div class="trust-badge" :class="badgeClass" :title="tooltip">
    <i :class="badgeIcon" class="badge-icon" />
    <span class="badge-label">{{ badgeLabel }}</span>
    <span class="badge-score">{{ score?.toFixed(0) }}%</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  score: number | null
  totalReviews?: number
}>()

const badgeClass = computed(() => {
  if (props.score === null) return 'badge-unknown'
  if (props.score >= 80) return 'badge-high'
  if (props.score >= 60) return 'badge-moderate'
  return 'badge-low'
})

const badgeIcon = computed(() => {
  if (props.score === null) return 'pi pi-question-circle'
  if (props.score >= 80) return 'pi pi-check-circle'
  if (props.score >= 60) return 'pi pi-info-circle'
  return 'pi pi-exclamation-triangle'
})

const badgeLabel = computed(() => {
  if (props.score === null) return 'No Data'
  if (props.score >= 80) return 'High Confidence'
  if (props.score >= 60) return 'Moderate Confidence'
  return 'Low Confidence'
})

const tooltip = computed(() => {
  const n = props.totalReviews ?? 0
  return `AI trust score based on ${n} reviewer decision${n !== 1 ? 's' : ''}`
})
</script>

<style scoped>
.trust-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: help;
  border: 1.5px solid;
}

.badge-high {
  background: #f0fdf4;
  border-color: #86efac;
  color: #166534;
}
.badge-moderate {
  background: #fffbeb;
  border-color: #fcd34d;
  color: #92400e;
}
.badge-low {
  background: #fef2f2;
  border-color: #fca5a5;
  color: #991b1b;
}
.badge-unknown {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #64748b;
}
.badge-icon { font-size: 0.85rem; }
.badge-score { font-size: 0.75rem; opacity: 0.8; }
</style>
