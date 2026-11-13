import { useRef, useState } from 'react'
import type { ChangeEvent, DragEvent, FormEvent } from 'react'
import './App.css'

type UploadResult = {
  statement_id: number
  filename: string
  transaction_count: number
  classified_count: number
  unclassified_count: number
  unclassified_output: string
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function App() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<UploadResult | null>(null)

  const chooseFile = (nextFile?: File) => {
    setError('')
    setResult(null)

    if (!nextFile) return
    if (!nextFile.name.toLowerCase().endsWith('.csv')) {
      setFile(null)
      setError('Please choose a CSV statement.')
      return
    }

    setFile(nextFile)
  }

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    chooseFile(event.target.files?.[0])
  }

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragging(false)
    chooseFile(event.dataTransfer.files[0])
  }

  const clearFile = () => {
    setFile(null)
    setResult(null)
    setError('')
    if (inputRef.current) inputRef.current.value = ''
  }

  const uploadStatement = async (event: FormEvent) => {
    event.preventDefault()
    if (!file || isUploading) return

    setIsUploading(true)
    setError('')
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/statements/upload', {
        method: 'POST',
        body: formData,
      })
      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.detail || 'The statement could not be uploaded.')
      }

      setResult(payload as UploadResult)
    } catch (uploadError) {
      setError(
        uploadError instanceof Error
          ? uploadError.message
          : 'The statement could not be uploaded.',
      )
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <main className="page-shell">
      <nav className="topbar" aria-label="Primary navigation">
        <a className="brand" href="/" aria-label="Ledger home">
          <span className="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 24 24">
              <path d="M5 4.5h14v15H5zM9 8h6M9 12h6M9 16h3" />
            </svg>
          </span>
          <span>Ledger</span>
        </a>
        <span className="environment"><i /> Development</span>
      </nav>

      <section className="content">
        <header className="intro">
          <span className="eyebrow">Statements</span>
          <h1>Import a bank statement</h1>
          <p>
            Upload a CSV and we’ll store its transactions, match known merchants,
            and flag anything that needs your review.
          </p>
        </header>

        <form className="upload-card" onSubmit={uploadStatement}>
          <div
            className={`drop-zone ${isDragging ? 'is-dragging' : ''} ${file ? 'has-file' : ''}`}
            onDragEnter={(event) => {
              event.preventDefault()
              setIsDragging(true)
            }}
            onDragOver={(event) => event.preventDefault()}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
          >
            <input
              ref={inputRef}
              id="statement-file"
              type="file"
              accept=".csv,text/csv"
              onChange={handleFileChange}
            />

            {file ? (
              <div className="selected-file">
                <span className="file-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path d="M7 3.5h7l4 4v13H7zM14 3.5v4h4M9.5 15.5l1.6 1.6 3.8-4" />
                  </svg>
                </span>
                <div>
                  <strong>{file.name}</strong>
                  <span>{formatBytes(file.size)} · CSV document</span>
                </div>
                <button className="remove-file" type="button" onClick={clearFile} aria-label="Remove file">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="m8 8 8 8M16 8l-8 8" />
                  </svg>
                </button>
              </div>
            ) : (
              <label htmlFor="statement-file">
                <span className="upload-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5M5 14v5h14v-5" />
                  </svg>
                </span>
                <strong>Drop your statement here</strong>
                <span>or <u>browse your files</u></span>
                <small>CSV files only</small>
              </label>
            )}
          </div>

          {error && (
            <div className="message error-message" role="alert">
              <span aria-hidden="true">!</span>
              {error}
            </div>
          )}

          {result && (
            <section className="result" aria-live="polite">
              <div className="result-heading">
                <span className="success-icon" aria-hidden="true">✓</span>
                <div>
                  <strong>Statement imported</strong>
                  <span>Statement #{result.statement_id} is ready to review.</span>
                </div>
              </div>
              <dl>
                <div><dt>Transactions</dt><dd>{result.transaction_count}</dd></div>
                <div><dt>Classified</dt><dd>{result.classified_count}</dd></div>
                <div><dt>Needs review</dt><dd>{result.unclassified_count}</dd></div>
              </dl>
              {result.unclassified_count > 0 && (
                <a className="download-link" href={result.unclassified_output}>
                  Download unclassified transactions
                  <span aria-hidden="true">↓</span>
                </a>
              )}
            </section>
          )}

          <button className="submit-button" type="submit" disabled={!file || isUploading}>
            {isUploading ? <><span className="spinner" /> Uploading…</> : 'Upload statement'}
          </button>
        </form>

        <aside className="format-note">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="12" r="9" />
            <path d="M12 11v5M12 8h.01" />
          </svg>
          <div>
            <strong>Expected columns</strong>
            <p><code>description</code>, <code>transaction_date</code>, and <code>amount</code>. Chase CSV exports are supported too.</p>
          </div>
        </aside>
      </section>
    </main>
  )
}

export default App
