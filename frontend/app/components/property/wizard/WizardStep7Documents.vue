<template>
  <div class="wizard-step">
    <div class="step-header">
      <div class="step-icon-wrap">
        <i class="pi pi-folder-open text-2xl text-white" />
      </div>
      <div>
        <h2 class="step-title">Documents & Photos</h2>
        <p class="step-subtitle">Upload property photos and required legal documents</p>
      </div>
    </div>

    <div class="step-body">
      <!-- Photos -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-camera text-teal-600" /> Property Photos
          <span class="badge-count">{{ form.photos.length }}/20</span>
        </h3>
        <p class="section-hint">Upload up to 20 photos. Max 5MB each. JPEG, PNG, WebP.</p>

        <div
          class="drop-zone"
          :class="{ 'drag-over': draggingPhoto }"
          @dragover.prevent="draggingPhoto = true"
          @dragleave="draggingPhoto = false"
          @drop.prevent="handlePhotoDrop"
          @click="photoInput?.click()"
        >
          <i class="pi pi-images drop-icon" />
          <span>Drag & drop photos here, or click to browse</span>
          <input
            ref="photoInput"
            type="file"
            accept="image/*"
            multiple
            class="hidden-input"
            @change="handlePhotoSelect"
          />
        </div>

        <div v-if="form.photos.length > 0" class="photo-grid">
          <div v-for="(photo, i) in form.photos" :key="i" class="photo-thumb">
            <img :src="photoURLs[i]" :alt="photo.name" class="thumb-img" />
            <button class="thumb-remove" @click="removePhoto(i)" type="button">
              <i class="pi pi-times" />
            </button>
            <span class="thumb-name">{{ truncate(photo.name) }}</span>
          </div>
        </div>
      </section>

      <!-- Documents -->
      <section class="form-section">
        <h3 class="section-title">
          <i class="pi pi-file-pdf text-teal-600" /> Legal Documents
          <span class="badge-count">{{ form.documents.length }}/10</span>
        </h3>
        <p class="section-hint">Upload PDF, DOC, or DOCX files. Max 10MB each.</p>

        <!-- Required checklist -->
        <div class="doc-checklist">
          <div
            v-for="req in requiredDocs"
            :key="req.key"
            class="doc-check-item"
            :class="{ uploaded: req.uploaded }"
          >
            <i :class="req.uploaded ? 'pi pi-check-circle text-emerald-500' : 'pi pi-circle text-slate-300'" />
            <span>{{ req.label }}</span>
            <span class="doc-status">{{ req.uploaded ? 'Uploaded' : 'Required' }}</span>
          </div>
        </div>

        <div
          class="drop-zone doc-drop"
          :class="{ 'drag-over': draggingDoc }"
          @dragover.prevent="draggingDoc = true"
          @dragleave="draggingDoc = false"
          @drop.prevent="handleDocDrop"
          @click="docInput?.click()"
        >
          <i class="pi pi-file-plus drop-icon" />
          <span>Drag & drop documents here, or click to browse</span>
          <input
            ref="docInput"
            type="file"
            accept=".pdf,.doc,.docx"
            multiple
            class="hidden-input"
            @change="handleDocSelect"
          />
        </div>

        <div v-if="form.documents.length > 0" class="doc-list">
          <div v-for="(doc, i) in form.documents" :key="i" class="doc-item">
            <i :class="docIcon(doc.name)" class="doc-type-icon" />
            <div class="doc-info">
              <span class="doc-name">{{ doc.name }}</span>
              <span class="doc-size">{{ formatSize(doc.size) }}</span>
            </div>
            <button class="doc-remove" @click="removeDoc(i)" type="button">
              <i class="pi pi-trash" />
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { usePropertyWizardStore } from '~/stores/propertyWizard'

const store = usePropertyWizardStore()
const form = store.formData

const photoInput = ref<HTMLInputElement | null>(null)
const docInput = ref<HTMLInputElement | null>(null)
const draggingPhoto = ref(false)
const draggingDoc = ref(false)

const photoURLs = computed(() =>
  form.photos.map(f => URL.createObjectURL(f))
)

function handlePhotoSelect(e: Event) {
  const files = Array.from((e.target as HTMLInputElement).files || [])
  addPhotos(files)
}
function handlePhotoDrop(e: DragEvent) {
  draggingPhoto.value = false
  const files = Array.from(e.dataTransfer?.files || []).filter(f => f.type.startsWith('image/'))
  addPhotos(files)
}
function addPhotos(files: File[]) {
  // Enforce image type in code — drag-and-drop can bypass input[accept]
  const filtered = files.filter(f => f.type.startsWith('image/') && f.size <= 5 * 1024 * 1024)
  const remaining = 20 - form.photos.length
  form.photos.push(...filtered.slice(0, remaining))
}
function removePhoto(i: number) {
  form.photos.splice(i, 1)
}

function handleDocSelect(e: Event) {
  const files = Array.from((e.target as HTMLInputElement).files || [])
  addDocs(files)
}
function handleDocDrop(e: DragEvent) {
  draggingDoc.value = false
  const files = Array.from(e.dataTransfer?.files || [])
  addDocs(files)
}
const ALLOWED_DOC_TYPES = [
  'application/pdf',
  'image/jpeg', 'image/png', 'image/tiff',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]
