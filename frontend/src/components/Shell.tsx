import { Suspense, useEffect, useRef, useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { ROLE_LABELS, useAuth } from '../auth/session';
const links = [
  ['/', 'Overview', '◫'],
  ['/new-analysis', 'New Analysis', '+'],
  ['/analyses', 'Analysis History', '↗'],
  ['/evidence/local', 'Explanation', '≋'],
  ['/evidence/stability', 'Reliability', '◎'],
  ['/review', 'Review', '✓'],
  ['/audit-history', 'Audit Trail', '↗'],
  ['/model-card', 'Model Card', '▤'],
];
export function Shell() {
  const auth = useAuth();
  const location = useLocation();
  const [dark, setDark] = useState(
    () => window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false,
  );
  const [menu, setMenu] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const main = useRef<HTMLElement>(null);
  const menuButton = useRef<HTMLButtonElement>(null);
  const previous = useRef(location.pathname);
  useEffect(() => {
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  }, [dark]);
  useEffect(() => {
    setMenu(false);
    if (previous.current !== location.pathname) {
      main.current?.focus();
      previous.current = location.pathname;
    }
    document.title = `Aletheia · ${links.find(([p]) => p === location.pathname)?.[1] ?? 'Evidence'}`;
  }, [location.pathname]);
  const nav = (
    <nav aria-label="Workspace">
      {links.map(([path, title, icon]) => (
        <NavLink key={path} to={path!} end={path === '/'} aria-label={title}>
          <span aria-hidden="true">{icon}</span>
          <span>{title}</span>
        </NavLink>
      ))}
      {auth.roles.includes('administrator') && (
        <NavLink to="/admin/models">Release evidence</NavLink>
      )}
    </nav>
  );
  return (
    <div className={`app ${collapsed ? 'collapsed' : ''}`}>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <aside className="sidebar">
        <div className="brand">
          <NavLink to="/" className="wordmark">
            {collapsed ? 'a' : 'aletheia'}
            <span />
          </NavLink>
          <button
            className="icon-button collapse"
            onClick={() => setCollapsed(!collapsed)}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            ⇔
          </button>
        </div>
        <div className="workspace">
          <span aria-hidden="true">✧</span>
          <div>
            <strong>Decision governance</strong>
            <small>Healthcare research</small>
          </div>
        </div>
        <div className="nav-label">WORKSPACE</div>
        {nav}
        <div className="sidebar-note">
          Approved frozen model
          <br />
          <small>Case data without identifiers</small>
        </div>
        <div className="sidebar-bottom">
          <strong>{auth.token ? 'Organization session' : 'Viewer · public evidence'}</strong>
          <small>{auth.roles.map((r) => ROLE_LABELS[r]).join(', ') || 'Read-only access'}</small>
          <button className="theme-button" onClick={() => setDark(!dark)}>
            {dark ? '☼ Light' : '☾ Dark'} appearance
          </button>
          {auth.token ? (
            <button className="text-button" onClick={auth.signOut}>
              Sign out
            </button>
          ) : (
            <NavLink to="/sign-in">Organization sign-in</NavLink>
          )}
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span aria-hidden="true">›</span>{' '}
            <strong>{links.find(([p]) => p === location.pathname)?.[1] ?? 'Evidence'}</strong>
          </div>
          <span className="chip">Research workspace</span>
          <button
            className="icon-button mobile-toggle"
            ref={menuButton}
            aria-label="Open navigation"
            aria-expanded={menu}
            aria-controls="mobile-menu"
            onClick={() => setMenu(!menu)}
          >
            Menu
          </button>
        </header>
        {menu && (
          <div
            className="mobile-menu"
            id="mobile-menu"
            onKeyDown={(e) => {
              if (e.key === 'Escape') {
                setMenu(false);
                menuButton.current?.focus();
              }
            }}
          >
            {nav}
            <NavLink to="/sign-in">Organization sign-in</NavLink>
            <button onClick={() => setDark(!dark)}>Toggle appearance</button>
            {auth.token && <button onClick={auth.signOut}>Sign out</button>}
          </div>
        )}
        <main id="main" ref={main} tabIndex={-1}>
          {auth.expired && (
            <p role="alert" className="notice warning">
              Your session has expired. <NavLink to="/sign-in">Sign in again</NavLink> to continue
              private actions.
            </p>
          )}
          <Suspense fallback={<div role="status">Loading page…</div>}>
            <Outlet />
          </Suspense>
        </main>
        <footer className="page-footer">
          <span>Educational research · No medical advice</span>
          <span>Aletheia / evidence workbench</span>
        </footer>
      </div>
    </div>
  );
}
export function PageHeading({ title, description }: { title: string; description: string }) {
  return (
    <header className="page-heading">
      <div className="eyebrow">DECISION INTELLIGENCE</div>
      <h1>{title}</h1>
      <p>{description}</p>
    </header>
  );
}
