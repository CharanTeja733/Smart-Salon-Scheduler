import { useState } from 'react'
import { createReview } from '../api/client'

export default function ReviewModal({ isOpen, onClose, appointment, onReviewSubmitted }) {
  const [rating, setRating] = useState(5)
  const [comment, setComment] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async () => {
    setSubmitting(true)
    setError(null)
    try {
      await createReview({
        appointment_id: appointment.id,
        rating,
        comment: comment || null,
      })
      onReviewSubmitted()
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit review')
    } finally {
      setSubmitting(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Write a Review</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        <div className="mb-4">
          <p className="font-medium">{appointment.practitioner_name}</p>
          <p className="text-sm text-gray-600">{new Date(appointment.start_time).toLocaleDateString()}</p>
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Rating *</label>
          <select
            value={rating}
            onChange={(e) => setRating(parseInt(e.target.value))}
            className="w-full border rounded-md p-2"
          >
            {[5,4,3,2,1].map(r => <option key={r} value={r}>{r} star{r !== 1 ? 's' : ''}</option>)}
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Comment (optional)</label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
            className="w-full border rounded-md p-2"
            placeholder="Share your experience..."
          />
        </div>
        {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
        <div className="flex gap-3">
          <button onClick={onClose} className="flex-1 px-3 py-2 border rounded-md">Cancel</button>
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="flex-1 bg-pink-600 text-white py-2 rounded-md disabled:bg-gray-400"
          >
            {submitting ? 'Submitting...' : 'Submit Review'}
          </button>
        </div>
      </div>
    </div>
  )
}