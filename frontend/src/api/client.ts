import axios from 'axios'
import type { ResumeOut, JobNormalized, GenerateShortRequest, GenerateShortResponse, GenerateLetterRequest, GenerateLetterResponse } from './types'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export const api = axios.create({ baseURL })

api.interceptors.response.use(r=>r, (err)=>{
  const status = err?.response?.status
  let msg = 'Unexpected error'
  if(status===400) msg = '参数有误'
  else if(status===404) msg = '资源不存在'
  else if(status===413) msg = '文件过大'
  else if(status===415) msg = '不支持的文件类型'
  else if(status===502) msg = '服务繁忙或模型异常'
  err.message = msg
  return Promise.reject(err)
})

export async function listResumes(): Promise<ResumeOut[]> {
  const { data } = await api.get('/api/resumes')
  return data
}

export async function uploadResume(file: File, tags?: string[]): Promise<{resumeId:number, snapshot:boolean}> {
  const fd = new FormData()
  fd.append('file', file)
  tags?.forEach(t => fd.append('tags', t))
  const { data } = await api.post('/api/resumes', fd, { headers: { 'Content-Type': 'multipart/form-data' }})
  return data
}

export async function normalizeJob(text: string): Promise<JobNormalized> {
  const { data } = await api.post('/api/jobs/normalize', { text })
  return data
}

export async function generateShort(payload: GenerateShortRequest): Promise<GenerateShortResponse> {
  const { data } = await api.post('/api/generate/short', payload)
  return data
}

export async function generateLetter(payload: GenerateLetterRequest): Promise<GenerateLetterResponse> {
  const { data } = await api.post('/api/generate/letter', payload)
  return data
}

export async function exportPDFByGenId(genId: number): Promise<Blob> {
  const { data } = await api.post('/api/exports/letter/pdf', { genId }, { responseType: 'blob' })
  return data
}

export async function exportPDFByHtml(html: string): Promise<Blob> {
  const { data } = await api.post('/api/exports/letter/pdf', { html }, { responseType: 'blob' })
  return data
}

