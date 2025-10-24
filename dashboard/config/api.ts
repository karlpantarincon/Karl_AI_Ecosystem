/**
 * API Configuration for Karl AI Dashboard
 */

export const API_CONFIG = {
  // Base URL for the API
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  
  // Refresh intervals (in milliseconds)
  REFRESH_INTERVALS: {
    METRICS: parseInt(process.env.NEXT_PUBLIC_METRICS_REFRESH_INTERVAL || '30000'),
    TASKS: parseInt(process.env.NEXT_PUBLIC_TASKS_REFRESH_INTERVAL || '30000'),
    AGENTS: parseInt(process.env.NEXT_PUBLIC_AGENTS_REFRESH_INTERVAL || '30000'),
    LOGS: parseInt(process.env.NEXT_PUBLIC_LOGS_REFRESH_INTERVAL || '30000'),
  },
  
  // Feature flags
  FEATURES: {
    REAL_TIME: process.env.NEXT_PUBLIC_ENABLE_REAL_TIME === 'true',
    NOTIFICATIONS: process.env.NEXT_PUBLIC_ENABLE_NOTIFICATIONS === 'true',
    DARK_MODE: process.env.NEXT_PUBLIC_ENABLE_DARK_MODE === 'true',
  },
  
  // Dashboard configuration
  DASHBOARD: {
    TITLE: process.env.NEXT_PUBLIC_DASHBOARD_TITLE || 'Karl AI Ecosystem',
    VERSION: process.env.NEXT_PUBLIC_DASHBOARD_VERSION || '1.0.0',
  },
  
  // Request configuration
  REQUEST: {
    TIMEOUT: 10000, // 10 seconds
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000, // 1 second
  }
}

// Environment detection
export const isDevelopment = process.env.NODE_ENV === 'development'
export const isProduction = process.env.NODE_ENV === 'production'

// API URL helper
export const getApiUrl = (): string => {
  if (typeof window !== 'undefined') {
    // Client-side: use environment variable or default
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }
  
  // Server-side: use environment variable or default
  return process.env.API_URL || 'http://localhost:8000'
}

// Feature flag helpers
export const isFeatureEnabled = (feature: keyof typeof API_CONFIG.FEATURES): boolean => {
  return API_CONFIG.FEATURES[feature]
}
