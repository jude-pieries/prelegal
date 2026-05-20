'use client'

import Link from 'next/link'
import { CATALOG } from '@/lib/catalog'

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="h-14 bg-white border-b flex items-center px-6">
        <span className="text-xs font-semibold tracking-widest uppercase" style={{ color: '#888888' }}>
          PreLegal
        </span>
        <span className="mx-2 text-muted-foreground">/</span>
        <span className="text-sm font-medium" style={{ color: '#032147' }}>
          Document Library
        </span>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-12">
        <div className="mb-10">
          <h1 className="text-3xl font-bold mb-2" style={{ color: '#032147' }}>
            Draft a Legal Agreement
          </h1>
          <p className="text-base" style={{ color: '#888888' }}>
            Choose a document type to get started. Our AI assistant will guide you through the required fields.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {CATALOG.map((entry) => (
            <Link
              key={entry.slug}
              href={`/${entry.slug}/`}
              className="block bg-white rounded-xl border border-slate-200 p-5 hover:border-blue-400 hover:shadow-md transition-all group"
            >
              <div
                className="text-xs font-semibold uppercase tracking-widest mb-1"
                style={{ color: '#209dd7' }}
              >
                Legal Agreement
              </div>
              <h2
                className="text-sm font-semibold mb-2 group-hover:underline"
                style={{ color: '#032147' }}
              >
                {entry.name}
              </h2>
              <p className="text-xs leading-relaxed line-clamp-3" style={{ color: '#888888' }}>
                {entry.description}
              </p>
            </Link>
          ))}
        </div>
      </main>
    </div>
  )
}
