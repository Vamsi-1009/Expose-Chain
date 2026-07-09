export default function ErrorBanner({ message }) {
  return (
    <div className="glass-card p-7 mb-10" style={{ borderColor: '#fecaca' }}>
      <div className="flex items-center gap-4">
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center"
          style={{ background: '#fee2e2', border: '1px solid #fecaca' }}
        >
          <i className="fas fa-times text-xl" style={{ color: '#dc2626' }}></i>
        </div>
        <div>
          <p className="text-base font-bold" style={{ color: '#dc2626' }}>Scan Failed</p>
          <p className="text-sm mt-1 font-semibold" style={{ color: '#64748b' }}>{message}</p>
        </div>
      </div>
    </div>
  )
}
