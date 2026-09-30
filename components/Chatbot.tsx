'use client'

import { FormEvent, useEffect, useRef, useState } from 'react'
import { LoaderCircle, MessageCircle, Send, X } from 'lucide-react'
import { apiRequest } from '@/lib/api'

type ChatRole = 'user' | 'assistant'
type ChatEntry = { id: number; role: ChatRole; content: string }
type ChatReply = { message: string }

const quickQuestions = ['View Menu', 'Coffee Prices', 'Opening Hours', 'Location', 'Special Offers']
const initialMessage: ChatEntry = {
  id: 0,
  role: 'assistant',
  content: "Hi there! I'm your Brew & Bloom assistant. What can I help you find?",
}

export default function Chatbot() {
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<ChatEntry[]>([initialMessage])
  const [loading, setLoading] = useState(false)
  const messageArea = useRef<HTMLDivElement>(null)
  const nextId = useRef(1)

  useEffect(() => {
    if (open && messageArea.current) messageArea.current.scrollTop = messageArea.current.scrollHeight
  }, [open, messages, loading])

  async function sendMessage(rawMessage: string) {
    const content = rawMessage.trim()
    if (!content || loading) return

    const userMessage: ChatEntry = { id: nextId.current++, role: 'user', content }
    const history = messages.filter(message => message.id !== 0).slice(-8).map(({ role, content: text }) => ({ role, content: text }))
    setMessages(current => [...current, userMessage])
    setInput('')
    setLoading(true)

    try {
      const result = await apiRequest<ChatReply>('/api/chat', {
        method: 'POST',
        body: { message: content, history },
      })
      const answer = result.success
        ? result.data.message
        : result.error.includes('Could not connect')
          ? "Sorry, I'm having trouble connecting right now. Please try again."
          : result.error.includes("couldn't process")
            ? result.error
            : "Sorry, I couldn't process that right now. Please try again."
      setMessages(current => [...current, { id: nextId.current++, role: 'assistant', content: answer }])
    } catch {
      setMessages(current => [...current, {
        id: nextId.current++,
        role: 'assistant',
        content: "Sorry, I couldn't process that right now. Please try again.",
      }])
    } finally {
      setLoading(false)
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    void sendMessage(input)
  }

  return (
    <div className="chatbot-root">
      {open && (
        <section className="chat-window" aria-label="Brew & Bloom Assistant" aria-live="polite">
          <header className="chat-header">
            <div className="chat-heading"><strong>Brew & Bloom Assistant</strong><span>Ask me about our cafe</span></div>
            <button className="chat-close" type="button" onClick={() => setOpen(false)} aria-label="Close chat"><X size={19} /></button>
          </header>

          <div className="chat-messages" ref={messageArea} role="log" aria-label="Conversation">
            {messages.map((message, index) => (
              <div key={message.id} className={`chat-message-row ${message.role}`}>
                <p className="chat-bubble">{message.content}</p>
                {index === 0 && messages.length === 1 && (
                  <div className="quick-questions" aria-label="Quick questions">
                    {quickQuestions.map(question => (
                      <button key={question} type="button" disabled={loading} onClick={() => void sendMessage(question)}>{question}</button>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && <div className="chat-message-row assistant"><p className="chat-bubble thinking"><LoaderCircle size={14} className="thinking-icon" /> Thinking...</p></div>}
          </div>

          <form className="chat-composer" onSubmit={handleSubmit}>
            <label className="sr-only" htmlFor="chat-message">Ask about our menu</label>
            <input id="chat-message" value={input} onChange={event => setInput(event.target.value)} maxLength={1000} placeholder="Ask about our menu..." autoComplete="off" />
            <button type="submit" disabled={loading || !input.trim()} aria-label="Send message"><Send size={17} /></button>
          </form>
          <p className="chat-disclaimer">Brew & Bloom cafe information assistant</p>
        </section>
      )}

      <button className="chat-launcher" type="button" onClick={() => setOpen(value => !value)} aria-label={open ? 'Close Brew & Bloom chat' : 'Open Brew & Bloom chat'} aria-expanded={open}>
        {open ? <X size={23} /> : <MessageCircle size={24} />}
      </button>
    </div>
  )
}
