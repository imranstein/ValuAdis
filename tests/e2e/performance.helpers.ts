import { Page } from '@playwright/test'

export interface PerformanceMetrics {
  name: string
  pageLoadTime: number
  apiResponseTime: number
  testDuration: number
  timestamp: string
}

export interface PerformanceReport {
  generatedAt: string
  baselines: Record<string, PerformanceMetrics>
  summary: {
    avgPageLoadTime: number
    avgApiResponseTime: number
    totalTests: number
  }
}

export class PerformanceTracker {
  private metrics: PerformanceMetrics[] = []
  private startTime: number = 0

  /**
   * Start tracking a test performance
   */
  startTest(): void {
    this.startTime = Date.now()
  }

  /**
   * Measure page load time
   */
  async measurePageLoad(page: Page, url: string): Promise<number> {
    const navigationStart = await page.evaluate(() => window.performance.timing.navigationStart)
    const loadEventEnd = await page.evaluate(() => window.performance.timing.loadEventEnd)
    return loadEventEnd - navigationStart
  }

  /**
   * Measure API response time by intercepting requests
   */
  async measureApiResponse(page: Page, urlPattern: string): Promise<number> {
    let responseTime = 0

    page.on('response', (response) => {
      if (response.url().includes(urlPattern)) {
        responseTime = response.timing().responseEnd - response.timing().requestStart
      }
    })

    return responseTime
  }

  /**
   * Record metrics for a test
   */
  recordMetric(
    name: string,
    pageLoadTime: number,
    apiResponseTime: number,
  ): PerformanceMetrics {
    const metric: PerformanceMetrics = {
      name,
      pageLoadTime,
      apiResponseTime,
      testDuration: Date.now() - this.startTime,
      timestamp: new Date().toISOString(),
    }

    this.metrics.push(metric)
    return metric
  }

  /**
   * Get all recorded metrics
   */
  getMetrics(): PerformanceMetrics[] {
    return this.metrics
  }

  /**
   * Generate performance report with baselines
   */
  generateReport(): PerformanceReport {
    const avgPageLoadTime =
      this.metrics.reduce((sum, m) => sum + m.pageLoadTime, 0) / this.metrics.length || 0
    const avgApiResponseTime =
      this.metrics.reduce((sum, m) => sum + m.apiResponseTime, 0) / this.metrics.length || 0

    const baselines: Record<string, PerformanceMetrics> = {}
    this.metrics.forEach((metric) => {
      baselines[metric.name] = metric
    })

    return {
      generatedAt: new Date().toISOString(),
      baselines,
      summary: {
        avgPageLoadTime,
        avgApiResponseTime,
        totalTests: this.metrics.length,
      },
    }
  }

  /**
   * Log metrics to console
   */
  logMetrics(): void {
    console.log('\n📊 PERFORMANCE METRICS\n')
    this.metrics.forEach((metric) => {
      console.log(`✓ ${metric.name}`)
      console.log(`  Page Load: ${metric.pageLoadTime}ms`)
      console.log(`  API Response: ${metric.apiResponseTime}ms`)
      console.log(`  Test Duration: ${metric.testDuration}ms\n`)
    })

    const report = this.generateReport()
    console.log('📈 SUMMARY')
    console.log(`  Avg Page Load: ${report.summary.avgPageLoadTime.toFixed(2)}ms`)
    console.log(`  Avg API Response: ${report.summary.avgApiResponseTime.toFixed(2)}ms`)
    console.log(`  Total Tests: ${report.summary.totalTests}\n`)
  }

  /**
   * Check if metrics meet baseline (regression detection)
   */
  checkRegressions(threshold: number = 1.1): string[] {
    const regressions: string[] = []

    // Example baseline: page load should be < 3000ms, API response < 500ms
    this.metrics.forEach((metric) => {
      if (metric.pageLoadTime > 3000 * threshold) {
        regressions.push(
          `${metric.name}: Page load time ${metric.pageLoadTime}ms exceeds threshold`,
        )
      }
      if (metric.apiResponseTime > 500 * threshold) {
        regressions.push(
          `${metric.name}: API response time ${metric.apiResponseTime}ms exceeds threshold`,
        )
      }
    })

    return regressions
  }
}

export const performanceTracker = new PerformanceTracker()
