import { CATALOG } from '@/lib/catalog'
import { DocumentEditor } from './document-editor'

export function generateStaticParams() {
  return CATALOG.map((entry) => ({ slug: entry.slug }))
}

interface PageProps {
  params: Promise<{ slug: string }>
}

export default async function DocumentPage({ params }: PageProps) {
  const { slug } = await params
  return <DocumentEditor slug={slug} />
}
