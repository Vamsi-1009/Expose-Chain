export default function ErrorBanner({ message }) {
  return (
    <div className="glass-card p-7 mb-10" style={{ borderColor: 'rgba(255,51,102,0.4)' }}>
      <div className="flex items-center gap-4">
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center"
          style={{ background: 'rgba(255,51,102,0.15)', border: '1px solid rgba(255,51,102,0.35)' }}
        >
          <i className="fas fa-times text-xl" style={{ color: '#ff3366' }}></i>
        </div>
        <div>
          <p className="text-base font-bold" style={{ color: '#ff3366' }}>Scan Failed</p>
          <p className="text-sm mt-1 font-semibold" style={{ color: '#8b9bb0' }}>{message}</p>
        </div>
      </div>
    </div>
  )
}
