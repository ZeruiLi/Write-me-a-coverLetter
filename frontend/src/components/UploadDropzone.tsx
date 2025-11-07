import { useRef, useState } from 'react'
import { extractResumeFile } from '../api/client'
import { useAppStore } from '../store'

export function UploadDropzone(){
  const inputRef = useRef<HTMLInputElement>(null)
  const [busy, setBusy] = useState(false)
  const setResumeId = useAppStore(s=>s.setResumeId)
  const setResumeObjId = useAppStore(s=>s.setResumeObjId)
  const onPick = async (e: React.ChangeEvent<HTMLInputElement>)=>{
    const f = e.target.files?.[0]
    if(!f) return
    setBusy(true)
    try{
      try {
        const res = await extractResumeFile(f)
        setResumeObjId(res.resumeObjId)
      } catch (e:any) {
        alert(e.message || 'Resume extraction failed')
      }
    } finally { setBusy(false) }
  }
  return (
    <div className="border-2 border-dashed rounded p-6 text-center">
      <p className="mb-2">Upload a resume file (pdf/docx/txt/md/jpg/png)</p>
      <button className="px-3 py-1 rounded bg-primary text-white" onClick={()=>inputRef.current?.click()} disabled={busy}>{busy?'Uploading...':'Choose File'}</button>
      <input ref={inputRef} type="file" className="hidden" onChange={onPick} />
    </div>
  )
}
