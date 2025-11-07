type Props = { html?: string }

export function A4Preview({ html }: Props){
  return (
    <div className="bg-white shadow rounded a4 min-h-[297mm] w-[210mm] mx-auto">
      <div className="prose max-w-none p-8" dangerouslySetInnerHTML={{ __html: html || '<p class="text-gray-400">No content yet</p>' }} />
    </div>
  )
}

