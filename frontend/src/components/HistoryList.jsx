import { Link } from 'react-router-dom'
import { File, Calendar, TrendingUp } from 'lucide-react'

const HistoryList = ({ results }) => {
  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'Real':
        return 'text-green-600'
      case 'Fake':
        return 'text-red-600'
      default:
        return 'text-yellow-600'
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (!results || results.length === 0) {
    return (
      <div className="text-center py-12">
        <File className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No verification history</h3>
        <p className="text-gray-500">Upload your first file to get started.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {results.map((result) => (
        <Link
          key={result.id}
          to={`/result/${result.id}`}
          className="block card hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                <File className="w-5 h-5 text-gray-600" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900">{result.file_name}</h3>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span className="flex items-center space-x-1">
                    <Calendar className="w-4 h-4" />
                    <span>{formatDate(result.created_at)}</span>
                  </span>
                  <span className="uppercase">{result.file_type}</span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-2 mb-1">
                <TrendingUp className="w-4 h-4 text-gray-400" />
                <span className="text-2xl font-bold text-gray-900">{result.trust_score}%</span>
              </div>
              <span className={`text-sm font-medium ${getVerdictColor(result.verdict)}`}>
                {result.verdict}
              </span>
            </div>
          </div>
        </Link>
      ))}
    </div>
  )
}

export default HistoryList