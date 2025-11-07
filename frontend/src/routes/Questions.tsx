import { useState } from 'react'
import { normalizeJob, generateShort } from '../api/client'
import { useAppStore } from '../store'

const QUESTIONS = [
  { key:'why_company', label:'Why you want to join our company?' },
  { key:'why_you', label:'Why you?' },
  { key:'biggest_achievement', label:'Biggest achievement related to this role?' },
]

export function Questions(){
  const { resumeId, jdText, setJdText } = useAppStore()
  const [q, setQ] = useState(QUESTIONS[0].key)
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)

  const onGenerate = async ()=>{
    if(!resumeId) return alert('Please select or upload a resume first')
    setBusy(true)
    try{
      const jd = await normalizeJob(jdText)
      const res = await generateShort({ resumeId, job: jd, question: q as any, language: 'auto' })
      setText(res.text)
    } catch(err:any){ alert(err.message || 'Failed') } finally{ setBusy(false) }
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm mb-1">Job Description</label>
        <textarea className="border rounded w-full h-40 p-2" value={jdText} onChange={e=>setJdText(e.target.value)} placeholder="Paste job description..." />
      </div>
      <div>
        <label className="block text-sm mb-1">Question</label>
        <select className="border rounded px-2 py-1" value={q} onChange={e=>setQ(e.target.value)}>
          {QUESTIONS.map(x=> <option key={x.key} value={x.key}>{x.label}</option>)}
        </select>
      </div>
      <button className="px-3 py-1 rounded bg-primary text-white" onClick={onGenerate} disabled={busy}>{busy?'Generating...':'Generate'}</button>
      <div className="border rounded p-3 min-h-[120px] whitespace-pre-wrap">{text || '—'}</div>
    </div>
  )
}

