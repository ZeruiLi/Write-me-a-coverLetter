import { useState } from 'react'
import { normalizeJob, generateLetter, exportPDFByGenId, exportPDFByHtml, extractJdFromText, generateLetter2 } from '../api/client'
import { useAppStore } from '../store'
import { StyleSelector } from '../components/StyleSelector'
import { A4Preview } from '../components/A4Preview'

export function Compose(){
  const { resumeObjId, jdText, setJdText, params, setParams, letterHtml, setLetter, genId } = useAppStore()
  const [busy, setBusy] = useState(false)

  const onGenerate = async ()=>{
    if(!resumeObjId) return alert('Please select or upload a resume first')
    setBusy(true)
    try{
      // v1.1 flow: extract JD then letter2
      const { jdObjId } = await extractJdFromText(jdText)
      const { genId, html } = await generateLetter2(resumeObjId, jdObjId, params.style, params.language)
      setLetter(html, genId)
    } catch(err:any){ alert(err.message || 'Failed') } finally{ setBusy(false) }
  }

  const onExport = async ()=>{
    if(genId){
      try{
        const blob = await exportPDFByGenId(genId)
        downloadBlob(blob, 'cover_letter.pdf')
        return
      }catch{}
    }
    if(letterHtml){
      const blob = await exportPDFByHtml(letterHtml)
      downloadBlob(blob, 'cover_letter.pdf')
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1 space-y-4">
        <div>
          <label className="block text-sm mb-1">Job Description</label>
          <textarea className="border rounded w-full h-40 p-2" value={jdText} onChange={e=>setJdText(e.target.value)} placeholder="Paste job description..." />
        </div>
        <StyleSelector />
        <button className="px-3 py-1 rounded bg-primary text-white" onClick={onGenerate} disabled={busy}>{busy?'Generating...':'Generate Letter'}</button>
        <button className="ml-2 px-3 py-1 rounded border" onClick={onExport} disabled={!letterHtml}>Export PDF</button>
      </div>
      <div className="lg:col-span-2">
        <A4Preview html={letterHtml} />
      </div>
    </div>
  )
}

function downloadBlob(blob: Blob, filename: string){
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  setTimeout(()=>URL.revokeObjectURL(url), 1000)
}
