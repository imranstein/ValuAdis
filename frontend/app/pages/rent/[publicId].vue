<template>
  <main class="rent-detail-page">
    <nav class="rent-nav" aria-label="Public navigation">
      <NuxtLink to="/" class="rent-brand">
        <span class="rent-mark" aria-hidden="true">V</span>
        <span>{{ t('rentals.publicNav.brand') }}</span>
      </NuxtLink>
      <div class="rent-nav-links">
        <NuxtLink to="/rent">{{ t('rentals.publicNav.allListings') }}</NuxtLink>
        <NuxtLink to="/login" class="rent-login">{{ t('rentals.publicNav.workspaceSignIn') }}</NuxtLink>
        <LanguageSwitcher />
      </div>
    </nav>

    <div v-if="loading" class="rent-state">{{ t('rentals.detail.loading') }}</div>

    <div v-else-if="errorMessage" class="rent-state rent-state-error" role="alert">
      <strong>{{ t('rentals.detail.unavailable') }}</strong>
      <span>{{ errorMessage }}</span>
      <NuxtLink to="/rent" class="rent-back-link">{{ t('rentals.detail.backToListings') }}</NuxtLink>
    </div>

    <template v-else-if="listing">
      <header class="detail-head">
        <div>
          <p class="detail-id">
            <span class="rent-card-id">{{ listing.public_id }}</span>
            <span class="rent-cert-badge" :title="t('rentals.detail.certifiedTitle')">
              <i class="pi pi-verified" aria-hidden="true"></i>
              {{ t('rentals.detail.certifiedBadge') }}
            </span>
          </p>
          <h1>{{ listing.property.address }}</h1>
          <p class="detail-location">
            {{ listing.property.subcity || listing.property.municipality }},
            {{ listing.property.municipality }}
            <template v-if="listing.published_at">
              · {{ t('rentals.detail.publishedOn', { date: formatDate(listing.published_at) }) }}
            </template>
          </p>
        </div>
      </header>

      <section class="detail-band" aria-label="Published rent band">
        <div>
          <span>{{ t('rentals.detail.suggestedRent') }}</span>
          <strong>{{ formatEtb(listing.suggested_rent) }}{{ t('common.perMonthSuffix') }}</strong>
        </div>
        <div>
          <span>{{ t('rentals.detail.bandMin') }}</span>
          <strong>{{ formatEtb(listing.band_min) }}</strong>
        </div>
        <div>
          <span>{{ t('rentals.detail.bandMax') }}</span>
          <strong>{{ formatEtb(listing.band_max) }}</strong>
        </div>
        <p class="detail-band-note">{{ t('rentals.detail.bandNote') }}</p>
      </section>

      <section class="detail-gallery" aria-label="Property photos">
        <div v-if="listing.property.photo_urls.length" class="gallery-grid">
          <img
            v-for="url in listing.property.photo_urls"
            :key="url"
            :src="resolvePhotoUrl(url)"
            :alt="t('rentals.detail.photoAlt', { address: listing.property.address })"
            loading="lazy"
          />
        </div>
        <div v-else class="rent-state gallery-placeholder">{{ t('rentals.detail.noPhotos') }}</div>
      </section>

      <div class="detail-columns">
        <section class="detail-facts" aria-label="Property facts">
          <h2>{{ t('rentals.detail.propertyFacts') }}</h2>
          <dl>
            <div>
              <dt>{{ t('rentals.detail.type') }}</dt>
              <dd>{{ labelize(listing.property.property_subtype || listing.property.property_type) }}</dd>
            </div>
            <div>
              <dt>{{ t('rentals.detail.area') }}</dt>
              <dd>{{ formatArea(listing.property.area_sqm) }} m²</dd>
            </div>
            <div v-if="listing.property.building_area_sqm">
              <dt>{{ t('rentals.detail.buildingArea') }}</dt>
              <dd>{{ formatArea(listing.property.building_area_sqm) }} m²</dd>
            </div>
            <div v-if="listing.property.number_of_bedrooms != null">
              <dt>{{ t('rentals.detail.bedrooms') }}</dt>
              <dd>{{ listing.property.number_of_bedrooms }}</dd>
            </div>
            <div v-if="listing.property.number_of_bathrooms != null">
              <dt>{{ t('rentals.detail.bathrooms') }}</dt>
              <dd>{{ listing.property.number_of_bathrooms }}</dd>
            </div>
            <div v-if="listing.property.number_of_floors != null">
              <dt>{{ t('rentals.detail.floors') }}</dt>
              <dd>{{ listing.property.number_of_floors }}</dd>
            </div>
            <div v-if="listing.property.year_built">
              <dt>{{ t('rentals.detail.yearBuilt') }}</dt>
              <dd>{{ listing.property.year_built }}</dd>
            </div>
            <div v-if="listing.property.condition">
              <dt>{{ t('rentals.detail.condition') }}</dt>
              <dd>{{ labelize(listing.property.condition) }}</dd>
            </div>
          </dl>

          <div class="apply-panel">
            <h3>{{ t('rentals.detail.applyHeading') }}</h3>

            <template v-if="!isAuthenticated">
              <p>{{ t('rentals.detail.applyUnauthed') }}</p>
              <NuxtLink to="/rent/signup" class="rent-btn-primary">{{ t('rentals.detail.registerAsRenter') }}</NuxtLink>
            </template>

            <template v-else-if="applicationResult">
              <p class="apply-success" role="status">
                {{ t('rentals.detail.applicationSubmitted', { amount: formatEtb(applicationResult.offered_rent), status: statusLabel(applicationResult.status) }) }}
                <NuxtLink to="/rentals/my-applications">{{ t('rentals.detail.myApplicationsLink') }}</NuxtLink>.
              </p>
            </template>

            <form v-else class="apply-form" @submit.prevent="submitApplication">
              <label class="apply-field">
                <span>{{ t('rentals.detail.yourOffer', { min: formatEtb(listing.band_min), max: formatEtb(listing.band_max) }) }}</span>
                <input
                  v-model.number="offeredRent"
                  type="number"
                  required
                  :min="listing.band_min"
                  :max="listing.band_max"
                  step="any"
                />
              </label>
              <p v-if="offerOutsideBand" class="apply-error" role="alert">{{ t('rentals.detail.offerOutsideBand') }}</p>
              <label class="apply-field">
                <span>{{ t('rentals.detail.messageToOwner') }}</span>
                <textarea v-model="applicationMessage" rows="2" maxlength="1000"></textarea>
              </label>
              <p v-if="applyError" class="apply-error" role="alert">{{ applyError }}</p>
              <button class="rent-btn-primary" type="submit" :disabled="applying || offerOutsideBand">
                {{ applying ? t('rentals.detail.applySubmitting') : t('rentals.detail.applySubmit') }}
              </button>
            </form>
          </div>
        </section>

        <section class="detail-map" aria-label="Listing location">
          <h2>{{ t('rentals.detail.location') }}</h2>
          <ClientOnly>
            <PropertyMap
              v-if="mapProperties.length"
              :properties="mapProperties"
              :center="mapCenter"
              :zoom="14"
              height="420px"
            />
            <div v-else class="rent-state">{{ t('rentals.detail.noCoordinates') }}</div>
          </ClientOnly>
        </section>
      </div>
    </template>

    <footer class="rent-footer">
      <span>{{ t('rentals.detail.footerTag') }}</span>
      <NuxtLink to="/rent">{{ t('rentals.detail.allListings') }}</NuxtLink>
    </footer>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import rentalService, { type PublicListing, type RenterApplication } from '~/services/rentalService'
