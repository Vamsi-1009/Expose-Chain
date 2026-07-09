const FEATURES = [
  { icon: 'fa-server', label: 'DNS Records', desc: 'A, AAAA, MX, NS, TXT lookups', color: '#4f46e5', bg: '#eef2ff' },
  { icon: 'fa-file-alt', label: 'WHOIS Lookup', desc: 'Registration & ownership data', color: '#7c3aed', bg: '#f5f3ff' },
  { icon: 'fa-lock', label: 'SSL Analysis', desc: 'Certificate & security scoring', color: '#0284c7', bg: '#eff6ff' },
  { icon: 'fa-brain', label: 'AI Risk Score', desc: 'Automated threat assessment', color: '#16a34a', bg: '#f0fdf4' },
]

export default function Hero() {
  return (
    <div className="text-center mb-10 animate-in">
      <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-3" style={{ color: '#0f172a' }}>
        Uncover a domain's full attack surface in seconds
      </h2>
      <p className="text-base max-w-2xl mx-auto mb-8" style={{ color: '#64748b' }}>
        Enter any domain to run DNS, WHOIS, SSL, and geolocation checks - then get an AI-generated
        risk score with clear, actionable recommendations.
      </p>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {FEATURES.map((f) => (
          <div key={f.label} className="glass-card p-5 text-left">
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center mb-3"
              style={{ background: f.bg }}
            >
              <i className={`fas ${f.icon} text-sm`} style={{ color: f.color }}></i>
            </div>
            <p className="text-sm font-bold mb-0.5" style={{ color: '#0f172a' }}>{f.label}</p>
            <p className="text-xs" style={{ color: '#94a3b8' }}>{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
