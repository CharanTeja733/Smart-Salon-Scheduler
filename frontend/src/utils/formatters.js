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