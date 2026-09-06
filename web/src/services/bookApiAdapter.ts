import type {
  BookState,
  Character,
  LoreItem,
  SceneReview,
  CanonicalContextResponse,
  IngestionResult,
  Assertion,
  UserProfile,
} from "@/types";
import { realApiClient } from "@/services/realApiClient";
import { adaptBackendBook } from "@/services/bookAdapter";
import type { BookApi } from "@/services/api";

const EMPTY_BOOK_ID = "proj-001";

export function emptyBook(): BookState {
  return {
    id: EMPTY_BOOK_ID,
    title: "",
    theme: "",
    authorIdea: "",
    lore: "",
    constraints: [],
    outlineApproved: false,
    chapters: [],
  };
}

function unsupported(feature: string): Promise<never> {
  return Promise.reject(new Error(`${feature} n'est pas encore disponible via l'API réelle.`));
}

function toCanonicalContext(context: Awaited<ReturnType<typeof realApiClient.getChapterContext>>): CanonicalContextResponse {
  const globalOutline = context.globalOutline?.chapters
    .map((chapter) => `## Chapitre ${chapter.number}: ${chapter.title}\nObjectif: ${chapter.objective}\n${chapter.synopsis}`)
    .join("\n\n") ?? "";

  return {
    authorIdea: context.authorIdea,
    theme: context.theme,
    lore: context.lore,
    globalOutline,
    constraints: context.constraints,
    previousSummaries: context.previousSummaries,
    currentObjective: context.currentObjective,
    formattedContext: context.formattedContext,
  };
}

export class RealBookApi implements BookApi {
  async getBook(id = EMPTY_BOOK_ID): Promise<BookState> {
    if (id === EMPTY_BOOK_ID) return emptyBook();
    return adaptBackendBook(await realApiClient.getBook(id));
  }

  async createBook(book: Partial<BookState>): Promise<BookState> {
    return adaptBackendBook(await realApiClient.createBook({
      title: book.title || "Nouveau Livre",
      theme: book.theme || "",
      author_idea: book.authorIdea || "",
      lore: book.lore,
      constraints: book.constraints,
    }));
  }

  async updateBook(id: string, updates: Partial<BookState>): Promise<BookState> {
    if (id === EMPTY_BOOK_ID) return this.createBook(updates);
    return adaptBackendBook(await realApiClient.updateBook(id, {
      ...(updates.title !== undefined ? { title: updates.title } : {}),
      ...(updates.theme !== undefined ? { theme: updates.theme } : {}),
      ...(updates.authorIdea !== undefined ? { author_idea: updates.authorIdea } : {}),
      ...(updates.lore !== undefined ? { lore: updates.lore } : {}),
      ...(updates.constraints !== undefined ? { constraints: updates.constraints } : {}),
    }));
  }

  async generateOutline(id: string): Promise<BookState> {
    if (id === EMPTY_BOOK_ID) return adaptBackendBook(await realApiClient.generateOutline(id));
    return adaptBackendBook(await realApiClient.generateOutline(id));
  }

  async approveOutline(id: string): Promise<BookState> {
    if (id === EMPTY_BOOK_ID) return adaptBackendBook(await realApiClient.approveOutline(id));
    return adaptBackendBook(await realApiClient.approveOutline(id));
  }

  async addChapter(id: string, title: string, objective: string): Promise<BookState> {
    return adaptBackendBook(await realApiClient.addChapter(id, title, objective));
  }

  async generateChapter(id: string, chapterNumber: number): Promise<{ book: BookState; versionNumber: number; content: string }> {
    const result = await realApiClient.generateChapter(id, chapterNumber);
    return {
      book: adaptBackendBook(result.book),
      versionNumber: result.versionNumber,
      content: result.content,
    };
  }

  async reviewChapter(id: string, chapterNumber: number, versionNumber?: number, draftText?: string): Promise<{ book: BookState; review: SceneReview }> {
    const result = await realApiClient.reviewChapter(id, chapterNumber, versionNumber, draftText);
    return {
      book: adaptBackendBook(result.book),
      review: result.review,
    };
  }

  async approveChapter(id: string, chapterNumber: number): Promise<BookState> {
    return adaptBackendBook(await realApiClient.approveChapter(id, chapterNumber));
  }

  async rejectChapter(id: string, chapterNumber: number): Promise<BookState> {
    return adaptBackendBook(await realApiClient.rejectChapter(id, chapterNumber));
  }

  async getCanonicalContext(id: string, chapterNumber: number): Promise<CanonicalContextResponse> {
    return toCanonicalContext(await realApiClient.getChapterContext(id, chapterNumber));
  }

  async createCharacter(id: string, char: Omit<Character, "id">): Promise<BookState> {
    return adaptBackendBook(await realApiClient.createCharacter(id, char));
  }

  async updateCharacter(id: string, charId: string, updates: Partial<Character>): Promise<BookState> {
    return adaptBackendBook(await realApiClient.updateCharacter(id, charId, updates));
  }

  async deleteCharacter(id: string, charId: string): Promise<BookState> {
    return adaptBackendBook(await realApiClient.deleteCharacter(id, charId));
  }

  async createLoreItem(id: string, item: Omit<LoreItem, "id">): Promise<BookState> {
    return adaptBackendBook(await realApiClient.createLoreItem(id, item));
  }

  async updateLoreItem(id: string, loreId: string, updates: Partial<LoreItem>): Promise<BookState> {
    return adaptBackendBook(await realApiClient.updateLoreItem(id, loreId, updates));
  }

  async deleteLoreItem(id: string, loreId: string): Promise<BookState> {
    return adaptBackendBook(await realApiClient.deleteLoreItem(id, loreId));
  }

  async ingestDocument(id: string, name: string, content: string, sourceType?: string): Promise<IngestionResult> {
    return realApiClient.ingestDocument(id, name, content, sourceType);
  }

  async listAssertions(id: string): Promise<Assertion[]> {
    return realApiClient.listAssertions(id);
  }

  async reviewAssertion(id: string, assertionId: string, decision: "accept" | "reject" | "defer", rationale?: string): Promise<void> {
    await realApiClient.reviewAssertion(id, assertionId, decision, rationale);
  }

  async registerUser(email: string, pass: string, name = ""): Promise<UserProfile> {
    return realApiClient.registerUser(email, pass, name);
  }

  async loginUser(email: string, pass: string): Promise<UserProfile> {
    return realApiClient.loginUser(email, pass);
  }

  async logoutUser(): Promise<void> {
    return realApiClient.logoutUser();
  }

  async getCurrentUser(): Promise<UserProfile | null> {
    return realApiClient.getCurrentUser();
  }
}
