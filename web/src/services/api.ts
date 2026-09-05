import {
  BookState,
  Chapter,
  Character,
  LoreItem,
  SceneReview,
  UserProfile,
  CanonicalContextResponse,
  SourceDocument,
  Assertion,
  IngestionResult
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
  ingestDocument(id: string, name: string, content: string, sourceType?: string): Promise<IngestionResult>;
  listAssertions(id: string): Promise<Assertion[]>;
  reviewAssertion(id: string, assertionId: string, decision: "accept" | "reject" | "defer", rationale?: string): Promise<void>;
  registerUser(email: string, pass: string, name?: string): Promise<UserProfile>;
  loginUser(email: string, pass: string): Promise<UserProfile>;
  logoutUser(): Promise<void>;
  getCurrentUser(): Promise<UserProfile | null>;
}

export class MockBookApi implements BookApi {
  async getBook(id?: string): Promise<BookState> { return loadStorageProject(); }
  async createBook(book: Partial<BookState>): Promise<BookState> { const newBook: BookState = { ...initialProjectData, id: `proj-${Date.now()}`, title: book.title || "Nouveau Livre", theme: book.theme || "Dark Fantasy", authorIdea: book.authorIdea || "", lore: book.lore || "", constraints: book.constraints || [], outlineApproved: false, chapters: [] }; saveStorageProject(newBook); return newBook; }
  async updateBook(id: string, updates: Partial<BookState>): Promise<BookState> { const book = loadStorageProject(); const updated = { ...book, ...updates }; saveStorageProject(updated); return updated; }
  async generateOutline(id: string): Promise<BookState> { const book = loadStorageProject(); book.outline = ["# Structure Proposée par le Modèle Agentique", "## Chapitre 1: Le Murmure du Parchemin", "Objectif: L'Archiviste Valerius découvre une tablette cryptée dans le Scriptorium Oublié.", "## Chapitre 2: La Cité Suspendue d'Aethelgard", "Objectif: Traversée du pont de verre et confrontation avec la première relique.", "## Chapitre 3: L'Éclipse du Codex", "Objectif: Révélation du rituel d'oblitérations et dilemme moral."].join("\n"); book.outlineApproved = false; saveStorageProject(book); return book; }
  async approveOutline(id: string): Promise<BookState> { const book = loadStorageProject(); book.outlineApproved = true; saveStorageProject(book); return book; }
  async addChapter(id: string, title: string, objective: string): Promise<BookState> { const book = loadStorageProject(); if (!book.outlineApproved) throw new Error("L'outline doit être approuvé avant d'ajouter un chapitre."); const nextNum = (book.chapters || []).length + 1; const newChapter: Chapter = { id: `ch-00${nextNum}`, number: nextNum, title, objective, status: "draft", currentVersion: 0, versions: [], scenes: [] }; book.chapters = book.chapters || []; book.chapters.push(newChapter); saveStorageProject(book); return book; }
  async generateChapter(id: string, chapterNumber: number): Promise<{ book: BookState; versionNumber: number; content: string }> { const book = loadStorageProject(); const chapterIndex = (book.chapters || []).findIndex(c => c.number === chapterNumber); if (chapterIndex === -1) throw new Error(`Chapitre ${chapterNumber} introuvable.`); const ch = book.chapters[chapterIndex]; const versionNumber = (ch.currentVersion || 0) + 1; const content = `[Version ${versionNumber}] La lueur d'obsidienne vacilla dans le silence absolu. Le chapitre ${chapterNumber} s'ouvrait sur l'inconnu.`; ch.currentVersion = versionNumber; ch.status = "approved"; ch.summary = `Résumé canonique du chapitre ${chapterNumber}.`; ch.versions = ch.versions || []; ch.versions.push({ id: `v-00${versionNumber}`, versionNumber, content, createdAt: new Date().toISOString(), source: "ai", status: "approved" }); saveStorageProject(book); return { book, versionNumber, content }; }
  async reviewChapter(id: string, chapterNumber: number, versionNumber?: number, draftText?: string): Promise<{ book: BookState; review: SceneReview }> { const book = loadStorageProject(); const review: SceneReview = { id: `rev-${Date.now()}`, score: 9, scoreStyle: 9, scoreCoherence: 9.5, approved: true, issues: [], suggestions: ["Conserver l'atmosphère scholastique sombre.", "Renforcer le vocabulaire d'alchimie antique."], critique: "Style hautement évocateur, respect parfait des contraintes de genre.", timestamp: "À l'instant" }; book.reviews = book.reviews || []; book.reviews.unshift(review); saveStorageProject(book); return { book, review }; }
  async approveChapter(id: string, chapterNumber: number): Promise<BookState> { const book = loadStorageProject(); const ch = (book.chapters || []).find(c => c.number === chapterNumber); if (ch) { ch.status = "approved"; saveStorageProject(book); } return book; }
  async rejectChapter(id: string, chapterNumber: number): Promise<BookState> { const book = loadStorageProject(); const ch = (book.chapters || []).find(c => c.number === chapterNumber); if (ch) { ch.status = "rejected"; saveStorageProject(book); } return book; }
  async getCanonicalContext(id: string, chapterNumber: number): Promise<CanonicalContextResponse> { const book = loadStorageProject(); const chapter = (book.chapters || []).find(c => c.number === chapterNumber); const previousSummaries = (book.chapters || []).filter(c => c.number < chapterNumber && c.summary).map(c => `Chapter ${c.number} (${c.title}): ${c.summary}`).join("\n"); const formattedContext = [`AUTHOR IDEA:\n${book.authorIdea}`, `THEME:\n${book.theme}`, `LORE:\n${book.lore}`, `GLOBAL OUTLINE:\n${book.outline || ""}`, `CONSTRAINTS:\n${(book.constraints || []).map(c => `- ${c}`).join("\n")}`, `PREVIOUS CHAPTER SUMMARIES:\n${previousSummaries}`, `CURRENT CHAPTER OBJECTIVE:\n${chapter?.objective || ""}`].join("\n\n"); return { authorIdea: book.authorIdea, theme: book.theme, lore: book.lore, globalOutline: book.outline || "", constraints: book.constraints || [], previousSummaries, currentObjective: chapter?.objective || "", formattedContext }; }
  async createCharacter(id: string, char: Omit<Character, "id">): Promise<BookState> { const book = loadStorageProject(); const newChar: Character = { ...char, id: `char-${Date.now()}`, status: char.status || "proposed" }; book.characters = book.characters || []; book.characters.push(newChar); book.graphNodes = book.graphNodes || []; book.graphNodes.push({ id: newChar.id, label: newChar.name, type: "character" }); saveStorageProject(book); return book; }
  async updateCharacter(id: string, charId: string, updates: Partial<Character>): Promise<BookState> { const book = loadStorageProject(); book.characters = (book.characters || []).map(c => c.id === charId ? { ...c, ...updates } : c); saveStorageProject(book); return book; }
  async deleteCharacter(id: string, charId: string): Promise<BookState> { const book = loadStorageProject(); book.characters = (book.characters || []).filter(c => c.id !== charId); book.graphNodes = (book.graphNodes || []).filter(n => n.id !== charId); book.graphEdges = (book.graphEdges || []).filter(e => e.source !== charId && e.target !== charId); saveStorageProject(book); return book; }
  async createLoreItem(id: string, item: Omit<LoreItem, "id">): Promise<BookState> { const book = loadStorageProject(); const newItem: LoreItem = { ...item, id: `lore-${Date.now()}`, canonStatus: item.canonStatus || "proposed" }; book.loreItems = book.loreItems || []; book.loreItems.push(newItem); book.graphNodes = book.graphNodes || []; book.graphNodes.push({ id: newItem.id, label: newItem.title, type: newItem.category }); saveStorageProject(book); return book; }
  async updateLoreItem(id: string, loreId: string, updates: Partial<LoreItem>): Promise<BookState> { const book = loadStorageProject(); book.loreItems = (book.loreItems || []).map(l => l.id === loreId ? { ...l, ...updates } : l); saveStorageProject(book); return book; }
  async deleteLoreItem(id: string, loreId: string): Promise<BookState> { const book = loadStorageProject(); book.loreItems = (book.loreItems || []).filter(l => l.id !== loreId); book.graphNodes = (book.graphNodes || []).filter(n => n.id !== loreId); book.graphEdges = (book.graphEdges || []).filter(e => e.source !== loreId && e.target !== loreId); saveStorageProject(book); return book; }
  async ingestDocument(id: string, name: string, content: string, sourceType = "markdown"): Promise<IngestionResult> { const book = loadStorageProject(); const source: SourceDocument = { id: `doc-${Date.now()}`, book_id: id, name, source_type: sourceType, content, content_hash: "mockhash", version: 1 }; const assertion: Assertion = { id: `ast-${Date.now()}-1`, source_document_id: source.id, chunk_id: "chk-1", statement: `${name}: Affirmation extraite automatiquement du texte source`, subject: "Entité Source", predicate: "concerne", object: name, confidence: 0.94, status: "proposed" }; return { source_document: source, already_ingested: false, assertions: [assertion] }; }
  async listAssertions(id: string): Promise<Assertion[]> { return [{ id: "ast-001", source_document_id: "doc-001", chunk_id: "chk-001", statement: "Valerius détient le Codex d'Obsidienne dans les archives.", subject: "Valerius", predicate: "holds", object: "Codex d'Obsidienne", confidence: 0.96, status: "proposed" }, { id: "ast-002", source_document_id: "doc-001", chunk_id: "chk-001", statement: "La cité d'Aethelgard a été fondée en l'an 1042.", subject: "Aethelgard", predicate: "founded_in", object: "1042", confidence: 0.88, status: "proposed" }]; }
  async reviewAssertion(id: string, assertionId: string, decision: "accept" | "reject" | "defer", rationale = ""): Promise<void> {}
  async registerUser(email: string, pass: string, name?: string): Promise<UserProfile> { return { id: "usr-001", email, name: name || "Auteur MS", plan: "pro" }; }
  async loginUser(email: string, pass: string): Promise<UserProfile> { return { id: "usr-001", email, name: "Valerius de Cendres", plan: "pro" }; }
  async logoutUser(): Promise<void> {}
  async getCurrentUser(): Promise<UserProfile | null> { return { id: "usr-001", email: "auteur@manuscript.studio", name: "Valerius de Cendres", plan: "pro" }; }
}

