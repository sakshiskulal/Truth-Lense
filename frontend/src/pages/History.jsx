import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../utils/auth'
import HistoryList from '../components/HistoryList'
import { Upload } from 'lucide-react'
import api from '../services/api'

const History = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) {
      navigate('/login')
      return
    }

    const fetchHistory = async () => {
      try {
        const data = await api.getHistory()
        setResults(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchHistory()
  }, [user, navigate])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Verification History</h1>
          <p className="mt-2 text-gray-600">
            View all your media verification results
          </p>
        </div>
        <button
          onClick={() => navigate('/upload')}
          className="btn-primary flex items-center space-x-2"
        >
          <Upload className="w-5 h-5" />
          <span>Upload New</span>
        </button>
      </div>

      {error ? (
        <div className="text-center py-12">
          <p className="text-red-600">{error}</p>
        </div>
      ) : (
        <HistoryList results={results} />
      )}
    </div>
  )
}

export default History