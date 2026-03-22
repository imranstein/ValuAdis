<template>
  <div class="reports-page">
    <div class="page-header bg-gradient-to-r from-emerald-600 to-teal-600 p-8 rounded-2xl mb-8 text-white">
      <h1 class="text-4xl font-bold">Compliance Reports</h1>
      <p class="text-emerald-50 mt-2">Generate and download valuation compliance reports</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div v-if="loading" class="text-center py-12">
        <i class="pi pi-spin pi-spinner text-4xl text-emerald-600 animate-spin"></i>
        <p class="text-gray-600 mt-4">Loading valuations...</p>
      </div>

      <div v-else-if="valuations.length === 0" class="col-span-full text-center py-12 bg-gray-50 rounded-2xl">
        <i class="pi pi-file-pdf text-6xl text-gray-300 mb-4"></i>
        <p class="text-gray-600">No valuations available</p>
      </div>

      <div
        v-for="valuation in valuations"
        v-else
        :key="valuation.id"
        class="bg-white rounded-2xl shadow-lg p-6 border border-gray-100 hover:shadow-xl transition-all"
      >
        <div class="flex items-start justify-between mb-4">
          <div>
            <h3 class="text-xl font-bold text-gray-800">{{ valuation.vehicle_make }} {{ valuation.vehicle_model }}</h3>
            <p class="text-gray-600 text-sm">VIN: {{ valuation.vehicle_vin }}</p>
          </div>
          <span class="bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full text-sm font-semibold">
            {{ valuation.status }}
          </span>
        </div>

        <div class="space-y-3 mb-6">
          <div class="flex justify-between items-center py-2 border-b border-gray-200">
            <span class="text-gray-600">Market Value:</span>
            <span class="font-bold text-emerald-600">ETB {{ valuation.market_value?.toLocaleString() }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-200">
            <span class="text-gray-600">Taxable Value:</span>
            <span class="font-bold">ETB {{ valuation.taxable_value?.toLocaleString() }}</span>
          </div>
          <div class="flex justify-between items-center py-2">
            <span class="text-gray-600">Confidence:</span>
            <span class="font-bold text-blue-600">{{ (valuation.confidence_score * 100).toFixed(0) }}%</span>
          </div>
        </div>

        <button
          @click="generateReport(valuation.id)"
          :disabled="generatingId === valuation.id"
          class="w-full bg-emerald-600 text-white font-semibold py-3 rounded-xl hover:bg-emerald-700 disabled:opacity-50 transition-all"
        >
          <i :class="['pi', generatingId === valuation.id ? 'pi-spin pi-spinner' : 'pi-download']"></i>
          <span class="ml-2">{{ generatingId === valuation.id ? 'Generating...' : 'Generate Report' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const valuations = ref([])
const loading = ref(true)
const generatingId = ref(null)

const fetchValuations = async () => {
  try {
    const response = await fetch('/api/v1/vehicles/valuations', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) {
      valuations.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching valuations:', error)
  } finally {
    loading.value = false
  }
}

const generateReport = async (valuationId: number) => {
  generatingId.value = valuationId
  try {
    const response = await fetch(`/api/v1/reports/compliance?valuation_id=${valuationId}`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })

    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `compliance_report_${valuationId}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    }
  } catch (error) {
    console.error('Error generating report:', error)
  } finally {
    generatingId.value = null
  }
}

onMounted(() => fetchValuations())
</script>
