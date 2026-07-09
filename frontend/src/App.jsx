import { useState } from 'react'
import Header from './components/Header.jsx'
import Hero from './components/Hero.jsx'
import SearchBar from './components/SearchBar.jsx'
import LoadingTerminal from './components/LoadingTerminal.jsx'
import ErrorBanner from './components/ErrorBanner.jsx'
import StatsGrid from './components/StatsGrid.jsx'
import AIPanel from './components/AIPanel.jsx'
import ResultTabs from './components/ResultTabs.jsx'
import Footer from './components/Footer.jsx'
import { runScan } from './api.js'

export default function App() {
  const [status, setStatus] = useState('idle') // idle | loading | done | error
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [scanTime, setScanTime] = useState('')

  const handleScan = async (target, scanType) => {
    setStatus('loading')
    setError('')
    try {
      const data = await runScan(target, scanType)
      setResult(data)
      setScanTime(new Date().toLocaleTimeString())
      setTimeout(() => setStatus('done'), 700)
    } catch (e) {
      setError(e.message)
      setStatus('error')
    }
  }

  const ai = result?.data?.ai_analysis || {}
  const sslScore = result?.data?.ssl_security_analysis?.security_score
  const ipCount = result?.data?.geolocation?.total_ips || 0

  return (
    <>
      <Header />

      <main className="max-w-7xl mx-auto px-6 py-10">
        {status === 'idle' && <Hero />}
        <SearchBar onScan={handleScan} scanning={status === 'loading'} />

        {status === 'loading' && <LoadingTerminal done={false} />}
        {status === 'error' && <ErrorBanner message={error} />}

        {status === 'done' && result && (
          <div>
            <div className="flex items-center gap-3 mb-8 animate-in flex-wrap">
              <div className="w-2.5 h-2.5 rounded-full" style={{ background: '#16a34a' }}></div>
              <span className="mono text-xs font-bold" style={{ color: '#475569' }}>TARGET</span>
              <span className="mono text-lg font-bold" style={{ color: '#4f46e5' }}>{result.target.toUpperCase()}</span>
              <span
                className="mono text-xs px-3 py-1 rounded-lg font-bold"
                style={{ background: '#eef2ff', color: '#4f46e5', border: '1px solid #e0e7ff' }}
              >
                {result.data.scan_type.toUpperCase()}
              </span>
              <div className="flex-1"></div>
              <span className="mono text-sm font-semibold" style={{ color: '#64748b' }}>
                <i className="far fa-clock mr-2"></i>{scanTime}
              </span>
            </div>

            <StatsGrid
              aiScore={ai.overall_risk_score || 0}
              threatLevel={ai.threat_level}
              sslScore={sslScore}
              ipCount={ipCount}
            />
            <AIPanel ai={ai} />
            <ResultTabs data={result.data} />
          </div>
        )}
      </main>

      <Footer />
    </>
  )
}
