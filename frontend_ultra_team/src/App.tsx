import './App.css'
import { Sidebar } from './components/Sidebar'
import { Topbar } from './components/Topbar'
import { ProjectsPanel } from './components/ProjectsPanel'

function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <Topbar />
      <main className="content">
        <ProjectsPanel />
      </main>
    </div>
  )
}

export default App
