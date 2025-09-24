import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, ExternalLink, CheckCircle, XCircle, AlertTriangle, Clock, Cpu, Eye, Zap, FileImage, Activity } from 'lucide-react'
import TrustScoreChart from '../components/TrustScoreChart'
import { useAuth } from '../utils/auth'
import api from '../services/api'

const Result = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) {
      navigate('/login')
      return
    }

    const fetchResult = async () => {
      try {
        const data = await api.getResult(id)
        setResult(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchResult()
  }, [id, user, navigate])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error</h3>
        <p className="text-gray-600 mb-4">{error || 'Result not found'}</p>
        <button onClick={() => navigate('/')} className="btn-primary">
          Go Home
        </button>
      </div>
    )
  }

  const getVerdictIcon = (verdict) => {
    switch (verdict) {
      case 'Real':
        return <CheckCircle className="w-8 h-8 text-green-500" />
      case 'Fake':
        return <XCircle className="w-8 h-8 text-red-500" />
      default:
        return <AlertTriangle className="w-8 h-8 text-yellow-500" />
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

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const formatFeatureValue = (value, type) => {
    if (typeof value !== 'number') return 'N/A'
    
    switch (type) {
      case 'percentage':
        return `${(value * 100).toFixed(1)}%`
      case 'score':
        return value.toFixed(3)
      case 'time':
        return `${value.toFixed(2)}s`
      default:
        return value.toFixed(2)
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => navigate('/history')}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to History</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Result - Left Column */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card-elevated">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-4">
                {getVerdictIcon(result.verdict)}
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{result.file_name}</h1>
                  <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                    <span className="flex items-center space-x-1">
                      <FileImage className="w-4 h-4" />
                      <span>{result.file_type.toUpperCase()}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>{new Date(result.created_at).toLocaleDateString()}</span>
                    </span>
                    {result.processing_time && (
                      <span className="flex items-center space-x-1">
                        <Zap className="w-4 h-4" />
                        <span>{formatFeatureValue(result.processing_time, 'time')}</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <span className={`px-4 py-2 rounded-full text-lg font-medium ${getVerdictColor(result.verdict)}`}>
                {result.verdict}
              </span>
            </div>

            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-lg font-medium text-gray-700">Trust Score</span>
                <span className="text-4xl font-bold text-gray-900">{result.trust_score}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4 shadow-inner">
                <div 
                  className={`trust-score-bar ${
                    result.trust_score >= 70 ? 'bg-green-500' : 
                    result.trust_score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${result.trust_score}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Low Trust</span>
                <span>High Trust</span>
              </div>
            </div>

            {result.analysis.onchain_tx && (
              <div className="flex items-center space-x-2 text-blue-600 bg-blue-50 p-3 rounded-lg border border-blue-200">
                <ExternalLink className="w-5 h-5" />
                <a 
                  href={`https://mumbai.polygonscan.com/tx/${result.analysis.onchain_tx}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline font-medium"
                >
                  View on Blockchain
                </a>
              </div>
            )}
          </div>

          {/* Image Preview */}
          {result.file_url && result.file_type === 'image' && (
            <div className="card-elevated">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <FileImage className="w-5 h-5" />
                <span>Analyzed Image</span>
              </h3>
              <div className="relative">
                <img 
                  src={result.file_url} 
                  alt={result.file_name}
                  className="w-full h-auto max-h-96 object-contain rounded-lg border border-gray-200 shadow-sm"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
                <div className="hidden text-center py-8 text-gray-500">
                  <FileImage className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                  <p>Image preview not available</p>
                </div>
              </div>
            </div>
          )}

          {/* Detailed Analysis */}
          <div className="card-elevated">
            <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center space-x-2">
              <Activity className="w-5 h-5" />
              <span>Detailed Analysis</span>
            </h3>
            
            <div className="space-y-6">
              {/* AI Analysis */}
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <div className="flex items-center space-x-2 mb-3">
                  <Cpu className="w-5 h-5 text-blue-600" />
                  <h4 className="font-medium text-blue-900">AI Detection Analysis</h4>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-blue-700">
                      <span className="font-medium">Score:</span> {formatFeatureValue(result.analysis.ai_analysis?.score || 0, 'percentage')}
                    </p>
                    <p className="text-sm text-blue-700">
                      <span className="font-medium">Model:</span> {result.analysis.ai_analysis?.model || 'Lightweight CV Analysis'}
                    </p>
                  </div>
                  {result.analysis.features && (
                    <div className="space-y-1">
                      <p className="text-xs font-medium text-blue-800 mb-2">Technical Features:</p>
                      {result.analysis.features.edge_density !== undefined && (
                        <p className="text-xs text-blue-700">
                          Edge Density: {formatFeatureValue(result.analysis.features.edge_density, 'score')}
                        </p>
                      )}
                      {result.analysis.features.texture_variance !== undefined && (
                        <p className="text-xs text-blue-700">
                          Texture Variance: {formatFeatureValue(result.analysis.features.texture_variance, 'score')}
                        </p>
                      )}
                      {result.analysis.features.suspicious_score !== undefined && (
                        <p className="text-xs text-blue-700">
                          Suspicious Score: {formatFeatureValue(result.analysis.features.suspicious_score, 'score')}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Azure Analysis */}
              {/* <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                <div className="flex items-center space-x-2 mb-3">
                  <Eye className="w-5 h-5 text-green-600" />
                  <h4 className="font-medium text-green-900">Azure Analysis</h4>
                </div>
                {result.analysis.azure_checked ? (
                  <div className="space-y-2">
                    <p className="text-sm text-green-700">
                      <span className="font-medium">Score:</span> {formatFeatureValue(result.analysis.azure_analysis?.score || 0, 'percentage')}
                    </p>
                    <p className="text-sm text-green-700">
                      <span className="font-medium">Service:</span> {result.analysis.azure_analysis?.service || 'Azure Cognitive Services'}
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-green-600 italic">Azure analysis not available for this content</p>
                )}
              </div> */}

              {/* News Verification */}
              {/* <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                <div className="flex items-center space-x-2 mb-3">
                  <AlertTriangle className="w-5 h-5 text-yellow-600" />
                  <h4 className="font-medium text-yellow-900">News Verification</h4>
                </div>
                {result.analysis.news_checked ? (
                  <div className="space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <p className="text-sm text-yellow-700">
                        <span className="font-medium">Articles Found:</span> {result.analysis.news_analysis?.found ? 'Yes' : 'No'}
                      </p>
                      <p className="text-sm text-yellow-700">
                        <span className="font-medium">Count:</span> {result.analysis.news_analysis?.article_count || 0}
                      </p>
                    </div>
                    {result.analysis.news_analysis?.articles && result.analysis.news_analysis.articles.length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-yellow-800 mb-2">Related Articles:</p>
                        <div className="space-y-1">
                          {result.analysis.news_analysis.articles.slice(0, 3).map((article, index) => (
                            <a 
                              key={index}
                              href={article.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="block text-sm text-yellow-700 hover:text-yellow-900 hover:underline p-2 bg-yellow-100 rounded border border-yellow-200"
                            >
                              {article.title}
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-yellow-600 italic">News verification not available for this content</p>
                )}
              </div> */}
            </div>
          </div>

          {/* Anomalies Detection */}
          {result.analysis.anomalies && result.analysis.anomalies.length > 0 && (
            <div className="card-elevated">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-orange-500" />
                <span>Detected Anomalies</span>
                <span className="anomaly-badge bg-orange-100 text-orange-800 border-orange-200">
                  {result.analysis.anomalies.length}
                </span>
              </h3>
              <div className="space-y-3">
                {result.analysis.anomalies.map((anomaly, index) => (
                  <div 
                    key={index}
                    className={`analysis-card ${getSeverityColor(anomaly.severity)}`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-medium text-sm">{anomaly.type}</span>
                          <span className={`anomaly-badge ${getSeverityColor(anomaly.severity)}`}>
                            {anomaly.severity}
                          </span>
                        </div>
                        <p className="text-sm">{anomaly.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Chart - Right Column */}
        <div className="lg:col-span-1">
          <TrustScoreChart analysis={result.analysis} />
        </div>
      </div>
    </div>
  )
}

export default Result