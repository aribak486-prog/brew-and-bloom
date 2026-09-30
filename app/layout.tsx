import type { Metadata } from 'next'
import Chatbot from '@/components/Chatbot'
import './globals.css'

export const metadata: Metadata = { title: 'Brew & Bloom — Coffee, comfort & good vibes', description: 'Freshly brewed coffee, handcrafted treats, and cozy moments made for you.' }

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}<Chatbot /></body></html>
}
