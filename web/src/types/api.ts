export type BackendChapterStatus = "draft" | "proposed" | "approved" | "rejected" | "canonical" | "needs_review";
export type BackendWorkflowRunStatus = "running" | "completed" | "needs_review" | "failed";
export type BackendWorkflowStep = "write" | "review" | "correct" | "summarize";
export interface BackendWorkflowRun { id: string; book_id: string; chapter_number: number; idempotency_key: string; status: BackendWorkflowRunStatus; step: BackendWorkflowStep; attempt: number; draft: string; review: BackendSceneReview | null; decision: string | null; summary: string | null; error: string | null; }
export interface BackendOutlineChapter { number: number; title: string; objective: string; synopsis: string; }
export interface BackendOutline { chapters: BackendOutlineChapter[]; }
export interface BackendChapterVersion { id: string; versionNumber: number; content: string; createdAt: string; source: "author" | "ai" | "edited" | "retry"; status: BackendChapterStatus; }
export interface BackendChapter { id: string; number: number; title: string; objective: string; status: BackendChapterStatus; current_version: number; reviewed_version: number | null; summary: string | null; versions: BackendChapterVersion[]; }
export interface BackendCreativeBrief { premise: string; audience: string; tone: string; themes: string[]; must_include: string[]; must_avoid: string[]; }
export interface BackendBook { id: string; owner_id: string; title: string; theme: string; author_idea: string; creative_brief: BackendCreativeBrief | null; lore: string; constraints: string[]; outline: BackendOutline | null; outline_approved: boolean; chapters: BackendChapter[]; }
export type BackendSubscriptionPlan = "free" | "creator" | "pro";
export interface BackendUser { id: string; email: string; name: string; plan: BackendSubscriptionPlan; }
export interface BackendBillingState { plan: BackendSubscriptionPlan; subscription_status: string; subscription_current_period_end: string | null; subscription_cancel_at_period_end: boolean; }
export interface BackendSceneReview { score: number; approved: boolean; issues: string[]; suggestions: string[]; }
export interface BackendSourceDocument { id: string; book_id: string; name: string; source_type: string; content: string; content_hash: string; metadata: Record<string, string>; version: number; }
export interface BackendAssertion { id: string; source_document_id: string; chunk_id: string; statement: string; subject: string; predicate: string; object: string; confidence: number; status: "proposed" | "accepted" | "rejected" | "deferred"; evidence_id: string; }
export interface BackendConflict { id: string; book_id: string; left_assertion_id: string; right_assertion_id: string; status: "open" | "resolved"; resolution_assertion_id: string | null; }
export interface BackendCanonicalFact { id: string; book_id: string; assertion_id: string; statement: string; subject: string; predicate: string; object: string; decision_id: string; version: number; active: boolean; previous_fact_id: string | null; }
export type BackendRegressionRisk = "high" | "medium";
export interface BackendRegressionFinding { fact_id: string; assertion_id: string; statement: string; source_document_id: string; chunk_id: string; excerpt: string; start_offset: number; end_offset: number; risk?: BackendRegressionRisk; dependency_depth?: number; }
export interface BackendCanonChangeImpact { changed_fact_id: string; findings: BackendRegressionFinding[]; }
export type BackendCanonChangeProposalStatus = "proposed" | "accepted" | "rejected" | "deferred";
export interface BackendCanonChangeProposal { id: string; book_id: string; canonical_fact_id: string; statement: string; subject: string; predicate: string; object: string; proposer_id: string | null; rationale: string; status: BackendCanonChangeProposalStatus; created_at: string | null; }
export type BackendCanonChangeReviewDecision = "accept" | "reject";
export interface BackendCanonChangeReview { id: string; proposal_id: string; decision: BackendCanonChangeReviewDecision; reviewer_id: string | null; rationale: string; created_at: string | null; }
export interface BackendIngestionResult { source_document: BackendSourceDocument; assertions: BackendAssertion[]; already_ingested: boolean; }

export type BackendCharacterStatus = "proposed" | "active" | "archived";
export interface BackendCharacter { id: string; book_id: string; name: string; aliases: string[]; summary: string; attributes: Record<string, string>; status: BackendCharacterStatus; assertion_ids: string[]; }
export interface BackendCharacterRelation { id: string; book_id: string; source_character_id: string; target_character_id: string; relation_type: string; status: BackendCharacterStatus; assertion_ids: string[]; }
