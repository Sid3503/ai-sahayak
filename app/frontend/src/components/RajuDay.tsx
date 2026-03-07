import { useEffect, useRef, useState } from 'react'
import { formatWelcomeName, getWelcomeMessage } from '../dashboard'

/** Today's date for WP UI date pill */
function getTodayDatePill(): string {
  return new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }).toUpperCase()
}

/** Time-of-day greeting in IST */
function getTimeGreeting(): string {
  const ist = new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }))
  const h = ist.getHours()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
}

/** IST time string for message/status bar — e.g. "2:45 PM" */
function formatISTTime(date: Date): string {
  return new Date(date.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }))
    .toLocaleTimeString('en-IN', { hour: 'numeric', minute: '2-digit', hour12: true })
}

/** IST time for status bar — e.g. "14:45" */
function formatISTStatusTime(date: Date): string {
  const ist = new Date(date.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }))
  return `${ist.getHours().toString().padStart(2, '0')}:${ist.getMinutes().toString().padStart(2, '0')}`
}

function useLiveClock() {
  const [time, setTime] = useState(() => new Date())
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  return time
}

export type RajuDayProps = {
  welcomeName?: string | null
  onClose: () => void
}

export type DayMessage = {
  from: 'user' | 'bot' | 'alert'
  text: string
  time?: string
  alertId?: string
  event_confidence_score?: number
}

const INITIAL_LIVE_MESSAGES: DayMessage[] = []

