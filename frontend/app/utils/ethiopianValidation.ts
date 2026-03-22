/**
 * Ethiopian Business License Validation Utility
 *
 * Validates Ethiopian business license numbers according to standard formats:
 * - Format: XXX-NNNNNNNNNN (prefix letters, hyphen, numbers)
 * - Prefix: 2-4 letters indicating license type/region
 * - Numbers: 6-10 digits
 * - Total length: 9-20 characters
 */

export interface LicenseValidationResult {
  valid: boolean
  error?: string
}

/**
 * Validates an Ethiopian business license number
 * @param license - The license string to validate
 * @returns LicenseValidationResult with valid status and optional error message
 */
export function validateEthiopianLicense(license: string): LicenseValidationResult {
  // Check if license is provided
  if (!license || typeof license !== 'string') {
    return {
      valid: false,
      error: 'License number is required'
    }
  }

  // Trim whitespace
  const trimmed = license.trim()

  // Check length
  if (trimmed.length < 9) {
    return {
      valid: false,
      error: 'License number must be at least 9 characters'
    }
  }

  if (trimmed.length > 20) {
    return {
      valid: false,
      error: 'License number must not exceed 20 characters'
    }
  }

  // Ethiopian license format: XXX-NNNNNNNNNN
  // - 2-4 uppercase letters (prefix)
  // - hyphen separator
  // - 6-10 digits
  const ethiopianLicenseRegex = /^[A-Z]{2,4}-\d{6,10}$/

  if (!ethiopianLicenseRegex.test(trimmed)) {
    return {
      valid: false,
      error: 'Invalid Ethiopian license format. Expected format: XXX-NNNNNNNNNN (e.g., AA-1234567890)'
    }
  }

  return {
    valid: true
  }
}

/**
 * Formats a license number to standard Ethiopian format
 * @param license - The license string to format
 * @returns Formatted license string or null if invalid
 */
export function formatEthiopianLicense(license: string): string | null {
  if (!license || typeof license !== 'string') {
    return null
  }

  // Remove all non-alphanumeric characters
  const cleaned = license.replace(/[^a-zA-Z0-9]/g, '').toUpperCase()

  // Separate letters and numbers
  const letterMatch = cleaned.match(/^[A-Z]+/)
  const numberMatch = cleaned.match(/\d+$/)

  if (!letterMatch || !numberMatch) {
    return null
  }

  const letters = letterMatch[0]
  const numbers = numberMatch[0]

  // Validate parts
  if (letters.length < 2 || letters.length > 4) {
    return null
  }

  if (numbers.length < 6 || numbers.length > 10) {
    return null
  }

  return `${letters}-${numbers}`
}

/**
 * Sanitizes a license input for display/storage
 * @param license - The license string to sanitize
 * @returns Sanitized license string
 */
export function sanitizeLicenseInput(license: string): string {
  if (!license || typeof license !== 'string') {
    return ''
  }

  return license.trim().toUpperCase()
}

/**
 * Extracts license components (prefix and number)
 * @param license - The license string to parse
 * @returns Object with prefix and number, or null if invalid
 */
export function extractLicenseComponents(license: string): { prefix: string; number: string } | null {
  const validation = validateEthiopianLicense(license)

  if (!validation.valid) {
    return null
  }

  const parts = license.trim().toUpperCase().split('-')

  if (parts.length !== 2) {
    return null
  }

  return {
    prefix: parts[0],
    number: parts[1]
  }
}

/**
 * Common Ethiopian license prefixes and their meanings
 */
export const ETHIOPIAN_LICENSE_PREFIXES = {
  'AA': 'Addis Ababa City Administration',
  'AD': 'Adama City Administration',
  'BA': 'Bahir Dar City Administration',
  'DD': 'Dire Dawa City Administration',
  'HA': 'Hawassa City Administration',
  'ME': 'Mekelle City Administration',
  'GO': 'Gondar City Administration',
  'JI': 'Jimma City Administration',
  'DE': 'Dessie City Administration',
  'TR': 'Tigray Regional State',
  'AM': 'Amhara Regional State',
  'OR': 'Oromia Regional State',
  'SN': 'Southern Nations, Nationalities, and Peoples Regional State',
  'AF': 'Afar Regional State',
  'SO': 'Somali Regional State',
  'BE': 'Benishangul-Gumuz Regional State',
  'GA': 'Gambela Regional State',
  'HA': 'Harari Regional State',
  'SI': 'Sidama Regional State',
  'SW': 'South West Ethiopia Peoples Regional State'
} as const

/**
 * Gets the region/authority name for a license prefix
 * @param prefix - The 2-4 letter prefix
 * @returns Region name or 'Unknown Region' if not recognized
 */
export function getLicenseRegion(prefix: string): string {
  const upperPrefix = prefix.toUpperCase()
  return ETHIOPIAN_LICENSE_PREFIXES[upperPrefix as keyof typeof ETHIOPIAN_LICENSE_PREFIXES] || 'Unknown Region'
}

/**
 * Validates if a license prefix is recognized
 * @param prefix - The prefix to check
 * @returns Boolean indicating if prefix is recognized
 */
export function isRecognizedPrefix(prefix: string): boolean {
  const upperPrefix = prefix.toUpperCase()
  return upperPrefix in ETHIOPIAN_LICENSE_PREFIXES
}
