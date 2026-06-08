export default function TimeSlotGrid({ slots, selectedSlot, onSelect }) {
  if (!slots.length) {
    return <p className="text-gray-500 text-sm mt-2">No available slots for this date.</p>
  }

  // Convert UTC slots to local time for display
  const localSlots = slots.map(slot => ({
    iso: slot,
    local: new Date(slot).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }))

  return (
    <div className="mt-2">
      <label className="block text-sm font-medium text-gray-700 mb-1">Select Time</label>
      <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
        {localSlots.map(({ iso, local }) => (
          <button
            key={iso}
            onClick={() => onSelect(iso)}
            className={`px-2 py-1 rounded-md border text-sm ${
              selectedSlot === iso
                ? 'bg-pink-600 text-white border-pink-600'
                : 'bg-white text-gray-700 border-gray-300 hover:border-pink-400'
            }`}
          >
            {local}
          </button>
        ))}
      </div>
    </div>
  )
}