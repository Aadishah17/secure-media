import { useEffect, useRef, useState } from 'react'

const idleResult = {
  status: 'Awaiting upload',
  similarity: '--',
  match: 'No file selected'
}

const readyResult = {
  status: 'Ready to analyze',
  similarity: 'Pending',
  match: 'Upload prepared'
}

const completedResult = {
  status: 'Original',
  similarity: '18%',
  match: 'No close match found'
}

function formatFileSize(bytes) {
  if (!bytes) return '0 KB'
  const kilobytes = bytes / 1024
  if (kilobytes < 1024) return `${kilobytes.toFixed(1)} KB`
  return `${(kilobytes / 1024).toFixed(1)} MB`
}

export default function App() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState(idleResult)
  const [error, setError] = useState('')
  const timerRef = useRef(null)

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
      if (timerRef.current) window.clearTimeout(timerRef.current)
    }
  }, [])

  function selectFile(nextFile) {
    if (!nextFile) return

    if (!nextFile.type.startsWith('image/')) {
      setError('Upload an image file to continue.')
      setFile(null)
      setResult(idleResult)
      return
    }

    setError('')
    setFile(nextFile)
    setResult(readyResult)
  }

  function clearSelection() {
    if (timerRef.current) window.clearTimeout(timerRef.current)
    setFile(null)
    setIsAnalyzing(false)
    setError('')
    setResult(idleResult)
  }

  function analyzeFile() {
    if (!file) return

    setIsAnalyzing(true)
    setResult({
      status: 'Analyzing',
      similarity: 'Checking',
      match: 'Comparing perceptual hash'
    })

    timerRef.current = window.setTimeout(() => {
      setIsAnalyzing(false)
      setResult(completedResult)
    }, 650)
  }

  function handleDrop(event) {
    event.preventDefault()
    setIsDragging(false)
    selectFile(event.dataTransfer.files?.[0])
  }

  const statusTone = result.status === 'Original' ? 'text-emerald-700' : 'text-slate-800'

  return (
    <main className="min-h-screen bg-[#f7f8fb] px-4 py-6 text-slate-900 sm:px-6 lg:px-8">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
        <header className="flex flex-col gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div className="max-w-2xl">
            <p className="text-sm font-medium uppercase tracking-[0.16em] text-slate-500">
              SecureMedia
            </p>
            <h1 className="mt-3 text-3xl font-semibold text-slate-950 sm:text-4xl">
              Upload media
            </h1>
            <p className="mt-3 max-w-xl text-base leading-7 text-slate-600">
              Prepare an image for duplicate checks with a quiet workspace, clear states,
              and room for the Flask API result.
            </p>
          </div>

          <div className="flex items-center gap-3 rounded-md border border-slate-200 bg-white px-4 py-3 shadow-sm">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" aria-hidden="true" />
            <span className="text-sm font-medium text-slate-700">Local preview mode</span>
          </div>
        </header>

        <section className="grid gap-5 lg:grid-cols-[minmax(0,1.3fr)_minmax(320px,0.7fr)]">
          <div
            className={`rounded-lg border bg-white p-4 shadow-sm transition sm:p-6 ${
              isDragging
                ? 'border-sky-400 ring-4 ring-sky-100'
                : 'border-slate-200'
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
                <h2 className="text-lg font-semibold text-slate-950">Image intake</h2>
                <p className="mt-1 text-sm leading-6 text-slate-600">
                  Drop a file here or choose an image from your device.
                </p>
              </div>

              <label
                htmlFor="image-upload"
                className="flex min-h-60 cursor-pointer flex-col items-center justify-center rounded-md border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center transition hover:border-slate-400 hover:bg-white focus-within:border-sky-500 focus-within:ring-4 focus-within:ring-sky-100"
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
                    className="max-h-72 w-full max-w-xl rounded-md object-contain"
                    src={previewUrl}
                    alt={`Preview of ${file.name}`}
                  />
                ) : (
                  <div className="flex max-w-md flex-col items-center gap-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-md bg-white text-2xl text-slate-600 shadow-sm">
                      +
                    </div>
                    <div>
                      <p className="text-base font-semibold text-slate-900">Choose image</p>
                      <p className="mt-1 text-sm leading-6 text-slate-500">
                        PNG, JPG, WEBP, or GIF files work best for preview.
                      </p>
                    </div>
                  </div>
                )}
              </label>

              {error ? (
                <p className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-medium text-rose-700">
                  {error}
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
                    className="rounded-md border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 focus:outline-none focus:ring-4 focus:ring-slate-200 disabled:cursor-not-allowed disabled:opacity-45"
                    type="button"
                    onClick={clearSelection}
                    disabled={!file && !error}
                  >
                    Clear selection
                  </button>
                  <button
                    className="rounded-md bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 focus:outline-none focus:ring-4 focus:ring-slate-300 disabled:cursor-not-allowed disabled:bg-slate-300"
                    type="button"
                    onClick={analyzeFile}
                    disabled={!file || isAnalyzing}
                  >
                    {isAnalyzing ? 'Analyzing...' : 'Analyze image'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <aside className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-slate-950">Result</h2>
                <p className="mt-1 text-sm leading-6 text-slate-600">
                  The final API response can replace this local preview state.
                </p>
              </div>
              <span className="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">
                JSON ready
              </span>
            </div>

            <dl className="mt-6 grid gap-4">
              <div className="border-b border-slate-200 pb-4">
                <dt className="text-sm font-medium text-slate-500">Status</dt>
                <dd className={`mt-1 text-2xl font-semibold ${statusTone}`}>{result.status}</dd>
              </div>
              <div className="border-b border-slate-200 pb-4">
                <dt className="text-sm font-medium text-slate-500">Similarity</dt>
                <dd className="mt-1 text-xl font-semibold text-slate-900">{result.similarity}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-slate-500">Best match</dt>
                <dd className="mt-1 break-words text-base font-semibold text-slate-900">
                  {result.match}
                </dd>
              </div>
            </dl>

            <div className="mt-6 rounded-md bg-slate-50 p-4">
              <p className="text-sm font-semibold text-slate-800">Expected API shape</p>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                hash, similarity, status, best_match, and matches can map directly
                into this result panel.
              </p>
            </div>
          </aside>
        </section>
      </div>
    </main>
  )
}