import propertyService from '~/services/propertyService'
import PropertyMap from '~/components/map/PropertyMap.vue'
import { getAccessToken } from '~/utils/authToken'
import { useI18n } from '~/composables/useI18n'
import LanguageSwitcher from '~/components/LanguageSwitcher.vue'

definePageMeta({ layout: 'landing' })

const { t } = useI18n()

const route = useRoute()
const loading = ref(true)
const errorMessage = ref('')
const listing = ref<PublicListing | null>(null)

const isAuthenticated = ref(false)
const offeredRent = ref<number | null>(null)
const applicationMessage = ref('')
const applying = ref(false)
const applyError = ref('')
const applicationResult = ref<RenterApplication | null>(null)

const offerOutsideBand = computed(() => {
  if (!listing.value || offeredRent.value == null) return false
  return offeredRent.value < listing.value.band_min || offeredRent.value > listing.value.band_max
})

async function submitApplication() {
  if (!listing.value || offeredRent.value == null) return
  applying.value = true
  applyError.value = ''
  try {
    applicationResult.value = await rentalService.applyToListing(
      listing.value.public_id,
      offeredRent.value,
      applicationMessage.value || undefined,
    )
  } catch (error) {
    applyError.value = error instanceof Error ? error.message : 'Application failed.'
  } finally {
    applying.value = false
  }
}

