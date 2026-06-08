import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js'
import { createBooking, confirmBooking, getIdempotencyKey } from '../api/client'
import { isValidE164Phone } from '../utils/validation'
import PhoneInput from './PhoneInput'

export default function BookingForm({ practitioner, preselectedSlot, onSuccess, onCancel }) {
  const navigate = useNavigate()
  const stripe = useStripe()
  const elements = useElements()

  const [customer, setCustomer] = useState({ name: '', email: '', phone: '', notes: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {

    // Add this line to prevent double submission
    if (loading) return
    
    e.preventDefault()
    if (!stripe || !elements) return
    if (!preselectedSlot) {
      setError('No time slot selected')
      return
    }
    if (!isValidE164Phone(customer.phone)) {
      setError('Phone must be in E.164 format (e.g., +1234567890)')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // 1. Create booking (hold)
      const bookingPayload = {
        practitioner_id: practitioner.id,
        start_time: preselectedSlot,
        service_type: practitioner.specializations?.[0] || 'haircut',
        duration_minutes: 30,
        customer: {
          name: customer.name,
          email: customer.email || null,
          phone: customer.phone,
          notes: customer.notes || null,
        },
      }
      const idempotencyKey = getIdempotencyKey()
      const bookingRes = await createBooking(bookingPayload, idempotencyKey)
      const { appointment_id, client_secret } = bookingRes.data

      // 2. Confirm payment with Stripe
      const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
        payment_method: { card: elements.getElement(CardElement) },
      })
      if (stripeError) {
        if (stripeError.type === 'card_error') {
            throw new Error(stripeError.message)
        } else {
            throw new Error('Payment failed. Please try again.')
        }
      }

      // 3. Confirm booking on backend
      await confirmBooking(appointment_id, paymentIntent.id)

      // 4. Navigate to confirmation page
      if (onSuccess) {
                onSuccess(appointment_id)
            } else {
                navigate(`/confirmation/${appointment_id}`)
            }
            } catch (err) {
            setError(err.message || 'Booking failed')
            } finally {
            setLoading(false)
            }
        }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
          {error}
        </div>
      )}
      <div>
        <label className="block text-sm font-medium text-gray-700">Name *</label>
        <input
          required
          value={customer.name}
          onChange={(e) => setCustomer({ ...customer, name: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm px-3 py-2 border"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Email (optional)</label>
        <input
          type="email"
          value={customer.email}
          onChange={(e) => setCustomer({ ...customer, email: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm px-3 py-2 border"
        />
      </div>
      <PhoneInput
        value={customer.phone}
        onChange={(phone) => setCustomer({ ...customer, phone })}
        required
      />
      <div>
        <label className="block text-sm font-medium text-gray-700">Notes (optional)</label>
        <textarea
          value={customer.notes}
          onChange={(e) => setCustomer({ ...customer, notes: e.target.value })}
          rows={2}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm px-3 py-2 border"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Card Details (Deposit: ${(practitioner.base_price * 0.2).toFixed(2)})
        </label>
        <div className="p-3 border rounded-md bg-gray-50">
          <CardElement options={{ hidePostalCode: true }} />
        </div>
      </div>
      <div className="flex gap-3 pt-2">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading || !stripe}
          className="flex-1 bg-pink-600 text-white py-2 rounded-md font-semibold hover:bg-pink-700 disabled:bg-gray-400"
        >
          {loading ? 'Processing...' : `Pay Deposit & Book`}
        </button>
      </div>
    </form>
  )
}