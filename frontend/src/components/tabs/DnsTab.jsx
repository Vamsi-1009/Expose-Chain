export default function DnsTab({ dns }) {
  if (!dns?.dns_records) {
    return <p className="text-sm font-semibold" style={{ color: '#6b7a94' }}>No DNS records found</p>
  }

  return (
    <>
      {Object.entries(dns.dns_records).map(([type, rec]) => {
        if (!rec.success) return null
        return (
          <div key={type} className="mb-5">
            <div className="flex items-center gap-3 mb-2">
              <span className="record-chip">{type}</span>
              <span className="text-sm font-semibold" style={{ color: '#6b7a94' }}>
                {rec.count} record(s) &bull; {rec.query_time_ms}ms
              </span>
            </div>
            <div className="terminal-block">
              {rec.records.map((r, i) => {
                if (type === 'A' || type === 'AAAA') {
                  return (
                    <div key={i}>
                      <span className="t-dim">ip:</span> <span className="t-green">{r.ip}</span>{' '}
                      <span className="t-dim">ttl:</span> <span className="t-cyan">{r.ttl}s</span>
                    </div>
                  )
                }
                if (type === 'MX') {
                  return (
                    <div key={i}>
                      <span className="t-dim">pri:</span> <span className="t-yellow">{r.priority}</span>{' '}
                      <span className="t-dim">srv:</span> <span className="t-green">{r.mail_server}</span>
                    </div>
                  )
                }
                if (type === 'NS') {
                  return (
                    <div key={i}>
                      <span className="t-dim">ns:</span> <span className="t-green">{r.nameserver}</span>
                    </div>
                  )
                }
                if (type === 'TXT') {
                  return (
                    <div key={i}>
                      <span className="t-dim">txt:</span>{' '}
                      <span className="t-green" style={{ wordBreak: 'break-all' }}>{r.data}</span>
                    </div>
                  )
                }
                return null
              })}
            </div>
          </div>
        )
      })}
    </>
  )
}
