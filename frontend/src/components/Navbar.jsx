import { Link } from 'react-router-dom'
import { useAuth } from '../utils/auth'

const Navbar = () => {
  const { user, logout } = useAuth()

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-900">
              TruthLens
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <Link to="/upload" className="text-gray-700 hover:text-primary-600">
                  Upload
                </Link>
                <Link to="/history" className="text-gray-700 hover:text-primary-600">
                  History
                </Link>
                <span className="text-sm text-gray-700">{user.email}</span>
                <button onClick={logout} className="text-gray-700 hover:text-primary-600">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-gray-700 hover:text-primary-600">
                  Login
                </Link>
                <Link to="/signup" className="btn-primary">
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar