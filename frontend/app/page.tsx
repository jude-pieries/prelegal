'use client'

import { useState } from 'react'
import { Download } from 'lucide-react'
import { ChatInterface } from '@/components/chat-interface'
import { MndaPreview } from '@/components/mnda-preview'
import { Button } from '@/components/ui/button'
import { defaultMndaFormData, type MndaFormData } from '@/lib/types'
import { renderDocument } from '@/lib/mnda-template'

export default function Home() {
  const [formData, setFormData] = useState<MndaFormData>(() => ({
    ...defaultMndaFormData,
    effectiveDate: new Date().toISOString().split('T')[0],
  }))

  const markdown = renderDocument(formData)

  const handleFieldUpdates = (updates: Partial<MndaFormData>) => {
    setFormData((prev) => ({ ...prev, ...updates }))
  }

  const handleDownloadPdf = () => {
    const original = document.title
    const company = formData.party1Company || formData.party2Company
    document.title = company ? `Mutual-NDA-${company}` : 'Mutual-NDA'
    window.addEventListener('afterprint', () => { document.title = original }, { once: true })
    window.print()
  }

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <header className="h-14 shrink-0 border-b bg-white flex items-center justify-between px-6 no-print">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold tracking-widest uppercase text-muted-foreground">PreLegal</span>
          <span className="text-muted-foreground">/</span>
          <span className="text-sm font-medium">Mutual NDA Creator</span>
        </div>
        <Button onClick={handleDownloadPdf} size="sm" className="gap-2">
          <Download className="h-4 w-4" />
          Download PDF
        </Button>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-[420px] shrink-0 border-r bg-white p-6 no-print flex flex-col overflow-hidden">
          <ChatInterface onFieldUpdates={handleFieldUpdates} />
        </aside>

        <main className="flex-1 overflow-y-auto bg-slate-50 p-8 print-area">
          <MndaPreview markdown={markdown} />
        </main>
      </div>
    </div>
  )
}
