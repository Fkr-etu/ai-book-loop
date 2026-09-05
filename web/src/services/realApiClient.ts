import type {
  BackendAssertion,
  BackendBook,
  BackendCanonicalFact,
  BackendConflict,
  BackendIngestionResult,
  BackendSceneReview,
  BackendUser,
} from "@/types/api";
import { API_BASE_URL } from "@/services/config";

export interface CreateBookInput {
  title: string;
  theme: string;
  author_idea: string;
  lore?: string;
  constraints?: string[];
}

export interface GenerateChapterResult {
  book: BackendBook;
  versionNumber: number;
  content: string;
}

export interface ReviewChapterResult {
  book: BackendBook;
  review: BackendSceneReview;
}

export interface BackendChapterContext {
  authorIdea: string;
  theme: string;
  lore: string;
  globalOutline: import("@/types/api").BackendOutline | null;
  constraints: string[];
  previousSummaries: string;
  currentObjective: string;
  formattedContext: string;
}

export class RealApiError extends Error {
  status: number | null;

  constructor(message: string, status: number | null = null) {
    super(message);
    this.name = "RealApiError";
    this.status = status;
  }
}

const RETRYABLE_STATUS = new Set([408, 429, 500, 502, 503, 504]);
const MAX_RETRIES = 2;
const REQUEST_TIMEOUT_MS = 30_000;

async function parseResponse(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

function errorMessage(payload: unknown, fallback: string): string {
  if (typeof payload === "object" && payload !== null && "detail" in payload) {
    const detail = (payload as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
  }
  return fallback;
}

export class RealApiClient {
  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const method = (options.method || "GET").toUpperCase();
    const canRetry = method === "GET";
    let attempt = 0;

    while (true) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
      try {
        const response = await fetch(`${API_BASE_URL}${path}`, {
          ...options,
          signal: controller.signal,
          headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        });
        const payload = await parseResponse(response);
        if (response.ok) return payload as T;
        if (canRetry && attempt < MAX_RETRIES && RETRYABLE_STATUS.has(response.status)) {
          attempt += 1;
          continue;
        }
        throw new RealApiError(errorMessage(payload, `Request failed with status ${response.status}`), response.status);
      } catch (error) {
        if (error instanceof RealApiError) throw error;
        if (canRetry && attempt < MAX_RETRIES) {
          attempt += 1;
          continue;
        }
        const message = error instanceof DOMException && error.name === "AbortError"
          ? "La requête a expiré."
          : "Impossible de joindre l'API.";
        throw new RealApiError(message);
      } finally {
        clearTimeout(timeout);
      }
    }
  }

  getCurrentUser(): Promise<BackendUser | null> {
    return this.request<BackendUser | null>("/api/auth/me");
  }

  async login(email: string, password: string): Promise<BackendUser> {
    return this.request<BackendUser>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async register(email: string, password: string, name: string): Promise<BackendUser> {
    return this.request<BackendUser>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    });
  }

  listBooks(): Promise<BackendBook[]> {
    return this.request<BackendBook[]>("/api/books");
  }

  getBook(bookId: string): Promise<BackendBook> {
    return this.request<BackendBook>(`/api/books/${encodeURIComponent(bookId)}`);
  }

  createBook(input: CreateBookInput): Promise<BackendBook> {
    return this.request<BackendBook>("/api/books", {
      method: "POST",
      body: JSON.stringify(input),
    });
  }

  updateBook(bookId: string, updates: Record<string, unknown>): Promise<BackendBook> {
    return this.request(`/api/books/${encodeURIComponent(bookId)}`, {
      method: "PUT",
      body: JSON.stringify(updates),
    });
  }

  generateOutline(bookId: string): Promise<BackendBook> {
    return this.request(`/api/books/${encodeURIComponent(bookId)}/outline/generate`, { method: "POST" });
  }

  approveOutline(bookId: string): Promise<BackendBook> {
    return this.request(`/api/books/${encodeURIComponent(bookId)}/outline/approve`, { method: "POST" });
  }

  addChapter(bookId: string, chapterNumber: number): Promise<BackendBook> {
    return this.request(`/api/books/${encodeURIComponent(bookId)}/chapters`, {
      method: "POST",
      body: JSON.stringify({ chapter_number: chapterNumber }),
    });
  }

  generateChapter(bookId: string, chapterNumber: number): Promise<GenerateChapterResult> {
    return this.request(`/api/books/${encodeURIComponent(bookId)}/chapters/${chapterNumber}/generate`, { method: "POST" });
  }

  reviewChapter(bookId: string, chapterNumber: number, versionNumber?: number, draftText?: string): Promise<ReviewChapterResult> {
    return this.request(`/api/books/${encodeURIComponent(bookId)}/chapters/${chapterNumber}/review`, {
      method: "POST",
      body: JSON.stringify({ versionNumber, draftText }),
    });
  }

  approveChapter(bookId: string, chapterNumber: number): Promise<BackendBook> {
    return this.request(`/api/books/${encodeURIComponent(bookId)}/chapters/${chapterNumber}/approve`, { method: "POST" });
  }

  rejectChapter(bookId: string, chapterNumber: number): Promise<BackendBook> {
    return this.request(`/api/books/${encodeURIComponent(bookId)}/chapters/${chapterNumber}/reject`, { method: "POST" });
  }

  getChapterContext(bookId: string, chapterNumber: number): Promise<BackendChapterContext> {
    return this.request(`/api/books/${encodeURIComponent(bookId)}/chapters/${chapterNumber}/context`);
  }

  ingestDocument(bookId: string, name: string, content: string, sourceType = "markdown"): Promise<BackendIngestionResult> {
    return this.request(`/api/books/${encodeURIComponent(bookId)}/documents/ingest`, {
      method: "POST",
      body: JSON.stringify({ name, content, sourceType }),
    });
  }

  async listAssertions(bookId: string): Promise<BackendAssertion[]> {
    const result = await this.request<{ assertions: BackendAssertion[] }>(`/api/books/${encodeURIComponent(bookId)}/assertions`);
    return result.assertions;
  }

  async listConflicts(bookId: string): Promise<BackendConflict[]> {
    const result = await this.request<{ conflicts: BackendConflict[] }>(`/api/books/${encodeURIComponent(bookId)}/conflicts`);
    return result.conflicts;
  }

  async listCanonicalFacts(bookId: string): Promise<BackendCanonicalFact[]> {
    const result = await this.request<{ facts: BackendCanonicalFact[] }>(`/api/books/${encodeURIComponent(bookId)}/canonical-facts`);
    return result.facts;
  }

  reviewAssertion(bookId: string, assertionId: string, decision: "accept" | "reject" | "defer", rationale = ""): Promise<void> {
    return this.request<void>(`/api/books/${encodeURIComponent(bookId)}/assertions/${encodeURIComponent(assertionId)}/review`, {
      method: "POST",
      body: JSON.stringify({ decision, rationale }),
    });
  }
}

export const realApiClient = new RealApiClient();
