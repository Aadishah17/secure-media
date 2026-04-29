import { useEffect, useRef, useState } from 'react'
import { StatusPill } from './components/StatusPill'
import { ResultCard } from './components/ResultCard'
import { Uploader } from './components/Uploader'
import { requestAccount } from './lib/web3'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const HEALTHCHECK_PATH = import.meta.env.VITE_HEALTHCHECK_PATH || '/api/health'

const emptyResult = {
  similarity: null,
  duplicate: null,
  owner: 'Unverified',
  blockchain_verified: false
}

async function readResponsePayload(response) {
  if (typeof response.clone === 'function' && typeof response.json === 'function') {
    const cloned = response.clone()

    try {
      return await response.json()
    } catch {
      try {
        const text = await cloned.text()
        return text ? { error: text } : null
      } catch {
        return null
      }
    }
  }

  if (typeof response.json === 'function') {
    try {
      return await response.json()
    } catch {
      return null
    }
  }

  if (typeof response.text === 'function') {
    try {
      const text = await response.text()
      return text ? { error: text } : null
    } catch {
      return null
    }
  }

  return null
}

export default function App() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [backendReady, setBackendReady] = useState(null)
  const [result, setResult] = useState(emptyResult)
  const [error, setError] = useState('')
  const [walletAddress, setWalletAddress] = useState('')
  const [isConnecting, setIsConnecting] = useState(false)
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

  useEffect(() => {
    let isMounted = true

    async function probeBackend() {
      try {
        const response = await fetch(`${API_BASE_URL}${HEALTHCHECK_PATH}`)
        if (!isMounted) return
        setBackendReady(response.ok)
      } catch {
        if (!isMounted) return
        setBackendReady(false)
      }
    }

    probeBackend()

    return () => {
      isMounted = false
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
      const payload = await readResponsePayload(response)

      if (!response.ok) {
        throw new Error(payload?.error || 'Upload failed')
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

  async function connectWallet() {
    setIsConnecting(true)
    try {
      const address = await requestAccount()
      if (address) {
        setWalletAddress(address)
      } else {
        setError('Failed to connect wallet or no Web3 provider found.')
      }
    } catch (err) {
      setError('Error connecting wallet: ' + err.message)
    } finally {
      setIsConnecting(false)
    }
  }

  const similarityText =
    result.similarity === null ? '--' : `${Number(result.similarity).toFixed(1)}%`
  const duplicateText =
    result.duplicate === null ? 'Awaiting upload' : result.duplicate ? 'Duplicate' : 'Original'
  const verificationText = result.blockchain_verified ? 'Verified' : 'Not verified'
  const duplicateAccent =
    result.duplicate === null
      ? 'text-slate-700'
      : result.duplicate
        ? 'text-rose-700'
        : 'text-emerald-700'

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

          <div className="flex flex-col items-end gap-3">
            {walletAddress ? (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm border border-slate-200">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
              </span>
            ) : (
              <button
                onClick={connectWallet}
                disabled={isConnecting}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 focus:outline-none focus:ring-4 focus:ring-slate-200 disabled:opacity-50"
              >
                {isConnecting ? 'Connecting...' : 'Connect Wallet'}
              </button>
            )}

            <StatusPill
              tone={
                backendReady === false
                  ? 'negative'
                  : result.duplicate === null
                    ? 'neutral'
                    : result.duplicate
                      ? 'negative'
                      : 'positive'
              }
              text={
                backendReady === false
                  ? 'Backend unavailable'
                  : result.duplicate === null
                    ? 'Awaiting analysis'
                    : result.duplicate
                      ? 'Duplicate alert'
                      : 'Ready for upload'
              }
            />
          </div>
        </header>

        <section className="grid gap-5 lg:grid-cols-[minmax(0,1.15fr)_minmax(340px,0.85fr)]">
          <Uploader
            file={file}
            previewUrl={previewUrl}
            isDragging={isDragging}
            setIsDragging={setIsDragging}
            isUploading={isUploading}
            error={error}
            result={result}
            handleDrop={handleDrop}
            selectFile={selectFile}
            clearSelection={clearSelection}
            analyzeFile={analyzeFile}
          />

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
                accent={duplicateAccent}
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
