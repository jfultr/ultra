export function Sidebar() {
  return (
    <aside className="w-64 bg-slate-100 dark:bg-slate-950 text-slate-900 dark:text-slate-200 border-r border-gray-200 dark:border-white/10 p-4 space-y-3">
      <div className="flex items-center gap-2 font-bold text-lg">ULTRA BUSINESS TEAM</div>
      <nav className="grid gap-1">
        <a className="px-2 py-2 rounded-md hover:bg-slate-200 dark:hover:bg-white/10" href="#">Home</a>
        <a className="px-2 py-2 rounded-md hover:bg-slate-200 dark:hover:bg-white/10" href="#">Projects</a>
        <a className="px-2 py-2 rounded-md hover:bg-slate-200 dark:hover:bg-white/10" href="#">Templates</a>
        <a className="px-2 py-2 rounded-md hover:bg-slate-200 dark:hover:bg-white/10" href="#">Settings</a>
      </nav>
    </aside>
  )
}


