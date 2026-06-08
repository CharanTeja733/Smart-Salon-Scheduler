import axios from 'axios'

if (!import.meta.env.VITE_API_URL) {
  console.error('Missing VITE_API_URL environment variable')
} 

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Helper to generate idempotency key for booking
export const getIdempotencyKey = () => `${Date.now()}-${Math.random().toString(36)}`

// API functions (to be implemented fully in later phases)
export const searchSalons = (params) => api.get('/salons', { params })
export const getSalon = (id) => api.get(`/salons/${id}`)
export const getPractitioner = (id, includeReviews = false) =>
  api.get(`/practitioners/${id}`, { params: { include_reviews: includeReviews } })
export const getAvailability = (id, date, duration = 30) =>
  api.get(`/practitioners/${id}/availability`, { params: { date, duration } })
export const createBooking = (data, idempotencyKey) =>
  api.post('/appointments', data, { headers: { 'Idempotency-Key': idempotencyKey } })
export const confirmBooking = (appointmentId, paymentIntentId) =>
  api.post(`/appointments/${appointmentId}/confirm`, { payment_intent_id: paymentIntentId })
export const getAppointment = (id) => api.get(`/appointments/${id}`)
export const getCustomerAppointments = (phone, status = null) =>
  api.get(`/customers/${encodeURIComponent(phone)}/appointments`, { params: { status } })
export const cancelBooking = (appointmentId, reason = '') =>
  api.post(`/appointments/${appointmentId}/cancel`, { reason })
export const rescheduleBooking = (appointmentId, newStartTime) =>
  api.post(`/appointments/${appointmentId}/reschedule`, { new_start_time: newStartTime })
export const createReview = (data) => api.post('/reviews', data)
export const addToWaitlist = (data) => api.post('/waitlist', data)
export const getWaitlistByPhone = (phone) =>
  api.get('/waitlist', { params: { customer_phone: phone } })

export default api