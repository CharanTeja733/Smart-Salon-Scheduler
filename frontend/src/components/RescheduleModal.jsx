import { useState, useEffect } from 'react'
import { getAvailability } from '../api/client'
import DatePicker from './DatePicker'
import TimeSlotGrid from './TimeSlotGrid'

export default function RescheduleModal({ isOpen, onClose, appointment, onRescheduled }) {
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [slots, setSlots] = useState([])
  const [selectedSlot, setSelectedSlot] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!isOpen || !appointment) return
    setSelectedDate(new Date())
    setSlots([])
    setSelectedSlot(null)
    setError(null)
  }, [isOpen, appointment])

  useEffect(() => {
    if (!isOpen || !appointment || !selectedDate) return
    const fetchSlots = async () => {
      setLoading(true)
      setError(null)
      try {
        const dateStr = selectedDate.toISOString().split('T')[0]
        const res = await getAvailability(appointment.practitioner_id, dateStr, 30)
        setSlots(res.data.available_slots)
        setSelectedSlot(null)
      } catch (err) {
        setError('Failed to load slots')
      } finally {
        setLoading(false)
      }
    }
    fetchSlots()
  }, [isOpen, appointment, selectedDate])

  const handleConfirm = async () => {
    if (!selectedSlot) {
      setError('Please select a new time slot')
      return
    }
    setError(null)
    try {
      await onRescheduled(selectedSlot)
      onClose()
    } catch (err) {
      // Extract detailed error message from backend
      let errorMsg = 'Reschedule failed'
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail
        if (Array.isArray(detail) && detail[0]?.msg) {
          errorMsg = detail[0].msg
        } else if (typeof detail === 'string') {
          errorMsg = detail
        }
      } else if (err.message) {
        errorMsg = err.message
      }
      setError(errorMsg)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Reschedule Appointment</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        <div className="mb-4">
          <p className="text-sm text-gray-600">Current: {new Date(appointment.start_time).toLocaleString()}</p>
        </div>
        <DatePicker selectedDate={selectedDate} onSelect={setSelectedDate} />
        {loading && <p className="text-gray-500 text-sm mt-2">Loading slots...</p>}
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        {!loading && (
          <TimeSlotGrid slots={slots} selectedSlot={selectedSlot} onSelect={setSelectedSlot} />
        )}
        <div className="flex gap-3 mt-4">
          <button onClick={onClose} className="flex-1 px-3 py-2 border rounded-md">Cancel</button>
          <button
            onClick={handleConfirm}
            disabled={!selectedSlot || loading}
            className="flex-1 bg-pink-600 text-white py-2 rounded-md disabled:bg-gray-400"
          >
            Confirm Reschedule
          </button>
        </div>
      </div>
    </div>
  )
}