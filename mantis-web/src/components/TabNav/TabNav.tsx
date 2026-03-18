import { useLocation, useNavigate } from 'react-router-dom';
import './TabNav.css';

const TABS = [
  { path: '/dashboard', label: 'DASHBOARD' },
  { path: '/vault', label: 'VAULT OPS' },
  { path: '/skills', label: 'SKILLS' },
  { path: '/system', label: 'SYSTEM' },
];

export function TabNav() {
  const location = useLocation();
  const navigate = useNavigate();
  return (
    <div className="tab-nav">
      {TABS.map(tab => (
        <button
          key={tab.path}
          className={`tab-nav__tab ${location.pathname === tab.path ? 'tab-nav__tab--active' : ''}`}
          onClick={() => navigate(tab.path)}
        >
          {tab.label}
        </button>
      ))}
      <div className="tab-nav__fill" />
    </div>
  );
}
