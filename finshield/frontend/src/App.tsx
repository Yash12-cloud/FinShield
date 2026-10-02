import { useRef, useState } from 'react'

const BACKEND_URL: string =
  (import.meta as any).env?.VITE_BACKEND_URL ?? 'http://localhost:8000'

type Mode = 'message' | 'claim' | 'screenshot'

interface RiskCategory {
  id: string
  label: string
  severity: string
  matches: string[]
  explanation: string
}

interface Signal {
  id: string
  label: string
  matches: string[]
  assessment: string
  explanation: string
  evidence_status: string
}

interface RegulatoryClaim {
  claim: string
  status: string
  official_source: string
  explanation: string
}

interface RegClaim {
  value: string
  status: string
  reason: string
  official_source: string
}

interface Evidence {
  signals: Signal[]
  regulatory_claims: RegulatoryClaim[]
  registration_claims: RegClaim[]
  suspicious_links: { url: string; status: string }[]
  grievance_note: string
}

interface Analysis {
  risk_level: string
  content_type: string
  severity: string
  requires_verification: boolean
  risk_categories: RiskCategory[]
  mercury: Record<string, unknown>
  evidence: Evidence
  explanation: string
  verification_steps: string[]
  safe_next_steps: string[]
  uncertainty: string
}

function severityDot(severity: string) {
  return severity === 'high' ? '🔴' : '🟡'
}

