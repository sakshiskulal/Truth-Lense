import UploadForm from '../components/UploadForm'

const Upload = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Upload Media</h1>
        <p className="mt-2 text-gray-600">
          Upload images, videos, or audio files for verification
        </p>
      </div>
      <UploadForm />
    </div>
  )
}

export default Upload