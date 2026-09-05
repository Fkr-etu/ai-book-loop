export type BackendChapterStatus =
  | "draft"
  | "proposed"
  | "approved"
  | "rejected"
  | "canonical"
  | "needs_review";

export interface BackendOutlineChapter {
  number: number;
  title: string;
  objective: string;
  synopsis: string;
}

export interface BackendOutline {
  chapters: BackendOutlineChapter[];
}

export interface BackendChapter {
  id: string;
  number: number;
  title: string;
  objective: string;
  status: BackendChapterStatus;
  current_version: number;
  summary: string | null;
}

export interface BackendCreativeBrief {
  premise: string;
  audience: string;
  tone: string;
  themes: string[];
  must_include: string[];
  must_avoid: string[];
}

export interface BackendBook {
  id: string;
  owner_id: string;
  title: string;
  theme: string;
  author_idea: string;
  creative_brief: BackendCreativeBrief | null;
  lore: string;
  constraints: string[];
  outline: BackendOutline | null;
  outline_approved: boolean;
  chapters: BackendChapter[];
}

export interface BackendUser {
  id: string;
  email: string;
  name: string;
}

export interface BackendSceneReview {
  score: number;
  approved: boolean;
  issues: string[];
  suggestions: string[];
}

export interface BackendSourceDocument {
  id: string;
  book_id: string;
  name: string;
  source_type: string;
  content: string;
  content_hash: string;
  metadata: Record<string, string>;
  version: number;
}

export interface BackendAssertion {
  id: string;
  source_document_id: string;
  chunk_id: string;
  statement: string;
  subject: string;
  predicate: string;
  object: string;
  confidence: number;
  status: "proposed" | "accepted" | "rejected" | "deferred";
  evidence_id: string;
}

export interface BackendConflict {
  id: string;
  book_id: string;
  left_assertion_id: string;
  right_assertion_id: string;
  status: "open" | "resolved";
  resolution_assertion_id: string | null;
}

export interface BackendCanonicalFact {
  id: string;
  book_id: string;
  assertion_id: string;
  statement: string;
  subject: string;
  predicate: string;
  object: string;
  decision_id: string;
  version: number;
  active: boolean;
  previous_fact_id: string | null;
}

export interface BackendIngestionResult {
  source_document: BackendSourceDocument;
  assertions: BackendAssertion[];
  already_ingested: boolean;
}
