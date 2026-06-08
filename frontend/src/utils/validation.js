// Validate E.164 phone number (e.g., +1234567890)
export const isValidE164Phone = (phone) => {
  const regex = /^\+\d{7,15}$/
  return regex.test(phone)
}

// Validate email (basic)
export const isValidEmail = (email) => {
  if (!email) return true // email is optional
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}