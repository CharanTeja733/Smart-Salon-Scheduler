import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="text-center py-12">
      <h1 className="text-6xl font-bold text-gray-300">404</h1>
      <p className="text-xl text-gray-600 mt-4">Page not found</p>
      <Link to="/" className="mt-6 inline-block bg-pink-600 text-white px-4 py-2 rounded-md">
        Go Home
      </Link>
    </div>
  )
}