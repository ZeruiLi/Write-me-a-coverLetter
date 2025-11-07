import { useEffect, useState } from 'react'
import { listResumes } from '../api/client'
import type { ResumeOut } from '../api/types'
import { UploadDropzone } from '../components/UploadDropzone'
import { ResumeCard } from '../components/ResumeCard'
import { useAppStore } from '../store'

export function Library({ onGoCompose }: { onGoCompose: ()=>void }){
  const [resumes, setResumes] = useState<ResumeOut[]>([])
  const resumeId = useAppStore(s=>s.resumeId)
  const setResumeId = useAppStore(s=>s.setResumeId)

  const refresh = async ()=>{
    const list = await listResumes()
    setResumes(list)
  }
  useEffect(()=>{ refresh() }, [])
  useEffect(()=>{ if(resumeId){ refresh() } }, [resumeId])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Upload</h2>
        <UploadDropzone />
      </div>
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Resumes</h2>
        <div className="space-y-2">
          {resumes.map(r=> (
            <ResumeCard key={r.id} r={r} onClick={()=>{ setResumeId(r.id); onGoCompose() }} />
          ))}
          {resumes.length===0 && <div className="text-sm text-gray-500">No resumes yet.</div>}
        </div>
      </div>
    </div>
  )
}

