'use client'

import axios from 'axios'
import { AlertTriangle, CheckCircle, FileSpreadsheet, FileText, Image as ImageIcon, Info, Loader2, Mic, MicOff, Pause, Play, Trash2, X } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useDropzone } from 'react-dropzone'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface FileUploadProps {
  onSessionCreated: (id: string, data: any) => void
  onComplete: () => void
  sessionId: string | null
}

// Extract domain from URL for auto-label
const getDomainLabel = (url: string): string => {
  try {
    const domain = new URL(url).hostname.replace('www.', '')
    return domain.split('.')[0].charAt(0).toUpperCase() + domain.split('.')[0].slice(1)
  } catch {
    return 'Link'
  }
}

// Audio player component with play/delete
const AudioPlayer = ({ blob, onDelete, index }: { blob: Blob; onDelete: () => void; index: number }) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string>('')
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => {
    const url = URL.createObjectURL(blob)
    setAudioUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [blob])

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  return (
    <div className="flex items-center gap-2 bg-white rounded-lg px-2 py-1 border">
      <audio ref={audioRef} src={audioUrl} onEnded={() => setIsPlaying(false)} />
      <button onClick={togglePlay} className="p-1 hover:bg-gray-100 rounded">
        {isPlaying ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
      </button>
      <span className="text-xs text-gray-600">Recording {index + 1}</span>
      <button onClick={onDelete} className="p-1 hover:bg-red-100 rounded text-red-500">
        <Trash2 className="h-3 w-3" />
      </button>
    </div>
  )
}

