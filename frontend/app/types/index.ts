// Core Types for ValuAdis Application

export interface User {
  id: number
  email: string
  full_name: string
  phone: string
  role: 'valuer' | 'reviewer' | 'firm_admin' | 'municipal_admin' | 'system_admin'
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  full_name: string
  phone: string
}

export interface Property {
  id: number
  user_id: number
  property_ref?: string
  // Address
  address: string
  municipality: string
  region?: string
  subcity?: string
  woreda?: string
  kebele?: string
  zone?: string
  neighborhood?: string
  // Type & classification
  property_type: 'residential' | 'commercial' | 'agricultural' | 'industrial' | 'mixed_use' | 'special_purpose'
  property_subtype?: string
  // Land/legal
  parcel_number?: string
  title_deed_number?: string
  registration_date?: string
  // Location
  latitude?: number
  longitude?: number
  boundaries: [number, number][]
  coordinates: number[][]
  boundary?: any
  // Physical
  area_sqm: number
  building_area_sqm?: number
  number_of_floors?: number
  number_of_bedrooms?: number
  number_of_bathrooms?: number
  number_of_rooms?: number
  garage_capacity?: number
  year_built?: number
  condition: 'excellent' | 'good' | 'fair' | 'poor' | 'dilapidated' | ''
  construction_material?: string
  roof_type?: string
  floor_type?: string
  // Amenities & utilities
  amenities: Record<string, boolean>
  utilities: Record<string, boolean>
  // Valuation
  market_value?: number
  land_value?: number
  building_value?: number
  valuation_method?: string
  valuation_date?: string
  valuer_name?: string
  valuer_license?: string
  valuer_phone?: string
  comparable_properties?: ComparableProperty[]
  valuation_notes?: string
  ai_estimated_value?: number
  ai_confidence_score?: number
  ai_trust_score_at_time?: number
  // Ownership
  owner_name?: string
  owner_phone?: string
  owner_email?: string
  owner_id_type?: string
  owner_id_number?: string
  ownership_type?: string
  legal_description?: string
  // Documents
  photos: string[]
  documents: string[]
  // Status
  status: string
  created_at: string
  updated_at: string
}

export interface ComparableProperty {
  address: string
  sale_price: number
  sale_date: string
  area_sqm: number
  notes?: string
}

export interface PropertyCreate {
  address: string
  municipality: string
  region: string
  property_type: string
  area_sqm: number
  condition: string
  [key: string]: any
}

export interface ValuationFeedback {
  id: number
  property_id: number
  reviewer_id: number
  ai_estimate: number
  final_value: number
  approved_without_change: boolean
  delta_percentage: number
  comments?: string
  created_at: string
}

export interface TrustMetrics {
  trust_score: number
  total_reviews: number
  avg_error_pct: number
  approved_unchanged: number
  modified_reviews: number
}

export interface FeedbackSubmitResult {
  success: boolean
  feedback_id: number
  trust_score: number
  delta_percentage: number
  approved: boolean
}

export interface Valuation {
  id: number
  property_id: number
  user_id: number
  market_value: number
  taxable_value: number
  base_rate: number
  type_multiplier: number
  condition_grade: number
  neighborhood_quality: number
  valuation_date: string
  is_proclamation_compliant: boolean
  created_at: string
  updated_at: string
  property?: Property
}

export interface ValuationCalculate {
  property_id?: number
  property_type: string
  municipality: string
  area_sqm: number
  condition_grade: number
  neighborhood_quality: number
}

export interface ValuationCreate {
  property_id: number
  market_value: number
  taxable_value: number
  base_rate: number
  type_multiplier: number
  condition_grade: number
  neighborhood_quality: number
}

export interface AnalyticsDashboard {
  total_properties: number
  total_valuations: number
  total_value: number
  average_value: number
  recent_properties: Property[]
  recent_valuations: Valuation[]
}

export interface PropertyTypeDistribution {
  property_type: string
  count: number
  percentage: number
}

export interface MunicipalityDistribution {
  municipality: string
  count: number
  total_value: number
}

export interface MarketTrend {
  date: string
  average_value: number
  count: number
}

export interface AuditReport {
  system_health: string
  compliance_status: string
  total_properties: number
  total_valuations: number
  proclamation_compliant: number
  non_compliant: number
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  success: boolean
  data: T[]
  pagination: {
    page: number
    per_page: number
    total: number
    pages: number
  }
}

export interface ApiError {
  success: false
  message: string
  errors?: Record<string, string[]>
}

// Ethiopian-specific types
export type EthiopianMunicipality = 
  | 'Addis Ababa'
  | 'Bahir Dar'
  | 'Mekelle'
  | 'Hawassa'
  | 'Dire Dawa'
  | 'Gondar'
  | 'Jimma'
  | 'Adama'

export type PropertyType = 'residential' | 'commercial' | 'agricultural'

export type ConditionGrade = 1 | 2 | 3 | 4 // 1=Excellent, 2=Good, 3=Fair, 4=Poor

export type NeighborhoodQuality = 1 | 2 | 3 // 1=Premium, 2=Standard, 3=Developing

export interface EthiopianPhoneNumber {
  countryCode: '+251'
  number: string // 9xxxxxxxx format
}

export interface ComplianceStatus {
  is_compliant: boolean
  proclamation: 'Proclamation 1365/2025'
  taxable_percentage: 25
  notes?: string
}
