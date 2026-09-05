import type {
  Assertion,
  BookState,
  CanonicalContextResponse,
  Character,
  IngestionResult,
  LoreItem,
  SceneReview,
  UserProfile,
} from "@/types";
import { initialProjectData } from "@/lib/mockData";
import { USE_REAL_API } from "@/services/config";
import { typedBookApi } from "@/services/bookApiAdapter";

const STORAGE_KEY = "manuscript_studio_project";

export interface BookApi {
  getBook(id?: string): Promise<BookState>;
  createBook(book: Partial<BookState>): Promise<BookState>;
  updateBook(id: string, updates: Partial<BookState>): Promise<BookState>;
  generateOutline(id: string): Promise<BookState>;
  approveOutline(id: string): Promise<BookState>;
  addChapter(id: string, title: string, objective: string): Promise<BookState>;
  generateChapter(id: string, chapterNumber: number): Promise<{ book: BookState; versionNumber: number; content: string }>;
  reviewChapter(id: string, chapterNumber: number, versionNumber?: number, draftText?: string): Promise<{ book: BookState; review: SceneReview }>;
  approveChapter(id: string, chapterNumber: number): Promise<BookState>;
  rejectChapter(id: string, chapterNumber: number): Promise<BookState>;
  getCanonicalContext(id: string, chapterNumber: number): Promise<CanonicalContextResponse>;
  createCharacter(id: string, char: Omit<Character, "id">): Promise<BookState>;
  updateCharacter(id: string, charId: string, updates: Partial<Character>): Promise<BookState>;
  deleteCharacter(id: string, charId: string): Promise<BookState>;
  createLoreItem(id: string, item: Omit<LoreItem, "id">): Promise<BookState>;
  updateLoreItem(id: string, loreId: string, updates: Partial<LoreItem>): Promise<BookState>;
  deleteLoreItem(id: string, loreId: string): Promise<BookState>;
  ingestDocument(id: string, name: string, content: string, sourceType?: string): Promise<IngestionResult>;
  listAssertions(id: string): Promise<Assertion[]>;
  reviewAssertion(id: string, assertionId: string, decision: "accept" | "reject" | "defer", rationale?: string): Promise<void>;
  registerUser(email: string, pass: string, name?: string): Promise<UserProfile>;
  loginUser(email: string, pass: string): Promise<UserProfile>;
  logoutUser(): Promise<void>;
  getCurrentUser(): Promise<UserProfile | null>;
}

function loadStorageProject(): BookState {
  if (typeof window === "undefined") return initialProjectData;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as BookState) : initialProjectData;
  } catch {
    return initialProjectData;
  }
}

function saveStorageProject(state: BookState): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Local persistence is best-effort in mock mode.
  }
}

export class MockBookApi implements BookApi {
  async getBook(): Promise<BookState> { return loadStorageProject(); }

  async createBook(book: Partial<BookState>): Promise<BookState> {
    const state: BookState = {
      ...initialProjectData,
      id: `proj-${Date.now()}`,
      title: book.title || "Nouveau Livre",
      theme: book.theme || "",
      authorIdea: book.authorIdea || "",
      lore: book.lore || "",
      constraints: book.constraints || [],
      outlineApproved: false,
      chapters: [],
    };
    saveStorageProject(state);
    return state;
  }

  async updateBook(id: string, updates: Partial<BookState>): Promise<BookState> {
    const state = { ...loadStorageProject(), ...updates, id };
    saveStorageProject(state);
    return state;
  }

  async generateOutline(): Promise<BookState> {
    const state = loadStorageProject();
    state.outline = state.outline || "# Structure proposée\n\n## Chapitre 1\nObjectif à définir.";
    state.outlineApproved = false;
    saveStorageProject(state);
    return state;
  }

  async approveOutline(): Promise<BookState> {
    const state = loadStorageProject();
    state.outlineApproved = true;
    saveStorageProject(state);
    return state;
  }

  async addChapter(id: string, title: string, objective: string): Promise<BookState> {
    const state = loadStorageProject();
    if (!state.outlineApproved) throw new Error("L'outline doit être approuvé avant d'ajouter un chapitre.");
    const number = state.chapters.length + 1;
    state.chapters.push({ id: `ch-${number}`, number, title, objective, status: "draft", currentVersion: 0, versions: [], scenes: [] });
    saveStorageProject(state);
    return state;
  }

