import { useTranslation } from 'react-i18next'
import { useAppStore } from '../store'

export function LanguageSwitch(){
  const { i18n } = useTranslation()
  const uiLang = useAppStore(s=>s.uiLang)
  const setUiLang = useAppStore(s=>s.setUiLang)
  const toggle = ()=>{
    const next = uiLang==='zh'?'en':'zh'
    setUiLang(next)
    i18n.changeLanguage(next)
  }
  return <button onClick={toggle} className="px-2 py-1 rounded border">{uiLang.toUpperCase()}</button>
}

