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

export interface ReviewAssertionInput {
  decision: "accept" | "reject" | "defer";
  rationale?: string;
}

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const REQUEST_TIMEOUT_MS = 30_000;
const MAX_GET_RETRIES = 2;

export class RealApiClient {
  constructor(private readonly baseUrl = API_BASE_URL) {}

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const method = options.method?.toUpperCase() || "GET";
    const retryable = method === "GET";
    let lastError: unknown;

    for (let attempt = 0; attempt <= (retryable ? MAX_GET_RETRIES : 0); attempt += 1) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

      try {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
          ...options,
          credentials: "include",
          signal: controller.signal,
          headers: {
            "Content-Type": "application/json",
            ...options.headers,
          },
        });

        if (!response.ok) {
          const message = await this.readError(response);
          const error = new ApiError(message, response.status);
          if (!retryable || response.status < 500 || attempt === MAX_GET_RETRIES) {
            throw error;
          }
          lastError = error;
        } else {
          return (await response.json()) as T;
        }
      } catch (error) {
        lastError = error;
        if (!retryable || attempt === MAX_GET_RETRIES) {
          if (error instanceof ApiError) throw error;
          if (error instanceof DOMException && error.name === "AbortError") {
            throw new ApiError("La requête API a expiré.", 408);
          }
          throw new ApiError("Impossible de joindre l'API.", 0);
        }
      } finally {
        clearTimeout(timeout);
      }

      await new Promise((resolve) => setTimeout(resolve, 250 * 2 ** attempt));
    }

    throw lastError instanceof Error ? lastError : new ApiError("Erreur API inconnue.", 0);
  }

  private async readError(response: Response): Promise<string> {
    const text = await response.text();
    if (!text) return `Erreur API (${response.status}).`;
    try {
      const parsed = JSON.parse(text) as { detail?: unknown };
      if (typeof parsed.detail === "string") return parsed.detail;
      if (parsed.detail) return JSON.stringify(parsed.detail);
    } catch {
      // Keep the plain response body below.
    }
    return text;
  }

  health(): Promise<{ status: string }> {
    return this.request("/health");
  }

  getCurrentUser(): Promise<{ user: BackendUser }> {
    return this.request("/api/auth/me");
  }

  login(email: string, password: string): Promise<{ user: BackendUser }> {
    return this.request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  register(email: string, password: string, name = ""): Promise<{ user: BackendUser }> {
    return this.request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    });
  }

  logout(): Promise<{ message: string }> {
    return this.request("/api/auth/logout", { method: "POST" });
  }

  getBook(bookId: string): Promise<BackendBook> {
    return this.request(`/api/books/${encodeURIComponent(bookId)}`);
  }

  createBook(input: CreateBookInput): Promise<BackendBook> {
    return this.request("/api/books", {
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
    return this.request(`/api/books/${encodeURIComponent(bookId)}/chapters/${chapterNumber}/generate`, {
      method: "POST",
    });
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

  getChapterContext(bookId: string, chapterNumber: number): Promise<Record<string, unknown>> {
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

  reviewAssertion(bookId: string, assertionId: string, input: ReviewAssertionInput): Promise<unknown> {
    return this.request(`/api/books/${encodeURIComponent(bookId)}/assertions/${encodeURIComponent(assertionId)}/review`, {
      method: "POST",
      body: JSON.stringify(input),
    });
  }
}

export const realApiClient = new RealApiClient();
