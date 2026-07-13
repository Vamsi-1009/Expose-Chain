export default function Footer() {
  return (
    <footer className="border-t mt-20 py-8" style={{ borderColor: '#e2e8f0' }}>
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ background: '#eef2ff', border: '1px solid #e0e7ff' }}
          >
            <i className="fas fa-shield-alt text-xs" style={{ color: '#4f46e5' }}></i>
          </div>
          <span className="text-sm font-bold" style={{ color: '#475569' }}>ExposeChain v2.0.0 - AI-Powered</span>
        </div>
        <p className="text-sm font-semibold" style={{ color: '#64748b' }}>
          Threat Intelligence Platform
        </p>
      </div>
    </footer>
  )
}
