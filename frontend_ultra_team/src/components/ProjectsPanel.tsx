export function ProjectsPanel() {
  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Boards in this team</h2>
        <button className="primary-btn">Create new project</button>
      </div>
      <div className="projects-grid">
        <div className="project-card">Main</div>
        <div className="project-card">Untitled</div>
        <div className="project-card">MetalStroy + Quant</div>
      </div>
    </section>
  )
}


