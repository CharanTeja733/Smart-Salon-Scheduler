import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getAppointment } from '../api/client'
import Loader from '../components/Loader'
import ErrorAlert from '../components/ErrorAlert'

export default function ConfirmationPage() {
  const { appointmentId } = useParams()
  const [appointment, setAppointment] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getAppointment(appointmentId)
      .then(res => setAppointment(res.data))
      .catch(err => setError(err.response?.data?.detail || 'Failed to load appointment'))
      .finally(() => setLoading(false))
  }, [appointmentId])

  if (loading) return <Loader />
  if (error) return <ErrorAlert message={error} />

  const localStart = appointment?.start_time ? new Date(appointment.start_time) : null

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="bg-white rounded-lg shadow-md p-6 text-center">
        <div className="text-green-500 text-5xl mb-4">✓</div>
        <h1 className="text-2xl font-bold text-gray-900">Booking Confirmed!</h1>
        <p className="text-gray-600 mt-2">Your appointment has been successfully booked.</p>
        <div className="mt-6 bg-gray-50 rounded-lg p-4 text-left">
          <h3 className="font-semibold text-lg">Appointment Details</h3>
          <p className="mt-2"><span className="font-medium">Salon:</span> {appointment.salon_name}</p>
          <p><span className="font-medium">Stylist:</span> {appointment.practitioner_name}</p>
          <p><span className="font-medium">Date & Time:</span> {localStart ? localStart.toLocaleString() : ''}</p>
          <p><span className="font-medium">Status:</span> <span className="text-green-600">{appointment.status}</span></p>
          <p><span className="font-medium">Total Price:</span> ${appointment.price}</p>
          <p><span className="font-medium">Deposit Paid:</span> ${appointment.deposit_paid ? (appointment.price * 0.2).toFixed(2) : 0}</p>
        </div>
        <div className="mt-6 flex gap-4 justify-center">
          <Link to="/" className="bg-pink-600 text-white px-4 py-2 rounded-md hover:bg-pink-700">Book Another</Link>
          <Link to="/my-bookings" className="border border-pink-600 text-pink-600 px-4 py-2 rounded-md hover:bg-pink-50">My Bookings</Link>
        </div>
      </div>
    </div>
  )
} 