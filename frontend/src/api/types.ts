export type ResumeOut = { id:number; fileName:string; tags:string[]; lang?:'zh'|'en'; createdAt:string };
export type JobNormalized = { role?:string; responsibilities:string[]; requirements:string[]; keywords:string[]; language?:'zh'|'en' };
export type GenerateShortRequest = { resumeId:number; job: JobNormalized|Record<string,unknown>; question:'why_company'|'why_you'|'biggest_achievement'; language:'auto'|'zh'|'en' };
export type GenerateShortResponse = { genId:number; text:string };
export type GenerateLetterRequest = { resumeId:number; job: JobNormalized|Record<string,unknown>; style:'Formal'|'Warm'|'Tech'; paragraphs_max:number; target_words:number; include_keywords:string[]; avoid_keywords:string[]; language:'auto'|'zh'|'en'; format:'html'|'md' };
export type GenerateLetterResponse = { genId:number; format:'html'|'md'; content:string; meta:{ style:string; language:string; counts:Record<string,number>; notes?:string } };
export type ExportPDFRequest = { genId?:number; html?:string; options?:Record<string,unknown> };