  async generateChapter(id: string, chapterNumber: number): Promise<{ book: BookState; versionNumber: number; content: string }> {
    const state = loadStorageProject();
    const chapter = state.chapters.find((item) => item.number === chapterNumber);
    if (!chapter) throw new Error(`Chapitre ${chapterNumber} introuvable.`);
    const versionNumber = chapter.currentVersion + 1;
    const content = `[Version ${versionNumber}] Brouillon local du chapitre ${chapterNumber}.`;
    chapter.currentVersion = versionNumber;
    chapter.versions = [...(chapter.versions || []), { id: `v-${versionNumber}`, versionNumber, content, createdAt: new Date().toISOString(), source: "ai", status: "proposed" }];
    chapter.status = "proposed";
    saveStorageProject(state);
    return { book: state, versionNumber, content };
  }

  async reviewChapter(id: string, chapterNumber: number): Promise<{ book: BookState; review: SceneReview }> {
    const state = loadStorageProject();
    const review: SceneReview = { id: `review-${Date.now()}`, score: 0, approved: false, issues: ["Revue locale simulée."], suggestions: [] };
    state.reviews = [review, ...(state.reviews || [])];
    saveStorageProject(state);
    return { book: state, review };
  }

  async approveChapter(id: string, chapterNumber: number): Promise<BookState> { return this.setChapterStatus(chapterNumber, "approved"); }
  async rejectChapter(id: string, chapterNumber: number): Promise<BookState> { return this.setChapterStatus(chapterNumber, "rejected"); }

  private async setChapterStatus(chapterNumber: number, status: BookState["chapters"][number]["status"]): Promise<BookState> {
    const state = loadStorageProject();
    const chapter = state.chapters.find((item) => item.number === chapterNumber);
    if (chapter) chapter.status = status;
    saveStorageProject(state);
    return state;
  }

  async getCanonicalContext(id: string, chapterNumber: number): Promise<CanonicalContextResponse> {
    const state = loadStorageProject();
    const chapter = state.chapters.find((item) => item.number === chapterNumber);
    const previousSummaries = state.chapters.filter((item) => item.number < chapterNumber && item.summary).map((item) => `${item.title}: ${item.summary}`).join("\n");
    return {
      authorIdea: state.authorIdea,
      theme: state.theme,
      lore: state.lore,
      globalOutline: state.outline || "",
      constraints: state.constraints,
      previousSummaries,
      currentObjective: chapter?.objective || "",
      formattedContext: [state.authorIdea, state.theme, state.lore, state.outline || "", ...state.constraints, previousSummaries, chapter?.objective || ""].join("\n\n"),
    };
  }

  async createCharacter(): Promise<BookState> { throw new Error("Les personnages ne sont pas disponibles en mode mock simplifié."); }
  async updateCharacter(): Promise<BookState> { throw new Error("Les personnages ne sont pas disponibles en mode mock simplifié."); }
  async deleteCharacter(): Promise<BookState> { throw new Error("Les personnages ne sont pas disponibles en mode mock simplifié."); }
  async createLoreItem(): Promise<BookState> { throw new Error("Le lore structuré n'est pas disponible en mode mock simplifié."); }
  async updateLoreItem(): Promise<BookState> { throw new Error("Le lore structuré n'est pas disponible en mode mock simplifié."); }
  async deleteLoreItem(): Promise<BookState> { throw new Error("Le lore structuré n'est pas disponible en mode mock simplifié."); }

  async ingestDocument(): Promise<IngestionResult> { throw new Error("L'ingestion locale est désactivée dans ce mock."); }
  async listAssertions(): Promise<Assertion[]> { return []; }
  async reviewAssertion(): Promise<void> {}

  async registerUser(email: string, pass: string, name = ""): Promise<UserProfile> { return { id: "mock-user", email, name, plan: "pro" }; }
  async loginUser(email: string, pass: string): Promise<UserProfile> { return { id: "mock-user", email, name: "Auteur", plan: "pro" }; }
  async logoutUser(): Promise<void> {}
  async getCurrentUser(): Promise<UserProfile | null> { return null; }
}

let apiInstance: BookApi | null = null;

export function getApiClient(): BookApi {
  if (!apiInstance) apiInstance = USE_REAL_API ? typedBookApi : new MockBookApi();
  return apiInstance;
}

export function setApiClient(client: BookApi): void { apiInstance = client; }
