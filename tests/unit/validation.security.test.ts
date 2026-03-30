/**
 * Security Unit Tests: Input Validation
 * Covers OWASP Top 10: A03 Injection, A07 Authentication Failures
 * Tests XSS, SQL Injection, and password strength validation patterns
 * mirroring backend Pydantic schema constraints.
 */

// ─── Validation Utilities (mirrors backend schema rules) ─────────────────────

/**
 * XSS sanitization: detect HTML tags and dangerous event handlers.
 * In production this runs server-side in Pydantic validators.
 */
function containsXss(input: string): boolean {
  const xssPatterns = [
    /<script[\s\S]*?>[\s\S]*?<\/script>/gi,
    /on\w+\s*=\s*["'][^"']*["']/gi,
    /<[^>]+>/g,
    /javascript\s*:/gi,
    /data\s*:\s*text\/html/gi,
    /vbscript\s*:/gi,
  ]
  return xssPatterns.some((re) => re.test(input))
}

/**
 * SQL injection detection: flags common injection patterns.
 * Backend uses parameterised queries; this validates input at boundary.
 */
function containsSqlInjection(input: string): boolean {
  const sqlPatterns = [
    /('\s*(or|and)\s*'?\d)/gi,
    /(--|#|\/\*)/g,
    /;\s*(drop|delete|insert|update|select|create|alter|truncate)\s/gi,
    /union\s+(all\s+)?select/gi,
    /'\s*;\s*--/gi,
    /xp_cmdshell/gi,
    /sleep\s*\(\s*\d+\s*\)/gi,
    /benchmark\s*\(/gi,
  ]
  return sqlPatterns.some((re) => re.test(input))
}

/**
 * Password strength validator mirroring backend UserCreate schema rules.
 * Min 8 chars, upper, lower, digit, special char required.
 */
function validatePasswordStrength(password: string): {
  valid: boolean
  errors: string[]
} {
  const errors: string[] = []
  if (password.length < 8) errors.push('Too short (min 8 chars)')
  if (!/[A-Z]/.test(password)) errors.push('Missing uppercase letter')
  if (!/[a-z]/.test(password)) errors.push('Missing lowercase letter')
  if (!/\d/.test(password)) errors.push('Missing digit')
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password))
    errors.push('Missing special character')
  return { valid: errors.length === 0, errors }
}

/**
 * Email format validator.
 */
function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

/**
 * Path traversal detector for file/resource inputs.
 */
function containsPathTraversal(input: string): boolean {
  return /(\.\.[/\\]|[/\\]\.\.)/.test(input)
}

// ─── XSS Tests ───────────────────────────────────────────────────────────────

describe('Input Validation — XSS Prevention', () => {
  const xssVectors = [
    '<script>alert("xss")</script>',
    '<img src=x onerror=alert(1)>',
    '<svg onload=alert(1)>',
    'javascript:alert(document.cookie)',
    '<body onload=alert("xss")>',
    'data:text/html,<script>alert(1)</script>',
  ]

  test.each(xssVectors)('detects XSS vector: %s', (vector) => {
    expect(containsXss(vector)).toBe(true)
  })

  const safeInputs = [
    'Hello, World!',
    'user@example.com',
    'Toyota Camry 2022',
    '123 Main Street',
    'Normal text with numbers 42',
  ]

  test.each(safeInputs)('accepts safe input: %s', (input) => {
    expect(containsXss(input)).toBe(false)
  })

  test('empty string does not trigger XSS detection', () => {
    expect(containsXss('')).toBe(false)
  })
})

// ─── SQL Injection Tests ──────────────────────────────────────────────────────

describe('Input Validation — SQL Injection Prevention', () => {
  const sqlVectors = [
    "' OR '1'='1",
    "admin'--",
    "1; DROP TABLE users--",
    "1 UNION SELECT username, password FROM users",
    "1 AND SLEEP(5)--",
    "1' AND BENCHMARK(1000000,MD5(1))--",
    "' OR 1=1 /*",
  ]

  test.each(sqlVectors)('detects SQL injection vector: %s', (vector) => {
    expect(containsSqlInjection(vector)).toBe(true)
  })

  const safeInputs = [
    'Toyota Camry',
    'New South Wales',
    'user@example.com',
    '2022',
    'VIN12345678',
  ]

  test.each(safeInputs)('accepts safe input for SQL context: %s', (input) => {
    expect(containsSqlInjection(input)).toBe(false)
  })
})

// ─── Password Strength Tests ─────────────────────────────────────────────────

describe('Input Validation — Password Strength', () => {
  test('rejects passwords shorter than 8 characters', () => {
    const { valid, errors } = validatePasswordStrength('Ab1!')
    expect(valid).toBe(false)
    expect(errors).toContain('Too short (min 8 chars)')
  })

  test('rejects passwords with no uppercase letter', () => {
    const { valid } = validatePasswordStrength('abcdef1!')
    expect(valid).toBe(false)
  })

  test('rejects passwords with no lowercase letter', () => {
    const { valid } = validatePasswordStrength('ABCDEF1!')
    expect(valid).toBe(false)
  })

  test('rejects passwords with no digit', () => {
    const { valid } = validatePasswordStrength('Abcdefg!')
    expect(valid).toBe(false)
  })

  test('rejects passwords with no special character', () => {
    const { valid } = validatePasswordStrength('Abcdefg1')
    expect(valid).toBe(false)
  })

  test('accepts a strong password meeting all criteria', () => {
    const { valid, errors } = validatePasswordStrength('SecureP@ss1')
    expect(valid).toBe(true)
    expect(errors).toHaveLength(0)
  })

  test('rejects empty password', () => {
    const { valid } = validatePasswordStrength('')
    expect(valid).toBe(false)
  })

  test('common weak passwords fail strength check', () => {
    const weak = ['password', '12345678', 'qwerty123', 'letmein1']
    weak.forEach((pwd) => {
      const { valid } = validatePasswordStrength(pwd)
      expect(valid).toBe(false)
    })
  })
})

// ─── Email Validation Tests ───────────────────────────────────────────────────

describe('Input Validation — Email Format', () => {
  test('accepts valid email addresses', () => {
    const validEmails = ['user@example.com', 'admin+tag@domain.org', 'test.user@sub.domain.com']
    validEmails.forEach((e) => expect(isValidEmail(e)).toBe(true))
  })

  test('rejects malformed email addresses', () => {
    const invalidEmails = ['notanemail', '@domain.com', 'user@', 'user @domain.com', '']
    invalidEmails.forEach((e) => expect(isValidEmail(e)).toBe(false))
  })
})

// ─── Path Traversal Tests ─────────────────────────────────────────────────────

describe('Input Validation — Path Traversal', () => {
  test('detects directory traversal sequences', () => {
    const vectors = ['../../etc/passwd', '..\\..\\windows\\system32', '/foo/../../../bar']
    vectors.forEach((v) => expect(containsPathTraversal(v)).toBe(true))
  })

  test('accepts normal file name inputs', () => {
    const safe = ['report.pdf', 'vehicle_data.json', 'images/photo.jpg']
    safe.forEach((v) => expect(containsPathTraversal(v)).toBe(false))
  })
})
