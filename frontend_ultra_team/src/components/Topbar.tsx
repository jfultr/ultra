import { ThemeToggle } from './ThemeToggle'

export function Topbar() {
  return (
    <header className="h-14 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-white/10 px-4 flex items-center justify-between">
      <div className="flex-1 max-w-xl">
        <input className="w-full bg-slate-100 dark:bg-gray-800 border border-gray-200 dark:border-white/10 rounded-md px-3 py-2 text-sm" placeholder="Search projects, plans, spaces..." />
      </div>
      <div className="flex items-center gap-3">
        <ThemeToggle />
        <button className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-2 rounded-md text-sm">Create new project</button>
        <div className="w-7 h-7 rounded-full bg-slate-400" />
      </div>
    </header>
  )
}


