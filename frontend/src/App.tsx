import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import {
  Link,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, User } from "./lib/api";

const NetworkGraph = lazy(() => import("./components/NetworkGraph"));
import {
  getAnalyticsConsent,
  setAnalyticsConsent,
} from "./lib/consent";

function useDocumentTitle(title: string) {
  useEffect(() => {
    document.title = title;

    const descriptions: Array<[string, string]> = [
      ["Privacy", "How ClaimGraph PI handles account, session, analytics, and synthetic claims data."],
      ["Terms", "Terms for using the ClaimGraph PI synthetic healthcare claims investigation demonstration."],
      ["Support", "Support and bug-report guidance for ClaimGraph PI."],
      ["Methodology", "How ClaimGraph PI builds deterministic, peer, anomaly, graph, and lineage evidence for human review."],
      ["Queue", "Prioritized investigation cases generated from transparent claims risk signals."],
      ["Provider", "Synthetic provider peer and network context for ClaimGraph PI investigations."],
      ["Case", "Investigator case evidence, workflow status, notes, and source lineage in ClaimGraph PI."],
    ];
    const description =
      descriptions.find(([key]) => title.includes(key))?.[1] ??
      "ClaimGraph PI is an explainable pre-payment claims investigation and provider network intelligence platform.";

    let descriptionMeta = document.querySelector('meta[name="description"]');
    if (!descriptionMeta) {
      descriptionMeta = document.createElement("meta");
      descriptionMeta.setAttribute("name", "description");
      document.head.appendChild(descriptionMeta);
    }
    descriptionMeta.setAttribute("content", description);

    let canonical = document.querySelector('link[rel="canonical"]') as HTMLLinkElement | null;
    if (!canonical) {
      canonical = document.createElement("link");
      canonical.rel = "canonical";
      document.head.appendChild(canonical);
    }
    canonical.href = window.location.origin + window.location.pathname;

    for (const [property, value] of [
      ["og:title", title],
      ["og:description", description],
      ["og:url", canonical.href],
    ]) {
      let meta = document.querySelector('meta[property="' + property + '"]');
      if (!meta) {
        meta = document.createElement("meta");
        meta.setAttribute("property", property);
        document.head.appendChild(meta);
      }
      meta.setAttribute("content", value);
    }
  }, [title]);
}

function formatMoney(value: string | number | null | undefined) {
  const numeric = Number(value || 0);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(numeric);
}

function formatDate(value: string | null | undefined) {
  if (!value) return "Unavailable";
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function StatusMessage({
  type,
  children,
}: {
  type: "success" | "error" | "info";
  children: React.ReactNode;
}) {
  return <div className={"status-message status-" + type}>{children}</div>;
}

function LoadingState({ label = "Loading data" }: { label?: string }) {
  return (
    <div className="loading-state" role="status" aria-live="polite">
      <span className="progress-marker" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

function TelemetryTracker() {
  const location = useLocation();

  useEffect(() => {
    if (getAnalyticsConsent() !== "granted") return;

    const normalizedRoute = location.pathname
      .replace(/^\/cases\/[^/]+$/, "/cases/:id")
      .replace(/^\/providers\/[^/]+$/, "/providers/:id");

    void api.track("page_view", normalizedRoute).catch(() => {
      // Analytics failures never block the product workflow.
    });
  }, [location.pathname]);

  return null;
}

function CookieBanner() {
  const [consent, setConsent] = useState(getAnalyticsConsent());

  if (consent !== null) return null;

  return (
    <aside className="cookie-banner" aria-label="Analytics consent">
      <div>
        <strong>Privacy choice</strong>
        <p>
          ClaimGraph PI can collect privacy-safe product usage events. Claims content and
          synthetic beneficiary identifiers are never sent to analytics.
        </p>
      </div>
      <div className="cookie-actions">
        <button
          className="button button-primary"
          type="button"
          onClick={() => {
            setAnalyticsConsent("granted");
            setConsent("granted");
          }}
        >
          Allow analytics
        </button>
        <button
          className="button button-secondary"
          type="button"
          onClick={() => {
            setAnalyticsConsent("denied");
            setConsent("denied");
          }}
        >
          Decline
        </button>
      </div>
    </aside>
  );
}

function AppHeader({ user }: { user: User | null }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const logout = useMutation({
    mutationFn: api.logout,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["me"] });
      navigate("/");
    },
  });

  return (
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
        {user ? <Link to="/queue" onClick={() => setMenuOpen(false)}>Queue</Link> : null}
        <Link to="/about" onClick={() => setMenuOpen(false)}>Methodology</Link>
        <Link to="/support" onClick={() => setMenuOpen(false)}>Support</Link>
        {user ? (
          <button
            className="nav-button"
            type="button"
            disabled={logout.isPending}
            onClick={() => logout.mutate()}
          >
            Sign out
          </button>
        ) : (
          <Link to="/login" onClick={() => setMenuOpen(false)}>Sign in</Link>
        )}
      </nav>
    </header>
  );
}

