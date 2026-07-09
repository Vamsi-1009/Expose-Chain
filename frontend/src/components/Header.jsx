export default function Header() {
  return (
    <header className="border-b sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-6 py-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div
              className="w-11 h-11 rounded-xl flex items-center justify-center"
              style={{
                background: 'linear-gradient(135deg, rgba(0,255,136,0.15), rgba(0,212,255,0.15))',
                border: '1px solid rgba(0,255,136,0.3)',
              }}
            >
              <i className="fas fa-shield-alt text-xl" style={{ color: '#00ff88' }}></i>
            </div>
            <div>
              <h1 className="display-font text-xl font-bold tracking-wider" style={{ color: '#ffffff' }}>
                EXPOSE<span style={{ color: '#00ff88' }}>CHAIN</span>
              </h1>
              <p className="text-xs mt-0.5 font-semibold" style={{ color: '#6b7a94', letterSpacing: '2px' }}>
                AI-POWERED THREAT INTELLIGENCE
              </p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="hidden md:flex items-center gap-3">
              <div className="status-dot"></div>
              <span className="mono text-xs font-bold" style={{ color: '#6b7a94' }}>SYSTEM ONLINE</span>
            </div>
            <div className="text-right hidden md:block">
              <div className="mono text-xs font-bold" style={{ color: '#8b9bb0' }}>v2.0.0</div>
              <div className="text-xs font-semibold" style={{ color: '#6b7a94' }}>
                by <span style={{ color: '#8b9bb0' }}>Vamsi Krishna</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
