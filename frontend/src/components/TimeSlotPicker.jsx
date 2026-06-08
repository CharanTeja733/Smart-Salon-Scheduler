export default function TimeSlotPicker({ slots, selectedSlot, onSelect }) {
  return (
    <div>
      <h4>Available time slots:</h4>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
        {slots.map(slot => (
          <button
            key={slot}
            onClick={() => onSelect(slot)}
            style={{
              padding: '0.5rem 1rem',
              background: selectedSlot === slot ? '#007bff' : '#f8f9fa',
              color: selectedSlot === slot ? 'white' : 'black',
              border: '1px solid #ccc',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {new Date(slot).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </button>
        ))}
      </div>
    </div>
  )
}