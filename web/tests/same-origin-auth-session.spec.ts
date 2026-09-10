import { test, expect } from "@playwright/test";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";
const password = "BookLoop-Auth-123!";

test.describe("Book Loop — same-origin auth session", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  test("keeps the login session on /me and first book creation", async ({ page }) => {
    const email = `same-origin-login-e2e-${Date.now()}@bookloop-e2e.com`;

    await page.goto("/register");
    const cookieBanner = page.getByRole("complementary", { name: "Préférences de cookies" });
    if (await cookieBanner.isVisible()) {
      await cookieBanner.getByRole("button", { name: "Refuser" }).click();
      await expect(cookieBanner).toBeHidden();
    }

    await page.getByLabel("Nom complet / Pseudonyme d'auteur").fill("Same Origin E2E Author");
    await page.getByLabel("Adresse e-mail").fill(email);
    await page.getByLabel("Mot de passe").fill(password);
    await page.getByRole("button", { name: "Créer mon compte" }).click();
    await expect(page).toHaveURL(/\/setup$/);

    const meAfterRegister = await page.request.get(new URL("/api/auth/me", page.url()).toString());
    expect(meAfterRegister.ok()).toBeTruthy();
    expect((await meAfterRegister.json()).user.email).toBe(email);

    await page.goto("/login");
    await page.getByLabel("Adresse e-mail").fill(email);
    await page.getByLabel("Mot de passe").fill(password);
    await page.getByRole("button", { name: "Se connecter" }).click();
    await expect(page).toHaveURL(/\/studio$/);

    const meAfterLogin = await page.request.get(new URL("/api/auth/me", page.url()).toString());
    expect(meAfterLogin.ok()).toBeTruthy();
    expect((await meAfterLogin.json()).user.email).toBe(email);

    await page.goto("/setup");
    const createBookResponsePromise = page.waitForResponse(
      (response) => response.url().endsWith("/api/books") && response.request().method() === "POST",
    );
    await page.getByRole("button", { name: "C’est bien ça — commencer l’atelier" }).click();
    const createBookResponse = await createBookResponsePromise;
    expect(createBookResponse.ok(), `POST /api/books returned ${createBookResponse.status()}`).toBeTruthy();
  });
});
