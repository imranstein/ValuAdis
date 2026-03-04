// Core Types for ValuAdis Application

export interface User {
  id: number
  email: string
  full_name: string
  phone: string
  role: 'valuer' | 'firm_admin' | 'municipal_admin' | 'system_admin'
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
  address: string
  municipality: string
  property_type: 'residential' | 'commercial' | 'agricultural'
  area_sqm: number
  coordinates: number[][]
  boundary?: any
  status: string
  created_at: string
  updated_at: string
}

export interface PropertyCreate {
  address: string
  municipality: string
  property_type: 'residential' | 'commercial' | 'agricultural'
  coordinates: number[][]
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