function AppFooter() {
  const year = new Date().getFullYear();
  return (
    <footer className="site-footer">
      <span>© {year} ClaimGraph PI</span>
      <nav aria-label="Footer navigation">
        <Link to="/privacy">Privacy</Link>
        <Link to="/terms">Terms</Link>
        <Link to="/support">Support</Link>
        <a
          href="https://github.com/SomeshZanwar/ClaimGraph-PI"
          target="_blank"
          rel="noreferrer"
        >
          Repository
        </a>
      </nav>
    </footer>
  );
}

function HomePage({ user }: { user: User | null }) {
  useDocumentTitle("ClaimGraph PI | Explainable Claims Investigation");

  return (
    <main className="page-shell">
      <section className="hero" aria-labelledby="home-title">
        <p className="eyebrow">Healthcare payment integrity</p>
        <h1 id="home-title">Investigate suspicious claims with traceable evidence.</h1>
        <p className="hero-copy">
          ClaimGraph PI combines deterministic billing signals, provider peer analysis,
          anomaly detection, network intelligence, and financial exposure into a human
          investigation workflow.
        </p>
        <div className="hero-actions">
          <Link className="button button-primary" to={user ? "/queue" : "/login"}>
            {user ? "Open investigation queue" : "Sign in to investigate"}
          </Link>
          <Link className="button button-secondary" to="/about">
            Review methodology
          </Link>
        </div>
      </section>

      <section className="product-flow" aria-labelledby="flow-title">
        <div className="section-heading">
          <p className="eyebrow">Investigation flow</p>
          <h2 id="flow-title">Evidence remains separate all the way to the case file.</h2>
        </div>
        <ol className="flow-list">
          <li>
            <span>01</span>
            <div>
              <h3>Validate source claims</h3>
              <p>CMS synthetic claims are schema-checked, line-normalized, and traceable to their ingestion batch.</p>
            </div>
          </li>
          <li>
            <span>02</span>
            <div>
              <h3>Generate independent signals</h3>
              <p>Rules, peer statistics, anomaly scores, and graph metrics preserve their own versions and evidence.</p>
            </div>
          </li>
          <li>
            <span>03</span>
            <div>
              <h3>Prioritize human review</h3>
              <p>Cases rank investigation workload while keeping the underlying evidence visible to the investigator.</p>
            </div>
          </li>
          <li>
            <span>04</span>
            <div>
              <h3>Record an auditable disposition</h3>
              <p>Status, notes, assignment, and disposition changes create an audit trail rather than an automated denial.</p>
            </div>
          </li>
        </ol>
      </section>

      <section className="boundary-callout">
        <p className="eyebrow">Responsible-use boundary</p>
        <h2>Investigation support only</h2>
        <p>
          The platform does not autonomously approve or deny healthcare claims. The public
          demonstration uses synthetic CMS DE-SynPUF data, and anomaly scores are not fraud
          probabilities.
        </p>
      </section>
    </main>
  );
}

