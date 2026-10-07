import { expect, test } from "@playwright/test";
import { expectAccessible } from "./accessibility";

const caseId = "11111111-1111-1111-1111-111111111111";
const providerId = "DEMO_NPI_0001";

test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: "22222222-2222-2222-2222-222222222222",
        email: "demo-investigator@example.test",
        role: "INVESTIGATOR",
        email_verified: true,
      }),
    });
  });

  await page.route("**/api/v1/cases?*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: [
          {
            id: caseId,
            claim_record_id: "DEMO_CLAIM_001",
            status: "NEW",
            priority_score: "68.50",
            priority_band: "HIGH",
            financial_exposure: "725.50",
            strongest_signal: "Deterministic duplicate pattern",
            disposition: null,
            assigned_user_id: null,
            updated_at: "2026-10-04T18:00:00Z",
          },
        ],
        meta: { page: 1, page_size: 25, total: 1 },
      }),
    });
  });

  await page.route("**/api/v1/cases", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: [
          {
            id: caseId,
            claim_record_id: "DEMO_CLAIM_001",
            status: "NEW",
            priority_score: "68.50",
            priority_band: "HIGH",
            financial_exposure: "725.50",
            strongest_signal: "Deterministic duplicate pattern",
            disposition: null,
            assigned_user_id: null,
            updated_at: "2026-10-04T18:00:00Z",
          },
        ],
        meta: { page: 1, page_size: 25, total: 1 },
      }),
    });
  });

  await page.route(`**/api/v1/cases/${caseId}/notes`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: "[]",
    });
  });

  await page.route(`**/api/v1/cases/${caseId}`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: caseId,
        claim_record_id: "DEMO_CLAIM_001",
        status: "NEW",
        priority_score: "68.50",
        priority_band: "HIGH",
        financial_exposure: "725.50",
        strongest_signal: "Deterministic duplicate pattern",
        disposition: null,
        assigned_user_id: null,
        updated_at: "2026-10-04T18:00:00Z",
        created_at: "2026-10-04T17:00:00Z",
        evidence_hash: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        evidence: {
          providers: [providerId],
          rule_signals: [{ rule_id: "CG-DUP-001", severity: "HIGH" }],
          model_signal: { anomaly_score: 0.62 },
          peer_signals: { status: "COMPARABLE" },
          graph_signals: { shared_provider_count: 2 },
          claim: { source_filename: "demo.zip" },
        },
      }),
    });
  });

  await page.route(`**/api/v1/providers/${providerId}`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        provider_npi: providerId,
        peer_metrics: { peer_comparison_status: "COMPARABLE" },
        graph_metrics: { member_count: 8, shared_provider_count: 2 },
        linked_case_count: 1,
        total_claim_count: 12,
        total_allowed_charge: "3400.00",
      }),
    });
  });

  await page.route(`**/api/v1/graph/providers/${providerId}`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        provider_npi: providerId,
        nodes: [
          { id: `provider:${providerId}`, type: "provider", label: providerId },
          { id: "claim:demo", type: "claim", label: "DEMO_CLAIM_001" },
          { id: "member:demo", type: "member", label: "DEMO_BENE_001" },
        ],
        edges: [
          { source: "claim:demo", target: `provider:${providerId}`, type: "BILLED_BY" },
          { source: "member:demo", target: "claim:demo", type: "HAS_CLAIM" },
        ],
        truncated: false,
      }),
    });
  });

  await page.route("**/api/v1/telemetry/events", async (route) => {
    await route.fulfill({
      status: 202,
      contentType: "application/json",
      body: JSON.stringify({ status: "accepted" }),
    });
  });
});

async function expectNoPageOverflow(page: import("@playwright/test").Page) {
  const overflow = await page.evaluate(() => ({
    viewport: window.innerWidth,
    document: document.documentElement.scrollWidth,
  }));
  expect(overflow.document).toBeLessThanOrEqual(overflow.viewport + 1);
  await expectAccessible(page);
}

test("investigation queue is usable without page overflow", async ({ page }) => {
  await page.goto("/queue");
  await expect(page.getByRole("heading", { name: "Case queue" })).toBeVisible();
  await expect(page.getByRole("link", { name: "DEMO_CLAIM_001" })).toBeVisible();
  await expectNoPageOverflow(page);
});

test("case evidence page renders workflow and evidence without page overflow", async ({ page }) => {
  await page.goto(`/cases/${caseId}`);
  await expect(page.getByRole("heading", { name: "Claim DEMO_CLAIM_001" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Deterministic signals" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Assign to me" })).toBeVisible();
  await expectNoPageOverflow(page);
});

test("provider network page renders bounded graph without page overflow", async ({ page }) => {
  await page.goto(`/providers/${providerId}`);
  await expect(page.getByRole("heading", { name: providerId })).toBeVisible();
  await expect(page.locator(".network-canvas")).toBeVisible();
  await expectNoPageOverflow(page);
});
