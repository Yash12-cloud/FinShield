import { useRef, useState } from 'react'
import { LOCALES, strings, Locale } from './i18n/translations'

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
  verified_information: { label: string; source?: string }[]
  regulatory_claims: RegulatoryClaim[]
  registration_claims: RegClaim[]
  suspicious_links: { url: string; status: string }[]
  grievance_note: string
}

interface Assessment {
  steps: { label: string; detail: string; status: string }[]
  deterministic_categories: string[]
  mercury_source: string
  limitation: string
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
  assessment: Assessment
}

function severityDot(severity: string) {
  return severity === 'high' ? '🔴' : '🟠'
}

const SAFE_DO = [
  'Verify the organization independently',
  'Verify the claimed registration',
  'Check the destination website / domain',
  'Confirm information using an official source',
]
const SAFE_DO_NOT = [
  'Do not transfer money based only on this message',
  'Do not share OTPs',
  'Do not share passwords',
  'Do not share UPI PINs',
]

export default function App() {
  const [locale, setLocale] = useState<Locale>('en')
  const t = strings[locale]
  const [mode, setMode] = useState<Mode>('message')
  const [text, setText] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [ocrText, setOcrText] = useState('')
  const [ocrBusy, setOcrBusy] = useState(false)
  const [ocrDone, setOcrDone] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<Analysis | null>(null)
  const [showTransparency, setShowTransparency] = useState(false)
  const [speaking, setSpeaking] = useState(false)
  const fileInput = useRef<HTMLInputElement>(null)

  function pickFile(f: File | null) {
    setError('')
    setResult(null)
    setOcrDone(false)
    setOcrText('')
    setFile(f)
    if (f) void runOcr(f)
  }

  async function runOcr(f: File) {
    setOcrBusy(true)
    try {
      const form = new FormData()
      form.append('file', f)
      const res = await fetch(`${BACKEND_URL}/api/v1/extract/image`, {
        method: 'POST',
        body: form,
      })
      const data = await res.json()
      setOcrText(data.text || '')
      if (!data.ok) setError(t.ocrFailed)
      setOcrDone(true)
    } catch {
      setError(t.offline)
      setOcrDone(true)
    } finally {
      setOcrBusy(false)
    }
  }

  async function analyze() {
    setError('')
    setResult(null)
    setLoading(true)
    try {
      if (mode === 'screenshot') {
        const content = ocrText.trim()
        if (!content) {
          setError(t.emptyInput)
          return
        }
        const res = await fetch(`${BACKEND_URL}/api/v1/analyze/text`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: content, locale }),
        })
        if (!res.ok) throw new Error((await res.json()).detail ?? 'Analysis failed')
        setResult(await res.json())
      } else {
        if (!text.trim()) {
          setError(t.emptyInput)
          return
        }
        const endpoint =
          mode === 'message' ? '/api/v1/analyze/text' : '/api/v1/analyze/claim'
        const res = await fetch(`${BACKEND_URL}${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, locale }),
        })
        if (!res.ok) throw new Error((await res.json()).detail ?? 'Analysis failed')
        setResult(await res.json())
      }
    } catch (e: any) {
      setError(e?.message?.includes('fetch') ? t.offline : e.message ?? 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  function readAloud() {
    if (!result || !('speechSynthesis' in window)) return
    const synth = window.speechSynthesis
    if (speaking) {
      synth.cancel()
      setSpeaking(false)
      return
    }
    const utterance = new SpeechSynthesisUtterance(result.explanation)
    utterance.lang = locale === 'hi' ? 'hi-IN' : locale === 'mr' ? 'mr-IN' : 'en-IN'
    utterance.onend = () => setSpeaking(false)
    synth.speak(utterance)
    setSpeaking(true)
  }

  return (
    <div className="page">
      <header className="header">
        <div className="header-top">
          <div>
            <h1>FinShield</h1>
            <p className="tagline">{t.tagline}</p>
            <p className="tagline-sub">{t.taglineSub}</p>
          </div>
          <div className="langs" role="group" aria-label="Language">
            {LOCALES.map((l) => (
              <button
                key={l.code}
                className={`lang ${locale === l.code ? 'active' : ''}`}
                onClick={() => setLocale(l.code)}
              >
                {l.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="card">
        <div className="tabs">
          {(
            [
              ['message', t.modeMessage],
              ['claim', t.modeClaim],
              ['screenshot', t.modeScreenshot],
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
            placeholder={mode === 'message' ? t.placeholderMessage : t.placeholderClaim}
          />
        )}

        {mode === 'screenshot' && (
          <>
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
                if (f && /image\/(png|jpeg|jpg)/.test(f.type)) pickFile(f)
                else setError('Please drop a PNG or JPG image.')
              }}
              onClick={() => fileInput.current?.click()}
            >
              <p className="dropzone-title">{file ? file.name : t.dropTitle}</p>
              <p className="dropzone-sub">{file ? t.chooseDifferent : t.dropSub}</p>
              <input
                ref={fileInput}
                type="file"
                accept="image/png,image/jpeg"
                hidden
                onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
              />
            </div>

            {ocrBusy && <p className="muted">{t.analyzing}</p>}

            {ocrDone && (
              <div className="ocr-block">
                <label htmlFor="ocr">{t.extractedTitle}</label>
                <p className="muted">{t.extractedHint}</p>
                <textarea
                  id="ocr"
                  className="input"
                  rows={5}
                  value={ocrText}
                  onChange={(e) => setOcrText(e.target.value)}
                  placeholder={t.placeholderMessage}
                />
              </div>
            )}
          </>
        )}

        <button className="analyze" onClick={analyze} disabled={loading}>
          {loading ? t.analyzing : t.analyze}
        </button>
        {error && <p className="error">{error}</p>}

        {result && (
          <section className="result">
            <div className="result-head">
              <span className={`badge ${result.risk_level.toLowerCase()}`}>
                {result.risk_level}
              </span>
              <span className="score">{t.riskCategories(result.risk_categories.length)}</span>
            </div>

            <h3>{t.whyFlagged}</h3>
            {result.risk_categories.length === 0 && <p>{t.noFlags}</p>}
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

            <h3>{t.beforeYouAct}</h3>
            <div className="act-grid">
              <div className="act-col do">
                <div className="act-head">{t.doThis}</div>
                <ul>
                  {SAFE_DO.map((s, i) => (
                    <li key={i}>✓ {s}</li>
                  ))}
                </ul>
              </div>
              <div className="act-col dont">
                <div className="act-head">{t.doNotThis}</div>
                <ul>
                  {SAFE_DO_NOT.map((s, i) => (
                    <li key={i}>✕ {s}</li>
                  ))}
                </ul>
              </div>
            </div>

            <h3>{t.whatToVerify}</h3>
            {result.evidence.registration_claims.map((r, i) => (
              <div key={`reg${i}`} className="verification-box">
                <div>
                  <strong>{t.registrationClaim}:</strong> {r.value}
                </div>
                <div>
                  <strong>{t.status}:</strong> ⚠️ {r.status}
                </div>
                <div>
                  <strong>{t.reason}:</strong> {r.reason}
                </div>
                <div>
                  <strong>{t.officialSource}:</strong> {r.official_source}
                </div>
              </div>
            ))}
            {result.evidence.regulatory_claims.map((r, i) => (
              <div key={`regc${i}`} className="verification-box">
                <div>
                  <strong>{t.claim}:</strong> {r.claim}
                </div>
                <div>
                  <strong>{t.status}:</strong> ⚠️ {r.status}
                </div>
                <p className="cat-explanation">{r.explanation}</p>
                <div>
                  <strong>{t.officialSource}:</strong> {r.official_source}
                </div>
              </div>
            ))}
            {result.evidence.registration_claims.length === 0 &&
              result.evidence.regulatory_claims.length === 0 && (
                <p className="muted">{t.noFlags}</p>
              )}

            <h3>{t.aiExplanation}</h3>
            <p>{result.explanation}</p>
            <button className="tts" onClick={readAloud}>
              🔊 {speaking ? t.stopReading : t.readAloud}
            </button>

            <h3>{t.evidence}</h3>
            <p className="muted">{t.signalsNote}</p>
            <ul>
              {result.evidence.signals.map((s, i) => (
                <li key={i}>
                  <strong>{s.label}</strong> — {s.assessment}. {s.evidence_status}
                </li>
              ))}
            </ul>

            <h4>{t.verifiedInfo}</h4>
            {result.evidence.verified_information.length === 0 ? (
              <p className="muted">{t.verifiedNone}</p>
            ) : (
              <ul>
                {result.evidence.verified_information.map((v, i) => (
                  <li key={i}>
                    <strong>{v.label}</strong>
                    {v.source ? ` — ${v.source}` : ''}
                  </li>
                ))}
              </ul>
            )}

            {result.evidence.suspicious_links.length > 0 && (
              <>
                <h4>{t.linksFound}</h4>
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

            <button
              className="transparency-toggle"
              onClick={() => setShowTransparency(!showTransparency)}
              aria-expanded={showTransparency}
            >
              {showTransparency ? '▾' : '▸'} {t.transparency}
            </button>
            {showTransparency && (
              <div className="transparency">
                <ol>
                  {result.assessment.steps.map((s, i) => (
                    <li key={i}>
                      <strong>{s.label}</strong> — {s.detail}
                    </li>
                  ))}
                </ol>
                <p className="muted">
                  {result.assessment.limitation}
                </p>
              </div>
            )}
          </section>
        )}
      </main>

      <p className="privacy">{t.privacy}</p>
      <footer className="footer">
        <strong>{t.important}:</strong> {t.limitation}
      </footer>
    </div>
  )
}