export class RealBookApi implements BookApi {
  private baseUrl: string;
  constructor(baseUrl: string = "http://localhost:8000") { this.baseUrl = baseUrl; }
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> { const res = await fetch(`${this.baseUrl}${endpoint}`, { credentials: "include", headers: { "Content-Type": "application/json", ...options?.headers }, ...options }); if (!res.ok) { let errorText = await res.text(); try { const parsed = JSON.parse(errorText); if (parsed.detail) errorText = typeof parsed.detail === "string" ? parsed.detail : JSON.stringify(parsed.detail); } catch {} throw new Error(errorText || `API Error (${res.status})`); } return res.json(); }
  async getBook(id: string = "proj-001"): Promise<BookState> { return this.request(`/api/books/${id}`); }
  async createBook(book: Partial<BookState>): Promise<BookState> { return this.request("/api/books", { method: "POST", body: JSON.stringify(book) }); }
  async updateBook(id: string, updates: Partial<BookState>): Promise<BookState> { return this.request(`/api/books/${id}`, { method: "PUT", body: JSON.stringify(updates) }); }
  async generateOutline(id: string): Promise<BookState> { return this.request(`/api/books/${id}/outline/generate`, { method: "POST" }); }
  async approveOutline(id: string): Promise<BookState> { return this.request(`/api/books/${id}/outline/approve`, { method: "POST" }); }
  async addChapter(id: string, title: string, objective: string): Promise<BookState> { return this.request(`/api/books/${id}/chapters`, { method: "POST", body: JSON.stringify({ title, objective }) }); }
  async generateChapter(id: string, chapterNumber: number): Promise<{ book: BookState; versionNumber: number; content: string }> { return this.request(`/api/books/${id}/chapters/${chapterNumber}/generate`, { method: "POST" }); }
  async reviewChapter(id: string, chapterNumber: number, versionNumber?: number, draftText?: string): Promise<{ book: BookState; review: SceneReview }> { return this.request(`/api/books/${id}/chapters/${chapterNumber}/review`, { method: "POST", body: JSON.stringify({ versionNumber, draftText }) }); }
  async approveChapter(id: string, chapterNumber: number): Promise<BookState> { return this.request(`/api/books/${id}/chapters/${chapterNumber}/approve`, { method: "POST" }); }
  async rejectChapter(id: string, chapterNumber: number): Promise<BookState> { return this.request(`/api/books/${id}/chapters/${chapterNumber}/reject`, { method: "POST" }); }
  async getCanonicalContext(id: string, chapterNumber: number): Promise<CanonicalContextResponse> { return this.request(`/api/books/${id}/chapters/${chapterNumber}/context`); }
  async createCharacter(id: string, char: Omit<Character, "id">): Promise<BookState> { return this.request(`/api/books/${id}/characters`, { method: "POST", body: JSON.stringify(char) }); }
  async updateCharacter(id: string, charId: string, updates: Partial<Character>): Promise<BookState> { return this.request(`/api/books/${id}/characters/${charId}`, { method: "PUT", body: JSON.stringify(updates) }); }
  async deleteCharacter(id: string, charId: string): Promise<BookState> { return this.request(`/api/books/${id}/characters/${charId}`, { method: "DELETE" }); }
  async createLoreItem(id: string, item: Omit<LoreItem, "id">): Promise<BookState> { return this.request(`/api/books/${id}/lore`, { method: "POST", body: JSON.stringify(item) }); }
  async updateLoreItem(id: string, loreId: string, updates: Partial<LoreItem>): Promise<BookState> { return this.request(`/api/books/${id}/lore/${loreId}`, { method: "PUT", body: JSON.stringify(updates) }); }
  async deleteLoreItem(id: string, loreId: string): Promise<BookState> { return this.request(`/api/books/${id}/lore/${loreId}`, { method: "DELETE" }); }
  async ingestDocument(id: string, name: string, content: string, sourceType = "markdown"): Promise<IngestionResult> { return this.request(`/api/books/${id}/documents/ingest`, { method: "POST", body: JSON.stringify({ name, sourceType, content }) }); }
  async listAssertions(id: string): Promise<Assertion[]> { const res = await this.request<{ assertions: Assertion[] }>(`/api/books/${id}/assertions`); return res.assertions; }
  async reviewAssertion(id: string, assertionId: string, decision: "accept" | "reject" | "defer", rationale = ""): Promise<void> { await this.request(`/api/books/${id}/assertions/${assertionId}/review`, { method: "POST", body: JSON.stringify({ decision, rationale }) }); }
  async registerUser(email: string, pass: string, name?: string): Promise<UserProfile> { const res = await this.request<{ user: UserProfile }>("/api/auth/register", { method: "POST", body: JSON.stringify({ email, password: pass, name: name || "" }) }); return res.user; }
  async loginUser(email: string, pass: string): Promise<UserProfile> { const res = await this.request<{ user: UserProfile }>("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password: pass }) }); return res.user; }
  async logoutUser(): Promise<void> { await this.request("/api/auth/logout", { method: "POST" }); }
  async getCurrentUser(): Promise<UserProfile | null> { try { const res = await this.request<{ user: UserProfile }>("/api/auth/me"); return res.user; } catch { return null; } }
}

let apiInstance: BookApi | null = null;
export function getApiClient(): BookApi { if (!apiInstance) { if (process.env.NEXT_PUBLIC_USE_REAL_API === "true") apiInstance = new RealBookApi(); else apiInstance = new MockBookApi(); } return apiInstance; }
export function setApiClient(client: BookApi): void { apiInstance = client; }