function LoginPage() {
  useDocumentTitle("Sign In | ClaimGraph PI");
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useMutation({
    mutationFn: () => api.login(email, password),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["me"] });
      navigate("/queue");
    },
  });

  return (
    <main className="narrow-shell">
      <section className="form-panel">
        <p className="eyebrow">Secure access</p>
        <h1>Sign in</h1>
        <p>Use a verified ClaimGraph PI investigator account.</p>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            login.mutate();
          }}
        >
          <label>
            Email
            <input
              type="email"
              autoComplete="email"
              value={email}
              required
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              required
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {login.isError ? <StatusMessage type="error">{login.error.message}</StatusMessage> : null}
          <button className="button button-primary" type="submit" disabled={login.isPending}>
            {login.isPending ? "Signing in" : "Sign in"}
          </button>
        </form>
        <div className="form-links">
          <Link to="/forgot-password">Forgot password</Link>
          <Link to="/signup">Create account</Link>
        </div>
      </section>
    </main>
  );
}

function SignupPage() {
  useDocumentTitle("Create Account | ClaimGraph PI");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const signup = useMutation({
    mutationFn: () => api.signup(email, password),
  });

  return (
    <main className="narrow-shell">
      <section className="form-panel">
        <p className="eyebrow">Investigator access</p>
        <h1>Create account</h1>
        <p>
          Passwords require at least 12 characters. Account access begins after email verification.
        </p>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            signup.mutate();
          }}
        >
          <label>
            Email
            <input
              type="email"
              autoComplete="email"
              value={email}
              required
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete="new-password"
              minLength={12}
              value={password}
              required
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {signup.isSuccess ? <StatusMessage type="success">{signup.data.message}</StatusMessage> : null}
          {signup.isError ? <StatusMessage type="error">{signup.error.message}</StatusMessage> : null}
          <button className="button button-primary" type="submit" disabled={signup.isPending}>
            {signup.isPending ? "Creating account" : "Create account"}
          </button>
        </form>
        <div className="form-links"><Link to="/login">Return to sign in</Link></div>
      </section>
    </main>
  );
}

function VerifyEmailPage() {
  useDocumentTitle("Verify Email | ClaimGraph PI");
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const verify = useMutation({
    mutationFn: () => api.verifyEmail(token),
  });

  useEffect(() => {
    if (token && verify.isIdle) verify.mutate();
  }, [token, verify]);

  return (
    <main className="narrow-shell">
      <section className="form-panel">
        <p className="eyebrow">Account verification</p>
        <h1>Verify email</h1>
        {!token ? <StatusMessage type="error">Verification token is missing.</StatusMessage> : null}
        {verify.isPending ? <LoadingState label="Verifying account" /> : null}
        {verify.isSuccess ? (
          <>
            <StatusMessage type="success">{verify.data.message}</StatusMessage>
            <Link className="button button-primary" to="/login">Continue to sign in</Link>
          </>
        ) : null}
        {verify.isError ? <StatusMessage type="error">{verify.error.message}</StatusMessage> : null}
      </section>
    </main>
  );
}

function ForgotPasswordPage() {
  useDocumentTitle("Password Reset | ClaimGraph PI");
  const [email, setEmail] = useState("");
  const reset = useMutation({
    mutationFn: () => api.requestPasswordReset(email),
  });

  return (
    <main className="narrow-shell">
      <section className="form-panel">
        <p className="eyebrow">Account recovery</p>
        <h1>Reset password</h1>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            reset.mutate();
          }}
        >
          <label>
            Email
            <input
              type="email"
              autoComplete="email"
              value={email}
              required
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          {reset.isSuccess ? <StatusMessage type="success">{reset.data.message}</StatusMessage> : null}
          {reset.isError ? <StatusMessage type="error">{reset.error.message}</StatusMessage> : null}
          <button className="button button-primary" type="submit" disabled={reset.isPending}>
            Send reset instructions
          </button>
        </form>
      </section>
    </main>
  );
}

