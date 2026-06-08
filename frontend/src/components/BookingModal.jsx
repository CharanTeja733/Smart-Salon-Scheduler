import { useEffect } from 'react'
import BookingForm from './BookingForm'

export default function BookingModal({ isOpen, onClose, practitioner, selectedSlot, onBookingSuccess }) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => { document.body.style.overflow = 'unset' }
  }, [isOpen])

  if (!isOpen) return null

  const handleSuccess = (appointmentId) => {
    onClose()
    if (onBookingSuccess) onBookingSuccess(appointmentId)
    else window.location.href = `/confirmation/${appointmentId}`
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Complete Your Booking</h2>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
          </div>
          <div className="mb-4 pb-3 border-b">
            <p className="font-medium">{practitioner.name}</p>
            <p className="text-sm text-gray-600">{practitioner.salon_name}</p>
            <p className="text-sm text-gray-600">
              {selectedSlot ? new Date(selectedSlot).toLocaleString() : 'No slot selected'}
            </p>
            <p className="text-sm font-semibold mt-1">Total: ${practitioner.base_price}</p>
          </div>
          <BookingForm
            practitioner={practitioner}
            preselectedSlot={selectedSlot}
            onSuccess={handleSuccess}
            onCancel={onClose}
          />
        </div>
      </div>
    </div>
  )
}