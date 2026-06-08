import { useState, useEffect } from 'react'
import api from '../services/api'
import Map from '../components/Map'
import SalonCard from '../components/SalonCard'
import { useGeoLocation } from '../hooks/useGeoLocation'

export default function Search() {
  const { location, loading: geoLoading, error: geoError } = useGeoLocation()
  const [lat, setLat] = useState(location.lat)
  const [lng, setLng] = useState(location.lng)
  const [salons, setSalons] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLat(location.lat)
    setLng(location.lng)
  }, [location])

  const searchSalons = async () => {
    setLoading(true)
    try {
      const res = await api.get('/salons', { params: { lat, lng, radius: 5000, limit: 50 } })
      setSalons(res.data)
    } catch (err) {
      console.error(err)
      alert('Failed to fetch salons')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!geoLoading && !geoError) searchSalons()
  }, [location])

  return (
    <div>
      <h1>Find a Salon</h1>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <input
          type="number"
          placeholder="Latitude"
          value={lat}
          onChange={e => setLat(parseFloat(e.target.value))}
          step="any"
        />
        <input
          type="number"
          placeholder="Longitude"
          value={lng}
          onChange={e => setLng(parseFloat(e.target.value))}
          step="any"
        />
        <button onClick={searchSalons} disabled={loading}>Search</button>
      </div>

      {geoLoading && <p>Getting your location...</p>}
      {geoError && <p style={{ color: 'red' }}>Geolocation error: {geoError}. Using default coordinates.</p>}

      {salons.length > 0 && <Map salons={salons} center={{ lat, lng }} />}

      <div style={{ marginTop: '2rem' }}>
        {loading && <p>Loading...</p>}
        {!loading && salons.length === 0 && <p>No salons found.</p>}
        {salons.map(salon => <SalonCard key={salon.id} salon={salon} />)}
      </div>
    </div>
  )
}