<template>
  <div class="page-shell my-applications-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">{{ t('rentals.myApplications.kicker') }}</p>
        <h2 class="page-title">{{ t('rentals.myApplications.title') }}</h2>
        <p class="page-subtitle">{{ t('rentals.myApplications.subtitle') }}</p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" @click="load">
          <i class="pi pi-refresh" aria-hidden="true"></i>
          {{ t('rentals.myApplications.refresh') }}
        </button>
        <NuxtLink to="/rent" class="btn-primary">
          <i class="pi pi-search" aria-hidden="true"></i>
          {{ t('rentals.myApplications.browseListings') }}
        </NuxtLink>
      </div>
    </section>

    <section class="table-panel">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">{{ t('rentals.myApplications.recordsTitle') }}</h3>
          <p class="panel-subtitle">{{ t('rentals.myApplications.showingRecords', { shown: applications.length, total }) }}</p>
        </div>
      </div>

      <div v-if="errorMessage" class="state-panel error-state" role="alert">
        <strong>{{ t('rentals.myApplications.unavailable') }}</strong>
        <span>{{ errorMessage }}</span>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ t('rentals.myApplications.colListing') }}</th>
              <th>{{ t('rentals.myApplications.colProperty') }}</th>
              <th class="text-right">{{ t('rentals.myApplications.colOffer') }}</th>
              <th class="text-right">{{ t('rentals.myApplications.colBand') }}</th>
              <th>{{ t('rentals.myApplications.colStatus') }}</th>
              <th>{{ t('rentals.myApplications.colSubmitted') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6">{{ t('rentals.myApplications.loading') }}</td>
            </tr>
            <tr v-else-if="applications.length === 0">
              <td colspan="6">{{ t('rentals.myApplications.noApplications') }}</td>
            </tr>
            <tr v-for="app in applications" v-else :key="app.id">
              <td class="record-id">
                <NuxtLink v-if="app.listing_public_id" :to="`/rent/${app.listing_public_id}`">
                  {{ app.listing_public_id }}
                </NuxtLink>
                <span v-else>—</span>
              </td>
              <td><strong>{{ app.property_address || '—' }}</strong></td>
              <td class="text-right num">{{ formatEtb(app.offered_rent) }}</td>
              <td class="text-right num">
                <template v-if="app.band_min != null && app.band_max != null">
                  {{ formatEtb(app.band_min) }} – {{ formatEtb(app.band_max) }}
                </template>
                <template v-else>—</template>
              </td>
              <td>
                <span class="status-pill" :class="statusClass(app.status)">{{ statusLabel(app.status) }}</span>
              </td>
              <td>{{ formatDate(app.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import rentalService, { type RenterApplication } from '~/services/rentalService'
import { useI18n } from '~/composables/useI18n'

definePageMeta({ middleware: 'auth' })

const { t } = useI18n()

const loading = ref(true)
const errorMessage = ref('')
const applications = ref<RenterApplication[]>([])
const total = ref(0)

onMounted(load)

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await rentalService.myApplications()
    applications.value = result.data
    total.value = result.total
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : t('rentals.myApplications.unavailable')
    applications.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function statusClass(status: string) {
  if (status === 'accepted') return 'good'
  if (status === 'pending') return 'warn'
  if (status === 'rejected' || status === 'withdrawn') return 'bad'
  return 'muted'
}

function labelize(value: string) {
  return String(value || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function statusLabel(status: string) {
  const key = status.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
  const translated = t(`rentals.statuses.${key}`)
  return translated === `rentals.statuses.${key}` ? labelize(status) : translated
}

function formatEtb(value: number) {
  return `ETB ${Number(value || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

function formatDate(value?: string | null) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('en-ET', { dateStyle: 'medium' }).format(date)
}
</script>
