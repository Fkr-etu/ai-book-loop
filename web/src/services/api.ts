import {
  BookState,
  Chapter,
  Character,
  LoreItem,
  SceneReview,
  UserProfile,
  CanonicalContextResponse
} from "@/types";
import { initialProjectData } from "@/lib/mockData";

const STORAGE_KEY = "manuscript_studio_project";

function loadStorageProject(): BookState {
  if (typeof window === "undefined") return initialProjectData;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : initialProjectData;
  } catch {
    return initialProjectData;
  }
}

function saveStorageProject(state: BookState): void {
  if (typeof window !== "undefined") {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      // ignore
    }
  }
}

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
  loginUser(email: string, pass: string): Promise<UserProfile>;
}

export class MockBookApi implements BookApi {
  async getBook(id: string = "proj-001"): Promise<BookState> {
    return loadStorageProject();
  }

  async createBook(book: Partial<BookState>): Promise<BookState> {
    const newBook: BookState = {
      ...initialProjectData,
      ...book,
      id: book.id || `proj-${Date.now()}`
    };
    saveStorageProject(newBook);
    return newBook;
  }

  async updateBook(id: string, updates: Partial<BookState>): Promise<BookState> {
    const book = loadStorageProject();
    const updated = { ...book, ...updates };
    saveStorageProject(updated);
    return updated;
  }

  async generateOutline(id: string): Promise<BookState> {
    const book = loadStorageProject();
    book.outline = `1. Le Murmure du Parchemin - Explorer les archives scellées\n2. La Cité Suspendue - Ascension du pont de verre\n3. L'Éclipse du Codex - Sacrifice du premier souvenir`;
    book.outlineApproved = false;
    saveStorageProject(book);
    return book;
  }

  async approveOutline(id: string): Promise<BookState> {
    const book = loadStorageProject();
    book.outlineApproved = true;
    saveStorageProject(book);
    return book;
  }

  async addChapter(id: string, title: string, objective: string): Promise<BookState> {
    const book = loadStorageProject();
    if (!book.outlineApproved) {
      throw new Error("Impossible d'ajouter un chapitre tant que l'outline n'est pas approuvé par l'auteur.");
    }
    const num = book.chapters.length + 1;
    const newChapter: Chapter = {
      id: `chap-${num}`,
      number: num,
      title,
      objective,
      status: "draft",
      currentVersion: 0,
      summary: "",
      versions: [],
      scenes: []
    };
    book.chapters.push(newChapter);
    saveStorageProject(book);
    return book;
  }

  async generateChapter(id: string, chapterNumber: number): Promise<{ book: BookState; versionNumber: number; content: string }> {
    const book = loadStorageProject();
    if (!book.outlineApproved) {
      throw new Error("L'outline doit être approuvé avant de générer un chapitre.");
    }
    const chapter = book.chapters.find((c) => c.number === chapterNumber);
    if (!chapter) {
      throw new Error(`Chapitre ${chapterNumber} introuvable.`);
    }

    const nextVerNum = (chapter.currentVersion || 0) + 1;
    const generatedText = `[Génération V${nextVerNum}] Chapitre ${chapter.number}: ${chapter.title}. ${chapter.objective}. L'obscurité résonnait d'un écho ancien...`;

    const newVersion = {
      id: `ver-${chapter.number}-${nextVerNum}-${Date.now()}`,
      versionNumber: nextVerNum,
      content: generatedText,
      createdAt: new Date().toISOString(),
      source: "ai" as const,
      status: "proposed" as const
    };

    chapter.versions = chapter.versions || [];
    chapter.versions.push(newVersion);
    chapter.currentVersion = nextVerNum;
    chapter.status = "proposed";

    saveStorageProject(book);
    return { book, versionNumber: nextVerNum, content: generatedText };
  }

  async reviewChapter(
    id: string,
    chapterNumber: number,
    versionNumber?: number,
    draftText?: string
  ): Promise<{ book: BookState; review: SceneReview }> {
    const book = loadStorageProject();
    const chapter = book.chapters.find((c) => c.number === chapterNumber);
    if (!chapter) throw new Error("Chapitre introuvable");

    const vNum = versionNumber || chapter.currentVersion;
    const ver = (chapter.versions || []).find((v) => v.versionNumber === vNum);
    const contentToReview = draftText || ver?.content || "";

    const hasForbiddenWord = /ordinateur|robot|telephone|internet|wifi|voiture/i.test(contentToReview);
    const issues: string[] = [];
    if (hasForbiddenWord) {
      issues.push("Propos ou termes anachroniques détectés.");
    }
    if (contentToReview.length < 30) {
      issues.push("Longueur insuffisante pour une scène canonique.");
    }

    const approved = issues.length === 0;
    const score = approved ? 9 : 4;

    const review: SceneReview = {
      id: `rev-${Date.now()}`,
      score,
      approved,
      issues,
      suggestions: approved
        ? ["Style conforme au styletone et à l'intention auteur."]
        : ["Corriger les termes non-diégétiques et enrichir le texte."],
      scoreStyle: score,
      scoreCoherence: score,
      timestamp: new Date().toISOString()
    };

    if (ver) {
      ver.review = review;
      ver.status = approved ? "needs_review" : "rejected";
    }
    chapter.status = approved ? "needs_review" : "rejected";

    book.reviews = book.reviews || [];
    book.reviews.unshift(review);

    saveStorageProject(book);
    return { book, review };
  }

