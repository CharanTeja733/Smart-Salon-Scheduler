import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { matchStylist } from '../api/client'
import DatePicker from '../components/DatePicker'
import PhoneInput from '../components/PhoneInput'
import Loader from '../components/Loader'
import ErrorAlert from '../components/ErrorAlert'
import BookingModal from '../components/BookingModal'

const SERVICE_TYPES = [
  'haircut',
  'color',
  'blowout',
  'nails',
  'makeup',
  'waxing',
  'facial',
]

export default function AIMatchPage() {
  const navigate = useNavigate()
  const [serviceType, setServiceType] = useState('haircut')
  const [lat, setLat] = useState('')
  const [lng, setLng] = useState('')
  const [preferredDate, setPreferredDate] = useState(null)
  const [phone, setPhone] = useState('')
  const [limit, setLimit] = useState(3)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [matches, setMatches] = useState(null)

  // Booking modal state
  const [modalOpen, setModalOpen] = useState(false)
  const [selectedPractitioner, setSelectedPractitioner] = useState(null)
  const [selectedSlot, setSelectedSlot] = useState(null)

  // Track expanded slots per practitioner
  const [expandedSlots, setExpandedSlots] = useState({})

  const handleUseCurrentLocation = () => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLat(pos.coords.latitude.toString())
          setLng(pos.coords.longitude.toString())
        },
        () => {
          setError('Unable to get your location. Please enter manually.')
        }
      )
    } else {
      setError('Geolocation not supported. Please enter manually.')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setMatches(null)

    const params = {
      service_type: serviceType,
      limit,
    }
    if (lat && lng) {
      params.lat = parseFloat(lat)
      params.lng = parseFloat(lng)
    }
    if (preferredDate) {
      params.preferred_date = preferredDate.toISOString().split('T')[0]
    }
    if (phone) {
      params.customer_phone = phone
    }

    try {
      const res = await matchStylist(params)
      setMatches(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch stylist matches')
    } finally {
      setLoading(false)
    }
  }

  const handleSlotClick = (practitioner, slotIso) => {
    setSelectedPractitioner(practitioner)
    setSelectedSlot(slotIso)
    setModalOpen(true)
  }

  const handleBookingSuccess = (appointmentId) => {
    setModalOpen(false)
    navigate(`/confirmation/${appointmentId}`)
  }

  const toggleShowAllSlots = (practitionerId) => {
    setExpandedSlots(prev => ({
      ...prev,
      [practitionerId]: !prev[practitionerId]
    }))
  }

  // MatchScore component – no duplicate percentage text
  const MatchScore = ({ score }) => {
    const color = score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
    return (
      <div className="flex items-center gap-2">
        <div className="flex-1 bg-gray-200 rounded-full h-2">
          <div className={`${color} h-2 rounded-full`} style={{ width: `${score}%` }} />
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">AI Stylist Match</h1>
      <p className="text-gray-600 mb-6">
        Find the best stylist for your service based on expertise, ratings, and availability.
      </p>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Service Type *</label>
            <select
              value={serviceType}
              onChange={(e) => setServiceType(e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            >
              {SERVICE_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Limit (1-10)</label>
            <input
              type="number"
              min="1"
              max="10"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value) || 3)}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Location (optional)</label>
            <div className="flex gap-2">
              <input
                type="number"
                step="any"
                placeholder="Latitude"
                value={lat}
                onChange={(e) => setLat(e.target.value)}
                className="flex-1 border rounded-md px-3 py-2"
              />
              <input
                type="number"
                step="any"
                placeholder="Longitude"
                value={lng}
                onChange={(e) => setLng(e.target.value)}
                className="flex-1 border rounded-md px-3 py-2"
              />
              <button
                type="button"
                onClick={handleUseCurrentLocation}
                className="bg-gray-200 px-3 py-2 rounded-md text-sm hover:bg-gray-300"
              >
                📍
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Preferred Date (optional)</label>
            <DatePicker
              selectedDate={preferredDate}
              onSelect={setPreferredDate}
              minDate={new Date()}
              maxDays={90}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Phone (optional, for better matching)</label>
            <PhoneInput value={phone} onChange={setPhone} />
          </div>
        </div>

        <div className="mt-6">
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-pink-600 text-white py-2 rounded-md hover:bg-pink-700 disabled:bg-gray-400"
          >
            {loading ? 'Finding matches...' : 'Find Best Stylist'}
          </button>
        </div>
      </form>

      <ErrorAlert message={error} onDismiss={() => setError(null)} />

      {loading && <Loader />}

      {matches && matches.matches && matches.matches.length === 0 && (
        <div className="text-center text-gray-500 py-8">No matches found. Try different criteria.</div>
      )}

      {matches && matches.matches && matches.matches.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold mb-4">Top {matches.matches.length} Stylists</h2>
          <div className="space-y-6">
            {matches.matches.map((practitioner) => (
              <div key={practitioner.practitioner_id} className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="flex flex-col md:flex-row">
                  {/* Left: Photo & basic info */}
                  <div className="md:w-1/3 p-4 bg-gray-50 flex flex-col items-center text-center">
                    {practitioner.photo_url ? (
                      <img
                        src={practitioner.photo_url}
                        alt={practitioner.name}
                        className="w-32 h-32 rounded-full object-cover mb-3"
                      />
                    ) : (
                      <div className="w-32 h-32 rounded-full bg-gray-300 flex items-center justify-center text-gray-500 mb-3">
                        No Photo
                      </div>
                    )}
                    <h3 className="text-xl font-bold">{practitioner.name}</h3>
                    <p className="text-gray-600">{practitioner.specialty}</p>
                    <p className="text-sm text-gray-500">{practitioner.experience_years} years experience</p>
                    <div className="flex items-center mt-1">
                      <span className="text-yellow-500">★</span>
                      <span className="ml-1">{practitioner.rating}</span>
                    </div>
                    <p className="text-lg font-bold mt-2">${practitioner.price}</p>
                  </div>

                  {/* Right: Details, breakdown, slots */}
                  <div className="md:w-2/3 p-4">
                    <div className="mb-3">
                      <p className="text-sm text-gray-600">{practitioner.salon_name}</p>
                      {practitioner.bio && <p className="text-sm text-gray-700 mt-1">{practitioner.bio}</p>}
                    </div>

                    {/* Match Score */}
                    <div className="mb-3">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium">Match Score</span>
                        <span className="text-sm font-semibold">{practitioner.match_score}%</span>
                      </div>
                      <MatchScore score={practitioner.match_score} />
                    </div>

                    {/* Match Breakdown (as compact badges) */}
                    {practitioner.match_breakdown && (
                      <div className="flex flex-wrap gap-2 mb-3 text-xs">
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          Expertise: {practitioner.match_breakdown.expertise_match}%
                        </span>
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                          Rating: {Math.round(practitioner.match_breakdown.rating)}%
                        </span>
                        <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded">
                          Sentiment: {practitioner.match_breakdown.review_sentiment}%
                        </span>
                        <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded">
                          Workload: {practitioner.match_breakdown.workload_balance}%
                        </span>
                        {practitioner.match_breakdown.distance && (
                          <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded">
                            Distance: {Math.round(practitioner.match_breakdown.distance)}m
                          </span>
                        )}
                      </div>
                    )}

                    {/* Explanation */}
                    {practitioner.explanation && (
                      <p className="text-sm italic text-gray-600 mb-3">💡 {practitioner.explanation}</p>
                    )}

                    {/* Available Slots with Show All */}
                    {practitioner.available_slots && practitioner.available_slots.length > 0 && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Available Slots (click to book):
                        </label>
                        <div className="flex flex-wrap gap-2">
                          {(expandedSlots[practitioner.practitioner_id]
                            ? practitioner.available_slots
                            : practitioner.available_slots.slice(0, 6)
                          ).map((slot) => (
                            <button
                              key={slot}
                              onClick={() => handleSlotClick(practitioner, slot)}
                              className="bg-pink-100 text-pink-800 px-3 py-1 rounded-md text-sm hover:bg-pink-200"
                            >
                              {new Date(slot).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </button>
                          ))}
                        </div>
                        {practitioner.available_slots.length > 6 && (
                          <button
                            onClick={() => toggleShowAllSlots(practitioner.practitioner_id)}
                            className="text-sm text-blue-600 hover:underline mt-2"
                          >
                            {expandedSlots[practitioner.practitioner_id] ? 'Show less' : `Show all ${practitioner.available_slots.length} slots`}
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Booking Modal */}
      {modalOpen && selectedPractitioner && (
        <BookingModal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          practitioner={selectedPractitioner}
          selectedSlot={selectedSlot}
          onBookingSuccess={handleBookingSuccess}
        />
      )}
    </div>
  )
}