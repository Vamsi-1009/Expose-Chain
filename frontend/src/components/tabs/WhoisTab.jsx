export default function WhoisTab({ whois: w }) {
  if (!w?.success) {
    return <p className="text-sm font-semibold" style={{ color: '#64748b' }}>WHOIS data not available</p>
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
      <div className="terminal-block">
        <div className="flex items-center gap-2 mb-3">
          <i className="fas fa-calendar-alt text-sm" style={{ color: '#0284c7' }}></i>
          <span className="section-label" style={{ color: '#0284c7' }}>Registration</span>
        </div>
        <div><span className="t-dim">registrar :</span> <span className="t-green">{w.registrar || 'N/A'}</span></div>
        <div><span className="t-dim">created   :</span> <span className="t-green">{w.creation_date || 'N/A'}</span></div>
        <div><span className="t-dim">expires   :</span> <span className="t-green">{w.expiration_date || 'N/A'}</span></div>
        <div><span className="t-dim">updated   :</span> <span className="t-green">{w.updated_date || 'N/A'}</span></div>
        <div><span className="t-dim">age       :</span> <span className="t-cyan">{w.domain_age_days || 'N/A'} days</span></div>
        <div>
          <span className="t-dim">exp_in    :</span>{' '}
          <span className={w.days_until_expiration < 30 ? 't-red' : 't-cyan'}>{w.days_until_expiration || 'N/A'} days</span>
        </div>
      </div>
      <div className="terminal-block">
        <div className="flex items-center gap-2 mb-3">
          <i className="fas fa-user text-sm" style={{ color: '#7c3aed' }}></i>
          <span className="section-label" style={{ color: '#7c3aed' }}>Registrant</span>
        </div>
        <div><span className="t-dim">org     :</span> <span className="t-green">{w.registrant?.organization || 'N/A'}</span></div>
        <div><span className="t-dim">country :</span> <span className="t-green">{w.registrant?.country || 'N/A'}</span></div>
        <div><span className="t-dim">email   :</span> <span className="t-green">{w.contacts?.registrant_email || 'N/A'}</span></div>
        <div className="mt-3 pt-3" style={{ borderTop: '1px solid #e2e8f0' }}>
          <div className="flex items-center gap-2 mb-2">
            <i className="fas fa-dns text-sm" style={{ color: '#0284c7' }}></i>
            <span className="section-label" style={{ color: '#0284c7' }}>Name Servers</span>
          </div>
          {(w.name_servers || []).map((ns, i) => (
            <div key={i}><span className="t-dim">ns:</span> <span className="t-green">{ns}</span></div>
          ))}
        </div>
      </div>
    </div>
  )
}
