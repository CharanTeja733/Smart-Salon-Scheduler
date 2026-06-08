import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getPractitioner, getAvailability } from '../api/client'
import DatePicker from '../components/DatePicker'
import TimeSlotGrid from '../components/TimeSlotGrid'
import BookingForm from '../components/BookingForm'
import Loader from '../components/Loader'
import ErrorAlert from '../components/ErrorAlert'

export default function BookingPage() {
  const { practitionerId } = useParams()
  const [practitioner, setPractitioner] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [slots, setSlots] = useState([])
  const [selectedSlot, setSelectedSlot] = useState(null)

  useEffect(() => {
    getPractitioner(practitionerId, false)
      .then(res => setPractitioner(res.data))
      .catch(err => setError(err.response?.data?.detail || 'Failed to load practitioner'))
      .finally(() => setLoading(false))
  }, [practitionerId])

  useEffect(() => {
    if (!practitionerId || !selectedDate) return
    const dateStr = selectedDate.toISOString().split('T')[0]
    getAvailability(practitionerId, dateStr, 30)
      .then(res => setSlots(res.data.available_slots))
      .catch(err => console.error('Slots error', err))
  }, [practitionerId, selectedDate])

  if (loading) return <Loader />
  if (error) return <ErrorAlert message={error} />

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="mb-4">
        <Link to="/" className="text-pink-600 hover:underline">← Back to Search</Link>
      </div>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-4 mb-6">
          {practitioner.photo_url && (
            <img src={practitioner.photo_url} alt={practitioner.name} className="w-16 h-16 rounded-full object-cover" />
          )}
          <div>
            <h1 className="text-2xl font-bold">{practitioner.name}</h1>
            <p className="text-gray-600">{practitioner.salon_name} • {practitioner.specialty}</p>
            <p className="text-lg font-semibold">${practitioner.base_price}</p>
          </div>
        </div>

        <DatePicker selectedDate={selectedDate} onSelect={setSelectedDate} />
        <TimeSlotGrid slots={slots} selectedSlot={selectedSlot} onSelect={setSelectedSlot} />

        {selectedSlot && (
          <div className="mt-8 border-t pt-6">
            <h3 className="text-lg font-medium mb-4">Your Information</h3>
            <BookingForm
              practitioner={practitioner}
              preselectedSlot={selectedSlot}
              onCancel={() => setSelectedSlot(null)}
            />
          </div>
        )}
      </div>
    </div>
  )
}