export function RajuDay({ welcomeName, onClose }: RajuDayProps) {
  const liveClock = useLiveClock()
  const displayName = formatWelcomeName(welcomeName)
  const retailerKey = (welcomeName || '').toString().trim().toLowerCase() || 'raju'
  const [welcome, setWelcome] = useState<{ main: string; sub: string } | null>(() =>
    displayName ? getWelcomeMessage(displayName, false) : null
  )
  useEffect(() => {
    if (displayName && !welcome) setWelcome(getWelcomeMessage(displayName, false))
  }, [displayName, welcome])

  const agentApiBase = (import.meta as any).env?.VITE_AGENT_API_BASE || 'http://localhost:8000'
  const [messages, setMessages] = useState<DayMessage[]>(INITIAL_LIVE_MESSAGES)
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [recording, setRecording] = useState(false)
  const [playingTtsIdx, setPlayingTtsIdx] = useState<number | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const seenAlertIdsRef = useRef<Set<string>>(new Set())
  const audioChunksRef = useRef<Blob[]>([])
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const ttsAudioRef = useRef<HTMLAudioElement | null>(null)

  // Seed welcome message when no messages yet (greet the corresponding customer in WP UI)
  useEffect(() => {
    if (typeof window === 'undefined') return
    const key = `ai_sahayak_live_messages_${retailerKey}`
    try {
      const raw = window.sessionStorage.getItem(key)
      if (raw) {
        const parsed = JSON.parse(raw)
        if (Array.isArray(parsed) && parsed.length > 0) {
          setMessages(parsed)
          return
        }
      }
      const greeting = getTimeGreeting()
      const welcomeText = displayName
        ? `${displayName} bhai, ${greeting.toLowerCase()}. Jo bhi chahiye bolo — main yahin hoon.`
        : `${greeting}. Jo chahiye bolo, main yahin hoon.`
      setMessages([{ from: 'bot', text: welcomeText }])
    } catch {
      const welcomeText = displayName
        ? `${displayName} bhai, jo chahiye bolo.`
        : "Jo chahiye bolo."
      setMessages([{ from: 'bot', text: welcomeText }])
    }
  }, [retailerKey, displayName])

  useEffect(() => {
    if (typeof window === 'undefined') return
    const key = `ai_sahayak_live_messages_${retailerKey}`
    try {
      window.sessionStorage.setItem(key, JSON.stringify(messages))
    } catch {
      // ignore
    }
  }, [messages, retailerKey])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    const userId = retailerKey
    const fetchAlerts = async () => {
      try {
        const res = await fetch(`${agentApiBase}/v1/alerts/for-user?user_id=${encodeURIComponent(userId)}`)
        if (!res.ok) return
        const data = await res.json()
        const alerts = data.alerts || []
        if (alerts.length === 0) return
        setMessages((prev) => {
          const seen = seenAlertIdsRef.current
          const toAdd: DayMessage[] = []
          for (const a of alerts) {
            if (a.id && !seen.has(a.id)) {
              seen.add(a.id)
              const timeStr = a.time ? new Date(a.time).toLocaleTimeString('en-IN', { hour: 'numeric', minute: '2-digit', hour12: true }) : ''
              toAdd.push({ from: 'alert', text: a.text, time: timeStr, alertId: a.id, event_confidence_score: a.event_confidence_score })
            }
          }
          if (toAdd.length === 0) return prev
          return [...prev, ...toAdd]
        })
      } catch {
        // ignore
      }
    }
    fetchAlerts()
    const t = setInterval(fetchAlerts, 30000)
    return () => clearInterval(t)
  }, [agentApiBase, retailerKey])

  async function sendMessage(overrideText?: string) {
    const text = (overrideText ?? input.trim()).trim()
    if (!text || sending) return
    if (!overrideText) setInput('')
    setMessages((prev) => [...prev, { from: 'user', text }])
    setSending(true)
    try {
      const response = await fetch(`${agentApiBase}/v1/webhook/incoming`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: retailerKey,
          text,
          platform: 'web',
          session_id: `day-session-${retailerKey}`,
        }),
      })
      if (!response.ok) throw new Error('Bot unavailable')
      const data = await response.json()
      const reply = data.reply || data.message || 'No reply from bot.'
      setMessages((prev) => [...prev, { from: 'bot', text: reply }])
    } catch {
      setMessages((prev) => [...prev, { from: 'bot', text: 'Bot is unavailable right now. Please try again.' }])
    } finally {
      setSending(false)
    }
  }

  function nowTime() {
    return new Date().toLocaleTimeString('en-IN', { hour: 'numeric', minute: '2-digit', hour12: true })
  }

  async function startVoiceRecording() {
    if (sending || recording) return
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioChunksRef.current = []
      const mime = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm'
      const recorder = new MediaRecorder(stream)
      recorder.ondataavailable = (e) => { if (e.data.size) audioChunksRef.current.push(e.data) }
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop())
        const blob = new Blob(audioChunksRef.current, { type: mime })
        const reader = new FileReader()
        reader.onloadend = async () => {
          const base64 = (reader.result as string)?.split(',')[1] ?? ''
          if (!base64) return
          setSending(true)
          const t = nowTime()
          setMessages((prev) => [...prev, { from: 'user', text: '…', time: t }])
          try {
            const response = await fetch(`${agentApiBase}/v1/webhook/incoming`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                user_id: retailerKey,
                text: 'Voice message',
                platform: 'web',
                phone_number: '0000000000',
                session_id: `day-session-${retailerKey}`,
                metadata: { voice_language: 'hi' },
                audio: base64,
                audio_media_type: mime,
              }),
            })
            const data = response.ok ? await response.json() : {}
            const reply = data.reply || data.message || 'Voice se reply nahi aa paaya. Dobara type karke bhejein.'
            const userText = data.transcribed_text || 'Voice message'
            setMessages((prev) => {
              const withoutPlaceholder = prev.slice(0, -1)
              return [...withoutPlaceholder, { from: 'user', text: userText, time: t }, { from: 'bot', text: reply, time: nowTime() }]
            })
          } catch {
            setMessages((prev) => {
              const withoutPlaceholder = prev.slice(0, -1)
              return [...withoutPlaceholder, { from: 'user', text: 'Voice message', time: t }, { from: 'bot', text: 'Voice abhi available nahi. Type karke bhejein.', time: nowTime() }]
            })
          } finally {
            setSending(false)
          }
        }
        reader.readAsDataURL(blob)
      }
      mediaRecorderRef.current = recorder
      recorder.start(200)
      setRecording(true)
    } catch (err) {
      console.error('Microphone access error', err)
    }
  }

  function stopVoiceRecording() {
    if (!recording || !mediaRecorderRef.current) return
    mediaRecorderRef.current.stop()
    mediaRecorderRef.current = null
    setRecording(false)
  }

  function toggleVoiceRecording() {
    if (recording) stopVoiceRecording()
    else startVoiceRecording()
  }

  async function playTts(text: string, msgIdx: number) {
    if (!text.trim() || playingTtsIdx !== null) return
    setPlayingTtsIdx(msgIdx)
    try {
      const res = await fetch(`${agentApiBase}/v1/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text.trim(), language_code: 'hi-IN' }),
      })
      if (!res.ok) throw new Error('TTS failed')
      const data = await res.json()
      const binary = atob(data.audio_base64)
      const bytes = new Uint8Array(binary.length)
      for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
      const blob = new Blob([bytes], { type: 'audio/mpeg' })
      const url = URL.createObjectURL(blob)
      const audio = new Audio(url)
      ttsAudioRef.current = audio
      audio.onended = () => { URL.revokeObjectURL(url); setPlayingTtsIdx(null) }
      audio.onerror = () => { URL.revokeObjectURL(url); setPlayingTtsIdx(null) }
      await audio.play()
    } catch {
      setPlayingTtsIdx(null)
    }
  }

  function stopTts() {
    const audio = ttsAudioRef.current
    if (audio) {
      audio.pause()
      audio.currentTime = 0
      ttsAudioRef.current = null
    }
    setPlayingTtsIdx(null)
  }

  return (
    <main style={{ height: '100%', overflow: 'hidden', position: 'relative', zIndex: 10, display: 'grid', placeItems: 'center' }}>

      {/* Live WhatsApp Feed (phone mockup) */}
      <section style={{ width: '100%', flex: '1 1 0%', display: 'grid', placeItems: 'center', overflow: 'hidden', position: 'relative', zIndex: 10, minHeight: 0 }}>
        <div style={{ pointerEvents: 'none', position: 'absolute', inset: 0, background: 'radial-gradient(ellipse 70% 70% at 55% 50%, rgba(251,191,36,0.05) 0%, transparent 65%)' }} />

        {/* Phone shell — match onboarding Bharat frame: amber border, same proportions */}
        <div style={{ position: 'relative', width: 'min(290px, 36vw)', height: 'min(560px, calc(100vh - 2rem))', flexShrink: 0, zIndex: 20 }}>
          <div style={{ position: 'absolute', left: -4, top: '18%', width: 3, height: 32, background: '#334155', borderRadius: '2px 0 0 2px' }} />
          <div style={{ position: 'absolute', left: -4, top: '26%', width: 3, height: 22, background: '#334155', borderRadius: '2px 0 0 2px' }} />
          <div style={{ position: 'absolute', right: -4, top: '22%', width: 3, height: 44, background: '#334155', borderRadius: '0 2px 2px 0' }} />

          <div style={{ borderRadius: '2.5rem', border: '6px solid #f59e0b', background: '#fff', overflow: 'hidden', isolation: 'isolate', zIndex: 20, height: '100%', display: 'flex', flexDirection: 'column', boxShadow: '0 20px 50px -12px rgba(0,0,0,0.2), 0 0 0 1px rgba(245,158,11,0.2)' }}>

            <div style={{ position: 'absolute', zIndex: 30, top: 8, left: '50%', transform: 'translateX(-50%)', width: 66, height: 18, borderRadius: 18, background: '#000' }} />

            <div style={{ background: '#075e54', padding: '10px 18px 4px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
              <span style={{ color: '#fff', fontSize: '0.62rem', fontWeight: 700 }}>{formatISTStatusTime(liveClock)}</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ display: 'flex', alignItems: 'flex-end', gap: '2px' }}>
                  {[3, 5, 7, 9].map(h => <span key={h} style={{ width: 2, height: h, background: '#fff', borderRadius: 1 }} />)}
                </span>
                <svg style={{ width: 10, height: 10, color: '#fff' }} fill="currentColor" viewBox="0 0 24 24"><path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3a4.237 4.237 0 00-6 0zm-4-4l2 2a7.074 7.074 0 0110 0l2-2C15.14 9.14 8.87 9.14 5 13z" /></svg>
                <span style={{ display: 'inline-flex', border: '1.5px solid rgba(255,255,255,0.7)', borderRadius: 3, padding: '1px 2px' }}>
                  <span style={{ width: 12, height: 5, background: '#4ade80', borderRadius: 1 }} />
                </span>
              </div>
            </div>

            <div style={{ background: '#075e54', padding: '5px 10px 9px', display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
              <button type="button" onClick={onClose} style={{ color: '#fff', background: 'none', border: 'none', cursor: 'pointer' }} aria-label="Back">
                <svg style={{ width: 16, height: 16 }} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7" /></svg>
              </button>
              <div style={{ width: 32, height: 32, borderRadius: '50%', background: '#fff', border: '2px solid rgba(255,255,255,0.3)', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <img src="/Generated_image.png" alt="AI Sahayak" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ fontSize: '0.88rem', fontWeight: 700, color: '#fff', lineHeight: 1.1 }}>AI Sahayak</p>
                <p style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.85)', margin: 0, lineHeight: 1.2 }}>
                  {sending ? 'typing…' : displayName ? `${displayName} · Live Alerts` : 'Live Alerts'}
                </p>
              </div>
              <div style={{ display: 'flex', gap: 2 }}>
                <button type="button" style={{ color: '#fff', background: 'none', border: 'none', cursor: 'pointer', padding: 4 }} aria-label="Video">
                  <svg style={{ width: 15, height: 15 }} fill="currentColor" viewBox="0 0 24 24"><path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z" /></svg>
                </button>
                <button type="button" style={{ color: '#fff', background: 'none', border: 'none', cursor: 'pointer', padding: 4 }} aria-label="Call">
                  <svg style={{ width: 15, height: 15 }} fill="currentColor" viewBox="0 0 24 24"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z" /></svg>
                </button>
              </div>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', background: '#efeae2', backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")", padding: '8px 10px', display: 'flex', flexDirection: 'column', gap: 6 }}>

              <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 4 }}>
                <span style={{ fontSize: '0.52rem', color: '#667781', background: 'rgba(0,0,0,0.06)', padding: '3px 12px', borderRadius: 12, fontWeight: 500 }}>{getTodayDatePill()}</span>
              </div>

              {messages.map((msg, i) => {
                const isRead = msg.from === 'user' && messages.slice(i + 1).some(m => m.from === 'bot')
                return (
                  <div key={i} style={{ display: 'flex', justifyContent: msg.from === 'user' ? 'flex-end' : 'flex-start', animation: 'messageIn 0.2s ease-out' }}>
                    {msg.from === 'alert' ? (
                      <div style={{ width: '94%', background: '#fff9e6', border: '1px solid #fcd34d', borderRadius: 10, padding: '7px 10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 3 }}>
                          <span style={{ fontSize: '0.55rem', fontWeight: 700, color: '#92400e', background: '#fde68a', borderRadius: 20, padding: '1px 7px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>AI Alert</span>
                          <span style={{ fontSize: '0.5rem', color: '#92400e', opacity: 0.7 }}>{msg.time}</span>
                          {msg.event_confidence_score != null && (
                            <span style={{ fontSize: '0.5rem', fontWeight: 700, color: '#b45309', marginLeft: 'auto' }}>{msg.event_confidence_score}% confidence</span>
                          )}
                        </div>
                        <p style={{ fontSize: '0.72rem', color: '#111b21', lineHeight: 1.4, whiteSpace: 'pre-wrap' }}>{msg.text}</p>
                      </div>
                    ) : (
                      <div style={{ maxWidth: '86%', borderRadius: msg.from === 'user' ? '8px 8px 2px 8px' : '8px 8px 8px 2px', padding: '6px 9px 4px', background: msg.from === 'user' ? '#d9fdd3' : '#ffffff', color: '#111b21', fontSize: '0.73rem', lineHeight: 1.42, wordBreak: 'break-word' as const, boxShadow: '0 1px 2px rgba(0,0,0,0.12)' }}>
                        <span style={{ display: 'block', whiteSpace: 'pre-wrap' }}>{msg.text}</span>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 3, marginTop: 3, flexWrap: 'wrap' }}>
                          {msg.from === 'bot' && msg.text.trim() && (
                            <button type="button" onClick={() => playingTtsIdx === i ? stopTts() : playTts(msg.text, i)} title={playingTtsIdx === i ? 'Stop' : 'Play (Polly)'} style={{ padding: 2, background: 'none', border: 'none', cursor: 'pointer', color: '#667781', display: 'flex' }} aria-label={playingTtsIdx === i ? 'Stop' : 'Play message'}><svg style={{ width: 14, height: 14 }} fill="currentColor" viewBox="0 0 24 24">{playingTtsIdx === i ? <path d="M6 6h12v12H6z" /> : <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z" />}</svg></button>
                          )}
                          <span style={{ fontSize: '0.5rem', color: '#667781' }}>{msg.time ?? formatISTTime(new Date())}</span>
                          {msg.from === 'user' && (
                            isRead ? (
                              <svg style={{ width: 14, height: 14, color: '#53bdeb' }} fill="currentColor" viewBox="0 0 24 24"><path d="M18 7l-1.41-1.41-6.34 6.34 1.41 1.41L18 7zm4.24-1.41L11.66 16.17 7.48 12l-1.41 1.41L11.66 19l12-12-1.42-1.41z" /></svg>
                            ) : (
                              <svg style={{ width: 12, height: 12, color: '#8696a0' }} fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" /></svg>
                            )
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}

              {sending && (
                <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                  <div style={{ background: '#fff', borderRadius: '8px 8px 8px 2px', padding: '8px 14px', display: 'flex', gap: 4, alignItems: 'center', boxShadow: '0 1px 2px rgba(0,0,0,0.12)' }}>
                    {[0, 150, 300].map(d => <span key={d} className="rounded-full animate-bounce" style={{ width: 5, height: 5, background: '#8696a0', animationDelay: `${d}ms`, display: 'inline-block' }} />)}
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            <div style={{ background: '#f0f2f5', borderTop: '1px solid #e9edef', padding: '7px 8px', flexShrink: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
              <button type="button" style={{ color: '#8696a0', background: 'none', border: 'none', cursor: 'pointer', padding: 2 }} aria-label="Emoji">
                <svg style={{ width: 20, height: 20 }} fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" /></svg>
              </button>
              <div style={{ flex: 1, background: '#fff', borderRadius: 22, padding: '5px 12px', display: 'flex', alignItems: 'center', boxShadow: '0 1px 2px rgba(0,0,0,0.08)' }}>
                <input
                  type="text"
                  placeholder="Message"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && sendMessage(undefined)}
                  disabled={sending}
                  style={{ flex: 1, background: 'transparent', border: 'none', outline: 'none', fontSize: '0.73rem', color: '#111b21' }}
                />
              </div>
              <button type="button" onClick={toggleVoiceRecording} disabled={sending} aria-label={recording ? 'Stop recording' : 'Voice message'}
                style={{ width: 32, height: 32, borderRadius: '50%', background: recording ? '#dc2626' : 'transparent', color: recording ? '#fff' : '#8696a0', border: 'none', cursor: sending ? 'default' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <svg style={{ width: 18, height: 18 }} fill="currentColor" viewBox="0 0 24 24"><path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z" /></svg>
              </button>
              <button type="button" onClick={() => sendMessage(undefined)} disabled={sending || !input.trim() || recording} aria-label="Send"
                style={{ width: 36, height: 36, borderRadius: '50%', background: '#128c7e', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', border: 'none', cursor: input.trim() ? 'pointer' : 'default', flexShrink: 0, boxShadow: '0 2px 8px rgba(18,140,126,0.5)', opacity: sending || !input.trim() ? 0.5 : 1 }}>
                {sending
                  ? <span style={{ fontSize: '0.65rem' }}>…</span>
                  : <svg style={{ width: 16, height: 16 }} fill="currentColor" viewBox="0 0 24 24"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z" /></svg>
                }
              </button>
            </div>

          </div>

          <div style={{ position: 'absolute', bottom: 4, left: '50%', transform: 'translateX(-50%)', width: 48, height: 3, borderRadius: 10, background: 'rgba(0,0,0,0.18)' }} />
        </div>

      </section>
    </main>
  )
}
