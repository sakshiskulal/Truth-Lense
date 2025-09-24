import { useState } from 'react'
import { useAuth } from '../utils/auth'
import { useNavigate } from 'react-router-dom'
import { Upload, AlertCircle, X, FileImage } from 'lucide-react'
import api from '../services/api'

const UploadForm = () => {
  const [file, setFile] = useState(null)
  const [filePreview, setFilePreview] = useState(null)
  const [metadata, setMetadata] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { user } = useAuth()
  const navigate = useNavigate()

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/png', 'video/mp4', 'audio/mp3', 'audio/wav']
      if (!allowedTypes.includes(selectedFile.type)) {
        setError('Unsupported file type. Please upload JPG, PNG, MP4, MP3, or WAV files.')
        return
      }

      // Validate file size
      const maxSize = selectedFile.type.startsWith('image/') ? 6 * 1024 * 1024 : 
                     selectedFile.type.startsWith('video/') ? 50 * 1024 * 1024 : 
                     20 * 1024 * 1024
      
      if (selectedFile.size > maxSize) {
        setError(`File too large. Max size: ${maxSize / (1024 * 1024)}MB`)
        return
      }

      setFile(selectedFile)
      setError('')

      // Create preview for images
      if (selectedFile.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          setFilePreview(e.target.result)
        }
        reader.readAsDataURL(selectedFile)
      } else {
        setFilePreview(null)
      }
    }
  }

  const clearFile = () => {
    setFile(null)
    setFilePreview(null)
    setError('')
    // Reset the file input
    const fileInput = document.getElementById('file')
    if (fileInput) fileInput.value = ''
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return

    setError('')
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      if (metadata) {
        formData.append('metadata', metadata)
      }

      console.info('[UploadForm] submitting file', { name: file.name, type: file.type, size: file.size })
      const res = await api.uploadFile(file, metadata)
      console.info('[UploadForm] upload success', res)
      navigate(`/result/${res.result_id}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return (
      <div className="text-center">
        <p className="text-gray-600">Please log in to upload files.</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload Media for Verification</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center space-x-2">
              <AlertCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label htmlFor="file" className="block text-sm font-medium text-gray-700 mb-2">
              Select File
            </label>
            
            {!file ? (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-500 transition-colors">
                <input
                  type="file"
                  id="file"
                  onChange={handleFileChange}
                  accept="image/*,video/*,audio/*"
                  className="hidden"
                />
                <label htmlFor="file" className="cursor-pointer">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Click to select a file</p>
                  <p className="text-sm text-gray-500 mt-2">
                    Images: JPG, PNG (max 6MB) | Videos: MP4 (max 50MB) | Audio: MP3, WAV (max 20MB)
                  </p>
                </label>
              </div>
            ) : (
              <div className="space-y-4">
                {/* File Info */}
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <FileImage className="w-8 h-8 text-blue-500" />
                      <div>
                        <p className="font-medium text-gray-900">{file.name}</p>
                        <p className="text-sm text-gray-500">
                          {file.type} • {(file.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={clearFile}
                      className="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {/* Image Preview */}
                {filePreview && (
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Preview</h4>
                    <div className="relative">
                      <img 
                        src={filePreview} 
                        alt="Preview"
                        className="w-full h-auto max-h-64 object-contain rounded-lg border border-gray-100"
                      />
                    </div>
                  </div>
                )}

                {/* Option to select different file */}
                <div className="text-center">
                  <input
                    type="file"
                    id="file-change"
                    onChange={handleFileChange}
                    accept="image/*,video/*,audio/*"
                    className="hidden"
                  />
                  <label htmlFor="file-change" className="text-sm text-blue-600 hover:text-blue-800 cursor-pointer underline">
                    Choose a different file
                  </label>
                </div>
              </div>
            )}
          </div>

          <div>
            <label htmlFor="metadata" className="block text-sm font-medium text-gray-700">
              Additional Information (Optional)
            </label>
            <textarea
              id="metadata"
              value={metadata}
              onChange={(e) => setMetadata(e.target.value)}
              className="input-field mt-1"
              rows={3}
              placeholder="Describe the content or provide context..."
            />
          </div>

          <button
            type="submit"
            disabled={!file || loading}
            className="w-full btn-primary disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Upload and Analyze'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default UploadForm