function addDocs(files: File[]) {
  // Enforce allowed document types — drag-and-drop can bypass input[accept]
  const filtered = files.filter(
    f => ALLOWED_DOC_TYPES.includes(f.type) && f.size <= 10 * 1024 * 1024
  )
  const remaining = 10 - form.documents.length
  form.documents.push(...filtered.slice(0, remaining))
}
function removeDoc(i: number) {
  form.documents.splice(i, 1)
}

const docKeywords: Record<string, string> = {
  'title': 'title_deed',
  'deed': 'title_deed',
  'tax': 'tax_clearance',
  'survey': 'survey_plan',
}
const requiredDocs = computed(() => {
  const names = form.documents.map(d => d.name.toLowerCase())
  return [
    { key: 'title_deed', label: 'Title Deed / Land Certificate', uploaded: names.some(n => n.includes('title') || n.includes('deed')) },
    { key: 'tax_clearance', label: 'Tax Clearance Certificate', uploaded: names.some(n => n.includes('tax')) },
    { key: 'survey_plan', label: 'Survey / Site Plan', uploaded: names.some(n => n.includes('survey') || n.includes('plan')) },
  ]
})

function docIcon(name: string): string {
  if (name.endsWith('.pdf')) return 'pi pi-file-pdf text-red-500'
  if (name.endsWith('.doc') || name.endsWith('.docx')) return 'pi pi-file-word text-blue-500'
  return 'pi pi-file text-slate-400'
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function truncate(name: string, max = 18): string {
  return name.length > max ? name.slice(0, max) + '…' : name
}
</script>

<style scoped>
.wizard-step { display: flex; flex-direction: column; gap: 0; }

.step-header {
  display: flex; align-items: center; gap: 1rem;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
  color: white;
  border-radius: 12px 12px 0 0;
}
.step-icon-wrap {
  width: 48px; height: 48px;
  background: rgba(255,255,255,0.2); border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.step-title { font-size: 1.25rem; font-weight: 700; margin: 0 0 0.2rem; }
.step-subtitle { font-size: 0.875rem; opacity: 0.85; margin: 0; }

.step-body { padding: 2rem; display: flex; flex-direction: column; gap: 2rem; }

.form-section { display: flex; flex-direction: column; gap: 1rem; }
.section-title {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.95rem; font-weight: 600; color: #334155;
  padding-bottom: 0.5rem; border-bottom: 1px solid #e2e8f0; margin: 0;
}
.badge-count {
  margin-left: auto; font-size: 0.75rem; font-weight: 600;
  background: #f1f5f9; color: #64748b;
  padding: 0.1rem 0.5rem; border-radius: 12px;
}
.section-hint { font-size: 0.8rem; color: #94a3b8; margin: 0; }

.drop-zone {
  display: flex; flex-direction: column; align-items: center; gap: 0.5rem;
  padding: 2rem 1rem;
  border: 2px dashed #cbd5e1; border-radius: 12px;
  background: #f8fafc; cursor: pointer; transition: all 0.2s;
  color: #94a3b8; font-size: 0.875rem; text-align: center;
}
.drop-zone:hover, .drop-zone.drag-over {
  border-color: #0d9488; background: #f0fdfa; color: #0f766e;
}
.doc-drop { padding: 1.5rem 1rem; }
.drop-icon { font-size: 2rem; }
.hidden-input { display: none; }

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.75rem;
}
.photo-thumb {
  position: relative; border-radius: 8px; overflow: hidden;
  border: 1.5px solid #e2e8f0;
}
.thumb-img { width: 100%; height: 80px; object-fit: cover; display: block; }
.thumb-remove {
  position: absolute; top: 4px; right: 4px;
  width: 20px; height: 20px; border-radius: 50%;
  background: rgba(220, 38, 38, 0.85); border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 0.65rem;
}
.thumb-name {
  display: block; padding: 0.2rem 0.3rem;
  font-size: 0.65rem; color: #64748b; background: #f8fafc;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.doc-checklist { display: flex; flex-direction: column; gap: 0.5rem; }
.doc-check-item {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.5rem 0.75rem; border-radius: 8px;
  background: #f8fafc; font-size: 0.875rem; color: #475569;
}
.doc-check-item.uploaded { background: #f0fdf4; color: #166534; }
.doc-status { margin-left: auto; font-size: 0.75rem; font-weight: 600; color: #94a3b8; }
.doc-check-item.uploaded .doc-status { color: #059669; }

.doc-list { display: flex; flex-direction: column; gap: 0.5rem; }
.doc-item {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.6rem 0.85rem; border-radius: 8px;
  border: 1px solid #e2e8f0; background: white;
}
.doc-type-icon { font-size: 1.25rem; flex-shrink: 0; }
.doc-info { flex: 1; display: flex; flex-direction: column; }
.doc-name { font-size: 0.875rem; font-weight: 500; color: #334155; }
.doc-size { font-size: 0.75rem; color: #94a3b8; }
.doc-remove {
  background: none; border: none; cursor: pointer;
  color: #94a3b8; padding: 0.2rem; border-radius: 4px;
  transition: color 0.15s;
}
.doc-remove:hover { color: #dc2626; }

@media (max-width: 640px) {
  .step-body { padding: 1rem; }
  .photo-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
