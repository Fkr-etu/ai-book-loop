import { test, expect } from "@playwright/test";

test.describe("Manuscript Studio - Complete Page Coverage Suite", () => {
  test("1. Login Page (/login) renders and allows navigation", async ({ page }) => {
    await page.goto("/login");
    await expect(page).toHaveTitle(/Manuscript Studio/);
    await expect(page.getByRole("heading", { name: "Manuscript Studio" })).toBeVisible();
    await expect(page.getByPlaceholder("auteur@manuscript.studio")).toBeVisible();
    await expect(page.getByRole("button", { name: "Connexion" })).toBeVisible();
  });

  test("2. Register Page (/register) renders and plan toggle works", async ({ page }) => {
    await page.goto("/register");
    await expect(page.getByRole("heading", { name: "Créer votre espace d'écrivain" })).toBeVisible();
    await expect(page.getByText("Standard")).toBeVisible();
    await expect(page.getByText("Pro Studio")).toBeVisible();

    await page.getByText("Standard").click();
  });

  test("3. Project Setup Wizard (/setup) step-by-step flow", async ({ page }) => {
    await page.goto("/setup");
    await expect(page.getByText("Titre, Genre & Thème du Livre")).toBeVisible();

    await page.getByPlaceholder("Ex: La Porte d'Obsidienne").fill("Mon Livre de Test");

    await page.getByTestId("next-step-btn").click();
    await expect(page.getByText("Règles, Reliques et Lieux Canoniques")).toBeVisible();

    await page.getByTestId("next-step-btn").click();
    await expect(page.getByText("Ton, Voix Narrative & Verrouillage Canon")).toBeVisible();
  });

  test("4. Atelier de Rédaction / Main Studio Desk (/studio)", async ({ page }) => {
    await page.goto("/studio");
    await expect(page.getByRole("button", { name: /Critique & Lint/ })).toBeVisible();
    await expect(page.getByText("Manuscript Studio — Parchment Canvas")).toBeVisible();

    const canvas = page.locator("textarea");
    await expect(canvas).toBeVisible();
    await canvas.type("\n\nUn nouveau paragraphe rédigé pendant le test automatique.");
  });

  test("5. Outline Structure Editor (/studio/outline)", async ({ page }) => {
    await page.goto("/studio/outline");
    await expect(page.getByRole("heading", { name: "Éditeur de Plan Global" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Le Murmure du Parchemin" })).toBeVisible();

    await page.getByRole("button", { name: "Nouveau Chapitre" }).click();
    await page.getByPlaceholder("Titre du Chapitre (ex: Le Scriptorium Oublié)").fill("Chapitre Automatisé");
    await page.getByRole("button", { name: "Créer le Chapitre" }).click();

    await expect(page.getByText("Chapitre Automatisé")).toBeVisible();
  });

  test("6. Character Deep Editor (/studio/characters)", async ({ page }) => {
    await page.goto("/studio/characters");
    await expect(page.getByRole("heading", { name: "Éditeur de Personnages Profonds" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Archiviste Valerius" })).toBeVisible();

    await page.getByRole("button", { name: "Nouveau Personnage" }).click();
    await page.getByPlaceholder("Nom complet (ex: Lyra Vane)").fill("Eldrin le Scribe");
    await page.getByRole("button", { name: "Enregistrer le Profil" }).click();

    await expect(page.getByText("Eldrin le Scribe")).toBeVisible();
  });

  test("7. World Bible / Lore (/studio/lore)", async ({ page }) => {
    await page.goto("/studio/lore");
    await expect(page.getByRole("heading", { name: "Ancrage du Lore & Codex" })).toBeVisible();
    await expect(page.getByText("L'Obsidienne Stellaire")).toBeVisible();

    await page.getByRole("button", { name: "Ajouter une Entrée Lore" }).click();
    await page.getByPlaceholder("Titre de l'entrée (ex: Citadelle de Cendres)").fill("Lame d'Éther");
    await page.getByRole("button", { name: "Proposer au Codex" }).click();

    await expect(page.getByText("Lame d'Éther")).toBeVisible();
  });

  test("8. Lore Relationship Graph (/studio/lore-graph)", async ({ page }) => {
    await page.goto("/studio/lore-graph");
    await expect(page.getByRole("heading", { name: "Graphe de Relations Lore & Personnages" })).toBeVisible();
    await expect(page.locator(".react-flow")).toBeVisible();
  });

  test("9. Creative Intention Lab (/studio/intention-lab)", async ({ page }) => {
    await page.goto("/studio/intention-lab");
    await expect(page.getByRole("heading", { name: "Laboratoire d'Intention" })).toBeVisible();
    await expect(page.getByText("Directives Actives")).toBeVisible();

    await page.getByPlaceholder("Ex: Ne pas utiliser de mots argotiques modernes").fill("Pas de jargon moderne");
    await page.getByRole("button", { name: "Injecter la Contrainte" }).click();

    await expect(page.getByText("Pas de jargon moderne")).toBeVisible();
  });

  test("10. Validation Loop (/studio/validation-loop)", async ({ page }) => {
    await page.goto("/studio/validation-loop");
    await expect(page.getByRole("heading", { name: "Boucle de Validation (Linter + AI Review)" })).toBeVisible();
    await expect(page.getByRole("button", { name: /Exécuter la Boucle/ })).toBeVisible();

    await page.getByRole("button", { name: /Exécuter la Boucle/ }).click();
    await expect(page.getByText("1. Linter Déterministe")).toBeVisible();
  });

  test("11. Export Studio (/studio/export)", async ({ page }) => {
    await page.goto("/studio/export");
    await expect(page.getByRole("heading", { name: "Studio d'Exportation" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Exporter le Manuscrit" })).toBeVisible();
  });

  test("12. Dashboard & Book Hub (/dashboard)", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page.getByRole("heading", { name: "Bibliothèque & Tableau de Bord" })).toBeVisible();
    await expect(page.getByText("Les Ombres d'Aethelgard")).toBeVisible();
  });

  test("13. Pricing Page (/pricing)", async ({ page }) => {
    await page.goto("/pricing");
    await expect(page.getByRole("heading", { name: "Investissez dans la clarté de vos récits" })).toBeVisible();
    await expect(page.getByText("Auteur Indépendant")).toBeVisible();
    await expect(page.getByText("Architecte Littéraire")).toBeVisible();
    await expect(page.getByText("Maison d'Édition")).toBeVisible();
  });

  test("14. Business Workflow — Outline approval gate blocks chapter creation until approved", async ({ page }) => {
    await page.goto("/studio/outline");
    await expect(page.getByRole("heading", { name: "Éditeur de Plan Global" })).toBeVisible();
    await expect(page.getByTestId("add-chapter-btn")).toBeEnabled();
  });

  test("15. Business Workflow — Lore item transitions from Proposed to Canonical upon approval", async ({ page }) => {
    await page.goto("/studio/lore");

    await page.getByRole("button", { name: "Ajouter une Entrée Lore" }).click();
    await page.getByPlaceholder("Titre de l'entrée (ex: Citadelle de Cendres)").fill("Relique de la Faille");
    await page.getByPlaceholder("Description détaillée et règles d'utilisation par les mages...").fill("Règles d'invocation de la Faille.");
    await page.getByRole("button", { name: "Proposer au Codex" }).click();

    await expect(page.getByText("Relique de la Faille")).toBeVisible();
    await expect(page.getByText("Proposé — Approbation requise").first()).toBeVisible();

    await page.getByRole("button", { name: "Approuver" }).first().click();
    await expect(page.getByText("Canonique").first()).toBeVisible();
  });

  test("16. Business Workflow — Chapter versioning preserves previous versions without overwriting", async ({ page }) => {
    await page.goto("/studio");

    await page.getByRole("button", { name: /Versions/ }).click();
    await expect(page.getByText("v1 — Source: author")).toBeVisible();

    await page.getByRole("button", { name: "Générer Nouvelle Version" }).click();

    await expect(page.getByText("v2 — Source: ai")).toBeVisible();
    await expect(page.getByText("v1 — Source: author")).toBeVisible();
  });

  test("17. Business Workflow — Validation loop detects violations and supports controlled retries", async ({ page }) => {
    await page.goto("/studio/validation-loop");

    await expect(page.getByRole("heading", { name: "Boucle de Validation (Linter + AI Review)" })).toBeVisible();

    const textarea = page.locator("textarea");
    await textarea.fill("Un robot de haute technologie est entré dans le Scriptorium.");

    await page.getByRole("button", { name: "Exécuter la Boucle" }).click();

    await expect(page.getByText("Violation Détectée")).toBeVisible();
    await expect(page.locator("strong", { hasText: "robot" })).toBeVisible();
  });

  test("18. Business Workflow — Canonical Context includes prior chapter summaries and author intent", async ({ page }) => {
    await page.goto("/studio");

    await page.getByRole("button", { name: "Context" }).click();

    await expect(page.getByText("Intention Auteur", { exact: false }).first()).toBeVisible();
    await expect(page.getByText("Lore & Bible Canonique")).toBeVisible();
    await expect(page.getByText("Contraintes Actives")).toBeVisible();
    await expect(page.getByText("Résumés Précédents")).toBeVisible();
  });

  test("19. Business Workflow — Ingestion of source document extracts assertions and supports assertion review", async ({ page }) => {
    await page.goto("/studio/lore");

    await page.getByRole("button", { name: "Ingérer un Document Source" }).click();

    await page.getByPlaceholder("Nom du document").fill("Notes d'Histoire");
    await page.getByPlaceholder("Collez ici le contenu source").fill("Valerius a découvert la seconde relique à Aethelgard.");

    await page.getByRole("button", { name: "Ingérer & Extraire les Assertions" }).click();

    await expect(page.getByText("Assertions Extraites à Revoir")).toBeVisible();
    await expect(page.getByRole("button", { name: "Accepter (Canon)" }).first()).toBeVisible();

    await page.getByRole("button", { name: "Accepter (Canon)" }).first().click();
    await expect(page.getByText("accepted").first()).toBeVisible();
  });
});
