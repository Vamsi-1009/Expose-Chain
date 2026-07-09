import { useState } from 'react'
import DnsTab from './tabs/DnsTab.jsx'
import WhoisTab from './tabs/WhoisTab.jsx'
import GeoTab from './tabs/GeoTab.jsx'
import SslTab from './tabs/SslTab.jsx'

const TABS = [
  { key: 'dns', label: 'DNS', icon: 'fa-server' },
  { key: 'whois', label: 'WHOIS', icon: 'fa-file-alt' },
  { key: 'geo', label: 'GEO', icon: 'fa-map-marker-alt' },
  { key: 'ssl', label: 'SSL', icon: 'fa-shield-alt' },
]

export default function ResultTabs({ data }) {
  const [active, setActive] = useState('dns')

  return (
    <div className="glass-card overflow-hidden animate-in">
      <div className="p-4 pb-0">
        <div className="nav-tabs">
          {TABS.map((t) => (
            <button key={t.key} onClick={() => setActive(t.key)} className={`nav-tab ${active === t.key ? 'active' : ''}`}>
              <i className={`fas ${t.icon} mr-2`}></i>{t.label}
            </button>
          ))}
        </div>
      </div>
      <div className="p-7 pt-5">
        <div className={active === 'dns' ? '' : 'hidden'}><DnsTab dns={data.dns_lookup} /></div>
        <div className={active === 'whois' ? '' : 'hidden'}><WhoisTab whois={data.whois_lookup} /></div>
        <div className={active === 'geo' ? '' : 'hidden'}><GeoTab geo={data.geolocation} active={active === 'geo'} /></div>
        <div className={active === 'ssl' ? '' : 'hidden'}><SslTab ssl={data.ssl_certificate} analysis={data.ssl_security_analysis} /></div>
      </div>
    </div>
  )
}
