'use client'

import { MndaPreview } from '@/components/mnda-preview'

interface DocumentPreviewProps {
  templateContent: string | null
  fields: Record<string, string | number | boolean>
  documentName: string
}

/**
 * Convert a span display name to a camelCase field key.
 * E.g. "Customer Name" -> "customerName", "Governing Law" -> "governingLaw"
 */
function spanNameToFieldKey(spanText: string): string {
  const words = spanText.trim().split(/\s+/)
  return words
    .map((word, idx) => {
      const lower = word.toLowerCase()
      if (idx === 0) return lower
      return lower.charAt(0).toUpperCase() + lower.slice(1)
    })
    .join('')
}

/**
 * Try to look up a field value from the fields record using the span display name.
 * Tries camelCase conversion first, then exact lowercase match.
 * Returns undefined if no match found.
 */
function lookupFieldValue(
  spanText: string,
  fields: Record<string, string | number | boolean>
): string | undefined {
  const camelKey = spanNameToFieldKey(spanText)
  if (camelKey in fields) {
    return String(fields[camelKey])
  }
  const lowerKey = spanText.toLowerCase()
  if (lowerKey in fields) {
    return String(fields[lowerKey])
  }
  return undefined
}

const SPAN_PATTERN =
  /<span class="(?:coverpage_link|keyterms_link|orderform_link|businessterms_link|sow_link)">([^<]+)<\/span>/g

function replaceSpans(
  content: string,
  fields: Record<string, string | number | boolean>
): string {
  return content.replace(SPAN_PATTERN, (_match, spanText: string) => {
    const value = lookupFieldValue(spanText, fields)
    return value !== undefined ? value : spanText
  })
}

function buildCoverPageSection(
  documentName: string,
  fields: Record<string, string | number | boolean>
): string {
  const entries = Object.entries(fields).filter(([, v]) => v !== null && v !== undefined && v !== '')
  if (entries.length === 0) {
    return `# ${documentName}\n\n## Cover Page\n\n*No fields collected yet. Start chatting to fill in the document details.*\n\n`
  }

  const rows = entries
    .map(([key, value]) => `| ${key} | ${String(value)} |`)
    .join('\n')

  return `# ${documentName}\n\n## Cover Page\n\n| Field | Value |\n|---|---|\n${rows}\n\n`
}

export function DocumentPreview({ templateContent, fields, documentName }: DocumentPreviewProps) {
  if (templateContent === null) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-10 max-w-3xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-slate-200 rounded w-1/2" />
          <div className="h-4 bg-slate-200 rounded w-3/4" />
          <div className="h-4 bg-slate-200 rounded w-2/3" />
          <div className="h-4 bg-slate-200 rounded w-4/5" />
        </div>
      </div>
    )
  }

  const coverSection = buildCoverPageSection(documentName, fields)
  const bodyWithReplacements = replaceSpans(templateContent, fields)
  const fullMarkdown = `${coverSection}---\n\n${bodyWithReplacements}`

  return <MndaPreview markdown={fullMarkdown} />
}
