/**
 * Frontend performance monitoring utilities
 */

/**
 * Measure and log component render time
 */
export function measureRenderTime(componentName: string, callback: () => void) {
  const startTime = performance.now();
  callback();
  const endTime = performance.now();
  const duration = endTime - startTime;
  
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Performance] ${componentName} rendered in ${duration.toFixed(2)}ms`);
  }
  
  return duration;
}

/**
 * Report Web Vitals to analytics
 */
export function reportWebVitals(metric: any) {
  if (process.env.NODE_ENV === 'development') {
    console.log('[Web Vitals]', metric);
  }
  
  // In production, send to analytics service
  // Example: sendToAnalytics(metric)
}

/**
 * Measure API call performance
 */
export async function measureApiCall<T>(
  name: string,
  apiCall: () => Promise<T>
): Promise<T> {
  const startTime = performance.now();
  
  try {
    const result = await apiCall();
    const duration = performance.now() - startTime;
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API] ${name} completed in ${duration.toFixed(2)}ms`);
    }
    
    // Track slow API calls
    if (duration > 1000) {
      console.warn(`[API] Slow API call detected: ${name} took ${duration.toFixed(2)}ms`);
    }
    
    return result;
  } catch (error) {
    const duration = performance.now() - startTime;
    console.error(`[API] ${name} failed after ${duration.toFixed(2)}ms`, error);
    throw error;
  }
}

/**
 * Debounce function for performance optimization
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };
    
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle function for performance optimization
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Lazy load images with Intersection Observer
 */
export function lazyLoadImage(
  img: HTMLImageElement,
  src: string,
  options?: IntersectionObserverInit
) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        img.src = src;
        observer.unobserve(img);
      }
    });
  }, options);
  
  observer.observe(img);
  
  return () => observer.disconnect();
}

/**
 * Prefetch data for better UX
 */
export function prefetchData(url: string) {
  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = url;
  document.head.appendChild(link);
}

/**
 * Check if user prefers reduced motion
 */
export function prefersReducedMotion(): boolean {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Get connection speed information
 */
export function getConnectionSpeed(): string {
  const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
  
  if (!connection) {
    return 'unknown';
  }
  
  return connection.effectiveType || 'unknown';
}

/**
 * Check if device is low-end
 */
export function isLowEndDevice(): boolean {
  const connection = getConnectionSpeed();
  const memory = (performance as any).memory;
  
  // Consider device low-end if:
  // - Connection is slow (2g or slow-2g)
  // - Device has less than 4GB RAM
  const isSlowConnection = connection === '2g' || connection === 'slow-2g';
  const isLowMemory = memory && memory.jsHeapSizeLimit < 4 * 1024 * 1024 * 1024;
  
  return isSlowConnection || isLowMemory;
}

/**
 * Performance observer for monitoring
 */
export class PerformanceMonitor {
  private metrics: Map<string, number[]> = new Map();
  
  record(name: string, value: number) {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    this.metrics.get(name)!.push(value);
  }
  
  getAverage(name: string): number {
    const values = this.metrics.get(name);
    if (!values || values.length === 0) return 0;
    
    const sum = values.reduce((a, b) => a + b, 0);
    return sum / values.length;
  }
  
  getPercentile(name: string, percentile: number): number {
    const values = this.metrics.get(name);
    if (!values || values.length === 0) return 0;
    
    const sorted = [...values].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[index];
  }
  
  clear(name?: string) {
    if (name) {
      this.metrics.delete(name);
    } else {
      this.metrics.clear();
    }
  }
  
  getSummary() {
    const summary: Record<string, any> = {};
    
    this.metrics.forEach((values, name) => {
      summary[name] = {
        count: values.length,
        average: this.getAverage(name),
        p95: this.getPercentile(name, 95),
        p99: this.getPercentile(name, 99),
      };
    });
    
    return summary;
  }
}

// Global performance monitor instance
export const performanceMonitor = new PerformanceMonitor();
