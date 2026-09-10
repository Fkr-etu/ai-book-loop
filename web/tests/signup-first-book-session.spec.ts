import { test, expect } from "@playwright/test";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";
const password = "BookLoop-Auth-123!";
const apiBaseUrl = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");

test.describe("Book Loop — signup to first book", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  test("keeps the signup session when creating the first book", async ({ page }) => {
    const email = `signup-book-e2e-${Date.now()}@bookloop-e2e.com`;

    await page.goto("/register");
    const cookieBanner = page.getByRole("complementary", { name: "Préférences de cookies" });
    if (await cookieBanner.isVisible()) {
      await cookieBanner.getByRole("button", { name: "Refuser" }).click();
      await expect(cookieBanner).toBeHidden();
    }

    await page.getByLabel("Nom complet / Pseudonyme d'auteur").fill("Signup E2E Author");
    await page.getByLabel("Adresse e-mail").fill(email);
    await page.getByLabel("Mot de passe").fill(password);
    await page.getByRole("button", { name: "Créer mon compte" }).click();
    await expect(page).toHaveURL(/\/setup$/);

    const meAfterRegister = await page.request.get(`${apiBaseUrl}/api/auth/me`);
    expect(meAfterRegister.ok()).toBeTruthy();
    expect((await meAfterRegister.json()).user.email).toBe(email);

    const createBookResponsePromise = page.waitForResponse(
      (response) => response.url() === `${apiBaseUrl}/api/books` && response.request().method() === "POST",
    );
    await page.getByRole("button", { name: "C’est bien ça — commencer l’atelier" }).click();
    const createBookResponse = await createBookResponsePromise;
    expect(createBookResponse.ok(), `POST /api/books returned ${createBookResponse.status()}`).toBeTruthy();
  });
});
