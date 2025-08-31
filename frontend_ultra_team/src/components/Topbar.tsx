export function Topbar() {
  return (
    <header className="topbar">
      <div className="search">
        <input placeholder="Search projects, plans, spaces..." />
      </div>
      <div className="account">
        <button className="primary-btn">Create new project</button>
        <div className="avatar" />
      </div>
    </header>
  )
}