function ResetPasswordPage() {
  useDocumentTitle("Choose New Password | ClaimGraph PI");
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const [password, setPassword] = useState("");
  const reset = useMutation({
    mutationFn: () => api.confirmPasswordReset(token, password),
  });

  return (
    <main className="narrow-shell">
      <section className="form-panel">
        <p className="eyebrow">Account recovery</p>
        <h1>Choose a new password</h1>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            reset.mutate();
          }}
        >
          <label>
            New password
            <input
              type="password"
              autoComplete="new-password"
              minLength={12}
              value={password}
              required
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {!token ? <StatusMessage type="error">Password reset token is missing.</StatusMessage> : null}
          {reset.isSuccess ? <StatusMessage type="success">{reset.data.message}</StatusMessage> : null}
          {reset.isError ? <StatusMessage type="error">{reset.error.message}</StatusMessage> : null}
          <button className="button button-primary" type="submit" disabled={reset.isPending || !token}>
            Set new password
          </button>
        </form>
      </section>
    </main>
  );
}

function ProtectedRoute({
  user,
  loading,
  children,
}: {
  user: User | null;
  loading: boolean;
  children: React.ReactNode;
}) {
  const location = useLocation();
  if (loading) return <main className="page-shell"><LoadingState label="Checking session" /></main>;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <>{children}</>;
}

