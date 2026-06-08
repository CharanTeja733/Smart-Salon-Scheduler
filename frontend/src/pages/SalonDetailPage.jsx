import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getSalon, getAvailability } from '../api/client'
import DatePicker from '../components/DatePicker'
import TimeSlotGrid from '../components/TimeSlotGrid'
import { getPractitioner } from '../api/client'
import ReviewListModal from '../components/ReviewListModal'
import WaitlistModal from '../components/WaitlistModal'
import BookingModal from '../components/BookingModal'

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY
const PLACEHOLDER_IMAGE = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200"%3E%3Crect width="400" height="200" fill="%23f3f4f6"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af" font-family="sans-serif" font-size="16"%3ENo Image%3C/text%3E%3C/svg%3E'

export default function SalonDetailPage() {
  const { salonId } = useParams()
  const navigate = useNavigate()
  const [salon, setSalon] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [modalOpen, setModalOpen] = useState(false)
  const [selectedPractitioner, setSelectedPractitioner] = useState(null)
  const [preselectedSlot, setPreselectedSlot] = useState(null)

  // Reviews modal state
  const [reviewsForPractitioner, setReviewsForPractitioner] = useState(null)
  const [reviewsData, setReviewsData] = useState(null)
  const [reviewsLoading, setReviewsLoading] = useState(false)

  const [waitlistPractitioner, setWaitlistPractitioner] = useState(null)


  // State for inline slot picker (per practitioner)
  const [activePractitionerId, setActivePractitionerId] = useState(null)
  const [selectedDate, setSelectedDate] = useState(null)
  const [slots, setSlots] = useState([])
  const [selectedSlot, setSelectedSlot] = useState(null)
  const [fetchingSlots, setFetchingSlots] = useState(false)

  useEffect(() => {
    const fetchSalon = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await getSalon(salonId)
        setSalon(res.data)
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load salon details')
      } finally {
        setLoading(false)
      }
    }
    fetchSalon()
  }, [salonId])

  // When date changes for active practitioner, fetch slots
  useEffect(() => {
    if (!activePractitionerId || !selectedDate) {
      setSlots([])
      setSelectedSlot(null)
      return
    }
    const fetchSlotsForDate = async () => {
      setFetchingSlots(true)
      try {
        const dateStr = selectedDate.toISOString().split('T')[0]
        const res = await getAvailability(activePractitionerId, dateStr, 30)
        setSlots(res.data.available_slots || [])
        setSelectedSlot(null)
      } catch (err) {
        console.error('Failed to fetch slots', err)
        setSlots([])
      } finally {
        setFetchingSlots(false)
      }
    }
    fetchSlotsForDate()
  }, [activePractitionerId, selectedDate])

  const getSalonImage = () => {
    if (salon?.photo_reference) {
      return `https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference=${salon.photo_reference}&key=${GOOGLE_MAPS_API_KEY}`
    }
    return PLACEHOLDER_IMAGE
  }

  const formatOpeningHours = (hoursObj) => {
    if (!hoursObj) return null
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    const formatted = days
      .map(day => {
        const hours = hoursObj[day]
        if (hours && hours !== 'closed') {
          const dayName = day.charAt(0).toUpperCase() + day.slice(1)
          return `${dayName}: ${hours}`
        }
        return null
      })
      .filter(Boolean)
    return formatted.length ? formatted : null
  }

  const handleAvailableSlots = (practitioner) => {
    // Toggle slot picker for this practitioner
    if (activePractitionerId === practitioner.id) {
      // Close it
      setActivePractitionerId(null)
      setSelectedDate(null)
      setSlots([])
      setSelectedSlot(null)
    } else {
      // Open for this practitioner
      setActivePractitionerId(practitioner.id)
      setSelectedDate(null) // will trigger date picker to choose first
      setSlots([])
      setSelectedSlot(null)
    }
  }

  const handleSlotSelect = (practitioner, slotIso) => {
    setSelectedPractitioner(practitioner)
    setPreselectedSlot(slotIso)
    setModalOpen(true)
  }

  const handleBook = (practitioner) => {
    navigate(`/booking/${practitioner.id}`)
  }

  const handleWaitlist = (practitioner) => {
    setWaitlistPractitioner(practitioner)
    }

  const handleShowReviews = async (practitioner) => {
    setReviewsForPractitioner(practitioner)
    setReviewsLoading(true)
    try {
        const res = await getPractitioner(practitioner.id, true)
        setReviewsData(res.data.reviews || [])
    } catch (err) {
        console.error('Failed to fetch reviews', err)
        setReviewsData([])
    } finally {
        setReviewsLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-600"></div>
      </div>
    )
  }

  if (error || !salon) {
    return (
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error || 'Salon not found'}
        </div>
        <Link to="/" className="text-pink-600 hover:underline">← Back to Search</Link>
      </div>
    )
  }

  const openingHoursList = formatOpeningHours(salon.opening_hours)

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="mb-6">
        <Link to="/" className="text-pink-600 hover:text-pink-700">← Back to Search</Link>
      </div>

      {/* Salon Header */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden mb-8">
        <img
          src={getSalonImage()}
          alt={salon.name}
          className="w-full h-64 object-cover"
          onError={(e) => { e.target.src = PLACEHOLDER_IMAGE }}
        />
        <div className="p-6">
          <h1 className="text-3xl font-bold text-gray-900">{salon.name}</h1>
          <p className="text-gray-600 mt-1">{salon.address}</p>
          <div className="flex items-center mt-2">
            <span className="text-yellow-500">★</span>
            <span className="ml-1 text-sm">{salon.rating}</span>
            <span className="text-gray-400 text-sm ml-1">({salon.rating_count})</span>
          </div>
          {salon.phone && <p className="text-gray-600 text-sm mt-2">📞 {salon.phone}</p>}
        </div>
      </div>

      {/* Opening Hours */}
      {openingHoursList && openingHoursList.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-3">Opening Hours</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {openingHoursList.map((line, idx) => (
              <p key={idx} className="text-gray-600">{line}</p>
            ))}
          </div>
        </div>
      )}

      {/* Practitioners Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Our Stylists</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {salon.practitioners?.map((p) => (
            <div key={p.id} className="bg-white rounded-lg shadow-md overflow-hidden border">
              <div className="w-full h-48 overflow-hidden bg-gray-100">
                {p.photo_url ? (
                  <img src={p.photo_url} alt={p.name} className="w-full h-full object-cover" onError={(e) => { e.target.src = PLACEHOLDER_IMAGE }} />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-500">No Photo</div>
                )}
              </div>
              <div className="p-4">
                <h3 className="text-xl font-semibold">{p.name}</h3>
                <p className="text-gray-600 text-sm">{p.specialty || 'Stylist'}</p>
                <div className="flex items-center mt-1">
                  <span className="text-yellow-500">★</span>
                  <span className="ml-1 text-sm">{p.rating || 'New'}</span>
                </div>
                <p className="text-lg font-bold mt-2">${p.base_price}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    onClick={() => handleAvailableSlots(p)}
                    className={`flex-1 px-3 py-1 rounded-md text-sm ${
                      activePractitionerId === p.id
                        ? 'bg-pink-600 text-white'
                        : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                    }`}
                  >
                    {activePractitionerId === p.id ? 'Hide Slots' : 'Available Slots'}
                  </button>
                  <button
                    onClick={() => handleBook(p)}
                    className="flex-1 bg-pink-600 text-white px-3 py-1 rounded-md text-sm hover:bg-pink-700"
                  >
                    Book
                  </button>
                  <button
                    onClick={() => handleWaitlist(p)}
                    className="flex-1 border border-pink-600 text-pink-600 px-3 py-1 rounded-md text-sm hover:bg-pink-50"
                  >
                    Waitlist
                  </button>
                  <button
                    onClick={() => handleShowReviews(p)}
                    className="w-full mt-2 text-sm text-pink-600 hover:underline"
                    >
                    Show Reviews
                  </button>
                </div>

                {/* Inline slot picker for this practitioner */}
                {activePractitionerId === p.id && (
                  <div className="mt-4 border-t pt-3">
                    <DatePicker
                      selectedDate={selectedDate}
                      onSelect={setSelectedDate}
                    />
                    {fetchingSlots && <p className="text-gray-500 text-sm mt-2">Loading slots...</p>}
                    {!fetchingSlots && selectedDate && (
                      <TimeSlotGrid
                        slots={slots}
                        selectedSlot={selectedSlot}
                        onSelect={(slotIso) => handleSlotSelect(p, slotIso)}
                      />
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
        {modalOpen && selectedPractitioner && (
            <BookingModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                practitioner={selectedPractitioner}
                selectedSlot={preselectedSlot}
                onBookingSuccess={(appointmentId) => {
                setModalOpen(false)
                window.location.href = `/confirmation/${appointmentId}`
                }}
            />
        )}

        {reviewsForPractitioner && (
            <ReviewListModal
                isOpen={!!reviewsForPractitioner}
                onClose={() => {
                setReviewsForPractitioner(null)
                setReviewsData(null)
                }}
                practitioner={reviewsForPractitioner}
                reviews={reviewsData}
                loading={reviewsLoading}
            />
        )}

        {waitlistPractitioner && (
            <WaitlistModal
                isOpen={!!waitlistPractitioner}
                onClose={() => setWaitlistPractitioner(null)}
                practitioner={waitlistPractitioner}
            />
        )}
    </div>
  )
}