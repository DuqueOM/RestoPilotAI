/**
 * Utility functions for MenuPilot frontend
 */

import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind CSS classes with clsx
 * Handles conflicts and deduplication
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format currency with locale support
 */
export function formatCurrency(
  amount: number,
  currency: string = 'USD',
  locale: string = 'en-US'
): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(amount)
}

/**
 * Format percentage
 */
export function formatPercent(value: number, decimals: number = 1): string {
  return `${(value * 100).toFixed(decimals)}%`
}

/**
 * Format date for display
 */
export function formatDate(
  date: string | Date,
  options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }
): string {
  return new Date(date).toLocaleDateString('en-US', options)
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return `${text.slice(0, maxLength - 3)}...`
}

/**
 * Delay utility for async operations
 */
export function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Get BCG category color
 */
export function getBCGColor(category: string): string {
  const colors: Record<string, string> = {
    STAR: '#f59e0b',        // amber
    star: '#f59e0b',
    CASH_COW: '#22c55e',    // green
    cash_cow: '#22c55e',
    QUESTION_MARK: '#3b82f6', // blue
    question_mark: '#3b82f6',
    DOG: '#ef4444',         // red
    dog: '#ef4444',
  }
  return colors[category] || '#6b7280'
}

/**
 * Get BCG category label
 */
export function getBCGLabel(category: string): string {
  const labels: Record<string, string> = {
    STAR: 'Star ⭐',
    star: 'Star ⭐',
    CASH_COW: 'Cash Cow 🐄',
    cash_cow: 'Cash Cow 🐄',
    QUESTION_MARK: 'Question Mark ❓',
    question_mark: 'Question Mark ❓',
    DOG: 'Dog 🐕',
    dog: 'Dog 🐕',
  }
  return labels[category] || category
}

/**
 * Generate a unique ID
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}
