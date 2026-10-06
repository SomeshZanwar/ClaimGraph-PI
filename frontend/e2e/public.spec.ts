import { expect, test } from "@playwright/test";

const PUBLIC_ROUTES = ["/", "/about", "/privacy", "/terms", "/support"];

test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Authentication required" }),
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

for (const route of PUBLIC_ROUTES) {
  test("public route renders without horizontal overflow: " + route, async ({ page }) => {
    await page.goto(route);
    await expect(page.locator("h1")).toBeVisible();

    const overflow = await page.evaluate(() => ({
      viewport: window.innerWidth,
      document: document.documentElement.scrollWidth,
    }));

    expect(overflow.document).toBeLessThanOrEqual(overflow.viewport + 1);
  });
}

test("custom 404 provides a working return path", async ({ page }) => {
  await page.goto("/not-a-real-page");
  await expect(page.getByRole("heading", { name: "Page not found" })).toBeVisible();

  const returnLink = page.getByRole("link", { name: "Return home" });
  await expect(returnLink).toHaveAttribute("href", "/");
});

test("public internal footer links resolve", async ({ page }) => {
  await page.goto("/");

  const hrefs = await page.locator("footer a").evaluateAll((anchors) =>
    anchors
      .map((anchor) => anchor.getAttribute("href"))
      .filter((href): href is string => Boolean(href && href.startsWith("/"))),
  );

  for (const href of hrefs) {
    await page.goto(href);
    await expect(page.locator("h1")).toBeVisible();
  }
});

test("public home page reaches interactive state quickly under local preview", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

  const timing = await page.evaluate(() => {
    const navigation = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming;
    return navigation.domContentLoadedEventEnd - navigation.startTime;
  });

  expect(timing).toBeLessThan(3000);
});


test("SEO support files are served from the built application", async ({ request }) => {
  const robots = await request.get("/robots.txt");
  expect(robots.ok()).toBeTruthy();
  expect(await robots.text()).toContain("Sitemap:");

  const sitemap = await request.get("/sitemap.xml");
  expect(sitemap.ok()).toBeTruthy();
  expect(await sitemap.text()).toContain("<urlset");

  const llms = await request.get("/llms.txt");
  expect(llms.ok()).toBeTruthy();
  expect(await llms.text()).toContain("ClaimGraph PI");
});

test("public pages expose canonical and description metadata", async ({ page }) => {
  await page.goto("/about");

  const canonical = page.locator('link[rel="canonical"]');
  await expect(canonical).toHaveAttribute("href", /\/about$/);

  const description = page.locator('meta[name="description"]');
  await expect(description).toHaveAttribute("content", /methodology|evidence|ClaimGraph/i);
});

test("mobile navigation opens and reaches support", async ({ page }, testInfo) => {
  test.skip(!testInfo.project.name.includes("mobile"), "mobile-specific navigation QA");

  await page.goto("/");
  await page.getByRole("button", { name: "Menu" }).click();
  const primaryNavigation = page.getByRole("navigation", { name: "Primary navigation" });
  await expect(primaryNavigation.getByRole("link", { name: "Support" })).toBeVisible();
  await primaryNavigation.getByRole("link", { name: "Support" }).click();
  await expect(page.getByRole("heading", { name: "Support and bug reports" })).toBeVisible();
});

test("analytics consent does not block public navigation", async ({ page }) => {
  await page.goto("/");
  const banner = page.getByRole("complementary", { name: "Analytics consent" });
  await expect(banner).toBeVisible();
  await banner.getByRole("button", { name: "Decline" }).click();
  await expect(banner).toBeHidden();

  await page.getByRole("navigation", { name: "Primary navigation" })
    .getByRole("link", { name: "Methodology", exact: true })
    .click();
  await expect(page.getByRole("heading", { name: /How ClaimGraph PI constructs/ })).toBeVisible();
});
