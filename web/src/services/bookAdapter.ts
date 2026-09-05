import type { BackendBook, BackendChapter } from "@/types/api";
import type { BookState, Chapter } from "@/types";

function adaptChapter(chapter: BackendChapter): Chapter {
  return {
    id: chapter.id,
    number: chapter.number,
    title: chapter.title,
    objective: chapter.objective,
    status: chapter.status,
    currentVersion: chapter.current_version,
    summary: chapter.summary ?? undefined,
  };
}

export function adaptBackendBook(book: BackendBook): BookState {
  return {
    id: book.id,
    title: book.title,
    theme: book.theme,
    authorIdea: book.author_idea,
    lore: book.lore,
    constraints: book.constraints,
    outline: book.outline
      ? book.outline.chapters
          .map((chapter) => `## Chapitre ${chapter.number}: ${chapter.title}\nObjectif: ${chapter.objective}\n${chapter.synopsis}`)
          .join("\n\n")
      : undefined,
    outlineApproved: book.outline_approved,
    chapters: book.chapters.map(adaptChapter),
  };
}
