import { Sidebar } from './components/Sidebar.tsx'
import { Topbar } from './components/Topbar.tsx'
import { ProjectsPanel } from './components/ProjectsPanel.tsx'

function App() {
  return (
    <div className="min-h-screen text-slate-900 dark:text-slate-100 bg-slate-50 dark:bg-slate-900 flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar />
        <main className="p-4">
          <ProjectsPanel />
        </main>
      </div>
    </div>
  )
}

export default App
