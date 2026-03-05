# Property Registration Wizard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a 7-step property registration wizard with full-stack field extension, Leaflet mapping, AI valuation with trust scoring, and a reviewer feedback loop.

**Architecture:** Composable step components orchestrated by a `PropertyWizard.vue` shell, Pinia store (`usePropertyWizardStore`) as single source of truth, backend DB extended with ~30 new fields, new `ValuationFeedback` model + `valuation_learning.json` for AI trust scoring.

**Tech Stack:** Nuxt 3, Vue 3, PrimeVue 3, Tailwind CSS, Pinia, Leaflet + leaflet-draw, FastAPI, SQLAlchemy + Alembic, PostgreSQL + PostGIS

---

## Task 1: Backend — Extend Property DB Model

**Files:**
- Modify: `backend/app/data/models/property.py`

**Step 1:** Replace existing Property model with extended version including all new fields:

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # --- Identity ---
    property_ref = Column(String(50), unique=True, index=True)  # e.g. ADD-2025-001234
    parcel_number = Column(String(100))
    title_deed_number = Column(String(100))
    registration_date = Column(DateTime(timezone=True))

    # --- Location ---
    address = Column(String(500), nullable=False)
    municipality = Column(String(100), nullable=False)
    region = Column(String(100))          # Ethiopian region
    subcity = Column(String(100))
    woreda = Column(String(100))
    kebele = Column(String(100))
    zone = Column(String(100))
    neighborhood = Column(String(200))

    # --- Classification ---
    property_type = Column(String(50), nullable=False)  # residential/commercial/industrial/agricultural
    property_subtype = Column(String(50))               # apartment/villa/office/shop/warehouse/farm

    # --- Spatial ---
    boundary = Column(Geometry('POLYGON', srid=4326))
    latitude = Column(Float)
    longitude = Column(Float)
    area_sqm = Column(Float, nullable=False)
    building_area_sqm = Column(Float)

    # --- Physical ---
    number_of_floors = Column(Integer)
    number_of_rooms = Column(Integer)
    number_of_bedrooms = Column(Integer)
    number_of_bathrooms = Column(Integer)
    year_built = Column(Integer)
    construction_material = Column(String(50))   # concrete/brick/wood/iron/mixed
    roof_material = Column(String(50))
    floor_material = Column(String(50))
    construction_quality = Column(String(20))    # premium/good/average/poor
    condition = Column(String(20))               # excellent/good/fair/poor
    parking_spaces = Column(Integer, default=0)

    # --- Amenities & Utilities (JSON for flexibility) ---
    amenities = Column(JSON, default=dict)   # {elevator, security, generator, water_tank, solar, cctv, gym, pool, garden, fence}
    utilities = Column(JSON, default=dict)   # {electricity, water, internet, sewage, gas}
    additional_features = Column(Text)

    # --- Ownership ---
    owner_name = Column(String(200))
    owner_phone = Column(String(30))
    owner_email = Column(String(200))
    owner_id_type = Column(String(50))      # national_id/passport/kebele_id
    owner_id_number = Column(String(100))
    ownership_type = Column(String(50))     # private/government/corporate/joint_venture/trust
    legal_description = Column(Text)

    # --- Valuation ---
    valuation_method = Column(String(30))   # comparative/cost/income
    land_value = Column(Float)
    building_value = Column(Float)
    market_value = Column(Float)
    taxable_value = Column(Float)
    valuation_date = Column(DateTime(timezone=True))
    valuer_name = Column(String(200))
    valuer_license_number = Column(String(100))
    valuer_phone = Column(String(30))
    comparable_properties = Column(JSON, default=list)
    valuation_notes = Column(Text)

    # --- AI Valuation ---
    ai_estimated_value = Column(Float)
    ai_confidence_score = Column(Float)       # 0.0 - 1.0
    ai_trust_score_at_time = Column(Float)    # snapshot of global trust score

    # --- Status ---
    status = Column(String(50), default="draft")   # draft/pending_review/valued/certified

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="properties")
    valuations = relationship("Valuation", back_populates="property")
    feedback = relationship("ValuationFeedback", back_populates="property")
