export function formatDateTime(isoString) {
  const date = new Date(isoString)
  return date.toLocaleString()
}

export function formatTime(isoString) {
  const date = new Date(isoString)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export function formatDate(isoString) {
  const date = new Date(isoString)
  return date.toLocaleDateString()
}

export function validatePhone(phone) {
  const re = /^\+\d{1,15}$/
  return re.test(phone)
}

/**
 * Format distance in meters to human readable string
 * @param {number} meters
 * @returns {string}
 */
export const formatDistance = (meters) => {
  if (meters < 1000) return `${Math.round(meters)} m`
  return `${(meters / 1000).toFixed(1)} km`
}