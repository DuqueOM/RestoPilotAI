'use client'

import axios from 'axios'
import { CheckCircle, FileSpreadsheet, Image, Loader2, Upload } from 'lucide-react'
import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface FileUploadProps {
  onSessionCreated: (id: string, data: any) => void
  onComplete: () => void
  sessionId: string | null
}

export default function FileUpload({ onSessionCreated, onComplete, sessionId }: FileUploadProps) {
  const [menuUploaded, setMenuUploaded] = useState(false)
  const [dishesUploaded, setDishesUploaded] = useState(false)
  const [salesUploaded, setSalesUploaded] = useState(false)
  const [isUploading, setIsUploading] = useState<string | null>(null)
  const [uploadResults, setUploadResults] = useState<any>({})

  const uploadMenu = async (file: File) => {
    setIsUploading('menu')
    const formData = new FormData()
    formData.append('file', file)
    if (sessionId) formData.append('session_id', sessionId)

    try {
      const res = await axios.post(`${API_URL}/api/v1/ingest/menu`, formData)
      onSessionCreated(res.data.session_id, res.data)
      setUploadResults((prev: any) => ({ ...prev, menu: res.data }))
      setMenuUploaded(true)
    } catch (err: any) {
      alert(`Menu upload failed: ${err.response?.data?.detail || err.message}`)
    } finally {
      setIsUploading(null)
    }
  }

  const uploadDishes = async (files: File[]) => {
    if (!sessionId) return alert('Please upload menu first')
    setIsUploading('dishes')
    const formData = new FormData()
    files.forEach(f => formData.append('files', f))
    formData.append('session_id', sessionId)

    try {
      const res = await axios.post(`${API_URL}/api/v1/ingest/dishes`, formData)
      setUploadResults((prev: any) => ({ ...prev, dishes: res.data }))
      setDishesUploaded(true)
    } catch (err: any) {
      alert(`Dish upload failed: ${err.response?.data?.detail || err.message}`)
    } finally {
      setIsUploading(null)
    }
  }

  const uploadSales = async (file: File) => {
    if (!sessionId) return alert('Please upload menu first')
    setIsUploading('sales')
    const formData = new FormData()
    formData.append('file', file)
    formData.append('session_id', sessionId)

    try {
      const res = await axios.post(`${API_URL}/api/v1/ingest/sales`, formData)
      setUploadResults((prev: any) => ({ ...prev, sales: res.data }))
      setSalesUploaded(true)
    } catch (err: any) {
      alert(`Sales upload failed: ${err.response?.data?.detail || err.message}`)
    } finally {
      setIsUploading(null)
    }
  }

  const MenuDropzone = () => {
    const onDrop = useCallback((files: File[]) => {
      if (files[0]) uploadMenu(files[0])
    }, [])
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      onDrop, accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] }, maxFiles: 1
    })

    return (
      <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
        isDragActive ? 'border-primary-500 bg-primary-50' : menuUploaded ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-primary-400'
      }`}>
        <input {...getInputProps()} />
        {isUploading === 'menu' ? (
          <Loader2 className="h-12 w-12 mx-auto text-primary-500 animate-spin" />
        ) : menuUploaded ? (
          <CheckCircle className="h-12 w-12 mx-auto text-green-500" />
        ) : (
          <Image className="h-12 w-12 mx-auto text-gray-400" />
        )}
        <p className="mt-4 font-medium">{menuUploaded ? 'Menu Uploaded!' : 'Upload Menu Image'}</p>
        <p className="text-sm text-gray-500 mt-1">
          {menuUploaded ? `${uploadResults.menu?.items_extracted || 0} items extracted` : 'Drop image or click to browse'}
        </p>
      </div>
    )
  }

  const DishesDropzone = () => {
    const onDrop = useCallback((files: File[]) => uploadDishes(files), [])
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      onDrop, accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] }, disabled: !sessionId
    })

    return (
      <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
        !sessionId ? 'opacity-50 cursor-not-allowed' : isDragActive ? 'border-primary-500 bg-primary-50' : dishesUploaded ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-primary-400'
      }`}>
        <input {...getInputProps()} />
        {isUploading === 'dishes' ? (
          <Loader2 className="h-12 w-12 mx-auto text-primary-500 animate-spin" />
        ) : dishesUploaded ? (
          <CheckCircle className="h-12 w-12 mx-auto text-green-500" />
        ) : (
          <Upload className="h-12 w-12 mx-auto text-gray-400" />
        )}
        <p className="mt-4 font-medium">{dishesUploaded ? 'Dishes Analyzed!' : 'Upload Dish Photos (Optional)'}</p>
        <p className="text-sm text-gray-500 mt-1">
          {dishesUploaded ? `${uploadResults.dishes?.images_analyzed || 0} images analyzed` : 'Multiple images allowed'}
        </p>
      </div>
    )
  }

  const SalesDropzone = () => {
    const onDrop = useCallback((files: File[]) => {
      if (files[0]) uploadSales(files[0])
    }, [])
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      onDrop, accept: { 'text/csv': ['.csv'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'] }, maxFiles: 1, disabled: !sessionId
    })

    return (
      <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
        !sessionId ? 'opacity-50 cursor-not-allowed' : isDragActive ? 'border-primary-500 bg-primary-50' : salesUploaded ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-primary-400'
      }`}>
        <input {...getInputProps()} />
        {isUploading === 'sales' ? (
          <Loader2 className="h-12 w-12 mx-auto text-primary-500 animate-spin" />
        ) : salesUploaded ? (
          <CheckCircle className="h-12 w-12 mx-auto text-green-500" />
        ) : (
          <FileSpreadsheet className="h-12 w-12 mx-auto text-gray-400" />
        )}
        <p className="mt-4 font-medium">{salesUploaded ? 'Sales Data Loaded!' : 'Upload Sales Data (CSV)'}</p>
        <p className="text-sm text-gray-500 mt-1">
          {salesUploaded ? `${uploadResults.sales?.records_imported || 0} records imported` : 'Columns: date, item_name, units_sold'}
        </p>
      </div>
    )
  }

  const canProceed = menuUploaded

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Upload Your Restaurant Data</h2>
        <p className="text-gray-600 mt-2">Start by uploading your menu image. Dish photos and sales data are optional but improve analysis.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MenuDropzone />
        <DishesDropzone />
        <SalesDropzone />
      </div>

      {canProceed && (
        <div className="text-center">
          <button onClick={onComplete} className="btn-primary px-8 py-3 text-lg">
            Continue to Analysis
          </button>
        </div>
      )}
    </div>
  )
}
