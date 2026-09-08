import { test, expect } from "@playwright/test";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";


test.describe("Book Loop — protected routes and session expiry", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  for (const path of ["/dashboard", "/studio", "/account"]) {
    test(`${path} redirects unauthenticated users to login`, async ({ page }) => {
      await page.goto(path);
      await expect(page).toHaveURL(new RegExp(`/login\\?next=${encodeURIComponent(path).replace(/[.*+?^${}()|[\\]\\]/g, "\\$&")}$`));
    });
  }

  test("an invalidated session cannot reopen Studio and preserves the destination", async ({ page }) => {
    const email = `protected-e2e-${Date.now()}@bookloop-e2e.com`;
    const password = "BookLoop-Protected-123!";

    await page.goto("/register");
    const cookieBanner = page.getByRole("complementary", { name: "Préférences de cookies" });
    if (await cookieBanner.isVisible()) {
      await cookieBanner.getByRole("button", { name: "Refuser" }).click();
      await expect(cookieBanner).toBeHidden();
    }

    await page.getByLabel("Nom complet / Pseudonyme d'auteur").fill("Protected E2E Author");
    await page.getByLabel("Adresse e-mail").fill(email);
    await page.getByLabel("Mot de passe").fill(password);
    await page.getByRole("button", { name: "Créer mon compte" }).click();
    await expect(page).toHaveURL(/\/setup$/);

    await page.goto("/studio?bookId=session-expiry-test");
    await expect(page).toHaveURL(/\/studio\?bookId=session-expiry-test$/);

    await page.context().clearCookies();
    await page.goto("/studio?bookId=session-expiry-test");
    await expect(page).toHaveURL(/\/login\?next=%2Fstudio%3FbookId%3Dsession-expiry-test$/);

    await page.getByLabel("Adresse e-mail").fill(email);
    await page.getByLabel("Mot de passe").fill(password);
    await page.getByRole("button", { name: "Connexion" }).click();
    await expect(page).toHaveURL(/\/studio\?bookId=session-expiry-test$/);
  });
});
