import { useEffect, useRef } from 'react'
import L from 'leaflet'

export default function GeoTab({ geo, active }) {
  const mapRef = useRef(null)
  const mapInstance = useRef(null)

  useEffect(() => {
    if (!geo?.ip_locations || !mapRef.current) return

    if (!mapInstance.current) {
      mapInstance.current = L.map(mapRef.current).setView([20, 0], 2)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap',
      }).addTo(mapInstance.current)
    } else {
      mapInstance.current.eachLayer((layer) => {
        if (layer instanceof L.Marker) mapInstance.current.removeLayer(layer)
      })
    }

    const bounds = []
    for (const [ip, d] of Object.entries(geo.ip_locations)) {
      if (!d.success) continue
      const { latitude, longitude } = d.coordinates
      const marker = L.marker([latitude, longitude]).addTo(mapInstance.current)
      marker.bindPopup(`<strong>${ip}</strong><br>${d.location.city}, ${d.location.country}`)
      bounds.push([latitude, longitude])
    }
    if (bounds.length > 0) mapInstance.current.fitBounds(bounds)

    return () => {
      // keep map instance alive across data updates; only cleaned up on unmount
    }
  }, [geo])

  useEffect(() => {
    if (active && mapInstance.current) {
      setTimeout(() => mapInstance.current.invalidateSize(), 100)
    }
  }, [active])

  useEffect(() => {
    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove()
        mapInstance.current = null
      }
    }
  }, [])

  if (!geo?.ip_locations) {
    return <p className="text-sm font-semibold" style={{ color: '#64748b' }}>Geolocation data not available</p>
  }

  return (
    <>
      <div id="map" ref={mapRef} className="mb-6"></div>
      {Object.entries(geo.ip_locations).map(([ip, d]) => {
        if (!d.success) return null
        return (
          <div key={ip} className="mb-5">
            <div className="mb-2"><span className="record-chip">{ip}</span></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="terminal-block">
                <div className="flex items-center gap-2 mb-2">
                  <i className="fas fa-map-pin text-sm" style={{ color: '#ea580c' }}></i>
                  <span className="section-label" style={{ color: '#ea580c' }}>Location</span>
                </div>
                <div><span className="t-dim">city    :</span> <span className="t-green">{d.location.city}</span></div>
                <div><span className="t-dim">country :</span> <span className="t-green">{d.location.country}</span></div>
                <div><span className="t-dim">coords  :</span> <span className="t-cyan">{d.coordinates.latitude}, {d.coordinates.longitude}</span></div>
                <div><span className="t-dim">tz      :</span> <span className="t-green">{d.location.timezone}</span></div>
              </div>
              <div className="terminal-block">
                <div className="flex items-center gap-2 mb-2">
                  <i className="fas fa-network-wired text-sm" style={{ color: '#0284c7' }}></i>
                  <span className="section-label" style={{ color: '#0284c7' }}>Network</span>
                </div>
                <div><span className="t-dim">isp  :</span> <span className="t-green">{d.network.isp}</span></div>
                <div><span className="t-dim">asn  :</span> <span className="t-cyan">{d.network.as_number}</span></div>
                <div><span className="t-dim">org  :</span> <span className="t-green">{d.network.organization}</span></div>
              </div>
              <div className="terminal-block">
                <div className="flex items-center gap-2 mb-2">
                  <i className="fas fa-flag text-sm" style={{ color: '#7c3aed' }}></i>
                  <span className="section-label" style={{ color: '#7c3aed' }}>Flags</span>
                </div>
                <div><span className={d.flags.is_hosting ? 't-green' : 't-dim'}>[{d.flags.is_hosting ? 'x' : ' '}]</span> <span className="t-white">Hosting/DC</span></div>
                <div><span className={d.flags.is_proxy ? 't-red' : 't-dim'}>[{d.flags.is_proxy ? 'x' : ' '}]</span> <span className="t-white">Proxy/VPN</span></div>
                <div><span className={d.flags.is_mobile ? 't-yellow' : 't-dim'}>[{d.flags.is_mobile ? 'x' : ' '}]</span> <span className="t-white">Mobile</span></div>
              </div>
            </div>
          </div>
        )
      })}
    </>
  )
}
