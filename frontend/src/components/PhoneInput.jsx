import { useState } from 'react'

export default function PhoneInput({ value, onChange, error, required }) {
  const [touched, setTouched] = useState(false)
  const isValidE164 = (phone) => /^\+\d{7,15}$/.test(phone)

  const handleBlur = () => setTouched(true)
  const displayError = (touched || error) && value && !isValidE164(value)

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700">
        Phone {required && '*'}
      </label>
      <input
        type="tel"
        placeholder="+1234567890"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onBlur={handleBlur}
        className={`mt-1 block w-full rounded-md shadow-sm border ${
          displayError ? 'border-red-300' : 'border-gray-300'
        } px-3 py-2 focus:outline-none focus:ring-pink-500 focus:border-pink-500`}
      />
      {displayError && (
        <p className="mt-1 text-sm text-red-600">Enter E.164 format (e.g., +1234567890)</p>
      )}
    </div>
  )
}