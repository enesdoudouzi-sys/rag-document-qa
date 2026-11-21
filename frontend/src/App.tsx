import { useState } from 'react'

const API = import.meta.env.VITE_API_URL ? `https://${import.meta.env.VITE_API_URL}` : ''

type Nachricht = { rolle: 'user' | 'bot'; text: string; quellen?: string[] }

export default function App() {
  const [dateiname, setDateiname] = useState<string | null>(null)
  const [chunks, setChunks] = useState<number | null>(null)
  const [nachrichten, setNachrichten] = useState<Nachricht[]>([])
  const [frage, setFrage] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [fehler, setFehler] = useState<string | null>(null)

  async function hochladen(e: React.ChangeEvent<HTMLInputElement>) {
    const datei = e.target.files?.[0]
    if (!datei) return
    setUploading(true); setFehler(null)
    try {
      const form = new FormData()
      form.append('datei', datei)
      const res = await fetch(`${API}/dokument`, { method: 'POST', body: form })
      if (!res.ok) throw new Error((await res.json()).detail)
      const data = await res.json()
      setDateiname(data.dateiname); setChunks(data.chunks)
      setNachrichten([{ rolle: 'bot', text: `✅ "${data.dateiname}" geladen — ${data.chunks} Chunks indexiert. Stell mir eine Frage!` }])
    } catch (e) { setFehler(e instanceof Error ? e.message : 'Fehler') }
    finally { setUploading(false) }
  }

  async function abfragen() {
    if (!frage.trim() || loading) return
    const f = frage.trim(); setFrage('')
    setNachrichten(n => [...n, { rolle: 'user', text: f }])
    setLoading(true)
    try {
      const res = await fetch(`${API}/fragen`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ frage: f }),
      })
      if (!res.ok) throw new Error((await res.json()).detail)
      const data = await res.json()
      setNachrichten(n => [...n, { rolle: 'bot', text: data.antwort, quellen: data.quellen }])
    } catch (e) { setNachrichten(n => [...n, { rolle: 'bot', text: '⚠️ ' + (e instanceof Error ? e.message : 'Fehler') }]) }
    finally { setLoading(false) }
  }

  async function leeren() {
    await fetch(`${API}/dokumente`, { method: 'DELETE' })
    setDateiname(null); setChunks(null); setNachrichten([])
  }

  return (
    <div className="min-h-screen bg-[#0a0f1a] text-gray-100 flex flex-col items-center px-4 py-10">
      <div className="w-full max-w-2xl flex flex-col gap-6">

        {/* Header */}
        <div>
          <div className="text-xs font-mono text-cyan-400 tracking-widest uppercase mb-1">RAG · Document Q&A</div>
          <h1 className="text-2xl font-bold font-mono">Frag dein Dokument</h1>
          <p className="text-sm text-gray-500 mt-1">PDF oder Text hochladen — KI beantwortet deine Fragen auf Basis des Inhalts.</p>
        </div>

        {/* Upload */}
        <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono text-gray-500 uppercase tracking-wider">Dokument</span>
            {dateiname && (
              <button onClick={leeren} className="text-xs text-red-400 hover:text-red-300">✕ Leeren</button>
            )}
          </div>
          <label className="cursor-pointer">
            <input type="file" accept=".pdf,.txt,.md" className="hidden" onChange={hochladen} />
            <div className={`border-2 border-dashed rounded-lg p-5 text-center transition-colors ${
              dateiname ? 'border-cyan-500/40 bg-cyan-500/5' : 'border-gray-700 hover:border-gray-500'
            }`}>
              {uploading ? (
                <span className="text-sm text-cyan-400">⏳ Indexiere Dokument…</span>
              ) : dateiname ? (
                <div>
                  <div className="text-sm font-mono text-cyan-400">{dateiname}</div>
                  <div className="text-xs text-gray-500 mt-1">{chunks} Chunks indexiert</div>
                </div>
              ) : (
                <span className="text-sm text-gray-500">📎 PDF, TXT oder MD auswählen</span>
              )}
            </div>
          </label>
          {fehler && <p className="text-xs text-red-400">⚠️ {fehler}</p>}
        </div>

        {/* Chat */}
        {nachrichten.length > 0 && (
          <div className="bg-[#111827] border border-gray-800 rounded-xl p-4 flex flex-col gap-3 max-h-96 overflow-y-auto">
            {nachrichten.map((n, i) => (
              <div key={i} className={`flex flex-col gap-1 ${n.rolle === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`rounded-xl px-4 py-2.5 text-sm max-w-[85%] leading-relaxed ${
                  n.rolle === 'user'
                    ? 'bg-cyan-600 text-white'
                    : 'bg-[#1e293b] text-gray-200'
                }`}>
                  {n.text}
                </div>
                {n.quellen && n.quellen.length > 0 && (
                  <div className="flex gap-1 flex-wrap">
                    {n.quellen.map((q, j) => (
                      <span key={j} className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded font-mono">
                        📄 {q}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex items-start">
                <div className="bg-[#1e293b] rounded-xl px-4 py-2.5 text-sm text-cyan-400">
                  ⏳ Suche im Dokument…
                </div>
              </div>
            )}
          </div>
        )}

        {/* Input */}
        <div className="flex gap-2">
          <input
            value={frage}
            onChange={e => setFrage(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && abfragen()}
            placeholder={dateiname ? 'Frage stellen…' : 'Zuerst Dokument hochladen'}
            disabled={!dateiname || loading}
            className="flex-1 bg-[#111827] border border-gray-700 rounded-lg px-4 py-2.5 text-sm font-mono focus:outline-none focus:border-cyan-500 disabled:opacity-40 placeholder-gray-600"
          />
          <button
            onClick={abfragen}
            disabled={!dateiname || !frage.trim() || loading}
            className="px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 rounded-lg text-sm font-semibold transition-colors"
          >
            →
          </button>
        </div>

      </div>
    </div>
  )
}
