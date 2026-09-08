import { test, expect } from "@playwright/test";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";
const apiBaseUrl = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");

test.describe("Book Loop — frontend API error states", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  for (const scenario of [
    { status: 401, message: "Votre session a expiré. Reconnectez-vous pour continuer.", action: "Se reconnecter" },
    { status: 403, message: "Vous n’avez pas accès à ce livre.", action: "Réessayer" },
    { status: 404, message: "Ce livre n’existe plus ou n’est plus disponible.", action: "Réessayer" },
  ]) {
    test(`${scenario.status} shows a contextual Studio error`, async ({ page }) => {
      await page.route(`${apiBaseUrl}/api/books/**`, async (route) => {
        await route.fulfill({
          status: scenario.status,
          contentType: "application/json",
          body: JSON.stringify({ detail: "backend detail should not leak into the contextual UI" }),
        });
      });

      await page.goto(`/studio?bookId=error-state-${scenario.status}`);

      await expect(page.getByRole("alert")).toContainText(scenario.message);
      await expect(page.getByRole("button", { name: scenario.action })).toBeVisible().catch(async () => {
        await expect(page.getByRole("link", { name: scenario.action })).toBeVisible();
      });
    });
  }
});
