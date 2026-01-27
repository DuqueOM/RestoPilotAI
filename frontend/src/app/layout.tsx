import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'MenuPilot - AI Restaurant Optimization',
  description: 'AI-powered menu optimization, BCG analysis, and campaign generation for restaurants',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">{children}</body>
    </html>
  )
}
