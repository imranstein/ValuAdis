<template>
  <main class="rent-detail-page">
    <nav class="rent-nav" aria-label="Public navigation">
      <NuxtLink to="/" class="rent-brand">
        <span class="rent-mark" aria-hidden="true">V</span>
        <span>ValuAdis Rentals</span>
      </NuxtLink>
      <div class="rent-nav-links">
        <NuxtLink to="/rent">All listings</NuxtLink>
        <NuxtLink to="/login" class="rent-login">Workspace sign in</NuxtLink>
      </div>
    </nav>

    <div v-if="loading" class="rent-state">Loading listing…</div>

    <div v-else-if="errorMessage" class="rent-state rent-state-error" role="alert">
      <strong>Listing unavailable</strong>
      <span>{{ errorMessage }}</span>
      <NuxtLink to="/rent" class="rent-back-link">Back to all listings</NuxtLink>
    </div>

    <template v-else-if="listing">
      <header class="detail-head">
        <div>
          <p class="detail-id">
            <span class="rent-card-id">{{ listing.public_id }}</span>
            <span class="rent-cert-badge" title="Backed by an approved rent valuation">
              <i class="pi pi-verified" aria-hidden="true"></i>
              Valuation certified
            </span>
          </p>
          <h1>{{ listing.property.address }}</h1>
          <p class="detail-location">
            {{ listing.property.subcity || listing.property.municipality }},
            {{ listing.property.municipality }}
            <template v-if="listing.published_at">
              · Published {{ formatDate(listing.published_at) }}
            </template>
          </p>
        </div>
      </header>

      <section class="detail-band" aria-label="Published rent band">
        <div>
          <span>Suggested rent</span>
          <strong>{{ formatEtb(listing.suggested_rent) }}/mo</strong>
        </div>
        <div>
          <span>Band minimum</span>
          <strong>{{ formatEtb(listing.band_min) }}</strong>
        </div>
        <div>
          <span>Band maximum</span>
          <strong>{{ formatEtb(listing.band_max) }}</strong>
        </div>
        <p class="detail-band-note">
          Applications are accepted only inside this officer-published band. The band is frozen
          at publication and backed by an approved rent valuation.
        </p>
      </section>

      <section class="detail-gallery" aria-label="Property photos">
        <div v-if="listing.property.photo_urls.length" class="gallery-grid">
          <img
            v-for="url in listing.property.photo_urls"
            :key="url"
            :src="resolvePhotoUrl(url)"
            :alt="`Photo of ${listing.property.address}`"
            loading="lazy"
          />
        </div>
        <div v-else class="rent-state gallery-placeholder">No photos have been uploaded for this listing yet.</div>
      </section>

      <div class="detail-columns">
        <section class="detail-facts" aria-label="Property facts">
          <h2>Property facts</h2>
          <dl>
            <div>
              <dt>Type</dt>
              <dd>{{ labelize(listing.property.property_subtype || listing.property.property_type) }}</dd>
            </div>
            <div>
              <dt>Area</dt>
              <dd>{{ formatArea(listing.property.area_sqm) }} m²</dd>
            </div>
            <div v-if="listing.property.building_area_sqm">
              <dt>Building area</dt>
              <dd>{{ formatArea(listing.property.building_area_sqm) }} m²</dd>
            </div>
            <div v-if="listing.property.number_of_bedrooms != null">
              <dt>Bedrooms</dt>
              <dd>{{ listing.property.number_of_bedrooms }}</dd>
            </div>
            <div v-if="listing.property.number_of_bathrooms != null">
              <dt>Bathrooms</dt>
              <dd>{{ listing.property.number_of_bathrooms }}</dd>
            </div>
            <div v-if="listing.property.number_of_floors != null">
              <dt>Floors</dt>
              <dd>{{ listing.property.number_of_floors }}</dd>
            </div>
            <div v-if="listing.property.year_built">
              <dt>Year built</dt>
              <dd>{{ listing.property.year_built }}</dd>
            </div>
            <div v-if="listing.property.condition">
              <dt>Condition</dt>
              <dd>{{ labelize(listing.property.condition) }}</dd>
            </div>
          </dl>

          <div class="apply-panel">
            <h3>Apply for this listing</h3>

            <template v-if="!isAuthenticated">
              <p>
                Applications are made through a registered citizen account, at any amount inside
                the published band.
              </p>
              <NuxtLink to="/rent/signup" class="rent-btn-primary">Register as a renter</NuxtLink>
            </template>

            <template v-else-if="applicationResult">
              <p class="apply-success" role="status">
                Application submitted at {{ formatEtb(applicationResult.offered_rent) }}/mo.
                Status: {{ labelize(applicationResult.status) }}. Track it under
                <NuxtLink to="/rentals/my-applications">my applications</NuxtLink>.
              </p>
            </template>

            <form v-else class="apply-form" @submit.prevent="submitApplication">
              <label class="apply-field">
                <span>Your offer (ETB/month, {{ formatEtb(listing.band_min) }} – {{ formatEtb(listing.band_max) }})</span>
                <input
                  v-model.number="offeredRent"
                  type="number"
                  required
                  :min="listing.band_min"
                  :max="listing.band_max"
                  step="any"
                />
              </label>
              <p v-if="offerOutsideBand" class="apply-error" role="alert">
                Offers outside the published band are rejected by the registry.
              </p>
              <label class="apply-field">
                <span>Message to the owner (optional)</span>
                <textarea v-model="applicationMessage" rows="2" maxlength="1000"></textarea>
              </label>
              <p v-if="applyError" class="apply-error" role="alert">{{ applyError }}</p>
              <button class="rent-btn-primary" type="submit" :disabled="applying || offerOutsideBand">
                {{ applying ? 'Submitting…' : 'Apply within band' }}
              </button>
            </form>
          </div>
        </section>

        <section class="detail-map" aria-label="Listing location">
          <h2>Location</h2>
          <ClientOnly>
            <PropertyMap
              v-if="mapProperties.length"
              :properties="mapProperties"
              :center="mapCenter"
              :zoom="14"
              height="420px"
            />
            <div v-else class="rent-state">Location coordinates are not published for this listing.</div>
          </ClientOnly>
        </section>
      </div>
    </template>

    <footer class="rent-footer">
      <span>ValuAdis &mdash; government-mediated rental registry</span>
      <NuxtLink to="/rent">All listings</NuxtLink>
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

definePageMeta({ layout: 'landing' })

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
        ? 'This listing is not published.'
        : error instanceof Error
          ? error.message
          : 'Could not load this listing.'
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