const mapProperties = computed(() => {
  const prop = listing.value?.property
  if (!prop || prop.latitude == null || prop.longitude == null) return []
  return [
    {
      id: listing.value!.public_id,
      address: prop.address,
      property_type: prop.property_type,
      area_sqm: prop.area_sqm,
      market_value: listing.value!.suggested_rent,
      latitude: prop.latitude,
      longitude: prop.longitude,
      number_of_bedrooms: prop.number_of_bedrooms,
      status: 'for_rent',
    },
  ]
})

const mapCenter = computed(() => {
  const prop = listing.value?.property
  if (prop?.latitude != null && prop?.longitude != null) return [prop.latitude, prop.longitude]
  return [9.0116, 38.7616]
})

onMounted(async () => {
  isAuthenticated.value = Boolean(getAccessToken())
  try {
    listing.value = await rentalService.getPublicListing(String(route.params.publicId))
    if (listing.value) offeredRent.value = listing.value.suggested_rent
  } catch (error) {
    errorMessage.value =
      error instanceof Error && error.message.includes('404')
        ? t('rentals.detail.unavailable')
        : error instanceof Error
          ? error.message
          : t('rentals.detail.unavailable')
  } finally {
    loading.value = false
  }
})

function formatEtb(value: number) {
  return `ETB ${Number(value || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

function formatDate(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('en-ET', { dateStyle: 'medium' }).format(date)
}

function labelize(value: string) {
  return String(value || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

// Known application-status enum values route through the shared glossary
// translation; anything unrecognized falls back to a generic label so the
// page never breaks on a new backend status.
function statusLabel(status: string) {
  const key = status.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
  const translated = t(`rentals.statuses.${key}`)
  return translated === `rentals.statuses.${key}` ? labelize(status) : translated
}

function formatArea(value: number) {
  return Number(value || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })
}

function resolvePhotoUrl(url: string) {
  return propertyService.resolvePhotoUrl(url)
}
</script>

<style scoped>
.rent-detail-page {
  min-height: 100vh;
  background: var(--canvas);
  color: var(--ink);
}

.rent-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  height: 72px;
  border-bottom: 1px solid var(--line);
  background: var(--surface);
  padding: 0 clamp(18px, 5vw, 64px);
}

.rent-brand {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  color: var(--ink);
  font-family: var(--serif);
  font-size: 22px;
  font-weight: 600;
  text-decoration: none;
}

.rent-mark {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border-radius: var(--radius);
  background: var(--green);
  color: var(--surface);
  font-size: 18px;
}

.rent-nav-links {
  display: flex;
  align-items: center;
  gap: var(--space-5);
}

.rent-nav-links a {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-decoration: none;
}

.rent-login {
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--line-strong);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 0 var(--space-4);
}

.rent-state {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  max-width: 560px;
  margin: var(--space-6) clamp(18px, 5vw, 64px);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--muted);
  padding: var(--space-5);
}

.rent-state-error strong {
  color: var(--red, #9d3a28);
}

.rent-back-link {
  color: var(--green);
  font-weight: 700;
  text-decoration: none;
}

.detail-head {
  padding: clamp(28px, 5vw, 56px) clamp(18px, 5vw, 64px) var(--space-5);
}

.detail-id {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin: 0 0 var(--space-3);
}

.rent-card-id {
  color: var(--muted);
  font-family: var(--mono);
  font-size: 13px;
}

.rent-cert-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--green);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.detail-head h1 {
  margin: 0;
  font-family: var(--serif);
  font-size: clamp(30px, 4.4vw, 48px);
  font-weight: 600;
  line-height: 1.08;
}

.detail-location {
  margin: var(--space-3) 0 0;
  color: var(--muted);
}

.detail-band {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1px;
  margin: 0 clamp(18px, 5vw, 64px);
  border: 1px solid var(--line-strong);
  border-top: 2px solid var(--gold-bright);
  border-radius: var(--radius);
  background: var(--line);
  overflow: hidden;
}

.detail-band > div {
  background: var(--surface);
  padding: var(--space-5);
}

.detail-band span {
  display: block;
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.detail-band strong {
  display: block;
  margin-top: var(--space-2);
  color: var(--green);
  font-family: var(--mono);
  font-size: clamp(18px, 2.4vw, 26px);
  font-variant-numeric: tabular-nums;
}

.detail-band-note {
  grid-column: 1 / -1;
  margin: 0;
  background: var(--surface-2, var(--surface));
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 13px;
  line-height: 1.5;
  padding: var(--space-4) var(--space-5);
}

.detail-gallery {
  padding: 0 clamp(18px, 5vw, 64px) var(--space-5);
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-3);
}

.gallery-grid img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--canvas);
}

.gallery-placeholder {
  margin: 0;
}

.detail-columns {
  display: grid;
  grid-template-columns: minmax(300px, 0.9fr) minmax(0, 1.1fr);
  gap: var(--space-5);
  padding: var(--space-6) clamp(18px, 5vw, 64px);
}

.detail-facts h2,
.detail-map h2 {
  margin: 0 0 var(--space-4);
  font-family: var(--serif);
  font-size: 24px;
  font-weight: 600;
}

.detail-facts dl {
  display: grid;
  gap: 0;
  margin: 0;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  overflow: hidden;
}

.detail-facts dl div {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  border-bottom: 1px solid var(--line);
  padding: var(--space-3) var(--space-4);
}

.detail-facts dl div:last-child {
  border-bottom: 0;
}

.detail-facts dt {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.detail-facts dd {
  margin: 0;
  color: var(--ink);
  font-family: var(--mono);
  font-variant-numeric: tabular-nums;
}

.apply-panel {
  margin-top: var(--space-5);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  padding: var(--space-5);
}

.apply-panel h3 {
  margin: 0 0 var(--space-3);
  font-family: var(--serif);
  font-size: 20px;
  font-weight: 600;
}

.apply-panel p {
  margin: 0 0 var(--space-4);
  color: var(--muted);
  font-size: 14px;
  line-height: 1.55;
}

.apply-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.apply-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.apply-field span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.apply-field input,
.apply-field textarea {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--canvas);
  color: var(--ink);
  padding: 10px 12px;
  font-family: inherit;
}

.apply-field input:focus,
.apply-field textarea:focus {
  outline: none;
  border-color: var(--green);
}

.apply-error {
  margin: 0;
  color: var(--red, #9d3a28);
  font-size: 13px;
  font-weight: 600;
}

.apply-success {
  margin: 0;
  border: 1px solid var(--line);
  border-left: 3px solid var(--green);
  border-radius: var(--radius);
  background: var(--canvas);
  color: var(--ink-soft);
  font-size: 14px;
  line-height: 1.55;
  padding: var(--space-4);
}

.apply-success a {
  color: var(--green);
  font-weight: 700;
}

.rent-btn-primary {
  display: inline-flex;
  align-items: center;
  min-height: 42px;
  border: 0;
  border-radius: var(--radius);
  background: var(--green);
  color: var(--surface);
  font-weight: 700;
  padding: 0 var(--space-5);
  text-decoration: none;
  cursor: pointer;
}

.rent-btn-primary:disabled {
  opacity: 0.6;
  cursor: default;
}

.rent-btn-primary:hover {
  background: var(--green-dark);
}

.rent-footer {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  border-top: 1px solid var(--line);
  padding: var(--space-6) clamp(18px, 5vw, 64px);
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
}

.rent-footer a {
  color: var(--green);
  text-decoration: none;
}

@media (max-width: 920px) {
  .detail-columns {
    grid-template-columns: 1fr;
  }

  .detail-band {
    grid-template-columns: 1fr;
  }
}
</style>
