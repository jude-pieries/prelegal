'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'

interface MndaPreviewProps {
  markdown: string
}

export function MndaPreview({ markdown }: MndaPreviewProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-10 max-w-3xl mx-auto">
      <div
        className="prose prose-slate prose-sm max-w-none
          prose-headings:font-semibold
          prose-h1:text-xl prose-h1:mb-6
          prose-h2:text-base prose-h2:mt-8 prose-h2:mb-3
          prose-h3:text-sm prose-h3:mt-6 prose-h3:mb-2
          prose-p:text-sm prose-p:leading-relaxed
          prose-li:text-sm
          prose-table:text-sm
          prose-th:bg-slate-50 prose-th:font-medium
          prose-td:align-top
          prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline
          prose-hr:my-8"
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeRaw]}
        >
          {markdown}
        </ReactMarkdown>
      </div>
    </div>
  )
}
