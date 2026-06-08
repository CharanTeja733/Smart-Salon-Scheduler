// Format UTC date to local datetime string
export const formatLocalDateTime = (utcDateString) => {
  if (!utcDateString) return ''
  return new Date(utcDateString).toLocaleString()
}

// Format date to YYYY-MM-DD
export const formatDate = (date) => date.toISOString().split('T')[0]

// Generate array of dates from today to maxDays ahead
export const getDateRange = (startDate, maxDays = 90) => {
  const dates = []
  for (let i = 0; i <= maxDays; i++) {
    const d = new Date(startDate)
    d.setDate(startDate.getDate() + i)
    dates.push(d)
  }
  return dates
}