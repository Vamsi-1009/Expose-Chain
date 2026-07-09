import { useEffect, useState } from 'react'

const MESSAGES = [
  'Initializing AI threat model',
  'Resolving DNS records',
  'Querying WHOIS database',
  'Mapping geolocation data',
  'Analyzing SSL certificate',
  'Running AI risk prediction',
  'Generating threat intelligence',
]

export default function LoadingTerminal({ done }) {
  const [lines, setLines] = useState([])

  useEffect(() => {
    setLines([])
    let i = 0
    const interval = setInterval(() => {
      if (i >= MESSAGES.length) {
        clearInterval(interval)
        return
      }
      setLines((prev) => {
        const updated = prev.map((l, idx) => (idx === prev.length - 1 ? { ...l, ok: true } : l))
        return [...updated, { text: MESSAGES[i], ok: false }]
      })
      i++
    }, 900)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (done) {
      setLines((prev) => prev.map((l) => ({ ...l, ok: true })))
    }
  }, [done])

  return (
    <>
      <div className="glass-card p-10 mb-10">
        <div className="flex flex-col items-center">
          <div className="flex items-center gap-3 mb-6">
            <div className="status-dot"></div>
            <span className="display-font text-lg font-semibold tracking-widest" style={{ color: '#4f46e5' }}>
              AI ANALYSIS IN PROGRESS
            </span>
          </div>
          <div className="terminal-block w-full max-w-2xl">
            {lines.map((l, i) => (
              <div key={i} className="t-green text-base">
                [*] {l.text}{l.ok ? <span className="t-cyan"> [OK]</span> : '...'}
              </div>
            ))}
            {done && <div className="t-cyan text-base font-bold">[+] AI ANALYSIS COMPLETE</div>}
          </div>
        </div>
      </div>
      <div className="space-y-6 mb-10">
        <div className="glass-card p-8">
          <div className="skeleton h-7 w-48 mb-6 rounded"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="skeleton h-28 rounded-2xl"></div>
            <div className="skeleton h-28 rounded-2xl"></div>
            <div className="skeleton h-28 rounded-2xl"></div>
            <div className="skeleton h-28 rounded-2xl"></div>
          </div>
        </div>
      </div>
    </>
  )
}
