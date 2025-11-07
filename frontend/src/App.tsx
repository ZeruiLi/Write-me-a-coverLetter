import { useState } from 'react'
import { Library } from './routes/Library'
import { Compose } from './routes/Compose'
import { Questions } from './routes/Questions'
import { LanguageSwitch } from './components/LanguageSwitch'

type View = 'library' | 'compose' | 'questions'

export default function App() {
  const [view, setView] = useState<View>('library')
  return (
    <div className="min-h-screen">
      <header className="border-b bg-white/70 dark:bg-gray-800/70 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="font-semibold">Write me a Cover Letter</div>
          <nav className="flex items-center gap-3">
            <button className={btn(view==='library')} onClick={()=>setView('library')}>Library</button>
            <button className={btn(view==='compose')} onClick={()=>setView('compose')}>Compose</button>
            <button className={btn(view==='questions')} onClick={()=>setView('questions')}>Questions</button>
            <LanguageSwitch />
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-6">
        {view==='library' && <Library onGoCompose={()=>setView('compose')} />}
        {view==='compose' && <Compose />}
        {view==='questions' && <Questions />}
      </main>
    </div>
  )
}

function btn(active:boolean){
  return `px-3 py-1 rounded ${active? 'bg-primary text-white':'hover:bg-gray-100 dark:hover:bg-gray-700'}`
}

