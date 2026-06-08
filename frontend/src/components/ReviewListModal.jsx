export default function ReviewListModal({ isOpen, onClose, practitioner, reviews, loading }) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md max-h-[80vh] flex flex-col">
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-bold">Reviews for {practitioner.name}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {loading && <p className="text-center text-gray-500">Loading reviews...</p>}
          {!loading && (!reviews || reviews.length === 0) && (
            <p className="text-center text-gray-500">No reviews yet.</p>
          )}
          {!loading && reviews && reviews.length > 0 && (
            <div className="space-y-4">
              {reviews.map((review, idx) => (
                <div key={idx} className="border-b pb-3">
                  <div className="flex items-center gap-2">
                    <div className="flex text-yellow-500">
                      {'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}
                    </div>
                    <span className="text-sm text-gray-500">
                      {review.customer_name || 'Anonymous'}
                    </span>
                  </div>
                  {review.comment && <p className="text-gray-700 mt-1">{review.comment}</p>}
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(review.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="p-3 border-t">
          <button
            onClick={onClose}
            className="w-full bg-gray-200 text-gray-800 py-2 rounded-md hover:bg-gray-300"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}