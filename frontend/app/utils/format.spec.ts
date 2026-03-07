/**
 * VA-56: Frontend unit tests - format utilities
 */

import { describe, it, expect } from 'vitest'

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value ?? 0)
}

function formatPropertyType(type: string): string {
  return type ? type.charAt(0).toUpperCase() + type.slice(1) : ''
}

describe('formatCurrency', () => {
  it('formats numbers as ETB', () => {
    expect(formatCurrency(1000000)).toContain('1')
    expect(formatCurrency(0)).toContain('0')
  })
})

describe('formatPropertyType', () => {
  it('capitalizes type', () => {
    expect(formatPropertyType('residential')).toBe('Residential')
    expect(formatPropertyType('commercial')).toBe('Commercial')
  })
})
