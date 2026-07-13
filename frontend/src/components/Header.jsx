export default function Header() {
  return (
    <header className="border-b sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-6 py-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div
              className="w-11 h-11 rounded-xl flex items-center justify-center"
              style={{
                background: '#eef2ff',
                border: '1px solid #e0e7ff',
              }}
            >
              <i className="fas fa-shield-alt text-xl" style={{ color: '#4f46e5' }}></i>
            </div>
            <div>
              <h1 className="display-font text-xl font-bold tracking-tight" style={{ color: '#0f172a' }}>
                Expose<span style={{ color: '#4f46e5' }}>Chain</span>
              </h1>
              <p className="text-xs mt-0.5 font-semibold" style={{ color: '#94a3b8', letterSpacing: '1px' }}>
                AI-Powered Threat Intelligence
              </p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="hidden md:flex items-center gap-3">
              <div className="status-dot"></div>
              <span className="mono text-xs font-bold" style={{ color: '#64748b' }}>SYSTEM ONLINE</span>
            </div>
            <div className="text-right hidden md:block">
              <div className="mono text-xs font-bold" style={{ color: '#475569' }}>v2.0.0</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
