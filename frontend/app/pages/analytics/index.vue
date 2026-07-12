<template>
  <div class="page-shell analytics-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">Market intelligence</p>
        <h2 class="page-title">Analytics command view.</h2>
        <p class="page-subtitle">Backend-backed valuation volume, property mix, municipality exposure, and compliance pipeline.</p>
      </div>
      <div class="page-actions">
        <NuxtLink to="/reports" class="btn-secondary">
          <i class="pi pi-download" aria-hidden="true"></i>
          Export report
        </NuxtLink>
        <NuxtLink to="/valuations/quick" class="btn-primary">
          <i class="pi pi-bolt" aria-hidden="true"></i>
          New valuation
        </NuxtLink>
      </div>
    </section>

    <section class="stats-grid" aria-label="Analytics metrics">
      <article class="stat-card" data-testid="analytics-market-growth">
            <p class="stat-label">Market Growth</p>
            <h3 class="stat-value">{{ formatPercent(dashboard.financials.marketValueGrowth) }}</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-green">YoY</span>
              <span class="stat-sub">vs last year</span>
            </div>
      </article>
      <article class="stat-card" data-testid="analytics-average-value">
            <p class="stat-label">Avg. Property Value</p>
            <h3 class="stat-value">{{ formatCompactCurrency(dashboard.financials.avgPropertyValue) }}</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-indigo">{{ dashboard.properties.total }} properties</span>
              <span class="stat-sub">this quarter</span>
            </div>
      </article>
      <article class="stat-card" data-testid="analytics-total-valuations">
            <p class="stat-label">Total Valuations</p>
            <h3 class="stat-value">{{ dashboard.valuations.total }}</h3>
            <div class="stat-badge-wrap">
              <span class="stat-badge badge-amber">{{ formatPercent(dashboard.valuations.growthRate) }}</span>
              <span class="stat-sub">period growth</span>
            </div>
      </article>
    </section>

    <section class="charts-grid">
          <article class="chart-card" data-testid="analytics-chart-valuation-volume">
            <div class="chart-header">
              <h3 class="chart-title">Valuation Volume Over Time</h3>
              <select v-model="selectedPeriod" class="chart-filter" @change="loadAnalytics">
                <option value="year">Last 12 Months</option>
                <option value="quarter">Last Quarter</option>
                <option value="month">Last 30 Days</option>
              </select>
            </div>
            <div class="chart-area">
              <Chart type="line" :data="valuationVolumeChartData" :options="lineChartOptions" class="analytics-chart" />
            </div>
          </article>

          <article class="chart-card" data-testid="analytics-chart-property-types">
            <div class="chart-header">
              <h3 class="chart-title">Property Type Distribution</h3>
            </div>
            <div class="chart-area">
              <Chart type="doughnut" :data="propertyTypeChartData" :options="doughnutChartOptions" class="analytics-chart" />
              <div class="chart-legend">
                <div class="legend-item" v-for="item in typeDistribution" :key="item.label">
                  <span class="legend-dot" :style="`background:${item.color}`"></span>
                  <span class="legend-label">{{ item.label }}</span>
                  <span class="legend-value">{{ item.value }}%</span>
                </div>
              </div>
            </div>
          </article>

          <article class="chart-card" data-testid="analytics-chart-municipality-breakdown">
            <div class="chart-header">
              <h3 class="chart-title">Municipality Breakdown</h3>
            </div>
            <div class="chart-area">
              <Chart type="bar" :data="municipalityChartData" :options="barChartOptions" class="analytics-chart" />
              <div class="region-list">
                <div class="region-item" v-for="region in regions" :key="region.name">
                  <div class="region-info">
                    <span class="region-name">{{ region.name }}</span>
                    <span class="region-value">{{ region.value }}</span>
                  </div>
                  <div class="region-bar">
                    <div class="region-fill" :style="`width:${region.pct}%`"></div>
                  </div>
                  <span class="region-pct">{{ region.pct }}%</span>
                </div>
              </div>
            </div>
          </article>

          <article class="chart-card" data-testid="analytics-chart-status-pipeline">
            <div class="chart-header">
              <h3 class="chart-title">Status Pipeline</h3>
            </div>
            <div class="chart-area">
              <Chart type="bar" :data="statusPipelineChartData" :options="statusChartOptions" class="analytics-chart" />
            </div>
          </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { getAccessToken } from '~/utils/authToken'

definePageMeta({ middleware: 'auth' })

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl
const selectedPeriod = ref('year')

