import { test, expect } from "@playwright/test";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";
const password = "BookLoop-Auth-123!";

test.describe("Book Loop — authentication journey", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  test("registers, restores the session, logs out, rejects bad credentials and logs back in", async ({ page }) => {
    const email = `auth-e2e-${Date.now()}@bookloop-e2e.com`;

    await page.goto("/register");
    const cookieBanner = page.getByRole("complementary", { name: "Préférences de cookies" });
    if (await cookieBanner.isVisible()) {
      await cookieBanner.getByRole("button", { name: "Refuser" }).click();
      await expect(cookieBanner).toBeHidden();
    }

    await page.getByLabel("Nom complet / Pseudonyme d'auteur").fill("Auth E2E Author");
    await page.getByLabel("Adresse e-mail").fill(email);
    await page.getByLabel("Mot de passe").fill(password);
    await page.getByRole("button", { name: "Créer mon compte" }).click();
    await expect(page).toHaveURL(/\/setup$/);

    const meAfterRegister = await page.request.get("/api/auth/me");
    expect(meAfterRegister.ok()).toBeTruthy();
    expect((await meAfterRegister.json()).user.email).toBe(email);

    await page.goto("/account");
    await expect(page.getByRole("heading", { name: "Mon abonnement" })).toBeVisible();
    await expect(page.getByText(email)).toBeVisible();

    await page.getByRole("button", { name: "Se déconnecter" }).click();
    await expect(page).toHaveURL(/\/login$/);

    const meAfterLogout = await page.request.get("/api/auth/me");
    expect(meAfterLogout.status()).toBe(401);

    await page.getByLabel("Adresse e-mail").fill(email);
    await page.getByLabel("Mot de passe").fill("Wrong-Password-123!");
    await page.getByRole("button", { name: "Connexion" }).click();
    await expect(page.getByRole("alert")).toContainText("Adresse e-mail ou mot de passe incorrect.");
    await expect(page).toHaveURL(/\/login$/);

    await page.getByLabel("Mot de passe").fill(password);
    await page.getByRole("button", { name: "Connexion" }).click();
    await expect(page).toHaveURL(/\/studio$/);

    const meAfterLogin = await page.request.get("/api/auth/me");
    expect(meAfterLogin.ok()).toBeTruthy();
    expect((await meAfterLogin.json()).user.email).toBe(email);

    await page.reload();
    await expect(page).toHaveURL(/\/studio$/);
  });

  test("exposes working legal destinations from registration", async ({ page }) => {
    await page.goto("/register");

    await page.getByRole("link", { name: "Conditions d'utilisation" }).click();
    await expect(page).toHaveURL(/\/terms$/);
    await expect(page.getByRole("heading", { name: "Conditions d’utilisation" })).toBeVisible();

    await page.getByRole("link", { name: "Consulter la politique de confidentialité" }).click();
    await expect(page).toHaveURL(/\/privacy$/);
    await expect(page.getByRole("heading", { name: "Politique de confidentialité" })).toBeVisible();
  });
});
