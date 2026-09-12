import { useState, useRef, useEffect } from 'react'
import client from '../api/client'

export default function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'bot', text: "Hey! I'm Fit Bot 💪 Ask me about workouts, nutrition, or form tips." },
  ])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  const send = async (e) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return
    setMessages((m) => [...m, { role: 'user', text }])
    setInput('')
    setSending(true)
    try {
      const res = await client.post('/chatbot', { message: text })
      setMessages((m) => [...m, { role: 'bot', text: res.data.response }])
    } catch {
      setMessages((m) => [...m, { role: 'bot', text: "Sorry, I couldn't respond right now." }])
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="fixed bottom-5 right-5 z-50">
      {open && (
        <div className="mb-3 w-80 max-w-[90vw] h-96 flex flex-col rounded-2xl border border-ink-800 bg-ink-900 shadow-2xl overflow-hidden">
          <div className="px-4 py-3 bg-brand-600 text-white font-semibold flex items-center justify-between">
            <span>Fit Bot</span>
            <button onClick={() => setOpen(false)} className="text-white/80 hover:text-white">
              ✕
            </button>
          </div>
          <div className="flex-1 overflow-y-auto px-3 py-3 space-y-2">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`text-sm px-3 py-2 rounded-xl max-w-[85%] ${
                  m.role === 'user'
                    ? 'ml-auto bg-brand-500 text-white'
                    : 'bg-ink-800 text-ink-100'
                }`}
              >
                {m.text}
              </div>
            ))}
            {sending && <div className="text-xs text-ink-500 px-2">Fit Bot is typing…</div>}
            <div ref={bottomRef} />
          </div>
          <form onSubmit={send} className="p-2 border-t border-ink-800 flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Fit Bot..."
              className="flex-1 bg-ink-800 rounded-lg px-3 py-2 text-sm text-white placeholder-ink-500 outline-none focus:ring-2 focus:ring-brand-500"
            />
            <button
              type="submit"
              disabled={sending}
              className="px-3 py-2 rounded-lg bg-brand-500 text-white text-sm font-medium disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </div>
      )}
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-14 h-14 rounded-full bg-brand-500 text-white shadow-xl flex items-center justify-center text-2xl hover:bg-brand-600 transition-colors"
        aria-label="Toggle Fit Bot chat"
      >
        {open ? '✕' : '💬'}
      </button>
    </div>
  )
}
