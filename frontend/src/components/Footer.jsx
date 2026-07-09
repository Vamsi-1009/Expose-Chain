export default function Footer() {
  return (
    <footer className="border-t mt-20 py-8" style={{ borderColor: 'rgba(54,65,96,0.4)' }}>
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ background: 'rgba(0,255,136,0.08)', border: '1px solid rgba(0,255,136,0.2)' }}
          >
            <i className="fas fa-shield-alt text-xs" style={{ color: '#00ff88' }}></i>
          </div>
          <span className="text-sm font-bold" style={{ color: '#8b9bb0' }}>ExposeChain v2.0.0 - AI-Powered</span>
        </div>
        <p className="text-sm font-semibold" style={{ color: '#6b7a94' }}>
          Built by <span style={{ color: '#8b9bb0' }}>Vamsi Krishna</span> &bull; Threat Intelligence Platform
        </p>
      </div>
    </footer>
  )
}
