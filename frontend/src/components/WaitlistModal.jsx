import { useState } from 'react'
import { addToWaitlist } from '../api/client'
import { isValidE164Phone } from '../utils/validation'
import PhoneInput from './PhoneInput'

export default function WaitlistModal({ isOpen, onClose, practitioner }) {
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [preferredStart, setPreferredStart] = useState('')
  const [preferredEnd, setPreferredEnd] = useState('')
  const [serviceType, setServiceType] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!name.trim()) {
      setError('Name is required')
      return
    }
    if (!isValidE164Phone(phone)) {
      setError('Phone must be in E.164 format (e.g., +1234567890)')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      await addToWaitlist({
        practitioner_id: practitioner.id,
        customer_phone: phone,
        preferred_date_start: preferredStart ? new Date(preferredStart).toISOString() : null,
        preferred_date_end: preferredEnd ? new Date(preferredEnd).toISOString() : null,
        preferred_service_type: serviceType || null,
        // Note: API also expects customer_name? The schema uses customer_phone only; name may not be required.
        // We'll assume name is not part of the payload; if needed, adjust.
      })
      setSuccess(true)
      setTimeout(() => {
        onClose()
        setSuccess(false)
        setName('')
        setPhone('')
        setPreferredStart('')
        setPreferredEnd('')
        setServiceType('')
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to join waitlist')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Join Waitlist for {practitioner.name}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        {success ? (
          <div className="text-green-600 text-center py-4">Added to waitlist!</div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium">Name *</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="mt-1 w-full border rounded-md p-2"
                required
              />
            </div>
            <PhoneInput value={phone} onChange={setPhone} required />
            <div>
              <label className="block text-sm font-medium">Preferred Date Start (optional)</label>
              <input
                type="date"
                value={preferredStart}
                onChange={(e) => setPreferredStart(e.target.value)}
                className="mt-1 w-full border rounded-md p-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Preferred Date End (optional)</label>
              <input
                type="date"
                value={preferredEnd}
                onChange={(e) => setPreferredEnd(e.target.value)}
                className="mt-1 w-full border rounded-md p-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Service Type (optional)</label>
              <input
                value={serviceType}
                onChange={(e) => setServiceType(e.target.value)}
                placeholder="e.g., haircut, color"
                className="mt-1 w-full border rounded-md p-2"
              />
            </div>
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <div className="flex gap-3">
              <button type="button" onClick={onClose} className="flex-1 px-3 py-2 border rounded-md">Cancel</button>
              <button type="submit" disabled={submitting} className="flex-1 bg-pink-600 text-white py-2 rounded-md disabled:bg-gray-400">
                {submitting ? 'Adding...' : 'Join Waitlist'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}