  async approveChapter(id: string, chapterNumber: number): Promise<BookState> {
    const book = loadStorageProject();
    const chapter = book.chapters.find((c) => c.number === chapterNumber);
    if (!chapter) throw new Error("Chapitre introuvable");

    chapter.status = "approved";
    chapter.summary = `Chapitre ${chapter.number} (${chapter.title}): ${chapter.objective} [Canonique]`;
    const curVer = (chapter.versions || []).find((v) => v.versionNumber === chapter.currentVersion);
    if (curVer) {
      curVer.status = "approved";
    }

    saveStorageProject(book);
    return book;
  }

  async rejectChapter(id: string, chapterNumber: number): Promise<BookState> {
    const book = loadStorageProject();
    const chapter = book.chapters.find((c) => c.number === chapterNumber);
    if (!chapter) throw new Error("Chapitre introuvable");

    chapter.status = "rejected";
    const curVer = (chapter.versions || []).find((v) => v.versionNumber === chapter.currentVersion);
    if (curVer) {
      curVer.status = "rejected";
    }

    saveStorageProject(book);
    return book;
  }

  async getCanonicalContext(id: string, chapterNumber: number): Promise<CanonicalContextResponse> {
    const book = loadStorageProject();
    const chapter = book.chapters.find((c) => c.number === chapterNumber);
    const prevSummaries = (book.chapters || [])
      .filter((c) => c.number < chapterNumber && c.summary)
      .map((c) => `Chapter ${c.number} (${c.title}): ${c.summary}`)
      .join("\n");

    const constraintsText = (book.constraints || []).map((c) => `- ${c}`).join("\n");

    const formatted = [
      `AUTHOR IDEA:\n${book.authorIdea}`,
      `THEME:\n${book.theme}`,
      `LORE:\n${book.lore}`,
      `GLOBAL OUTLINE:\n${book.outline || ""}`,
      `CONSTRAINTS:\n${constraintsText}`,
      `PREVIOUS CHAPTER SUMMARIES:\n${prevSummaries}`,
      `CURRENT CHAPTER OBJECTIVE:\n${chapter?.objective || ""}`
    ].join("\n\n");

    return {
      authorIdea: book.authorIdea,
      theme: book.theme,
      lore: book.lore,
      globalOutline: book.outline || "",
      constraints: book.constraints || [],
      previousSummaries: prevSummaries,
      currentObjective: chapter?.objective || "",
      formattedContext: formatted
    };
  }

  async createCharacter(id: string, char: Omit<Character, "id">): Promise<BookState> {
    const book = loadStorageProject();
    const newChar: Character = {
      ...char,
      id: `char-${Date.now()}`,
      status: char.status || "proposed"
    };
    book.characters = book.characters || [];
    book.characters.push(newChar);
    book.graphNodes = book.graphNodes || [];
    book.graphNodes.push({ id: newChar.id, label: newChar.name, type: "character" });
    saveStorageProject(book);
    return book;
  }

  async updateCharacter(id: string, charId: string, updates: Partial<Character>): Promise<BookState> {
    const book = loadStorageProject();
    book.characters = (book.characters || []).map((c) => (c.id === charId ? { ...c, ...updates } : c));
    saveStorageProject(book);
    return book;
  }

  async deleteCharacter(id: string, charId: string): Promise<BookState> {
    const book = loadStorageProject();
    book.characters = (book.characters || []).filter((c) => c.id !== charId);
    book.graphNodes = (book.graphNodes || []).filter((n) => n.id !== charId);
    book.graphEdges = (book.graphEdges || []).filter((e) => e.source !== charId && e.target !== charId);
    saveStorageProject(book);
    return book;
  }

  async createLoreItem(id: string, item: Omit<LoreItem, "id">): Promise<BookState> {
    const book = loadStorageProject();
    const newItem: LoreItem = {
      ...item,
      id: `lore-${Date.now()}`,
      canonStatus: item.canonStatus || "proposed"
    };
    book.loreItems = book.loreItems || [];
    book.loreItems.push(newItem);
    book.graphNodes = book.graphNodes || [];
    book.graphNodes.push({ id: newItem.id, label: newItem.title, type: newItem.category });
    saveStorageProject(book);
    return book;
  }

  async updateLoreItem(id: string, loreId: string, updates: Partial<LoreItem>): Promise<BookState> {
    const book = loadStorageProject();
    book.loreItems = (book.loreItems || []).map((l) => (l.id === loreId ? { ...l, ...updates } : l));
    saveStorageProject(book);
    return book;
  }

  async deleteLoreItem(id: string, loreId: string): Promise<BookState> {
    const book = loadStorageProject();
    book.loreItems = (book.loreItems || []).filter((l) => l.id !== loreId);
    book.graphNodes = (book.graphNodes || []).filter((n) => n.id !== loreId);
    book.graphEdges = (book.graphEdges || []).filter((e) => e.source !== loreId && e.target !== loreId);
    saveStorageProject(book);
    return book;
  }

