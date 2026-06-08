import { useNavigate } from 'react-router-dom'

export default function SalonCard({ salon }) {
  const navigate = useNavigate()
  return (
    <div style={{ border: '1px solid #ddd', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>
      <h3>{salon.name}</h3>
      <p>{salon.address}</p>
      <p>⭐ {salon.rating} ({salon.rating_count} reviews)</p>
      {salon.practitioners && salon.practitioners.length > 0 && (
        <div>
          <strong>Stylists:</strong>
          <ul style={{ listStyle: 'none', paddingLeft: 0 }}>
            {salon.practitioners.map(p => (
              <li key={p.id} style={{ marginBottom: '0.5rem' }}>
                {p.name} – ${p.base_price} (⭐ {p.rating})
                <button onClick={() => navigate(`/booking/${p.id}`)} style={{ marginLeft: '1rem' }}>Book</button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}