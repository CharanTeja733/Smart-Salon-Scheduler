import { useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { GoogleMap, LoadScript, Marker, InfoWindow } from '@react-google-maps/api'
import { searchSalons } from '../api/client'
import { formatDistance } from '../utils/formatters'

const mapContainerStyle = { width: '100%', height: '400px' }
const defaultCenter = { lat: 40.7128, lng: -74.0060 }
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY
const PLACEHOLDER_IMAGE = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200"%3E%3Crect width="400" height="200" fill="%23f3f4f6"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af" font-family="sans-serif" font-size="16"%3ENo Image%3C/text%3E%3C/svg%3E'

export default function SearchPage() {
  const navigate = useNavigate()
  const [salons, setSalons] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [userLocation, setUserLocation] = useState(defaultCenter)
  const [selectedSalon, setSelectedSalon] = useState(null)
  const [manualLat, setManualLat] = useState('')
  const [manualLng, setManualLng] = useState('')
  const mapRef = useRef(null)
  const [mapKey, setMapKey] = useState(Date.now())

  useEffect(() => {
    setMapKey(Date.now())
  }, [])

  const onMapLoad = useCallback((map) => {
    mapRef.current = map
    setTimeout(() => {
      if (mapRef.current) {
        window.google.maps.event.trigger(mapRef.current, 'resize')
        mapRef.current.setCenter(userLocation)
      }
    }, 100)
  }, [userLocation])

  const fetchSalons = useCallback(async (lat, lng) => {
    setLoading(true)
    setError(null)
    try {
      const res = await searchSalons({ lat, lng, radius: 5000, limit: 30 })
      const salonsWithDistance = res.data.map(salon => ({
        ...salon,
        distance: salon.distance_meters // API now provides it directly
      }))
      // Sort by distance (closest first)
      salonsWithDistance.sort((a, b) => (a.distance || Infinity) - (b.distance || Infinity))
      setSalons(salonsWithDistance)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch salons')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const { latitude, longitude } = pos.coords
          setUserLocation({ lat: latitude, lng: longitude })
          fetchSalons(latitude, longitude)
        },
        () => {
          fetchSalons(defaultCenter.lat, defaultCenter.lng)
        }
      )
    } else {
      fetchSalons(defaultCenter.lat, defaultCenter.lng)
    }
  }, [fetchSalons])

  const handleManualSearch = (e) => {
    e.preventDefault()
    const lat = parseFloat(manualLat)
    const lng = parseFloat(manualLng)
    if (!isNaN(lat) && !isNaN(lng)) {
      setUserLocation({ lat, lng })
      fetchSalons(lat, lng)
      if (mapRef.current) {
        mapRef.current.setCenter({ lat, lng })
        window.google.maps.event.trigger(mapRef.current, 'resize')
      }
    } else {
      setError('Please enter valid latitude and longitude')
    }
  }

  const getSalonImage = (salon) => {
    if (salon.photo_reference) {
      return `https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=${salon.photo_reference}&key=${GOOGLE_MAPS_API_KEY}`
    }
    return PLACEHOLDER_IMAGE
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Find a Salon Near You</h1>

      <form onSubmit={handleManualSearch} className="mb-6 flex gap-2 flex-wrap">
        <input
          type="number"
          step="any"
          placeholder="Latitude"
          value={manualLat}
          onChange={(e) => setManualLat(e.target.value)}
          className="rounded-md border-gray-300 shadow-sm px-3 py-2 border focus:ring-pink-500 focus:border-pink-500"
        />
        <input
          type="number"
          step="any"
          placeholder="Longitude"
          value={manualLng}
          onChange={(e) => setManualLng(e.target.value)}
          className="rounded-md border-gray-300 shadow-sm px-3 py-2 border focus:ring-pink-500 focus:border-pink-500"
        />
        <button type="submit" className="bg-pink-600 text-white px-4 py-2 rounded-md hover:bg-pink-700">
          Search
        </button>
      </form>

      <LoadScript googleMapsApiKey={GOOGLE_MAPS_API_KEY}>
        <GoogleMap key={mapKey} mapContainerStyle={mapContainerStyle} center={userLocation} zoom={13} onLoad={onMapLoad}>
          {salons.map((salon) => (
            <Marker
              key={salon.id}
              position={{ lat: salon.latitude, lng: salon.longitude }}
              onClick={() => setSelectedSalon(salon)}
            />
          ))}
          {selectedSalon && (
            <InfoWindow
              position={{ lat: selectedSalon.latitude, lng: selectedSalon.longitude }}
              onCloseClick={() => setSelectedSalon(null)}
            >
              <div className="p-2 max-w-xs">
                <h3 className="font-bold">{selectedSalon.name}</h3>
                <p className="text-sm text-gray-600">{selectedSalon.address}</p>
                <p className="text-sm">⭐ {selectedSalon.rating} ({selectedSalon.rating_count})</p>
              </div>
            </InfoWindow>
          )}
        </GoogleMap>
      </LoadScript>

      {error && <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">{error}</div>}
      {loading && <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div></div>}

      {!loading && !error && (
        <div className="mt-8 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {salons.map((salon) => (
            <div
              key={salon.id}
              className="bg-white rounded-lg shadow-md overflow-hidden border cursor-pointer hover:shadow-lg transition"
              onClick={() => navigate(`/salon/${salon.id}`)}
            >
              <img src={getSalonImage(salon)} alt={salon.name} className="w-full h-48 object-cover" onError={(e) => { e.target.src = PLACEHOLDER_IMAGE }} />
              <div className="p-5">
                <h2 className="text-xl font-semibold text-gray-900">{salon.name}</h2>
                <p className="text-gray-600 text-sm mt-1">{salon.address}</p>
                <div className="flex items-center justify-between mt-2">
                  <div className="flex items-center">
                    <span className="text-yellow-500">★</span>
                    <span className="ml-1 text-sm">{salon.rating}</span>
                    <span className="text-gray-400 text-sm ml-1">({salon.rating_count})</span>
                  </div>
                  {salon.distance && (
                    <span className="text-xs text-gray-500">{formatDistance(salon.distance)}</span>
                  )}
                </div>
                <p className="text-sm text-gray-500 mt-2">{salon.practitioners?.length || 0} practitioner(s)</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}