// Canvas (chart.js) cannot resolve CSS vars, so these mirror the civic-ledger
// token hex values directly. Keep in sync with assets/css/main.css.
const chartColors = {
  green: '#235c43',
  blue: '#33566a',
  orange: '#c79a3e',
  gold: '#8a5f14',
  slate: '#5c665d',
}

const dashboard = ref({
  properties: { total: 0, active: 0, growthRate: 0 },
  valuations: { total: 0, growthRate: 0 },
  financials: { totalMarketValue: 0, totalTaxableValue: 0, avgPropertyValue: 0, marketValueGrowth: 0 },
  compliance: { complianceRate: 0, compliantValuations: 0 },
})

const trends = ref<Record<string, { count: number; total_value: number; total_taxable: number; avg_value: number }>>({})
const municipalityData = ref<Record<string, { properties: number; total_value: number; valuations: number }>>({})
const propertyTypeData = ref<Record<string, { count: number; total_value: number }>>({})

const labelsFrom = (source: Record<string, unknown>) => Object.keys(source)
const valuesFrom = <T extends Record<string, number>>(source: Record<string, T>, key: keyof T) => Object.values(source).map(item => Number(item[key] ?? 0))

const valuationVolumeChartData = computed(() => ({
  labels: labelsFrom(trends.value),
  datasets: [
    {
      label: 'Valuations',
      data: valuesFrom(trends.value, 'count'),
      borderColor: chartColors.green,
      backgroundColor: 'rgba(7, 129, 96, 0.14)',
      tension: 0.32,
      fill: true,
    },
  ],
}))

const municipalityChartData = computed(() => ({
  labels: labelsFrom(municipalityData.value),
  datasets: [
    {
      label: 'Market Value',
      data: valuesFrom(municipalityData.value, 'total_value'),
      backgroundColor: chartColors.blue,
      borderRadius: 6,
    },
  ],
}))

const propertyTypeChartData = computed(() => ({
  labels: labelsFrom(propertyTypeData.value),
  datasets: [
    {
      label: 'Properties',
      data: valuesFrom(propertyTypeData.value, 'count'),
      backgroundColor: [chartColors.green, chartColors.blue, chartColors.orange, chartColors.gold, chartColors.slate],
      borderWidth: 0,
    },
  ],
}))

const statusPipelineChartData = computed(() => {
  const approved = dashboard.value.compliance.compliantValuations
  const total = dashboard.value.valuations.total
  return {
    labels: ['Approved', 'Pending Review'],
    datasets: [
      {
        label: 'Valuations',
        data: [approved, Math.max(total - approved, 0)],
        backgroundColor: [chartColors.green, chartColors.gold],
        borderRadius: 6,
      },
    ],
  }
})

const baseChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: '#475569',
        boxWidth: 10,
        font: { family: 'Inter' },
      },
    },
  },
}

const lineChartOptions = computed(() => ({
  ...baseChartOptions,
  scales: {
    x: { ticks: { color: '#5c665d' }, grid: { display: false } },
    y: { beginAtZero: true, ticks: { color: '#5c665d' }, grid: { color: 'rgba(148, 163, 184, 0.18)' } },
  },
}))

const barChartOptions = computed(() => ({
  ...baseChartOptions,
  scales: {
    x: { ticks: { color: '#5c665d' }, grid: { display: false } },
    y: { beginAtZero: true, ticks: { color: '#5c665d' }, grid: { color: 'rgba(148, 163, 184, 0.18)' } },
  },
}))

const statusChartOptions = computed(() => ({
  ...barChartOptions.value,
  indexAxis: 'y',
}))

const doughnutChartOptions = computed(() => ({
  ...baseChartOptions,
  cutout: '68%',
}))

const typeDistribution = computed(() => {
  const total = valuesFrom(propertyTypeData.value, 'count').reduce((sum, value) => sum + value, 0)
  return labelsFrom(propertyTypeData.value).map((label, index) => {
    const count = propertyTypeData.value[label]?.count ?? 0
    return {
      label,
      value: total > 0 ? Math.round((count / total) * 100) : 0,
      color: propertyTypeChartData.value.datasets[0].backgroundColor[index % 5],
    }
  })
})

const regions = computed(() => {
  const total = valuesFrom(municipalityData.value, 'total_value').reduce((sum, value) => sum + value, 0)
  return labelsFrom(municipalityData.value).map(name => {
    const value = municipalityData.value[name]?.total_value ?? 0
    return {
      name,
      value: formatCompactCurrency(value),
      pct: total > 0 ? Math.round((value / total) * 100) : 0,
    }
  })
})

onMounted(loadAnalytics)