export default function App() {
  const [mode, setMode] = useState<Mode>('message')
  const [text, setText] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<Analysis | null>(null)
  const fileInput = useRef<HTMLInputElement>(null)

  async function analyze() {
    setError('')
    setResult(null)
    setLoading(true)
    try {
      if (mode === 'screenshot') {
        if (!file) {
          setError('Please upload or drop a screenshot first.')
          setLoading(false)
          return
        }
        const form = new FormData()
        form.append('file', file)
        const res = await fetch(`${BACKEND_URL}/api/v1/analyze/image`, {
          method: 'POST',
          body: form,
        })
        if (!res.ok) throw new Error((await res.json()).detail ?? 'Image analysis failed')
        setResult(await res.json())
      } else {
        if (!text.trim()) {
          setError('Please paste content before analyzing.')
          setLoading(false)
          return
        }
        const endpoint =
          mode === 'message' ? '/api/v1/analyze/text' : '/api/v1/analyze/claim'
        const res = await fetch(`${BACKEND_URL}${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text }),
        })
        if (!res.ok) throw new Error((await res.json()).detail ?? 'Analysis failed')
        setResult(await res.json())
      }
    } catch (e: any) {
      setError(e.message ?? 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="header">
        <h1>FinShield</h1>
        <p className="tagline">Don't trust. Verify.</p>
      </header>

      <main className="card">
        <div className="tabs">
          {(
            [
              ['message', 'Message'],
              ['claim', 'Financial Claim'],
              ['screenshot', 'Screenshot'],
            ] as [Mode, string][]
          ).map(([m, label]) => (
            <button
              key={m}
              className={`tab ${mode === m ? 'active' : ''}`}
              onClick={() => setMode(m)}
            >
              {label}
            </button>
          ))}
        </div>

        {mode !== 'screenshot' && (
          <textarea
            className="input"
            rows={7}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={
              mode === 'message'
                ? 'e.g. "SEBI APPROVED! Earn 30% guaranteed monthly. Join t.me/vip now." — paste the WhatsApp/Telegram/Instagram message here'
                : 'e.g. "This investment is guaranteed to double your money in 3 years." — paste the financial claim here'
            }
          />
        )}

        {mode === 'screenshot' && (
          <div
            className={`dropzone ${dragOver ? 'over' : ''}`}
            onDragOver={(e) => {
              e.preventDefault()
              setDragOver(true)
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault()
              setDragOver(false)
              const f = e.dataTransfer.files?.[0]
              if (f && /image\/(png|jpeg|jpg)/.test(f.type)) setFile(f)
              else setError('Please drop a PNG or JPG image.')
            }}
            onClick={() => fileInput.current?.click()}
          >
            <p className="dropzone-title">
              {file ? file.name : 'Drag & drop a screenshot here'}
            </p>
            <p className="dropzone-sub">
              {file
                ? 'Click to choose a different file'
                : 'or click to browse — PNG, JPG, JPEG'}
            </p>
            <input
              ref={fileInput}
              type="file"
              accept="image/png,image/jpeg"
              hidden
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </div>
        )}

        <button className="analyze" onClick={analyze} disabled={loading}>
          {loading ? 'Analyzing…' : 'ANALYZE'}
        </button>
        {error && <p className="error">{error}</p>}

        {result && (
          <section className="result">
            <div className="result-head">
              <span className={`badge ${result.risk_level.toLowerCase()}`}>
                {result.risk_level}
              </span>
              <span className="score">
                {result.risk_categories.length} risk categor
                {result.risk_categories.length === 1 ? 'y' : 'ies'} detected
              </span>
              <span className="content-type">{result.content_type}</span>
            </div>

            <h3>Why was this flagged?</h3>
            {result.risk_categories.length === 0 && (
              <p>No strong red flags detected.</p>
            )}
            <ul className="categories">
              {result.risk_categories.map((c) => (
                <li key={c.id}>
                  <div className="cat-title">
                    {severityDot(c.severity)} <strong>{c.label.toUpperCase()}</strong>
                  </div>
                  <div className="cat-matches">
                    {c.matches.map((m, i) => (
                      <span key={i} className="match-quote">
                        “{m}”
                      </span>
                    ))}
                  </div>
                  <p className="cat-explanation">{c.explanation}</p>
                </li>
              ))}
            </ul>

            <h3>Verification</h3>
            {result.evidence.registration_claims.map((r, i) => (
              <div key={i} className="verification-box">
                <div>
                  <strong>Registration claim:</strong> {r.value}
                </div>
                <div>
                  <strong>Status:</strong> ⚠️ {r.status}
                </div>
                <div>
                  <strong>Reason:</strong> {r.reason}
                </div>
                <div>
                  <strong>Official source:</strong> {r.official_source}
                </div>
              </div>
            ))}
            {result.evidence.regulatory_claims.map((r, i) => (
              <div key={i} className="verification-box">
                <div>
                  <strong>Claim:</strong> {r.claim}
                </div>
                <div>
                  <strong>Status:</strong> ⚠️ {r.status}
                </div>
                <p className="cat-explanation">{r.explanation}</p>
                <div>
                  <strong>Official source:</strong> {r.official_source}
                </div>
              </div>
            ))}
            {result.evidence.registration_claims.length === 0 &&
              result.evidence.regulatory_claims.length === 0 && (
                <p>No registration or regulatory claims found in this content.</p>
              )}

            <h3>Structured decision</h3>
            <pre className="json">{JSON.stringify(result.mercury, null, 2)}</pre>

            <h3>Why this matters</h3>
            <p>{result.explanation}</p>

            <h3>Verify before acting</h3>
            <ul>
              {result.verification_steps.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>

            <h3>Before you act</h3>
            <ul>
              {result.safe_next_steps.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>

            <h3>Evidence & signals</h3>
            <p className="muted">
              Pattern-based signals are indicators detected by rule matching — they are
              not independently verified evidence.
            </p>
            <ul>
              {result.evidence.signals.map((s, i) => (
                <li key={i}>
                  <strong>{s.label}</strong> — {s.assessment}. Matched:{' '}
                  {s.matches.map((m) => `"${m}"`).join(', ')}. {s.evidence_status}
                </li>
              ))}
            </ul>
            {result.evidence.suspicious_links.length > 0 && (
              <>
                <h4>Links found</h4>
                <ul>
                  {result.evidence.suspicious_links.map((l, i) => (
                    <li key={i}>
                      {l.url} — {l.status}
                    </li>
                  ))}
                </ul>
              </>
            )}
            <p className="muted">{result.evidence.grievance_note}</p>

            <p className="uncertainty">{result.uncertainty}</p>
          </section>
        )}
      </main>

      <footer className="footer">
        FinShield identifies risk indicators. It is not investment advice and does not
        store your content.
      </footer>
    </div>
  )
}
