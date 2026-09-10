import { test, expect } from "@playwright/test";

const apiBaseUrl = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");
const bookId = "async-analysis-e2e";
const consistencyStorageKey = `book-loop:consistency-analysis:${bookId}`;

const book = {
  id: bookId,
  owner_id: "e2e-user",
  title: "Livre E2E",
  theme: "Roman",
  author_idea: "Tester les analyses asynchrones.",
  creative_brief: null,
  lore: "",
  constraints: [],
  outline: null,
  outline_approved: false,
  chapters: [],
};

const mockProject = {
  id: bookId,
  title: book.title,
  theme: book.theme,
  authorIdea: book.author_idea,
  lore: book.lore,
  constraints: [],
  creativeConstraints: [],
  outline: "",
  outlineApproved: false,
  chapters: [],
  characters: [],
  loreItems: [],
  reviews: [],
};

const queuedJob = {
  job_id: "job-async-e2e",
  book_id: bookId,
  analysis_type: "consistency",
  status: "queued",
  progress: 0,
  current_step: null,
  attempt: 0,
  created_at: "2026-09-10T10:00:00Z",
  started_at: null,
  completed_at: null,
  failed_at: null,
  error_code: null,
  error_message: null,
  result: null,
};

const runningJob = {
  ...queuedJob,
  status: "running",
  progress: 35,
  current_step: "analyzing",
  attempt: 1,
  started_at: "2026-09-10T10:00:01Z",
};

const succeededJob = {
  ...runningJob,
  status: "succeeded",
  progress: 100,
  current_step: null,
  completed_at: "2026-09-10T10:00:05Z",
  result: {
    issues: [
      {
        id: "issue-1",
        category: "continuity",
        severity: "warning",
        status: "open",
        message: "Une contradiction de continuité a été détectée.",
        left_assertion_id: "assertion-1",
        right_assertion_id: "assertion-2",
        left_statement: "Maya vit à Paris.",
        right_statement: "Maya vit à Lyon.",
        left_evidence: "Source A",
        right_evidence: "Source B",
        confidence: 0.92,
        rule_id: null,
        metadata: {},
        resolution_assertion_id: null,
      },
    ],
  },
};

test.describe("Book Loop — async consistency analysis", () => {
  test("launches, survives reload while running, polls and renders the result", async ({ page }) => {
    let statusCalls = 0;

    await page.addInitScript(({ project, storageKey }) => {
      window.localStorage.setItem("manuscript_studio_project", JSON.stringify(project));
      window.localStorage.removeItem(storageKey);
    }, { project: mockProject, storageKey: consistencyStorageKey });

    await page.route(`${apiBaseUrl}/api/auth/me`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ user: { id: "e2e-user", email: "e2e@example.com", name: "E2E", plan: "free" } }),
      });
    });

    await page.route(`${apiBaseUrl}/api/books/${bookId}`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(book) });
    });

    await page.route(`${apiBaseUrl}/api/books/${bookId}/assertions`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
    });

    await page.route(`${apiBaseUrl}/api/books/${bookId}/consistency/analyze`, async (route) => {
      expect(route.request().method()).toBe("POST");
      await route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify(queuedJob) });
    });

    await page.route(`${apiBaseUrl}/api/books/${bookId}/consistency/analyses/job-async-e2e`, async (route) => {
      statusCalls += 1;
      const response = statusCalls === 1 ? queuedJob : statusCalls <= 3 ? runningJob : succeededJob;
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(response) });
    });

    await page.goto(`/studio/canon?bookId=${bookId}`);
    await expect(page.getByRole("heading", { name: "Analyse de cohérence" })).toBeVisible();
    await page.getByRole("button", { name: "Lancer l’analyse" }).click();

    await expect(page.getByText("En attente dans la file")).toBeVisible();
    await expect(page.getByText("Analyse du Canon en cours")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("35%")).toBeVisible();
    await expect(page.getByRole("button", { name: "Analyse en cours…" })).toBeDisabled();
    await expect.poll(async () => page.evaluate((key) => localStorage.getItem(key), consistencyStorageKey)).toBe("job-async-e2e");

    await page.reload();
    await expect(page.getByText("Analyse du Canon en cours")).toBeVisible();
    await expect(page.getByText("35%")).toBeVisible();

    await expect(page.getByText("Analyse terminée — 1 problème détecté.")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Une contradiction de continuité a été détectée.")).toBeVisible();
    await expect(page.getByText("Maya vit à Paris.")).toBeVisible();
    await expect(page.getByText("Maya vit à Lyon.")).toBeVisible();
    await expect(page.getByText("35%")).toHaveCount(0);
    await expect.poll(async () => page.evaluate((key) => localStorage.getItem(key), consistencyStorageKey)).toBeNull();
    expect(statusCalls).toBeGreaterThanOrEqual(4);
  });
});
