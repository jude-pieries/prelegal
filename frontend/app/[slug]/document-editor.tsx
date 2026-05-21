'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getCatalogEntry } from '@/lib/catalog'
import { ChatInterface } from '@/components/chat-interface'
import { MndaPreview } from '@/components/mnda-preview'
import { DocumentPreview } from '@/components/document-preview'
import { renderDocument } from '@/lib/mnda-template'
import type { MndaFormData } from '@/lib/types'
import { defaultMndaFormData } from '@/lib/types'

interface DocumentEditorProps {
  slug: string
}

export function DocumentEditor({ slug }: DocumentEditorProps) {
  const entry = getCatalogEntry(slug)
  const [templateContent, setTemplateContent] = useState<string | null>(null)
  const [fields, setFields] = useState<Record<string, string | number | boolean>>({})

  useEffect(() => {
    fetch(`/api/templates/${slug}/content`)
      .then((res) => (res.ok ? res.text() : null))
      .then((text) => setTemplateContent(text))
      .catch(() => setTemplateContent(''))
  }, [slug])

  const handleFieldUpdates = (updates: Record<string, string | number | boolean>) => {
    setFields((prev) => ({ ...prev, ...updates }))
  }

  if (!entry) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2" style={{ color: '#032147' }}>
            Document not found
          </h1>
          <p className="mb-4" style={{ color: '#888888' }}>
            The document type &quot;{slug}&quot; is not in the catalog.
          </p>
          <Link href="/" className="text-sm underline" style={{ color: '#209dd7' }}>
            ← Back to Document Library
          </Link>
        </div>
      </div>
    )
  }

  const isMnda = slug === 'mutual-non-disclosure-agreement'

  const mndaData: MndaFormData = isMnda
    ? {
        ...defaultMndaFormData,
        ...Object.fromEntries(
          Object.entries(fields).filter(([k]) => k in defaultMndaFormData)
        ),
      }
    : defaultMndaFormData

  const mndaMarkdown = isMnda ? renderDocument(mndaData) : ''

  const handleDownload = () => {
    const original = document.title
    document.title = slug
    window.addEventListener('afterprint', () => { document.title = original }, { once: true })
    window.print()
  }

  return (
    <div className="h-screen overflow-hidden bg-slate-50 flex flex-col">
      <header className="h-14 bg-white border-b flex items-center px-6 gap-3 shrink-0 no-print">
        <Link
          href="/"
          className="text-xs font-semibold tracking-widest uppercase hover:underline"
          style={{ color: '#888888' }}
        >
          ← PreLegal
        </Link>
        <span className="text-muted-foreground">/</span>
        <span className="text-sm font-medium truncate" style={{ color: '#032147' }}>
          {entry.name}
        </span>
        <div className="ml-auto">
          <button
            onClick={handleDownload}
            className="text-xs font-semibold px-4 py-1.5 rounded-lg text-white transition-opacity hover:opacity-90"
            style={{ backgroundColor: '#753991' }}
          >
            Download PDF
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <aside
          className="shrink-0 bg-white border-r flex flex-col overflow-hidden no-print"
          style={{ width: 420 }}
        >
          <div className="flex-1 overflow-hidden flex flex-col p-6">
            <ChatInterface
              documentType={slug}
              documentName={entry.name}
              onFieldUpdates={handleFieldUpdates}
            />
          </div>
        </aside>

        <main className="flex-1 overflow-y-auto p-8 print-area">
          {isMnda ? (
            <MndaPreview markdown={mndaMarkdown} />
          ) : (
            <DocumentPreview
              templateContent={templateContent}
              fields={fields}
              documentName={entry.name}
            />
          )}
        </main>
      </div>
    </div>
  )
}

