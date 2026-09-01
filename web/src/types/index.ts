export type RoleType = "Protagoniste" | "Antagoniste" | "Allié Majeur" | "Secondaire";

export interface Character {
  id: string;
  name: string;
  role: RoleType | string;
  archetype: string;
  psychology: string;
  goal: string;
  secret: string;
  status: "active" | "draft" | "archived";
}

export type LoreCategory = "faction" | "location" | "artifact" | "rule";

export interface LoreItem {
  id: string;
  title: string;
  category: LoreCategory;
  description: string;
  importance: "high" | "medium" | "low";
  canonStatus: "canonical" | "proposed" | "deprecated";
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

export type ChapterStatus = "approved" | "in_progress" | "pending";

export interface Chapter {
  id: string;
  number: number;
  title: string;
  summary: string;
  status: ChapterStatus;
  scenes: Scene[];
}

export type ConstraintType = "forbidden_word" | "pacing" | "tone" | "pov";

export interface CreativeConstraint {
  id: string;
  type: ConstraintType;
  description: string;
  active: boolean;
}

export interface SceneReview {
  id: string;
  sceneId: string;
  scoreStyle: number;
  scoreCoherence: number;
  forbiddenPatternsFound: string[];
  critique: string;
  approved: boolean;
  timestamp: string;
}

export interface ProjectState {
  id: string;
  title: string;
  subtitle: string;
  genre: string;
  targetAudience: string;
  theme: string;
  loreSummary: string;
  styleTone: string;
  wordCountTarget: number;
  currentWordCount: number;
  characters: Character[];
  loreItems: LoreItem[];
  graphNodes: GraphNode[];
  graphEdges: GraphEdge[];
  chapters: Chapter[];
  constraints: CreativeConstraint[];
  reviews: SceneReview[];
}

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
