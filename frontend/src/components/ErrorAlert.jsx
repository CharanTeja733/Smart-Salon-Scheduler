import { useEffect } from 'react'

export default function ErrorAlert({ message, onDismiss }) {
  if (!message) return null
  useEffect(() => {
    if (message) {
      const timer = setTimeout(onDismiss, 5000)
      return () => clearTimeout(timer)
    }
  }, [message, onDismiss])
  return (
    <div className="rounded-md bg-red-50 p-4 mb-4 border border-red-200">
      <div className="flex">
        <div className="flex-shrink-0">⚠️</div>
        <div className="ml-3">
          <p className="text-sm text-red-700">{message}</p>
        </div>
        {onDismiss && (
          <button onClick={onDismiss} className="ml-auto text-red-500 hover:text-red-700">
            ✕
          </button>
        )}
      </div>
    </div>
  )
}