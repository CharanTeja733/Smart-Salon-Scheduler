import { format, addDays } from 'date-fns'

export default function DatePicker({ selectedDate, onSelect, minDate = new Date(), maxDays = 90 }) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const dates = []
  for (let i = 0; i <= maxDays; i++) {
    const d = addDays(today, i)
    dates.push(d)
  }

  return (
    <div className="mt-2">
      <label className="block text-sm font-medium text-gray-700 mb-1">Select Date</label>
      <div className="flex overflow-x-auto pb-2 gap-2">
        {dates.map((date) => {
          const isSelected = selectedDate && format(selectedDate, 'yyyy-MM-dd') === format(date, 'yyyy-MM-dd')
          return (
            <button
              key={date.toISOString()}
              onClick={() => onSelect(date)}
              className={`px-3 py-1 rounded-full border text-sm whitespace-nowrap ${
                isSelected
                  ? 'bg-pink-600 text-white border-pink-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-pink-400'
              }`}
            >
              {format(date, 'MMM d')}
            </button>
          )
        })}
      </div>
    </div>
  )
}