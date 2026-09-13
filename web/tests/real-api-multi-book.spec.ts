import { test, expect } from "@playwright/test";

const realApiEnabled = process.env.NEXT_PUBLIC_USE_REAL_API === "true";

const secondBook = {
  id: "multi-book-second-e2e",
  owner_id: "e2e-multi-book",
  title: "Livre B — récit sélectionné",
  theme: "Science-fiction",
  author_idea: "Deuxième projet de test multi-livres.",
  creative_brief: null,
  lore: "",
  constraints: [],
  outline: null,
  outline_approved: false,
  chapters: [],
};

test.describe("Book Loop — real API multi-book selection", () => {
  test.skip(!realApiEnabled, "Requires NEXT_PUBLIC_USE_REAL_API=true");

  test("selects the second book and keeps it selected after refresh", async ({ page }) => {
    const email = `e2e-multi-book-${Date.now()}@bookloop-e2e.com`;
    const password = "BookLoop-E2E-123!";

    await page.goto("/register");
    const cookieBanner = page.getByRole("complementary", { name: "Préférences de cookies" });
    if (await cookieBanner.isVisible()) {
      await cookieBanner.getByRole("button", { name: "Refuser" }).click();
      await expect(cookieBanner).toBeHidden();
    }

    await page.getByPlaceholder("Votre nom ou pseudonyme").fill("E2E Multi Book Author");
    await page.getByPlaceholder("votre@email.com").fill(email);
    await page.getByLabel("Mot de passe").fill(password);
    await page.getByRole("button", { name: "Créer mon compte" }).click();
    await expect(page).toHaveURL(/\/setup$/);

    await page.getByLabel("Comment appelez-vous votre projet ?").fill("Livre A — premier récit");
    await page.getByRole("button", { name: "Fantasy" }).click();
    await page.getByLabel("De quoi parle votre histoire ?").fill("Premier projet de test multi-livres.");
    await page.getByTestId("next-step-btn").click();
    await page.getByLabel("Qu'aimeriez-vous faire ressentir, raconter ou explorer ?").fill("Construire un premier récit.");
    await page.getByTestId("next-step-btn").click();
    await page.getByRole("button", { name: "Voir la synthèse" }).click();
    await page.getByRole("button", { name: /C’est bien ça — commencer l’atelier/ }).click();
    await expect(page).toHaveURL(/\/studio\?bookId=/);

    await page.goto("/dashboard");
    await expect(page.getByText("Vos récits (1)")).toBeVisible();

    await page.route("/api/books", async (route) => {
      if (route.request().method() !== "POST") {
        await route.continue();
        return;
      }
      const body = route.request().postDataJSON() as { title?: string };
      if (body.title !== secondBook.title) {
        await route.continue();
        return;
      }
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(secondBook) });
    });
    await page.route(`/api/books/${secondBook.id}`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(secondBook) });
    });

    await page.getByRole("link", { name: "Commencer un livre" }).click();
    await expect(page).toHaveURL(/\/setup$/);
    await page.getByLabel("Comment appelez-vous votre projet ?").fill(secondBook.title);
    await page.getByRole("button", { name: "Science-fiction" }).click();
    await page.getByLabel("De quoi parle votre histoire ?").fill(secondBook.author_idea);
    await page.getByTestId("next-step-btn").click();
    await page.getByTestId("next-step-btn").click();
    await page.getByRole("button", { name: "Voir la synthèse" }).click();
    await page.getByRole("button", { name: /C’est bien ça — commencer l’atelier/ }).click();

    await expect(page).toHaveURL(/\/studio\?bookId=multi-book-second-e2e/);
    await expect(page.getByText(secondBook.title, { exact: true })).toBeVisible();

    const selectedBookUrl = page.url();
    await page.reload();
    await expect(page).toHaveURL(selectedBookUrl);
    await expect(page.getByText(secondBook.title, { exact: true })).toBeVisible();
    await expect(page.getByText("Livre A — premier récit", { exact: true })).not.toBeVisible();
  });
});
