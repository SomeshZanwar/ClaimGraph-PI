import { useState } from "react";
import { Link, Route, Routes } from "react-router-dom";

function HomePage() {
  return (
    <main className="page-shell">
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Healthcare payment integrity</p>
        <h1 id="page-title">Claims investigation built around evidence.</h1>
        <p className="hero-copy">
          ClaimGraph PI brings claim rules, provider peer analysis, network relationships,
          and model signals into one investigator workflow.
        </p>
        <div className="hero-actions">
          <Link className="button button-primary" to="/queue">
            Open investigation queue
          </Link>
          <a
            className="button button-secondary"
            href="https://github.com/SomeshZanwar/ClaimGraph-PI/blob/main/PRD.md"
          >
            Read product requirements
          </a>
        </div>
      </section>
    </main>
  );
}

function QueuePage() {
  return (
    <main className="page-shell">
      <section className="content-panel">
        <p className="eyebrow">Investigation workspace</p>
        <h1>Investigation queue</h1>
        <p>
          The case queue will be connected after the canonical claims model and risk engine are in place.
        </p>
      </section>
    </main>
  );
}

function NotFoundPage() {
  return (
    <main className="page-shell">
      <section className="content-panel">
        <p className="eyebrow">404</p>
        <h1>Page not found</h1>
        <p>The requested page does not exist.</p>
        <Link className="button button-primary" to="/">
          Return to ClaimGraph PI
        </Link>
      </section>
    </main>
  );
}

function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const currentYear = new Date().getFullYear();

  return (
    <div className="app-frame">
      <header className="site-header">
        <Link
          className="brand"
          to="/"
          aria-label="ClaimGraph PI home"
          onClick={() => setMenuOpen(false)}
        >
          ClaimGraph PI
        </Link>

        <button
          className="menu-toggle"
          type="button"
          aria-expanded={menuOpen}
          aria-controls="primary-navigation"
          onClick={() => setMenuOpen((open) => !open)}
        >
          {menuOpen ? "Close" : "Menu"}
        </button>

        <nav
          id="primary-navigation"
          className={menuOpen ? "primary-nav primary-nav-open" : "primary-nav"}
          aria-label="Primary navigation"
        >
          <Link to="/queue" onClick={() => setMenuOpen(false)}>
            Queue
          </Link>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/queue" element={<QueuePage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>

      <footer className="site-footer">
        <span>© {currentYear} ClaimGraph PI</span>
      </footer>
    </div>
  );
}

export default App;
