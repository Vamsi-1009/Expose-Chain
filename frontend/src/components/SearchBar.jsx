import { useState } from 'react'

export default function SearchBar({ onScan, scanning }) {
  const [target, setTarget] = useState('')
  const [scanType, setScanType] = useState('quick')
  const [shake, setShake] = useState(false)

  const handleSubmit = () => {
    const trimmed = target.trim()
    if (!trimmed) {
      setShake(true)
      setTimeout(() => setShake(false), 500)
      return
    }
    onScan(trimmed, scanType)
  }

  return (
    <div className="glass-card p-8 mb-10 animate-in">
      <div className="flex items-center gap-3 mb-5">
        <span className="section-label">Target Analysis</span>
        <div className="flex-1 section-divider"></div>
      </div>
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <div className="absolute left-5 top-1/2 -translate-y-1/2 mono text-base" style={{ color: '#4a5a74' }}>
            <i className="fas fa-terminal"></i>
          </div>
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="Enter domain name (e.g. google.com)"
            className={`search-input w-full pl-14 pr-5 py-4 text-base ${shake ? 'shake' : ''}`}
            style={shake ? { borderColor: '#ff3366' } : undefined}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            autoComplete="off"
            spellCheck="false"
          />
        </div>
        <select
          value={scanType}
          onChange={(e) => setScanType(e.target.value)}
          className="cyber-select px-5 py-4 text-sm md:w-44"
        >
          <option value="quick">QUICK SCAN</option>
          <option value="full">FULL SCAN</option>
        </select>
        <button onClick={handleSubmit} disabled={scanning} className="exec-btn px-8 py-4 text-sm uppercase flex items-center justify-center gap-2">
          <i className={`fas ${scanning ? 'fa-spinner fa-spin' : 'fa-bolt'} text-base`}></i>
          <span>{scanning ? 'Scanning' : 'Execute'}</span>
        </button>
      </div>
    </div>
  )
}
