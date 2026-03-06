<template>
  <div class="vehicle-valuation">
    <div class="valuation-header">
      <h3>Vehicle Valuation Analysis</h3>
      <p>Ethiopian market-specific valuation with regional factors</p>
    </div>

    <div class="valuation-summary">
      <div class="summary-card primary">
        <div class="summary-content">
          <div class="summary-label">Market Value</div>
          <div class="summary-value">{{ formatCurrency(valuation.market_value) }}</div>
          <div class="summary-trend positive">
            <i class="pi pi-arrow-up"></i>
            <span>{{ formatCurrency(valuation.appreciation) }} from last year</span>
          </div>
        </div>
        <div class="summary-icon">
          <i class="pi pi-money-bill"></i>
        </div>
      </div>

      <div class="summary-card secondary">
        <div class="summary-content">
          <div class="summary-label">Taxable Value</div>
          <div class="summary-value">{{ formatCurrency(valuation.taxable_value) }}</div>
          <div class="summary-trend neutral">
            <i class="pi pi-percentage"></i>
            <span>25% of market value</span>
          </div>
        </div>
        <div class="summary-icon">
          <i class="pi pi-calculator"></i>
        </div>
      </div>

      <div class="summary-card tertiary">
        <div class="summary-content">
          <div class="summary-label">Confidence Score</div>
          <div class="summary-value">{{ valuation.confidence_score }}%</div>
          <div class="summary-trend" :class="getConfidenceTrend()">
            <i :class="getConfidenceIcon()"></i>
            <span>{{ getConfidenceText() }}</span>
          </div>
        </div>
        <div class="summary-icon">
          <i class="pi pi-chart-line"></i>
        </div>
      </div>
    </div>

    <div class="valuation-factors">
      <div class="factors-header">
        <h4>Ethiopian Market Factors</h4>
        <button @click="toggleFactors" class="toggle-button">
          <i class="pi" :class="showFactors ? 'pi-chevron-up' : 'pi-chevron-down'"></i>
          {{ showFactors ? 'Hide' : 'Show' }} Details
        </button>
      </div>

      <div v-show="showFactors" class="factors-grid">
        <!-- Regional Factors -->
        <div class="factor-group">
          <h5>Regional Analysis</h5>
          <div class="factor-item">
            <div class="factor-info">
              <span class="factor-label">Region</span>
              <span class="factor-value">{{ vehicle.region || 'N/A' }}</span>
            </div>
            <div class="factor-multiplier">
              <span class="multiplier-value">{{ valuation.regional_multiplier }}x</span>
              <span class="multiplier-label">Regional demand</span>
            </div>
          </div>
          <div class="factor-item">
            <div class="factor-info">
              <span class="factor-label">City</span>
              <span class="factor-value">{{ vehicle.city || 'N/A' }}</span>
            </div>
            <div class="factor-description">
              Urban market with higher demand
            </div>
          </div>
        </div>

        <!-- Import Factors -->
        <div class="factor-group">
          <h5>Import Analysis</h5>
          <div class="factor-item">
            <div class="factor-info">
              <span class="factor-label">Import Year</span>
              <span class="factor-value">{{ vehicle.import_year || 'N/A' }}</span>
            </div>
            <div class="factor-multiplier">
              <span class="multiplier-value">{{ valuation.import_multiplier }}x</span>
              <span class="multiplier-label">Import age factor</span>
            </div>
          </div>
          <div class="factor-item">
            <div class="factor-info">
              <span class="factor-label">Customs Status</span>
              <span class="factor-value">{{ vehicle.custom_duty_paid ? 'Paid' : 'Unpaid' }}</span>
            </div>
            <div class="factor-multiplier">
              <span class="multiplier-value">{{ valuation.customs_multiplier }}x</span>
              <span class="multiplier-label">Customs adjustment</span>
            </div>
          </div>
        </div>

        <!-- Vehicle Factors -->
        <div class="factor-group">
          <h5>Vehicle Analysis</h5>
          <div class="factor-item">
            <div class="factor-info">
              <span class="factor-label">Make Reliability</span>
              <span class="factor-value">{{ vehicle.make }}</span>
            </div>
            <div class="factor-multiplier">
              <span class="multiplier-value">{{ valuation.make_reliability_multiplier }}x</span>
              <span class="multiplier-label">Market preference</span>
            </div>
          </div>
          <div class="factor-item">
            <div class="factor-info">
              <span class="factor-label">Fuel Type</span>
              <span class="factor-value">{{ vehicle.fuel_type || 'N/A' }}</span>
            </div>
            <div class="factor-multiplier">
              <span class="multiplier-value">{{ valuation.fuel_type_multiplier }}x</span>
              <span class="multiplier-label">Fuel efficiency</span>
            </div>
          </div>
          <div class="factor-item">
            <div class="factor-info">
              <span class="factor-label">Body Type</span>
              <span class="factor-value">{{ vehicle.body_type || 'N/A' }}</span>
            </div>
            <div class="factor-multiplier">
              <span class="multiplier-value">{{ valuation.body_type_multiplier }}x</span>
              <span class="multiplier-label">Market demand</span>
            </div>
          </div>
        </div>

        <!-- Condition Factors -->
        <div class="factor-group">
          <h5>Condition Analysis</h5>
          <div class="factor-item">
            <div class="factor-info">
              <span class="factor-label">Mileage</span>
              <span class="factor-value">{{ formatNumber(vehicle.mileage) }} km</span>
            </div>
            <div class="factor-multiplier">
              <span class="multiplier-value">{{ valuation.condition_multiplier }}x</span>
              <span class="multiplier-label">Wear factor</span>
            </div>
          </div>
          <div class="factor-item">
            <div class="factor-info">
              <span class="factor-label">Previous Owners</span>
              <span class="factor-value">{{ vehicle.previous_owners || 1 }}</span>
            </div>
            <div class="factor-description">
              {{ getOwnershipDescription(vehicle.previous_owners) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="valuation-breakdown">
      <div class="breakdown-header">
        <h4>Valuation Breakdown</h4>
        <button @click="toggleBreakdown" class="toggle-button">
          <i class="pi" :class="showBreakdown ? 'pi-chevron-up' : 'pi-chevron-down'"></i>
          {{ showBreakdown ? 'Hide' : 'Show' }} Calculation
        </button>
      </div>

      <div v-show="showBreakdown" class="breakdown-content">
        <div class="calculation-steps">
          <div class="calc-step">
            <div class="step-number">1</div>
            <div class="step-content">
              <div class="step-label">Base Market Value</div>
              <div class="step-value">{{ formatCurrency(valuation.base_value) }}</div>
              <div class="step-description">Initial market assessment</div>
            </div>
          </div>

          <div class="calc-step">
            <div class="step-number">2</div>
            <div class="step-content">
              <div class="step-label">Regional Adjustment</div>
              <div class="step-value">{{ formatCurrency(valuation.base_value * (valuation.regional_multiplier - 1)) }}</div>
              <div class="step-description">{{ getRegionalDescription(valuation.regional_multiplier) }}</div>
            </div>
          </div>

          <div class="calc-step">
            <div class="step-number">3</div>
            <div class="step-content">
              <div class="step-label">Import & Customs</div>
              <div class="step-value">{{ formatCurrency(valuation.base_value * (valuation.import_multiplier * valuation.customs_multiplier - 1)) }}</div>
              <div class="step-description">Import year and customs duty factors</div>
            </div>
          </div>

          <div class="calc-step">
            <div class="step-number">4</div>
            <div class="step-content">
              <div class="step-label">Vehicle Characteristics</div>
              <div class="step-value">{{ formatCurrency(valuation.base_value * (valuation.make_reliability_multiplier * valuation.fuel_type_multiplier * valuation.body_type_multiplier - 1)) }}</div>
              <div class="step-description">Make, fuel type, and body type adjustments</div>
            </div>
          </div>

          <div class="calc-step">
            <div class="step-number">5</div>
            <div class="step-content">
              <div class="step-label">Condition Adjustment</div>
              <div class="step-value">{{ formatCurrency(valuation.base_value * (valuation.condition_multiplier - 1)) }}</div>
              <div class="step-description">Mileage and ownership history</div>
            </div>
          </div>

          <div class="calc-step final">
            <div class="step-number">✓</div>
            <div class="step-content">
              <div class="step-label">Final Market Value</div>
              <div class="step-value">{{ formatCurrency(valuation.market_value) }}</div>
              <div class="step-description">All factors applied</div>
            </div>
          </div>
        </div>

        <div class="calculation-summary">
          <div class="summary-item">
            <span class="summary-label">Taxable Value (25%)</span>
            <span class="summary-value">{{ formatCurrency(valuation.taxable_value) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Market Position</span>
            <span class="summary-value">{{ valuation.market_position }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Valuation Date</span>
            <span class="summary-value">{{ formatDate(valuation.created_date) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="valuation-actions">
      <button @click="generateReport" class="action-button primary">
        <i class="pi pi-file-pdf"></i>
        Generate Report
      </button>
      <button @click="shareValuation" class="action-button secondary">
        <i class="pi pi-share-alt"></i>
        Share
      </button>
      <button @click="exportData" class="action-button secondary">
        <i class="pi pi-download"></i>
        Export Data
      </button>
      <button @click="printValuation" class="action-button secondary">
        <i class="pi pi-print"></i>
        Print
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  vehicle: {
    type: Object,
    required: true
  },
  valuation: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['generate-report', 'share', 'export', 'print'])

// Reactive data
const showFactors = ref(true)
const showBreakdown = ref(false)

// Methods
function toggleFactors() {
  showFactors.value = !showFactors.value
}

function toggleBreakdown() {
  showBreakdown.value = !showBreakdown.value
}

function getConfidenceTrend() {
  const score = props.valuation.confidence_score
  if (score >= 80) return 'positive'
  if (score >= 60) return 'neutral'
  return 'negative'
}

function getConfidenceIcon() {
  const score = props.valuation.confidence_score
  if (score >= 80) return 'pi-check-circle'
  if (score >= 60) return 'pi-info-circle'
  return 'pi-exclamation-triangle'
}

function getConfidenceText() {
  const score = props.valuation.confidence_score
  if (score >= 80) return 'High confidence'
  if (score >= 60) return 'Moderate confidence'
  return 'Low confidence'
}

function getRegionalDescription(multiplier) {
  if (multiplier >= 1.1) return 'High demand region'
  if (multiplier >= 1.0) return 'Standard demand region'
  return 'Lower demand region'
}

function getOwnershipDescription(owners) {
  if (!owners || owners === 1) return 'Single owner - excellent'
  if (owners <= 2) return 'Two owners - good'
  if (owners <= 3) return 'Three owners - fair'
  return 'Multiple owners - poor'
}

function formatCurrency(value) {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function formatNumber(value) {
  return new Intl.NumberFormat('en-ET').format(value)
}

function formatDate(date) {
  return new Intl.DateTimeFormat('en-ET', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(new Date(date))
}

function generateReport() {
  emit('generate-report')
}

function shareValuation() {
  emit('share')
}

function exportData() {
  emit('export')
}

function printValuation() {
  emit('print')
}
</script>

<style scoped>
.vehicle-valuation {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.valuation-header {
  padding: 1.5rem;
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  color: white;
}

.valuation-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.valuation-header p {
  opacity: 0.9;
  font-size: 0.875rem;
  margin: 0;
}

.valuation-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 12px;
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.summary-card.primary {
  border-left: 4px solid #059669;
}

.summary-card.secondary {
  border-left: 4px solid #3b82f6;
}

.summary-card.tertiary {
  border-left: 4px solid #f59e0b;
}

.summary-content {
  flex: 1;
}

.summary-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.summary-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.summary-trend.positive {
  color: #059669;
}

.summary-trend.neutral {
  color: #6b7280;
}

.summary-trend.negative {
  color: #dc2626;
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.summary-card.primary .summary-icon {
  background: #dcfce7;
  color: #059669;
}

.summary-card.secondary .summary-icon {
  background: #dbeafe;
  color: #3b82f6;
}

.summary-card.tertiary .summary-icon {
  background: #fef3c7;
  color: #f59e0b;
}

.valuation-factors,
.valuation-breakdown {
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.factors-header,
.breakdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.factors-header h4,
.breakdown-header h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.toggle-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  color: #6b7280;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-button:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

.factors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.factor-group {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1rem;
}

.factor-group h5 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 1rem 0;
}

.factor-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.factor-item:last-child {
  border-bottom: none;
}

.factor-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.factor-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.factor-value {
  font-size: 0.875rem;
  color: #374151;
  font-weight: 500;
}

.factor-multiplier {
  text-align: right;
}

.multiplier-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #059669;
  display: block;
}

.multiplier-label {
  font-size: 0.75rem;
  color: #6b7280;
}

.factor-description {
  font-size: 0.75rem;
  color: #6b7280;
  font-style: italic;
}

.breakdown-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.calculation-steps {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.calc-step {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e5e7eb;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.calc-step.final .step-number {
  background: #059669;
  color: white;
}

.step-content {
  flex: 1;
}

.step-label {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.step-value {
  color: #059669;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.step-description {
  font-size: 0.875rem;
  color: #6b7280;
}

.calculation-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.valuation-actions {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: #f8fafc;
  flex-wrap: wrap;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action-button.primary {
  background: #059669;
  color: white;
}

.action-button.primary:hover {
  background: #047857;
}

.action-button.secondary {
  background: white;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.action-button.secondary:hover {
  background: #f8fafc;
  border-color: #9ca3af;
}

/* Responsive Design */
@media (max-width: 768px) {
  .valuation-summary {
    grid-template-columns: 1fr;
  }
  
  .factors-grid {
    grid-template-columns: 1fr;
  }
  
  .calculation-summary {
    grid-template-columns: 1fr;
  }
  
  .valuation-actions {
    flex-direction: column;
  }
  
  .action-button {
    justify-content: center;
  }
}
</style>
