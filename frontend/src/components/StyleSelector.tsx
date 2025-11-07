import { useAppStore } from '../store'

export function StyleSelector(){
  const params = useAppStore(s=>s.params)
  const setParams = useAppStore(s=>s.setParams)
  return (
    <div className="space-y-3">
      <div>
        <label className="block text-sm mb-1">Style</label>
        <select className="border rounded px-2 py-1" value={params.style} onChange={e=>setParams({style: e.target.value as any})}>
          <option>Formal</option>
          <option>Warm</option>
          <option>Tech</option>
        </select>
      </div>
      <div>
        <label className="block text-sm mb-1">Paragraphs Max</label>
        <input type="number" className="border rounded px-2 py-1 w-24" min={1} max={7} value={params.paragraphs_max} onChange={e=>setParams({paragraphs_max: Number(e.target.value)})} />
      </div>
      <div>
        <label className="block text-sm mb-1">Target Words</label>
        <input type="number" className="border rounded px-2 py-1 w-24" min={200} max={700} value={params.target_words} onChange={e=>setParams({target_words: Number(e.target.value)})} />
      </div>
      <div>
        <label className="block text-sm mb-1">Language</label>
        <select className="border rounded px-2 py-1" value={params.language} onChange={e=>setParams({language: e.target.value as any})}>
          <option value="auto">auto</option>
          <option value="zh">zh</option>
          <option value="en">en</option>
        </select>
      </div>
    </div>
  )
}

