export function ProjectsPanel() {
  return (
    <section className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-white/10 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold">Boards in this team</h2>
        <button className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-2 rounded-md text-sm">Create new project</button>
      </div>
      <div className="grid grid-cols-[repeat(auto-fill,minmax(220px,1fr))] gap-3">
        <div className="bg-slate-100 dark:bg-gray-800 border border-gray-200 dark:border-white/10 rounded-lg p-3">Main</div>
        <div className="bg-slate-100 dark:bg-gray-800 border border-gray-200 dark:border-white/10 rounded-lg p-3">Untitled</div>
        <div className="bg-slate-100 dark:bg-gray-800 border border-gray-200 dark:border-white/10 rounded-lg p-3">MetalStroy + Quant</div>
      </div>
    </section>
  )
}


