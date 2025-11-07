import type { ResumeOut } from '../api/types'

export function ResumeCard({ r, onClick }: { r: ResumeOut; onClick: ()=>void }){
  return (
    <button onClick={onClick} className="w-full text-left border rounded p-3 hover:bg-gray-50">
      <div className="font-medium">{r.fileName}</div>
      <div className="text-sm text-gray-500">{new Date(r.createdAt).toLocaleString()} · {r.lang || '—'}</div>
    </button>
  )
}

