import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'RestoPilotAI - AI Restaurant Optimization',
  description: 'AI-powered menu optimization, BCG analysis, and campaign generation for restaurants powered by Google Gemini 3',
  keywords: ['restaurant', 'menu optimization', 'AI', 'BCG analysis', 'Gemini', 'marketing campaigns'],
  authors: [{ name: 'RestoPilotAI Team' }],
  icons: {
    icon: '/favicon.ico',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#ec751d',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className={`${inter.className} min-h-screen bg-gray-50 antialiased`}>
        {children}
      </body>
    </html>
  )
}
