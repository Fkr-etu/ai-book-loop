export type CanonicalStatus =
  | "draft"
  | "proposed"
  | "approved"
  | "rejected"
  | "canonical"
  | "needs_review"
  | "in_progress"
  | "pending";

export type RoleType = "Protagoniste" | "Antagoniste" | "Allié Majeur" | "Secondaire";

export interface Character {
  id: string;
  name: string;
  role: RoleType | string;
  archetype: string;
  psychology: string;
  goal: string;
  secret: string;
  status: "active" | "draft" | "archived" | CanonicalStatus;
  traits?: string[];
  motivations?: string;
  canonicalFacts?: string[];
  source?: string;
}

export type LoreCategory = "faction" | "location" | "artifact" | "rule";

export interface LoreItem {
  id: string;
  title: string;
  category: LoreCategory;
  description: string;
  importance: "high" | "medium" | "low";
  canonStatus: "canonical" | "proposed" | "rejected" | "deprecated";
  source?: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: "character" | "location" | "faction" | "artifact" | "rule";
  x?: number;
  y?: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relation: string;
}

export type SceneStatus = "validated" | "in_review" | "draft" | "rejected";

export interface Scene {
  id: string;
  title: string;
  summary: string;
  status: SceneStatus;
  content?: string;
  scoreStyle?: number;
  scoreCoherence?: number;
}

export type ChapterStatus = CanonicalStatus;

export interface ChapterVersion {
  id: string;
  versionNumber: number;
  content: string;
  createdAt: string;
  source: "author" | "ai" | "edited" | "retry";
  status: CanonicalStatus;
  review?: SceneReview;
}

export interface Chapter {
  id: string;
  number: number;
  title: string;
  objective: string;
  status: ChapterStatus;
  currentVersion: number;
  summary?: string;
  versions?: ChapterVersion[];
  scenes?: Scene[];
}

export type ConstraintType = "forbidden_word" | "pacing" | "tone" | "pov";

export interface CreativeConstraint {
  id: string;
  type: ConstraintType;
  description: string;
  active: boolean;
}

export interface SceneReview {
  id?: string;
  sceneId?: string;
  score: number;
  approved: boolean;
  issues: string[];
  suggestions: string[];
  scoreStyle?: number;
  scoreCoherence?: number;
  forbiddenPatternsFound?: string[];
  critique?: string;
  timestamp?: string;
}

export interface AuthorIntent {
  originalIdea: string;
  theme: string;
  constraints: string[];
  styleTone: string;
}

export interface BookState {
  id: string;
  title: string;
  theme: string;
  authorIdea: string;
  lore: string;
  constraints: string[];
  outline?: string;
  outlineApproved: boolean;
  chapters: Chapter[];

  // UI / Extended properties
  subtitle?: string;
  genre?: string;
  targetAudience?: string;
  styleTone?: string;
  loreSummary?: string;
  wordCountTarget?: number;
  currentWordCount?: number;
  characters?: Character[];
  loreItems?: LoreItem[];
  graphNodes?: GraphNode[];
  graphEdges?: GraphEdge[];
  creativeConstraints?: CreativeConstraint[];
  reviews?: SceneReview[];
  authorIntent?: AuthorIntent;
}

export type ProjectState = BookState;

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  plan: "standard" | "pro" | "elite";
  avatarUrl?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface CanonicalContextResponse {
  authorIdea: string;
  theme: string;
  lore: string;
  globalOutline: string;
  constraints: string[];
  previousSummaries: string;
  currentObjective: string;
  formattedContext: string;
}