  async loginUser(email: string, pass: string): Promise<UserProfile> {
    return {
      id: "usr-001",
      email,
      name: "Valerius de Cendres",
      plan: "pro"
    };
  }
}

export class RealBookApi implements BookApi {
  private baseUrl: string;

  constructor(baseUrl: string = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...options?.headers
      },
      ...options
    });
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`API Error (${res.status}): ${errorText}`);
    }
    return res.json();
  }

  async getBook(id: string = "proj-001"): Promise<BookState> {
    return this.request<BookState>(`/api/books/${id}`);
  }

  async createBook(book: Partial<BookState>): Promise<BookState> {
    return this.request<BookState>("/api/books", {
      method: "POST",
      body: JSON.stringify(book)
    });
  }

  async updateBook(id: string, updates: Partial<BookState>): Promise<BookState> {
    return this.request<BookState>(`/api/books/${id}`, {
      method: "PUT",
      body: JSON.stringify(updates)
    });
  }

  async generateOutline(id: string): Promise<BookState> {
    return this.request<BookState>(`/api/books/${id}/outline/generate`, {
      method: "POST"
    });
  }

  async approveOutline(id: string): Promise<BookState> {
    return this.request<BookState>(`/api/books/${id}/outline/approve`, {
      method: "POST"
    });
  }

  async addChapter(id: string, title: string, objective: string): Promise<BookState> {
    return this.request<BookState>(`/api/books/${id}/chapters`, {
      method: "POST",
      body: JSON.stringify({ title, objective })
    });
  }

  async generateChapter(id: string, chapterNumber: number): Promise<{ book: BookState; versionNumber: number; content: string }> {
    return this.request<{ book: BookState; versionNumber: number; content: string }>(
      `/api/books/${id}/chapters/${chapterNumber}/generate`,
      { method: "POST" }
    );
  }

  async reviewChapter(
    id: string,
    chapterNumber: number,
    versionNumber?: number,
    draftText?: string
  ): Promise<{ book: BookState; review: SceneReview }> {
    return this.request<{ book: BookState; review: SceneReview }>(
      `/api/books/${id}/chapters/${chapterNumber}/review`,
      {
        method: "POST",
        body: JSON.stringify({ versionNumber, draftText })
      }
    );
  }

  async approveChapter(id: string, chapterNumber: number): Promise<BookState> {
    return this.request<BookState>(`/api/books/${id}/chapters/${chapterNumber}/approve`, {
      method: "POST"
    });
  }

  async rejectChapter(id: string, chapterNumber: number): Promise<BookState> {
    return this.request<BookState>(`/api/books/${id}/chapters/${chapterNumber}/reject`, {
      method: "POST"
    });
  }

  async getCanonicalContext(id: string, chapterNumber: number): Promise<CanonicalContextResponse> {
    return this.request<CanonicalContextResponse>(`/api/books/${id}/chapters/${chapterNumber}/context`);
  }

  async createCharacter(id: string, char: Omit<Character, "id">): Promise<BookState> {
    return this.request<BookState>(`/api/books/${id}/characters`, {
      method: "POST",
      body: JSON.stringify(char)
    });
  }

  async updateCharacter(id: string, charId: string, updates: Partial<Character>): Promise<BookState> {
    return this.request<BookState>(`/api/books/${id}/characters/${charId}`, {
      method: "PUT",
      body: JSON.stringify(updates)
    });
  }

  async deleteCharacter(id: string, charId: string): Promise<BookState> {
    return this.request<BookState>(`/api/books/${id}/characters/${charId}`, {
      method: "DELETE"
    });
  }

  async createLoreItem(id: string, item: Omit<LoreItem, "id">): Promise<BookState> {
    return this.request<BookState>(`/api/books/${id}/lore`, {
      method: "POST",
      body: JSON.stringify(item)
    });
  }

  async updateLoreItem(id: string, loreId: string, updates: Partial<LoreItem>): Promise<BookState> {
    return this.request<BookState>(`/api/books/${id}/lore/${loreId}`, {
      method: "PUT",
      body: JSON.stringify(updates)
    });
  }

  async deleteLoreItem(id: string, loreId: string): Promise<BookState> {
    return this.request<BookState>(`/api/books/${id}/lore/${loreId}`, {
      method: "DELETE"
    });
  }

  async loginUser(email: string, pass: string): Promise<UserProfile> {
    return {
      id: "usr-001",
      email,
      name: "Valerius de Cendres",
      plan: "pro"
    };
  }
}

let apiInstance: BookApi | null = null;

export function getApiClient(): BookApi {
  if (!apiInstance) {
    if (process.env.NEXT_PUBLIC_USE_REAL_API === "true") {
      apiInstance = new RealBookApi();
    } else {
      apiInstance = new MockBookApi();
    }
  }
  return apiInstance;
}

export function setApiClient(client: BookApi): void {
  apiInstance = client;
}
