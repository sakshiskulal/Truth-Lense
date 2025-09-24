import { CheckCircle, XCircle, AlertTriangle, ExternalLink } from 'lucide-react'

const ResultCard = ({ result }) => {
  const getVerdictIcon = (verdict) => {
    switch (verdict) {
      case 'Real':
        return <CheckCircle className="w-6 h-6 text-green-500" />
      case 'Fake':
        return <XCircle className="w-6 h-6 text-red-500" />
      default:
        return <AlertTriangle className="w-6 h-6 text-yellow-500" />
    }
  }

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'Real':
        return 'bg-green-100 text-green-800'
      case 'Fake':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-yellow-100 text-yellow-800'
    }
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          {getVerdictIcon(result.verdict)}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{result.file_name}</h3>
            <p className="text-sm text-gray-500">{result.file_type.toUpperCase()}</p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getVerdictColor(result.verdict)}`}>
          {result.verdict}
        </span>
      </div>

      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Trust Score</span>
          <span className="text-2xl font-bold text-gray-900">{result.trust_score}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full ${
              result.trust_score >= 70 ? 'bg-green-500' : 'bg-red-500'
            }`}
            style={{ width: `${result.trust_score}%` }}
          ></div>
        </div>
      </div>

      {result.onchain_tx && (
        <div className="flex items-center space-x-2 text-sm text-blue-600">
          <ExternalLink className="w-4 h-4" />
          <a 
            href={`https://mumbai.polygonscan.com/tx/${result.onchain_tx}`}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:underline"
          >
            View on Blockchain
          </a>
        </div>
      )}
    </div>
  )
}

export default ResultCard