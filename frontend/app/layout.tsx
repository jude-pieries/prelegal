import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
<<<<<<< feature/kan-5-all-document-types
  title: 'PreLegal | Legal Document Drafting',
  description: 'AI-assisted legal document drafting',
=======
  title: 'Mutual NDA Creator | PreLegal',
  description: 'Generate a Mutual Non-Disclosure Agreement',
>>>>>>> main
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
