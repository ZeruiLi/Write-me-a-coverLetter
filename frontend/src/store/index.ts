import { create } from 'zustand'

type Lang = 'auto'|'zh'|'en'
type Style = 'Formal'|'Warm'|'Tech'

type State = {
  resumeId?: number
  resumeObjId?: number
  jdText: string
  letterHtml?: string
  genId?: number
  params: { style: Style; paragraphs_max: number; target_words: number; include_keywords: string[]; avoid_keywords: string[]; language: Lang; format: 'html'|'md' }
  uiLang: 'zh'|'en'
  setResumeId: (id:number)=>void
  setResumeObjId: (id:number)=>void
  setJdText: (t:string)=>void
  setParams: (p: Partial<State['params']>)=>void
  setLetter: (html?:string, genId?:number)=>void
  setUiLang: (l:'zh'|'en')=>void
}

const initialParams: State['params'] = { style:'Formal', paragraphs_max:5, target_words:400, include_keywords:[], avoid_keywords:[], language:'auto', format:'html' }

export const useAppStore = create<State>((set)=>({
  jdText: '',
  params: initialParams,
  uiLang: navigator.language.toLowerCase().startsWith('zh') ? 'zh' : 'en',
  setResumeId: (id)=> set({ resumeId:id }),
  setResumeObjId: (id)=> set({ resumeObjId:id }),
  setJdText: (t)=> set({ jdText:t }),
  setParams: (p)=> set((s)=>({ params: { ...s.params, ...p } })),
  setLetter: (html, genId)=> set({ letterHtml: html, genId }),
  setUiLang: (l)=> set({ uiLang:l }),
}))
