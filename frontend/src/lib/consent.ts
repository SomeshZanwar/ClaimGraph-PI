const CONSENT_KEY = "claimgraph_analytics_consent";

export function getAnalyticsConsent(): "granted" | "denied" | null {
  const value = localStorage.getItem(CONSENT_KEY);
  return value === "granted" || value === "denied" ? value : null;
}

export function setAnalyticsConsent(value: "granted" | "denied"): void {
  localStorage.setItem(CONSENT_KEY, value);
}

export function clearAnalyticsConsent(): void {
  localStorage.removeItem(CONSENT_KEY);
}
