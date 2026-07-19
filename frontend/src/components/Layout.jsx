import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Layout.css';

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>Email CRM</h2>
        </div>
        <nav className="sidebar-nav">
          <Link to="/" className="nav-link">Dashboard</Link>
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-name">{user?.full_name}</div>
            <div className="user-email">{user?.email}</div>
          </div>
          <button onClick={handleLogout} className="secondary logout-btn">
            Logout
          </button>
        </div>
      </aside>
      
      <main className="main-content">
        <header className="main-header">
          <h1>Support Desk</h1>
        </header>
        <div className="content-area">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
