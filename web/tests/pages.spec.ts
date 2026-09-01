import { test, expect } from "@playwright/test";

test.describe("Manuscript Studio - Complete Page Coverage Suite", () => {
  test("1. Login Page (/login) renders and allows navigation", async ({ page }) => {
    await page.goto("/login");
    await expect(page).toHaveTitle(/Manuscript Studio/);
    await expect(page.getByRole("heading", { name: "Manuscript Studio" })).toBeVisible();
    await expect(page.getByPlaceholder("auteur@manuscript.studio")).toBeVisible();
    await expect(page.getByRole("button", { name: "Connexion" })).toBeVisible();
    await page.screenshot({ path: "tests/screenshots/01_login.png" });
  });

  test("2. Register Page (/register) renders and plan toggle works", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByRole("heading", { name: "Créer votre espace d'écrivain" })).toBeVisible();
    await expect(page.getByText("Standard")).toBeVisible();
    await expect(page.getByText("Pro Studio")).toBeVisible();

    await page.getByText("Standard").click();
    await page.screenshot({ path: "tests/screenshots/02_register.png" });
  });

  test("3. Project Setup Wizard (/setup) step-by-step flow", async ({ page }) => {
    await page.goto("/setup");
    await expect(page.getByText("Titre, Genre & Thème du Livre")).toBeVisible();

    await page.getByPlaceholder("Ex: La Porte d'Obsidienne").fill("Mon Livre de Test");

    await page.getByTestId("next-step-btn").click();
    await expect(page.getByText("Règles, Reliques et Lieux Canoniques")).toBeVisible();

    await page.getByTestId("next-step-btn").click();
    await expect(page.getByText("Ton, Voix Narrative & Verrouillage Canon")).toBeVisible();

    await page.screenshot({ path: "tests/screenshots/03_setup.png" });
  });

  test("4. Atelier de Rédaction / Main Studio Desk (/studio)", async ({ page }) => {
    await page.goto("/studio");
    await expect(page.getByText("Atelier de Conception")).toBeVisible();
    await expect(page.getByRole("button", { name: /Critique & Validation IA/ })).toBeVisible();
    await expect(page.getByText("Manuscript Studio — Parchment Canvas")).toBeVisible();

    const canvas = page.locator("textarea");
    await expect(canvas).toBeVisible();
    await canvas.type("\n\nUn nouveau paragraphe rédigé pendant le test automatique.");

    await page.screenshot({ path: "tests/screenshots/04_studio_desk.png" });
  });

  test("5. Outline Structure Editor (/studio/outline)", async ({ page }) => {
    await page.goto("/studio/outline");
    await expect(page.getByRole("heading", { name: "Éditeur de Plan Global" })).toBeVisible();
    await expect(page.getByText("Le Murmure du Parchemin")).toBeVisible();

    await page.getByRole("button", { name: "Nouveau Chapitre" }).click();
    await page.getByPlaceholder("Titre du Chapitre (ex: Le Scriptorium Oublié)").fill("Chapitre Automatisé");
    await page.getByRole("button", { name: "Créer le Chapitre" }).click();

    await expect(page.getByText("Chapitre Automatisé")).toBeVisible();
    await page.screenshot({ path: "tests/screenshots/05_outline.png" });
  });

  test("6. Character Deep Editor (/studio/characters)", async ({ page }) => {
    await page.goto("/studio/characters");
    await expect(page.getByRole("heading", { name: "Éditeur de Personnages Profonds" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Archiviste Valerius" })).toBeVisible();

    await page.getByRole("button", { name: "Nouveau Personnage" }).click();
    await page.getByPlaceholder("Nom complet (ex: Lyra Vane)").fill("Eldrin le Scribe");
    await page.getByRole("button", { name: "Enregistrer le Profil" }).click();

    await expect(page.getByText("Eldrin le Scribe")).toBeVisible();
    await page.screenshot({ path: "tests/screenshots/06_characters.png" });
  });

  test("7. World Bible / Lore (/studio/lore)", async ({ page }) => {
    await page.goto("/studio/lore");
    await expect(page.getByRole("heading", { name: "Ancrage du Lore & Codex" })).toBeVisible();
    await expect(page.getByText("L'Obsidienne Stellaire")).toBeVisible();

    await page.getByRole("button", { name: "Ajouter une Entrée Canon" }).click();
    await page.getByPlaceholder("Titre de l'entrée (ex: Citadelle de Cendres)").fill("Lame d'Éther");
    await page.getByRole("button", { name: "Verrouiller dans le Codex" }).click();

    await expect(page.getByText("Lame d'Éther")).toBeVisible();
    await page.screenshot({ path: "tests/screenshots/07_lore.png" });
  });

  test("8. Lore Relationship Graph (/studio/lore-graph)", async ({ page }) => {
    await page.goto("/studio/lore-graph");
    await expect(page.getByRole("heading", { name: "Graphe de Relations Lore & Personnages" })).toBeVisible();
    await expect(page.locator(".react-flow")).toBeVisible();

    await page.screenshot({ path: "tests/screenshots/08_lore_graph.png" });
  });

  test("9. Creative Intention Lab (/studio/intention-lab)", async ({ page }) => {
    await page.goto("/studio/intention-lab");
    await expect(page.getByRole("heading", { name: "Laboratoire d'Intention" })).toBeVisible();
    await expect(page.getByText("Directives Actives")).toBeVisible();

    await page.getByPlaceholder("Ex: Ne pas utiliser de mots argotiques modernes").fill("Pas de jargon moderne");
    await page.getByRole("button", { name: "Injecter la Contrainte" }).click();

    await expect(page.getByText("Pas de jargon moderne")).toBeVisible();
    await page.screenshot({ path: "tests/screenshots/09_intention_lab.png" });
  });

  test("10. Validation Loop (/studio/validation-loop)", async ({ page }) => {
    await page.goto("/studio/validation-loop");
    await expect(page.getByRole("heading", { name: "Boucle de Validation & Critique" })).toBeVisible();
    await expect(page.getByRole("button", { name: /Lancer le Linter/ })).toBeVisible();

    await page.getByRole("button", { name: /Lancer le Linter/ }).click();
    await expect(page.getByText("Accepté dans le Canon")).toBeVisible();

    await page.screenshot({ path: "tests/screenshots/10_validation_loop.png" });
  });

  test("11. Pricing Page (/pricing)", async ({ page }) => {
    await page.goto("/pricing");
    await expect(page.getByRole("heading", { name: "Investissez dans la clarté de vos récits" })).toBeVisible();
    await expect(page.getByText("Auteur Indépendant")).toBeVisible();
    await expect(page.getByText("Architecte Littéraire")).toBeVisible();
    await expect(page.getByText("Maison d'Édition")).toBeVisible();

    await page.screenshot({ path: "tests/screenshots/11_pricing.png" });
  });
});
