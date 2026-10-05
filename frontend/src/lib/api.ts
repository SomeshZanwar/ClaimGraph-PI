export type User = {
  id: string;
  email: string;
  role: string;
  email_verified: boolean;
};

export type CaseSummary = {
  id: string;
  claim_record_id: string;
  status: string;
  priority_score: string;
  priority_band: string;
  financial_exposure: string;
  strongest_signal: string | null;
  disposition: string | null;
  assigned_user_id: string | null;
  updated_at: string;
};

export type CaseDetail = CaseSummary & {
  evidence_hash: string;
  evidence: Record<string, unknown>;
  created_at: string;
};

export type CaseList = {
  items: CaseSummary[];
  meta: { page: number; page_size: number; total: number };
};

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api/v1";

function csrfToken(): string | null {
  const pair = document.cookie
    .split("; ")
    .find((item) => item.startsWith("cg_csrf="));
  return pair ? decodeURIComponent(pair.split("=", 2)[1]) : null;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const method = (options.method || "GET").toUpperCase();
  if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
    const csrf = csrfToken();
    if (csrf) headers.set("X-CSRF-Token", csrf);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // Use status-derived message when response has no JSON body.
    }
    throw new Error(message);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const api = {
  me: () => request<User>("/auth/me"),
  login: (email: string, password: string) =>
    request<{ user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  signup: (email: string, password: string) =>
    request<{ message: string }>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  verifyEmail: (token: string) =>
    request<{ message: string }>("/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ token }),
    }),
  requestPasswordReset: (email: string) =>
    request<{ message: string }>("/auth/password-reset/request", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),
  confirmPasswordReset: (token: string, newPassword: string) =>
    request<{ message: string }>("/auth/password-reset/confirm", {
      method: "POST",
      body: JSON.stringify({ token, new_password: newPassword }),
    }),
  logout: () => request<{ message: string }>("/auth/logout", { method: "POST" }),
  cases: (params = "") => request<CaseList>(`/cases${params}`),
  case: (id: string) => request<CaseDetail>(`/cases/${encodeURIComponent(id)}`),
  updateCase: (
    id: string,
    payload: { status?: string; disposition?: string; assign_to_self?: boolean },
  ) =>
    request<CaseSummary>(`/cases/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  notes: (id: string) =>
    request<Array<{
      id: string;
      case_id: string;
      author_user_id: string;
      body: string;
      created_at: string;
    }>>(`/cases/${encodeURIComponent(id)}/notes`),
  addNote: (id: string, body: string) =>
    request(`/cases/${encodeURIComponent(id)}/notes`, {
      method: "POST",
      body: JSON.stringify({ body }),
    }),
  provider: (id: string) =>
    request<Record<string, unknown>>(`/providers/${encodeURIComponent(id)}`),
  providerGraph: (id: string) =>
    request<{
      provider_npi: string;
      nodes: Array<{ id: string; type: string; label: string }>;
      edges: Array<{ source: string; target: string; type: string }>;
      truncated: boolean;
    }>(`/graph/providers/${encodeURIComponent(id)}`),
  track: (
    eventName: string,
    route: string,
    properties: Record<string, string | number | boolean | null> = {},
  ) =>
    request<{ status: string }>("/telemetry/events", {
      method: "POST",
      body: JSON.stringify({
        event_name: eventName,
        route,
        properties,
      }),
    }),
};
