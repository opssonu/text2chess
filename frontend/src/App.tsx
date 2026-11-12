import { useEffect, useState } from 'react'
import './App.css'

type Status = {
  version: string
  env: string
  checks: Record<string, boolean>
}

function useApiStatus() {
  const [status, setStatus] = useState<Status | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      try {
        const res = await fetch('/api/v1/status')
        if (!res.ok) throw new Error(String(res.status))
        const body = (await res.json()) as Status
        if (!cancelled) {
          setStatus(body)
          setError(false)
        }
      } catch {
        if (!cancelled) setError(true)
      }
    }
    load()
    const id = setInterval(load, 10_000)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [])

  return { status, error }
}

const MODES = [
  { icon: '🤝', title: 'Play a friend', text: 'Send an invite link and play live.' },
  { icon: '🎲', title: 'Random opponent', text: 'Get matched with a player at your level.' },
  { icon: '🤖', title: 'Play a bot', text: 'Stockfish bots from beginner to master.' },
  { icon: '📱', title: 'Play by text', text: 'Slow games by SMS. Reply "Nf3" to move.' },
]

export default function App() {
  const { status, error } = useApiStatus()

  return (
    <main className="page">
      <header className="hero">
        <h1>♟️ text2chess</h1>
        <p className="tagline">Chess online, or one text message at a time.</p>
      </header>

      <section className="modes">
        {MODES.map((m) => (
          <article key={m.title} className="card">
            <span className="icon">{m.icon}</span>
            <h2>{m.title}</h2>
            <p>{m.text}</p>
            <span className="soon">Coming soon</span>
          </article>
        ))}
      </section>

      <footer className="status">
        {error && <span className="dot bad" />}
        {error && 'API unreachable'}
        {status && (
          <>
            {Object.entries(status.checks).map(([name, ok]) => (
              <span key={name} className="check">
                <span className={`dot ${ok ? 'ok' : 'bad'}`} /> {name}
              </span>
            ))}
            <span className="meta">
              v{status.version} · {status.env}
            </span>
          </>
        )}
        {!status && !error && 'Checking API…'}
      </footer>
    </main>
  )
}
