import { GoogleMap, LoadScript, Marker, InfoWindow } from '@react-google-maps/api'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const containerStyle = { width: '100%', height: '400px' }

export default function Map({ salons, center }) {
  const [selected, setSelected] = useState(null)
  const navigate = useNavigate()

  if (!import.meta.env.VITE_GOOGLE_MAPS_API_KEY) {
    return <div style={{ height: 400, background: '#eee', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      Google Maps API key missing
    </div>
  }

  const handleBook = (salon) => {
    if (salon.practitioners && salon.practitioners.length) {
      navigate(`/booking/${salon.practitioners[0].id}`)
    } else {
      alert('No stylists available at this salon')
    }
  }

  return (
    <LoadScript googleMapsApiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY}>
      <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={14}>
        {salons.map(salon => (
          <Marker
            key={salon.id}
            position={{ lat: salon.latitude, lng: salon.longitude }}
            onClick={() => setSelected(salon)}
          />
        ))}
        {selected && (
          <InfoWindow
            position={{ lat: selected.latitude, lng: selected.longitude }}
            onCloseClick={() => setSelected(null)}
          >
            <div>
              <h4>{selected.name}</h4>
              <p>{selected.address}</p>
              <button onClick={() => handleBook(selected)}>Book now</button>
            </div>
          </InfoWindow>
        )}
      </GoogleMap>
    </LoadScript>
  )
}