export default function FileUpload({ onSessionCreated, onComplete, sessionId }: FileUploadProps) {
  // Upload states - separate for each type to allow simultaneous uploads
  const [salesUploaded, setSalesUploaded] = useState(false)
  const [menuUploaded, setMenuUploaded] = useState(false)
  const [mediaUploaded, setMediaUploaded] = useState(false)
  const [uploadingTypes, setUploadingTypes] = useState<Set<string>>(new Set())
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})
  const [uploadResults, setUploadResults] = useState<any>({})
  
  // Context state
  const [businessContext, setBusinessContext] = useState('')
  const [competitorContext, setCompetitorContext] = useState('')
  const [businessLinks, setBusinessLinks] = useState<string[]>([])
  const [competitorLinks, setCompetitorLinks] = useState<string[]>([])
  const [newBusinessLink, setNewBusinessLink] = useState('')
  const [newCompetitorLink, setNewCompetitorLink] = useState('')
  
  // Audio recording state
  const [isRecordingBusiness, setIsRecordingBusiness] = useState(false)
  const [isRecordingCompetitor, setIsRecordingCompetitor] = useState(false)
  const [businessAudios, setBusinessAudios] = useState<Blob[]>([])
  const [competitorAudios, setCompetitorAudios] = useState<Blob[]>([])
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  // Helper to start uploading a type
  const startUploading = (type: string) => {
    setUploadingTypes(prev => new Set(prev).add(type))
    setUploadProgress(prev => ({ ...prev, [type]: 0 }))
  }

  // Helper to stop uploading a type
  const stopUploading = (type: string) => {
    setUploadingTypes(prev => {
      const next = new Set(prev)
      next.delete(type)
      return next
    })
    setUploadProgress(prev => ({ ...prev, [type]: 100 }))
  }

  const uploadWithProgress = async (url: string, formData: FormData, type: string) => {
    return axios.post(url, formData, {
      onUploadProgress: (progressEvent) => {
        const percent = progressEvent.total 
          ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
          : 0
        setUploadProgress(prev => ({ ...prev, [type]: percent }))
      }
    })
  }

  const uploadSales = async (file: File) => {
    startUploading('sales')
    const formData = new FormData()
    formData.append('file', file)
    if (sessionId) formData.append('session_id', sessionId)

    try {
      const res = await uploadWithProgress(`${API_URL}/api/v1/ingest/sales`, formData, 'sales')
      if (!sessionId && res.data.session_id) {
        onSessionCreated(res.data.session_id, res.data)
      }
      setUploadResults((prev: any) => ({ ...prev, sales: res.data }))
      setSalesUploaded(true)
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message
      alert(`Sales upload failed: ${typeof msg === 'string' ? msg : JSON.stringify(msg)}`)
    } finally {
      stopUploading('sales')
    }
  }

  const uploadMenu = async (files: File[]) => {
    startUploading('menu')
    const formData = new FormData()
    files.forEach(f => formData.append('files', f))
    if (sessionId) formData.append('session_id', sessionId)

    try {
      const res = await uploadWithProgress(`${API_URL}/api/v1/ingest/menu`, formData, 'menu')
      if (!sessionId && res.data.session_id) {
        onSessionCreated(res.data.session_id, res.data)
      }
      setUploadResults((prev: any) => ({ ...prev, menu: res.data }))
      setMenuUploaded(true)
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message
      alert(`Menu upload failed: ${typeof msg === 'string' ? msg : JSON.stringify(msg)}`)
    } finally {
      stopUploading('menu')
    }
  }

  const uploadMedia = async (files: File[]) => {
    startUploading('media')
    const formData = new FormData()
    files.forEach(f => formData.append('files', f))
    if (sessionId) formData.append('session_id', sessionId)

    try {
      const res = await uploadWithProgress(`${API_URL}/api/v1/ingest/dishes`, formData, 'media')
      setUploadResults((prev: any) => ({ ...prev, media: res.data }))
      setMediaUploaded(true)
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message
      alert(`Media upload failed: ${typeof msg === 'string' ? msg : JSON.stringify(msg)}`)
    } finally {
      stopUploading('media')
    }
  }

  // Audio recording functions
  const startRecording = async (type: 'business' | 'competitor') => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
        stream.getTracks().forEach(track => track.stop())
        
        if (type === 'business') {
          setBusinessAudios(prev => [...prev, audioBlob])
        } else {
          setCompetitorAudios(prev => [...prev, audioBlob])
        }

        // Upload to backend
        if (sessionId) {
          const formData = new FormData()
          formData.append('file', audioBlob, `recording_${Date.now()}.webm`)
          formData.append('session_id', sessionId)
          formData.append('context_type', type)
          try {
            await axios.post(`${API_URL}/api/v1/ingest/audio`, formData)
          } catch (err) {
            console.error('Audio upload failed:', err)
          }
        }
      }

      mediaRecorder.start()
      if (type === 'business') setIsRecordingBusiness(true)
      else setIsRecordingCompetitor(true)
    } catch (err) {
      alert('Microphone access denied')
    }
  }

  const stopRecording = (type: 'business' | 'competitor') => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
    if (type === 'business') setIsRecordingBusiness(false)
    else setIsRecordingCompetitor(false)
  }

  const deleteAudio = (type: 'business' | 'competitor', index: number) => {
    if (type === 'business') {
      setBusinessAudios(prev => prev.filter((_, i) => i !== index))
    } else {
      setCompetitorAudios(prev => prev.filter((_, i) => i !== index))
    }
  }

  const addLink = (type: 'business' | 'competitor') => {
    const link = type === 'business' ? newBusinessLink : newCompetitorLink
    if (!link) return
    try {
      new URL(link)
      if (type === 'business') {
        setBusinessLinks(prev => [...prev, link])
        setNewBusinessLink('')
      } else {
        setCompetitorLinks(prev => [...prev, link])
        setNewCompetitorLink('')
      }
    } catch {
      alert('Please enter a valid URL')
    }
  }

  const removeLink = (type: 'business' | 'competitor', index: number) => {
    if (type === 'business') {
      setBusinessLinks(prev => prev.filter((_, i) => i !== index))
    } else {
      setCompetitorLinks(prev => prev.filter((_, i) => i !== index))
    }
  }

  // Dropzone components
  const SalesDropzone = () => {
    const onDrop = useCallback((files: File[]) => {
      if (files[0]) uploadSales(files[0])
    }, [sessionId])
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      onDrop, 
      accept: { 'text/csv': ['.csv'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'] }, 
      maxFiles: 1
    })
    const isLoading = uploadingTypes.has('sales')
    const salesResult = uploadResults.sales
    const warnings = salesResult?.warnings || []
    const capabilities = salesResult?.data_capabilities || {}

    return (
      <div className="space-y-3">
        <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
          isDragActive ? 'border-blue-500 bg-blue-50' : salesUploaded ? 'border-green-500 bg-green-50' : 'border-blue-300 hover:border-blue-400 bg-blue-50/30'
        }`}>
          <input {...getInputProps()} />
          <div className="relative">
            {isLoading ? (
              <>
                <Loader2 className="h-10 w-10 mx-auto text-blue-500 animate-spin" />
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full transition-all" style={{ width: `${uploadProgress.sales || 0}%` }} />
                </div>
                <p className="text-sm text-blue-600 mt-1">{uploadProgress.sales || 0}%</p>
              </>
            ) : salesUploaded ? (
              <CheckCircle className="h-10 w-10 mx-auto text-green-500" />
            ) : (
              <FileSpreadsheet className="h-10 w-10 mx-auto text-blue-500" />
            )}
          </div>
          <p className="mt-3 font-semibold text-sm">{salesUploaded ? 'Sales Data Loaded!' : 'Sales Data (Required)'}</p>
          <p className="text-xs text-gray-500 mt-1">
            {salesUploaded 
              ? `${salesResult?.records_imported || 0} records • ${salesResult?.unique_items || 0} items • ${salesResult?.days_span || 0} days` 
              : 'CSV: date, item_name, units_sold'}
          </p>
          {salesUploaded && salesResult?.date_range && (
            <p className="text-xs text-gray-400 mt-1">
              {salesResult.date_range.start} → {salesResult.date_range.end}
            </p>
          )}
          <span className="inline-block mt-2 px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full font-medium">Required</span>
        </div>
        
        {/* Data Validation Feedback */}
        {salesUploaded && (
          <div className="space-y-2">
            {/* Warnings */}
            {warnings.length > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-amber-500 mt-0.5 flex-shrink-0" />
                  <div className="text-xs text-amber-700 space-y-1">
                    {warnings.map((w: string, i: number) => (
                      <p key={i}>{w}</p>
                    ))}
                  </div>
                </div>
              </div>
            )}
            
            {/* Data Capabilities */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <Info className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                <div className="text-xs text-blue-700">
                  <p className="font-medium mb-1">Data Capabilities Detected:</p>
                  <div className="flex flex-wrap gap-1">
                    {capabilities.has_price && <span className="px-1.5 py-0.5 bg-green-100 text-green-700 rounded">✓ Price</span>}
                    {capabilities.has_cost && <span className="px-1.5 py-0.5 bg-green-100 text-green-700 rounded">✓ Cost</span>}
                    {capabilities.can_calculate_margin && <span className="px-1.5 py-0.5 bg-green-100 text-green-700 rounded">✓ Margin Analysis</span>}
                    {capabilities.has_category && <span className="px-1.5 py-0.5 bg-green-100 text-green-700 rounded">✓ Categories</span>}
                    {!capabilities.has_price && <span className="px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded">No Price</span>}
                    {!capabilities.has_cost && <span className="px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded">No Cost</span>}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Minimum Requirements Info */}
            <div className="text-xs text-gray-500 p-2 bg-gray-50 rounded-lg">
              <p className="font-medium">📋 Minimum Requirements for Full Analysis:</p>
              <ul className="mt-1 space-y-0.5 ml-4 list-disc">
                <li><strong>date</strong>, <strong>item_name</strong>, <strong>units_sold</strong> (required)</li>
                <li><strong>price</strong>, <strong>cost</strong> (for margin/profitability analysis)</li>
                <li><strong>categoria</strong> (for category breakdown)</li>
                <li>30+ days of data recommended for reliable BCG analysis</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    )
  }

  const MenuDropzone = () => {
    const onDrop = useCallback((files: File[]) => {
      if (files.length) uploadMenu(files)
    }, [sessionId])
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      onDrop, 
      accept: { 
        'application/pdf': ['.pdf'],
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png']
      },
      multiple: true
    })
    const isLoading = uploadingTypes.has('menu')

    return (
      <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
        isDragActive ? 'border-purple-500 bg-purple-50' : menuUploaded ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-purple-400'
      }`}>
        <input {...getInputProps()} />
        {isLoading ? (
          <>
            <Loader2 className="h-10 w-10 mx-auto text-purple-500 animate-spin" />
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div className="bg-purple-500 h-2 rounded-full transition-all" style={{ width: `${uploadProgress.menu || 0}%` }} />
            </div>
            <p className="text-sm text-purple-600 mt-1">{uploadProgress.menu || 0}%</p>
          </>
        ) : menuUploaded ? (
          <CheckCircle className="h-10 w-10 mx-auto text-green-500" />
        ) : (
          <FileText className="h-10 w-10 mx-auto text-gray-400" />
        )}
        <p className="mt-3 font-semibold text-sm">{menuUploaded ? 'Menu Uploaded!' : 'Menu PDF/Images'}</p>
        <p className="text-xs text-gray-500 mt-1">
          {menuUploaded ? `${uploadResults.menu?.items_extracted || 0} items` : 'Multiple files • Clear photos of menu'}
        </p>
        <p className="text-xs text-gray-400 mt-1">
          {!menuUploaded && 'Ideal: prices visible, good lighting'}
        </p>
        <span className="inline-block mt-2 px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">Optional</span>
      </div>
    )
  }

  // Combined Photos & Videos Dropzone
  const MediaDropzone = () => {
    const onDrop = useCallback((files: File[]) => uploadMedia(files), [sessionId])
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      onDrop, 
      accept: { 
        'image/*': ['.jpg', '.jpeg', '.png', '.webp'],
        'video/*': ['.mp4', '.mov', '.avi', '.webm']
      },
      multiple: true
    })
    const isLoading = uploadingTypes.has('media')

    return (
      <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
        isDragActive ? 'border-amber-500 bg-amber-50' : mediaUploaded ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-amber-400'
      }`}>
        <input {...getInputProps()} />
        {isLoading ? (
          <>
            <Loader2 className="h-10 w-10 mx-auto text-amber-500 animate-spin" />
            <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
              <div className="bg-amber-500 h-2 rounded-full transition-all" style={{ width: `${uploadProgress.media || 0}%` }} />
            </div>
            <p className="text-sm text-amber-600 mt-1">{uploadProgress.media || 0}%</p>
          </>
        ) : mediaUploaded ? (
          <CheckCircle className="h-10 w-10 mx-auto text-green-500" />
        ) : (
          <ImageIcon className="h-10 w-10 mx-auto text-gray-400" />
        )}
        <p className="mt-3 font-semibold text-sm">{mediaUploaded ? 'Media Uploaded!' : 'Photos & Videos'}</p>
        <p className="text-xs text-gray-500 mt-1">
          {mediaUploaded ? `${uploadResults.media?.images_analyzed || 0} files analyzed` : 'Dish photos, promo videos'}
        </p>
        <span className="inline-block mt-2 px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">Optional</span>
      </div>
    )
  }

  const canProceed = salesUploaded

  return (
    <div className="space-y-6">
      <div className="text-center mb-4">
        <h2 className="text-2xl font-bold text-gray-900">Upload Your Restaurant Data</h2>
        <p className="text-gray-600 mt-2">Sales data (CSV) is required. Other files enable advanced AI features.</p>
      </div>

      {/* Continue Button - Always visible, disabled until CSV uploaded */}
      <div className="text-center">
        <button 
          onClick={onComplete} 
          disabled={!canProceed}
          className={`px-8 py-3 text-lg font-semibold rounded-xl transition-all ${
            canProceed 
              ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl' 
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          {canProceed ? 'Continue to Analysis →' : 'Upload Sales CSV to Continue'}
        </button>
      </div>

      {/* Upload Panels - Sales takes full width on mobile, then 2-column layout */}
      <div className="space-y-4">
        {/* Sales CSV - Full width with validation info */}
        <SalesDropzone />
        
        {/* Optional uploads - Side by side */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <MenuDropzone />
          <MediaDropzone />
        </div>
      </div>

      {/* Context Panels */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Business Context */}
        <div className="bg-blue-50 rounded-xl p-5 border border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-3">Your Business Context</h3>
          <div className="relative">
            <textarea
              value={businessContext}
              onChange={(e) => setBusinessContext(e.target.value)}
              placeholder="Describe your restaurant, cuisine type, target customers..."
              className="w-full h-24 p-3 pr-12 rounded-lg border border-blue-200 text-sm resize-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
            />
            {/* Voice Recording - Icon only, inside text box */}
            <button
              onClick={() => isRecordingBusiness ? stopRecording('business') : startRecording('business')}
              className={`absolute right-2 top-2 p-2 rounded-lg transition-all ${
                isRecordingBusiness 
                  ? 'bg-red-500 text-white animate-pulse' 
                  : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
              }`}
              title={isRecordingBusiness ? 'Stop Recording' : 'Record Voice Note'}
            >
              {isRecordingBusiness ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
            </button>
          </div>
          
          {/* Audio recordings */}
          {businessAudios.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {businessAudios.map((blob, idx) => (
                <AudioPlayer key={idx} blob={blob} index={idx} onDelete={() => deleteAudio('business', idx)} />
              ))}
            </div>
          )}

          {/* Context Suggestions */}
          <div className="flex flex-wrap gap-2 mt-3">
            {['Family restaurant', 'Fast food', 'Fine dining', 'Weekday lunch crowd', 'Weekend dinners', 'Tourist area'].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => setBusinessContext(prev => prev ? `${prev}, ${suggestion.toLowerCase()}` : suggestion)}
                className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
              >
                + {suggestion}
              </button>
            ))}
          </div>

          {/* Links */}
          <div className="mt-3">
            <div className="flex gap-2">
              <input
                type="url"
                value={newBusinessLink}
                onChange={(e) => setNewBusinessLink(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addLink('business')}
                placeholder="Add link (website, social media...)"
                className="flex-1 px-3 py-2 rounded-lg border border-blue-200 text-sm"
              />
              <button onClick={() => addLink('business')} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium">
                Add
              </button>
            </div>
            {businessLinks.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {businessLinks.map((link, idx) => (
                  <span key={idx} className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                    {getDomainLabel(link)}
                    <button onClick={() => removeLink('business', idx)} className="hover:text-red-500">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Competitor Context */}
        <div className="bg-orange-50 rounded-xl p-5 border border-orange-200">
          <h3 className="font-semibold text-orange-900 mb-3">Competitor Context</h3>
          <div className="relative">
            <textarea
              value={competitorContext}
              onChange={(e) => setCompetitorContext(e.target.value)}
              placeholder="Describe your competitors, their strengths, pricing..."
              className="w-full h-24 p-3 pr-12 rounded-lg border border-orange-200 text-sm resize-none focus:ring-2 focus:ring-orange-400 focus:border-transparent"
            />
            {/* Voice Recording - Icon only, inside text box */}
            <button
              onClick={() => isRecordingCompetitor ? stopRecording('competitor') : startRecording('competitor')}
              className={`absolute right-2 top-2 p-2 rounded-lg transition-all ${
                isRecordingCompetitor 
                  ? 'bg-red-500 text-white animate-pulse' 
                  : 'bg-orange-100 text-orange-700 hover:bg-orange-200'
              }`}
              title={isRecordingCompetitor ? 'Stop Recording' : 'Record Voice Note'}
            >
              {isRecordingCompetitor ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
            </button>
          </div>
          
          {/* Audio recordings */}
          {competitorAudios.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {competitorAudios.map((blob, idx) => (
                <AudioPlayer key={idx} blob={blob} index={idx} onDelete={() => deleteAudio('competitor', idx)} />
              ))}
            </div>
          )}

          {/* Context Suggestions */}
          <div className="flex flex-wrap gap-2 mt-3">
            {['Lower prices', 'Better location', 'More variety', 'Faster service', 'Larger portions', 'Open late'].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => setCompetitorContext(prev => prev ? `${prev}, ${suggestion.toLowerCase()}` : suggestion)}
                className="px-2 py-1 text-xs bg-orange-100 text-orange-700 rounded-full hover:bg-orange-200 transition-colors"
              >
                + {suggestion}
              </button>
            ))}
          </div>

          {/* Links */}
          <div className="mt-3">
            <div className="flex gap-2">
              <input
                type="url"
                value={newCompetitorLink}
                onChange={(e) => setNewCompetitorLink(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addLink('competitor')}
                placeholder="Add competitor link..."
                className="flex-1 px-3 py-2 rounded-lg border border-orange-200 text-sm"
              />
              <button onClick={() => addLink('competitor')} className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 text-sm font-medium">
                Add
              </button>
            </div>
            {competitorLinks.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {competitorLinks.map((link, idx) => (
                  <span key={idx} className="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
                    {getDomainLabel(link)}
                    <button onClick={() => removeLink('competitor', idx)} className="hover:text-red-500">
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
