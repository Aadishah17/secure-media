import { useEffect, useRef, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'

const emptyResult = {
  similarity: null,
  duplicate: null,
  owner: 'Unverified',
  blockchain_verified: false
}

function formatFileSize(bytes) {
  if (!bytes) return '0 KB'
  const kilobytes = bytes / 1024
  if (kilobytes < 1024) return `${kilobytes.toFixed(1)} KB`
  return `${(kilobytes / 1024).toFixed(1)} MB`
}

function StatusPill({ tone, text }) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-semibold ${
        tone === 'positive'
          ? 'bg-emerald-100 text-emerald-800'
          : tone === 'negative'
            ? 'bg-rose-100 text-rose-800'
            : 'bg-slate-100 text-slate-700'
      }`}
    >
      <span
        className={`h-2.5 w-2.5 rounded-full ${
          tone === 'positive'
            ? 'bg-emerald-500'
            : tone === 'negative'
              ? 'bg-rose-500'
              : 'bg-slate-400'
        }`}
      />
      {text}
    </span>
  )
}

function ResultCard({ label, value, accent = 'text-slate-950' }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className={`mt-2 text-2xl font-semibold ${accent}`}>{value}</p>
    </div>
  )
}

export default function App() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [result, setResult] = useState(emptyResult)
  const [error, setError] = useState('')
  const abortRef = useRef(null)

  useEffect(() => {
    if (!file) {
      setPreviewUrl('')
      return undefined
    }

    const objectUrl = URL.createObjectURL(file)
    setPreviewUrl(objectUrl)

    return () => URL.revokeObjectURL(objectUrl)
  }, [file])

  useEffect(() => {
    return () => {
      abortRef.current?.abort()
    }
  }, [])

  function resetResult() {
    setResult(emptyResult)
    setError('')
  }

  function selectFile(nextFile) {
    if (!nextFile) return

    if (!nextFile.type.startsWith('image/')) {
      setFile(null)
      setError('Upload an image file to continue.')
      setResult(emptyResult)
      return
    }

    setFile(nextFile)
    resetResult()
  }

  function clearSelection() {
    abortRef.current?.abort()
    setFile(null)
    setIsUploading(false)
    resetResult()
  }

  async function analyzeFile() {
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    const controller = new AbortController()
    abortRef.current = controller
    setIsUploading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
        signal: controller.signal
      })
      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.error || 'Upload failed')
      }

      setResult(payload)
    } catch (requestError) {
      if (requestError.name !== 'AbortError') {
        setError(requestError.message || 'Upload failed')
        setResult(emptyResult)
      }
    } finally {
      setIsUploading(false)
      abortRef.current = null
    }
  }

  function handleDrop(event) {
    event.preventDefault()
    setIsDragging(false)
    selectFile(event.dataTransfer.files?.[0])
  }

  const similarityText =
    result.similarity === null ? '--' : `${Number(result.similarity).toFixed(1)}%`
  const duplicateText =
    result.duplicate === null ? 'Awaiting upload' : result.duplicate ? 'Duplicate' : 'Original'
  const verificationText = result.blockchain_verified ? 'Verified' : 'Not verified'

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_#eef6ff,_#f7f8fb_38%,_#ffffff_100%)] px-4 py-6 text-slate-900 sm:px-6 lg:px-8">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
        <header className="flex flex-col gap-4 border-b border-slate-200/80 pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div className="max-w-2xl">
            <p className="text-sm font-medium uppercase tracking-[0.16em] text-sky-700">
              SecureMedia AI
            </p>
            <h1 className="mt-3 text-3xl font-semibold text-slate-950 sm:text-4xl">
              Upload media
            </h1>
            <p className="mt-3 max-w-xl text-base leading-7 text-slate-600">
              Preview the image, send it to the Flask API, and review similarity,
              duplicate status, owner, and blockchain verification in one place.
            </p>
          </div>

          <StatusPill
            tone={result.duplicate === true ? 'negative' : 'positive'}
            text={result.duplicate === true ? 'Duplicate alert' : 'Ready for upload'}
          />
        </header>

        <section className="grid gap-5 lg:grid-cols-[minmax(0,1.15fr)_minmax(340px,0.85fr)]">
          <div
            className={`rounded-2xl border bg-white/95 p-5 shadow-sm backdrop-blur sm:p-6 ${
              isDragging ? 'border-sky-400 ring-4 ring-sky-100' : 'border-slate-200'
            }`}
            onDragEnter={(event) => {
              event.preventDefault()
              setIsDragging(true)
            }}
            onDragOver={(event) => event.preventDefault()}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
          >
            <div className="flex flex-col gap-5">
              <div>
                <h2 className="text-lg font-semibold text-slate-950">File upload</h2>
                <p className="mt-1 text-sm leading-6 text-slate-600">
                  Choose one image to run similarity, duplicate, and ownership checks.
                </p>
              </div>

              <label
                htmlFor="image-upload"
                className="flex min-h-72 cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center transition hover:border-slate-400 hover:bg-white focus-within:border-sky-500 focus-within:ring-4 focus-within:ring-sky-100"
              >
                <input
                  id="image-upload"
                  aria-label="Choose image"
                  className="sr-only"
                  type="file"
                  accept="image/*"
                  onChange={(event) => selectFile(event.target.files?.[0])}
                />

                {file && previewUrl ? (
                  <img
                    className="max-h-80 w-full max-w-xl rounded-xl object-contain"
                    src={previewUrl}
                    alt={`Preview of ${file.name}`}
                  />
                ) : (
                  <div className="flex max-w-md flex-col items-center gap-3">
                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-3xl text-slate-600 shadow-sm">
                      +
                    </div>
                    <div>
                      <p className="text-base font-semibold text-slate-900">Choose image</p>
                      <p className="mt-1 text-sm leading-6 text-slate-500">
                        PNG, JPG, WEBP, or GIF files work best for secure-media checks.
                      </p>
                    </div>
                  </div>
                )}
              </label>

              {error ? (
                <p className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">
                  {error}
                </p>
              ) : null}

              {result.duplicate === true ? (
                <p className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">
                  Duplicate detected. Review ownership and similarity before proceeding.
                </p>
              ) : null}

              <div className="flex flex-col gap-3 border-t border-slate-200 pt-5 sm:flex-row sm:items-center sm:justify-between">
                <div className="min-h-11">
                  {file ? (
                    <>
                      <p className="break-all text-sm font-semibold text-slate-900">{file.name}</p>
                      <p className="mt-1 text-sm text-slate-500">{formatFileSize(file.size)}</p>
                    </>
                  ) : (
                    <p className="text-sm text-slate-500">No image selected.</p>
                  )}
                </div>

                <div className="flex flex-col gap-2 sm:flex-row">
                  <button
                    className="rounded-xl border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 focus:outline-none focus:ring-4 focus:ring-slate-200 disabled:cursor-not-allowed disabled:opacity-45"
                    type="button"
                    onClick={clearSelection}
                    disabled={!file && !error}
                  >
                    Clear selection
                  </button>
                  <button
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 focus:outline-none focus:ring-4 focus:ring-slate-300 disabled:cursor-not-allowed disabled:bg-slate-300"
                    type="button"
                    onClick={analyzeFile}
                    disabled={!file || isUploading}
                  >
                    {isUploading ? (
                      <>
                        <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                        Uploading image
                      </>
                    ) : (
                      'Analyze image'
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <aside className="rounded-2xl border border-slate-200 bg-white/95 p-5 shadow-sm backdrop-blur sm:p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-slate-950">Result</h2>
                <p className="mt-1 text-sm leading-6 text-slate-600">
                  Similarity, duplicate state, owner, and blockchain verification.
                </p>
              </div>
              <StatusPill
                tone={
                  result.blockchain_verified
                    ? 'positive'
                    : result.duplicate === true
                      ? 'negative'
                      : 'neutral'
                }
                text={verificationText}
              />
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <ResultCard label="Similarity" value={similarityText} accent="text-sky-700" />
              <ResultCard
                label="Duplicate status"
                value={duplicateText}
                accent={result.duplicate ? 'text-rose-700' : 'text-emerald-700'}
              />
              <ResultCard label="Owner" value={result.owner || 'Unverified'} />
              <ResultCard
                label="Blockchain"
                value={verificationText}
                accent={result.blockchain_verified ? 'text-emerald-700' : 'text-rose-700'}
              />
            </div>
          </aside>
        </section>
      </div>
    </main>
  )
}
