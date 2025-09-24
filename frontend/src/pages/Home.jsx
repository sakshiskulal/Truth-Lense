import { Link } from 'react-router-dom'
import { useAuth } from '../utils/auth'
import { Upload, Shield, BarChart3, Globe } from 'lucide-react'

const Home = () => {
  const { user } = useAuth()

  const features = [
    {
      icon: <Shield className="w-8 h-8 text-primary-600" />,
      title: "AI Detection",
      description: "Advanced machine learning models detect deepfakes and synthetic media"
    },
    {
      icon: <Globe className="w-8 h-8 text-primary-600" />,
      title: "News Verification",
      description: "Cross-reference content with news sources for additional verification"
    },
    {
      icon: <BarChart3 className="w-8 h-8 text-primary-600" />,
      title: "Trust Scoring",
      description: "Comprehensive trust score combining multiple verification methods"
    }
  ]

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
          TruthLens
        </h1>
        <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
          Verify the authenticity of images, videos, and audio files using AI detection, 
          Azure Cognitive Services, and blockchain verification.
        </p>
        <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
          {user ? (
            <Link to="/upload" className="btn-primary text-lg px-8 py-3">
              Start Verifying
            </Link>
          ) : (
            <div className="space-x-4">
              <Link to="/signup" className="btn-primary text-lg px-8 py-3">
                Get Started
              </Link>
              <Link to="/login" className="btn-secondary text-lg px-8 py-3">
                Sign In
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Features Section */}
      <div className="py-12">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900">How It Works</h2>
          <p className="mt-4 text-lg text-gray-600">
            Our multi-layered approach ensures accurate media verification
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="card text-center">
              <div className="flex justify-center mb-4">
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      {!user && (
        <div className="bg-primary-50 rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Ready to verify your media?
          </h2>
          <p className="text-gray-600 mb-6">
            Join thousands of users who trust TruthLens for media verification
          </p>
          <div className="space-x-4">
            <Link to="/signup" className="btn-primary text-lg px-8 py-3">
              Create Account
            </Link>
            <Link to="/login" className="btn-secondary text-lg px-8 py-3">
              Sign In
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

export default Home