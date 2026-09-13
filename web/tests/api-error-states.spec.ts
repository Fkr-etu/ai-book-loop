import { test, expect } from "@playwright/test";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";

test.describe("Book Loop — frontend API error states", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  for (const scenario of [
    { status: 401, message: "Votre session a expiré. Reconnectez-vous pour continuer.", action: "Se reconnecter", actionType: "link" as const },
    { status: 403, message: "Vous n’avez pas accès à ce livre.", action: "Réessayer", actionType: "button" as const },
    { status: 404, message: "Ce livre n’existe plus ou n’est plus disponible.", action: "Réessayer", actionType: "button" as const },
  ]) {
    test(`${scenario.status} shows a contextual Studio error`, async ({ page }) => {
      // Browser API calls use the same-origin Next.js rewrite so session cookies
      // stay on the web origin. Mock that public origin, not localhost:8000.
      await page.route("**/api/auth/me", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            id: "e2e-user",
            email: "e2e@bookloop.test",
            name: "E2E User",
          }),
        });
      });

      await page.route("**/api/books/**", async (route) => {
        await route.fulfill({
          status: scenario.status,
          contentType: "application/json",
          body: JSON.stringify({ detail: "backend detail should not leak into the contextual UI" }),
        });
      });

      await page.goto(`/studio?bookId=error-state-${scenario.status}`);

      const errorAlert = page.getByTestId("studio-api-error");
      await expect(errorAlert).toContainText(scenario.message);
      if (scenario.actionType === "link") {
        await expect(page.getByRole("link", { name: scenario.action })).toBeVisible();
      } else {
        await expect(page.getByRole("button", { name: scenario.action })).toBeVisible();
      }
    });
  }
});
