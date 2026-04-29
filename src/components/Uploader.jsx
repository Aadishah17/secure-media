export function formatFileSize(bytes) {
  if (!bytes) return '0 KB'
  const kilobytes = bytes / 1024
  if (kilobytes < 1024) return `${kilobytes.toFixed(1)} KB`
  return `${(kilobytes / 1024).toFixed(1)} MB`
}

export function Uploader({
  file,
  previewUrl,
  isDragging,
  setIsDragging,
  isUploading,
  error,
  result,
  handleDrop,
  selectFile,
  clearSelection,
  analyzeFile
}) {
  return (
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
  )
}