```

**Step 2:** Commit:
```bash
git add backend/app/data/models/property.py
git commit -m "feat(db): extend Property model with 30 new fields for comprehensive valuation"
```

---

## Task 2: Backend — Add ValuationFeedback Model

**Files:**
- Create: `backend/app/data/models/valuation_feedback.py`
- Modify: `backend/app/data/models/__init__.py`

**Step 1:** Create the feedback model:

```python
"""ValuationFeedback Model — stores reviewer decisions for AI trust scoring"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ValuationFeedback(Base):
    __tablename__ = "valuation_feedback"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    valuation_id = Column(Integer, ForeignKey("valuations.id"), nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    ai_estimate = Column(Float, nullable=False)
    final_approved_value = Column(Float, nullable=False)
    delta_percentage = Column(Float)               # abs((final - ai) / ai * 100)
    approved_without_change = Column(Boolean, default=False)
    reviewer_comments = Column(Text)
    trust_impact = Column(Float)                   # +/- applied to global score
    property_context = Column(JSON, default=dict)  # snapshot of key property attrs

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    property = relationship("Property", back_populates="feedback")
    reviewer = relationship("User")
```

**Step 2:** Update `__init__.py` to import the new model so Alembic picks it up.

**Step 3:** Commit:
```bash
git add backend/app/data/models/valuation_feedback.py backend/app/data/models/__init__.py
git commit -m "feat(db): add ValuationFeedback model for AI trust scoring loop"
```

---

## Task 3: Backend — Alembic Migration

**Files:**
- Create: `backend/alembic/versions/<hash>_extend_property_add_feedback.py`

**Step 1:** Generate migration:
```bash
cd backend && alembic revision --autogenerate -m "extend_property_add_feedback"
```

**Step 2:** Review generated migration, then run it:
```bash
alembic upgrade head
```

**Step 3:** Commit:
```bash
git add backend/alembic/versions/
git commit -m "feat(migration): extend property table and add valuation_feedback"
```

---

## Task 4: Backend — Extend Property Schemas

**Files:**
- Modify: `backend/app/schemas/property.py`

**Step 1:** Replace `PropertyCreate` with comprehensive schema covering all new fields. Key additions:

```python
from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class PropertyCreate(BaseModel):
    # Identity
    parcel_number: Optional[str] = None
    title_deed_number: Optional[str] = None

    # Location (required)
    address: str
    municipality: str
    region: Optional[str] = None
    subcity: Optional[str] = None
    woreda: Optional[str] = None
    kebele: Optional[str] = None
    zone: Optional[str] = None
    neighborhood: Optional[str] = None

    # Classification
    property_type: str
    property_subtype: Optional[str] = None

    # Spatial
    coordinates: List[List[float]]  # [[lon, lat], ...]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_sqm: float
    building_area_sqm: Optional[float] = None

    # Physical
    number_of_floors: Optional[int] = None
    number_of_rooms: Optional[int] = None
    number_of_bedrooms: Optional[int] = None
    number_of_bathrooms: Optional[int] = None
    year_built: Optional[int] = None
    construction_material: Optional[str] = None
    roof_material: Optional[str] = None
    floor_material: Optional[str] = None
    construction_quality: Optional[str] = None
    condition: Optional[str] = None
    parking_spaces: Optional[int] = 0

    # Amenities & Utilities
    amenities: Optional[Dict[str, bool]] = Field(default_factory=dict)
    utilities: Optional[Dict[str, bool]] = Field(default_factory=dict)
    additional_features: Optional[str] = None

    # Ownership
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    owner_id_type: Optional[str] = None
    owner_id_number: Optional[str] = None
    ownership_type: Optional[str] = None
    legal_description: Optional[str] = None

    # Valuation
    valuation_method: Optional[str] = None
    land_value: Optional[float] = None
    building_value: Optional[float] = None
    market_value: Optional[float] = None
    valuation_date: Optional[datetime] = None
    valuer_name: Optional[str] = None
    valuer_license_number: Optional[str] = None
    comparable_properties: Optional[List[Dict]] = Field(default_factory=list)
    valuation_notes: Optional[str] = None


class PropertyUpdate(BaseModel):
    # All fields optional for PATCH semantics
    address: Optional[str] = None
    municipality: Optional[str] = None
    # ... mirror PropertyCreate with all Optional
    status: Optional[str] = None
```

**Step 2:** Commit:
```bash
git add backend/app/schemas/property.py
git commit -m "feat(schemas): extend PropertyCreate/Update with all new wizard fields"
```

---

## Task 5: Backend — Valuation Feedback Service + Trust Score

**Files:**
- Create: `backend/app/services/valuation_feedback_service.py`
- Create: `backend/data/valuation_learning.json` (initial seed)

**Step 1:** Create `valuation_learning.json` seed:
```json
{
  "version": "1.0",
  "trust_score": 75.0,
  "total_reviews": 0,
  "approved_unchanged": 0,
  "modified_reviews": 0,
  "avg_error_pct": 0.0,
  "last_30d_accuracy": 0.0,
  "feedback_history": [],
  "patterns": {
    "overestimated_when": [],
    "underestimated_when": []
  }
}
```

**Step 2:** Create feedback service:

```python
"""ValuationFeedbackService — manages AI trust scoring and learning loop"""

import json
import os
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.data.models.valuation_feedback import ValuationFeedback

LEARNING_FILE = os.path.join(os.path.dirname(__file__), "../../data/valuation_learning.json")
APPROVAL_BOOST = 2.0      # +2.0 pts on unchanged approval
MODIFICATION_PENALTY = 0.05  # delta_pct * 0.05 penalty


def _load_learning() -> dict:
    try:
        with open(LEARNING_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"version": "1.0", "trust_score": 75.0, "total_reviews": 0,
                "approved_unchanged": 0, "modified_reviews": 0,
                "avg_error_pct": 0.0, "last_30d_accuracy": 0.0,
                "feedback_history": [], "patterns": {"overestimated_when": [], "underestimated_when": []}}


def _save_learning(data: dict):
    os.makedirs(os.path.dirname(LEARNING_FILE), exist_ok=True)
    with open(LEARNING_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def get_trust_metrics() -> dict:
    return _load_learning()


def record_feedback(
    db: Session,
    property_id: int,
    reviewer_id: int,
    ai_estimate: float,
    final_value: float,
    approved_without_change: bool,
    comments: Optional[str],
    property_context: dict,
    valuation_id: Optional[int] = None,
) -> ValuationFeedback:
    delta_pct = abs((final_value - ai_estimate) / ai_estimate * 100) if ai_estimate else 0

    # Compute trust impact
    if approved_without_change:
        trust_impact = APPROVAL_BOOST
    else:
        trust_impact = -(delta_pct * MODIFICATION_PENALTY)

    # Persist to DB
    feedback = ValuationFeedback(
        property_id=property_id,
        valuation_id=valuation_id,
        reviewer_id=reviewer_id,
        ai_estimate=ai_estimate,
        final_approved_value=final_value,
        delta_percentage=delta_pct,
        approved_without_change=approved_without_change,
        reviewer_comments=comments,
        trust_impact=trust_impact,
        property_context=property_context,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    # Update learning JSON
    learning = _load_learning()
    old_score = learning["trust_score"]
    new_score = max(0.0, min(100.0, old_score + trust_impact))
    learning["trust_score"] = round(new_score, 2)
    learning["total_reviews"] += 1
    if approved_without_change:
        learning["approved_unchanged"] += 1
    else:
        learning["modified_reviews"] += 1

    # Running avg error
    n = learning["total_reviews"]
    learning["avg_error_pct"] = round(
        (learning["avg_error_pct"] * (n - 1) + delta_pct) / n, 2
    )

    # Append to history
    learning["feedback_history"].append({
        "feedback_id": feedback.id,
        "property_id": property_id,
        "ai_estimate": ai_estimate,
        "final_value": final_value,
        "delta_pct": round(delta_pct, 2),
        "approved": approved_without_change,
        "comments": comments,
        "trust_impact": round(trust_impact, 3),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": property_context,
    })

    _save_learning(learning)
    return feedback
```

**Step 3:** Commit:
```bash
git add backend/app/services/valuation_feedback_service.py backend/data/valuation_learning.json
git commit -m "feat(backend): add valuation feedback service with AI trust scoring"
```

---

## Task 6: Backend — Feedback API Routes

**Files:**
- Create: `backend/app/api/routes/valuation_feedback.py`
- Modify: `backend/app/main.py` (or router aggregator) to include new router

**Step 1:** Create routes:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.auth import get_current_user
from app.services import valuation_feedback_service as svc

router = APIRouter(prefix="/api/v1/valuation-feedback", tags=["valuation-feedback"])


class FeedbackCreate(BaseModel):
    property_id: int
    valuation_id: Optional[int] = None
    ai_estimate: float
    final_value: float
    approved_without_change: bool
    comments: Optional[str] = None
    property_context: Optional[dict] = {}


@router.post("")
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db),
                    current_user=Depends(get_current_user)):
    fb = svc.record_feedback(
        db=db,
        property_id=payload.property_id,
        reviewer_id=current_user.id,
        ai_estimate=payload.ai_estimate,
        final_value=payload.final_value,
        approved_without_change=payload.approved_without_change,
        comments=payload.comments,
        property_context=payload.property_context,
        valuation_id=payload.valuation_id,
    )
    return {"success": True, "feedback_id": fb.id,
            "trust_score": svc.get_trust_metrics()["trust_score"]}


@router.get("/metrics")
def get_metrics():
    return svc.get_trust_metrics()
```

**Step 2:** Register router in main app.

**Step 3:** Commit:
```bash
git add backend/app/api/routes/valuation_feedback.py
git commit -m "feat(api): add /valuation-feedback endpoints for reviewer loop"
```

---

## Task 7: Frontend — Pinia Wizard Store

**Files:**
- Create: `frontend/app/stores/propertyWizard.ts`

**Step 1:** Create the store with full state, step validation, draft persistence, and AI calc:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface WizardFormData {
  // Step 1 - Basic Info
  property_ref: string
  parcel_number: string
  title_deed_number: string
  registration_date: string
  address: string
  municipality: string
  region: string
  subcity: string
  woreda: string
  kebele: string
  zone: string
  neighborhood: string
  property_type: string
  property_subtype: string

  // Step 2 - Location (populated from map)
  latitude: number | null
  longitude: number | null
  boundaries: number[][]

  // Step 3 - Physical
  area_sqm: number | null
  building_area_sqm: number | null
  number_of_floors: number | null
  number_of_rooms: number | null
  number_of_bedrooms: number | null
  number_of_bathrooms: number | null
  year_built: number | null
  construction_material: string
  roof_material: string
  floor_material: string
  construction_quality: string
  condition: string
  parking_spaces: number | null

  // Step 4 - Amenities
  amenities: Record<string, boolean>
  utilities: Record<string, boolean>
  additional_features: string

  // Step 5 - Valuation
  valuation_method: string
  land_value: number | null
  building_value: number | null
  market_value: number | null
  valuation_date: string
  valuer_name: string
  valuer_license_number: string
  valuer_phone: string
  comparable_properties: any[]
  valuation_notes: string

  // Step 6 - Ownership
  owner_name: string
  owner_phone: string
  owner_email: string
  owner_id_type: string
  owner_id_number: string
  ownership_type: string
  legal_description: string

  // Step 7 - Documents (handled separately as File objects)
  photos: File[]
  documents: File[]
}

const DRAFT_KEY = 'property_wizard_draft'
const TOTAL_STEPS = 7

const defaultForm = (): WizardFormData => ({
  property_ref: '', parcel_number: '', title_deed_number: '', registration_date: '',
  address: '', municipality: '', region: '', subcity: '', woreda: '', kebele: '',
  zone: '', neighborhood: '', property_type: '', property_subtype: '',
  latitude: null, longitude: null, boundaries: [],
  area_sqm: null, building_area_sqm: null, number_of_floors: null,
  number_of_rooms: null, number_of_bedrooms: null, number_of_bathrooms: null,
  year_built: null, construction_material: '', roof_material: '', floor_material: '',
  construction_quality: '', condition: '', parking_spaces: null,
  amenities: {}, utilities: {}, additional_features: '',
  valuation_method: '', land_value: null, building_value: null, market_value: null,
  valuation_date: '', valuer_name: '', valuer_license_number: '', valuer_phone: '',
  comparable_properties: [], valuation_notes: '',
  owner_name: '', owner_phone: '', owner_email: '', owner_id_type: '',
  owner_id_number: '', ownership_type: '', legal_description: '',
  photos: [], documents: [],
})

export const usePropertyWizardStore = defineStore('propertyWizard', () => {
  const currentStep = ref(1)
  const completedSteps = ref<Set<number>>(new Set())
  const formData = ref<WizardFormData>(defaultForm())
  const stepErrors = ref<Record<number, Record<string, string>>>({})
  const isSubmitting = ref(false)
  const isDraft = ref(false)
  const aiEstimate = ref<{ value: number; confidence: number; method: string; breakdown: any } | null>(null)
  const trustMetrics = ref<{ trust_score: number; total_reviews: number; avg_error_pct: number } | null>(null)

  const progressPercent = computed(() => Math.round((completedSteps.value.size / TOTAL_STEPS) * 100))
  const canProceed = computed(() => !stepErrors.value[currentStep.value] || Object.keys(stepErrors.value[currentStep.value] || {}).length === 0)

  function validateStep(step: number): boolean {
    const errs: Record<string, string> = {}
    const d = formData.value

    if (step === 1) {
      if (!d.address?.trim()) errs.address = 'Address is required'
      if (!d.municipality) errs.municipality = 'Municipality is required'
      if (!d.property_type) errs.property_type = 'Property type is required'
      if (!d.region) errs.region = 'Region is required'
    }
    if (step === 2) {
      if (!d.latitude || !d.longitude) errs.location = 'Place a pin on the map to set location'
    }
    if (step === 3) {
      if (!d.area_sqm || d.area_sqm <= 0) errs.area_sqm = 'Land area is required'
      if (!d.condition) errs.condition = 'Property condition is required'
    }

    stepErrors.value[step] = errs
    if (Object.keys(errs).length === 0) completedSteps.value.add(step)
    return Object.keys(errs).length === 0
  }

  function nextStep() {
    if (validateStep(currentStep.value) && currentStep.value < TOTAL_STEPS) {
      currentStep.value++
    }
  }

  function prevStep() {
    if (currentStep.value > 1) currentStep.value--
  }

  function goToStep(step: number) {
    currentStep.value = step
  }

  function saveDraft() {
    const serializable = { ...formData.value, photos: [], documents: [] }
    localStorage.setItem(DRAFT_KEY, JSON.stringify({ data: serializable, step: currentStep.value }))
    isDraft.value = true
  }

  function loadDraft(): boolean {
    try {
      const raw = localStorage.getItem(DRAFT_KEY)
      if (!raw) return false
      const { data, step } = JSON.parse(raw)
      formData.value = { ...defaultForm(), ...data }
      currentStep.value = step || 1
      isDraft.value = true
      return true
    } catch { return false }
  }

  function clearWizard() {
    formData.value = defaultForm()
    currentStep.value = 1
    completedSteps.value.clear()
    stepErrors.value = {}
    isDraft.value = false
    aiEstimate.value = null
    localStorage.removeItem(DRAFT_KEY)
  }

  async function calculateAIValuation() {
    const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8020'
    const token = localStorage.getItem('valuadis_token')
    const d = formData.value

    const res = await fetch(`${API_BASE}/api/v1/valuations/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        property_type: d.property_type,
        municipality: d.municipality,
        area_sqm: d.area_sqm,
        condition_grade: { excellent: 1, good: 2, fair: 3, poor: 4 }[d.condition] || 2,
        neighborhood_quality: 2,
      }),
    })
    if (res.ok) {
      const json = await res.json()
      aiEstimate.value = {
        value: json.market_value || json.estimated_value,
        confidence: json.confidence || 0.75,
        method: d.valuation_method || 'comparative',
        breakdown: json,
      }
    }
  }

  async function fetchTrustMetrics() {
    const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8020'
    const res = await fetch(`${API_BASE}/api/v1/valuation-feedback/metrics`)
    if (res.ok) trustMetrics.value = await res.json()
  }

  return {
    currentStep, completedSteps, formData, stepErrors, isSubmitting,
    isDraft, aiEstimate, trustMetrics, progressPercent, canProceed,
    validateStep, nextStep, prevStep, goToStep,
    saveDraft, loadDraft, clearWizard,
    calculateAIValuation, fetchTrustMetrics,
  }
})
```

**Step 2:** Commit:
```bash
git add frontend/app/stores/propertyWizard.ts
git commit -m "feat(store): add usePropertyWizardStore with 7-step state management"
```

---

## Task 8: Frontend — WizardStepIndicator Component

**Files:**
- Create: `frontend/app/components/property/wizard/WizardStepIndicator.vue`

**Step 1:** Build animated step bubbles + progress bar:

```vue
<template>
  <div class="wizard-indicator">
    <div class="progress-bar-track">
      <div class="progress-bar-fill" :style="{ width: progressPercent + '%' }" />
    </div>
    <div class="steps-row">
      <div
        v-for="step in steps"
        :key="step.number"
        class="step-item"
        :class="{ active: current === step.number, completed: completed.has(step.number), clickable: completed.has(step.number) }"
        @click="completed.has(step.number) && emit('go-to', step.number)"
      >
        <div class="bubble">
          <i v-if="completed.has(step.number) && current !== step.number" class="pi pi-check" />
          <span v-else>{{ step.number }}</span>
        </div>
        <span class="label">{{ step.label }}</span>
      </div>
    </div>
    <p class="progress-text">{{ progressPercent }}% complete</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  current: number
  completed: Set<number>
  progressPercent: number
}>()

const emit = defineEmits<{ (e: 'go-to', step: number): void }>()

const steps = [
  { number: 1, label: 'Basic Info' },
  { number: 2, label: 'Location' },
  { number: 3, label: 'Physical' },
  { number: 4, label: 'Amenities' },
  { number: 5, label: 'Valuation' },
  { number: 6, label: 'Ownership' },
  { number: 7, label: 'Review' },
]
</script>
```

**Step 2:** Add scoped styles with green brand color (#059669), transition animations on bubble state changes, responsive wrapping for mobile.

**Step 3:** Commit:
```bash
git add frontend/app/components/property/wizard/WizardStepIndicator.vue
git commit -m "feat(ui): add WizardStepIndicator with progress bar and animated step bubbles"
```

---

## Task 9: Frontend — Step 1: Basic Info

**Files:**
- Create: `frontend/app/components/property/wizard/WizardStep1BasicInfo.vue`

**Step 1:** Build the step with all basic info fields using PrimeVue components. Include Ethiopian regions dropdown, property type + subtype with dynamic subtype options based on type selection. Auto-generate `property_ref` when address + municipality are filled.

Key fields: Property type, subtype, address, region, municipality, subcity, woreda, kebele, zone, neighborhood, parcel number, title deed number, registration date.

Use `v-model` binding into the wizard store's `formData`. Show `stepErrors[1]` inline. Layout: 2-column grid, full-width for address.

**Step 2:** Commit:
```bash
git add frontend/app/components/property/wizard/WizardStep1BasicInfo.vue
git commit -m "feat(wizard): add Step 1 - Basic Property Information"
```

---

## Task 10: Frontend — Step 2: Location & Map

**Files:**
- Create: `frontend/app/components/property/wizard/WizardStep2Location.vue`

**Step 1:** Wrap `PropertyMapEditor.vue` with address geocoding. When address changes (from step 1), call Nominatim API to auto-center the map. On map click, capture lat/lng into store. Show coordinates in read-only inputs below map. Show neighborhood info panel if lat/lng are set.

**Step 2:** Commit:
```bash
git add frontend/app/components/property/wizard/WizardStep2Location.vue
git commit -m "feat(wizard): add Step 2 - Location and Interactive Map"
```

---

## Task 11: Frontend — Step 3: Physical Details

**Files:**
- Create: `frontend/app/components/property/wizard/WizardStep3Physical.vue`

**Step 1:** Build with all physical fields: land area (m²), building area (m²), floors, rooms, bedrooms, bathrooms, year built, construction material dropdown, roof material dropdown, floor material dropdown, construction quality dropdown, condition dropdown, parking spaces. Show building age computed from year_built. Validate area_sqm > 0 and condition required.

**Step 2:** Commit:
```bash
git add frontend/app/components/property/wizard/WizardStep3Physical.vue
git commit -m "feat(wizard): add Step 3 - Physical Characteristics"
```

---

## Task 12: Frontend — Step 4: Amenities & Utilities

**Files:**
- Create: `frontend/app/components/property/wizard/WizardStep4Amenities.vue`

**Step 1:** Build a visual checkbox grid. Two sections:

- **Amenities** (with icons): Elevator (pi-arrow-up), Security guard (pi-shield), Generator (pi-bolt), Water tank (pi-tint), Solar panels (pi-sun), CCTV (pi-video), Gym (pi-heart), Swimming pool (pi-circle), Garden (pi-tree), Fence (pi-lock)
- **Utilities**: Electricity, Water supply, Internet, Sewage, Gas

Store as `amenities: { elevator: true, security: false, ... }` and `utilities: { electricity: true, ... }`.

Add a textarea for additional features.

**Step 2:** Commit:
```bash
git add frontend/app/components/property/wizard/WizardStep4Amenities.vue
git commit -m "feat(wizard): add Step 4 - Amenities and Utilities checklist"
```

---

## Task 13: Frontend — Step 5: Valuation + AI Trust Badge

**Files:**
- Create: `frontend/app/components/property/wizard/WizardStep5Valuation.vue`
- Create: `frontend/app/components/property/ValuationTrustBadge.vue`

**Step 1:** Build `ValuationTrustBadge.vue` — reusable badge showing trust score with color coding:
- ≥80%: green badge "High Confidence"
- 60–79%: amber badge "Moderate Confidence"
- <60%: red badge "Low Confidence"
Includes tooltip explaining "Based on N reviewer approvals"

**Step 2:** Build `WizardStep5Valuation.vue`:
- Valuation method selector (Comparative/Cost/Income) with description cards
- Land value + Building value inputs → auto-sum to total market value
- "Calculate AI Estimate" button → calls `store.calculateAIValuation()` → shows animated result card
- AI result card shows: estimated value, confidence bar, `ValuationTrustBadge`, breakdown table
- Valuation date, valuer name, license number, phone
- Comparable properties: add/remove rows with address + value columns
- Valuation notes textarea

**Step 3:** Commit:
```bash
git add frontend/app/components/property/wizard/WizardStep5Valuation.vue frontend/app/components/property/ValuationTrustBadge.vue
git commit -m "feat(wizard): add Step 5 - Valuation with AI estimate and trust badge"
```

---

## Task 14: Frontend — Step 6: Ownership

**Files:**
- Create: `frontend/app/components/property/wizard/WizardStep6Ownership.vue`

**Step 1:** Fields: owner name, phone (Ethiopian format +251), email, ID type dropdown (National ID/Passport/Kebele ID), ID number, ownership type dropdown, legal description textarea. Phone validation for Ethiopian format.

**Step 2:** Commit:
```bash
git add frontend/app/components/property/wizard/WizardStep6Ownership.vue
git commit -m "feat(wizard): add Step 6 - Ownership Information"
```

---

## Task 15: Frontend — Step 7: Documents & Photos

**Files:**
- Create: `frontend/app/components/property/wizard/WizardStep7Documents.vue`

**Step 1:** Two upload zones using PrimeVue FileUpload:

**Photos section** (accept: `image/*`, max 5MB each, up to 20):
- Drag & drop zone with preview grid
- Thumbnail previews with remove button

**Documents section** (accept: `.pdf,.doc,.docx`, max 10MB, up to 10):
- Required documents checklist (Title Deed, Tax Clearance, Survey Plan — mark checked when uploaded)
- File list with type icon, name, size, remove button

Store files in `formData.photos` and `formData.documents` arrays.

**Step 2:** Commit:
```bash
git add frontend/app/components/property/wizard/WizardStep7Documents.vue
git commit -m "feat(wizard): add Step 7 - Documents and Photos upload"
```

---

## Task 16: Frontend — Review & Submit (Step 7 wrapper)

**Files:**
- Create: `frontend/app/components/property/wizard/WizardReviewSummary.vue`

**Step 1:** Build summary page showing all 6 steps data as cards:
- Each card has section title, key data grid, and pencil "Edit" button
- Edit button calls `store.goToStep(n)` to jump back
- Show total amenity count, utility count, AI estimate (if calculated), trust badge
- "Save as Draft" and "Submit Property" buttons at bottom
- On submit: show confirmation dialog → call submit API → show success with property_ref

**Step 2:** Commit:
```bash
git add frontend/app/components/property/wizard/WizardReviewSummary.vue
git commit -m "feat(wizard): add Review & Submit summary page"
```

---

## Task 17: Frontend — PropertyWizard Orchestrator

**Files:**
- Create: `frontend/app/components/property/PropertyWizard.vue`

**Step 1:** Build the shell component:

```vue
<template>
  <div class="property-wizard">
    <WizardStepIndicator
      :current="store.currentStep"
      :completed="store.completedSteps"
      :progress-percent="store.progressPercent"
      @go-to="store.goToStep"
    />

    <div class="wizard-body">
      <!-- Side summary panel (desktop only) -->
      <aside class="wizard-sidebar" v-if="store.currentStep < 7">
        <WizardSidePanel :form-data="store.formData" :current-step="store.currentStep" />
      </aside>

      <!-- Active step -->
      <main class="wizard-main">
        <Transition name="slide-fade" mode="out-in">
          <component :is="currentStepComponent" :key="store.currentStep" />
        </Transition>

        <!-- Navigation bar -->
        <div class="wizard-nav">
          <Button label="Cancel" severity="secondary" @click="handleCancel" :disabled="store.isSubmitting" />
          <Button label="Save Draft" severity="info" icon="pi pi-save" @click="store.saveDraft()" :disabled="store.isSubmitting" />
          <div class="spacer" />
          <Button v-if="store.currentStep > 1" label="Previous" icon="pi pi-arrow-left" severity="secondary" @click="store.prevStep()" />
          <Button v-if="store.currentStep < 7" label="Next" icon="pi pi-arrow-right" icon-pos="right" @click="store.nextStep()" />
        </div>
      </main>
    </div>
  </div>
</template>
```

Map `currentStep` → component using `computed` with a lookup object.
Add `slide-fade` CSS transition (translate X + opacity).
Auto-save draft every 30s with `setInterval` in `onMounted`.

**Step 2:** Commit:
```bash
git add frontend/app/components/property/PropertyWizard.vue
git commit -m "feat(wizard): add PropertyWizard orchestrator shell with transitions"
```

---

## Task 18: Frontend — Refactor create.vue + edit/[id].vue

**Files:**
- Modify: `frontend/app/pages/properties/create.vue`
- Modify: `frontend/app/pages/properties/edit/[id].vue`

**Step 1:** Replace `create.vue` to use `PropertyWizard` directly. Load draft on mount. Remove old step indicators and `PropertyForm` usage.

**Step 2:** Update `edit/[id].vue` to load existing property data into wizard store on mount, then render `PropertyWizard` in edit mode.

**Step 3:** Commit:
```bash
git add frontend/app/pages/properties/create.vue frontend/app/pages/properties/edit/[id].vue
git commit -m "refactor(pages): replace PropertyForm with PropertyWizard in create/edit pages"
```

---

## Task 19: Frontend — Reviewer Feedback UI

**Files:**
- Create: `frontend/app/components/property/ValuationReviewPanel.vue`
- Modify: `frontend/app/pages/properties/[id].vue`

**Step 1:** Build `ValuationReviewPanel.vue` — shown on the property detail page for reviewers:
- Shows AI estimated value prominently with trust badge
- "Approve Valuation" button (no change needed)
- "Modify & Approve" section: input for final value + comments textarea
- On submit: POST to `/api/v1/valuation-feedback`
- Shows confirmation with new trust score

**Step 2:** Add the panel to `[id].vue` detail page (conditionally shown for reviewer roles).

**Step 3:** Commit:
```bash
git add frontend/app/components/property/ValuationReviewPanel.vue frontend/app/pages/properties/[id].vue
git commit -m "feat(ui): add ValuationReviewPanel for reviewer feedback loop"
```

---

## Task 20: Final — Update TypeScript Types

**Files:**
- Modify: `frontend/app/types/index.ts`

**Step 1:** Extend `Property` and `PropertyCreate` interfaces to match all new backend fields. Add `ValuationFeedback` and `TrustMetrics` interfaces.

**Step 2:** Commit:
```bash
git add frontend/app/types/index.ts
git commit -m "feat(types): extend Property types with all wizard fields and feedback types"
```

---

## Task 21: Commit Design Doc

```bash
git add docs/plans/2026-03-05-property-wizard.md
git commit -m "docs: add property wizard implementation plan"
```
