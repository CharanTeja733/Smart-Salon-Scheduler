import React, { useState } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

function App() {
  const [salons, setSalons] = useState([])
  const [slots, setSlots] = useState([])
  const [selectedSalon, setSelectedSalon] = useState(null)

  const searchSalons = async () => {
    const res = await axios.get(`${API}/salons`)
    setSalons(res.data)
  }

  const checkAvailability = async (practitionerId, date) => {
    const res = await axios.get(`${API}/practitioners/${practitionerId}/availability?date_str=${date}`)
    setSlots(res.data.slots)
  }

  const bookAppointment = async () => {
    const booking = {
      practitioner_id: 1,
      start_time: slots[0],
      service_type: "haircut",
      duration_minutes: 30,
      customer_name: "John Doe",
      customer_email: "john@example.com",
      customer_phone: "+1234567890"
    }
    const res = await axios.post(`${API}/bookings`, booking)
    alert(`Booking created! Appointment ID: ${res.data.appointment_id}`)
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>✂️ Salon Scheduler</h1>
      
      <button onClick={searchSalons}>Find Salons Near Me</button>
      
      <div>
        {salons.map(salon => (
          <div key={salon.id} style={{ border: '1px solid #ccc', margin: 10, padding: 10 }}>
            <h3>{salon.name}</h3>
            <p>⭐ {salon.rating || 'New'}</p>
            <button onClick={() => checkAvailability(1, '2024-12-15')}>Check Availability</button>
          </div>
        ))}
      </div>

      {slots.length > 0 && (
        <div>
          <h3>Available Slots</h3>
          {slots.slice(0, 5).map(slot => (
            <button key={slot} onClick={bookAppointment}>
              {new Date(slot).toLocaleTimeString()}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default App