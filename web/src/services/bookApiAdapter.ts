import type { BookState, Character, LoreItem, SceneReview, CanonicalContextResponse, IngestionResult, Assertion, UserProfile } from "@/types";
import type { BackendWorkflowRun } from "@/types/api";
import { realApiClient } from "@/services/realApiClient";
import { adaptBackendBook } from "@/services/bookAdapter";
import type { BookApi } from "@/services/api";

const EMPTY_BOOK_ID = "proj-001";
export function emptyBook(): BookState { return { id: EMPTY_BOOK_ID, title: "", theme: "", authorIdea: "", lore: "", constraints: [], outlineApproved: false, chapters: [] }; }
function unsupported(feature: string): Promise<never> { return Promise.reject(new Error(`${feature} n'est pas encore disponible via l'API réelle.`)); }
function toCanonicalContext(context: Awaited<ReturnType<typeof realApiClient.getChapterContext>>): CanonicalContextResponse { const globalOutline = context.globalOutline?.chapters.map((c) => `## Chapitre ${c.number}: ${c.title}\nObjectif: ${c.objective}\n${c.synopsis}`).join("\n\n") ?? ""; return { authorIdea: context.authorIdea, theme: context.theme, lore: context.lore, globalOutline, constraints: context.constraints, previousSummaries: context.previousSummaries, currentObjective: context.currentObjective, formattedContext: context.formattedContext }; }

export class RealBookApi implements BookApi {
  async getBook(id = EMPTY_BOOK_ID): Promise<BookState> { if (id === EMPTY_BOOK_ID) { const books = await realApiClient.listBooks(); if (books.length === 0) return emptyBook(); return adaptBackendBook(books[0]); } return adaptBackendBook(await realApiClient.getBook(id)); }
  async createBook(book: Partial<BookState>): Promise<BookState> { return adaptBackendBook(await realApiClient.createBook({ title: book.title || "Nouveau Livre", theme: book.theme || "", author_idea: book.authorIdea || "", lore: book.lore, constraints: book.constraints })); }
  async updateBook(id: string, updates: Partial<BookState>): Promise<BookState> { if (id === EMPTY_BOOK_ID) return this.createBook(updates); return adaptBackendBook(await realApiClient.updateBook(id, { ...(updates.title !== undefined ? { title: updates.title } : {}), ...(updates.theme !== undefined ? { theme: updates.theme } : {}), ...(updates.authorIdea !== undefined ? { author_idea: updates.authorIdea } : {}), ...(updates.lore !== undefined ? { lore: updates.lore } : {}), ...(updates.constraints !== undefined ? { constraints: updates.constraints } : {}) })); }
  async generateOutline(id: string): Promise<BookState> { return adaptBackendBook(await realApiClient.generateOutline(id)); }
  async approveOutline(id: string): Promise<BookState> { return adaptBackendBook(await realApiClient.approveOutline(id)); }
  async addChapter(id: string, title: string, objective: string): Promise<BookState> { void title; void objective; const current = await realApiClient.getBook(id); return adaptBackendBook(await realApiClient.addChapter(id, current.chapters.length + 1)); }
  async generateChapter(id: string, n: number): Promise<{ book: BookState; versionNumber: number; content: string; run: BackendWorkflowRun }> { const result = await realApiClient.generateChapter(id, n); const book = adaptBackendBook(await realApiClient.getBook(id)); const chapter = book.chapters.find((item) => item.number === n); return { book, versionNumber: chapter?.currentVersion ?? 0, content: result.run.draft, run: result.run }; }
  async getChapterWorkflowRun(id: string, n: number, runId: string): Promise<BackendWorkflowRun> { return realApiClient.getChapterWorkflowRun(id, n, runId); }
  async getLatestChapterWorkflowRun(id: string, n: number): Promise<BackendWorkflowRun | null> { return realApiClient.getLatestChapterWorkflowRun(id, n); }
  async reviewChapter(id: string, n: number, v?: number, draft?: string): Promise<{ book: BookState; review: SceneReview }> { const result = await realApiClient.reviewChapter(id, n, v, draft); return { book: adaptBackendBook(result.book), review: result.review as SceneReview }; }
  async approveChapter(id: string, n: number): Promise<BookState> { return adaptBackendBook(await realApiClient.approveChapter(id, n)); }
  async rejectChapter(id: string, n: number): Promise<BookState> { return adaptBackendBook(await realApiClient.rejectChapter(id, n)); }
  async getCanonicalContext(id: string, n: number): Promise<CanonicalContextResponse> { return toCanonicalContext(await realApiClient.getChapterContext(id, n)); }
  async createCharacter(_id: string, _char: Omit<Character, "id">): Promise<BookState> { return unsupported("La gestion des personnages"); }
  async updateCharacter(_id: string, _charId: string, _updates: Partial<Character>): Promise<BookState> { return unsupported("La gestion des personnages"); }
  async deleteCharacter(_id: string, _charId: string): Promise<BookState> { return unsupported("La gestion des personnages"); }
  async createLoreItem(_id: string, _item: Omit<LoreItem, "id">): Promise<BookState> { return unsupported("La gestion du lore"); }
  async updateLoreItem(_id: string, _loreId: string, _updates: Partial<LoreItem>): Promise<BookState> { return unsupported("La gestion du lore"); }
  async deleteLoreItem(_id: string, _loreId: string): Promise<BookState> { return unsupported("La gestion du lore"); }
  async ingestDocument(id: string, name: string, content: string, sourceType?: string): Promise<IngestionResult> { return realApiClient.ingestDocument(id, name, content, sourceType); }
  async listAssertions(id: string): Promise<Assertion[]> { return realApiClient.listAssertions(id) as Promise<Assertion[]>; }
  async reviewAssertion(id: string, assertionId: string, decision: "accept" | "reject" | "defer", rationale?: string): Promise<void> { return realApiClient.reviewAssertion(id, assertionId, decision, rationale); }
  async loginUser(email: string, password: string): Promise<UserProfile> { return realApiClient.login(email, password) as Promise<UserProfile>; }
  async registerUser(email: string, password: string, name: string): Promise<UserProfile> { return realApiClient.register(email, password, name) as Promise<UserProfile>; }
  async logoutUser(): Promise<void> { await realApiClient.logout(); }
  async getCurrentUser(): Promise<UserProfile | null> { return realApiClient.getCurrentUser() as Promise<UserProfile | null>; }
  async createCheckout(plan: "creator" | "pro", billingCycle: "monthly" | "yearly"): Promise<string> { return (await realApiClient.createCheckout(plan, billingCycle)).url; }
  async openBillingPortal(): Promise<string> { return (await realApiClient.createBillingPortal()).url; }
}
export const typedBookApi = new RealBookApi();
