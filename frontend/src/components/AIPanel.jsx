import { useEffect, useState } from 'react'

function TypedSummary({ text }) {
  const [shown, setShown] = useState('')
  useEffect(() => {
    setShown('')
    let i = 0
    const interval = setInterval(() => {
      if (i >= text.length) {
        clearInterval(interval)
        return
      }
      setShown((prev) => prev + text.charAt(i))
      i++
    }, 20)
    return () => clearInterval(interval)
  }, [text])
  return <>{shown}</>
}

export default function AIPanel({ ai }) {
  const score = ai.overall_risk_score || 0
  const threat = ai.threat_level || 'unknown'
  const threats = ai.threats_detected || []
  const recs = ai.recommendations || []
  const barColor = score <= 30 ? '#16a34a' : score <= 60 ? '#d97706' : '#dc2626'

  return (
    <div className="glass-card p-8 mb-8 animate-in">
      <div className="flex items-center gap-4 mb-6">
        <div
          className="w-11 h-11 rounded-lg flex items-center justify-center"
          style={{ background: '#eff6ff', border: '1px solid #dbeafe' }}
        >
          <i className="fas fa-brain text-lg" style={{ color: '#0284c7' }}></i>
        </div>
        <span className="text-lg font-bold" style={{ color: '#0f172a' }}>AI Threat Intelligence</span>
        <div className="flex-1"></div>
        <span className={`text-sm px-3 py-1.5 rounded-lg font-bold mono badge-${threat}`}>
          {threat.toUpperCase()} RISK
        </span>
      </div>

      <div className="mb-8">
        <div className="flex justify-between mb-2">
          <span className="section-label">AI CONFIDENCE SCORE</span>
          <span className="mono text-sm font-bold" style={{ color: barColor }}>{score} / 100</span>
        </div>
        <div className="risk-gauge">
          <div className="risk-gauge-fill" style={{ width: `${score}%`, background: barColor }}></div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="terminal-block">
          <div className="flex items-center gap-2 mb-3">
            <i className="fas fa-exclamation-triangle text-sm" style={{ color: '#dc2626' }}></i>
            <span className="section-label" style={{ color: '#dc2626' }}>DETECTED THREATS</span>
          </div>
          {threats.length > 0 ? (
            threats.map((t, i) => (
              <div key={i} className="text-sm">
                <i className="fas fa-exclamation-circle mr-2 t-red"></i>
                <span className="t-red">{typeof t === 'object' ? t.factor : t}</span>
              </div>
            ))
          ) : (
            <div className="text-sm">
              <i className="fas fa-check-circle mr-2 t-green"></i>
              <span className="t-green">No major threats detected</span>
            </div>
          )}
        </div>
        <div className="terminal-block">
          <div className="flex items-center gap-2 mb-3">
            <i className="fas fa-lightbulb text-sm" style={{ color: '#d97706' }}></i>
            <span className="section-label" style={{ color: '#d97706' }}>AI RECOMMENDATIONS</span>
          </div>
          {recs.length > 0 ? (
            recs.map((r, i) => (
              <div key={i} className="text-sm">
                <i className="fas fa-lightbulb mr-2 t-yellow"></i>
                <span className="t-yellow">{r}</span>
              </div>
            ))
          ) : (
            <div className="text-sm">
              <i className="fas fa-check-circle mr-2 t-green"></i>
              <span className="t-green">No specific recommendations</span>
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 p-5 rounded-xl" style={{ background: '#f8fafc', border: '1px solid #e2e8f0' }}>
        <div className="flex items-center gap-2 mb-3">
          <i className="fas fa-info-circle text-sm" style={{ color: '#0284c7' }}></i>
          <span className="section-label" style={{ color: '#0284c7' }}>AI SUMMARY</span>
        </div>
        <p className="text-sm font-semibold" style={{ color: '#334155', lineHeight: 1.7 }}>
          <TypedSummary text={ai.summary || 'AI analysis completed.'} />
        </p>
      </div>
    </div>
  )
}
