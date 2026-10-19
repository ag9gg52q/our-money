import { NavLink, Outlet } from 'react-router'

export default function Layout() {
  return (
    <div className="layout">
      <header className="header">
        <span className="logo">Our Money</span>
        <nav className="nav">
          <NavLink to="/" end>
            Acasă
          </NavLink>
          <NavLink to="/status">Status</NavLink>
        </nav>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