function QueuePage() {
  useDocumentTitle("Investigation Queue | ClaimGraph PI");
  const [band, setBand] = useState("");
  const [caseStatus, setCaseStatus] = useState("");
  const query = useMemo(() => {
    const params = new URLSearchParams();
    if (band) params.set("priority_band", band);
    if (caseStatus) params.set("status", caseStatus);
    const serialized = params.toString();
    return serialized ? "?" + serialized : "";
  }, [band, caseStatus]);
  const cases = useQuery({
    queryKey: ["cases", query],
    queryFn: () => api.cases(query),
  });

  return (
    <main className="workspace-shell">
      <header className="workspace-heading">
        <div>
          <p className="eyebrow">Investigation workspace</p>
          <h1>Case queue</h1>
        </div>
        {cases.data ? <p className="queue-count">{cases.data.meta.total} visible cases</p> : null}
      </header>

      <section className="filter-row" aria-label="Case filters">
        <label>
          Priority
          <select value={band} onChange={(event) => setBand(event.target.value)}>
            <option value="">All priorities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </label>
        <label>
          Status
          <select value={caseStatus} onChange={(event) => setCaseStatus(event.target.value)}>
            <option value="">All statuses</option>
            <option value="NEW">New</option>
            <option value="IN_REVIEW">In review</option>
            <option value="NEEDS_DOCUMENTATION">Needs documentation</option>
            <option value="ESCALATED">Escalated</option>
            <option value="CLEARED">Cleared</option>
            <option value="CONFIRMED_ISSUE">Confirmed issue</option>
            <option value="CLOSED">Closed</option>
          </select>
        </label>
      </section>

      {cases.isLoading ? <LoadingState label="Loading investigation cases" /> : null}
      {cases.isError ? <StatusMessage type="error">{cases.error.message}</StatusMessage> : null}
      {cases.data && cases.data.items.length === 0 ? (
        <div className="empty-state">
          <h2>No cases match these filters</h2>
          <p>Change the filters or run the analytical pipeline to generate investigation cases.</p>
        </div>
      ) : null}
      {cases.data && cases.data.items.length > 0 ? (
        <div className="table-region" role="region" aria-label="Investigation cases" tabIndex={0}>
          <table>
            <thead>
              <tr>
                <th>Priority</th>
                <th>Claim</th>
                <th>Exposure</th>
                <th>Status</th>
                <th>Strongest signal</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              {cases.data.items.map((item) => (
                <tr key={item.id}>
                  <td><span className={"risk-label risk-" + item.priority_band.toLowerCase()}>{item.priority_band} {item.priority_score}</span></td>
                  <td><Link to={"/cases/" + item.id}>{item.claim_record_id}</Link></td>
                  <td>{formatMoney(item.financial_exposure)}</td>
                  <td>{item.status.replaceAll("_", " ")}</td>
                  <td>{item.strongest_signal || "Multiple signals"}</td>
                  <td>{formatDate(item.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </main>
  );
}

function EvidenceBlock({ title, value }: { title: string; value: unknown }) {
  if (value === null || value === undefined) return null;
  return (
    <section className="evidence-block">
      <h2>{title}</h2>
      <pre>{JSON.stringify(value, null, 2)}</pre>
    </section>
  );
}

function CasePage() {
  const { caseId = "" } = useParams();
  const queryClient = useQueryClient();
  const [note, setNote] = useState("");
  const caseQuery = useQuery({
    queryKey: ["case", caseId],
    queryFn: () => api.case(caseId),
    enabled: Boolean(caseId),
  });
  const notesQuery = useQuery({
    queryKey: ["case-notes", caseId],
    queryFn: () => api.notes(caseId),
    enabled: Boolean(caseId),
  });
  const assign = useMutation({
    mutationFn: () => api.updateCase(caseId, { assign_to_self: true, status: "IN_REVIEW" }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["case", caseId] });
      await queryClient.invalidateQueries({ queryKey: ["cases"] });
    },
  });
  const addNote = useMutation({
    mutationFn: () => api.addNote(caseId, note),
    onSuccess: async () => {
      setNote("");
      await queryClient.invalidateQueries({ queryKey: ["case-notes", caseId] });
    },
  });
  const update = useMutation({
    mutationFn: (payload: { status?: string; disposition?: string }) =>
      api.updateCase(caseId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["case", caseId] });
      await queryClient.invalidateQueries({ queryKey: ["cases"] });
    },
  });

  const current = caseQuery.data;
  useDocumentTitle(current ? "Case " + current.claim_record_id + " | ClaimGraph PI" : "Case Review | ClaimGraph PI");

  if (caseQuery.isLoading) return <main className="workspace-shell"><LoadingState label="Loading case evidence" /></main>;
  if (caseQuery.isError) return <main className="workspace-shell"><StatusMessage type="error">{caseQuery.error.message}</StatusMessage></main>;
  if (!current) return null;

  const evidence = current.evidence as Record<string, unknown>;
  const providers = Array.isArray(evidence.providers) ? evidence.providers.map(String) : [];

  return (
    <main className="workspace-shell">
      <header className="case-heading">
        <div>
          <Link className="back-link" to="/queue">Back to queue</Link>
          <p className="eyebrow">Case {current.id}</p>
          <h1>Claim {current.claim_record_id}</h1>
        </div>
        <div className="case-priority">
          <span className={"risk-label risk-" + current.priority_band.toLowerCase()}>{current.priority_band}</span>
          <strong>{current.priority_score}</strong>
          <small>priority score, not fraud probability</small>
        </div>
      </header>

      <section className="case-facts">
        <div><span>Exposure</span><strong>{formatMoney(current.financial_exposure)}</strong></div>
        <div><span>Status</span><strong>{current.status.replaceAll("_", " ")}</strong></div>
        <div><span>Assigned</span><strong>{current.assigned_user_id ? "Assigned" : "Unassigned"}</strong></div>
        <div><span>Evidence version</span><strong className="mono">{current.evidence_hash.slice(0, 12)}</strong></div>
      </section>

      <section className="case-actions">
        {!current.assigned_user_id ? (
          <button className="button button-primary" type="button" disabled={assign.isPending} onClick={() => assign.mutate()}>
            Assign to me
          </button>
        ) : null}
        <label>
          Case status
          <select
            value={current.status}
            onChange={(event) => update.mutate({ status: event.target.value })}
            disabled={update.isPending}
          >
            {["NEW","IN_REVIEW","NEEDS_DOCUMENTATION","ESCALATED","CLEARED","CONFIRMED_ISSUE","CLOSED"].map((value) => (
              <option key={value} value={value}>{value.replaceAll("_", " ")}</option>
            ))}
          </select>
        </label>
      </section>

      {assign.isError ? <StatusMessage type="error">{assign.error.message}</StatusMessage> : null}
      {update.isError ? <StatusMessage type="error">{update.error.message}</StatusMessage> : null}
      {update.isSuccess ? <StatusMessage type="success">Case workflow updated.</StatusMessage> : null}

      {providers.length > 0 ? (
        <section className="provider-links">
          <h2>Linked providers</h2>
          <div>{providers.map((provider) => <Link key={provider} to={"/providers/" + encodeURIComponent(provider)}>{provider}</Link>)}</div>
        </section>
      ) : null}

      <div className="evidence-layout">
        <EvidenceBlock title="Deterministic signals" value={evidence.rule_signals} />
        <EvidenceBlock title="Model signal" value={evidence.model_signal} />
        <EvidenceBlock title="Peer comparison" value={evidence.peer_signals} />
        <EvidenceBlock title="Network evidence" value={evidence.graph_signals} />
        <EvidenceBlock title="Source lineage" value={(evidence.claim as Record<string, unknown> | undefined)?.source_filename ? evidence.claim : evidence.claim} />
      </div>

      <section className="notes-panel">
        <h2>Investigator notes</h2>
        {notesQuery.isLoading ? <LoadingState label="Loading notes" /> : null}
        {notesQuery.data && notesQuery.data.length === 0 ? <p>No notes have been recorded for this case.</p> : null}
        {notesQuery.data ? (
          <ol className="note-list">
            {notesQuery.data.map((item) => (
              <li key={item.id}>
                <p>{item.body}</p>
                <small>{formatDate(item.created_at)}</small>
              </li>
            ))}
          </ol>
        ) : null}
        <form
          className="note-form"
          onSubmit={(event) => {
            event.preventDefault();
            if (note.trim()) addNote.mutate();
          }}
        >
          <label>
            Add note
            <textarea value={note} maxLength={4000} required onChange={(event) => setNote(event.target.value)} />
          </label>
          {addNote.isError ? <StatusMessage type="error">{addNote.error.message}</StatusMessage> : null}
          {addNote.isSuccess ? <StatusMessage type="success">Note added to the audit trail.</StatusMessage> : null}
          <button className="button button-primary" type="submit" disabled={addNote.isPending}>Save note</button>
        </form>
      </section>
    </main>
  );
}

function ProviderPage() {
  const { providerId = "" } = useParams();
  const provider = useQuery({
    queryKey: ["provider", providerId],
    queryFn: () => api.provider(providerId),
    enabled: Boolean(providerId),
  });
  const graph = useQuery({
    queryKey: ["provider-graph", providerId],
    queryFn: () => api.providerGraph(providerId),
    enabled: Boolean(providerId),
  });
  useDocumentTitle("Provider " + providerId + " | ClaimGraph PI");

  return (
    <main className="workspace-shell">
      <Link className="back-link" to="/queue">Back to queue</Link>
      <p className="eyebrow">Synthetic provider profile</p>
      <h1>{providerId}</h1>
      <p className="page-intro">
        DE-SynPUF provider identifiers are synthetic. This profile shows behavioral and network context for investigation methodology only.
      </p>

      {provider.isLoading ? <LoadingState label="Loading provider profile" /> : null}
      {provider.isError ? <StatusMessage type="error">{provider.error.message}</StatusMessage> : null}
      {provider.data ? <EvidenceBlock title="Provider metrics" value={provider.data} /> : null}

      <section className="graph-panel">
        <div className="section-heading">
          <p className="eyebrow">Relationship graph</p>
          <h2>Claims and synthetic members connected to this provider</h2>
        </div>
        {graph.isLoading ? <LoadingState label="Loading relationship graph" /> : null}
        {graph.isError ? <StatusMessage type="error">{graph.error.message}</StatusMessage> : null}
        {graph.data ? (
          <>
            <Suspense fallback={<LoadingState label="Preparing relationship graph" />}>
              <NetworkGraph data={graph.data} />
            </Suspense>
            {graph.data.truncated ? <StatusMessage type="info">The network view is bounded for safe interactive exploration.</StatusMessage> : null}
          </>
        ) : null}
      </section>
    </main>
  );
}

function MethodologyPage() {
  useDocumentTitle("Methodology | ClaimGraph PI");
  return (
    <main className="article-shell">
      <p className="eyebrow">Methodology</p>
      <h1>How ClaimGraph PI constructs investigation evidence</h1>
      <p className="lede">
        The system preserves deterministic, statistical, machine-learning, graph, financial, and lineage evidence independently so investigators can inspect the source of a case priority.
      </p>
      <h2>Data foundation</h2>
      <p>Development uses CMS DE-SynPUF Carrier Claims. The dataset is synthetic and cannot support real Medicare fraud prevalence or provider misconduct conclusions.</p>
      <h2>Rules</h2>
      <p>Versioned deterministic checks identify review patterns such as duplicates, rapid repeated services, and payment consistency issues.</p>
      <h2>Peer analysis</h2>
      <p>Providers are grouped only from observable synthetic billing behavior and volume. Small cohorts do not receive robust peer-deviation scores.</p>
      <h2>Anomaly detection</h2>
      <p>An Isolation Forest supplies an unsupervised anomaly signal. It is not trained on fabricated fraud labels, and its score is not a probability of fraud.</p>
      <h2>Network analysis</h2>
      <p>Neo4j and NetworkX expose provider-member-claim relationships. Connectivity and shared-member metrics are investigation signals, not proof of wrongdoing.</p>
      <h2>Human review</h2>
      <p>Case status and disposition remain investigator actions. ClaimGraph PI does not automatically deny or approve claims.</p>
    </main>
  );
}

function PrivacyPage() {
  useDocumentTitle("Privacy Policy | ClaimGraph PI");
  return (
    <main className="article-shell">
      <p className="eyebrow">Legal</p>
      <h1>Privacy Policy</h1>
      <p>Last updated: October 4, 2026</p>
      <h2>Data used by the demonstration</h2>
      <p>ClaimGraph PI uses public synthetic CMS DE-SynPUF claims data. The public demonstration is not designed to receive real protected health information.</p>
      <h2>Account information</h2>
      <p>If account access is enabled, the application stores the email address you provide, a one-way password hash, session metadata, verification/reset token hashes, and audit events needed to secure the account.</p>
      <h2>Application telemetry</h2>
      <p>Optional analytics may record page and workflow event names after consent. Claims payloads, passwords, authentication tokens, and synthetic beneficiary identifiers are excluded from analytics events.</p>
      <h2>Cookies</h2>
      <p>Secure application cookies are used for authenticated sessions and CSRF protection. Optional analytics consent is stored in your browser.</p>
      <h2>Retention and deletion</h2>
      <p>This portfolio demonstration retains operational records only as required for the configured environment. Repository code does not include production user data or secrets.</p>
      <h2>Contact</h2>
      <p>Questions or bug reports can be submitted through the repository support link on the Support page.</p>
    </main>
  );
}

function TermsPage() {
  useDocumentTitle("Terms of Service | ClaimGraph PI");
  return (
    <main className="article-shell">
      <p className="eyebrow">Legal</p>
      <h1>Terms of Service</h1>
      <p>Last updated: October 4, 2026</p>
      <h2>Purpose</h2>
      <p>ClaimGraph PI is a software demonstration for healthcare payment-integrity investigation workflows using synthetic data.</p>
      <h2>No clinical or payment decision</h2>
      <p>The service is not medical advice, does not determine eligibility or coverage, and must not be used as the sole basis for approving, denying, or recovering a healthcare claim.</p>
      <h2>Data restrictions</h2>
      <p>Do not upload or submit real patient protected health information, confidential payer data, credentials, or other sensitive production records to the public demonstration.</p>
      <h2>Acceptable use</h2>
      <p>Do not attempt unauthorized access, bypass rate limits, interfere with service availability, or use the demonstration to make claims about real providers or beneficiaries.</p>
      <h2>Availability</h2>
      <p>The demonstration may change or become unavailable and is provided without a production service-level commitment.</p>
      <h2>Open-source code</h2>
      <p>Repository source code is licensed under the Apache License 2.0. These service terms apply to the hosted demonstration, not to rights separately granted by the software license.</p>
    </main>
  );
}

function SupportPage() {
  useDocumentTitle("Support and Bug Reports | ClaimGraph PI");
  return (
    <main className="article-shell">
      <p className="eyebrow">Support</p>
      <h1>Support and bug reports</h1>
      <p className="lede">Use the public repository issue tracker for reproducible bugs, documentation problems, or security-neutral product feedback.</p>
      <a
        className="button button-primary"
        href="https://github.com/SomeshZanwar/ClaimGraph-PI/issues/new"
        target="_blank"
        rel="noreferrer"
      >
        Open a bug report
      </a>
      <h2>Security-sensitive reports</h2>
      <p>Do not post passwords, tokens, real healthcare data, or exploitable secrets in a public issue. Remove sensitive material before sharing reproduction details.</p>
      <h2>Useful bug details</h2>
      <p>Include the affected route, expected behavior, observed behavior, browser or environment, and a minimal reproduction that contains no sensitive data.</p>
    </main>
  );
}

function NotFoundPage({ user }: { user: User | null }) {
  useDocumentTitle("Page Not Found | ClaimGraph PI");
  return (
    <main className="narrow-shell">
      <section className="form-panel">
        <p className="eyebrow">404</p>
        <h1>Page not found</h1>
        <p>The requested page does not exist or is no longer available.</p>
        <Link className="button button-primary" to={user ? "/queue" : "/"}>
          {user ? "Return to investigation queue" : "Return home"}
        </Link>
      </section>
    </main>
  );
}

function App() {
  const me = useQuery({
    queryKey: ["me"],
    queryFn: api.me,
    retry: false,
  });
  const user = me.data || null;

  return (
    <div className="app-frame">
      <TelemetryTracker />
      <AppHeader user={user} />
      <Routes>
        <Route path="/" element={<HomePage user={user} />} />
        <Route path="/about" element={<MethodologyPage />} />
        <Route path="/login" element={user ? <Navigate to="/queue" replace /> : <LoginPage />} />
        <Route path="/signup" element={user ? <Navigate to="/queue" replace /> : <SignupPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route
          path="/queue"
          element={<ProtectedRoute user={user} loading={me.isLoading}><QueuePage /></ProtectedRoute>}
        />
        <Route
          path="/cases/:caseId"
          element={<ProtectedRoute user={user} loading={me.isLoading}><CasePage /></ProtectedRoute>}
        />
        <Route
          path="/providers/:providerId"
          element={<ProtectedRoute user={user} loading={me.isLoading}><ProviderPage /></ProtectedRoute>}
        />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/terms" element={<TermsPage />} />
        <Route path="/support" element={<SupportPage />} />
        <Route path="*" element={<NotFoundPage user={user} />} />
      </Routes>
      <AppFooter />
      <CookieBanner />
    </div>
  );
}

export default App;
