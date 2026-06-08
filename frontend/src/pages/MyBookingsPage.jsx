import { useState } from "react";
import { Link } from "react-router-dom";
import {
  getCustomerAppointments,
  cancelBooking,
  rescheduleBooking,
  getWaitlistByPhone,   // <-- added missing import
} from "../api/client";
import PhoneInput from "../components/PhoneInput";
import Loader from "../components/Loader";
import ErrorAlert from "../components/ErrorAlert";
import RescheduleModal from "../components/RescheduleModal";
import ReviewModal from "../components/ReviewModal";

export default function MyBookingsPage() {
  const [phone, setPhone] = useState("");
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [submittingId, setSubmittingId] = useState(null);

  // Modal states
  const [rescheduleFor, setRescheduleFor] = useState(null);
  const [reviewFor, setReviewFor] = useState(null);

  // Waitlist states
  const [waitlistEntries, setWaitlistEntries] = useState([]);
  const [showWaitlist, setShowWaitlist] = useState(false);
  const [waitlistLoading, setWaitlistLoading] = useState(false);

  // Helper to refresh appointments after cancel/reschedule
  const refreshAppointments = async () => {
    if (!phone) return;
    try {
      const res = await getCustomerAppointments(phone);
      const appointmentsArray = Array.isArray(res.data) ? res.data : res.data.appointments || [];
      setAppointments(appointmentsArray);
    } catch (err) {
      // Silent fail – error already shown from search
    }
  };

  const fetchWaitlist = async (phoneNum) => {
    setWaitlistLoading(true);
    setError(null);
    try {
      const res = await getWaitlistByPhone(phoneNum);
      setWaitlistEntries(res.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch waitlist");
      setWaitlistEntries([]);
    } finally {
      setWaitlistLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!phone.match(/^\+\d{7,15}$/)) {
      setError("Enter a valid E.164 phone number (e.g., +1234567890)");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await getCustomerAppointments(phone);
      const appointmentsArray = Array.isArray(res.data) ? res.data : res.data.appointments || [];
      setAppointments(appointmentsArray);
    } catch (err) {
      setError(err.response?.data?.detail || "No bookings found for this number");
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (appointmentId) => {
    if (!confirm("Are you sure you want to cancel this appointment?")) return;
    setSubmittingId(appointmentId);
    try {
      await cancelBooking(appointmentId, "Cancelled by customer");
      await refreshAppointments();
    } catch (err) {
      setError(err.response?.data?.detail || "Cancellation failed");
    } finally {
      setSubmittingId(null);
    }
  };

  const handleReschedule = async (appointmentId, newSlot) => {
    await rescheduleBooking(appointmentId, newSlot);
    await refreshAppointments();
  };

  const toggleWaitlist = () => {
    const newShow = !showWaitlist;
    setShowWaitlist(newShow);
    if (newShow && phone) {
      fetchWaitlist(phone);
    }
  };

  const now = new Date();
  const upcoming = appointments.filter(
    (a) => new Date(a.start_time) > now && a.status !== "cancelled"
  );
  const past = appointments.filter(
    (a) => new Date(a.start_time) <= now || a.status === "cancelled"
  );

  // Waitlist display
  const renderWaitlist = () => {
    if (waitlistLoading) return <Loader />;
    if (!waitlistEntries.length)
      return <div className="text-center text-gray-500 py-8">No waitlist entries found.</div>;

    return (
      <div className="space-y-4">
        {waitlistEntries.map((entry) => (
          <div key={entry.id} className="bg-white rounded-lg shadow p-4">
            <p className="font-medium">{entry.practitioner_name}</p>
            <p className="text-sm text-gray-600">Service: {entry.preferred_service_type || "Any"}</p>
            {entry.preferred_date_start && (
              <p className="text-sm text-gray-600">
                Preferred: {new Date(entry.preferred_date_start).toLocaleDateString()}
                {entry.preferred_date_end && ` – ${new Date(entry.preferred_date_end).toLocaleDateString()}`}
              </p>
            )}
            <p className="text-sm text-gray-500 mt-1">
              Position: #{entry.position} • Status: {entry.status}
            </p>
            {entry.notified_at && (
              <p className="text-xs text-green-600">Notified on {new Date(entry.notified_at).toLocaleString()}</p>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center mb-6 gap-3 flex-wrap">
        <h1 className="text-3xl font-bold text-gray-900">My Bookings</h1>
        <div className="flex gap-2">
          <Link
            to="/"
            className="bg-pink-600 text-white px-4 py-2 rounded-md hover:bg-pink-700"
          >
            Find Salons
          </Link>
          <button
            onClick={toggleWaitlist}
            className="border border-pink-600 text-pink-600 px-4 py-2 rounded-md hover:bg-pink-50"
          >
            {showWaitlist ? "Show Bookings" : "My Waitlist"}
          </button>
        </div>
      </div>

      <form
        onSubmit={handleSearch}
        className="bg-white p-6 rounded-lg shadow-md mb-8"
      >
        <div className="flex gap-4 flex-col sm:flex-row">
          <div className="flex-1">
            <PhoneInput value={phone} onChange={setPhone} required />
          </div>
          <button
            type="submit"
            className="bg-pink-600 text-white px-6 py-2 rounded-md self-end hover:bg-pink-700"
          >
            Search
          </button>
        </div>
      </form>

      <ErrorAlert message={error} onDismiss={() => setError(null)} />

      {!showWaitlist ? (
        // Bookings view
        <>
          {loading && <Loader />}
          {!loading && appointments.length === 0 && phone && !error && (
            <div className="text-center text-gray-500 py-8">
              No bookings found for this number.
            </div>
          )}

          {/* Upcoming Appointments */}
          {upcoming.length > 0 && (
            <div className="mb-8">
              <h2 className="text-xl font-semibold mb-4">Upcoming Appointments</h2>
              <div className="space-y-4">
                {upcoming.map((app) => (
                  <div
                    key={app.id}
                    className="bg-white rounded-lg shadow p-4 flex justify-between items-center flex-wrap gap-3"
                  >
                    <div>
                      <p className="font-medium">{app.salon_name}</p>
                      <p className="text-gray-600">{app.practitioner_name}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(app.start_time).toLocaleString()}
                      </p>
                      <span className="inline-block px-2 py-1 text-xs rounded-full mt-1 bg-green-100 text-green-800">
                        {app.status}
                      </span>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setRescheduleFor(app)}
                        className="border border-blue-600 text-blue-600 px-3 py-1 rounded-md text-sm hover:bg-blue-50"
                      >
                        Reschedule
                      </button>
                      <button
                        onClick={() => handleCancel(app.id)}
                        disabled={submittingId === app.id}
                        className="text-red-600 border border-red-300 px-3 py-1 rounded-md text-sm hover:bg-red-50 disabled:opacity-50"
                      >
                        {submittingId === app.id ? "..." : "Cancel"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Past & Cancelled Appointments */}
          {past.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Past & Cancelled</h2>
              <div className="space-y-4">
                {past.map((app) => (
                  <div key={app.id} className="bg-gray-50 rounded-lg p-4 opacity-75">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{app.salon_name}</p>
                        <p className="text-gray-600">{app.practitioner_name}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(app.start_time).toLocaleString()}
                        </p>
                        <span className="inline-block px-2 py-1 text-xs rounded-full bg-gray-200 text-gray-700 mt-1">
                          {app.status}
                        </span>
                      </div>
                      {app.status === "completed" && (
                        <button
                          onClick={() => setReviewFor(app)}
                          className="border border-pink-600 text-pink-600 px-3 py-1 rounded-md text-sm hover:bg-pink-50"
                        >
                          Write a Review
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        // Waitlist view
        renderWaitlist()
      )}

      {/* Modals */}
      {rescheduleFor && (
        <RescheduleModal
          isOpen={!!rescheduleFor}
          onClose={() => setRescheduleFor(null)}
          appointment={rescheduleFor}
          onRescheduled={(newSlot) => handleReschedule(rescheduleFor.id, newSlot)}
        />
      )}
      {reviewFor && (
        <ReviewModal
          isOpen={!!reviewFor}
          onClose={() => setReviewFor(null)}
          appointment={reviewFor}
          onReviewSubmitted={() => {
            alert("Thank you for your review!");
          }}
        />
      )}
    </div>
  );
}