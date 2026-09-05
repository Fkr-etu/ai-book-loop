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

function unsupported(feature: string): never {
  throw new Error(`${feature} n'est pas encore exposé par l'API backend.`);
}

export class TypedBookApiAdapter implements BookApi {
  async getBook(id: string): Promise<BookState> {
    return adaptBackendBook(await realApiClient.getBook(id));
  }

  async createBook(book: Partial<BookState>): Promise<BookState> {
    return adaptBackendBook(
      await realApiClient.createBook({
        title: book.title || "Nouveau livre",
        theme: book.theme || "",
        author_idea: book.authorIdea || "",
        lore: book.lore || "",
        constraints: book.constraints || [],
      })
    );
  }

  async updateBook(id: string, updates: Partial<BookState>): Promise<BookState> {
    const payload: Record<string, unknown> = {};
    if (updates.title !== undefined) payload.title = updates.title;
    if (updates.theme !== undefined) payload.theme = updates.theme;
    if (updates.authorIdea !== undefined) payload.author_idea = updates.authorIdea;
    if (updates.lore !== undefined) payload.lore = updates.lore;
    if (updates.constraints !== undefined) payload.constraints = updates.constraints;
    return adaptBackendBook(await realApiClient.updateBook(id, payload));
  }

  async generateOutline(id: string): Promise<BookState> {
    return adaptBackendBook(await realApiClient.generateOutline(id));
  }

  async approveOutline(id: string): Promise<BookState> {
    return adaptBackendBook(await realApiClient.approveOutline(id));
  }

  async addChapter(id: string, _title: string, _objective: string): Promise<BookState> {
    const current = await realApiClient.getBook(id);
    const nextNumber = current.chapters.length + 1;
    return adaptBackendBook(await realApiClient.addChapter(id, nextNumber));
  }

  async generateChapter(id: string, chapterNumber: number) {
    const result = await realApiClient.generateChapter(id, chapterNumber);
    return { book: adaptBackendBook(result.book), versionNumber: result.versionNumber, content: result.content };
  }

  async reviewChapter(id: string, chapterNumber: number, versionNumber?: number, draftText?: string) {
    const result = await realApiClient.reviewChapter(id, chapterNumber, versionNumber, draftText);
    return { book: adaptBackendBook(result.book), review: result.review as SceneReview };
  }

  async approveChapter(id: string, chapterNumber: number): Promise<BookState> {
    return adaptBackendBook(await realApiClient.approveChapter(id, chapterNumber));
  }

  async rejectChapter(id: string, chapterNumber: number): Promise<BookState> {
    return adaptBackendBook(await realApiClient.rejectChapter(id, chapterNumber));
  }

  async getCanonicalContext(id: string, chapterNumber: number): Promise<CanonicalContextResponse> {
    const context = await realApiClient.getChapterContext(id, chapterNumber);
    return context as CanonicalContextResponse;
  }

  async createCharacter(_id: string, _char: Omit<Character, "id">): Promise<BookState> {
    return unsupported("La gestion des personnages");
  }
  async updateCharacter(_id: string, _charId: string, _updates: Partial<Character>): Promise<BookState> {
    return unsupported("La gestion des personnages");
  }
  async deleteCharacter(_id: string, _charId: string): Promise<BookState> {
    return unsupported("La gestion des personnages");
  }
  async createLoreItem(_id: string, _item: Omit<LoreItem, "id">): Promise<BookState> {
    return unsupported("La gestion du lore");
  }
  async updateLoreItem(_id: string, _loreId: string, _updates: Partial<LoreItem>): Promise<BookState> {
    return unsupported("La gestion du lore");
  }
  async deleteLoreItem(_id: string, _loreId: string): Promise<BookState> {
    return unsupported("La gestion du lore");
  }

  async ingestDocument(id: string, name: string, content: string, sourceType?: string): Promise<IngestionResult> {
    return (await realApiClient.ingestDocument(id, name, content, sourceType)) as IngestionResult;
  }

  async listAssertions(id: string): Promise<Assertion[]> {
    return (await realApiClient.listAssertions(id)) as Assertion[];
  }

  async reviewAssertion(id: string, assertionId: string, decision: "accept" | "reject" | "defer", rationale?: string): Promise<void> {
    await realApiClient.reviewAssertion(id, assertionId, { decision, rationale });
  }

  async registerUser(email: string, pass: string, name?: string): Promise<UserProfile> {
    const result = await realApiClient.register(email, pass, name);
    return { ...result.user, plan: "standard" };
  }

  async loginUser(email: string, pass: string): Promise<UserProfile> {
    const result = await realApiClient.login(email, pass);
    return { ...result.user, plan: "standard" };
  }

  async logoutUser(): Promise<void> {
    await realApiClient.logout();
  }

  async getCurrentUser(): Promise<UserProfile | null> {
    try {
      const result = await realApiClient.getCurrentUser();
      return { ...result.user, plan: "standard" };
    } catch {
      return null;
    }
  }
}

export const typedBookApi = new TypedBookApiAdapter();
