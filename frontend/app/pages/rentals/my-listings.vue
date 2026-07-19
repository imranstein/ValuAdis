<template>
  <div class="page-shell my-listings-page">
    <section class="page-head">
      <div>
        <p class="page-kicker">{{ t('rentals.myListings.kicker') }}</p>
        <h2 class="page-title">{{ t('rentals.myListings.title') }}</h2>
        <p class="page-subtitle">{{ t('rentals.myListings.subtitle') }}</p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary" type="button" @click="loadAll">
          <i class="pi pi-refresh" aria-hidden="true"></i>
          {{ t('rentals.myListings.refresh') }}
        </button>
        <NuxtLink to="/properties/create" class="btn-primary">
          <i class="pi pi-plus" aria-hidden="true"></i>
          {{ t('rentals.myListings.registerProperty') }}
        </NuxtLink>
      </div>
    </section>

    <section v-if="ownerUnverified" class="panel verification-banner" role="status">
      <i class="pi pi-id-card" aria-hidden="true"></i>
      <div>
        <strong>{{ t('rentals.myListings.verificationPendingTitle') }}</strong>
        <span>{{ t('rentals.myListings.verificationPendingBody') }}</span>
      </div>
    </section>

    <section class="panel create-panel">
      <div class="panel-head">
        <div>
          <h3 class="panel-title">{{ t('rentals.myListings.createPanelTitle') }}</h3>
          <p class="panel-subtitle">{{ t('rentals.myListings.createPanelSubtitle') }}</p>
        </div>
      </div>

      <div class="create-form">
        <select v-model="selectedPropertyId" class="filter-select" aria-label="Select property">
          <option value="">{{ t('rentals.myListings.selectProperty') }}</option>
          <option v-for="property in availableProperties" :key="property.id" :value="String(property.id)">
            {{ property.address }} · {{ property.municipality }} · {{ property.area_sqm }} m²
          </option>
        </select>
        <button class="btn-primary" type="button" :disabled="!selectedPropertyId || creating" @click="createListing">
          {{ creating ? t('rentals.myListings.submitting') : t('rentals.myListings.submitForReview') }}
        </button>
      </div>

      <p v-if="propertiesError" class="inline-error" role="alert">{{ propertiesError }}</p>
      <p v-else-if="properties.length === 0 && !loadingProperties" class="inline-muted">{{ t('rentals.myListings.noProperties') }}</p>
      <p v-if="createError" class="inline-error" role="alert">{{ createError }}</p>
      <p v-if="createNotice" class="inline-notice" role="status">{{ createNotice }}</p>
    </section>

    <section class="table-panel">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">{{ t('rentals.myListings.recordsTitle') }}</h3>
          <p class="panel-subtitle">{{ t('rentals.myListings.showingRecords', { shown: listings.length, total }) }}</p>
        </div>
      </div>

      <div v-if="listingsError" class="state-panel error-state" role="alert">
        <strong>{{ t('rentals.myListings.unavailable') }}</strong>
        <span>{{ listingsError }}</span>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ t('rentals.myListings.colListing') }}</th>
              <th>{{ t('rentals.myListings.colProperty') }}</th>
              <th class="text-right">{{ t('rentals.myListings.colSuggestedRent') }}</th>
              <th class="text-right">{{ t('rentals.myListings.colBand') }}</th>
              <th>{{ t('rentals.myListings.colStatus') }}</th>
              <th class="text-right">{{ t('rentals.myListings.colActions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loadingListings">
              <td colspan="6">{{ t('rentals.myListings.loadingListings') }}</td>
            </tr>
            <tr v-else-if="listings.length === 0">
              <td colspan="6">{{ t('rentals.myListings.noListings') }}</td>
            </tr>
            <tr v-for="listing in listings" v-else :key="listing.public_id">
              <td class="record-id">{{ listing.public_id }}</td>
              <td><strong>{{ listing.property_address || `Property #${listing.property_id}` }}</strong></td>
              <td class="text-right num">{{ formatEtb(listing.suggested_rent) }}</td>
              <td class="text-right num">{{ formatEtb(listing.band_min) }} – {{ formatEtb(listing.band_max) }}</td>
              <td>
                <span class="status-pill" :class="statusClass(listing.status)">{{ statusLabel(listing.status) }}</span>
              </td>
              <td class="text-right">
                <NuxtLink
                  v-if="listing.status === 'published'"
                  :to="`/rent/${listing.public_id}`"
                  class="icon-button inline"
                  :aria-label="t('rentals.myListings.viewPublicListing')"
                >
                  <i class="pi pi-external-link" aria-hidden="true"></i>
                </NuxtLink>
                <button
                  v-if="['published', 'rented'].includes(listing.status)"
                  class="icon-button inline"
                  type="button"
                  :aria-label="t('rentals.myListings.viewApplications')"
                  @click="openApplications(listing)"
                >
                  <i class="pi pi-users" aria-hidden="true"></i>
                </button>
                <button
                  class="icon-button inline"
                  type="button"
                  :aria-label="t('rentals.myListings.managePhotos')"
                  @click="openPhotos(listing)"
                >
                  <i class="pi pi-images" aria-hidden="true"></i>
                </button>
                <button
                  v-if="listing.listing_agreement_pdf"
                  class="icon-button inline"
                  type="button"
                  :aria-label="t('rentals.myListings.downloadAgreement')"
                  :disabled="acting"
                  @click="downloadAgreement(listing)"
                >
                  <i class="pi pi-file-pdf" aria-hidden="true"></i>
                </button>
                <button
                  v-if="['pending_review', 'published'].includes(listing.status)"
                  class="icon-button inline"
                  type="button"
                  :aria-label="t('rentals.myListings.withdrawListing')"
                  :disabled="acting"
                  @click="withdraw(listing)"
                >
                  <i class="pi pi-undo" aria-hidden="true"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-if="applicationsFor" class="table-panel applications-panel" aria-label="Listing applications">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">{{ t('rentals.myListings.applicationsFor', { id: applicationsFor.public_id }) }}</h3>
          <p class="panel-subtitle">{{ t('rentals.myListings.applicationsSubtitle') }}</p>
        </div>
        <button class="icon-button" type="button" :aria-label="t('rentals.myListings.closeApplications')" @click="applicationsFor = null">
          <i class="pi pi-times" aria-hidden="true"></i>
        </button>
      </div>

      <div v-if="applicationsError" class="state-panel error-state" role="alert">
        <strong>{{ t('rentals.myApplications.unavailable') }}</strong>
        <span>{{ applicationsError }}</span>
      </div>
      <p v-if="decisionNotice" class="inline-notice" role="status">{{ decisionNotice }}</p>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ t('rentals.myListings.colRenter') }}</th>
              <th class="text-right">{{ t('rentals.myListings.colOffer') }}</th>
              <th>{{ t('rentals.myListings.colMessage') }}</th>
              <th>{{ t('rentals.myListings.colStatus') }}</th>
              <th class="text-right">{{ t('rentals.myListings.colActions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loadingApplications">
              <td colspan="5">{{ t('rentals.myListings.loadingApplications') }}</td>
            </tr>
            <tr v-else-if="listingApplications.length === 0">
              <td colspan="5">{{ t('rentals.myListings.noApplications') }}</td>
            </tr>
            <tr v-for="app in listingApplications" v-else :key="app.id">
              <td>
                <strong>{{ app.renter_name || t('rentals.myListings.colRenter') }}</strong>
                <span>{{ app.renter_phone || '' }}</span>
              </td>
              <td class="text-right num">{{ formatEtb(app.offered_rent) }}</td>
              <td>{{ app.message || '—' }}</td>
              <td>
                <span class="status-pill" :class="applicationStatusClass(app.status)">{{ statusLabel(app.status) }}</span>
              </td>
              <td class="text-right">
                <template v-if="app.status === 'pending'">
                  <button class="btn-primary btn-compact" type="button" :disabled="acting" @click="decide(app, 'accept')">
                    {{ t('rentals.myListings.accept') }}
                  </button>
                  <button class="btn-secondary btn-compact" type="button" :disabled="acting" @click="decide(app, 'reject')">
                    {{ t('rentals.myListings.reject') }}
                  </button>
                </template>
                <template v-else>—</template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-if="photosFor" class="table-panel photos-panel" aria-label="Listing photos">
      <div class="panel-head table-head">
        <div>
          <h3 class="panel-title">{{ t('rentals.myListings.photosFor', { property: photosFor.property_address || `Property #${photosFor.property_id}` }) }}</h3>
          <p class="panel-subtitle">{{ t('rentals.myListings.photosSubtitle', { max: maxPhotos, sizeMb: maxPhotoSizeMb }) }}</p>
        </div>
        <button class="icon-button" type="button" :aria-label="t('rentals.myListings.closePhotos')" @click="photosFor = null">
          <i class="pi pi-times" aria-hidden="true"></i>
        </button>
      </div>

      <div v-if="photosError" class="state-panel error-state" role="alert">
        <strong>{{ t('rentals.myListings.unavailablePhotos') }}</strong>
        <span>{{ photosError }}</span>
      </div>

      <label class="photo-upload" :class="{ disabled: uploadingPhoto || photos.length >= maxPhotos }">
        <i class="pi pi-upload" aria-hidden="true"></i>
        <span>{{ uploadingPhoto ? t('rentals.myListings.uploading') : t('rentals.myListings.uploadPhoto') }}</span>
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          :disabled="uploadingPhoto || photos.length >= maxPhotos"
          @change="uploadPhoto"
        />
      </label>

      <div v-if="loadingPhotos" class="inline-muted">{{ t('rentals.myListings.loadingPhotos') }}</div>
      <div v-else-if="photos.length === 0" class="inline-muted">{{ t('rentals.myListings.noPhotos') }}</div>
      <div v-else class="photo-grid">
        <figure v-for="photo in photos" :key="photo.id" class="photo-tile">
          <img :src="propertyService.resolvePhotoUrl(photo.url)" :alt="`Property photo ${photo.position + 1}`" />
          <button
            class="icon-button photo-delete"
            type="button"
            :aria-label="t('rentals.myListings.deletePhoto')"
            :disabled="deletingPhotoId === photo.id"
            @click="deletePhoto(photo)"
          >
            <i class="pi pi-trash" aria-hidden="true"></i>
          </button>
        </figure>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import rentalService, { type OwnerApplication, type OwnerListing } from '~/services/rentalService'
import propertyService, { type PropertyPhoto } from '~/services/propertyService'
import { getAccessToken } from '~/utils/authToken'
import { useI18n } from '~/composables/useI18n'

const MAX_PHOTOS = 8
const MAX_PHOTO_SIZE_MB = 5

definePageMeta({ middleware: 'auth' })

const { t } = useI18n()

const config = useRuntimeConfig()
const apiBase = config.public.apiBaseUrl

const properties = ref<any[]>([])
const loadingProperties = ref(true)
const propertiesError = ref('')

const listings = ref<OwnerListing[]>([])
const total = ref(0)
const loadingListings = ref(true)
const listingsError = ref('')

const selectedPropertyId = ref('')
const creating = ref(false)
const createError = ref('')
const createNotice = ref('')
const acting = ref(false)
const ownerUnverified = ref(false)

const applicationsFor = ref<OwnerListing | null>(null)
const listingApplications = ref<OwnerApplication[]>([])
const loadingApplications = ref(false)
const applicationsError = ref('')
const decisionNotice = ref('')

const photosFor = ref<OwnerListing | null>(null)
const photos = ref<PropertyPhoto[]>([])
const loadingPhotos = ref(false)
const photosError = ref('')
const uploadingPhoto = ref(false)
const deletingPhotoId = ref<number | null>(null)
const maxPhotos = MAX_PHOTOS
const maxPhotoSizeMb = MAX_PHOTO_SIZE_MB

const availableProperties = computed(() => {
  const activeIds = new Set(
    listings.value
      .filter((l) => ['draft', 'pending_review', 'published', 'rented'].includes(l.status))
      .map((l) => l.property_id),
  )
  return properties.value.filter((p) => !activeIds.has(p.id))
})

onMounted(loadAll)

async function loadAll() {
  await Promise.all([loadProperties(), loadListings()])
}

async function loadProperties() {
  loadingProperties.value = true
  propertiesError.value = ''
  try {
    const response = await fetch(`${apiBase}/api/v1/properties?limit=100`, {
      headers: { Authorization: `Bearer ${getAccessToken()}` },
    })
    if (!response.ok) throw new Error(`Property request failed with ${response.status}`)
    const body = await response.json()
    properties.value = Array.isArray(body.data) ? body.data : []
  } catch (error) {
    propertiesError.value = error instanceof Error ? error.message : t('rentals.myListings.couldNotLoadProperties')
    properties.value = []
  } finally {
    loadingProperties.value = false
  }
}

async function loadListings() {
  loadingListings.value = true
  listingsError.value = ''
  try {
    const result = await rentalService.myListings()
    listings.value = result.data
    total.value = result.total
  } catch (error) {
    listingsError.value = error instanceof Error ? error.message : t('rentals.myListings.couldNotLoadListings')
    listings.value = []
    total.value = 0
  } finally {
    loadingListings.value = false
  }
}

async function createListing() {
  if (!selectedPropertyId.value) return
  creating.value = true
  createError.value = ''
  createNotice.value = ''
  try {
    const listing = await rentalService.createListing(Number(selectedPropertyId.value))
    createNotice.value = t('rentals.myListings.createSuccessNotice', {
      id: listing.public_id,
      min: formatEtb(listing.band_min),
      max: formatEtb(listing.band_max),
    })
    selectedPropertyId.value = ''
    await loadListings()
  } catch (error) {
    const message = error instanceof Error ? error.message : t('rentals.myListings.couldNotCreateListing')
    createError.value = message
    if (message.toLowerCase().includes('property owners')) {
      ownerUnverified.value = true
    }
  } finally {
    creating.value = false
  }
}

async function withdraw(listing: OwnerListing) {
  acting.value = true
  try {
    await rentalService.withdrawListing(listing.public_id)
    await loadListings()
  } catch (error) {
    listingsError.value = error instanceof Error ? error.message : t('rentals.myListings.couldNotWithdraw')
  } finally {
    acting.value = false
  }
}

async function openApplications(listing: OwnerListing) {
  applicationsFor.value = listing
  loadingApplications.value = true
  applicationsError.value = ''
  decisionNotice.value = ''
  try {
    listingApplications.value = await rentalService.listingApplications(listing.public_id)
  } catch (error) {
    applicationsError.value = error instanceof Error ? error.message : t('rentals.myListings.couldNotLoadApplications')
    listingApplications.value = []
  } finally {
    loadingApplications.value = false
  }
}

async function decide(app: OwnerApplication, action: 'accept' | 'reject') {
  acting.value = true
  applicationsError.value = ''
  decisionNotice.value = ''
  try {
    await rentalService.decideApplication(app.id, action)
    decisionNotice.value =
      action === 'accept'
        ? t('rentals.myListings.applicationAccepted')
        : t('rentals.myListings.applicationRejected')
    if (applicationsFor.value) {
      listingApplications.value = await rentalService.listingApplications(applicationsFor.value.public_id)
    }
    await loadListings()
  } catch (error) {
    applicationsError.value = error instanceof Error ? error.message : t('rentals.myListings.decisionFailed')
  } finally {
    acting.value = false
  }
}

async function openPhotos(listing: OwnerListing) {
  photosFor.value = listing
  loadingPhotos.value = true
  photosError.value = ''
  try {
    photos.value = await propertyService.listPhotos(listing.property_id)
  } catch (error) {
    photosError.value = error instanceof Error ? error.message : t('rentals.myListings.couldNotLoadPhotos')
    photos.value = []
  } finally {
    loadingPhotos.value = false
  }
}

async function uploadPhoto(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file || !photosFor.value) return

  uploadingPhoto.value = true
  photosError.value = ''
  try {
    const photo = await propertyService.uploadPhoto(photosFor.value.property_id, file)
    photos.value = [...photos.value, photo]
  } catch (error) {
    photosError.value = error instanceof Error ? error.message : t('rentals.myListings.couldNotUploadPhoto')
  } finally {
    uploadingPhoto.value = false
  }
}

async function deletePhoto(photo: PropertyPhoto) {
  if (!photosFor.value) return
  deletingPhotoId.value = photo.id
  photosError.value = ''
  try {
    await propertyService.deletePhoto(photosFor.value.property_id, photo.id)
    photos.value = photos.value.filter((p) => p.id !== photo.id)
  } catch (error) {
    photosError.value = error instanceof Error ? error.message : t('rentals.myListings.couldNotDeletePhoto')
  } finally {
    deletingPhotoId.value = null
  }
}

async function downloadAgreement(listing: OwnerListing) {
  acting.value = true
  listingsError.value = ''
  try {
    const blob = await rentalService.downloadListingAgreement(listing.public_id)
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `ValuAdis_ListingAgreement_${listing.public_id}.pdf`
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
  } catch (error) {
    listingsError.value = error instanceof Error ? error.message : t('rentals.myListings.couldNotDownloadAgreement')
  } finally {
    acting.value = false
  }
}

function applicationStatusClass(status: string) {
  if (status === 'accepted') return 'good'
  if (status === 'pending') return 'warn'
  return 'bad'
}

function statusClass(status: string) {
  if (status === 'published') return 'good'
  if (status === 'pending_review') return 'warn'
  if (status === 'withdrawn') return 'bad'
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
</script>

<style scoped>
.verification-banner {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  border-left: 3px solid var(--gold-bright);
  padding: var(--space-4) var(--space-5);
}

.verification-banner i {
  color: var(--gold);
  font-size: 20px;
  margin-top: 2px;
}

.verification-banner strong {
  display: block;
  color: var(--ink);
}

.verification-banner span {
  color: var(--muted);
  font-size: 13px;
  line-height: 1.5;
}

.create-panel {
  padding: var(--space-5);
}

.create-form {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) auto;
  gap: 10px;
  margin-top: var(--space-4);
}

.filter-select {
  min-height: 42px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  color: var(--ink-soft);
  padding: 0 10px;
}

.inline-error {
  margin: var(--space-3) 0 0;
  color: var(--red, #9d3a28);
  font-weight: 600;
  font-size: 13px;
}

.inline-muted {
  margin: var(--space-3) 0 0;
  color: var(--muted);
  font-size: 13px;
}

.inline-notice {
  margin: var(--space-3) 0 0;
  border: 1px solid var(--line);
  border-left: 3px solid var(--green);
  border-radius: var(--radius);
  background: var(--canvas);
  color: var(--ink-soft);
  font-size: 13px;
  padding: var(--space-3) var(--space-4);
}

.applications-panel .panel-subtitle {
  max-width: 560px;
}

.photos-panel .panel-subtitle {
  max-width: 560px;
}

.photo-upload {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  min-height: 40px;
  margin: var(--space-4) 0;
  border: 1px dashed var(--line-strong);
  border-radius: var(--radius);
  background: var(--canvas);
  color: var(--ink-soft);
  font-size: 13px;
  font-weight: 600;
  padding: 0 var(--space-4);
  cursor: pointer;
}

.photo-upload.disabled {
  opacity: 0.6;
  cursor: default;
}

.photo-upload input[type='file'] {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  opacity: 0;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--space-3);
}

.photo-tile {
  position: relative;
  margin: 0;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
  aspect-ratio: 4 / 3;
  background: var(--canvas);
}

.photo-tile img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.photo-delete {
  position: absolute;
  top: 6px;
  right: 6px;
  background: var(--surface);
}

.btn-compact {
  min-height: 32px;
  padding: 0 12px;
  font-size: 13px;
  margin-left: 8px;
}

@media (max-width: 720px) {
  .create-form {
    grid-template-columns: 1fr;
  }
}
</style>