async function loadAnalytics() {
  const [dashboardData, trendsData, municipalityAnalytics, propertyTypes] = await Promise.all([
    fetchAnalytics('/dashboard', { period: 'month' }),
    fetchAnalytics('/trends', { period: selectedPeriod.value }),
    fetchAnalytics('/municipalities', { period: selectedPeriod.value }),
    fetchAnalytics('/property-types', { period: selectedPeriod.value }),
  ])

  dashboard.value = {
    properties: {
      total: dashboardData.properties?.total ?? 0,
      active: dashboardData.properties?.active ?? 0,
      growthRate: dashboardData.properties?.growth_rate ?? 0,
    },
    valuations: {
      total: dashboardData.valuations?.total ?? 0,
      growthRate: dashboardData.valuations?.growth_rate ?? 0,
    },
    financials: {
      totalMarketValue: dashboardData.financials?.total_market_value ?? 0,
      totalTaxableValue: dashboardData.financials?.total_taxable_value ?? 0,
      avgPropertyValue: dashboardData.financials?.avg_property_value ?? 0,
      marketValueGrowth: dashboardData.financials?.market_value_growth ?? 0,
    },
    compliance: {
      complianceRate: dashboardData.compliance?.compliance_rate ?? 0,
      compliantValuations: dashboardData.compliance?.compliant_valuations ?? 0,
    },
  }
  trends.value = trendsData.trends ?? {}
  municipalityData.value = municipalityAnalytics.municipalities ?? {}
  propertyTypeData.value = propertyTypes.property_types ?? {}
}

async function fetchAnalytics(path: string, params: Record<string, string>) {
  const token = getAccessToken()
  const search = new URLSearchParams(params)
  const response = await fetch(`${apiBase}/api/v1/analytics${path}?${search}`, {
    headers: { Authorization: `Bearer ${token}` },
  })

  if (!response.ok) return {}
  return response.json()
}

function formatCompactCurrency(value: number) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value)
}

function formatPercent(value: number) {
  return `${value > 0 ? '+' : ''}${Number(value || 0).toFixed(1)}%`
}

useHead({
  title: 'Analytics — ValuAdis',
  meta: [{ name: 'description', content: 'Property valuation analytics and market insights.' }]
})
</script>

<style scoped>
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 2rem; }
.stat-card { padding: 1.5rem; border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface); position: relative; overflow: hidden; }
.stat-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: var(--muted); margin: 0 0 0.5rem; }
.stat-value { font-family: var(--display); font-size: 1.75rem; font-weight: 700; color: var(--ink); margin: 0 0 1rem; }
.stat-badge-wrap { display: flex; align-items: center; gap: 0.5rem; }
.stat-badge { font-size: 0.7rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 9999px; }
.badge-green { background: var(--green-soft); color: var(--green-dark); }
.badge-indigo { background: var(--blue-soft); color: var(--blue); }
.badge-amber { background: var(--amber-soft); color: var(--gold); }
.stat-sub { font-size: 0.7rem; color: var(--muted); font-style: italic; }

.charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.chart-card { padding: 1.5rem; border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface); }
.chart-card.wide { grid-column: 1 / -1; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.chart-title { font-family: var(--display); font-size: 1.1rem; font-weight: 700; color: var(--ink); margin: 0; }
.chart-filter { padding: 0.35rem 0.75rem; background: var(--surface-2); border: 1px solid var(--line); border-radius: 0.5rem; font-size: 0.75rem; color: var(--muted); }
.chart-area { min-height: 220px; }
.analytics-chart { height: 220px; width: 100%; display: block; }
.chart-legend { display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 0.35rem; }
.legend-dot { width: 0.75rem; height: 0.75rem; border-radius: 50%; }
.legend-label { font-size: 0.75rem; color: var(--muted); }
.legend-value { font-size: 0.75rem; font-weight: 700; color: var(--ink-soft); }

.region-list { display: flex; flex-direction: column; gap: 1rem; }
.region-item { display: flex; align-items: center; gap: 1rem; }
.region-info { width: 180px; display: flex; justify-content: space-between; }
.region-name { font-size: 0.875rem; font-weight: 500; color: var(--ink-soft); }
.region-value { font-size: 0.875rem; color: var(--muted); }
.region-bar { flex: 1; height: 0.5rem; background: var(--surface-2); border-radius: 9999px; overflow: hidden; }
.region-fill { height: 100%; background: var(--green); border-radius: 9999px; }
.region-pct { width: 40px; text-align: right; font-size: 0.875rem; font-weight: 600; color: var(--ink-soft); }
</style>
