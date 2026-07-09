import { useEffect, useState } from 'react'

function useCountUp(target, delay = 0) {
  const [value, setValue] = useState(0)
  useEffect(() => {
    if (target === undefined || target === null) return
    const timeout = setTimeout(() => {
      let current = 0
      const increment = Math.max(target / 30, 0.5)
      const timer = setInterval(() => {
        current += increment
        if (current >= target) {
          setValue(target)
          clearInterval(timer)
        } else {
          setValue(Math.floor(current))
        }
      }, 30)
    }, delay)
    return () => clearTimeout(timeout)
  }, [target, delay])
  return value
}

export default function StatsGrid({ aiScore, threatLevel, sslScore, ipCount }) {
  const animatedAi = useCountUp(aiScore)
  const animatedSsl = useCountUp(sslScore, 200)
  const animatedIp = useCountUp(ipCount, 400)

  const sslColor = sslScore === undefined ? '#8b9bb0' : sslScore >= 85 ? '#00ff88' : sslScore >= 70 ? '#ffcc00' : '#ff3366'

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mb-10">
      <div className="stat-card p-6 animate-in" style={{ '--accent-color': '#00d4ff' }}>
        <p className="section-label mb-2">AI Risk Score</p>
        <p className="display-font text-3xl font-bold" style={{ color: '#00d4ff' }}>{animatedAi}/100</p>
      </div>
      <div className="stat-card p-6 animate-in" style={{ '--accent-color': '#ffcc00' }}>
        <p className="section-label mb-2">Threat Level</p>
        <p className={`text-lg font-bold badge-${threatLevel || 'unknown'} inline-block px-3 py-1 rounded-lg`}>
          {(threatLevel || '-').toUpperCase()}
        </p>
      </div>
      <div className="stat-card p-6 animate-in" style={{ '--accent-color': '#00ff88' }}>
        <p className="section-label mb-2">SSL Score</p>
        <p className="display-font text-2xl font-bold" style={{ color: sslColor }}>
          {sslScore === undefined ? 'N/A' : `${animatedSsl}`}
        </p>
      </div>
      <div className="stat-card p-6 animate-in" style={{ '--accent-color': '#a855f7' }}>
        <p className="section-label mb-2">IPs Found</p>
        <p className="display-font text-2xl font-bold" style={{ color: '#a855f7' }}>{animatedIp}</p>
      </div>
    </div>
  )
}
