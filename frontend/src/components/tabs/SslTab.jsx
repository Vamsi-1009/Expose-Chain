export default function SslTab({ ssl, analysis: an }) {
  if (!ssl?.success) {
    return <p className="text-sm font-semibold" style={{ color: '#64748b' }}>SSL certificate not available</p>
  }
  const ct = ssl.certificate

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
      <div className="terminal-block">
        <div className="flex items-center gap-2 mb-3">
          <i className="fas fa-certificate text-sm" style={{ color: '#0284c7' }}></i>
          <span className="section-label" style={{ color: '#0284c7' }}>Certificate</span>
        </div>
        <div><span className="t-dim">cn        :</span> <span className="t-green">{ct.subject.commonName}</span></div>
        <div><span className="t-dim">issuer    :</span> <span className="t-green">{ct.issuer.organizationName}</span></div>
        <div><span className="t-dim">valid_from:</span> <span className="t-green">{new Date(ct.valid_from).toLocaleDateString()}</span></div>
        <div>
          <span className="t-dim">valid_to  :</span>{' '}
          <span className={ct.days_until_expiration < 30 ? 't-red' : 't-green'}>{new Date(ct.valid_until).toLocaleDateString()}</span>
        </div>
        <div>
          <span className="t-dim">remaining :</span>{' '}
          <span className={ct.days_until_expiration < 30 ? 't-red' : 't-cyan'}>{ct.days_until_expiration} days</span>
        </div>
        <div><span className="t-dim">san_count :</span> <span className="t-cyan">{ct.san_count} domains</span></div>
      </div>
      <div className="terminal-block">
        <div className="flex items-center gap-2 mb-3">
          <i className="fas fa-tachometer-alt text-sm" style={{ color: '#4f46e5' }}></i>
          <span className="section-label" style={{ color: '#4f46e5' }}>Security</span>
        </div>
        <div>
          <span className="t-dim">score    :</span>{' '}
          <span
            style={{ fontSize: '18px', fontWeight: 800 }}
            className={an?.security_score >= 85 ? 't-green' : an?.security_score >= 70 ? 't-yellow' : 't-red'}
          >
            {an?.security_score || 'N/A'}/100
          </span>
        </div>
        <div>
          <span className="t-dim">risk     :</span>{' '}
          <span className={`badge-${an?.risk_level} px-2 py-0.5 rounded-lg text-xs mono`}>{an?.risk_level?.toUpperCase()}</span>
        </div>
        <div><span className="t-dim">protocol :</span> <span className="t-green">{ssl.ssl_version}</span></div>
        <div><span className="t-dim">key      :</span> <span className="t-green">{ct.key_type} {ct.key_size}-bit</span></div>
        <div><span className="t-dim">cipher   :</span> <span className="t-green">{ssl.cipher_suite.name}</span></div>
        {an?.issues?.length > 0 && (
          <div className="mt-3 pt-3" style={{ borderTop: '1px solid #e2e8f0' }}>
            {an.issues.map((issue, i) => (
              <div key={i} className={`text-xs ${issue === 'No major issues detected' ? 't-green' : 't-red'}`}>
                [{issue === 'No major issues detected' ? '+' : '-'}] {issue}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
