'use client'

import { useRef, useEffect, useState } from 'react'
import { Send } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface Message {
  role: 'assistant' | 'user'
  content: string
}

interface ChatInterfaceProps {
  documentType: string
  documentName: string
  onFieldUpdates: (updates: Record<string, string | number | boolean>) => void
}

const MNDA_GREETING =
  "Hi! I'm here to help you draft your Mutual NDA. Let's start — what's the purpose of this agreement? For example, are you evaluating a potential business partnership, exploring an acquisition, or something else?"

function getGreeting(documentType: string, documentName: string): string {
  if (documentType === 'mutual-non-disclosure-agreement') {
    return MNDA_GREETING
  }
  return `Hi! I'm here to help you draft your ${documentName}. Let's get started — what are the names of the two parties involved?`
}

export function ChatInterface({ documentType, documentName, onFieldUpdates }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: getGreeting(documentType, documentName) },
  ])
  const [confirmedFields, setConfirmedFields] = useState<Record<string, string | number | boolean>>({})
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = { role: 'user', content: input.trim() }
    const updatedMessages = [...messages, userMessage]
    setMessages(updatedMessages)
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: updatedMessages,
          current_fields: confirmedFields,
          document_type: documentType,
        }),
      })

      if (!res.ok) throw new Error('Request failed')

      const data = await res.json()

      setMessages((prev) => [...prev, { role: 'assistant', content: data.message }])

      const updates = Object.fromEntries(
        Object.entries(data.field_updates).filter(([, v]) => v !== null && v !== undefined)
      ) as Record<string, string | number | boolean>

      if (Object.keys(updates).length > 0) {
        setConfirmedFields((prev) => ({ ...prev, ...updates }))
        onFieldUpdates(updates)
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' },
      ])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="mb-4 pb-3 border-b">
        <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: '#888888' }}>
          AI Assistant
        </p>
        <p className="text-sm font-medium mt-0.5" style={{ color: '#032147' }}>
          {documentName}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className="max-w-[88%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed"
              style={
                msg.role === 'user'
                  ? { backgroundColor: '#753991', color: '#ffffff' }
                  : { backgroundColor: '#f1f5f9', color: '#1e293b' }
              }
            >
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div
              className="rounded-2xl px-4 py-2.5 text-sm"
              style={{ backgroundColor: '#f1f5f9', color: '#888888' }}
            >
              <span className="animate-pulse">Thinking…</span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="shrink-0 flex items-end gap-2 pt-4 border-t mt-4">
        <Textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message… (Enter to send)"
          className="resize-none min-h-[60px] max-h-[120px] flex-1"
          rows={2}
          disabled={loading}
        />
        <Button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          size="icon"
          className="shrink-0 self-end"
          style={{ backgroundColor: '#753991' }}
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
