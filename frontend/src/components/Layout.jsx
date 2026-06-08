import { Outlet, Link } from 'react-router-dom'

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="text-xl font-bold text-pink-600">
              ✂️ Salon Scheduler
            </Link>
            <Link
              to="/my-bookings"
              className="bg-pink-600 text-white px-4 py-2 rounded-md text-sm hover:bg-pink-700"
            >
              My Bookings
            </Link>
          </div>
        </div>
      </nav>
      <main className="py-8">
        <Outlet />
      </main>
    </div>
  )
}